# Verification Matrix: TASK-2026-0042

| Инвариант | Сценарий нарушения | Проверка | Статус |
|-----------|-------------------|----------|--------|
| Package layout корректен | setuptools не находит модули | `python3 -m build --wheel` или `pip install -e .` | pending |
| CLI доступен после установки | Сломан entrypoint | `task-knowledge --help` после `make install-local` | pending |
| Глобальная установка работает | Live-copy не консистентна | `make install-global && make verify-global-install` | pending |
| Тесты проходят | Сломан импорт в тестах | `python3 -m unittest discover -s tests -v` | pending |
| Нет хаков sys.path | Код или тесты ломаются без `scripts` в PYTHONPATH | `grep -r "sys.path.insert.*scripts" tests/ scripts/` | pending |
