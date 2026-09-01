# GitHub Environments для E2E

Workflow `.github/workflows/e2e.yml` использует три GitHub Environment: `dev`, `alpha` и `main`.
Environment, профиль и браузер выбираются вручную через `Actions → Environment E2E → Run workflow`.

## Обязательные variables

Создайте одинаковый набор имён в каждом Environment.

| Variable | `dev` | `alpha` | `main` |
|---|---|---|---|
| `E2E_BASE_URL` | `https://dev.drillcloud.ru` | `https://alpha.drillcloud.ru` | `https://beta.drillcloud.ru` |
| `E2E_API_URL` | `https://dev.drillcloud.ru/api` | `https://alpha.drillcloud.ru/api` | `https://beta.drillcloud.ru/api` |
| `E2E_AUTH_MODE` | `required` | `required` | `required` |
| `E2E_SEED_ENABLED` | `false` | `false` | `false` |
| `E2E_PUBLISH_LIVE` | `false` | `false` | `false` |
| `E2E_REQUIRE_HISTORY_DATA` | `false` | `false` | `false` |
| `E2E_REQUIRE_VIDEO_PLAYBACK` | `false` | `false` | `false` |
| `E2E_VISUAL_ENABLED` | `false` | `false` | `false` |
| `E2E_LIVE_WAIT_SECONDS` | `30` | `30` | `30` |
| `E2E_SSE_OBSERVE_SECONDS` | `8` | `8` | `8` |
| `E2E_MAX_CURRENT_REQUESTS` | `12` | `12` | `12` |
| `REPORTPORTAL_ENABLED` | `true` | `true` | `true` |
| `REPORTPORTAL_ENDPOINT` | `https://reportportal.drillcloud.ru` | `https://reportportal.drillcloud.ru` | `https://reportportal.drillcloud.ru` |
| `REPORTPORTAL_PROJECT` | `drill_cloud` | `drill_cloud` | `drill_cloud` |

Начальная конфигурация намеренно не включает seed и live publisher. Она безопасна для всех стендов и запускает P0 по первой буровой, доступной основной тестовой учётной записи.

## Обязательные secrets

| Secret | Значение |
|---|---|
| `E2E_USERNAME` | логин отдельного пользователя Keycloak для автоматических тестов |
| `E2E_PASSWORD` | пароль этого пользователя |
| `REPORTPORTAL_API_KEY` | API key отдельного технического пользователя ReportPortal |

Основному пользователю назначьте `drill-admin` либо все необходимые роли `drill-edge-<edge-id>`. Не используйте личную или `kc_admin` учётную запись.

Если один Keycloak realm обслуживает все три стенда, допустимо сохранить одинаковую пару в каждом Environment. Раздельное хранение всё равно полезно: пароль можно заменить на одном контуре без изменения workflow.

Развёртывание ReportPortal, создание проекта и получение API key описаны в [REPORTPORTAL.md](REPORTPORTAL.md). Чтобы временно отключить публикацию для одного контура без изменения workflow, задайте в нём `REPORTPORTAL_ENABLED=false`.

## Secrets для расширенной проверки ролей

Создайте после подготовки трёх отдельных пользователей Keycloak:

| Secret | Пользователь и роль |
|---|---|
| `E2E_ADMIN_USERNAME` | отдельный пользователь с ролью `drill-admin` |
| `E2E_ADMIN_PASSWORD` | его пароль |
| `E2E_EDGE_USERNAME` | пользователь с одной ролью `drill-edge-<E2E_EDGE_ID>` |
| `E2E_EDGE_PASSWORD` | его пароль |
| `E2E_NO_ROLE_USERNAME` | пользователь без `drill-admin` и `drill-edge-*` |
| `E2E_NO_ROLE_PASSWORD` | его пароль |

Пароли генерируются в менеджере паролей, не записываются в этот документ и не добавляются в repository variables.

## Variables для подготовленных данных

Эти variables добавляются только после проверки данных конкретного стенда. Если их не создать, зависимые сценарии будут пропущены с объяснением.

| Variable | Рекомендуемое значение для управляемых данных | Назначение |
|---|---|---|
| `E2E_EDGE_ID` | `e2e-main` | current и history |
| `E2E_FORBIDDEN_EDGE_ID` | `e2e-no-video` | буровая, недоступная edge-пользователю |
| `E2E_VIDEO_EDGE_ID` | `e2e-video` | буровая с камерой |
| `E2E_NO_VIDEO_EDGE_ID` | `e2e-no-video` | буровая без камеры |
| `E2E_INDICATOR_QUERY` | `e2e-pressure` | стабильный поиск показателя |
| `E2E_HISTORY_TAG_QUERY` | `e2e-pressure` | показатель с историей |
| `E2E_LIVE_TAG` | `e2e-live` | изменяемый live-показатель |
| `E2E_VIDEO_WS_URL` | URL тестового `ws://` или `wss://` потока | источник тестовой камеры |

Для `main` не включайте `E2E_SEED_ENABLED` и `E2E_PUBLISH_LIVE`: workflow дополнительно блокирует эти операции.

## Secrets для seed и live publisher

Добавляются только в `dev` или `alpha`:

| Secret | Значение |
|---|---|
| `E2E_DATABASE_URL` | отдельная строка подключения к БД выбранного стенда |
| `E2E_INGEST_API_KEY` | значение `INGEST_API_KEY` backend выбранного стенда; не создавайте, если ingest не защищён |

GitHub-hosted runner должен иметь сетевой доступ к PostgreSQL. Не открывайте БД в интернет ради тестов: при закрытой БД используйте self-hosted runner либо один раз подготовьте `e2e-*` данные из внутренней сети и оставьте seed выключенным.

## Настройки, не блокирующие merge

- не добавляйте `Environment E2E / e2e` в обязательные status checks branch protection;
- required reviewers и wait timer для этих Environment не нужны;
- workflow не подписан на `push`, `pull_request`, расписание или внешний dispatch;
- результат ручного запуска виден в Actions, но не блокирует merge и deployment.

## Ручной запуск

После завершения redeploy в Portainer откройте `Actions → Environment E2E → Run workflow` и выберите параметры:

```text
dev:   environment=dev,   profile=p0, browser=chromium
alpha: environment=alpha, profile=p1, browser=chromium
main:  environment=main,  profile=p0, browser=chromium
```

Отдельный `E2E_REPOSITORY_TOKEN` для этой схемы не требуется.
