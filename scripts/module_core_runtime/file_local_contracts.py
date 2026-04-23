"""Parser/runtime for governed file-local contracts and hot-spot policy."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re

from task_workflow_runtime.models import DELIVERY_ROW_PLACEHOLDER, normalize_table_value
from task_workflow_runtime.task_markdown import find_section_bounds, split_markdown_row


PLACEHOLDER = "—"
FILE_LOCAL_POLICY_FILENAME = "file-local-policy.md"
HOT_SPOTS_SECTION = "## Hot spots"
HOT_SPOTS_HEADERS = ("Путь", "Режим", "Разрешённые markers", "Обязательные blocks", "Назначение")
ALLOWED_MARKERS = ("MODULE_CONTRACT", "MODULE_MAP", "CHANGE_SUMMARY")
ALLOWED_MODES = {"required", "advisory"}
COMMENT_PREFIX_RE = re.compile(r"^\s*(//|#|--|;|\*)\s*(?P<body>.*?)\s*$")
TOKEN_RE = re.compile(
    r"^(?:(?P<token1>MODULE_CONTRACT|MODULE_MAP|CHANGE_SUMMARY|BLOCK_[A-Z0-9_]+)"
    r"\s*[:=-]?\s*(?P<direction1>BEGIN|END)|"
    r"(?P<direction2>BEGIN|END)\s+(?P<token2>MODULE_CONTRACT|MODULE_MAP|CHANGE_SUMMARY|BLOCK_[A-Z0-9_]+))$"
)
BLOCK_ID_RE = re.compile(r"BLOCK_[A-Z0-9_]+$")


@dataclass(frozen=True)
class FileHotSpotPolicy:
    path_ref: str
    mode: str
    allowed_markers: tuple[str, ...]
    required_blocks: tuple[str, ...]
    purpose: str


@dataclass(frozen=True)
class FileLocalPolicy:
    policy_ref: str
    hot_spots: tuple[FileHotSpotPolicy, ...]

    @property
    def hot_spots_by_path(self) -> dict[str, FileHotSpotPolicy]:
        return {item.path_ref: item for item in self.hot_spots}


@dataclass(frozen=True)
class FileLocalContractWarning:
    code: str
    detail: str


@dataclass(frozen=True)
class ContractMarkerStatus:
    marker: str
    required: bool
    present: bool
    start_line: int | None
    end_line: int | None


@dataclass(frozen=True)
class ContractBlockStatus:
    block_id: str
    required: bool
    present: bool
    start_line: int | None
    end_line: int | None


@dataclass(frozen=True)
class ParsedFileLocalContracts:
    contract_markers: tuple[ContractMarkerStatus, ...]
    blocks: tuple[ContractBlockStatus, ...]
    warnings: tuple[FileLocalContractWarning, ...]


class FileLocalPolicyError(ValueError):
    """Raised when file-local policy markdown is invalid."""


def _relative_path(project_root: Path, path: Path) -> str:
    return path.relative_to(project_root).as_posix()


def _looks_like_file_path(value: str) -> bool:
    normalized = value.strip().replace("\\", "/")
    if not normalized or normalized.endswith("/"):
        return False
    parts = [part for part in normalized.split("/") if part]
    return bool(parts) and all(part not in {".", ".."} for part in parts)


def _normalize_project_file_ref(project_root: Path, value: str) -> str | None:
    normalized = normalize_table_value(value).replace("\\", "/")
    if not normalized or normalized == PLACEHOLDER or not _looks_like_file_path(normalized):
        return None
    if re.fullmatch(r"[A-Za-z]:/.*", normalized):
        return None
    resolved_root = project_root.resolve()
    candidate = Path(normalized)
    if candidate.is_absolute():
        return None
    resolved = (resolved_root / candidate).resolve()
    try:
        return resolved.relative_to(resolved_root).as_posix()
    except ValueError:
        return None


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def _parse_table_rows(lines: list[str], title: str, expected_headers: tuple[str, ...]) -> list[tuple[str, ...]]:
    bounds = find_section_bounds(lines, title)
    if bounds is None:
        raise FileLocalPolicyError(f"В файле не найден раздел {title!r}.")
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
            raise FileLocalPolicyError(
                f"Раздел {title!r} должен начинаться с канонической строки заголовков таблицы."
            )
        if all(re.fullmatch(r"-+", cell) for cell in normalized):
            continue
        if len(normalized) != len(expected_headers):
            raise FileLocalPolicyError(
                f"Раздел {title!r} содержит строку с {len(normalized)} колонками вместо {len(expected_headers)}."
            )
        if normalized[0] == DELIVERY_ROW_PLACEHOLDER:
            continue
        rows.append(normalized)
    return rows


def _split_csv(value: str) -> tuple[str, ...]:
    normalized = normalize_table_value(value)
    if not normalized or normalized == PLACEHOLDER:
        return ()
    items = [normalize_table_value(part) for part in normalized.split(",")]
    result: list[str] = []
    for item in items:
        if not item or item == PLACEHOLDER:
            continue
        if item not in result:
            result.append(item)
    return tuple(result)


def load_file_local_policy(project_root: Path, policy_path: Path) -> FileLocalPolicy:
    lines = _read_lines(policy_path)
    rows = _parse_table_rows(lines, HOT_SPOTS_SECTION, HOT_SPOTS_HEADERS)
    if not rows:
        raise FileLocalPolicyError("Раздел `## Hot spots` должен содержать хотя бы одну строку.")

    hot_spots: list[FileHotSpotPolicy] = []
    seen_paths: set[str] = set()
    for path_ref, mode, allowed_markers_raw, required_blocks_raw, purpose in rows:
        normalized_path = _normalize_project_file_ref(project_root, path_ref)
        if normalized_path is None:
            raise FileLocalPolicyError(
                "Каждая строка `## Hot spots` должна использовать project-relative путь в колонке `Путь`."
            )
        if normalized_path in seen_paths:
            raise FileLocalPolicyError(f"Путь `{normalized_path}` указан в `## Hot spots` более одного раза.")
        seen_paths.add(normalized_path)

        if mode not in ALLOWED_MODES:
            raise FileLocalPolicyError("Колонка `Режим` должна иметь значение `required` или `advisory`.")

        allowed_markers = _split_csv(allowed_markers_raw)
        unknown_markers = [item for item in allowed_markers if item not in ALLOWED_MARKERS]
        if unknown_markers:
            raise FileLocalPolicyError(
                "Колонка `Разрешённые markers` может содержать только `MODULE_CONTRACT`, `MODULE_MAP`, `CHANGE_SUMMARY`."
            )

        required_blocks = _split_csv(required_blocks_raw)
        invalid_blocks = [item for item in required_blocks if not BLOCK_ID_RE.fullmatch(item)]
        if invalid_blocks:
            raise FileLocalPolicyError(
                "Колонка `Обязательные blocks` может содержать только значения формата `BLOCK_<NAME>` или `—`."
            )

        hot_spots.append(
            FileHotSpotPolicy(
                path_ref=normalized_path,
                mode=mode,
                allowed_markers=allowed_markers,
                required_blocks=required_blocks,
                purpose=purpose,
            )
        )

    return FileLocalPolicy(
        policy_ref=_relative_path(project_root, policy_path),
        hot_spots=tuple(hot_spots),
    )


@dataclass
class _TokenCapture:
    start_line: int | None = None
    end_line: int | None = None
    present: bool = False


def _scan_comment_tokens(lines: list[str]) -> tuple[dict[str, _TokenCapture], list[FileLocalContractWarning]]:
    captures: dict[str, _TokenCapture] = {}
    open_tokens: dict[str, int] = {}
    warnings: list[FileLocalContractWarning] = []

    for line_number, line in enumerate(lines, start=1):
        match = COMMENT_PREFIX_RE.match(line)
        if match is None:
            continue
        token_match = TOKEN_RE.match(match.group("body").strip())
        if token_match is None:
            continue
        token = token_match.group("token1") or token_match.group("token2")
        direction = token_match.group("direction1") or token_match.group("direction2")
        assert token is not None
        assert direction is not None

        capture = captures.setdefault(token, _TokenCapture())
        if direction == "BEGIN":
            if token in open_tokens:
                warnings.append(
                    FileLocalContractWarning(
                        code="file_contract_duplicate_begin",
                        detail=f"Marker `{token}` открыт повторно на строке {line_number} до закрытия предыдущей пары.",
                    )
                )
                continue
            open_tokens[token] = line_number
            if capture.start_line is None:
                capture.start_line = line_number
            continue

        start_line = open_tokens.pop(token, None)
        if start_line is None:
            warnings.append(
                FileLocalContractWarning(
                    code="file_contract_end_without_begin",
                    detail=f"Marker `{token}` закрыт на строке {line_number} без соответствующего BEGIN.",
                )
            )
            continue
        if capture.present:
            warnings.append(
                FileLocalContractWarning(
                    code="file_contract_duplicate_pair",
                    detail=f"Marker `{token}` размечен более одной полной парой; учитывается первая.",
                )
            )
            continue
        capture.start_line = start_line
        capture.end_line = line_number
        capture.present = True

    for token, start_line in sorted(open_tokens.items(), key=lambda item: item[1]):
        capture = captures.setdefault(token, _TokenCapture())
        if capture.start_line is None:
            capture.start_line = start_line
        warnings.append(
            FileLocalContractWarning(
                code="file_contract_missing_end",
                detail=f"Marker `{token}` открыт на строке {start_line}, но не закрыт.",
            )
        )

    return captures, warnings


def _serialize_contract_marker(item: ContractMarkerStatus) -> dict[str, object]:
    return asdict(item)


def _serialize_contract_block(item: ContractBlockStatus) -> dict[str, object]:
    return asdict(item)


def parse_file_local_contracts(file_path: Path, hot_spot: FileHotSpotPolicy) -> ParsedFileLocalContracts:
    lines = _read_lines(file_path)
    captures, warnings = _scan_comment_tokens(lines)

    contract_markers: list[ContractMarkerStatus] = []
    required_markers = set(hot_spot.allowed_markers) if hot_spot.mode == "required" else set()
    discovered_contract_markers = [
        marker
        for marker in ALLOWED_MARKERS
        if marker in hot_spot.allowed_markers or marker in captures
    ]
    for marker in discovered_contract_markers:
        capture = captures.get(marker, _TokenCapture())
        required = marker in required_markers
        present = capture.present
        contract_markers.append(
            ContractMarkerStatus(
                marker=marker,
                required=required,
                present=present,
                start_line=capture.start_line,
                end_line=capture.end_line,
            )
        )
        if marker in captures and marker not in hot_spot.allowed_markers:
            warnings.append(
                FileLocalContractWarning(
                    code="file_contract_marker_not_allowed",
                    detail=f"Marker `{marker}` присутствует в файле, но не разрешён policy hot spot.",
                )
            )
        if required and not present:
            warnings.append(
                FileLocalContractWarning(
                    code="file_contract_required_marker_missing",
                    detail=f"Обязательный marker `{marker}` отсутствует или не закрыт полной парой.",
                )
            )

    discovered_blocks = [
        token
        for token in captures
        if BLOCK_ID_RE.fullmatch(token)
    ]
    block_order = [*hot_spot.required_blocks]
    for block_id in discovered_blocks:
        if block_id not in block_order:
            block_order.append(block_id)

    blocks: list[ContractBlockStatus] = []
    required_blocks = set(hot_spot.required_blocks)
    for block_id in block_order:
        capture = captures.get(block_id, _TokenCapture())
        present = capture.present
        required = block_id in required_blocks
        blocks.append(
            ContractBlockStatus(
                block_id=block_id,
                required=required,
                present=present,
                start_line=capture.start_line,
                end_line=capture.end_line,
            )
        )
        if required and not present:
            warnings.append(
                FileLocalContractWarning(
                    code="file_contract_required_block_missing",
                    detail=f"Обязательный block `{block_id}` отсутствует или не закрыт полной парой.",
                )
            )

    return ParsedFileLocalContracts(
        contract_markers=tuple(contract_markers),
        blocks=tuple(blocks),
        warnings=tuple(warnings),
    )


__all__ = [
    "ALLOWED_MARKERS",
    "FILE_LOCAL_POLICY_FILENAME",
    "FileHotSpotPolicy",
    "FileLocalContractWarning",
    "FileLocalPolicy",
    "FileLocalPolicyError",
    "ParsedFileLocalContracts",
    "load_file_local_policy",
    "parse_file_local_contracts",
    "_serialize_contract_block",
    "_serialize_contract_marker",
]
