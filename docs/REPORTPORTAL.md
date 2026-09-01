# ReportPortal для Drill Cloud E2E

В репозитории подготовлены:

- Portainer stack `deploy/reportportal/docker-compose.yml` на основе официального ReportPortal `26.0.5`;
- подключение входного gateway к существующей external network `proxy`;
- постоянные Docker volumes для PostgreSQL, файлов, OpenSearch и Analyzer;
- нативная отправка pytest-результатов, логов и вложений из `.github/workflows/e2e.yml`.

ReportPortal состоит из нескольких сервисов. Отдельный `Dockerfile` здесь не нужен: stack использует зафиксированные официальные образы ReportPortal, PostgreSQL, RabbitMQ, OpenSearch и Traefik. Локальные `build`-контексты из upstream compose удалены, потому что исходников этих сервисов в `drill-cloud-test` нет.

## 1. Подготовить сервер

Для установки нужен Linux-сервер с Docker Compose 2.2 или новее. Официальный абсолютный минимум — 2 CPU, 6 GB RAM и 20 GB свободного места; для постоянно используемого небольшого стенда разумнее иметь не менее 4 CPU, 8 GB RAM и SSD с запасом от 40 GB. На сервере с меньшим объёмом памяти ReportPortal и OpenSearch могут завершаться по OOM.

Проверьте ресурсы и Docker:

```bash
docker version
docker compose version
free -h
df -h
```

OpenSearch требует `vm.max_map_count` не меньше `262144`:

```bash
echo 'vm.max_map_count=262144' | sudo tee /etc/sysctl.d/99-opensearch.conf
sudo sysctl --system
cat /proc/sys/vm/max_map_count
```

Убедитесь, что общая сеть Nginx Proxy Manager уже существует:

```bash
docker network inspect proxy
```

Если сеть отсутствует, создайте её один раз:

```bash
docker network create proxy
```

## 2. Подготовить DNS

Создайте `A`-запись, например:

```text
reportportal.drillcloud.ru -> публичный IP Timeweb-сервера
```

Дождитесь, пока имя начнёт разрешаться на сервер. Порт `8080` во внешний интернет открывать не нужно: Nginx Proxy Manager обращается к gateway по Docker-сети `proxy`.

## 3. Создать stack в Portainer

1. Запушьте изменения `drill-cloud-test` в нужную ветку.
2. Откройте `Portainer → Stacks → Add stack`.
3. Выберите `Repository`.
4. Укажите репозиторий `drill-cloud-test`, нужный reference ветки и Compose path:

```text
deploy/reportportal/docker-compose.yml
```

5. В разделе Environment variables создайте:

| Variable | Значение |
|---|---|
| `POSTGRES_USER` | `rpuser` |
| `POSTGRES_PASSWORD` | новый случайный пароль не короче 24 символов |
| `POSTGRES_DB` | `reportportal` |
| `RABBITMQ_DEFAULT_USER` | `reportportal` |
| `RABBITMQ_DEFAULT_PASS` | другой случайный пароль не короче 24 символов |
| `RP_INITIAL_ADMIN_PASSWORD` | отдельный сильный пароль администратора ReportPortal |

Не добавляйте эти значения в Git. Сохраните их в менеджере паролей. После первого запуска не меняйте PostgreSQL и RabbitMQ credentials только в Portainer: существующие volumes сохраняют старые учётные данные, и сервисы перестанут подключаться.

6. Нажмите `Deploy the stack`.
7. Дождитесь загрузки образов и инициализации. Первый запуск обычно занимает несколько минут.

Нормальное итоговое состояние:

- `gateway`, `postgres`, `rabbitmq`, `opensearch`, `index`, `ui`, `api`, `uat`, `jobs`, `analyzer` — running/healthy;
- `migrations` и `analyzer-storage-init` — завершены с кодом `0`.

Если `opensearch` перезапускается, сначала проверьте `vm.max_map_count`, память сервера и его logs. Если `api` или `uat` не поднимаются, проверьте, что `migrations` завершился успешно и PostgreSQL/RabbitMQ healthy.

## 4. Настроить Nginx Proxy Manager

Создайте новый `Proxy Host`:

| Поле | Значение |
|---|---|
| Domain Names | `reportportal.drillcloud.ru` |
| Scheme | `http` |
| Forward Hostname / IP | `container-reportportal-gateway` |
| Forward Port | `8080` |
| Cache Assets | выключено |
| Block Common Exploits | включено |
| Websockets Support | включено |

Во вкладке `Advanced` добавьте:

```nginx
client_max_body_size 100m;
proxy_read_timeout 600s;
proxy_send_timeout 600s;
```

Во вкладке `SSL`:

1. запросите новый Let's Encrypt certificate;
2. включите `Force SSL`;
3. включите `HTTP/2 Support`;
4. после проверки можно включить HSTS.

