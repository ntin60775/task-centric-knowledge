"""Shared models and constants for install skill runtime."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field


SKILL_NAME = "task-centric-knowledge"
BEGIN_MARKER = "⟦⟦BEGIN_TASK_KNOWLEDGE_SYSTEM#KB01⟧⟧"
END_MARKER = "⟦⟦END_TASK_KNOWLEDGE_SYSTEM#KB01⟧⟧"
MIGRATION_NOTE_NAME = "MIGRATION-SUGGESTION.md"
PROFILE_TO_BLOCK = {
    "generic": "assets/agents-managed-block-generic.md",
    "1c": "assets/agents-managed-block-1c.md",
}
KNOWLEDGE_ASSET_FILES = (
    "assets/knowledge/README.md",
    "assets/knowledge/modules/README.md",
    "assets/knowledge/modules/registry.md",
    "assets/knowledge/modules/_templates/module.md",
    "assets/knowledge/modules/_templates/file-local-policy.md",
    "assets/knowledge/modules/_templates/verification.md",
    "assets/knowledge/operations/README.md",
    "assets/knowledge/tasks/README.md",
    "assets/knowledge/tasks/registry.md",
    "assets/knowledge/tasks/_templates/task.md",
    "assets/knowledge/tasks/_templates/plan.md",
    "assets/knowledge/tasks/_templates/sdd.md",
    "assets/knowledge/tasks/_templates/artifacts/verification-matrix.md",
    "assets/knowledge/tasks/_templates/worklog.md",
    "assets/knowledge/tasks/_templates/decisions.md",
    "assets/knowledge/tasks/_templates/handoff.md",
)
REQUIRED_RELATIVE_PATHS = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/deployment.md",
    "references/consumer-runtime-v1.md",
    "references/upgrade-transition.md",
    "references/task-routing.md",
    "references/task-workflow.md",
    "src/task_knowledge/cli.py",
    "assets/agents-managed-block-generic.md",
    "assets/agents-managed-block-1c.md",
    *KNOWLEDGE_ASSET_FILES,
)
FOREIGN_SYSTEM_INDICATORS = (
    ".sisyphus",
    "doc/tasks",
    "docs/tasks",
    "docs/roadmap",
    "docs/plans",
)
MANAGED_TARGET_FILES = tuple(relative.removeprefix("assets/") for relative in KNOWLEDGE_ASSET_FILES)
PROJECT_DATA_TARGET_FILES = (
    "knowledge/modules/registry.md",
    "knowledge/tasks/registry.md",
)
FORCE_OVERWRITABLE_TARGET_FILES = tuple(
    relative
    for relative in MANAGED_TARGET_FILES
    if relative not in PROJECT_DATA_TARGET_FILES
)
ADDITIVE_MANAGED_TARGET_FILES = (
    "knowledge/modules/README.md",
    "knowledge/modules/registry.md",
    "knowledge/modules/_templates/module.md",
    "knowledge/modules/_templates/file-local-policy.md",
    "knowledge/modules/_templates/verification.md",
    "knowledge/tasks/_templates/sdd.md",
    "knowledge/tasks/_templates/artifacts/verification-matrix.md",
)
COMPATIBILITY_BASELINE_TARGET_FILES = tuple(
    relative
    for relative in MANAGED_TARGET_FILES
    if relative not in ADDITIVE_MANAGED_TARGET_FILES
)
MODE_CHECK = "check"
MODE_INSTALL = "install"
MODE_DOCTOR_DEPS = "doctor-deps"
MODE_VERIFY_PROJECT = "verify-project"
MODE_MIGRATE_CLEANUP_PLAN = "migrate-cleanup-plan"
MODE_MIGRATE_CLEANUP_CONFIRM = "migrate-cleanup-confirm"
VALID_MODES = (
    MODE_CHECK,
    MODE_INSTALL,
    MODE_DOCTOR_DEPS,
    MODE_VERIFY_PROJECT,
    MODE_MIGRATE_CLEANUP_PLAN,
    MODE_MIGRATE_CLEANUP_CONFIRM,
)
DEPENDENCY_CLASS_REQUIRED = "required"
DEPENDENCY_CLASS_CONDITIONAL = "conditional"
DEPENDENCY_CLASS_OPTIONAL = "optional"
DEPENDENCY_CLASS_NOT_APPLICABLE = "not-applicable"
DEPENDENCY_STATUS_OK = "ok"
DEPENDENCY_STATUS_MISSING = "missing"
DEPENDENCY_STATUS_MISCONFIGURED = "misconfigured"
DEPENDENCY_STATUS_OPTIONAL = "optional"
DEPENDENCY_STATUS_NOT_APPLICABLE = "not-applicable"
BLOCKING_LAYER_CORE = "core/local mode"
BLOCKING_LAYER_PUBLISH = "publish/integration"
FINGERPRINT_PLACEHOLDER = "<PLAN_FINGERPRINT>"


@dataclass
class StepResult:
    """Результат одного шага install/runtime операции.

    Args:
        key: Идентификатор шага.
        status: Статус выполнения.
        detail: Человекочитаемое описание.
        path: Опциональный путь к затронутому файлу.
    """
    key: str
    status: str
    detail: str
    path: str | None = None

    def to_payload(self) -> dict[str, object]:
        """Преобразовать результат в payload-словарь.

        Returns:
            Словарь с ключом, статусом и деталями.
        """
        payload = {
            "key": self.key,
            "status": self.status,
            "detail": self.detail,
        }
        if self.path is not None:
            payload["path"] = self.path
        return payload


@dataclass
class ExistingSystemReport:
    """Отчёт о состоянии существующей системы в целевом проекте.

    Args:
        classification: Классификация системы (fresh, managed, foreign, mixed).
        recommendation: Рекомендация по установке.
        managed_present: Список обнаруженных managed-файлов.
        foreign_present: Список обнаруженных foreign-индикаторов.
        agents_block_state: Состояние managed-блока в AGENTS.md.
    """
    classification: str
    recommendation: str
    managed_present: list[str]
    foreign_present: list[str]
    agents_block_state: str


@dataclass
class DependencyCheck:
    """Результат проверки одной зависимости.

    Args:
        name: Имя зависимости.
        dependency_class: Класс (`required`, `conditional`, `optional`, `not-applicable`).
        status: Статус проверки (`ok`, `missing`, `misconfigured`).
        blocking_layer: Блокирующий слой (`core/local mode`, `publish/integration`).
        detail: Детальное описание.
        hint: Подсказка для устранения.
        path: Опциональный путь.
    """
    name: str
    dependency_class: str
    status: str
    blocking_layer: str
    detail: str
    hint: str
    path: str | None = None

    def blocks_execution(self) -> bool:
        """Проверить, блокирует ли эта зависимость выполнение.

        Returns:
            `True`, если зависимость critical и имеет ошибку.
        """
        return self.blocking_layer == BLOCKING_LAYER_CORE and self.status in {
            DEPENDENCY_STATUS_MISSING,
            DEPENDENCY_STATUS_MISCONFIGURED,
        }

    def to_payload(self) -> dict[str, object]:
        """Serialize to a dictionary payload.

    Returns:
        Result.
        """
        payload = {
            "name": self.name,
            "dependency_class": self.dependency_class,
            "status": self.status,
            "blocking_layer": self.blocking_layer,
            "detail": self.detail,
            "hint": self.hint,
        }
        if self.path is not None:
            payload["path"] = self.path
        return payload


@dataclass
class CleanupCandidate:
    """Кандидат на cleanup (удаление или пересмотр).

    Args:
        path: Путь к файлу или директории.
        category: Категория кандидата.
        reason: Причина включения в cleanup.
        kind: Тип (`file`, `directory`, `symlink`).
        item_count: Количество элементов (для директорий).
    """
    path: str
    category: str
    reason: str
    kind: str
    item_count: int | None = None

    def to_payload(self) -> dict[str, object]:
        """Преобразовать кандидата в payload-словарь.

        Returns:
            Словарь с полями кандидата.
        """
        payload = {
            "path": self.path,
            "category": self.category,
            "reason": self.reason,
            "kind": self.kind,
        }
        if self.item_count is not None:
            payload["item_count"] = self.item_count
        return payload


@dataclass
class CleanupPlan:
    """План cleanup — список кандидатов на удаление и пересмотр.

    Args:
        safe_delete: Список безопасных для удаления кандидатов.
        keep: Список кандидатов, которые следует оставить.
        manual_review: Список кандидатов, требующих ручного пересмотра.
        targets: Целевые пути плана.
        target_count: Количество целевых путей.
        count: Общее количество кандидатов.
        confirm_command: Команда для подтверждения плана.
        plan_fingerprint: SHA256-фингерпринт плана.
        scope_locked: Флаг блокировки scope.
    """
    safe_delete: list[CleanupCandidate] = field(default_factory=list)
    keep: list[CleanupCandidate] = field(default_factory=list)
    manual_review: list[CleanupCandidate] = field(default_factory=list)
    targets: tuple[str, ...] = ()
    target_count: int = 0
    count: int = 0
    confirm_command: str = "—"
    plan_fingerprint: str = "—"
    scope_locked: bool = False
    expanded_scope: tuple[str, ...] = field(default_factory=tuple, repr=False)
    confirm_template: str = field(default="—", repr=False)

    def to_payload(self) -> dict[str, object]:
        """Преобразовать план в payload-словарь.

        Returns:
            Словарь с полным описанием плана.
        """
        return {
            "safe_delete": [item.to_payload() for item in self.safe_delete],
            "keep": [item.to_payload() for item in self.keep],
            "manual_review": [item.to_payload() for item in self.manual_review],
            "targets": list(self.targets),
            "target_count": self.target_count,
            "count": self.count,
            "confirm_command": self.confirm_command,
            "plan_fingerprint": self.plan_fingerprint,
            "scope_locked": self.scope_locked,
        }


def has_errors(results: list[StepResult]) -> bool:
    """Проверить, есть ли среди результатов ошибки.

    Args:
        results: Список результатов шагов.

    Returns:
        `True`, если хотя бы один статус равен `error`.
    """
    return any(item.status == "error" for item in results)


def cleanup_scope_fingerprint(
    *,
    targets: tuple[str, ...],
    expanded_scope: tuple[str, ...],
    target_count: int,
    count: int,
    confirm_template: str,
) -> str:
    """Вычислить SHA256-фингерпринт scope cleanup.

    Используется для проверки целостности плана перед подтверждением.

    Args:
        targets: Целевые пути.
        expanded_scope: Расширенный scope.
        target_count: Количество целевых путей.
        count: Общее количество элементов.
        confirm_template: Шаблон команды подтверждения.

    Returns:
        SHA256-хеш в шестнадцатеричном виде.
    """
    payload = {
        "targets": list(targets),
        "expanded_scope": list(expanded_scope),
        "target_count": target_count,
        "count": count,
        "confirm_template": confirm_template,
    }
    normalized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
