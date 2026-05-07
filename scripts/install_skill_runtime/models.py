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
    "scripts/task_knowledge_cli.py",
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


## @brief Результат одного шага install/runtime операции.
#
#  @param key    Идентификатор шага.
#  @param status Статус выполнения.
#  @param detail Человекочитаемое описание.
#  @param path   Опциональный путь к затронутому файлу.
@dataclass
class StepResult:
    """Результат одного шага install/runtime операции."""
    key: str
    status: str
    detail: str
    path: str | None = None

    ## @brief Преобразовать результат в payload-словарь.
    #  @return Словарь с ключом, статусом и деталями.
    ## @brief Преобразовать результат проверки в payload-словарь.
    #  @return Словарь с полями зависимости.
    def to_payload(self) -> dict[str, object]:
        payload = {
            "key": self.key,
            "status": self.status,
            "detail": self.detail,
        }
        if self.path is not None:
            payload["path"] = self.path
        return payload


## @brief Отчёт о состоянии существующей системы в целевом проекте.
#
#  @param classification      Классификация системы (fresh, managed, foreign, mixed).
#  @param recommendation      Рекомендация по установке.
#  @param managed_present     Список обнаруженных managed-файлов.
#  @param foreign_present     Список обнаруженных foreign-индикаторов.
#  @param agents_block_state  Состояние managed-блока в AGENTS.md.
@dataclass
class ExistingSystemReport:
    """Отчёт о состоянии существующей системы в целевом проекте."""
    classification: str
    recommendation: str
    managed_present: list[str]
    foreign_present: list[str]
    agents_block_state: str


## @brief Результат проверки одной зависимости.
#
#  @param name             Имя зависимости.
#  @param dependency_class Класс (`required`, `conditional`, `optional`, `not-applicable`).
#  @param status           Статус проверки (`ok`, `missing`, `misconfigured`).
#  @param blocking_layer   Блокирующий слой (`core/local mode`, `publish/integration`).
#  @param detail           Детальное описание.
#  @param hint             Подсказка для устранения.
#  @param path             Опциональный путь.
@dataclass
class DependencyCheck:
    """Результат проверки одной зависимости."""
    name: str
    dependency_class: str
    status: str
    blocking_layer: str
    detail: str
    hint: str
    path: str | None = None

    ## @brief Проверить, блокирует ли эта зависимость выполнение.
    #  @return `True`, если зависимость critical и имеет ошибку.
    def blocks_execution(self) -> bool:
        return self.blocking_layer == BLOCKING_LAYER_CORE and self.status in {
            DEPENDENCY_STATUS_MISSING,
            DEPENDENCY_STATUS_MISCONFIGURED,
        }

    def to_payload(self) -> dict[str, object]:
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


## @brief Кандидат на cleanup (удаление или пересмотр).
#
#  @param path       Путь к файлу или директории.
#  @param category   Категория кандидата.
#  @param reason     Причина включения в cleanup.
#  @param kind       Тип (`file`, `directory`, `symlink`).
#  @param item_count Количество элементов (для директорий).
@dataclass
class CleanupCandidate:
    """Кандидат на cleanup (удаление или пересмотр)."""
    path: str
    category: str
    reason: str
    kind: str
    item_count: int | None = None

    ## @brief Преобразовать кандидата в payload-словарь.
    #  @return Словарь с полями кандидата.
    def to_payload(self) -> dict[str, object]:
        payload = {
            "path": self.path,
            "category": self.category,
            "reason": self.reason,
            "kind": self.kind,
        }
        if self.item_count is not None:
            payload["item_count"] = self.item_count
        return payload


## @brief План cleanup — список кандидатов на удаление и пересмотр.
#
#  @param safe_delete      Список безопасных для удаления кандидатов.
#  @param keep             Список кандидатов, которые следует оставить.
#  @param manual_review    Список кандидатов, требующих ручного пересмотра.
#  @param targets          Целевые пути плана.
#  @param target_count     Количество целевых путей.
#  @param count            Общее количество кандидатов.
#  @param confirm_command  Команда для подтверждения плана.
#  @param plan_fingerprint SHA256-фингерпринт плана.
#  @param scope_locked     Флаг блокировки scope.
@dataclass
class CleanupPlan:
    """План cleanup — список кандидатов на удаление и пересмотр."""
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

    ## @brief Преобразовать план в payload-словарь.
    #  @return Словарь с полным описанием плана.
    def to_payload(self) -> dict[str, object]:
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


## @brief Проверить, есть ли среди результатов ошибки.
#  @param results Список результатов шагов.
#  @return        `True`, если хотя бы один статус равен `error`.
def has_errors(results: list[StepResult]) -> bool:
    return any(item.status == "error" for item in results)


## @brief Вычислить SHA256-фингерпринт scope cleanup.
#
#  Используется для проверки целостности плана перед подтверждением.
#  @param targets          Целевые пути.
#  @param expanded_scope   Расширенный scope.
#  @param target_count     Количество целевых путей.
#  @param count            Общее количество элементов.
#  @param confirm_template Шаблон команды подтверждения.
#  @return                 SHA256-хеш в шестнадцатеричном виде.
def cleanup_scope_fingerprint(
    *,
    targets: tuple[str, ...],
    expanded_scope: tuple[str, ...],
    target_count: int,
    count: int,
    confirm_template: str,
) -> str:
    payload = {
        "targets": list(targets),
        "expanded_scope": list(expanded_scope),
        "target_count": target_count,
        "count": count,
        "confirm_template": confirm_template,
    }
    normalized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
