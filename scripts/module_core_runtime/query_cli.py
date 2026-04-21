"""Transport and text formatter for Module Core query commands."""

from __future__ import annotations

from .read_model import (
    file_show,
    find_modules,
    module_show,
    warning_to_dict,
)


def _append_section(lines: list[str], title: str, rows: list[str]) -> None:
    if not rows:
        return
    if lines:
        lines.append("")
    lines.append(title)
    lines.extend(rows)


def _format_warnings(warnings: list[dict[str, object]]) -> list[str]:
    rows: list[str] = []
    for item in warnings:
        path = f" path={item['path']}" if item.get("path") else ""
        rows.append(f"- [{item['severity']}] {item['code']}: {item['detail']}{path}")
    return rows


def format_module_find_payload(payload: dict[str, object]) -> str:
    lines: list[str] = [
        "module find",
        f"query={payload['query']}",
        f"count={payload['count']}",
    ]
    items = payload["items"]
    assert isinstance(items, list)
    if items:
        rows: list[str] = []
        for item in items:
            assert isinstance(item, dict)
            rows.append(
                (
                    f"- {item['module_id']} | slug={item['slug']} | source={item['source_state']} | "
                    f"readiness={item['readiness_status']} | matched={','.join(item['matched_fields'])}"
                )
            )
            rows.append(f"  purpose_summary={item['purpose_summary'] or '—'}")
            rows.append(f"  verification_ref={item['verification_ref'] or '—'}")
            rows.append(f"  passport_ref={item['passport_ref'] or '—'}")
            rows.append(
                "  governed_files="
                + (", ".join(item["governed_files"]) if item["governed_files"] else "—")
            )
        _append_section(lines, "Results", rows)
    _append_section(lines, "Warnings", _format_warnings(payload["warnings"]))
    return "\n".join(lines) + "\n"


def format_module_show_payload(
    payload: dict[str, object],
    *,
    with_sections: set[str] | None = None,
) -> str:
    with_sections = with_sections or set()
    lines: list[str] = ["module show", f"selector={payload['selector']}"]
    module = payload["module"]
    if module is None:
        _append_section(lines, "Result", ["Модуль не найден."])
        _append_section(lines, "Warnings", _format_warnings(payload["warnings"]))
        return "\n".join(lines) + "\n"
    assert isinstance(module, dict)
    _append_section(
        lines,
        "Module",
        [
            f"{module['module_id']} · {module['slug']}",
            f"source_state={module['source_state']}",
            f"verification_ref={module['verification_ref'] or '—'}",
            f"passport_ref={module['passport_ref'] or '—'}",
            f"purpose_summary={module['purpose_summary'] or '—'}",
        ],
    )
    public_truth = module["public_truth"]
    assert isinstance(public_truth, dict)
    _append_section(
        lines,
        "Public truth",
        [
            "governed_files="
            + (", ".join(module["governed_files"]) if module["governed_files"] else "—"),
            f"file_local_policy_ref={public_truth['file_local_policy_ref'] or '—'}",
        ],
    )
    readiness = module["readiness"]
    assert isinstance(readiness, dict)
    _append_section(
        lines,
        "Readiness",
        [
            f"status={readiness['status']}",
            "blocking_reasons="
            + (", ".join(readiness["blocking_reasons"]) if readiness["blocking_reasons"] else "—"),
        ],
    )
    if with_sections & {"verification", "all"}:
        excerpt = module["verification_excerpt"]
        rows = ["verification_excerpt=—"]
        if isinstance(excerpt, dict):
            rows = [
                f"readiness_status={excerpt['readiness_status']}",
                "writer_checks="
                + (", ".join(item["ref"] for item in excerpt["writer_checks"]) or "—"),
                "required_scenarios="
                + (", ".join(item["ref"] for item in excerpt["required_scenarios"]) or "—"),
                "task_followups="
                + (", ".join(item["ref"] for item in excerpt["task_followups"]) or "—"),
            ]
        _append_section(lines, "Verification", rows)
    if with_sections & {"files", "all"}:
        files = module["files"]
        assert isinstance(files, dict)
        _append_section(
            lines,
            "Files",
            [
                f"verification_file={files['verification_file'] or '—'}",
                f"passport_file={files['passport_file'] or '—'}",
                "evidence_file_refs="
                + (", ".join(files["evidence_file_refs"]) if files["evidence_file_refs"] else "—"),
            ],
        )
    if with_sections & {"relations", "all"}:
        relations = module["relations"]
        assert isinstance(relations, dict)
        summary = relations.get("summary", {})
        assert isinstance(summary, dict)
        relation_rows = [f"status={relations['status']}"]
        reason = relations.get("reason")
        if reason:
            relation_rows.append(f"reason={reason}")
        relation_rows.extend(
            [
                f"depends_on_total={summary.get('depends_on_total', 0)}",
                f"depends_on_required={summary.get('depends_on_required', 0)}",
                f"depends_on_informational={summary.get('depends_on_informational', 0)}",
                f"depends_on_planned={summary.get('depends_on_planned', 0)}",
                f"used_by_total={summary.get('used_by_total', 0)}",
            ]
        )
        outgoing = relations.get("outgoing", [])
        assert isinstance(outgoing, list)
        if outgoing:
            relation_rows.append("depends_on:")
            for item in outgoing:
                assert isinstance(item, dict)
                relation_rows.append(
                    (
                        f"- {item['target_module_id']} | type={item['relation_type']} | "
                        f"status={item['relation_status']} | slug={item['target_slug'] or '—'} | "
                        f"source={item['target_source_state'] or '—'} | readiness={item['target_readiness_status'] or '—'}"
                    )
                )
                relation_rows.append(f"  passport_ref={item['target_passport_ref'] or '—'}")
                relation_rows.append(f"  verification_ref={item['target_verification_ref'] or '—'}")
                relation_rows.append(f"  notes={item['notes'] or '—'}")
        else:
            relation_rows.append("depends_on=—")
        used_by = relations.get("used_by", [])
        assert isinstance(used_by, list)
        if used_by:
            relation_rows.append("used_by:")
            for item in used_by:
                assert isinstance(item, dict)
                relation_rows.append(
                    (
                        f"- {item['source_module_id']} | type={item['relation_type']} | "
                        f"status={item['relation_status']} | slug={item['source_slug'] or '—'} | "
                        f"source={item['source_source_state'] or '—'} | readiness={item['source_readiness_status'] or '—'}"
                    )
                )
                relation_rows.append(f"  passport_ref={item['source_passport_ref'] or '—'}")
                relation_rows.append(f"  verification_ref={item['source_verification_ref'] or '—'}")
                relation_rows.append(f"  notes={item['notes'] or '—'}")
        else:
            relation_rows.append("used_by=—")
        _append_section(lines, "Relations", relation_rows)
    _append_section(lines, "Warnings", _format_warnings(payload["warnings"]))
    return "\n".join(lines) + "\n"


