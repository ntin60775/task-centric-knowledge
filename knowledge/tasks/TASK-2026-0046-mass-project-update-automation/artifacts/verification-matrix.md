# Verification Matrix: TASK-2026-0046

| Инвариант | Сценарий нарушения | Проверка | Статус |
|-----------|-------------------|----------|--------|
| Только явный запрос | Команда запускается неявно | Unit-тест: вызов `install-global` не триггерит mass update | pending |
| Dry-run не мутирует | Проект изменён при `--dry-run` | Тест с `tempfile.TemporaryDirectory` + `--dry-run` + diff | pending |
| Ошибка не останавливает batch | Первый failed project прерывает цикл | Тест с mock-failure на втором проекте | pending |
| Verify-project обязателен | Apply без verify | Тест: verify должен вызываться после apply | pending |
| Отчёт содержит все проекты | Пропущенный проект в выводе | Проверка JSON/text output на полноту | pending |
