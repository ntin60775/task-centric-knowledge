"""Markdown-backed module verification catalog for Module Core."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from task_workflow_runtime.models import DELIVERY_ROW_PLACEHOLDER, normalize_table_value
from task_workflow_runtime.task_markdown import find_section_bounds, split_markdown_row


PASSPORT_SECTION = "## Паспорт"
CHECKS_SECTION = "## Канонические проверки"
EVIDENCE_SECTION = "## Доказательства"
SCENARIOS_SECTION = "## Сценарии"
MANUAL_RESIDUAL_SECTION = "## Ручной остаток"

PASSPORT_FIELDS = (
    "Модуль",
    "Ссылка верификации",
    "Статус готовности",
    "Дата обновления",
)
CHECK_HEADERS = ("ID проверки", "Гейт", "Тип", "Команда", "Блокирует", "Назначение")
EVIDENCE_HEADERS = ("ID доказательства", "Тип", "Значение", "Якорь", "Заметки")
SCENARIO_HEADERS = (
    "ID сценария",
    "Тип",
    "Описание",
    "Обязательные проверки",
    "Обязательные доказательства",
    "Блокирует",
)
MANUAL_RESIDUAL_HEADERS = ("ID риска", "Применимость", "Причина", "Действие контроллера")

ALLOWED_GATES = {"writer", "task-followup"}
ALLOWED_CHECK_KINDS = {"command", "artifact-check"}
ALLOWED_EVIDENCE_KINDS = {
    "test-file",
    "log-marker",
    "trace-assertion",
    "output-snapshot",
    "diagnostic-report",
    "query-snapshot",
}
ALLOWED_SCENARIO_KINDS = {"success", "failure", "regression", "observability"}
ALLOWED_READINESS_STATUSES = {"ready", "partial", "blocked"}
ALLOWED_ACTIONS = {"fix_code", "restore_observability", "strengthen_verification", "controller_decision"}

CHECK_REF_RE = re.compile(r"CHK-[A-Z0-9][A-Z0-9-]*$")
EVIDENCE_REF_RE = re.compile(r"EVD-[A-Z0-9][A-Z0-9-]*$")
SCENARIO_REF_RE = re.compile(r"SCN-[A-Z0-9][A-Z0-9-]*$")
RISK_REF_RE = re.compile(r"RISK-[A-Z0-9][A-Z0-9-]*$")


class ModuleVerificationError(ValueError):
    """Raised when a module verification artifact is invalid."""


@dataclass(frozen=True)
class VerificationCheck:
    ref: str
    gate: str
    kind: str
    command: str
    blocking: bool
    purpose: str


@dataclass(frozen=True)
class VerificationEvidence:
    ref: str
    kind: str
    value: str
    anchor_ref: str
    notes: str


@dataclass(frozen=True)
class VerificationScenario:
    ref: str
    kind: str
    description: str
    required_check_refs: tuple[str, ...]
    required_evidence_refs: tuple[str, ...]
    blocking: bool


@dataclass(frozen=True)
class ManualResidualRisk:
    ref: str
    applies_to: str
    reason: str
    controller_action: str


@dataclass(frozen=True)
class ModuleVerificationRecord:
    path: Path
    module_id: str
    verification_ref: str
    declared_status: str
    updated_at: str
    governed_files: tuple[str, ...]
    checks: dict[str, VerificationCheck]
    evidence: dict[str, VerificationEvidence]
    scenarios: dict[str, VerificationScenario]
    manual_residual: dict[str, ManualResidualRisk]


@dataclass(frozen=True)
class ExecutionReadiness:
    status: str
    blocking_reasons: tuple[str, ...]
    required_verification_refs: tuple[str, ...]
    required_governed_files: tuple[str, ...]
    residual_manual_risk: tuple[str, ...]


@dataclass(frozen=True)
class VerificationExcerpt:
    verification_ref: str
    readiness_status: str
    blocking_reasons: tuple[str, ...]
    writer_checks: tuple[VerificationCheck, ...]
    required_scenarios: tuple[VerificationScenario, ...]
    required_evidence: tuple[VerificationEvidence, ...]
    task_followups: tuple[VerificationCheck, ...]
    manual_residual: tuple[ManualResidualRisk, ...]


@dataclass(frozen=True)
class FailureHandoff:
    contract_ref: str
    scenario: str
    expected_evidence: tuple[str, ...]
    observed_evidence: tuple[str, ...]
    first_divergent_anchor: str
    suggested_next_action: str


def _parse_table_rows(
    lines: list[str],
    title: str,
    expected_headers: tuple[str, ...],
    *,
    required: bool = True,
) -> list[tuple[str, ...]]:
    bounds = find_section_bounds(lines, title)
    if bounds is None:
        if required:
            raise ModuleVerificationError(f"В файле не найден раздел {title!r}.")
        return []
    start_index, end_index = bounds
    rows: list[tuple[str, ...]] = []
    header_seen = False
    for line in lines[start_index + 1 : end_index]:
        cells = split_markdown_row(line)
        if not cells:
            continue
        normalized = tuple(normalize_table_value(cell) for cell in cells)
        if normalized == expected_headers:
            header_seen = True
            continue
        if not header_seen:
            raise ModuleVerificationError(
                f"Раздел {title!r} должен начинаться с канонической строки заголовков таблицы."
            )
        if all(re.fullmatch(r"-+", cell) for cell in normalized):
            continue
        if len(normalized) != len(expected_headers):
            raise ModuleVerificationError(
                f"Раздел {title!r} содержит строку с {len(normalized)} колонками вместо {len(expected_headers)}."
            )
        if normalized[0] == DELIVERY_ROW_PLACEHOLDER:
            continue
        rows.append(normalized)
    return rows


def _parse_passport(lines: list[str]) -> dict[str, str]:
    rows = _parse_table_rows(lines, PASSPORT_SECTION, ("Поле", "Значение"))
    fields: dict[str, str] = {}
    for field, value in rows:
        if field in fields:
            raise ModuleVerificationError(f"Поле {field!r} в разделе паспорта задано более одного раза.")
        fields[field] = value
    missing = [field for field in PASSPORT_FIELDS if field not in fields]
    if missing:
        raise ModuleVerificationError(f"В разделе паспорта отсутствуют обязательные поля: {', '.join(missing)}.")
    status = fields["Статус готовности"]
    if status not in ALLOWED_READINESS_STATUSES:
        raise ModuleVerificationError(
            "Поле `Статус готовности` должно иметь значение `ready`, `partial` или `blocked`."
        )
    return fields


def _validate_ref(ref: str, pattern: re.Pattern[str], label: str) -> None:
    if not pattern.fullmatch(ref):
        raise ModuleVerificationError(f"{label} {ref!r} имеет некорректный формат.")


def _parse_bool(value: str, *, label: str) -> bool:
    if value == "да":
        return True
    if value == "нет":
        return False
    raise ModuleVerificationError(f"Поле {label!r} должно иметь значение `да` или `нет`.")


def _parse_ref_list(value: str) -> tuple[str, ...]:
    normalized = normalize_table_value(value)
    if not normalized or normalized == DELIVERY_ROW_PLACEHOLDER:
        return ()
    refs = tuple(part.strip() for part in normalized.split(",") if part.strip())
    if not refs:
        return ()
    return refs


def _parse_checks(lines: list[str]) -> dict[str, VerificationCheck]:
    rows = _parse_table_rows(lines, CHECKS_SECTION, CHECK_HEADERS)
    checks: dict[str, VerificationCheck] = {}
    for ref, gate, kind, command, blocking, purpose in rows:
        _validate_ref(ref, CHECK_REF_RE, "Check Ref")
        if ref in checks:
            raise ModuleVerificationError(f"Check Ref {ref!r} задан более одного раза.")
        if gate not in ALLOWED_GATES:
            raise ModuleVerificationError(f"Check Ref {ref!r} использует недопустимый Gate {gate!r}.")
        if kind not in ALLOWED_CHECK_KINDS:
            raise ModuleVerificationError(f"Check Ref {ref!r} использует недопустимый Kind {kind!r}.")
        if not command and (gate == "writer" or kind == "command"):
            raise ModuleVerificationError(f"Check Ref {ref!r} должен содержать исполнимую команду.")
        checks[ref] = VerificationCheck(
            ref=ref,
            gate=gate,
            kind=kind,
            command=command,
            blocking=_parse_bool(blocking, label=f"Blocking для {ref}"),
            purpose=purpose,
        )
    return checks


def _parse_evidence(lines: list[str]) -> dict[str, VerificationEvidence]:
    rows = _parse_table_rows(lines, EVIDENCE_SECTION, EVIDENCE_HEADERS)
    evidence: dict[str, VerificationEvidence] = {}
    for ref, kind, value, anchor_ref, notes in rows:
        _validate_ref(ref, EVIDENCE_REF_RE, "Evidence Ref")
        if ref in evidence:
            raise ModuleVerificationError(f"Evidence Ref {ref!r} задан более одного раза.")
        if kind not in ALLOWED_EVIDENCE_KINDS:
            raise ModuleVerificationError(f"Evidence Ref {ref!r} использует недопустимый Kind {kind!r}.")
        if not value:
            raise ModuleVerificationError(f"Evidence Ref {ref!r} должен содержать Value.")
        evidence[ref] = VerificationEvidence(
            ref=ref,
            kind=kind,
            value=value,
            anchor_ref=anchor_ref,
            notes=notes,
        )
    return evidence


def _parse_scenarios(lines: list[str]) -> dict[str, VerificationScenario]:
    rows = _parse_table_rows(lines, SCENARIOS_SECTION, SCENARIO_HEADERS)
    scenarios: dict[str, VerificationScenario] = {}
    for ref, kind, description, check_refs, evidence_refs, blocking in rows:
        _validate_ref(ref, SCENARIO_REF_RE, "Scenario Ref")
        if ref in scenarios:
            raise ModuleVerificationError(f"Scenario Ref {ref!r} задан более одного раза.")
        if kind not in ALLOWED_SCENARIO_KINDS:
            raise ModuleVerificationError(f"Scenario Ref {ref!r} использует недопустимый Kind {kind!r}.")
        if not description:
            raise ModuleVerificationError(f"Scenario Ref {ref!r} должен содержать Description.")
        scenarios[ref] = VerificationScenario(
            ref=ref,
            kind=kind,
            description=description,
            required_check_refs=_parse_ref_list(check_refs),
            required_evidence_refs=_parse_ref_list(evidence_refs),
            blocking=_parse_bool(blocking, label=f"Blocking для {ref}"),
        )
    return scenarios


def _parse_manual_residual(lines: list[str]) -> dict[str, ManualResidualRisk]:
    rows = _parse_table_rows(lines, MANUAL_RESIDUAL_SECTION, MANUAL_RESIDUAL_HEADERS, required=False)
    residual: dict[str, ManualResidualRisk] = {}
    for ref, applies_to, reason, controller_action in rows:
        _validate_ref(ref, RISK_REF_RE, "Risk Ref")
        if ref in residual:
            raise ModuleVerificationError(f"Risk Ref {ref!r} задан более одного раза.")
        residual[ref] = ManualResidualRisk(
            ref=ref,
            applies_to=applies_to,
            reason=reason,
            controller_action=controller_action,
        )
    return residual


def _validate_cross_refs(record: ModuleVerificationRecord) -> None:
    for scenario in record.scenarios.values():
        if scenario.blocking and not scenario.required_check_refs:
            raise ModuleVerificationError(
                f"Blocking Scenario Ref {scenario.ref!r} должен ссылаться минимум на один Check Ref."
            )
        for ref in scenario.required_check_refs:
            if ref not in record.checks:
                raise ModuleVerificationError(
                    f"Scenario Ref {scenario.ref!r} ссылается на неизвестный Check Ref {ref!r}."
                )
        for ref in scenario.required_evidence_refs:
            if ref not in record.evidence:
                raise ModuleVerificationError(
                    f"Scenario Ref {scenario.ref!r} ссылается на неизвестный Evidence Ref {ref!r}."
                )


def _infer_verification_ref_from_path(path: Path) -> str | None:
    parts = path.resolve().parts
    if "knowledge" not in parts:
        return None
    start_index = max(index for index, part in enumerate(parts) if part == "knowledge")
    return Path(*parts[start_index:]).as_posix()


def _looks_like_file_path(value: str) -> bool:
    normalized = value.strip()
    return "/" in normalized or "\\" in normalized or normalized.endswith(
        (".md", ".txt", ".json", ".yaml", ".yml", ".log", ".xml", ".py", ".bsl")
    )


def _collect_evidence_file_paths(
    record: ModuleVerificationRecord,
    evidence_refs: tuple[str, ...],
) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            record.evidence[ref].value.strip()
            for ref in evidence_refs
            if ref in record.evidence and _looks_like_file_path(record.evidence[ref].value)
        )
    )


def load_module_verification(
    path: Path,
    *,
    expected_verification_ref: str | None = None,
    governed_files: tuple[str, ...] = (),
) -> ModuleVerificationRecord:
    verification_path = path.resolve()
    if not verification_path.exists():
        raise ModuleVerificationError(f"Файл модульной верификации не найден: {verification_path}")
    lines = verification_path.read_text(encoding="utf-8").splitlines()
    passport = _parse_passport(lines)
    inferred_verification_ref = expected_verification_ref or _infer_verification_ref_from_path(verification_path)
    if inferred_verification_ref and passport["Ссылка верификации"] != inferred_verification_ref:
        raise ModuleVerificationError(
            "Ссылка верификации в файле не совпадает с ожидаемой ссылкой из внешнего контракта."
        )
    record = ModuleVerificationRecord(
        path=verification_path,
        module_id=passport["Модуль"],
        verification_ref=passport["Ссылка верификации"],
        declared_status=passport["Статус готовности"],
        updated_at=passport["Дата обновления"],
        governed_files=tuple(dict.fromkeys(item for item in governed_files if item)),
        checks=_parse_checks(lines),
        evidence=_parse_evidence(lines),
        scenarios=_parse_scenarios(lines),
        manual_residual=_parse_manual_residual(lines),
    )
    _validate_cross_refs(record)
    return record


def _ready_state(record: ModuleVerificationRecord) -> ExecutionReadiness:
    blocking_reasons: list[str] = []
    required_refs: list[str] = [record.verification_ref]
    required_governed_files = list(record.governed_files)
    blocking_scenarios = [item for item in record.scenarios.values() if item.blocking]
    if not blocking_scenarios:
        blocking_reasons.append("Не определены blocking-сценарии для безопасного writer-pass.")
    for scenario in blocking_scenarios:
        required_refs.append(f"{record.verification_ref}#{scenario.ref}")
        writer_checks = [record.checks[ref] for ref in scenario.required_check_refs if record.checks[ref].gate == "writer"]
        if not writer_checks:
            blocking_reasons.append(
                f"Сценарий {scenario.ref} не содержит writer-level проверки с исполнимой командой."
            )
        for ref in scenario.required_check_refs:
            required_refs.append(f"{record.verification_ref}#{ref}")
        for ref in scenario.required_evidence_refs:
            required_refs.append(f"{record.verification_ref}#{ref}")
            evidence = record.evidence[ref]
            evidence_paths = _collect_evidence_file_paths(record, (ref,))
            has_path_like_value = bool(evidence_paths)
            required_governed_files.extend(evidence_paths)
            if (
                evidence.anchor_ref == DELIVERY_ROW_PLACEHOLDER
                and not record.governed_files
                and not has_path_like_value
            ):
                blocking_reasons.append(
                    f"Evidence Ref {ref!r} не имеет anchor_ref и governed-file fallback для failure handoff."
                )
    status = "ready" if not blocking_reasons else "partial"
    if record.declared_status != status:
        blocking_reasons.append(
            f"Заявленный статус готовности {record.declared_status!r} не совпадает с вычисленным {status!r}."
        )
        status = "partial"
    return ExecutionReadiness(
        status=status,
        blocking_reasons=tuple(blocking_reasons),
        required_verification_refs=tuple(dict.fromkeys(required_refs)),
        required_governed_files=tuple(dict.fromkeys(required_governed_files)),
        residual_manual_risk=tuple(risk.ref for risk in record.manual_residual.values()),
    )


def resolve_execution_readiness(
    path: Path,
    *,
    expected_verification_ref: str | None = None,
    governed_files: tuple[str, ...] = (),
) -> ExecutionReadiness:
    inferred_verification_ref = expected_verification_ref or _infer_verification_ref_from_path(path)
    normalized_governed_files = tuple(dict.fromkeys(item for item in governed_files if item))
    try:
        record = load_module_verification(
            path,
            expected_verification_ref=expected_verification_ref,
            governed_files=normalized_governed_files,
        )
    except ModuleVerificationError as error:
        required_refs = (inferred_verification_ref,) if inferred_verification_ref else ()
        return ExecutionReadiness(
            status="blocked",
            blocking_reasons=(str(error),),
            required_verification_refs=required_refs,
            required_governed_files=normalized_governed_files,
            residual_manual_risk=(),
        )
    return _ready_state(record)


def build_verification_excerpt(record: ModuleVerificationRecord) -> VerificationExcerpt:
    readiness = _ready_state(record)
    blocking_scenarios = tuple(item for item in record.scenarios.values() if item.blocking)
    required_evidence_refs: list[str] = []
    for scenario in blocking_scenarios:
        required_evidence_refs.extend(scenario.required_evidence_refs)
    required_evidence = tuple(
        record.evidence[ref] for ref in dict.fromkeys(required_evidence_refs) if ref in record.evidence
    )
    writer_checks = tuple(item for item in record.checks.values() if item.gate == "writer")
    task_followups = tuple(item for item in record.checks.values() if item.gate == "task-followup")
    manual_residual = tuple(record.manual_residual.values())
    return VerificationExcerpt(
        verification_ref=record.verification_ref,
        readiness_status=readiness.status,
        blocking_reasons=readiness.blocking_reasons,
        writer_checks=writer_checks,
        required_scenarios=blocking_scenarios,
        required_evidence=required_evidence,
        task_followups=task_followups,
        manual_residual=manual_residual,
    )


def build_failure_handoff(
    record: ModuleVerificationRecord,
    *,
    reference: str,
    observed_evidence: str | tuple[str, ...] | list[str],
    anchor_override: str | None = None,
    suggested_next_action: str | None = None,
) -> FailureHandoff:
    observed = (observed_evidence,) if isinstance(observed_evidence, str) else tuple(observed_evidence)
    scenario_text = ""
    evidence_refs: tuple[str, ...] = ()
    default_action = "controller_decision"
    if reference in record.scenarios:
        scenario = record.scenarios[reference]
        scenario_text = scenario.description
        evidence_refs = scenario.required_evidence_refs
        writer_checks = [record.checks[ref] for ref in scenario.required_check_refs if record.checks[ref].gate == "writer"]
        default_action = "fix_code" if writer_checks else "strengthen_verification"
    elif reference in record.checks:
        check = record.checks[reference]
        scenario_text = check.purpose
        linked_evidence: list[str] = []
        for scenario in record.scenarios.values():
            if reference in scenario.required_check_refs:
                linked_evidence.extend(scenario.required_evidence_refs)
        evidence_refs = tuple(dict.fromkeys(linked_evidence))
        default_action = "fix_code" if check.gate == "writer" else "controller_decision"
    else:
        raise ModuleVerificationError(f"Неизвестная ссылка для failure handoff: {reference!r}.")
    expected_evidence = tuple(record.evidence[ref].value for ref in evidence_refs if ref in record.evidence)
    evidence_file_paths = _collect_evidence_file_paths(record, evidence_refs)
    anchor = next(
        (
            record.evidence[ref].anchor_ref
            for ref in evidence_refs
            if ref in record.evidence and record.evidence[ref].anchor_ref != DELIVERY_ROW_PLACEHOLDER
        ),
        anchor_override
        or next(iter(record.governed_files), None)
        or next(iter(evidence_file_paths), None)
        or str(record.path),
    )
    action = suggested_next_action or default_action
    if action not in ALLOWED_ACTIONS:
        raise ModuleVerificationError(f"Недопустимое suggested_next_action: {action!r}.")
    return FailureHandoff(
        contract_ref=f"{record.verification_ref}#{reference}",
        scenario=scenario_text,
        expected_evidence=expected_evidence,
        observed_evidence=observed,
        first_divergent_anchor=anchor,
        suggested_next_action=action,
    )
