"""Read-only Module Core projections for `module` / `file` query commands."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
import re

from task_workflow_runtime.models import DELIVERY_ROW_PLACEHOLDER, normalize_table_value
from task_workflow_runtime.task_markdown import find_section_bounds, split_markdown_row

from .file_local_contracts import (
    FILE_LOCAL_POLICY_FILENAME,
    FileLocalPolicy,
    FileLocalPolicyError,
    load_file_local_policy,
    parse_file_local_contracts,
)
from .verification import (
    ExecutionReadiness,
    ModuleVerificationError,
    ModuleVerificationRecord,
    build_verification_excerpt,
    load_module_verification,
    resolve_execution_readiness,
)


MODULES_ROOT = Path("knowledge/modules")
REGISTRY_FILENAME = "registry.md"
PASSPORT_FILENAME = "module.md"
VERIFICATION_FILENAME = "verification.md"
PLACEHOLDER = "—"

PASSPORT_SECTION = "## Паспорт"
SCOPE_SECTION = "## Назначение и границы"
OWNED_SURFACE_SECTION = "## Управляемая поверхность"
PUBLIC_CONTRACTS_SECTION = "## Публичные контракты"
RELATIONS_SECTION = "## Связи"
REGISTRY_TABLE_SECTION = "## Таблица"

PASSPORT_FIELDS = (
    "Модуль",
    "Слаг",
    "Название",
    "Краткое назначение",
    "Ссылка верификации",
    "Ссылка file-local policy",
    "Статус готовности исполнения",
    "Краткая сводка готовности",
    "Задача происхождения",
    "Последняя задача обновления",
    "Дата обновления",
)
OWNED_SURFACE_HEADERS = ("Тип", "Путь", "Роль", "Причина владения")
PUBLIC_CONTRACT_HEADERS = ("Контракт", "Форма", "Ссылка/маркер", "Для кого")
RELATION_HEADERS = ("Тип связи", "Цель", "Статус", "Заметка")
REGISTRY_HEADERS = (
    "MODULE-ID",
    "Slug",
    "Source State",
    "Readiness",
    "Паспорт",
    "Верификация",
    "File Policy",
    "Каталог",
    "Краткое назначение",
)

MODULE_ID_RE = re.compile(r"M-[A-Z0-9][A-Z0-9-]*$")
SLUG_RE = re.compile(r"[a-z0-9][a-z0-9-]*$")
ALLOWED_SOURCE_STATES = {"verification_only", "passport_ready", "partial"}
ALLOWED_READINESS_STATUSES = {"ready", "partial", "blocked"}
ALLOWED_RELATION_TYPES = {"depends_on"}
ALLOWED_RELATION_STATUSES = {"required", "informational", "planned"}


@dataclass
class WarningItem:
    code: str
    severity: str
    detail: str
    path: str | None = None


@dataclass(frozen=True)
class OwnedSurfaceItem:
    kind: str
    path_ref: str
    role: str
    ownership_reason: str


@dataclass(frozen=True)
class PublicContractItem:
    contract: str
    kind: str
    reference: str
    audience: str


@dataclass(frozen=True)
class RelationEnvelopeItem:
    relation_type: str
    target: str
    status: str
    notes: str


@dataclass(frozen=True)
class ModulePassport:
    path: Path
    module_id: str
    slug: str
    title: str
    purpose_summary: str
    verification_ref: str
    file_local_policy_ref: str | None
    execution_readiness_status: str
    execution_readiness_summary: str
    origin_task_ref: str | None
    last_updated_task_ref: str | None
    updated_at: str
    scope_text: str
    owned_surface: tuple[OwnedSurfaceItem, ...]
    public_contracts: tuple[PublicContractItem, ...]
    relation_envelope: tuple[RelationEnvelopeItem, ...]


@dataclass(frozen=True)
class RegistryRow:
    module_id: str
    slug: str
    source_state: str
    readiness_status: str
    passport_ref: str | None
    verification_ref: str | None
    file_local_policy_ref: str | None
    catalog_ref: str
    purpose_summary: str
    path: str


@dataclass
class ModuleSummary:
    module_id: str
    slug: str
    source_state: str
    readiness_status: str
    passport_ref: str | None
    verification_ref: str | None
    governed_files: list[str]
    purpose_summary: str | None = None
    warnings: list[WarningItem] = field(default_factory=list)


@dataclass
class ModuleRecord:
    summary: ModuleSummary
    verification_record: ModuleVerificationRecord | None
    verification_excerpt: dict[str, object] | None
    public_truth: dict[str, object]
    readiness: dict[str, object]
    relations: dict[str, object]
    files: dict[str, object]
    verification_anchors: dict[str, list[dict[str, str]]]
    failure_handoff_refs: dict[str, list[str]]
    declared_relations: tuple[RelationEnvelopeItem, ...]
    has_valid_passport: bool
    file_local_policy: FileLocalPolicy | None


@dataclass
class ModuleIndex:
    records: list[ModuleRecord]
    duplicate_module_ids: dict[str, list[ModuleRecord]]
    warnings: list[WarningItem] = field(default_factory=list)


@dataclass
class FileOwner:
    module_id: str
    slug: str
    source_state: str
    readiness_status: str
    passport_ref: str | None
    verification_ref: str | None


class ModulePassportError(ValueError):
    """Raised when a module passport is invalid."""


def warning_to_dict(item: WarningItem) -> dict[str, str | None]:
    return asdict(item)


def module_summary_to_dict(item: ModuleSummary) -> dict[str, object]:
    return {
        "module_id": item.module_id,
        "slug": item.slug,
        "source_state": item.source_state,
        "readiness_status": item.readiness_status,
        "passport_ref": item.passport_ref,
        "verification_ref": item.verification_ref,
        "governed_files": item.governed_files,
        "purpose_summary": item.purpose_summary,
        "warnings": [warning_to_dict(warning) for warning in item.warnings],
    }


def module_record_to_dict(item: ModuleRecord) -> dict[str, object]:
    return {
        "module_id": item.summary.module_id,
        "slug": item.summary.slug,
        "source_state": item.summary.source_state,
        "passport_ref": item.summary.passport_ref,
        "verification_ref": item.summary.verification_ref,
        "governed_files": item.summary.governed_files,
        "purpose_summary": item.summary.purpose_summary,
        "public_truth": item.public_truth,
        "readiness": item.readiness,
        "verification_excerpt": item.verification_excerpt,
        "relations": item.relations,
        "files": item.files,
        "warnings": [warning_to_dict(warning) for warning in item.summary.warnings],
    }


def file_owner_to_dict(item: FileOwner) -> dict[str, object]:
    return asdict(item)


def _relative_path(project_root: Path, path: Path) -> str:
    return path.relative_to(project_root).as_posix()


def _is_within_project(path: Path, project_root: Path) -> bool:
    try:
        path.relative_to(project_root)
    except ValueError:
        return False
    return True


def _looks_like_file_path(value: str) -> bool:
    normalized = value.strip()
    return "/" in normalized or "\\" in normalized or normalized.endswith(
        (".md", ".txt", ".json", ".yaml", ".yml", ".log", ".xml", ".py", ".bsl")
    )


def _normalize_optional(value: str) -> str | None:
    normalized = normalize_table_value(value)
    if not normalized or normalized == PLACEHOLDER:
        return None
    return normalized


def _normalize_project_file_ref(project_root: Path, value: str) -> str | None:
    normalized = normalize_table_value(value).replace("\\", "/")
    if not normalized or normalized == PLACEHOLDER or not _looks_like_file_path(normalized):
        return None
    candidate = Path(normalized)
    if candidate.is_absolute():
        try:
            return candidate.relative_to(project_root).as_posix()
        except ValueError:
            return candidate.as_posix()
    return candidate.as_posix()


def _normalize_catalog_ref(project_root: Path, directory_path: Path) -> str:
    return f"{_relative_path(project_root, directory_path)}/"


def _derive_slug(directory_name: str, module_id: str) -> str:
    prefix = f"{module_id}-"
    if directory_name.startswith(prefix):
        suffix = directory_name[len(prefix) :]
        if suffix:
            return suffix
    return directory_name


def _source_state(*, passport: ModulePassport | None, verification_ref: str | None) -> str:
    if passport is not None and verification_ref:
        return "passport_ready"
    if verification_ref and passport is None:
        return "verification_only"
    return "partial"


def _module_warning(code: str, detail: str, *, path: str | None = None, severity: str = "warning") -> WarningItem:
    return WarningItem(code=code, severity=severity, detail=detail, path=path)


def _serialize_verification_excerpt(record: ModuleVerificationRecord) -> dict[str, object]:
    excerpt = build_verification_excerpt(record)
    return {
        "verification_ref": excerpt.verification_ref,
        "readiness_status": excerpt.readiness_status,
        "blocking_reasons": list(excerpt.blocking_reasons),
        "writer_checks": [asdict(item) for item in excerpt.writer_checks],
        "required_scenarios": [asdict(item) for item in excerpt.required_scenarios],
        "required_evidence": [asdict(item) for item in excerpt.required_evidence],
        "task_followups": [asdict(item) for item in excerpt.task_followups],
        "manual_residual": [asdict(item) for item in excerpt.manual_residual],
    }


def _collect_path_anchors(
    project_root: Path,
    record: ModuleVerificationRecord,
) -> tuple[dict[str, list[dict[str, str]]], dict[str, list[str]], list[str]]:
    anchors_by_path: dict[str, list[dict[str, str]]] = {}
    handoff_refs_by_path: dict[str, list[str]] = {}
    evidence_file_refs: list[str] = []
    for evidence in record.evidence.values():
        relative_ref = _normalize_project_file_ref(project_root, evidence.value)
        if relative_ref is None:
            continue
        evidence_file_refs.append(relative_ref)
        anchors = anchors_by_path.setdefault(relative_ref, [])
        anchors.append(
            {
                "module_id": record.module_id,
                "verification_ref": record.verification_ref,
                "evidence_ref": evidence.ref,
                "kind": evidence.kind,
                "value": evidence.value,
                "anchor": evidence.anchor_ref,
            }
        )
    for scenario in record.scenarios.values():
        contract_ref = f"{record.verification_ref}#{scenario.ref}"
        for evidence_ref in scenario.required_evidence_refs:
            evidence = record.evidence.get(evidence_ref)
            if evidence is None:
                continue
            relative_ref = _normalize_project_file_ref(project_root, evidence.value)
            if relative_ref is None:
                continue
            refs = handoff_refs_by_path.setdefault(relative_ref, [])
            if contract_ref not in refs:
                refs.append(contract_ref)
    return anchors_by_path, handoff_refs_by_path, sorted(dict.fromkeys(evidence_file_refs))


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


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
            raise ModulePassportError(f"В файле не найден раздел {title!r}.")
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
            raise ModulePassportError(
                f"Раздел {title!r} должен начинаться с канонической строки заголовков таблицы."
            )
        if all(re.fullmatch(r"-+", cell) for cell in normalized):
            continue
        if len(normalized) != len(expected_headers):
            raise ModulePassportError(
                f"Раздел {title!r} содержит строку с {len(normalized)} колонками вместо {len(expected_headers)}."
            )
        if normalized[0] == DELIVERY_ROW_PLACEHOLDER:
            continue
        rows.append(normalized)
    return rows


def _parse_passport_fields(lines: list[str]) -> dict[str, str]:
    rows = _parse_table_rows(lines, PASSPORT_SECTION, ("Поле", "Значение"))
    fields: dict[str, str] = {}
    for field, value in rows:
        if field in fields:
            raise ModulePassportError(f"Поле {field!r} в разделе паспорта задано более одного раза.")
        fields[field] = value
    missing = [field for field in PASSPORT_FIELDS if field not in fields]
    if missing:
        raise ModulePassportError(f"В разделе паспорта отсутствуют обязательные поля: {', '.join(missing)}.")
    return fields


def _parse_section_text(lines: list[str], title: str) -> str:
    bounds = find_section_bounds(lines, title)
    if bounds is None:
        raise ModulePassportError(f"В файле не найден раздел {title!r}.")
    start_index, end_index = bounds
    text_lines = [line.rstrip() for line in lines[start_index + 1 : end_index] if line.strip()]
    if not text_lines:
        raise ModulePassportError(f"Раздел {title!r} не должен быть пустым.")
    return "\n".join(text_lines)


def load_module_passport(project_root: Path, passport_path: Path) -> ModulePassport:
    lines = _read_lines(passport_path)
    passport = _parse_passport_fields(lines)

    module_id = passport["Модуль"]
    slug = passport["Слаг"]
    if not MODULE_ID_RE.fullmatch(module_id):
        raise ModulePassportError("Поле `Модуль` должно иметь формат `M-...` в upper-kebab виде.")
    if not SLUG_RE.fullmatch(slug):
        raise ModulePassportError("Поле `Слаг` должно иметь lower-kebab формат.")

    expected_dir_name = f"{module_id}-{slug}"
    if passport_path.parent.name != expected_dir_name:
        raise ModulePassportError(
            f"Каталог модуля должен называться `{expected_dir_name}`, а не `{passport_path.parent.name}`."
        )

    verification_ref = passport["Ссылка верификации"]
    expected_verification_ref = f"knowledge/modules/{expected_dir_name}/verification.md"
    if verification_ref != expected_verification_ref:
        raise ModulePassportError(
            "Поле `Ссылка верификации` должно указывать на канонический verification.md внутри каталога модуля."
        )

    expected_file_local_policy_ref = f"knowledge/modules/{expected_dir_name}/{FILE_LOCAL_POLICY_FILENAME}"
    readiness_status = passport["Статус готовности исполнения"]
    if readiness_status not in ALLOWED_READINESS_STATUSES:
        raise ModulePassportError(
            "Поле `Статус готовности исполнения` должно иметь значение `ready`, `partial` или `blocked`."
        )

    file_local_policy_ref = _normalize_optional(passport["Ссылка file-local policy"])
    if file_local_policy_ref is not None and Path(file_local_policy_ref).is_absolute():
        raise ModulePassportError("Поле `Ссылка file-local policy` не может быть абсолютным путём.")
    if file_local_policy_ref is not None and file_local_policy_ref != expected_file_local_policy_ref:
        raise ModulePassportError(
            "Поле `Ссылка file-local policy` должно указывать на канонический `file-local-policy.md` внутри каталога модуля."
        )

    owned_surface_rows = _parse_table_rows(lines, OWNED_SURFACE_SECTION, OWNED_SURFACE_HEADERS)
    if not owned_surface_rows:
        raise ModulePassportError("Раздел `## Управляемая поверхность` должен содержать хотя бы одну строку.")
    owned_surface: list[OwnedSurfaceItem] = []
    for kind, path_ref, role, reason in owned_surface_rows:
        normalized_path = _normalize_project_file_ref(project_root, path_ref)
        if normalized_path is None:
            raise ModulePassportError("Каждая строка управляемой поверхности должна ссылаться на project-relative путь.")
        if Path(path_ref).is_absolute():
            raise ModulePassportError("Абсолютные пути в `## Управляемая поверхность` запрещены.")
        owned_surface.append(
            OwnedSurfaceItem(kind=kind, path_ref=normalized_path, role=role, ownership_reason=reason)
        )

    public_contract_rows = _parse_table_rows(lines, PUBLIC_CONTRACTS_SECTION, PUBLIC_CONTRACT_HEADERS)
    if not public_contract_rows:
        raise ModulePassportError("Раздел `## Публичные контракты` должен содержать хотя бы одну строку.")
    public_contracts = tuple(
        PublicContractItem(contract=contract, kind=kind, reference=reference, audience=audience)
        for contract, kind, reference, audience in public_contract_rows
    )

    relation_rows = _parse_table_rows(lines, RELATIONS_SECTION, RELATION_HEADERS)
    relation_envelope = tuple(
        RelationEnvelopeItem(relation_type=relation_type, target=target, status=status, notes=notes)
        for relation_type, target, status, notes in relation_rows
    )

    return ModulePassport(
        path=passport_path,
        module_id=module_id,
        slug=slug,
        title=passport["Название"],
        purpose_summary=passport["Краткое назначение"],
        verification_ref=verification_ref,
        file_local_policy_ref=file_local_policy_ref,
        execution_readiness_status=readiness_status,
        execution_readiness_summary=passport["Краткая сводка готовности"],
        origin_task_ref=_normalize_optional(passport["Задача происхождения"]),
        last_updated_task_ref=_normalize_optional(passport["Последняя задача обновления"]),
        updated_at=passport["Дата обновления"],
        scope_text=_parse_section_text(lines, SCOPE_SECTION),
        owned_surface=tuple(owned_surface),
        public_contracts=public_contracts,
        relation_envelope=relation_envelope,
    )


def _parse_registry(project_root: Path) -> tuple[dict[str, RegistryRow], list[WarningItem]]:
    registry_path = project_root / MODULES_ROOT / REGISTRY_FILENAME
    if not registry_path.exists():
        return {}, []
    lines = _read_lines(registry_path)
    try:
        rows = _parse_table_rows(lines, REGISTRY_TABLE_SECTION, REGISTRY_HEADERS)
    except ModulePassportError as error:
        return {}, [_module_warning("module_registry_invalid", str(error), path=_relative_path(project_root, registry_path))]

    registry_rows: dict[str, RegistryRow] = {}
    warnings: list[WarningItem] = []
    seen_slugs: dict[str, RegistryRow] = {}
    for (
        module_id,
        slug,
        source_state,
        readiness,
        passport_ref,
        verification_ref,
        file_policy_ref,
        catalog_ref,
        purpose_summary,
    ) in rows:
        if module_id in registry_rows:
            warnings.append(
                _module_warning(
                    "module_registry_duplicate_module_id",
                    f"В module registry найден дубликат MODULE-ID `{module_id}`.",
                    path=_relative_path(project_root, registry_path),
                )
            )
            continue
        if slug in seen_slugs:
            warnings.append(
                _module_warning(
                    "module_registry_duplicate_slug",
                    f"В module registry найден дубликат slug `{slug}`.",
                    path=_relative_path(project_root, registry_path),
                )
            )
            continue
        if source_state not in ALLOWED_SOURCE_STATES:
            warnings.append(
                _module_warning(
                    "module_registry_invalid_source_state",
                    f"Строка `{module_id}` использует недопустимый Source State `{source_state}`.",
                    path=_relative_path(project_root, registry_path),
                )
            )
        if readiness not in ALLOWED_READINESS_STATUSES:
            warnings.append(
                _module_warning(
                    "module_registry_invalid_readiness",
                    f"Строка `{module_id}` использует недопустимый Readiness `{readiness}`.",
                    path=_relative_path(project_root, registry_path),
                )
            )
        row = RegistryRow(
            module_id=module_id,
            slug=slug,
            source_state=source_state,
            readiness_status=readiness,
            passport_ref=_normalize_optional(passport_ref),
            verification_ref=_normalize_optional(verification_ref),
            file_local_policy_ref=_normalize_optional(file_policy_ref),
            catalog_ref=catalog_ref,
            purpose_summary=purpose_summary,
            path=_relative_path(project_root, registry_path),
        )
        registry_rows[module_id] = row
        seen_slugs[slug] = row
    return registry_rows, warnings


def _readiness_without_verification(passport: ModulePassport | None, passport_ref: str | None) -> ExecutionReadiness:
    blocking_reasons = ("Модульный passport существует без канонического verification.md.",)
    return ExecutionReadiness(
        status="blocked",
        blocking_reasons=blocking_reasons,
        required_verification_refs=((passport.verification_ref,) if passport is not None else ()),
        required_governed_files=tuple(item.path_ref for item in passport.owned_surface) if passport is not None else (),
        residual_manual_risk=(passport_ref or "verification_missing",),
    )


def _blocked_readiness(
    *,
    reason: str,
    expected_verification_ref: str | None = None,
    governed_files: tuple[str, ...] = (),
    residual_manual_risk: tuple[str, ...] = (),
) -> ExecutionReadiness:
    required_refs = (expected_verification_ref,) if expected_verification_ref else ()
    return ExecutionReadiness(
        status="blocked",
        blocking_reasons=(reason,),
        required_verification_refs=required_refs,
        required_governed_files=governed_files,
        residual_manual_risk=residual_manual_risk,
    )


def _registry_expected_row(
    project_root: Path,
    directory_path: Path,
    *,
    passport: ModulePassport | None,
    passport_ref: str | None,
    verification_ref: str | None,
    source_state: str,
    readiness_status: str,
    purpose_summary: str | None,
) -> dict[str, str | None]:
    file_local_policy_ref = passport.file_local_policy_ref if passport is not None else None
    return {
        "Slug": passport.slug if passport is not None else None,
        "Source State": source_state,
        "Readiness": readiness_status,
        "Паспорт": passport_ref,
        "Верификация": verification_ref,
        "File Policy": file_local_policy_ref,
        "Каталог": _normalize_catalog_ref(project_root, directory_path),
        "Краткое назначение": purpose_summary,
    }


def _compare_registry_row(
    registry_row: RegistryRow | None,
    *,
    expected: dict[str, str | None],
    path: str | None,
) -> list[WarningItem]:
    if registry_row is None:
        return [
            _module_warning(
                "module_registry_missing_row",
                "Для governed module отсутствует строка в `knowledge/modules/registry.md`.",
                path=path,
            )
        ]
    mismatches: list[str] = []
    if expected["Slug"] and registry_row.slug != expected["Slug"]:
        mismatches.append("Slug")
    if registry_row.source_state != expected["Source State"]:
        mismatches.append("Source State")
    if registry_row.readiness_status != expected["Readiness"]:
        mismatches.append("Readiness")
    if registry_row.passport_ref != expected["Паспорт"]:
        mismatches.append("Паспорт")
    if registry_row.verification_ref != expected["Верификация"]:
        mismatches.append("Верификация")
    if registry_row.file_local_policy_ref != expected["File Policy"]:
        mismatches.append("File Policy")
    if registry_row.catalog_ref != expected["Каталог"]:
        mismatches.append("Каталог")
    if expected["Краткое назначение"] and registry_row.purpose_summary != expected["Краткое назначение"]:
        mismatches.append("Краткое назначение")
    if not mismatches:
        return []
    return [
        _module_warning(
            "module_registry_drift",
            "Строка в `knowledge/modules/registry.md` расходится с каноническим module passport: "
            + ", ".join(mismatches)
            + ".",
            path=registry_row.path,
        )
    ]


def _empty_relation_summary() -> dict[str, int]:
    return {
        "depends_on_total": 0,
        "depends_on_required": 0,
        "depends_on_informational": 0,
        "depends_on_planned": 0,
        "used_by_total": 0,
    }


def _relation_reason(*, unavailable: bool = False) -> str:
    if unavailable:
        return "Module passport недоступен или невалиден; relation-truth не может быть собран."
    return "Некоторые relation rows невалидны или ссылаются на отсутствующие governed modules."


def _module_ref_fields(record: ModuleRecord, *, prefix: str) -> dict[str, object]:
    return {
        f"{prefix}_module_id": record.summary.module_id,
        f"{prefix}_slug": record.summary.slug,
        f"{prefix}_source_state": record.summary.source_state,
        f"{prefix}_readiness_status": record.summary.readiness_status,
        f"{prefix}_passport_ref": record.summary.passport_ref,
        f"{prefix}_verification_ref": record.summary.verification_ref,
    }


def _build_relation_payloads(module_index: ModuleIndex) -> None:
    unique_records_by_id = {
        record.summary.module_id.casefold(): record
        for record in module_index.records
        if record.summary.module_id.casefold() not in module_index.duplicate_module_ids
    }
    outgoing_by_module_id: dict[str, list[dict[str, object]]] = {}
    reverse_by_module_id: dict[str, list[dict[str, object]]] = {}
    degraded_by_module_id: dict[str, bool] = {}

    for record in module_index.records:
        module_id_key = record.summary.module_id.casefold()
        outgoing_items: list[dict[str, object]] = []
        degraded = False
        seen_edges: set[tuple[str, str]] = set()
        if record.has_valid_passport:
            for relation in record.declared_relations:
                relation_type = normalize_table_value(relation.relation_type)
                relation_status = normalize_table_value(relation.status)
                target_module_id = normalize_table_value(relation.target)
                relation_key = (relation_type.casefold(), target_module_id.casefold())

                if relation_type not in ALLOWED_RELATION_TYPES:
                    degraded = True
                    record.summary.warnings.append(
                        _module_warning(
                            "module_relation_invalid_type",
                            f"Недопустимый тип связи `{relation_type}`; v1 поддерживает только `depends_on`.",
                            path=record.summary.passport_ref,
                        )
                    )
                    continue
                if relation_status not in ALLOWED_RELATION_STATUSES:
                    degraded = True
                    record.summary.warnings.append(
                        _module_warning(
                            "module_relation_invalid_status",
                            (
                                f"Недопустимый relation status `{relation_status}`; "
                                "ожидается `required`, `informational` или `planned`."
                            ),
                            path=record.summary.passport_ref,
                        )
                    )
                    continue
                if not MODULE_ID_RE.fullmatch(target_module_id):
                    degraded = True
                    record.summary.warnings.append(
                        _module_warning(
                            "module_relation_invalid_target",
                            "Цель связи должна быть exact MODULE-ID формата `M-...`.",
                            path=record.summary.passport_ref,
                        )
                    )
                    continue
                if target_module_id.casefold() == module_id_key:
                    degraded = True
                    record.summary.warnings.append(
                        _module_warning(
                            "module_relation_self_reference",
                            "Self-edge в relation layer запрещён; модуль не может зависеть от самого себя.",
                            path=record.summary.passport_ref,
                        )
                    )
                    continue
                if relation_key in seen_edges:
                    degraded = True
                    record.summary.warnings.append(
                        _module_warning(
                            "module_relation_duplicate",
                            (
                                f"Связь `{relation_type}` -> `{target_module_id}` объявлена более одного раза; "
                                "допускается только один edge на пару type/target."
                            ),
                            path=record.summary.passport_ref,
                        )
                    )
                    continue
                seen_edges.add(relation_key)

                target_record = unique_records_by_id.get(target_module_id.casefold())
                if target_record is None:
                    degraded = True
                    record.summary.warnings.append(
                        _module_warning(
                            "module_relation_target_missing",
                            (
                                f"Целевой governed module `{target_module_id}` не найден "
                                "или неразрешим в текущем Module Core scope."
                            ),
                            path=record.summary.passport_ref,
                        )
                    )

                outgoing_item = {
                    "relation_type": relation_type,
                    "relation_status": relation_status,
                    "target_module_id": target_module_id,
                    "target_slug": (target_record.summary.slug if target_record is not None else None),
                    "target_source_state": (target_record.summary.source_state if target_record is not None else None),
                    "target_readiness_status": (
                        target_record.summary.readiness_status if target_record is not None else None
                    ),
                    "target_passport_ref": (target_record.summary.passport_ref if target_record is not None else None),
                    "target_verification_ref": (
                        target_record.summary.verification_ref if target_record is not None else None
                    ),
                    "notes": relation.notes,
                }
                outgoing_items.append(outgoing_item)
                if target_record is not None:
                    reverse_by_module_id.setdefault(target_module_id.casefold(), []).append(
                        {
                            **_module_ref_fields(record, prefix="source"),
                            "relation_type": relation_type,
                            "relation_status": relation_status,
                            "notes": relation.notes,
                        }
                    )

        outgoing_by_module_id[module_id_key] = outgoing_items
        degraded_by_module_id[module_id_key] = degraded

    for record in module_index.records:
        module_id_key = record.summary.module_id.casefold()
        if not record.has_valid_passport:
            record.relations = {
                "status": "unavailable",
                "reason": _relation_reason(unavailable=True),
                "outgoing": [],
                "used_by": [],
                "summary": _empty_relation_summary(),
            }
            continue

        outgoing_items = outgoing_by_module_id.get(module_id_key, [])
        used_by_items = reverse_by_module_id.get(module_id_key, [])
        summary = _empty_relation_summary()
        summary["depends_on_total"] = len(outgoing_items)
        summary["depends_on_required"] = sum(1 for item in outgoing_items if item["relation_status"] == "required")
        summary["depends_on_informational"] = sum(
            1 for item in outgoing_items if item["relation_status"] == "informational"
        )
        summary["depends_on_planned"] = sum(1 for item in outgoing_items if item["relation_status"] == "planned")
        summary["used_by_total"] = len(used_by_items)

        if degraded_by_module_id.get(module_id_key):
            record.relations = {
                "status": "degraded",
                "reason": _relation_reason(),
                "outgoing": outgoing_items,
                "used_by": used_by_items,
                "summary": summary,
            }
            continue

        record.relations = {
            "status": "ready",
            "outgoing": outgoing_items,
            "used_by": used_by_items,
            "summary": summary,
        }


def _record_from_directory(
    project_root: Path,
    directory_path: Path,
    registry_rows: dict[str, RegistryRow],
) -> ModuleRecord:
    passport_path = directory_path / PASSPORT_FILENAME
    verification_path = directory_path / VERIFICATION_FILENAME
    passport_ref = _relative_path(project_root, passport_path) if passport_path.exists() else None
    verification_ref = _relative_path(project_root, verification_path) if verification_path.exists() else None
    warnings: list[WarningItem] = []

    passport: ModulePassport | None = None
    if passport_path.exists():
        try:
            passport = load_module_passport(project_root, passport_path)
        except ModulePassportError as error:
            warnings.append(_module_warning("module_passport_invalid", str(error), path=passport_ref))

    readiness_payload: ExecutionReadiness
    verification_record: ModuleVerificationRecord | None = None
    verification_excerpt: dict[str, object] | None = None
    file_local_policy: FileLocalPolicy | None = None
    anchors_by_path: dict[str, list[dict[str, str]]] = {}
    handoff_refs_by_path: dict[str, list[str]] = {}
    evidence_file_refs: list[str] = []

    if verification_path.exists():
        readiness_payload = resolve_execution_readiness(verification_path)
        try:
            verification_record = load_module_verification(
                verification_path,
                expected_verification_ref=(passport.verification_ref if passport is not None else None),
                governed_files=tuple(item.path_ref for item in passport.owned_surface) if passport is not None else (),
            )
            verification_excerpt = _serialize_verification_excerpt(verification_record)
            anchors_by_path, handoff_refs_by_path, evidence_file_refs = _collect_path_anchors(project_root, verification_record)
        except ModuleVerificationError as error:
            warnings.append(_module_warning("verification_invalid", str(error), path=verification_ref))
            readiness_payload = resolve_execution_readiness(
                verification_path,
                expected_verification_ref=(passport.verification_ref if passport is not None else None),
                governed_files=tuple(item.path_ref for item in passport.owned_surface) if passport is not None else (),
            )
    else:
        readiness_payload = _readiness_without_verification(passport, passport_ref)

    module_id = passport.module_id if passport is not None else (
        verification_record.module_id if verification_record is not None else directory_path.name
    )
    slug = passport.slug if passport is not None else _derive_slug(directory_path.name, module_id)

    if passport is not None and verification_ref is None:
        warnings.append(
            _module_warning(
                "module_verification_missing",
                "Для module passport отсутствует канонический `verification.md`.",
                path=passport_ref,
            )
        )
    if passport is None and verification_ref is not None:
        warnings.append(
            _module_warning(
                "module_passport_missing",
                "Паспорт модуля ещё не внедрён; shared/public truth ограничен verification layer.",
                path=verification_ref,
            )
        )
    if passport is not None and verification_ref is not None and passport.verification_ref != verification_ref:
        warnings.append(
            _module_warning(
                "module_passport_verification_mismatch",
                "Ссылка на verification.md в module passport расходится с фактическим путём модуля.",
                path=passport_ref,
            )
        )
    if (
        passport is not None
        and verification_record is not None
        and verification_record.module_id != passport.module_id
    ):
        warnings.append(
            _module_warning(
                "module_passport_verification_module_mismatch",
                "MODULE-ID в module passport расходится с MODULE-ID внутри verification.md.",
                path=passport_ref,
            )
        )
        readiness_payload = _blocked_readiness(
            reason="MODULE-ID в `module.md` и `verification.md` расходятся; execution context ненадёжен.",
            expected_verification_ref=verification_ref,
            governed_files=tuple(item.path_ref for item in passport.owned_surface),
            residual_manual_risk=("module_identity_mismatch",),
        )
    if passport is not None and passport.execution_readiness_status != readiness_payload.status:
        warnings.append(
            _module_warning(
                "module_passport_readiness_stale",
                "Кэш readiness в module passport расходится с readiness, вычисленным из verification.md.",
                path=passport_ref,
            )
        )
    if passport is not None and passport.file_local_policy_ref is not None:
        policy_path = (project_root / passport.file_local_policy_ref).resolve()
        if not _is_within_project(policy_path, project_root) or not policy_path.exists() or not policy_path.is_file():
            warnings.append(
                _module_warning(
                    "file_local_policy_missing",
                    "Канонический `file-local-policy.md` указан в module passport, но файл не найден.",
                    path=passport.file_local_policy_ref,
                )
            )
        else:
            try:
                file_local_policy = load_file_local_policy(project_root, policy_path)
            except FileLocalPolicyError as error:
                warnings.append(
                    _module_warning(
                        "file_local_policy_invalid",
                        str(error),
                        path=passport.file_local_policy_ref,
                    )
                )

    source_state = _source_state(passport=passport, verification_ref=verification_ref)
    if passport is not None:
        governed_files = list(
            dict.fromkeys(
                [
                    *(item.path_ref for item in passport.owned_surface),
                    *(_normalize_project_file_ref(project_root, path) or path for path in readiness_payload.required_governed_files),
                    *evidence_file_refs,
                ]
            )
        )
        public_truth = {
            "passport_ref": passport_ref,
            "verification_ref": verification_ref,
            "file_local_policy_ref": passport.file_local_policy_ref,
            "purpose_summary": passport.purpose_summary,
            "scope_summary": passport.scope_text,
            "owned_surface": [asdict(item) for item in passport.owned_surface],
            "public_contracts": [asdict(item) for item in passport.public_contracts],
            "governed_files": governed_files,
            "evidence_file_refs": evidence_file_refs,
            "origin_task_ref": passport.origin_task_ref,
            "last_updated_task_ref": passport.last_updated_task_ref,
            "execution_readiness_summary": passport.execution_readiness_summary,
        }
    else:
        governed_files = list(
            dict.fromkeys(
                [
                    *(_normalize_project_file_ref(project_root, path) or path for path in readiness_payload.required_governed_files),
                    *evidence_file_refs,
                ]
            )
        )
        public_truth = {
            "passport_ref": passport_ref,
            "verification_ref": verification_ref,
            "file_local_policy_ref": None,
            "purpose_summary": None,
            "scope_summary": None,
            "owned_surface": [],
            "public_contracts": [],
            "governed_files": governed_files,
            "evidence_file_refs": evidence_file_refs,
            "origin_task_ref": None,
            "last_updated_task_ref": None,
            "execution_readiness_summary": None,
        }

    warnings.extend(
        _compare_registry_row(
            registry_rows.get(module_id),
            expected=_registry_expected_row(
                project_root,
                directory_path,
                passport=passport,
                passport_ref=passport_ref,
                verification_ref=verification_ref,
                source_state=source_state,
                readiness_status=readiness_payload.status,
                purpose_summary=passport.purpose_summary if passport is not None else None,
            ),
            path=passport_ref or verification_ref,
        )
    )

    if passport is None or public_truth["file_local_policy_ref"] is None:
        warnings.append(
            _module_warning(
                "file_contract_unavailable",
                "File-local contracts ещё не реализованы; будут возвращены только verification-derived anchors.",
                path=passport_ref or verification_ref,
            )
        )
    if passport is None:
        warnings.append(
            _module_warning(
                "partial_governed_scope",
                "Read-model работает в partial rollout: passports, relations и file-local contracts могут отсутствовать.",
                path=verification_ref,
            )
        )

    summary = ModuleSummary(
        module_id=module_id,
        slug=slug,
        source_state=source_state,
        readiness_status=readiness_payload.status,
        passport_ref=passport_ref,
        verification_ref=verification_ref,
        governed_files=governed_files,
        purpose_summary=(passport.purpose_summary if passport is not None else None),
        warnings=warnings,
    )
    return ModuleRecord(
        summary=summary,
        verification_record=verification_record,
        verification_excerpt=verification_excerpt,
        public_truth=public_truth,
        readiness={
            "status": readiness_payload.status,
            "blocking_reasons": list(readiness_payload.blocking_reasons),
            "required_verification_refs": list(readiness_payload.required_verification_refs),
            "required_governed_files": list(readiness_payload.required_governed_files),
            "residual_manual_risk": list(readiness_payload.residual_manual_risk),
        },
        relations={
            "status": "unavailable",
            "items": [],
            "reason": _relation_reason(unavailable=True),
        },
        files={
            "verification_file": verification_ref,
            "passport_file": passport_ref,
            "governed_files": governed_files,
            "evidence_file_refs": evidence_file_refs,
        },
        verification_anchors=anchors_by_path,
        failure_handoff_refs=handoff_refs_by_path,
        declared_relations=(passport.relation_envelope if passport is not None else ()),
        has_valid_passport=(passport is not None),
        file_local_policy=file_local_policy,
    )


def build_module_index(project_root: Path) -> ModuleIndex:
    modules_root = project_root / MODULES_ROOT
    if not modules_root.exists():
        return ModuleIndex(records=[], duplicate_module_ids={}, warnings=[])

    registry_rows, registry_warnings = _parse_registry(project_root)
    records: list[ModuleRecord] = []
    by_module_id: dict[str, list[ModuleRecord]] = {}
    seen_ids: set[str] = set()
    module_dirs = [
        item
        for item in sorted(modules_root.iterdir(), key=lambda path: path.name)
        if item.is_dir()
        and not item.name.startswith("_")
        and ((item / PASSPORT_FILENAME).exists() or (item / VERIFICATION_FILENAME).exists())
    ]
    for module_dir in module_dirs:
        record = _record_from_directory(project_root, module_dir.resolve(), registry_rows)
        records.append(record)
        by_module_id.setdefault(record.summary.module_id.casefold(), []).append(record)
        seen_ids.add(record.summary.module_id)

    for module_id, row in registry_rows.items():
        if module_id not in seen_ids:
            registry_warnings.append(
                _module_warning(
                    "module_registry_orphan_row",
                    f"Строка `{module_id}` присутствует в module registry, но канонический каталог модуля не найден.",
                    path=row.path,
                )
            )

    duplicate_module_ids = {module_id: items for module_id, items in by_module_id.items() if len(items) > 1}
    module_index = ModuleIndex(records=records, duplicate_module_ids=duplicate_module_ids, warnings=registry_warnings)
    _build_relation_payloads(module_index)
    return module_index


def _searchable_fields(record: ModuleRecord) -> dict[str, list[str]]:
    public_truth = record.public_truth
    return {
        "module_id": [record.summary.module_id],
        "slug": [record.summary.slug],
        "purpose_summary": [record.summary.purpose_summary or ""],
        "verification_ref": [record.summary.verification_ref or ""],
        "passport_ref": [record.summary.passport_ref or ""],
        "governed_files": record.summary.governed_files,
        "public_contracts": [item["reference"] for item in public_truth.get("public_contracts", [])],
    }


def _match_fields(record: ModuleRecord, query: str) -> tuple[int, list[str]] | None:
    normalized = query.casefold()
    matched_fields: list[str] = []
    best_rank: int | None = None
    field_values = _searchable_fields(record)
    for field_name, values in field_values.items():
        for value in values:
            text = value.casefold()
            if not text:
                continue
            rank: int | None = None
            if field_name == "module_id" and text == normalized:
                rank = 0
            elif field_name in {"module_id", "slug"} and text.startswith(normalized):
                rank = 1
            elif field_name in {"module_id", "slug", "purpose_summary"} and normalized in text:
                rank = 2
            elif field_name in {"governed_files", "verification_ref", "passport_ref", "public_contracts"} and text.startswith(normalized):
                rank = 3
            elif normalized in text:
                rank = 4
            if rank is None:
                continue
            if field_name not in matched_fields:
                matched_fields.append(field_name)
            if best_rank is None or rank < best_rank:
                best_rank = rank
    if best_rank is None:
        return None
    return best_rank, matched_fields


def find_modules(
    project_root: Path,
    *,
    query: str,
    readiness: str | None = None,
    source_state: str | None = None,
    limit: int | None = None,
) -> tuple[list[dict[str, object]], list[WarningItem]]:
    module_index = build_module_index(project_root)
    warnings: list[WarningItem] = [*module_index.warnings]
    items: list[tuple[int, ModuleRecord, list[str]]] = []
    for record in module_index.records:
        if readiness and record.summary.readiness_status != readiness:
            continue
        if source_state and record.summary.source_state != source_state:
            continue
        matched = _match_fields(record, query)
        if matched is None:
            continue
        rank, matched_fields = matched
        items.append((rank, record, matched_fields))
    items.sort(key=lambda item: (item[0], item[1].summary.module_id.casefold()))
    limited = items[: max(limit or 20, 0)]
    payload_items = [
        {
            **module_summary_to_dict(record.summary),
            "matched_fields": matched_fields,
        }
        for _, record, matched_fields in limited
    ]
    for duplicate_records in module_index.duplicate_module_ids.values():
        warnings.append(
            WarningItem(
                code="duplicate_module_id",
                severity="warning",
                detail=(
                    f"Обнаружено несколько module records с MODULE-ID `{duplicate_records[0].summary.module_id}`; "
                    "точный lookup по нему неоднозначен."
                ),
                path=None,
            )
        )
    if not payload_items:
        warnings.append(
            WarningItem(
                code="module_query_empty",
                severity="warning",
                detail="Совпадения не найдены в текущем governed scope Module Core.",
                path=None,
            )
        )
    return payload_items, warnings


def _resolve_module_record(
    project_root: Path,
    selector: str,
) -> tuple[ModuleRecord | None, list[WarningItem], str | None]:
    module_index = build_module_index(project_root)
    exact_matches = [
        record for record in module_index.records if record.summary.module_id.casefold() == selector.casefold()
    ]
    if len(exact_matches) == 1:
        return exact_matches[0], [*module_index.warnings], None
    if len(exact_matches) > 1:
        return (
            None,
            [
                *module_index.warnings,
                WarningItem(
                    code="duplicate_module_id",
                    severity="error",
                    detail="Точный MODULE-ID совпал с несколькими module records; сначала устраните дубликаты.",
                    path=None,
                ),
            ],
            "duplicate_module_id",
        )
    slug_matches = [record for record in module_index.records if record.summary.slug.casefold() == selector.casefold()]
    if len(slug_matches) == 1:
        return slug_matches[0], [*module_index.warnings], None
    if len(slug_matches) > 1:
        return (
            None,
            [
                *module_index.warnings,
                WarningItem(
                    code="module_selector_ambiguous",
                    severity="error",
                    detail="Selector совпал с несколькими module slug; используйте точный MODULE-ID.",
                    path=None,
                ),
            ],
            "module_selector_ambiguous",
        )
    return (
        None,
        [
            *module_index.warnings,
            WarningItem(
                code="module_not_found",
                severity="error",
                detail="Модуль не найден; поддерживаются только точный MODULE-ID или уникальный slug.",
                path=None,
            )
        ],
        "module_not_found",
    )


def module_show(
    project_root: Path,
    *,
    selector: str,
) -> tuple[dict[str, object] | None, list[WarningItem], str | None]:
    record, warnings, error_code = _resolve_module_record(project_root, selector)
    if record is None:
        return None, warnings, error_code
    module_payload = module_record_to_dict(record)
    return module_payload, [*record.summary.warnings, *warnings], None


def _resolve_file_path(project_root: Path, raw_path: str) -> tuple[Path | None, list[WarningItem], str | None]:
    candidate = Path(raw_path)
    resolved = (candidate if candidate.is_absolute() else project_root / candidate).resolve()
    if not _is_within_project(resolved, project_root):
        return (
            None,
            [
                WarningItem(
                    code="path_outside_project",
                    severity="error",
                    detail="Путь должен оставаться внутри `project_root`.",
                    path=str(resolved),
                )
            ],
            "path_outside_project",
        )
    if not resolved.exists() or not resolved.is_file():
        return (
            None,
            [
                WarningItem(
                    code="file_not_found",
                    severity="error",
                    detail="Файл не найден в пределах `project_root`.",
                    path=str(resolved),
                )
            ],
            "file_not_found",
        )
    return resolved, [], None


def _extend_unique_warnings(target: list[WarningItem], items: list[WarningItem]) -> None:
    seen = {(item.code, item.severity, item.detail, item.path) for item in target}
    for item in items:
        signature = (item.code, item.severity, item.detail, item.path)
        if signature in seen:
            continue
        target.append(item)
        seen.add(signature)


def file_show(
    project_root: Path,
    *,
    raw_path: str,
    module_selector: str | None = None,
) -> tuple[dict[str, object] | None, list[WarningItem], str | None]:
    resolved_path, warnings, error_code = _resolve_file_path(project_root, raw_path)
    if resolved_path is None:
        return None, warnings, error_code
    relative_ref = _relative_path(project_root, resolved_path)
    module_index = build_module_index(project_root)
    records = module_index.records
    _extend_unique_warnings(warnings, module_index.warnings)

    def _owns_file(record: ModuleRecord) -> bool:
        return relative_ref in record.summary.governed_files

    matching_owner_records = [record for record in records if _owns_file(record)]
    owner_records = list(matching_owner_records)
    if module_selector:
        selected_record, selector_warnings, selector_error = _resolve_module_record(project_root, module_selector)
        if selected_record is None:
            return None, selector_warnings, selector_error
        _extend_unique_warnings(warnings, selector_warnings)
        owner_records = [record for record in owner_records if record.summary.module_id == selected_record.summary.module_id]
        if not owner_records and matching_owner_records:
            return (
                None,
                [
                    WarningItem(
                        code="file_module_mismatch",
                        severity="error",
                        detail="Файл governed, но не принадлежит выбранному модулю.",
                        path=relative_ref,
                    )
                ],
                "file_module_mismatch",
        )
    owner_payloads = [
        file_owner_to_dict(
            FileOwner(
                module_id=record.summary.module_id,
                slug=record.summary.slug,
                source_state=record.summary.source_state,
                readiness_status=record.summary.readiness_status,
                passport_ref=record.summary.passport_ref,
                verification_ref=record.summary.verification_ref,
            )
        )
        for record in owner_records
    ]
    _extend_unique_warnings(
        warnings,
        [warning for record in owner_records for warning in record.summary.warnings],
    )
    if len(owner_records) > 1 and not module_selector:
        warnings.append(
            WarningItem(
                code="multi_owner_file",
                severity="warning",
                detail="Файл связан с несколькими governed modules; используйте `--module` для точной фильтрации.",
                path=relative_ref,
            )
        )
    if not owner_records:
        warnings.append(
            WarningItem(
                code="ungoverned_file",
                severity="warning",
                detail="Файл не входит в текущий governed scope Module Core.",
                path=relative_ref,
            )
        )
    verification_anchors: list[dict[str, str]] = []
    failure_handoff_refs: list[str] = []
    governance_state = "ungoverned"
    for record in owner_records:
        if record.summary.source_state == "passport_ready":
            governance_state = "passport_governed"
        elif governance_state == "ungoverned":
            governance_state = "verification_evidence_only"
        for anchor in record.verification_anchors.get(relative_ref, []):
            if anchor not in verification_anchors:
                verification_anchors.append(anchor)
        refs = record.failure_handoff_refs.get(relative_ref)
        if refs:
            for ref in refs:
                if ref not in failure_handoff_refs:
                    failure_handoff_refs.append(ref)
            continue
        if record.summary.governed_files and relative_ref in record.summary.governed_files and record.summary.verification_ref:
            excerpt = record.verification_excerpt or {}
            required_scenarios = excerpt.get("required_scenarios", [])
            for scenario in required_scenarios:
                contract_ref = f"{record.summary.verification_ref}#{scenario['ref']}"
                if contract_ref not in failure_handoff_refs:
                    failure_handoff_refs.append(contract_ref)
    contract_markers: list[dict[str, object]] = []
    blocks: list[dict[str, object]] = []

    contract_owner: ModuleRecord | None = None
    if module_selector and owner_records:
        contract_owner = owner_records[0]
    elif len(owner_records) == 1:
        contract_owner = owner_records[0]
    elif len(owner_records) > 1:
        warnings.append(
            WarningItem(
                code="multi_owner_file_contract_ambiguous",
                severity="warning",
                detail=(
                    "File-local policy для multi-owner файла неоднозначна; "
                    "передайте `--module`, чтобы выбрать конкретного владельца."
                ),
                path=relative_ref,
            )
        )

    if contract_owner is not None:
        file_local_policy_ref = contract_owner.public_truth.get("file_local_policy_ref")
        if file_local_policy_ref is None:
            warnings.append(
                WarningItem(
                    code="file_contract_unavailable",
                    severity="warning",
                    detail="Для выбранного владельца file-local policy ещё не подключена.",
                    path=relative_ref,
                )
            )
        elif contract_owner.file_local_policy is not None:
            hot_spot = contract_owner.file_local_policy.hot_spots_by_path.get(relative_ref)
            if hot_spot is None:
                warnings.append(
                    WarningItem(
                        code="file_not_governed_hotspot",
                        severity="warning",
                        detail="Файл принадлежит модулю, но не входит в явный hot-spot scope его file-local policy.",
                        path=relative_ref,
                    )
                )
            else:
                parsed_contracts = parse_file_local_contracts(resolved_path, hot_spot)
                contract_markers = [asdict(item) for item in parsed_contracts.contract_markers]
                blocks = [asdict(item) for item in parsed_contracts.blocks]
                warnings.extend(
                    WarningItem(
                        code=item.code,
                        severity="warning",
                        detail=item.detail,
                        path=relative_ref,
                    )
                    for item in parsed_contracts.warnings
                )
    payload = {
        "resolved_path": relative_ref,
        "governance_state": governance_state,
        "owner_modules": owner_payloads,
        "contract_markers": contract_markers,
        "blocks": blocks,
        "verification_anchors": verification_anchors,
        "failure_handoff_refs": failure_handoff_refs,
    }
    return payload, warnings, None
