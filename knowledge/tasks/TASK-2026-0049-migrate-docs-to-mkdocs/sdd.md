# SDD: Миграция docs-инфраструктуры на mkdocstrings + MkDocs

## 1. Контекст

Текущая система использует Doxygen для документирования Python runtime. Doxygen неидиоматичен для Python: требует `## @brief` перед декораторами, плохо понимает type hints и Python AST. Задача — мигрировать на `mkdocstrings + MkDocs` с нативными Google-style docstrings и программной проверкой покрытия через Griffe.

## 2. Целевая архитектура

### 2.1 Компоненты

| Компонент | Роль | Технология |
|-----------|------|------------|
| Docstring source | Исходники документации | Google-style docstrings в `scripts/` |
| Doc generator | Сборка Markdown + HTML | MkDocs + mkdocstrings |
| AST parser | Извлечение API model | Griffe (бэкенд mkdocstrings) |
| Coverage checker | Проверка покрытия | `scripts/check_doc_coverage.py` (Griffe API) |
| Build orchestrator | Цели сборки | `Makefile` |

### 2.2 Поток данных

```
scripts/*.py (docstrings)
    → mkdocstrings (Griffe parses AST)
        → output/docs/api/*.md (Markdown API reference)
            → MkDocs → output/docs/site/ (HTML for human)

scripts/*.py (AST)
    → Griffe (scripts/check_doc_coverage.py)
        → JSON-like object model
            → coverage report (stdout / exit code)
```

## 3. Допустимые связи

- `mkdocstrings` → `griffe` (бэкенд парсинга Python).
- `scripts/check_doc_coverage.py` → `griffe` (прямое использование библиотеки).
- `Makefile` → `mkdocs build`, `python3 scripts/check_doc_coverage.py`.
- `pyproject.toml` → `mkdocs`, `mkdocstrings[python]`, `griffe` в `[project.optional-dependencies]` или `[dependency-groups]` / `[tool.uv.dev-dependencies]`.

## 4. Недопустимые связи

- Не оставлять Doxygen-блоки (`## @brief`, `#  @param`) в `scripts/`.
- Не использовать reST-style docstrings (проект стандартизирует Google-style).
- Не добавлять runtime-зависимость от `mkdocs` / `griffe` — только dev.
- Не хранить сгенерированные `output/docs/` в git.

## 5. Формат docstrings (канонический)

Google-style:

```python
def load_module_passport(project_root: Path, passport_path: Path) -> ModulePassport:
    """Parse and validate a module passport from markdown.

    Args:
        project_root: Absolute path to the project root.
        passport_path: Absolute path to the `module.md` file.

    Returns:
        Validated `ModulePassport` instance.

    Raises:
        ModulePassportError: If passport format is invalid or fields mismatch.
    """
```

Правила:
- Однострочный docstring допустим только для тривиальных функций без параметров.
- Args / Returns / Raises — секции обязательны, если есть параметры / возвращаемое значение / исключения.
- Type information в docstrings не дублируется (уже в type hints).

## 6. Конфигурация mkdocs.yml (sketch)

```yaml
site_name: task-centric-knowledge API
site_url: ""
use_directory_urls: false

plugins:
  - search
  - mkdocstrings:
      default_handler: python
      handlers:
        python:
          paths: [scripts]
          options:
            docstring_style: google
            show_source: true
            show_root_heading: true

theme:
  name: material
```

## 7. Coverage checker (sketch)

```python
# scripts/check_doc_coverage.py
import sys
from pathlib import Path
import griffe

REQUIRED_PUBLIC_DOCSTRING = True


def check_package(package_path: Path) -> list[str]:
    loader = griffe.GriffeLoader()
    missing: list[str] = []
    for py_file in package_path.rglob("*.py"):
        if py_file.name.startswith("_"):
            continue
        module_path = py_file.relative_to(package_path).with_suffix("").as_posix().replace("/", ".")
        try:
            module = loader.load_module(module_path, search_paths=[str(package_path)])
        except Exception:
            continue
        for obj in module.walk(filter=lambda o: o.is_public and (o.is_function or o.is_class)):
            if not obj.docstring:
                missing.append(obj.path)
    return missing


if __name__ == "__main__":
    missing = check_package(Path("scripts"))
    if missing:
        for path in missing:
            print(f"MISSING_DOCSTRING: {path}")
        sys.exit(1)
    print("OK: all public API documented")
```

## 8. Makefile targets

```makefile
docs:
	mkdocs build -f mkdocs.yml -d output/docs/site/

docs-serve:
	mkdocs serve -f mkdocs.yml

docs-check:
	python3 -m compileall -q scripts tests
	python3 scripts/check_doc_coverage.py scripts/

docs-coverage: docs-check
```

## 9. Изменения в project layout

```
+ mkdocs.yml
+ scripts/check_doc_coverage.py
- Doxyfile                  (удалить)
  Makefile                  (обновить)
  pyproject.toml            (обновить)
  .gitignore                (обновить)
  scripts/                  (переписать docstrings)
```

## 10. Диагностические сигналы

| Симптом | Причина | Проверка |
|---------|---------|----------|
| `mkdocs build` падает с `mkdocstrings` error | Невалидный Google-style docstring | `make docs-check` |
| `MISSING_DOCSTRING` в stdout | Public API без docstring | `make docs-coverage` |
| `grep "## @brief"` находит совпадения | Незавершённая миграция | `grep -r "## @brief" scripts/` |
| Unit tests fail | Изменение imports / логики при миграции | `make check` |

## 11. Риски и митигация

| Риск | Митигация |
|------|-----------|
| Griffe не парсит какой-то Python 3.11+ синтаксис | Проверить на CI; при необходимости обновить Griffe. |
| MkDocs Material ломает offline-режим | Использовать `use_directory_urls: false` и локальные assets. |
| Объём ручной работы (переписывание docstrings) | Декомпозиция на подзадачи по модулям; возможно автоматизировать регулярками для простых `@brief`. |

## 12. Версионирование и обратная совместимость

- Удаление `Doxyfile` — breaking change для тех, кто использовал `make docs` с Doxygen.
- Старые `output/doxygen/` после удаления из `.gitignore` останутся в рабочей директории (не в git).
- `AGENTS.md` / `SKILL.md` должны обновиться, чтобы ссылки на `Doxyfile` указывали на `mkdocs.yml`.