def format_file_show_payload(
    payload: dict[str, object],
    *,
    show_contracts: bool = False,
    show_blocks: bool = False,
) -> str:
    lines: list[str] = ["file show", f"path={payload['path']}"]
    file_payload = payload["file"]
    if file_payload is None:
        _append_section(lines, "Result", ["Файл не найден."])
        _append_section(lines, "Warnings", _format_warnings(payload["warnings"]))
        return "\n".join(lines) + "\n"
    assert isinstance(file_payload, dict)
    _append_section(
        lines,
        "File",
        [
            f"resolved_path={file_payload['resolved_path']}",
            f"governance_state={file_payload['governance_state']}",
            (
                "contract_markers="
                f"{sum(1 for item in file_payload['contract_markers'] if item['present'])}"
                f"/{len(file_payload['contract_markers'])}"
            ),
            f"blocks={sum(1 for item in file_payload['blocks'] if item['present'])}/{len(file_payload['blocks'])}",
        ],
    )
    owners = file_payload["owner_modules"]
    assert isinstance(owners, list)
    if owners:
        _append_section(
            lines,
            "Owner modules",
            [
                (
                    f"- {item['module_id']} | slug={item['slug']} | source={item['source_state']} | "
                    f"readiness={item['readiness_status']}"
                )
                for item in owners
            ],
        )
    anchors = file_payload["verification_anchors"]
    assert isinstance(anchors, list)
    _append_section(
        lines,
        "Verification anchors",
        [
            f"- {item['module_id']} | {item['evidence_ref']} | anchor={item['anchor']} | kind={item['kind']}"
            for item in anchors
        ],
    )
    if show_contracts:
        contract_markers = file_payload["contract_markers"]
        assert isinstance(contract_markers, list)
        _append_section(
            lines,
            "Contract markers",
            [
                (
                    f"- {item['marker']} | required={item['required']} | present={item['present']} | "
                    f"start_line={item['start_line'] or '—'} | end_line={item['end_line'] or '—'}"
                )
                for item in contract_markers
            ]
            or ["—"],
        )
    if show_blocks:
        blocks = file_payload["blocks"]
        assert isinstance(blocks, list)
        _append_section(
            lines,
            "Blocks",
            [
                (
                    f"- {item['block_id']} | required={item['required']} | present={item['present']} | "
                    f"start_line={item['start_line'] or '—'} | end_line={item['end_line'] or '—'}"
                )
                for item in blocks
            ]
            or ["—"],
        )
    refs = file_payload["failure_handoff_refs"]
    assert isinstance(refs, list)
    _append_section(lines, "Failure handoff refs", [f"- {item}" for item in refs])
    _append_section(lines, "Warnings", _format_warnings(payload["warnings"]))
    return "\n".join(lines) + "\n"


def dispatch_module(args) -> tuple[dict[str, object], int]:
    project_root = args.project_root.resolve()
    if args.module_command == "find":
        items, warnings = find_modules(
            project_root,
            query=args.query,
            readiness=args.readiness,
            source_state=args.source_state,
            limit=args.limit,
        )
        payload = {
            "ok": True,
            "command": "module find",
            "project_root": str(project_root),
            "query": args.query,
            "count": len(items),
            "items": items,
            "warnings": [warning_to_dict(item) for item in warnings],
        }
        return payload, 0
    module_payload, warnings, error_code = module_show(project_root, selector=args.selector)
    payload = {
        "ok": error_code is None,
        "command": "module show",
        "project_root": str(project_root),
        "selector": args.selector,
        "module": module_payload,
        "warnings": [warning_to_dict(item) for item in warnings],
    }
    return payload, 0 if error_code is None else 2


def dispatch_file(args) -> tuple[dict[str, object], int]:
    project_root = args.project_root.resolve()
    file_payload, warnings, error_code = file_show(
        project_root,
        raw_path=args.path,
        module_selector=args.module,
    )
    payload = {
        "ok": error_code is None,
        "command": "file show",
        "project_root": str(project_root),
        "path": args.path,
        "file": file_payload,
        "warnings": [warning_to_dict(item) for item in warnings],
    }
    return payload, 0 if error_code is None else 2
