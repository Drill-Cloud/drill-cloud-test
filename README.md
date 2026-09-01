# Drill Cloud Test

Автоматизированный smoke-набор для Drill Cloud на **Python + pytest + Playwright**.

Проект проверяет реальный пользовательский маршрут: Keycloak → список буровых → обзор → показатели/live-график → архив → видео → глобальные настройки. Для каждого падения Playwright сохраняет trace, screenshot и video, а pytest формирует читаемый HTML-отчёт.

## Структура

```text
drill-cloud-test/
├── docs/SMOKE_AUTOMATION_MATRIX.md   # соответствие ручному smoke-сценарию
├── scripts/
│   ├── bootstrap.sh                  # установка Python-зависимостей и браузера
│   ├── run-smoke.sh                  # стандартный запуск с HTML-отчётом
│   ├── seed-test-data.sh             # управляемые e2e-* данные
│   └── publish-live-data.sh          # меняющийся live-тег
├── src/drill_cloud_test/
│   ├── config.py                     # единый источник конфигурации окружения
│   ├── diagnostics.py                # console/page/network diagnostics
│   ├── api.py, sessions.py           # API и изолированные ролевые сессии
│   ├── accessibility.py, visual.py   # UI quality-проверки
│   └── pages/                        # Page Objects без тестовой бизнес-логики
├── tests/                             # сценарии, сгруппированные по разделам продукта
├── .env.example
└── pyproject.toml
```

## Быстрый старт

### Что необходимо для запуска

- Python 3.11 или новее, доступный как `python3`, `python` либо `py`;
- Bash: в Windows рекомендуется Git Bash, в Linux/macOS используется системный Bash;
- сетевой доступ к UI, Cloud API и Keycloak выбранного стенда;
- тестовая учётная запись Keycloak, если авторизация включена;
- разрешённый redirect URI для адреса тестируемого UI;
- для полного набора — подготовленные буровые, история, live-данные, камера и ролевые учётные записи.

Docker для обычного запуска не требуется. Доступ к PostgreSQL нужен только для автоматического создания и удаления управляемых `e2e-*` данных.

```bash
cd /c/Users/myart/drill/drill-cloud-test
bash scripts/bootstrap.sh
cp .env.example .env
```

Заполните `.env`, как минимум:

```dotenv
E2E_BASE_URL=http://localhost:5173
E2E_API_URL=http://localhost:5173/api
E2E_USERNAME=test-user
E2E_PASSWORD=change-me
E2E_EDGE_ID=edge5-v3
```

Запуск обязательного P0:

```bash
bash scripts/run-smoke.sh
```

Запуск с видимым браузером:

```bash
bash scripts/run-smoke.sh --headed
```

Полный набор P0+P1+P2:

```bash
bash scripts/run-smoke.sh --priority all
```

## Основные команды

### Установка окружения

```bash
bash scripts/bootstrap.sh
```

Создаёт `.venv`, устанавливает проект с dev-зависимостями и загружает Chromium для Playwright. Команду достаточно выполнить при первом запуске и после изменения зависимостей в `pyproject.toml`.

```bash
bash scripts/bootstrap.sh --all-browsers
```

Дополнительно устанавливает Firefox и WebKit. Это нужно для кроссбраузерного прогона и release workflow.

### Запуск smoke-тестов

```bash
bash scripts/run-smoke.sh
```

Запускает обязательный профиль P0 и создаёт автономный отчёт `reports/smoke-report.html`.

```bash
bash scripts/run-smoke.sh --headed
```

Запускает P0 с видимым браузером. Режим удобен при разработке и разборе падений. Для более медленного выполнения можно добавить в `.env` `E2E_SLOW_MO_MS=500`.

```bash
bash scripts/run-smoke.sh --priority p1
bash scripts/run-smoke.sh --priority p2
bash scripts/run-smoke.sh --priority all
```

- `p0` — минимальный обязательный smoke;
- `p1` — расширенные интеграционные сценарии;
- `p2` — негативные, accessibility, responsive и runtime-проверки;
- `all` — вся коллекция без фильтра по приоритету.

Перед запуском необходимы настроенный `.env`, доступный стенд и установленный браузер Playwright. Сценарии, для которых не заданы специальные данные или учётные записи, будут отмечены как `SKIPPED` с указанием причины.

### Управляемые тестовые данные

```bash
bash scripts/seed-test-data.sh
```

Создаёт или обновляет безопасные буровые и показатели с префиксом `e2e-`, current-значения и историю. Необходим доступный `E2E_DATABASE_URL`. Если задан `E2E_VIDEO_WS_URL`, также создаётся тестовая камера.

```bash
bash scripts/seed-test-data.sh cleanup
```

Удаляет только созданные E2E-данные. Скрипт откажется работать с ID буровой без префикса `e2e-`.

```bash
bash scripts/publish-live-data.sh --duration 300
```

