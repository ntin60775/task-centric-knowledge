install-local:
	mkdir -p "$(HOME)/.local/bin"
	printf '%s\n' '#!/usr/bin/env bash' 'exec python3 "$(CURDIR)/scripts/task_knowledge_cli.py" "$$@"' > "$(HOME)/.local/bin/task-knowledge"
	chmod +x "$(HOME)/.local/bin/task-knowledge"
