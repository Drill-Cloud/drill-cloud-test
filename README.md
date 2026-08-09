# Drill Cloud Test

Автоматизированный smoke-набор для Drill Cloud на **Python + pytest + Playwright**.

Проект проверяет реальный пользовательский маршрут: Keycloak → список буровых → обзор → показатели/live-график → архив → видео → глобальные настройки. Для каждого падения Playwright сохраняет trace, screenshot и video, а pytest формирует читаемый HTML-отчёт.

## Структура

```text
drill-cloud-test/
├── docs/SMOKE_AUTOMATION_MATRIX.md   # соответствие ручному smoke-сценарию
├── scripts/
│   ├── bootstrap.sh                  # установка Python-зависимостей и браузера
│   └── run-smoke.sh                  # стандартный запуск с HTML-отчётом
├── src/drill_cloud_test/
│   ├── config.py                     # единый источник конфигурации окружения
│   ├── diagnostics.py                # console/page/network diagnostics
│   └── pages/                        # Page Objects без тестовой бизнес-логики
├── tests/                             # сценарии, сгруппированные по разделам продукта
├── .env.example
└── pyproject.toml
```

## Быстрый старт

Требуется Python 3.11+ и Bash. В Windows команды можно выполнять через Git Bash.

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
| `E2E_EDGE_ID` | буровая с current/history | рекомендуется; иначе первая карточка |
| `E2E_VIDEO_EDGE_ID` | буровая с рабочей камерой | для VIDEO-01 |
| `E2E_NO_VIDEO_EDGE_ID` | буровая без камер | для VIDEO-03 |
| `E2E_INDICATOR_QUERY` | стабильный поиск показателя | опционально |
| `E2E_HISTORY_TAG_QUERY` | показатель с историей | рекомендуется |
| `E2E_LIVE_TAG` | гарантированно меняющийся тег | для CURRENT-02 |
| `E2E_REQUIRE_HISTORY_DATA` | требовать canvas, не принимать empty state | подготовленный стенд |
| `E2E_REQUIRE_VIDEO_PLAYBACK` | ждать фактическое воспроизведение | подготовленный поток |

Полный шаблон и значения по умолчанию находятся в [.env.example](.env.example).

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

## Запуск против локального UI

1. Запустите backend `cloud` либо настройте `DEV_API_URL` UI на доступный dev backend.
2. В проекте `ui` выполните `npm.cmd run dev`.
3. Укажите `E2E_BASE_URL=http://localhost:5173` и `E2E_API_URL=http://localhost:5173/api`.
4. Убедитесь, что redirect URI `http://localhost:5173/*` разрешён в клиенте Keycloak.
5. Запустите P0.

При тестировании уже развёрнутого стенда укажите его HTTPS URL в обеих переменных; если API находится под тем же origin, добавьте `/api` в `E2E_API_URL`.

## Как добавлять тесты

1. Пользовательские действия раздела добавляются в соответствующий Page Object.
2. В тесте остаются только шаги сценария и бизнес-ожидания.
3. Тест получает маркеры `case`, `p0/p1/p2` и функциональный маркер.
4. Сценарий, который меняет серверное состояние, обязан восстанавливать его через `try/finally`.
5. Для отсутствующих тестовых данных используется `pytest.skip` с точной инструкцией, а не ложный `PASS`.
6. Обновляется [матрица автоматизации](docs/SMOKE_AUTOMATION_MATRIX.md).

## GitHub Actions

Workflow `.github/workflows/smoke.yml` запускается вручную через **Actions → Drill Cloud smoke → Run workflow**. При запуске выбираются стенд, приоритет и браузер.

В repository secrets необходимо создать:

- `E2E_USERNAME`;
- `E2E_PASSWORD`.

ID буровых и тестовые теги задаются через repository variables с теми же именами, что в `.env.example`. После каждого CI-прогона HTML-отчёт, trace, screenshot и video публикуются единым artifact на 14 дней.

## Проверка качества самого тестового проекта

```bash
VENV_PYTHON=.venv/Scripts/python.exe  # Git Bash в Windows
# VENV_PYTHON=.venv/bin/python        # Linux/macOS

"$VENV_PYTHON" -m ruff check .
"$VENV_PYTHON" -m mypy src
"$VENV_PYTHON" -m pytest --collect-only
```

Page Objects используют преимущественно role/label/text-селекторы. CSS-классы применены только там, где у визуальных элементов ECharts и карточек пока нет стабильных `data-testid` или ARIA-имён.
