#!/usr/bin/env python3
"""Install and verify the user-local live copy of the task-centric-knowledge skill."""

from __future__ import annotations

import argparse
import filecmp
import json
import os
import shutil
import site
import subprocess
import sys
import sysconfig
from dataclasses import asdict, dataclass
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SRC_DIR = SCRIPT_DIR.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from task_knowledge.install_runtime.models import REQUIRED_RELATIVE_PATHS, SKILL_NAME


DEPLOY_INCLUDE_PATHS = (
    "SKILL.md",
    "README.md",
    "Makefile",
    "pyproject.toml",
    "agents",
    "assets",
    "borrowings",
    "references",
    "scripts",
    "src",
    "tests",
)
DEPLOY_EXCLUDED_DIR_NAMES = {"__pycache__"}
DEPLOY_TARGET_TOP_LEVEL_EXTRA_DIR_NAMES = {".codex", ".git", "knowledge", "output"}
DEPLOY_EXCLUDED_FILE_NAMES = {".gitignore", "AGENTS.md", "zip_context_ignore.md"}
DEPLOY_EXCLUDED_SUFFIXES = {".pyc"}


@dataclass(frozen=True)
class DeployFile:
    """Single file entry in a deployment plan.

    Args:
        relative: Relative path within the skill.
        source: Absolute source filesystem path.
        target: Absolute target filesystem path.
        status: Deployment action status for this file.
    """
    relative: str
    source: str
    target: str
    status: str


@dataclass(frozen=True)
class VerificationIssue:
    """Describes a single verification failure.

    Args:
        relative: Relative path or identifier of the affected resource.
        detail: Human-readable explanation of the issue.
    """
    relative: str
    detail: str


@dataclass(frozen=True)
class SmokeResult:
    """Result of a single smoke-test command execution.

    Args:
        name: Short name of the checked component.
        command: The executed command as a list of arguments.
        returncode: Process exit code.
        ok: Whether the check is considered successful.
        stdout_excerpt: Trimmed standard output.
        stderr_excerpt: Trimmed standard error.
    """
    name: str
    command: list[str]
    returncode: int
    ok: bool
    stdout_excerpt: str
    stderr_excerpt: str


def default_source_root() -> Path:
    """Return the canonical source root for the skill.

    Returns:
        Path to the repository root containing the skill sources.
    """
    return SCRIPT_DIR.parent.resolve()


def default_target_root() -> Path:
    """Return the default user-local installation directory.

    Returns:
        Path under ~/.agents/skills for the live copy.
    """
    return Path.home() / ".agents" / "skills" / SKILL_NAME


def default_user_bin() -> Path:
    """Return the default user-local bin directory.

    Returns:
        Path to ~/.local/bin.
    """
    return Path.home() / ".local" / "bin"


def default_python_site() -> Path:
    """Return a writable Python site-packages directory.

    Returns:
        The system purelib path if writable, otherwise the user site-packages path.
    """
    purelib = sysconfig.get_path("purelib")
    if purelib and os.access(purelib, os.W_OK):
        return Path(purelib)
    return Path(site.getusersitepackages())


def should_skip_manifest_path(path: Path) -> bool:
    """Determine whether a source path should be excluded from the manifest.

    Args:
        path: Filesystem path to evaluate.

    Returns:
        True if the path matches excluded names or suffixes.
    """
    if path.name in DEPLOY_EXCLUDED_DIR_NAMES or path.name in DEPLOY_EXCLUDED_FILE_NAMES:
        return True
    return path.suffix in DEPLOY_EXCLUDED_SUFFIXES


def should_ignore_target_noise(path: Path, root: Path) -> bool:
    """Determine whether a target path is deployment noise.

    Args:
        path: Filesystem path to evaluate.
        root: Target root used for relative-path checks.

    Returns:
        True if the path is inside an excluded directory or has an excluded suffix.
    """
    relative_parts = path.relative_to(root).parts
    if any(part in DEPLOY_EXCLUDED_DIR_NAMES for part in relative_parts):
        return True
    return path.suffix in DEPLOY_EXCLUDED_SUFFIXES


