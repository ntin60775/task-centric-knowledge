"""Dependency diagnostics for install/upgrade governance."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from task_workflow_runtime.legacy_upgrade import upgrade_state_summary

from .environment import detect_existing_system, summarize_existing_system, validate_source, validate_target
from .models import (
    BLOCKING_LAYER_CORE,
    BLOCKING_LAYER_PUBLISH,
    DEPENDENCY_CLASS_CONDITIONAL,
    DEPENDENCY_CLASS_OPTIONAL,
    DEPENDENCY_CLASS_REQUIRED,
    DEPENDENCY_STATUS_MISCONFIGURED,
    DEPENDENCY_STATUS_MISSING,
    DEPENDENCY_STATUS_NOT_APPLICABLE,
    DEPENDENCY_STATUS_OK,
    DEPENDENCY_STATUS_OPTIONAL,
    DependencyCheck,
    ExistingSystemReport,
    SKILL_NAME,
    StepResult,
    has_errors,
)


GIT_TIMEOUT_SECONDS = 120


def _command_exists(command: str) -> str | None:
    return shutil.which(command)


def _git_output(project_root: Path, *args: str) -> tuple[bool, str]:
    command = ["git", "-C", str(project_root), *args]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=GIT_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return False, f"git command timed out after {GIT_TIMEOUT_SECONDS}s: {' '.join(command)}"
    output = completed.stdout.strip() or completed.stderr.strip()
    return completed.returncode == 0, output


def _git_repository_check(project_root: Path, git_path: str | None) -> DependencyCheck:
    if git_path is None:
        return DependencyCheck(
            name="git_repository",
            dependency_class=DEPENDENCY_CLASS_CONDITIONAL,
            status=DEPENDENCY_STATUS_NOT_APPLICABLE,
            blocking_layer=BLOCKING_LAYER_CORE,
            detail="Репозиторий нельзя проверить без `git`.",
            hint="Сначала установите `git`.",
        )
    ok, output = _git_output(project_root, "rev-parse", "--git-dir")
    if ok:
        return DependencyCheck(
            name="git_repository",
            dependency_class=DEPENDENCY_CLASS_CONDITIONAL,
            status=DEPENDENCY_STATUS_OK,
            blocking_layer=BLOCKING_LAYER_CORE,
            detail=f"Git-контур доступен: {output or '.git'}",
            hint="Дополнительных действий не требуется.",
        )
    return DependencyCheck(
        name="git_repository",
        dependency_class=DEPENDENCY_CLASS_CONDITIONAL,
        status=DEPENDENCY_STATUS_MISCONFIGURED,
        blocking_layer=BLOCKING_LAYER_CORE,
        detail="Целевой проект не выглядит git-репозиторием.",
        hint="Инициализируйте git-репозиторий или выберите корректный `--project-root`.",
        path=str(project_root),
    )


def _first_remote(project_root: Path) -> tuple[str | None, str | None]:
    ok, output = _git_output(project_root, "remote")
    if not ok or not output:
        return None, None
    remote_name = output.splitlines()[0].strip()
    ok, remote_url = _git_output(project_root, "remote", "get-url", remote_name)
    if not ok:
        return remote_name, None
    return remote_name, remote_url


def _detect_remote_host(remote_url: str | None) -> str | None:
    if remote_url is None:
        return None
    lowered = remote_url.lower()
    if "github" in lowered:
        return "github"
    if "gitlab" in lowered:
        return "gitlab"
    return "generic"


def _auth_check_for_host(host: str | None, *, cli_present: bool) -> DependencyCheck:
    env_map = {
        "github": ("GH_TOKEN", "GITHUB_TOKEN"),
        "gitlab": ("GLAB_TOKEN", "GITLAB_TOKEN"),
    }
    if host not in env_map:
        return DependencyCheck(
            name="forge_auth",
            dependency_class=DEPENDENCY_CLASS_OPTIONAL,
            status=DEPENDENCY_STATUS_NOT_APPLICABLE,
            blocking_layer=BLOCKING_LAYER_PUBLISH,
            detail="Публикационный host не требует auth-проверки через `gh` или `glab`.",
            hint="Дополнительных действий не требуется.",
        )
    if not cli_present:
        return DependencyCheck(
            name="forge_auth",
            dependency_class=DEPENDENCY_CLASS_OPTIONAL,
            status=DEPENDENCY_STATUS_NOT_APPLICABLE,
            blocking_layer=BLOCKING_LAYER_PUBLISH,
            detail=f"Auth для `{host}` не проверяется без соответствующего CLI.",
            hint=f"Сначала установите {'gh' if host == 'github' else 'glab'}.",
        )
    if any(os.environ.get(variable) for variable in env_map[host]):
        return DependencyCheck(
            name="forge_auth",
            dependency_class=DEPENDENCY_CLASS_OPTIONAL,
            status=DEPENDENCY_STATUS_OK,
            blocking_layer=BLOCKING_LAYER_PUBLISH,
            detail=f"Обнаружены env-маркеры auth для `{host}`.",
            hint="Дополнительных действий не требуется.",
        )
    return DependencyCheck(
        name="forge_auth",
        dependency_class=DEPENDENCY_CLASS_OPTIONAL,
        status=DEPENDENCY_STATUS_OPTIONAL,
        blocking_layer=BLOCKING_LAYER_PUBLISH,
        detail=(
            f"CLI для `{host}` найден, но offline-диагностика не подтвердила токены окружения; "
            "публикация может потребовать ручной auth."
        ),
        hint=(
            "Если планируется publish-flow, проверьте локальную авторизацию CLI или задайте "
            f"{'GH_TOKEN/GITHUB_TOKEN' if host == 'github' else 'GLAB_TOKEN/GITLAB_TOKEN'}."
        ),
    )


def _knowledge_check(project_root: Path, report: ExistingSystemReport) -> DependencyCheck:
    knowledge_path = project_root / "knowledge"
    if knowledge_path.exists() and knowledge_path.is_dir():
        return DependencyCheck(
            name="knowledge_contour",
            dependency_class=DEPENDENCY_CLASS_CONDITIONAL,
            status=DEPENDENCY_STATUS_OK,
            blocking_layer=BLOCKING_LAYER_CORE,
            detail="Каталог `knowledge/` присутствует.",
            hint="Дополнительных действий не требуется.",
            path=str(knowledge_path),
        )
    if knowledge_path.exists():
        return DependencyCheck(
            name="knowledge_contour",
            dependency_class=DEPENDENCY_CLASS_CONDITIONAL,
            status=DEPENDENCY_STATUS_MISCONFIGURED,
            blocking_layer=BLOCKING_LAYER_CORE,
            detail="Путь `knowledge` существует, но не является каталогом проекта.",
            hint="Уберите конфликтующий файл/ссылку или передайте корректный `--project-root`.",
            path=str(knowledge_path),
        )
    if report.classification in {"clean", "foreign_system"}:
        return DependencyCheck(
            name="knowledge_contour",
            dependency_class=DEPENDENCY_CLASS_CONDITIONAL,
            status=DEPENDENCY_STATUS_NOT_APPLICABLE,
            blocking_layer=BLOCKING_LAYER_CORE,
            detail="`knowledge/` ещё не развернут; install-режим может создать его автоматически.",
            hint="Запустите `--mode install`, если нужен managed knowledge-контур.",
            path=str(knowledge_path),
        )
    return DependencyCheck(
        name="knowledge_contour",
        dependency_class=DEPENDENCY_CLASS_CONDITIONAL,
        status=DEPENDENCY_STATUS_MISCONFIGURED,
        blocking_layer=BLOCKING_LAYER_CORE,
        detail="Классификация ожидает knowledge-контур, но каталог `knowledge/` отсутствует.",
        hint="Проверьте целевой проект и предыдущие шаги установки.",
        path=str(knowledge_path),
    )


def _agents_check(project_root: Path, report: ExistingSystemReport) -> DependencyCheck:
    agents_path = project_root / "AGENTS.md"
    if report.agents_block_state == "invalid":
        return DependencyCheck(
            name="agents_contour",
            dependency_class=DEPENDENCY_CLASS_CONDITIONAL,
            status=DEPENDENCY_STATUS_MISCONFIGURED,
            blocking_layer=BLOCKING_LAYER_CORE,
            detail="Managed-маркеры в `AGENTS.md` неконсистентны.",
            hint="Исправьте managed-блок knowledge-системы или восстановите `AGENTS.md`.",
            path=str(agents_path),
        )
    if agents_path.exists():
        detail = "Найден `AGENTS.md`."
        if report.agents_block_state == "managed":
            detail = "Найден `AGENTS.md` с валидным managed-блоком knowledge-системы."
        return DependencyCheck(
            name="agents_contour",
            dependency_class=DEPENDENCY_CLASS_CONDITIONAL,
            status=DEPENDENCY_STATUS_OK,
            blocking_layer=BLOCKING_LAYER_CORE,
            detail=detail,
            hint="Дополнительных действий не требуется.",
            path=str(agents_path),
        )
    return DependencyCheck(
        name="agents_contour",
        dependency_class=DEPENDENCY_CLASS_CONDITIONAL,
        status=DEPENDENCY_STATUS_NOT_APPLICABLE,
        blocking_layer=BLOCKING_LAYER_CORE,
        detail="`AGENTS.md` отсутствует; installer создаст snippet для ручного включения.",
        hint="При желании создайте `AGENTS.md` заранее, чтобы installer встроил managed-блок напрямую.",
        path=str(agents_path),
    )


def build_dependency_checks(project_root: Path, source_root: Path, report: ExistingSystemReport, source_results: list[StepResult]) -> list[DependencyCheck]:
    missing_source = [item.path for item in source_results if item.status == "error" and item.path]
    source_detail = "Исходный дистрибутив целостен."
    source_status = DEPENDENCY_STATUS_OK
    source_hint = "Дополнительных действий не требуется."
    if missing_source:
        source_status = DEPENDENCY_STATUS_MISCONFIGURED
        source_detail = f"В исходном skill-е отсутствуют обязательные ресурсы: {len(missing_source)}."
        source_hint = "Восстановите отсутствующие файлы skill-а или передайте корректный `--source-root`."

    python_path = _command_exists("python3")
    git_path = _command_exists("git")
    git_repo_check = _git_repository_check(project_root, git_path)
    remote_name, remote_url = _first_remote(project_root) if git_repo_check.status == DEPENDENCY_STATUS_OK else (None, None)
    remote_host = _detect_remote_host(remote_url)
    gh_path = _command_exists("gh")
    glab_path = _command_exists("glab")

    checks = [
        DependencyCheck(
            name="python3",
            dependency_class=DEPENDENCY_CLASS_REQUIRED,
            status=DEPENDENCY_STATUS_OK if python_path else DEPENDENCY_STATUS_MISSING,
            blocking_layer=BLOCKING_LAYER_CORE,
            detail=f"Интерпретатор Python доступен: {python_path}." if python_path else "Интерпретатор `python3` не найден.",
            hint="Дополнительных действий не требуется." if python_path else "Установите `python3` и повторите запуск.",
            path=python_path,
        ),
        DependencyCheck(
            name="git",
            dependency_class=DEPENDENCY_CLASS_REQUIRED,
            status=DEPENDENCY_STATUS_OK if git_path else DEPENDENCY_STATUS_MISSING,
            blocking_layer=BLOCKING_LAYER_CORE,
            detail=f"CLI `git` найден: {git_path}." if git_path else "CLI `git` не найден.",
            hint="Дополнительных действий не требуется." if git_path else "Установите `git` и повторите запуск.",
            path=git_path,
        ),
        DependencyCheck(
            name="skill_source",
            dependency_class=DEPENDENCY_CLASS_REQUIRED,
            status=source_status,
            blocking_layer=BLOCKING_LAYER_CORE,
            detail=source_detail,
            hint=source_hint,
            path=str(source_root),
        ),
        DependencyCheck(
            name="project_root",
            dependency_class=DEPENDENCY_CLASS_REQUIRED,
            status=DEPENDENCY_STATUS_OK if project_root.is_dir() else DEPENDENCY_STATUS_MISSING,
            blocking_layer=BLOCKING_LAYER_CORE,
            detail="Каталог проекта доступен." if project_root.is_dir() else "Каталог проекта не найден.",
            hint="Дополнительных действий не требуется." if project_root.is_dir() else "Передайте существующий абсолютный `--project-root`.",
            path=str(project_root),
        ),
        git_repo_check,
        _knowledge_check(project_root, report),
        _agents_check(project_root, report),
    ]

    if git_repo_check.status == DEPENDENCY_STATUS_OK and remote_url:
        remote_detail = f"Найден git remote `{remote_name}`: {remote_url}"
        remote_status = DEPENDENCY_STATUS_OK
        remote_hint = "Дополнительных действий не требуется."
    elif git_repo_check.status == DEPENDENCY_STATUS_OK:
        remote_detail = "Связанный git remote не найден; publish-flow пока неактивен."
        remote_status = DEPENDENCY_STATUS_OPTIONAL
        remote_hint = "Настройте remote, если планируется publish/integration слой."
    else:
        remote_detail = "Публикационный remote не проверяется, пока не подтверждён git-контур проекта."
        remote_status = DEPENDENCY_STATUS_NOT_APPLICABLE
        remote_hint = "Сначала исправьте core/local режим."
    checks.append(
        DependencyCheck(
            name="publish_remote",
            dependency_class=DEPENDENCY_CLASS_OPTIONAL,
            status=remote_status,
            blocking_layer=BLOCKING_LAYER_PUBLISH,
            detail=remote_detail,
            hint=remote_hint,
            path=remote_url,
        )
    )

    if remote_host == "github":
        gh_status = DEPENDENCY_STATUS_OK if gh_path else DEPENDENCY_STATUS_MISSING
        gh_detail = f"CLI `gh` найден: {gh_path}." if gh_path else "Remote указывает на GitHub, но `gh` не найден."
        gh_hint = "Дополнительных действий не требуется." if gh_path else "Установите `gh` для publish/integration с GitHub."
    elif remote_host is None:
        gh_status = DEPENDENCY_STATUS_NOT_APPLICABLE
        gh_detail = "GitHub CLI не требуется, пока publish-host не определён."
        gh_hint = "Дополнительных действий не требуется."
    else:
        gh_status = DEPENDENCY_STATUS_NOT_APPLICABLE
        gh_detail = "GitHub CLI не требуется для текущего publish-host."
        gh_hint = "Дополнительных действий не требуется."
    checks.append(
        DependencyCheck(
            name="gh",
            dependency_class=DEPENDENCY_CLASS_OPTIONAL,
            status=gh_status,
            blocking_layer=BLOCKING_LAYER_PUBLISH,
            detail=gh_detail,
            hint=gh_hint,
            path=gh_path,
        )
    )

    if remote_host == "gitlab":
        glab_status = DEPENDENCY_STATUS_OK if glab_path else DEPENDENCY_STATUS_MISSING
        glab_detail = f"CLI `glab` найден: {glab_path}." if glab_path else "Remote указывает на GitLab, но `glab` не найден."
        glab_hint = "Дополнительных действий не требуется." if glab_path else "Установите `glab` для publish/integration с GitLab."
    elif remote_host is None:
        glab_status = DEPENDENCY_STATUS_NOT_APPLICABLE
        glab_detail = "GitLab CLI не требуется, пока publish-host не определён."
        glab_hint = "Дополнительных действий не требуется."
    else:
        glab_status = DEPENDENCY_STATUS_NOT_APPLICABLE
        glab_detail = "GitLab CLI не требуется для текущего publish-host."
        glab_hint = "Дополнительных действий не требуется."
    checks.append(
        DependencyCheck(
            name="glab",
            dependency_class=DEPENDENCY_CLASS_OPTIONAL,
            status=glab_status,
            blocking_layer=BLOCKING_LAYER_PUBLISH,
            detail=glab_detail,
            hint=glab_hint,
            path=glab_path,
        )
    )

    checks.append(
        _auth_check_for_host(
            remote_host,
            cli_present=(gh_path is not None if remote_host == "github" else glab_path is not None),
        )
    )
    return checks


def doctor_deps(project_root: Path, source_root: Path, profile: str) -> dict[str, object]:
    results: list[StepResult] = []
    source_results = validate_source(source_root)
    results.extend(source_results)
    results.extend(validate_target(project_root))
    existing_report = detect_existing_system(project_root)
    results.extend(summarize_existing_system(existing_report))
    results.append(StepResult("profile", "ok", f"Выбран профиль {profile}", profile))

    dependencies = build_dependency_checks(project_root, source_root, existing_report, source_results)
    blocking_failures = sum(1 for item in dependencies if item.blocks_execution())
    publish_issues = sum(
        1
        for item in dependencies
        if item.blocking_layer == BLOCKING_LAYER_PUBLISH and item.status in {DEPENDENCY_STATUS_MISSING, DEPENDENCY_STATUS_MISCONFIGURED}
    )
    results.append(
        StepResult(
            "doctor_summary",
            "ok" if blocking_failures == 0 and not has_errors(results) else "error",
            f"Core/local blockers: {blocking_failures}; publish/integration issues: {publish_issues}.",
        )
    )

    return {
        "skill": SKILL_NAME,
        "mode": "doctor-deps",
        "project_root": str(project_root),
        "profile": profile,
        "existing_system_classification": existing_report.classification,
        **upgrade_state_summary(
            project_root,
            existing_system_classification=existing_report.classification,
        ),
        "ok": not has_errors(results) and blocking_failures == 0,
        "results": [item.to_payload() for item in results],
        "dependencies": [item.to_payload() for item in dependencies],
    }
