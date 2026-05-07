"""Path-safety helpers for mutating workflow commands."""

from __future__ import annotations

from pathlib import Path


## @brief Resolve a path and ensure it lies inside the project root.
#  @param project_root Path to the project root.
#  @param path Path to resolve, either absolute or relative to project_root.
#  @param field_name Name of the field being validated (used in error messages).
#  @return Fully resolved path inside the project root.
#  @exception ValueError If the resolved path escapes project_root.
def resolve_inside_project_root(project_root: Path, path: Path, *, field_name: str) -> Path:
    resolved_project_root = project_root.resolve()
    candidate = path if path.is_absolute() else resolved_project_root / path
    resolved_candidate = candidate.resolve()
    try:
        resolved_candidate.relative_to(resolved_project_root)
    except ValueError as error:
        raise ValueError(
            f"{field_name}_outside_project_root: `{field_name}` должен находиться внутри project_root; "
            f"project_root={resolved_project_root}; {field_name}={resolved_candidate}"
        ) from error
    return resolved_candidate


## @brief Resolve a task directory path and ensure it lies inside the project root.
#  @param project_root Path to the project root.
#  @param task_dir Path to the task directory.
#  @return Fully resolved task directory path inside the project root.
#  @exception ValueError If the resolved path escapes project_root.
def resolve_task_dir_inside_project(project_root: Path, task_dir: Path) -> Path:
    return resolve_inside_project_root(project_root, task_dir, field_name="task_dir")