def iter_manifest_files(source_root: Path) -> list[Path]:
    """Collect all source files that belong to the deployment manifest.

    Args:
        source_root: Root of the skill repository.

    Returns:
        Sorted list of source file paths.
    """
    files: list[Path] = []
    for include in DEPLOY_INCLUDE_PATHS:
        root = source_root / include
        if not root.exists():
            continue
        if root.is_file():
            if not should_skip_manifest_path(root):
                files.append(root)
            continue
        for path in root.rglob("*"):
            if any(part in DEPLOY_EXCLUDED_DIR_NAMES for part in path.relative_to(source_root).parts):
                continue
            if path.is_file() and not should_skip_manifest_path(path):
                files.append(path)
    return sorted(files, key=lambda item: item.relative_to(source_root).as_posix())


def _absolute_target_for_check(target_root: Path, target_path: Path) -> Path:
    if target_path.is_absolute():
        return target_path
    root = target_root if target_root.is_absolute() else Path.cwd() / target_root
    return root / target_path


def target_path_safety_status(target_root: Path, target_path: Path) -> str | None:
    """Check whether a target path is safe to write.

    Args:
        target_root: Root of the live skill copy.
        target_path: Destination path to evaluate.

    Returns:
        None if safe, otherwise a blocked-target-* status string.
    """
    resolved_root = target_root.resolve()
    absolute_target = _absolute_target_for_check(target_root, target_path)

    try:
        relative_parts = absolute_target.relative_to(target_root if target_root.is_absolute() else Path.cwd() / target_root).parts
    except ValueError:
        return "blocked-target-outside-root"

    current = target_root if target_root.is_absolute() else Path.cwd() / target_root
    for part in relative_parts:
        current = current / part
        if current.is_symlink():
            return "blocked-target-symlink"

    resolved_target = absolute_target.resolve(strict=False)
    try:
        resolved_target.relative_to(resolved_root)
    except ValueError:
        return "blocked-target-outside-root"
    return None


def status_for_file(source_path: Path, target_path: Path, *, target_root: Path) -> str:
    """Compute the deployment status for a single source file.

    Args:
        source_path: Path to the source file.
        target_path: Corresponding destination path.
        target_root: Root of the live skill copy.

    Returns:
        Deployment action status string.
    """
    safety_status = target_path_safety_status(target_root, target_path)
    if safety_status is not None:
        return safety_status
    if not target_path.exists():
        return "create"
    if not target_path.is_file():
        return "blocked-target-not-file"
    if filecmp.cmp(source_path, target_path, shallow=False):
        return "unchanged"
    return "update"


def build_plan(source_root: Path, target_root: Path) -> list[DeployFile]:
    """Build the full deployment plan from source to target.

    Args:
        source_root: Root of the skill repository.
        target_root: Root of the live skill copy.

    Returns:
        List of DeployFile entries describing every planned action.
    """
    source_root = source_root.resolve()
    target_root = target_root.resolve()
    plan: list[DeployFile] = []
    for source_path in iter_manifest_files(source_root):
        relative = source_path.relative_to(source_root).as_posix()
        target_path = target_root / relative
        plan.append(
            DeployFile(
                relative=relative,
                source=str(source_path),
                target=str(target_path),
                status=status_for_file(source_path, target_path, target_root=target_root),
            )
        )
    return plan


def plan_blocking_issues(plan: list[DeployFile]) -> list[VerificationIssue]:
    """Extract blocking issues from a deployment plan.

    Args:
        plan: Deployment plan to inspect.

    Returns:
        List of VerificationIssue for every blocked target.
    """
    return [
        VerificationIssue(item.relative, f"manifest target is unsafe: {item.status}")
        for item in plan
        if item.status.startswith("blocked-target-")
    ]


def required_missing(root: Path) -> list[str]:
    """List required relative paths that are absent from the given root.

    Args:
        root: Directory to inspect.

    Returns:
        List of missing required relative paths.
    """
    return [relative for relative in REQUIRED_RELATIVE_PATHS if not (root / relative).exists()]


