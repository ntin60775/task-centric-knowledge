PYTHON ?= python3
USER_BIN ?= $(HOME)/.local/bin
TASK_KNOWLEDGE_BIN := $(USER_BIN)/task-knowledge
PYTHON_SITE ?= $(shell "$(PYTHON)" -c 'import os, site, sysconfig; purelib = sysconfig.get_path("purelib"); target = purelib if os.access(purelib, os.W_OK) else site.getusersitepackages(); print(target)')
TASK_KNOWLEDGE_PTH := $(PYTHON_SITE)/task_knowledge_local.pth

install-local:
	@if "$(PYTHON)" -c 'import setuptools' >/dev/null 2>&1; then \
		"$(PYTHON)" -m pip install --user --editable . --no-build-isolation; \
	else \
		$(MAKE) install-wrapper PYTHON="$(PYTHON)" USER_BIN="$(USER_BIN)" PYTHON_SITE="$(PYTHON_SITE)"; \
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
