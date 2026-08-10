# Матрица автоматизации smoke-тестов

Источник сценариев: `cloud/SMOKE_TEST_SCENARIO.md`, ветки `dev` проектов `ui` и `cloud`.

## Автоматизировано

| Сценарий | Приоритет | Тест | Что проверяется |
|---|---:|---|---|
| ENV-01 | P0 | `test_health.py` | Доступность `GET /api/health` и JSON-ответ |
| AUTH-01 | P0 | `test_auth.py` | Keycloak-вход, reload сессии, прямой URL буровой |
| AUTH-04 | P0 | `test_auth.py` | Выход и сокрытие защищённого UI |
| EDGE-01 | P0 | `test_edges.py` | Список, статистика, refresh, отсутствие runtime errors |
| EDGE-02 | P0 | `test_edges.py` | Поиск по ID, отсутствие результата, восстановление списка |
| EDGE-03 | P0 | `test_edges.py` | Открытие карточки и возврат к списку |
| OVERVIEW-01 | P0 | `test_overview.py` | Заголовок, summary-карточки, SSE/polling status |
| OVERVIEW-02 | P0 | `test_overview.py` | Маршруты Overview/Archive/Indicators/Video |
| CURRENT-01 | P0 | `test_current.py` | Виджеты показателей и поиск |
| CURRENT-02 | P1 | `test_current.py` | Изменение подготовленного live-тега без reload |
| CURRENT-03 | P0 | `test_current.py` | Canvas live-графика или корректное пустое состояние |
| HISTORY-01/02 | P0 | `test_history.py` | Picker показателей и построение/empty state архива |
| HISTORY-03 | P0 | `test_history.py` | Переключение периода на 1 час |
| HISTORY-06 | P1 | `test_history.py` | Добавление и удаление нескольких графиков |
| VIDEO-01 | P0 | `test_video.py` | Камера, video element, опционально реальный playback |
| VIDEO-03 | P0 | `test_video.py` | Понятное состояние буровой без камер |
| SETTINGS-01 | P0 | `test_settings.py` | Открытие, сохранение, modal, reload и восстановление настройки |
| API-CONTRACT | P1 | `test_api_contract.py` | Формат edge/current/history/camera/settings и статус-коды |
| AUTH-ROLES | P1 | `test_roles.py` | admin, edge-only, пользователь без ролей, изоляция настроек |
| EDGE/CURRENT/CAMERA/SETTINGS-500 | P2 | `test_api_errors.py` | Безопасное и понятное состояние UI при ответе API 500 |
| REALTIME-SSE | P1 | `test_realtime.py` | Одно SSE-соединение, отсутствие дублей и fallback polling |
| VIDEO-02 | P1 | `test_video_connections.py` | Закрытие WebSocket и ровно одно соединение после возврата |
| UI-QUALITY | P2 | `test_accessibility.py` | accessible names, duplicate IDs, overflow и ширины 1024–1920 |
| UI-VISUAL | P2 | `test_visual.py` | Явно утверждённые screenshot baselines с PNG diff |
| RUNTIME | P2 | `test_runtime_quality.py` | Бюджет current-запросов и корректный неизвестный SPA-маршрут |

## Оставлено ручным или требует управляемого стенда

- AUTH-02: неверный пароль оставлен ручным, чтобы автоматизация не включала защиту Keycloak от перебора.
- HISTORY-07: сложные деградации архива при частичном отказе БД требуют отдельного управляемого backend-стенда.
- CURRENT-02 без `E2E_LIVE_TAG`: невозможно отличить дефект SSE от действительно постоянного показателя.
- HISTORY-04/05: функциональные состояния покрыты, но математическую корректность каждого пикселя ECharts/avg-линии по-прежнему подтверждаем ручным исследовательским тестом.
- Длительные memory/performance-прогоны видео и браузера остаются отдельной нагрузочной задачей; smoke проверяет жизненный цикл соединений и бюджет запросов.
- YDISK-01/02: относится к `mqtt-ingest` и внешнему Яндекс.Диску; нужен отдельный integration suite с секретом и короткими archive buckets.
- Browser zoom и мобильные устройства не входят в desktop-продуктовый контракт; Chromium/Firefox и ширины 1024–1920 запускаются автоматизированно.

## Правило интерпретации результата

- `PASSED`: сценарий выполнен и ожидаемое состояние подтверждено.
- `FAILED`: функциональный дефект, проблема окружения либо неверные тестовые данные — смотреть trace, screenshot и diagnostics.
- `SKIPPED`: для сценария не задано необходимое значение `.env`; причина всегда указана в отчёте.
- P0 считается успешным, если все применимые проверки прошли, а пропуски сценариев с видео/спецданными согласованы до запуска.