def apply_plan(plan: list[DeployFile]) -> list[DeployFile]:
    """Copy source files to their targets according to the plan.

    Args:
        plan: Deployment plan to execute.

    Returns:
        List of DeployFile entries that were actually copied.

    Note:
        Returns an empty list if the plan contains any blocking issues.
    """
    if plan_blocking_issues(plan):
        return []
    applied: list[DeployFile] = []
    for item in plan:
        if item.status == "unchanged":
            continue
        source = Path(item.source)
        target = Path(item.target)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        applied.append(item)
    return applied


def target_extra_files(target_root: Path, manifest_relatives: set[str]) -> list[str]:
    """Find files present in the target but not in the manifest.

    Args:
        target_root: Root of the live skill copy.
        manifest_relatives: Set of relative paths known to the manifest.

    Returns:
        Sorted list of extra file and directory paths.
    """
    if not target_root.exists():
        return []
    extras: list[str] = []
    for path in sorted(target_root.iterdir(), key=lambda item: item.name):
        if path.is_dir() and path.name in DEPLOY_TARGET_TOP_LEVEL_EXTRA_DIR_NAMES:
            extras.append(f"{path.name}/")
            continue
        if path.is_file() and not should_ignore_target_noise(path, target_root):
            relative = path.relative_to(target_root).as_posix()
            if relative not in manifest_relatives:
                extras.append(relative)
            continue
        if not path.is_dir():
            continue
        for nested in path.rglob("*"):
            if should_ignore_target_noise(nested, target_root):
                continue
            if nested.is_file():
                relative = nested.relative_to(target_root).as_posix()
                if relative not in manifest_relatives:
                    extras.append(relative)
    return sorted(extras)


def verify_target(source_root: Path, target_root: Path) -> tuple[list[VerificationIssue], list[str]]:
    """Verify the live skill copy against the source manifest.

    Args:
        source_root: Root of the skill repository.
        target_root: Root of the live skill copy.

    Returns:
        Tuple of verification issues and extra target files.
    """
    source_root = source_root.resolve()
    target_root = target_root.resolve()
    issues: list[VerificationIssue] = []
    for relative in required_missing(target_root):
        issues.append(VerificationIssue(relative, "required resource is missing in live skill copy"))
    manifest = iter_manifest_files(source_root)
    manifest_relatives = {path.relative_to(source_root).as_posix() for path in manifest}
    for source_path in manifest:
        relative = source_path.relative_to(source_root).as_posix()
        target_path = target_root / relative
        safety_status = target_path_safety_status(target_root, target_path)
        if safety_status is not None:
            issues.append(VerificationIssue(relative, f"manifest target is unsafe: {safety_status}"))
            continue
        if not target_path.exists():
            issues.append(VerificationIssue(relative, "manifest file is missing in live skill copy"))
            continue
        if not target_path.is_file():
            issues.append(VerificationIssue(relative, "manifest target is not a file"))
            continue
        if not filecmp.cmp(source_path, target_path, shallow=False):
            issues.append(VerificationIssue(relative, "manifest file differs from source"))
    return issues, target_extra_files(target_root, manifest_relatives)


def excerpt(text: str, limit: int = 2000) -> str:
    """Return the trailing portion of a text string.

    Args:
        text: Input string.
        limit: Maximum number of trailing characters to retain.

    Returns:
        Trimmed string.
    """
    return text[-limit:]


def trim_smoke_result(smoke: SmokeResult) -> SmokeResult:
    """Trim stdout and stderr excerpts in a SmokeResult.

    Args:
        smoke: Original smoke result.

    Returns:
        New SmokeResult with trimmed output fields.
    """
    return SmokeResult(
        name=smoke.name,
        command=smoke.command,
        returncode=smoke.returncode,
        ok=smoke.ok,
        stdout_excerpt=excerpt(smoke.stdout_excerpt),
        stderr_excerpt=excerpt(smoke.stderr_excerpt),
    )


def run_command(
    command: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    keep_full_stdout: bool = False,
) -> SmokeResult:
    """Execute a shell command and capture its result.

    Args:
        command: Command and arguments as a list.
        cwd: Working directory for the subprocess.
        env: Environment variables to set.
        keep_full_stdout: Whether to keep the full stdout or trim it.

    Returns:
        SmokeResult summarising the execution.
    """
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
    except FileNotFoundError as error:
        return SmokeResult(
            name=Path(command[0]).name,
            command=command,
            returncode=127,
            ok=False,
            stdout_excerpt="",
            stderr_excerpt=str(error),
        )
    return SmokeResult(
        name=Path(command[0]).name,
        command=command,
        returncode=completed.returncode,
        ok=completed.returncode == 0,
        stdout_excerpt=completed.stdout if keep_full_stdout else excerpt(completed.stdout),
        stderr_excerpt=excerpt(completed.stderr),
    )