Пять минут отправляет меняющееся значение `e2e-live` через ingest API. Команда нужна для достоверной проверки SSE и live-графика. Требуются `E2E_API_URL`, `E2E_EDGE_ID` и, если ingest защищён, `E2E_INGEST_API_KEY`.

Интервал публикации можно изменить:

```bash
bash scripts/publish-live-data.sh --duration 600 --interval 2
```

## Ручная установка

```bash
PYTHON_BOOTSTRAP="$(command -v python3 || command -v python)"
"$PYTHON_BOOTSTRAP" -m venv .venv

if [[ -x .venv/Scripts/python.exe ]]; then
  VENV_PYTHON=.venv/Scripts/python.exe
else
  VENV_PYTHON=.venv/bin/python
fi

"$VENV_PYTHON" -m pip install -e ".[dev]"
"$VENV_PYTHON" -m playwright install chromium
```

Для Firefox/WebKit:

```bash
bash scripts/bootstrap.sh --all-browsers
```

## Конфигурация тестовых данных

Все параметры читаются только из `.env`; секреты в git не попадают.

| Переменная | Назначение | Обязательность |
|---|---|---|
| `E2E_BASE_URL` | URL UI | всегда |
| `E2E_API_URL` | базовый URL API с `/api` | всегда |
| `E2E_AUTH_MODE` | `auto`, `required` или `disabled` | по умолчанию `auto` |
| `E2E_USERNAME`, `E2E_PASSWORD` | тестовая учётная запись Keycloak | при включённом SSO |
| `E2E_ADMIN_*`, `E2E_EDGE_*`, `E2E_NO_ROLE_*` | отдельные учётные записи для матрицы ролей | для role-тестов |
| `E2E_API_TOKEN` | готовый Bearer token вместо перехвата токена UI | опционально |
| `E2E_EDGE_ID` | буровая с current/history | рекомендуется; иначе первая карточка |
| `E2E_FORBIDDEN_EDGE_ID` | буровая, запрещённая edge-пользователю | для проверки 403 |
| `E2E_VIDEO_EDGE_ID` | буровая с рабочей камерой | для VIDEO-01 |
| `E2E_NO_VIDEO_EDGE_ID` | буровая без камер | для VIDEO-03 |
| `E2E_INDICATOR_QUERY` | стабильный поиск показателя | опционально |
| `E2E_HISTORY_TAG_QUERY` | показатель с историей | рекомендуется |
| `E2E_LIVE_TAG` | гарантированно меняющийся тег | для CURRENT-02 |
| `E2E_REQUIRE_HISTORY_DATA` | требовать canvas, не принимать empty state | подготовленный стенд |
| `E2E_REQUIRE_VIDEO_PLAYBACK` | ждать фактическое воспроизведение | подготовленный поток |
| `E2E_DATABASE_URL` | PostgreSQL для seed/cleanup | только подготовка данных |
| `E2E_INGEST_API_KEY` | ключ `/ingest`, если он включён | live publisher |
| `E2E_VISUAL_ENABLED` | включить visual regression | по умолчанию `false` |
| `E2E_UPDATE_SNAPSHOTS` | осознанно перезаписать visual baselines | только локально |
| `E2E_UI_COMMIT`, `E2E_CLOUD_COMMIT` | версии стенда в отчёте | рекомендуется в CI |

Полный шаблон и значения по умолчанию находятся в [.env.example](.env.example).
Подготовка воспроизводимых данных подробно описана в [docs/TEST_DATA.md](docs/TEST_DATA.md).

## Команды pytest

```bash
VENV_PYTHON=.venv/Scripts/python.exe  # Git Bash в Windows
# VENV_PYTHON=.venv/bin/python        # Linux/macOS

# Только обязательный smoke
"$VENV_PYTHON" -m pytest -m p0

# Предрелизные проверки
"$VENV_PYTHON" -m pytest -m p1

# Один функциональный раздел
"$VENV_PYTHON" -m pytest -m history

# API-контракты и негативные ответы
"$VENV_PYTHON" -m pytest -m api

# SSE и WebSocket
"$VENV_PYTHON" -m pytest -m integration

# Доступность и responsive layout
"$VENV_PYTHON" -m pytest -m accessibility

# Один сценарий
"$VENV_PYTHON" -m pytest tests/test_settings.py -v

# HTML-отчёт
"$VENV_PYTHON" -m pytest -m p0 --html=reports/smoke-report.html --self-contained-html
```

## Артефакты и диагностика

После падения смотреть:

- `test-results/**/trace.zip` — открыть командой `python -m playwright show-trace <trace.zip>`;
- screenshot и video из того же каталога;
- `browser-diagnostics.txt` — ошибки Console, React/Page и неуспешные запросы;
- `reports/smoke-report.html` — сводный автономный HTML-отчёт.

Артефакты и `.env` исключены из git.

## Visual regression

Visual-тесты выключены по умолчанию. Первый утверждённый эталон создаётся только после ручной проверки страницы:

```bash
E2E_VISUAL_ENABLED=true E2E_UPDATE_SNAPSHOTS=true \
  "$VENV_PYTHON" -m pytest -m visual --browser chromium
```

