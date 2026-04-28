PYTHON ?= python3
USER_BIN ?= $(HOME)/.local/bin
TASK_KNOWLEDGE_BIN := $(USER_BIN)/task-knowledge
LIVE_SKILL_ROOT ?= $(HOME)/.agents/skills/task-centric-knowledge
PYTHON_SITE ?= $(shell "$(PYTHON)" -c 'import os, site, sysconfig; purelib = sysconfig.get_path("purelib"); target = purelib if os.access(purelib, os.W_OK) else site.getusersitepackages(); print(target)')
TASK_KNOWLEDGE_PTH := $(PYTHON_SITE)/task_knowledge_local.pth
SOURCE_ROOT ?= $(LIVE_SKILL_ROOT)
PROJECT_ROOT ?= $(CURDIR)
PROFILE ?= generic
PYTHON_EXTERNALLY_MANAGED ?= $(shell "$(PYTHON)" -c 'import pathlib, sys, sysconfig; marker = pathlib.Path(sysconfig.get_path("stdlib"), "EXTERNALLY-MANAGED"); in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix); print("1" if marker.exists() and not in_venv else "0")')
PYTHON_HAS_PIP ?= $(shell "$(PYTHON)" -c 'import pip' >/dev/null 2>&1 && echo 1 || echo 0)
PYTHON_HAS_SETUPTOOLS ?= $(shell "$(PYTHON)" -c 'import setuptools' >/dev/null 2>&1 && echo 1 || echo 0)

install-local:
	@if [ "$(PYTHON_EXTERNALLY_MANAGED)" = "1" ] || [ "$(PYTHON_HAS_PIP)" != "1" ] || [ "$(PYTHON_HAS_SETUPTOOLS)" != "1" ]; then \
		$(MAKE) install-wrapper PYTHON="$(PYTHON)" USER_BIN="$(USER_BIN)" PYTHON_SITE="$(PYTHON_SITE)"; \
	else \
		"$(PYTHON)" -m pip install --user --editable . --no-build-isolation; \
	fi

install-editable:
	"$(PYTHON)" -m pip install --user --editable . --no-build-isolation

install-wrapper:
	mkdir -p "$(USER_BIN)" "$(PYTHON_SITE)"
	@if [ -L "$(TASK_KNOWLEDGE_BIN)" ]; then echo "Refusing to overwrite symlink: $(TASK_KNOWLEDGE_BIN)" >&2; exit 2; fi
	@if [ -L "$(TASK_KNOWLEDGE_PTH)" ]; then echo "Refusing to overwrite symlink: $(TASK_KNOWLEDGE_PTH)" >&2; exit 2; fi
	printf '%s\n' '#!/usr/bin/env bash' 'exec "$(PYTHON)" "$(CURDIR)/scripts/task_knowledge_cli.py" "$$@"' > "$(TASK_KNOWLEDGE_BIN)"
	chmod +x "$(TASK_KNOWLEDGE_BIN)"
	printf '%s\n' '$(CURDIR)/scripts' > "$(TASK_KNOWLEDGE_PTH)"

install-global-dry-run:
	"$(PYTHON)" scripts/install_global_skill.py --mode dry-run --source-root "$(CURDIR)" --target-root "$(LIVE_SKILL_ROOT)"

install-global:
	"$(PYTHON)" scripts/install_global_skill.py --mode apply --source-root "$(CURDIR)" --target-root "$(LIVE_SKILL_ROOT)" --project-root "$(CURDIR)"

verify-global-install:
	"$(PYTHON)" scripts/install_global_skill.py --mode verify --source-root "$(CURDIR)" --target-root "$(LIVE_SKILL_ROOT)" --project-root "$(CURDIR)"

check:
	"$(PYTHON)" -m compileall -q scripts tests
	"$(PYTHON)" -m unittest discover -s tests -v

lint:
	"$(PYTHON)" -m ruff check scripts tests

typecheck:
	"$(PYTHON)" -m mypy scripts

check-strict: lint typecheck

check-production: check verify-global-install

project-install-check:
	task-knowledge install check --project-root "$(PROJECT_ROOT)" --source-root "$(SOURCE_ROOT)" --profile "$(PROFILE)"

project-install-apply:
	task-knowledge install apply --project-root "$(PROJECT_ROOT)" --source-root "$(SOURCE_ROOT)" --profile "$(PROFILE)" --force

project-install-verify:
	task-knowledge install verify-project --project-root "$(PROJECT_ROOT)" --source-root "$(SOURCE_ROOT)" --profile "$(PROFILE)" --force