def install_cli_layer(target_root: Path, *, user_bin: Path | None, python_site: Path | None) -> SmokeResult:
    """Run the Makefile target that installs CLI wrappers.

    Args:
        target_root: Root of the live skill copy.
        user_bin: User bin directory for the wrapper.
        python_site: Python site-packages for the .pth file.

    Returns:
        SmokeResult of the make invocation.
    """
    env = os.environ.copy()
    command = ["make", "install-wrapper", f"PYTHON={sys.executable}"]
    if user_bin is not None:
        command.append(f"USER_BIN={user_bin}")
    if python_site is not None:
        command.append(f"PYTHON_SITE={python_site}")
    return run_command(command, cwd=target_root, env=env)


def verify_cli_layer(target_root: Path, *, user_bin: Path | None, python_site: Path | None) -> list[VerificationIssue]:
    """Verify that the user-site CLI wrapper and .pth file are correct.

    Args:
        target_root: Root of the live skill copy.
        user_bin: User bin directory to inspect.
        python_site: Python site-packages to inspect.

    Returns:
        List of VerificationIssue for any CLI-layer problems.
    """
    issues: list[VerificationIssue] = []
    resolved_user_bin = user_bin if user_bin is not None else default_user_bin()
    resolved_python_site = python_site if python_site is not None else default_python_site()
    wrapper_path = resolved_user_bin / "task-knowledge"
    if wrapper_path.is_symlink():
        issues.append(VerificationIssue("user-site CLI layer", f"task-knowledge wrapper is a symlink and is unsafe: {wrapper_path}"))
    elif not wrapper_path.exists():
        issues.append(VerificationIssue("user-site CLI layer", f"task-knowledge wrapper is missing: {wrapper_path}"))
    elif not wrapper_path.is_file():
        issues.append(VerificationIssue("user-site CLI layer", f"task-knowledge wrapper is not a file: {wrapper_path}"))
    else:
        wrapper_text = wrapper_path.read_text(encoding="utf-8")
        if "-m task_knowledge" not in wrapper_text:
            issues.append(
                VerificationIssue(
                    "user-site CLI layer",
                    f"task-knowledge wrapper does not invoke task_knowledge module: expected '-m task_knowledge' in wrapper",
                )
            )

    pth_path = resolved_python_site / "task_knowledge_local.pth"
    expected_pth = str((target_root / "src").resolve())
    if pth_path.is_symlink():
        issues.append(VerificationIssue("user-site CLI layer", f"task_knowledge_local.pth is a symlink and is unsafe: {pth_path}"))
    elif not pth_path.exists():
        issues.append(VerificationIssue("user-site CLI layer", f"task_knowledge_local.pth is missing: {pth_path}"))
    elif pth_path.read_text(encoding="utf-8").strip() != expected_pth:
        issues.append(
            VerificationIssue(
                "user-site CLI layer",
                f"task_knowledge_local.pth does not point to live skill copy: expected {expected_pth}",
            )
        )
    return issues


