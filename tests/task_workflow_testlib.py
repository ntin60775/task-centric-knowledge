from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def git(project_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(project_root), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()


class TempRepoCase(unittest.TestCase):
    def make_tempdir(self) -> tempfile.TemporaryDirectory[str]:
        return tempfile.TemporaryDirectory()

    def init_repo(self, root: Path) -> Path:
        project_root = root / "project"
        project_root.mkdir()
        git(project_root, "init")
        git(project_root, "config", "user.name", "Test User")
        git(project_root, "config", "user.email", "test@example.com")
        (project_root / "README.md").write_text("repo\n", encoding="utf-8")
        git(project_root, "add", "README.md")
        git(project_root, "commit", "-m", "init")
        return project_root

    def write_registry(self, project_root: Path) -> None:
        registry_path = project_root / "knowledge/tasks/registry.md"
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text(
            textwrap.dedent(
                """\
                # Реестр задач

                | ID | Parent ID | Статус | Приоритет | Ветка | Каталог | Краткое описание |
                |----|-----------|--------|-----------|-------|---------|------------------|
                """
            ),
            encoding="utf-8",
        )

    def write_task(
        self,
        task_dir: Path,
        *,
        task_id: str,
        slug: str,
        branch: str = "не создана",
        goal: str = "Краткое описание задачи.",
        status: str = "в работе",
        priority: str = "средний",
        human_description: str = "Краткое описание задачи.",
        reference_mode: str = "нет",
    ) -> None:
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "task.md").write_text(
            textwrap.dedent(
                f"""\
                # Карточка задачи {task_id}

                ## Паспорт

                | Поле | Значение |
                |------|----------|
                | ID задачи | `{task_id}` |
                | Parent ID | `—` |
                | Уровень вложенности | `0` |
                | Ключ в путях | `{task_id}` |
                | Технический ключ для новых именуемых сущностей | `—` |
                | Краткое имя | `{slug}` |
                | Человекочитаемое описание | `{human_description}` |
                | Справочный режим | `{reference_mode}` |
                | Статус | `{status}` |
                | Приоритет | `{priority}` |
                | Ответственный | `Codex` |
                | Ветка | `{branch}` |
                | Требуется SDD | `нет` |
                | Статус SDD | `не требуется` |
                | Ссылка на SDD | `—` |
                | Дата создания | `2026-04-09` |
                | Дата обновления | `2026-04-09` |

                ## Цель

                {goal}

                ## Текущий этап

                Черновик.
                """
            ),
            encoding="utf-8",
        )