Не ставьте перед ReportPortal NPM Basic Auth: GitHub runner не сможет отправлять результаты без дополнительной прокси-аутентификации. Доступ к API уже защищён API key ReportPortal. Если используется IP allowlist, в неё потребуется добавить меняющиеся диапазоны GitHub-hosted runners либо перейти на self-hosted runner.

Откройте `https://reportportal.drillcloud.ru`. Для первого входа используйте пользователя `superadmin` и значение `RP_INITIAL_ADMIN_PASSWORD` из Portainer.

## 5. Создать проект и ключ для GitHub Actions

1. Войдите как `superadmin`.
2. Создайте проект, например `drill_cloud`.
3. Создайте отдельного пользователя для автоматизации или назначьте существующего технического пользователя в проект. Не используйте API key `superadmin` в CI.
4. Войдите под техническим пользователем.
5. Откройте профиль пользователя, раздел `API Keys`, и сгенерируйте ключ.
6. Скопируйте ключ сразу и сохраните в менеджере паролей.

Для трёх контуров можно использовать один проект `drill_cloud`: workflow добавляет каждому запуску атрибуты `environment:dev|alpha|main`, `browser:*` и `profile:*`. Если нужна строгая изоляция, создайте три проекта и задайте разное значение `REPORTPORTAL_PROJECT` в каждом GitHub Environment.

## 6. Настроить GitHub Environments

В `drill-cloud-test → Settings → Environments` откройте по очереди `dev`, `alpha`, `main`.

В каждом Environment создайте Variables:

```text
REPORTPORTAL_ENABLED=true
REPORTPORTAL_ENDPOINT=https://reportportal.drillcloud.ru
REPORTPORTAL_PROJECT=drill_cloud
```

И Secret:

```text
REPORTPORTAL_API_KEY=<API key технического пользователя>
```

Можно вместо трёх одинаковых secrets создать organization/repository secret с доступом к `drill-cloud-test`. Environment secret с тем же именем имеет приоритет.

`REPORTPORTAL_ENDPOINT` указывается без `/api` и без завершающего `/`.

## 7. Проверить полный цикл

1. Откройте `drill-cloud-test → Actions → Environment E2E`.
2. Нажмите `Run workflow`.
3. Для первой проверки выберите `dev`, `p0`, `chromium`.
4. Дождитесь завершения job.
5. Откройте ReportPortal, проект `drill_cloud`, раздел Launches.

Должен появиться Launch вида:

```text
Drill Cloud dev / p0 / chromium / GitHub #<номер>
```

Ссылка на GitHub Actions хранится в description запуска. У упавших UI-тестов в ReportPortal должны быть `browser-diagnostics.txt` и `failure.png`. Независимо от ReportPortal GitHub Actions продолжает сохранять HTML, JUnit, Playwright trace, video и screenshots как artifact на 30 дней.

Workflow запускается только вручную через `workflow_dispatch` и не является обязательным status check, поэтому не блокирует merge request. Если `REPORTPORTAL_ENABLED` не равен `true` или не заполнена одна из трёх настроек, тесты выполнятся без публикации и покажут warning.

## 8. Локальная проверка публикации

PowerShell:

```powershell
$env:RP_API_KEY = '<API key>'
python -m pytest -m p0 --reportportal `
  -o 'rp_endpoint=https://reportportal.drillcloud.ru' `
  -o 'rp_project=drill_cloud' `
  -o 'rp_launch=Local Drill Cloud P0'
```

Не сохраняйте `RP_API_KEY` в `.env`, если файл может попасть в Git.

## 9. Данные, backup и обновление

Данные переживают обычный redeploy stack благодаря фиксированным volumes:

```text
drillcloud_reportportal_postgres_data
reportportal_storage
reportportal_opensearch
reportportal_analyzer_storage
```

Не используйте `Remove volumes` при удалении или пересоздании stack. Перед обновлением ReportPortal сделайте как минимум backup PostgreSQL и `reportportal_storage`; для полного восстановления сохраните все четыре volumes. Образы в compose зафиксированы версиями — не заменяйте их на `latest`. Обновление выполняйте отдельным изменением compose после чтения release/migration notes и сначала проверяйте восстановление backup.

## Официальные материалы

- [ReportPortal: Deploy with Docker](https://github.com/reportportal/docs/blob/develop/versioned_docs/version-26.0.5/installation-steps/DeployWithDocker.md)
- [ReportPortal 26.0.5 docker-compose](https://github.com/reportportal/reportportal/blob/26.0.5/docker-compose.yml)
- [pytest-reportportal](https://github.com/reportportal/agent-python-pytest)
- [OpenSearch Docker host settings](https://docs.opensearch.org/latest/install-and-configure/install-opensearch/docker/)