def validate_user_cli_smoke(smoke: SmokeResult, target_root: Path) -> SmokeResult:
    """Validate the JSON payload returned by the user CLI smoke test.

    Args:
        smoke: SmokeResult from the user CLI invocation.
        target_root: Root of the live skill copy.

    Returns:
        Trimmed SmokeResult, marked failed if the payload is invalid or roots mismatch.
    """
    if not smoke.ok:
        return trim_smoke_result(smoke)
    try:
        payload = json.loads(smoke.stdout_excerpt)
    except json.JSONDecodeError as error:
        return SmokeResult(
            name=smoke.name,
            command=smoke.command,
            returncode=2,
            ok=False,
            stdout_excerpt=excerpt(smoke.stdout_excerpt),
            stderr_excerpt=f"user CLI smoke did not return JSON doctor payload: {error}",
        )
    expected_runtime_root = str((target_root / "src" / "task_knowledge").resolve())
    expected_source_root = str(target_root.resolve())
    actual_runtime_root = payload.get("runtime_root")
    actual_source_root = payload.get("source_root")
    if actual_runtime_root != expected_runtime_root or actual_source_root != expected_source_root:
        return SmokeResult(
            name=smoke.name,
            command=smoke.command,
            returncode=2,
            ok=False,
            stdout_excerpt=excerpt(smoke.stdout_excerpt),
            stderr_excerpt=(
                "user CLI smoke resolved unexpected roots: "
                f"runtime_root={actual_runtime_root!r}, source_root={actual_source_root!r}, "
                f"expected_runtime_root={expected_runtime_root!r}, expected_source_root={expected_source_root!r}"
            ),
        )
    return trim_smoke_result(smoke)


def run_smoke_checks(target_root: Path, project_root: Path, *, user_bin: Path | None) -> list[SmokeResult]:
    """Run smoke tests against both the direct live copy and the user CLI.

    Args:
        target_root: Root of the live skill copy.
        project_root: Project root for the smoke checks.
        user_bin: User bin directory containing the task-knowledge wrapper.

    Returns:
        List of SmokeResult entries for each check.
    """
    direct_live_env = os.environ.copy()
    direct_live_env["PYTHONPATH"] = str(target_root / "src")
    direct_live = run_command(
        [
            sys.executable,
            "-m",
            "task_knowledge",
            "--json",
            "install",
            "check",
            "--project-root",
            str(project_root),
        ],
        env=direct_live_env,
    )
    cli_path = (user_bin / "task-knowledge") if user_bin is not None else Path.home() / ".local" / "bin" / "task-knowledge"
    user_cli = validate_user_cli_smoke(
        run_command(
            [
                str(cli_path),
                "--json",
                "doctor",
                "--project-root",
                str(project_root),
                "--source-root",
                str(target_root),
            ],
            keep_full_stdout=True,
        ),
        target_root,
    )
    return [direct_live, user_cli]


def summarize_plan(plan: list[DeployFile]) -> dict[str, int]:
    """Summarise a deployment plan by status counts.

    Args:
        plan: Deployment plan to analyse.

    Returns:
        Dictionary with total, create, update, unchanged and blocked counts.
    """
    return {
        "total": len(plan),
        "create": sum(1 for item in plan if item.status == "create"),
        "update": sum(1 for item in plan if item.status == "update"),
        "unchanged": sum(1 for item in plan if item.status == "unchanged"),
        "blocked": sum(1 for item in plan if item.status.startswith("blocked-target-")),
    }


def build_payload(
    *,
    mode: str,
    source_root: Path,
    target_root: Path,
    project_root: Path,
    plan: list[DeployFile],
    applied: list[DeployFile] | None = None,
    verification_issues: list[VerificationIssue] | None = None,
    extra_target_files: list[str] | None = None,
    smoke_results: list[SmokeResult] | None = None,
    cli_install: SmokeResult | None = None,
) -> dict[str, object]:
    """Assemble the final JSON-serialisable result payload.

    Args:
        mode: Execution mode (dry-run, apply or verify).
        source_root: Root of the skill repository.
        target_root: Root of the live skill copy.
        project_root: Project root used for smoke checks.
        plan: Full deployment plan.
        applied: Files that were actually copied.
        verification_issues: List of verification issues found.
        extra_target_files: Files present in the target but not in the manifest.
        smoke_results: Results of smoke-test executions.
        cli_install: Result of the CLI-layer installation.

    Returns:
        Dictionary suitable for JSON output.
    """
    source_missing = required_missing(source_root)
    verification_issues = verification_issues or []
    smoke_results = smoke_results or []
    ok = not source_missing and not verification_issues
    if mode == "verify":
        ok = ok and not verification_issues and all(item.ok for item in smoke_results)
    if mode == "apply":
        ok = ok and not verification_issues and all(item.ok for item in smoke_results) and (cli_install is None or cli_install.ok)
    return {
        "ok": ok,
        "mode": mode,
        "skill": SKILL_NAME,
        "source_root": str(source_root),
        "target_root": str(target_root),
        "project_root": str(project_root),
        "plan_summary": summarize_plan(plan),
        "source_missing": source_missing,
        "applied": [asdict(item) for item in applied or []],
        "verification_issues": [asdict(item) for item in verification_issues],
        "extra_target_files": extra_target_files or [],
        "cli_install": asdict(cli_install) if cli_install is not None else None,
        "smoke_results": [asdict(item) for item in smoke_results],
    }


