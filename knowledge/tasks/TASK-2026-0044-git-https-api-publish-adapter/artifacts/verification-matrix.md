# Verification Matrix: TASK-2026-0044

| Инвариант | Сценарий нарушения | Проверка | Статус |
|-----------|-------------------|----------|--------|
| Нет обязательной зависимости от gh/glab | Publish-flow падает без gh/glab | Удалить `gh`/`glab` из PATH, запустить `task-knowledge workflow publish` с токеном | pending |
| HTTPS API создаёт PR/MR | Неправильный payload или auth | Mock-тесты на HTTP-запросы | pending |
| Fallback-цепочка корректна | Приоритет нарушен | Unit-тест `test_publish_flow.py` с патчами адаптеров | pending |
| Нет heavy deps | Добавлен `requests`/`httpx` | `grep -E "requests|httpx" scripts/task_workflow_runtime/*.py` | pending |
| JSON-контракт стабилен | Ломающее изменение в publish-flow | Golden-тесты и `test_task_knowledge_cli.py` | pending |
