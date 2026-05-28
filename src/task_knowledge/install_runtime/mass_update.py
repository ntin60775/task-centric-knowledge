"""Mass project update automation for task-centric-knowledge.

Discovers all projects with installed knowledge systems and performs
batch check → apply → verify.

Usage:
    task-knowledge install mass-update --source-root /path/to/skill [--projects /proj1 /proj2] [--dry-run]
"""

from __future__ import annotations

from pathlib import Path

from .environment import check, install, verify_project


def discover_projects(
    search_roots: list[Path],
    max_depth: int = 3,
) -> list[Path]:
    """Discover project roots with installed knowledge systems.

    Scans directories for `knowledge/tasks/registry.md` as a marker
    of an installed knowledge system.

    Args:
        search_roots: Directories to scan for projects.
        max_depth: Maximum directory depth to search.

    Returns:
        List of absolute project root paths.
    """
    found: list[Path] = []
    seen: set[str] = set()

    for root in search_roots:
        root = root.resolve()
        if not root.is_dir():
            continue
        _scan_dir(root, found, seen, max_depth=max_depth, current_depth=0)

    return found


def _scan_dir(
    directory: Path,
    found: list[Path],
    seen: set[str],
    max_depth: int,
    current_depth: int,
) -> None:
    """Recursively scan a directory for knowledge system markers."""
    if current_depth > max_depth:
        return
    marker = directory / "knowledge" / "tasks" / "registry.md"
    if marker.is_file():
        key = str(directory.resolve())
        if key not in seen:
            seen.add(key)
            found.append(directory.resolve())
        return  # don't recurse into project directories

    try:
        entries = sorted(directory.iterdir())
    except (PermissionError, OSError):
        return

    for entry in entries:
        if entry.is_dir() and not entry.name.startswith("."):
            _scan_dir(entry, found, seen, max_depth, current_depth + 1)


def mass_update(
    source_root: Path,
    projects: list[Path] | None = None,
    search_roots: list[Path] | None = None,
    profile: str = "generic",
    dry_run: bool = False,
    output_format: str = "text",
) -> dict[str, object]:
    """Perform mass update of knowledge systems across projects.

    Args:
        source_root: Path to the source skill distribution.
        projects: Explicit list of project roots to update.
        search_roots: Directories to search for projects if `projects` is empty.
        profile: Profile name for install operations.
        dry_run: If True, only check without applying.
        output_format: Output format (text or json).

    Returns:
        Summary payload with per-project results.
    """
    # Resolve project list
    if projects is None:
        projects = []
    project_set: list[Path] = [p.resolve() for p in projects if p.is_dir()]

    if not project_set and search_roots:
        project_set = discover_projects(search_roots)

    if not project_set:
        return {
            "ok": False,
            "command": "mass-update",
            "error": "Проекты не найдены. Укажите --projects или --search-roots.",
            "projects": [],
            "summary": {"total": 0, "ok": 0, "failed": 0, "skipped": 0},
        }

    results: list[dict[str, object]] = []
    for project_root in sorted(project_set):
        result = _process_project(
            project_root,
            source_root,
            profile=profile,
            dry_run=dry_run,
            output_format=output_format,
        )
        results.append(result)
        if not dry_run and output_format == "text":
            status = "OK" if result["ok"] else "FAIL"
            print(f"[{status}] {result['project_root']}")

    summary = {
        "total": len(results),
        "ok": sum(1 for r in results if r["ok"]),
        "failed": sum(1 for r in results if not r["ok"] and not r.get("skipped")),
        "skipped": sum(1 for r in results if r.get("skipped")),
    }

    return {
        "ok": summary["failed"] == 0,
        "command": "mass-update",
        "source_root": str(source_root),
        "dry_run": dry_run,
        "profile": profile,
        "summary": summary,
        "projects": results,
    }


def _process_project(
    project_root: Path,
    source_root: Path,
    profile: str,
    dry_run: bool,
    output_format: str,
) -> dict[str, object]:
    """Process a single project: check → (apply → verify) or dry-run check only.

    Args:
        project_root: Path to the project.
        source_root: Path to the source skill distribution.
        profile: Profile name.
        dry_run: If True, only check.
        output_format: Output format.

    Returns:
        Result payload for this project.
    """
    project_key = str(project_root)

    # Step 1: Check
    try:
        check_payload = check(project_root, source_root, profile)
    except Exception as exc:
        return {
            "project_root": project_key,
            "ok": False,
            "skipped": False,
            "stage": "check",
            "error": str(exc),
        }

    if not check_payload.get("ok"):
        return {
            "project_root": project_key,
            "ok": False,
            "skipped": False,
            "stage": "check",
            "check_ok": False,
            "check_results": check_payload.get("results", []),
        }

    if dry_run:
        return {
            "project_root": project_key,
            "ok": True,
            "skipped": False,
            "stage": "check",
            "dry_run": True,
            "check_ok": True,
        }

    # Step 2: Apply
    try:
        apply_payload = install(
            project_root,
            source_root,
            profile,
            force=True,
            existing_system_mode="migrate",
        )
    except Exception as exc:
        return {
            "project_root": project_key,
            "ok": False,
            "skipped": False,
            "stage": "apply",
            "error": str(exc),
        }

    if not apply_payload.get("ok"):
        return {
            "project_root": project_key,
            "ok": False,
            "skipped": False,
            "stage": "apply",
            "apply_ok": False,
            "apply_results": apply_payload.get("results", []),
        }

    # Step 3: Verify
    try:
        verify_payload = verify_project(project_root, source_root, profile, force=True)
    except Exception as exc:
        return {
            "project_root": project_key,
            "ok": False,
            "skipped": False,
            "stage": "verify",
            "error": str(exc),
        }

    return {
        "project_root": project_key,
        "ok": verify_payload.get("ok", False),
        "skipped": False,
        "stage": "verify",
        "check_ok": True,
        "apply_ok": True,
        "verify_ok": verify_payload.get("ok", False),
    }