Обычная проверка не меняет эталоны:

```bash
E2E_VISUAL_ENABLED=true \
  "$VENV_PYTHON" -m pytest -m visual --browser chromium
```

Эталоны лежат в `tests/visual_baselines/<browser>/`. При несовпадении фактический PNG и diff сохраняются в `test-results/visual/`.

## Запуск против локального UI

1. Запустите backend `cloud` либо настройте `DEV_API_URL` UI на доступный dev backend.
2. В проекте `ui` выполните `npm.cmd run dev`.
3. Укажите `E2E_BASE_URL=http://localhost:5173` и `E2E_API_URL=http://localhost:5173/api`.
4. Убедитесь, что redirect URI `http://localhost:5173/*` разрешён в клиенте Keycloak.
5. Запустите P0.

Текущие Page Objects опираются на стабильные `data-testid`, добавленные в ветку `dev` UI. Перед запуском нового набора против общего стенда эту версию UI нужно сначала развернуть.

При тестировании уже развёрнутого стенда укажите его HTTPS URL в обеих переменных; если API находится под тем же origin, добавьте `/api` в `E2E_API_URL`.

## Как добавлять тесты

1. Пользовательские действия раздела добавляются в соответствующий Page Object.
2. В тесте остаются только шаги сценария и бизнес-ожидания.
3. Тест получает маркеры `case`, `p0/p1/p2` и функциональный маркер.
4. Сценарий, который меняет серверное состояние, обязан восстанавливать его через `try/finally`.
5. Для отсутствующих тестовых данных используется `pytest.skip` с точной инструкцией, а не ложный `PASS`.
6. Обновляется [матрица автоматизации](docs/SMOKE_AUTOMATION_MATRIX.md).

## GitHub Actions

В проекте два workflow:

- `quality.yml` — lint, форматирование, mypy, unit и сбор коллекции на каждый PR;
- `e2e.yml` — единый ручной запуск для `dev`, `alpha` и `main`.

URL, идентификаторы тестовых данных и учётные записи хранятся в GitHub Environments, а не в общих repository variables/secrets. Полный список имён и готовые значения URL приведены в [docs/GITHUB_ENVIRONMENTS.md](docs/GITHUB_ENVIRONMENTS.md).

В каждом Environment необходимо создать как минимум:

- `E2E_USERNAME`;
- `E2E_PASSWORD`;
- variables `E2E_BASE_URL`, `E2E_API_URL`, `E2E_AUTH_MODE` и безопасные feature flags из инструкции.

После каждого CI-прогона HTML-отчёт, trace, screenshot и video публикуются единым artifact на 30 дней.

### Проверки PR тестового проекта

Workflow `.github/workflows/quality.yml` уже запускается автоматически для каждого PR в `drill-cloud-test`. Он не использует секреты и выполняет:

```bash
python -m ruff check .
python -m ruff format --check .
python -m mypy src tests scripts
python -m pytest -m unit -v
python -m pytest --collect-only -q
```

Чтобы запретить merge с ошибками, в GitHub откройте `Settings → Branches`, необходимо правило для `main`, включить `Require status checks to pass before merging` и выбрать check `Test project quality / quality`.

### Ручной E2E развёрнутого окружения

Полноценный Playwright-прогон требует секретов и уже работающего стенда. Он запускается только вручную и не участвует в обязательных проверках pull request:

1. Развернуть нужную версию на выбранном стенде.
2. Открыть `Actions → Environment E2E → Run workflow`.
3. Выбрать `dev`, `alpha` или `main`, профиль и браузер.
4. Workflow дождётся доступности UI/API и загрузит отчёт с Playwright-артефактами.

Не добавляйте `Environment E2E / e2e` в `Require status checks to pass before merging`. Ручное падение E2E останется видимым в Actions и артефактах, но не будет блокировать merge или deployment.

В `drill-cloud-test → Settings → Environments` создайте `dev`, `alpha` и `main` по [готовому списку](docs/GITHUB_ENVIRONMENTS.md).

GitHub не передаёт repository secrets workflow из внешнего fork. Поэтому PR из fork должен проходить безопасный `quality.yml`, а авторизованный E2E следует запускать после доверенного deployment, вручную через `workflow_dispatch` либо через защищённый GitHub Environment с approval.

## Проверка качества самого тестового проекта

```bash
VENV_PYTHON=.venv/Scripts/python.exe  # Git Bash в Windows
# VENV_PYTHON=.venv/bin/python        # Linux/macOS

"$VENV_PYTHON" -m ruff check .
"$VENV_PYTHON" -m ruff format --check .
"$VENV_PYTHON" -m mypy src tests scripts
"$VENV_PYTHON" -m pytest -m unit
"$VENV_PYTHON" -m pytest --collect-only
```

Page Objects используют role/label и добавленные в UI `data-testid`. CSS остаётся только для canvas/ECharts и диагностических проверок, где это естественная граница компонента.
