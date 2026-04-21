from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any


SUPPORTED_SOURCE = "grace"
CHECKOUT_ENV = "TASK_KNOWLEDGE_GRACE_CHECKOUT"
ALLOWED_ACTIONS = {"create", "update", "noop"}


class BorrowingsError(ValueError):
    """Raised when borrowed-layer input cannot be interpreted safely."""


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _json_fingerprint(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(encoded)


def _run_git(checkout: Path, *args: str) -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(checkout), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def _git_status_for_paths(checkout: Path, paths: list[Path]) -> str | None:
    if not paths:
        return ""
    completed = subprocess.run(
        [
            "git",
            "-C",
            str(checkout),
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
            "--",
            *[path.as_posix() for path in paths],
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def _manifest_path(skill_root: Path, source: str) -> Path:
    if source != SUPPORTED_SOURCE:
        raise BorrowingsError(f"Неподдерживаемый borrowed source: {source}")
    return skill_root / "borrowings" / source / "source.json"


def _safe_relative_path(raw_path: str, *, field: str) -> Path:
    if not raw_path:
        raise BorrowingsError(f"{field} должен быть непустым относительным путём")
    candidate = Path(raw_path)
    if candidate.is_absolute():
        raise BorrowingsError(f"{field} должен быть относительным путём: {raw_path}")
    if not candidate.parts or any(part in {"", ".", ".."} for part in candidate.parts):
        raise BorrowingsError(f"{field} содержит небезопасный сегмент пути: {raw_path}")
    return candidate


def _resolve_target(skill_root: Path, raw_path: str) -> Path:
    relative_path = _safe_relative_path(raw_path, field="local_target")
    target = (skill_root / relative_path).resolve()
    root = skill_root.resolve()
    if target != root and root not in target.parents:
        raise BorrowingsError(f"local_target выходит за пределы skill root: {raw_path}")
    return target


def _load_manifest(skill_root: Path, source: str) -> tuple[Path, dict[str, Any]]:
    path = _manifest_path(skill_root, source)
    if not path.exists():
        raise BorrowingsError(f"Manifest borrowed source не найден: {path}")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise BorrowingsError(f"Manifest содержит некорректный JSON: {error}") from error

    if manifest.get("schema_version") != 1:
        raise BorrowingsError("Поддерживается только schema_version=1")
    if manifest.get("source_id") != "grace-marketplace":
        raise BorrowingsError("source_id должен быть `grace-marketplace`")
    if not manifest.get("pinned_revision"):
        raise BorrowingsError("Manifest должен содержать pinned_revision")
    if not isinstance(manifest.get("surfaces"), list) or not manifest["surfaces"]:
        raise BorrowingsError("Manifest должен содержать непустой список surfaces")

    seen_surface_ids: set[str] = set()
    seen_local_targets: set[str] = set()
    for surface in manifest["surfaces"]:
        if not isinstance(surface, dict):
            raise BorrowingsError("Каждый surface должен быть объектом")
        surface_id = str(surface.get("surface_id", ""))
        if not surface_id:
            raise BorrowingsError("Каждый surface должен содержать surface_id")
        if surface_id in seen_surface_ids:
            raise BorrowingsError(f"surface_id должен быть уникальным: {surface_id}")
        seen_surface_ids.add(surface_id)
        mappings = surface.get("mappings")
        if not isinstance(mappings, list) or not mappings:
            raise BorrowingsError(f"surface {surface_id} должен содержать mappings")
        manifest_upstream_paths = surface.get("upstream_paths")
        if not isinstance(manifest_upstream_paths, list) or not manifest_upstream_paths:
            raise BorrowingsError(f"surface {surface_id} должен содержать непустой upstream_paths")
        manifest_local_targets = surface.get("local_targets")
        if not isinstance(manifest_local_targets, list) or not manifest_local_targets:
            raise BorrowingsError(f"surface {surface_id} должен содержать непустой local_targets")
        mapping_upstream_paths: list[str] = []
        mapping_local_targets: list[str] = []
        for mapping in mappings:
            if not isinstance(mapping, dict):
                raise BorrowingsError(f"surface {surface_id} содержит некорректный mapping")
            upstream_path = _safe_relative_path(str(mapping.get("upstream_path", "")), field="upstream_path").as_posix()
            local_target = _safe_relative_path(str(mapping.get("local_target", "")), field="local_target").as_posix()
            _resolve_target(skill_root, local_target)
            if local_target in seen_local_targets:
                raise BorrowingsError(f"local_target должен быть уникальным в manifest: {local_target}")
            seen_local_targets.add(local_target)
            mapping_upstream_paths.append(upstream_path)
            mapping_local_targets.append(local_target)
        if manifest_upstream_paths != mapping_upstream_paths:
            raise BorrowingsError(
                f"surface {surface_id} содержит drift между upstream_paths и mappings"
            )
        if manifest_local_targets != mapping_local_targets:
            raise BorrowingsError(
                f"surface {surface_id} содержит drift между local_targets и mappings"
            )

    return path, manifest


def _resolve_checkout(checkout: str | None) -> tuple[Path | None, str, list[dict[str, Any]]]:
    warnings: list[dict[str, Any]] = []
    if checkout:
        return Path(checkout).expanduser().resolve(), "argument", warnings
    env_value = os.environ.get(CHECKOUT_ENV)
    if env_value:
        return Path(env_value).expanduser().resolve(), "environment", warnings
    warnings.append(
        {
            "key": "checkout",
            "status": "warning",
            "detail": f"Локальный checkout не задан. Укажи --checkout или env {CHECKOUT_ENV}.",
            "path": None,
        }
    )
    return None, "missing", warnings


def _checkout_state(checkout: Path | None, pinned_revision: str) -> dict[str, Any]:
    if checkout is None:
        return {
            "checkout_state": "missing",
            "checkout_path": None,
            "checkout_source": "missing",
            "checkout_revision": None,
            "matches_pinned_revision": False,
        }
    if not checkout.exists() or not checkout.is_dir():
        return {
            "checkout_state": "missing",
            "checkout_path": str(checkout),
            "checkout_source": None,
            "checkout_revision": None,
            "matches_pinned_revision": False,
        }
    revision = _run_git(checkout, "rev-parse", "HEAD")
    if not revision:
        return {
            "checkout_state": "invalid",
            "checkout_path": str(checkout),
            "checkout_source": None,
            "checkout_revision": None,
            "matches_pinned_revision": False,
        }
    return {
        "checkout_state": "available",
        "checkout_path": str(checkout),
        "checkout_source": None,
        "checkout_revision": revision,
        "matches_pinned_revision": revision == pinned_revision,
    }


def _surface_summary(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    surfaces: list[dict[str, Any]] = []
    for surface in manifest["surfaces"]:
        surfaces.append(
            {
                "surface_id": surface["surface_id"],
                "adoption_mode": surface.get("adoption_mode"),
                "concepts": surface.get("concepts", []),
                "upstream_paths": surface.get("upstream_paths", []),
                "local_targets": surface.get("local_targets", []),
            }
        )
    return surfaces


def _mapped_upstream_paths(manifest: dict[str, Any]) -> list[Path]:
    paths: list[Path] = []
    for surface in manifest["surfaces"]:
        for mapping in surface["mappings"]:
            paths.append(_safe_relative_path(mapping["upstream_path"], field="upstream_path"))
    return paths


def _dirty_mapped_paths(checkout: Path, manifest: dict[str, Any]) -> list[str] | None:
    status = _git_status_for_paths(checkout, _mapped_upstream_paths(manifest))
    if status is None:
        return None
    return [line for line in status.splitlines() if line.strip()]


def read_status(skill_root: Path, project_root: Path, *, source: str, checkout: str | None) -> dict[str, Any]:
    manifest_path, manifest = _load_manifest(skill_root, source)
    resolved_checkout, checkout_source, warnings = _resolve_checkout(checkout)
    checkout_payload = _checkout_state(resolved_checkout, manifest["pinned_revision"])
    checkout_payload["checkout_source"] = checkout_source

    if checkout_payload["checkout_state"] == "available" and not checkout_payload["matches_pinned_revision"]:
        warnings.append(
            {
                "key": "pinned_revision",
                "status": "warning",
                "detail": "Checkout HEAD не совпадает с pinned_revision manifest.",
                "path": checkout_payload["checkout_path"],
            }
        )
    dirty_paths: list[str] = []
    mapped_paths_dirty: bool | None = None
    if checkout_payload["checkout_state"] == "available" and resolved_checkout is not None:
        dirty_paths_result = _dirty_mapped_paths(resolved_checkout, manifest)
        if dirty_paths_result is None:
            warnings.append(
                {
                    "key": "checkout_dirty",
                    "status": "warning",
                    "detail": "Не удалось проверить чистоту mapped upstream paths.",
                    "path": checkout_payload["checkout_path"],
                }
            )
        else:
            dirty_paths = dirty_paths_result
            mapped_paths_dirty = bool(dirty_paths_result)
            if dirty_paths_result:
                warnings.append(
                    {
                        "key": "checkout_dirty",
                        "status": "warning",
                        "detail": "Mapped upstream paths содержат staged, unstaged или untracked изменения; refresh-plan будет заблокирован.",
                        "path": checkout_payload["checkout_path"],
                    }
                )

    return {
        "ok": True,
        "command": "borrowings status",
        "project_root": str(project_root.resolve()),
        "source": source,
        "manifest_path": str(manifest_path),
        "manifest_sha256": _sha256_file(manifest_path),
        "origin_url": manifest["origin_url"],
        "pinned_revision": manifest["pinned_revision"],
        "upstream_version": manifest["upstream_version"],
        **checkout_payload,
        "mapped_paths_dirty": mapped_paths_dirty,
        "dirty_paths": dirty_paths,
        "surfaces": _surface_summary(manifest),
        "warnings": warnings,
    }


def _plan_actions(skill_root: Path, checkout: Path, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for surface in manifest["surfaces"]:
        for mapping in surface["mappings"]:
            upstream_relative = _safe_relative_path(mapping["upstream_path"], field="upstream_path")
            target_relative = _safe_relative_path(mapping["local_target"], field="local_target")
            source_path = checkout / upstream_relative
            target_path = _resolve_target(skill_root, mapping["local_target"])
            if not source_path.exists() or not source_path.is_file():
                raise BorrowingsError(f"Upstream source не найден: {source_path}")
            source_sha = _sha256_file(source_path)
            target_before_sha = _sha256_file(target_path) if target_path.exists() else None
            if target_before_sha is None:
                action = "create"
            elif target_before_sha == source_sha:
                action = "noop"
            else:
                action = "update"
            if action not in ALLOWED_ACTIONS:
                raise BorrowingsError(f"Недопустимое refresh-действие: {action}")
            actions.append(
                {
                    "action": action,
                    "surface_id": surface["surface_id"],
                    "source_path": str(upstream_relative),
                    "target_path": str(target_relative),
                    "source_sha256": source_sha,
                    "target_before_sha256": target_before_sha,
                }
            )
    return actions


def build_refresh_plan(skill_root: Path, project_root: Path, *, source: str, checkout: str | None) -> dict[str, Any]:
    manifest_path, manifest = _load_manifest(skill_root, source)
    resolved_checkout, checkout_source, warnings = _resolve_checkout(checkout)
    checkout_payload = _checkout_state(resolved_checkout, manifest["pinned_revision"])
    checkout_payload["checkout_source"] = checkout_source

    if checkout_payload["checkout_state"] != "available":
        return {
            "ok": False,
            "command": "borrowings refresh-plan",
            "project_root": str(project_root.resolve()),
            "source": source,
            "manifest_path": str(manifest_path),
            **checkout_payload,
            "plan_fingerprint": None,
            "actions": [],
            "warnings": warnings,
            "results": [
                {
                    "key": "checkout",
                    "status": "error",
                    "detail": "Refresh-plan требует локальный git checkout pinned upstream.",
                    "path": checkout_payload["checkout_path"],
                }
            ],
        }
    if not checkout_payload["matches_pinned_revision"]:
        return {
            "ok": False,
            "command": "borrowings refresh-plan",
            "project_root": str(project_root.resolve()),
            "source": source,
            "manifest_path": str(manifest_path),
            **checkout_payload,
            "plan_fingerprint": None,
            "actions": [],
            "warnings": warnings,
            "results": [
                {
                    "key": "pinned_revision",
                    "status": "error",
                    "detail": "Checkout HEAD должен совпадать с pinned_revision manifest.",
                    "path": checkout_payload["checkout_path"],
                }
            ],
        }

    dirty_paths = _dirty_mapped_paths(resolved_checkout, manifest)
    if dirty_paths is None:
        return {
            "ok": False,
            "command": "borrowings refresh-plan",
            "project_root": str(project_root.resolve()),
            "source": source,
            "manifest_path": str(manifest_path),
            **checkout_payload,
            "plan_fingerprint": None,
            "actions": [],
            "warnings": warnings,
            "results": [
                {
                    "key": "checkout_dirty",
                    "status": "error",
                    "detail": "Не удалось проверить чистоту mapped upstream paths в checkout.",
                    "path": checkout_payload["checkout_path"],
                }
            ],
        }
    if dirty_paths:
        return {
            "ok": False,
            "command": "borrowings refresh-plan",
            "project_root": str(project_root.resolve()),
            "source": source,
            "manifest_path": str(manifest_path),
            **checkout_payload,
            "plan_fingerprint": None,
            "actions": [],
            "dirty_paths": dirty_paths,
            "warnings": warnings,
            "results": [
                {
                    "key": "checkout_dirty",
                    "status": "error",
                    "detail": "Mapped upstream paths содержат staged, unstaged или untracked изменения; refresh разрешён только из clean pinned checkout.",
                    "path": checkout_payload["checkout_path"],
                }
            ],
        }

    try:
        actions = _plan_actions(skill_root, resolved_checkout, manifest)
    except BorrowingsError as error:
        return {
            "ok": False,
            "command": "borrowings refresh-plan",
            "project_root": str(project_root.resolve()),
            "source": source,
            "manifest_path": str(manifest_path),
            **checkout_payload,
            "plan_fingerprint": None,
            "actions": [],
            "warnings": warnings,
            "results": [{"key": "refresh-plan", "status": "error", "detail": str(error), "path": None}],
        }

    fingerprint_input = {
        "schema_version": manifest["schema_version"],
        "source_id": manifest["source_id"],
        "origin_url": manifest["origin_url"],
        "pinned_revision": manifest["pinned_revision"],
        "checkout_revision": checkout_payload["checkout_revision"],
        "manifest_sha256": _sha256_file(manifest_path),
        "actions": actions,
    }
    plan_fingerprint = _json_fingerprint(fingerprint_input)
    actionable = [item for item in actions if item["action"] != "noop"]
    return {
        "ok": True,
        "command": "borrowings refresh-plan",
        "project_root": str(project_root.resolve()),
        "source": source,
        "manifest_path": str(manifest_path),
        "manifest_sha256": fingerprint_input["manifest_sha256"],
        "origin_url": manifest["origin_url"],
        "pinned_revision": manifest["pinned_revision"],
        "upstream_version": manifest["upstream_version"],
        **checkout_payload,
        "plan_fingerprint": plan_fingerprint,
        "action_count": len(actions),
        "pending_action_count": len(actionable),
        "actions": actions,
        "warnings": warnings,
        "results": [
            {
                "key": "refresh-plan",
                "status": "ok",
                "detail": f"Построен refresh-plan: всего действий {len(actions)}, к применению {len(actionable)}.",
                "path": None,
            }
        ],
    }


def apply_refresh(
    skill_root: Path,
    project_root: Path,
    *,
    source: str,
    checkout: str | None,
    plan_fingerprint: str,
    assume_yes: bool,
) -> dict[str, Any]:
    if not assume_yes:
        return {
            "ok": False,
            "command": "borrowings refresh-apply",
            "project_root": str(project_root.resolve()),
            "source": source,
            "plan_fingerprint": plan_fingerprint,
            "applied": [],
            "results": [
                {
                    "key": "confirmation",
                    "status": "error",
                    "detail": "refresh-apply требует явный флаг --yes.",
                    "path": None,
                }
            ],
        }

    plan = build_refresh_plan(skill_root, project_root, source=source, checkout=checkout)
    if not plan["ok"]:
        plan["command"] = "borrowings refresh-apply"
        return plan
    if plan["plan_fingerprint"] != plan_fingerprint:
        return {
            "ok": False,
            "command": "borrowings refresh-apply",
            "project_root": str(project_root.resolve()),
            "source": source,
            "expected_plan_fingerprint": plan["plan_fingerprint"],
            "provided_plan_fingerprint": plan_fingerprint,
            "applied": [],
            "results": [
                {
                    "key": "plan_fingerprint",
                    "status": "error",
                    "detail": "Refresh scope изменился после preview; сначала построй новый refresh-plan.",
                    "path": None,
                }
            ],
        }

    checkout_path = Path(str(plan["checkout_path"]))
    applied: list[dict[str, Any]] = []
    for action in plan["actions"]:
        if action["action"] == "noop":
            continue
        source_path = checkout_path / _safe_relative_path(str(action["source_path"]), field="source_path")
        target_path = _resolve_target(skill_root, str(action["target_path"]))
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(source_path.read_bytes())
        applied.append(action)

    return {
        "ok": True,
        "command": "borrowings refresh-apply",
        "project_root": str(project_root.resolve()),
        "source": source,
        "plan_fingerprint": plan_fingerprint,
        "applied_count": len(applied),
        "applied": applied,
        "results": [
            {
                "key": "refresh-apply",
                "status": "ok",
                "detail": f"Применено borrowed refresh действий: {len(applied)}.",
                "path": None,
            }
        ],
    }
