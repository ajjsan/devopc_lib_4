# DevOps
- Выполнил: Хабибуллин Айсан

## Лабораторная работа №3

В рамках лабораторной работы №3 настроено хранилище секретов **HashiCorp Vault** (контейнер в **docker-compose**), секреты для доступа к БД и к API вынесены в Vault, приложение получает их при старте до установления соединения с PostgreSQL. Для одноразовой записи секретов в Vault используется отдельный сервис **vault-init**, образ которого собирается из `docker/vault-init/Dockerfile` (в образ попадают только скрипты; значения секретов передаются переменными окружения при запуске compose).

## Ссылки

- GitHub (ЛР2): https://github.com/ajjsan/devopc_lib_3
- Docker Hub: https://hub.docker.com/repository/docker/ajjsan/devops_hw_3


**Инфраструктура в Docker Compose.** В `docker-compose.yml` (и зеркально в `docker-compose.jenkins.yml` для CD) добавлены сервисы:
   - **vault** — официальный образ `hashicorp/vault`, режим `server -dev` для лабораторной среды; заданы `VAULT_DEV_ROOT_TOKEN_ID`, прослушивание `0.0.0.0:8200`, healthcheck через `vault status`.
   - **vault-init** — сборка из `docker/vault-init/Dockerfile`; при старте выполняется `docker/vault-init/entrypoint.sh`, который ждёт готовности Vault и выполняет `vault kv put` в движок **KV v2** по пути `secret/<VAULT_KV_PATH>` (по умолчанию `ml-lab`). В Vault записываются: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `JWT_SECRET_KEY`, `API_USERNAME`, `API_PASSWORD`.
   - **db** — PostgreSQL 16, как в предыдущих работах; учётные данные кластера по-прежнему задаются через `.env` для инициализации тома данных.
   - **api** — образ приложения `devops_hw_3:latest` (сборка из корневого `Dockerfile`); включён режим `USE_VAULT=true`, заданы `VAULT_ADDR`, `VAULT_TOKEN`, `VAULT_KV_MOUNT`, `VAULT_KV_PATH`. Зависимости сервиса: готовность Vault, успешное завершение `vault-init`, готовность БД.

**Приложение.** В `requirements-api.txt` добавлена библиотека **hvac**. Модуль `src/vault_env.py` при `USE_VAULT=true` один раз читает секрет из Vault и переносит перечисленные ключи в `os.environ`. Вызов выполняется из `src/settings.py` до первого использования настроек, чтобы строка подключения к БД в `src/database.py` формировалась уже с учётными данными из Vault. Локальный запуск тестов без Vault не меняется: переменная `USE_VAULT` не задаётся.

**Конфигурация и запуск.** Пример переменных окружения, включая параметры Vault, приведён в `.env.example`. Локальный запуск стека: `docker compose up -d --build` из корня репозитория при наличии `.env` и артефакта модели `experiments/tfidf_log_reg.pkl`.


