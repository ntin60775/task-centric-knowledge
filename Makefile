PYTHON ?= python3
USER_BIN ?= $(HOME)/.local/bin
TASK_KNOWLEDGE_BIN := $(USER_BIN)/task-knowledge
PYTHON_SITE ?= $(shell "$(PYTHON)" -c 'import os, site, sysconfig; purelib = sysconfig.get_path("purelib"); target = purelib if os.access(purelib, os.W_OK) else site.getusersitepackages(); print(target)')
TASK_KNOWLEDGE_PTH := $(PYTHON_SITE)/task_knowledge_local.pth
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
	printf '%s\n' '#!/usr/bin/env bash' 'exec "$(PYTHON)" "$(CURDIR)/scripts/task_knowledge_cli.py" "$$@"' > "$(TASK_KNOWLEDGE_BIN)"
	chmod +x "$(TASK_KNOWLEDGE_BIN)"
	printf '%s\n' '$(CURDIR)/scripts' > "$(TASK_KNOWLEDGE_PTH)"

check:
	"$(PYTHON)" -m compileall -q scripts tests
	"$(PYTHON)" -m unittest discover -s tests -v
