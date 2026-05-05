"""CLI output formatting for install skill runtime."""

from __future__ import annotations


def print_text_report(payload: dict[str, object]) -> None:
    print(f"skill={payload['skill']}")
    if "mode" in payload:
        print(f"mode={payload['mode']}")
    print(f"project_root={payload['project_root']}")
    print(f"profile={payload['profile']}")
    print(f"existing_system_classification={payload['existing_system_classification']}")
    for key in (
        "compatibility_epoch",
        "upgrade_status",
        "execution_rollout",
        "legacy_pending_count",
        "reference_manual_count",
    ):
        if key in payload:
            print(f"{key}={payload[key]}")
    print(f"ok={payload['ok']}")
    for item in payload["results"]:
        suffix = f" path={item['path']}" if item.get("path") else ""
        print(f"- [{item['status']}] {item['key']}: {item['detail']}{suffix}")
    for dependency in payload.get("dependencies", []):
        suffix = f" path={dependency['path']}" if dependency.get("path") else ""
        print(
            f"* dep name={dependency['name']} class={dependency['dependency_class']} "
            f"status={dependency['status']} layer={dependency['blocking_layer']}{suffix}"
        )
        print(f"  detail={dependency['detail']}")
        print(f"  hint={dependency['hint']}")
    if "targets" in payload:
        print(f"TARGET_COUNT={payload['target_count']}")
        print(f"COUNT={payload['count']}")
        print(f"SCOPE_LOCKED={payload['scope_locked']}")
        print(f"PLAN_FINGERPRINT={payload['plan_fingerprint']}")
        print(f"CONFIRM_COMMAND={payload['confirm_command']}")
        for key in ("safe_delete", "keep", "manual_review"):
            print(f"{key.upper()}={len(payload.get(key, []))}")
            for item in payload.get(key, []):
                count_suffix = f" item_count={item['item_count']}" if "item_count" in item else ""
                print(f"  - {item['path']} kind={item['kind']}{count_suffix}")
                print(f"    reason={item['reason']}")
