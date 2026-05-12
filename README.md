# DevOps — лабораторные работы по ML
- Выполнил: Хабибуллин Айсан

## Ссылки

| Артефакт | Ссылка |
|----------|--------|
| GitHub | https://github.com/ajjsan/devopc_lib_4
| Docker Hub (образ API) | https://hub.docker.com/repository/docker/ajjsan/devops_hw_4 |


## Лабораторная работа №4

### Выполненные пункты 

1. **Kafka Producer** — реализован на уровне сервиса модели (контейнер **api**). После успешной записи предсказания в PostgreSQL в топик отправляется JSON с результатом (`prediction_id`, `sentiment`, `label`, `text`, для батча ещё `batch_index`, поле `kind`: `single` / `batch`). Код: `src/kafka_publish.py`, вызовы из `src/api.py`.
2. **Kafka Consumer** — отдельный процесс в контейнере **kafka-consumer** (`python -m src.kafka_consumer`), читает тот же топик и выводит полученные сообщения в stdout. Код: `src/kafka_consumer.py`.
3. **Интеграция с Vault** — адрес брокера и имя топика хранятся в том же KV, что учётные данные БД и API: ключи `KAFKA_BOOTSTRAP_SERVERS`, `KAFKA_TOPIC`. Их записывает **vault-init** (`docker/vault-init/entrypoint.sh`); при старте приложения `src/vault_env.py` подтягивает все перечисленные ключи (включая Kafka) в окружение до чтения `Settings`. Подключение к БД по-прежнему строится из секретов Vault (`POSTGRES_*` и т.д.), без хранения пароля БД в образе.

### Инфраструктура docker-compose (ЛР4)

Дополнительно к сервисам ЛР3 в `docker-compose.yml` добавлены:

| Сервис | Назначение |
|--------|------------|
| **zookeeper** | `confluentinc/cp-zookeeper:7.5.0`, порт 2181. |
| **kafka** | `confluentinc/cp-kafka:7.5.0`, hostname `kafka`; для контейнеров объявлен listener `PLAINTEXT://kafka:9092`; healthcheck `kafka-broker-api-versions`. |
| **kafka-consumer** | тот же образ, что **api** (`devops_hw_4:latest`), `USE_VAULT=true`, чтение параметров Kafka из Vault, подписка на топик. |

Сервис **api** ждёт готовности **kafka** (`condition: service_healthy`), чтобы Producer мог стабильно подключаться к брокеру.

### Зависимости Python

В `requirements-api.txt` добавлен клиент **kafka-python** для Producer и Consumer.

---

## Инструкция: подготовка и запуск

### Предварительные требования

- Установлены **Docker** и **Docker Compose** (v2).
- Файл **`.env`** в корне репозитория
```

Нужны как минимум: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `JWT_SECRET_KEY`, `API_USERNAME`, `API_PASSWORD`; для compose удобно оставить `VAULT_DEV_ROOT_TOKEN_ID`, `VAULT_KV_PATH` как в примере.
- Обученная модель **`experiments/tfidf_log_reg.pkl`** (например, после `python -m dvc repro` или `python src/train.py` по методичке курса).

### Запуск всего стека
Из корня репозитория (PowerShell):

```powershell
cd "C:\Users\ajjsa\OneDrive\Desktop\DevOps\devopc_lib_4"
docker compose up -d --build
```

Проверка статуса:

```powershell
docker compose ps
```