def print_text(payload: dict[str, object]) -> None:
    """Print the result payload in human-readable text form.

    Args:
        payload: Dictionary produced by build_payload.
    """
    print(f"skill={payload['skill']}")
    print(f"mode={payload['mode']}")
    print(f"source_root={payload['source_root']}")
    print(f"target_root={payload['target_root']}")
    print(f"project_root={payload['project_root']}")
    print(f"ok={payload['ok']}")
    print(f"plan_summary={payload['plan_summary']}")
    for relative in payload["source_missing"]:
        print(f"- [error] source_missing: {relative}")
    for issue in payload["verification_issues"]:
        print(f"- [error] verify: {issue['relative']} — {issue['detail']}")
    for relative in payload["extra_target_files"]:
        print(f"- [warning] extra_target_file: {relative}")
    cli_install = payload.get("cli_install")
    if cli_install:
        print(f"- [{'ok' if cli_install['ok'] else 'error'}] cli_install: {' '.join(cli_install['command'])}")
    for smoke in payload["smoke_results"]:
        print(f"- [{'ok' if smoke['ok'] else 'error'}] smoke: {' '.join(smoke['command'])}")


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser for the install CLI.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(description="Install or verify the user-local live copy of task-centric-knowledge.")
    parser.add_argument("--mode", choices=("dry-run", "apply", "verify"), default="dry-run")
    parser.add_argument("--source-root", default=str(default_source_root()))
    parser.add_argument("--target-root", default=str(default_target_root()))
    parser.add_argument("--project-root", default=str(default_source_root()))
    parser.add_argument("--user-bin")
    parser.add_argument("--python-site")
    parser.add_argument("--skip-cli-install", action="store_true")
    parser.add_argument("--skip-smoke", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the install/verify CLI.

    Args:
        argv: Optional argument list; defaults to sys.argv.

    Returns:
        Exit code 0 on success, 2 on failure.
    """
    args = build_parser().parse_args(argv)
    source_root = Path(args.source_root).resolve()
    target_root = Path(args.target_root).resolve()
    project_root = Path(args.project_root).resolve()
    user_bin = Path(args.user_bin).resolve() if args.user_bin else None
    python_site = Path(args.python_site).resolve() if args.python_site else None
    plan = build_plan(source_root, target_root)
    blocking_issues = plan_blocking_issues(plan)
    applied: list[DeployFile] = []
    cli_install: SmokeResult | None = None
    smoke_results: list[SmokeResult] = []
    if args.mode == "apply" and not blocking_issues:
        applied = apply_plan(plan)
        if not args.skip_cli_install:
            cli_install = install_cli_layer(target_root, user_bin=user_bin, python_site=python_site)
        if not args.skip_smoke:
            smoke_results = run_smoke_checks(target_root, project_root, user_bin=user_bin)
    elif args.mode == "verify" and not args.skip_smoke:
        smoke_results = run_smoke_checks(target_root, project_root, user_bin=user_bin)
    if args.mode == "dry-run" or blocking_issues:
        verification_issues: list[VerificationIssue] = blocking_issues
        extra_target_files: list[str] = []
    else:
        verification_issues, extra_target_files = verify_target(source_root, target_root)
        verification_issues = blocking_issues + verification_issues
        if args.mode == "verify" or not args.skip_cli_install:
            verification_issues.extend(verify_cli_layer(target_root, user_bin=user_bin, python_site=python_site))
    payload = build_payload(
        mode=args.mode,
        source_root=source_root,
        target_root=target_root,
        project_root=project_root,
        plan=plan,
        applied=applied,
        verification_issues=verification_issues,
        extra_target_files=extra_target_files,
        smoke_results=smoke_results,
        cli_install=cli_install,
    )
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_text(payload)
    return 0 if payload["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
