#!/bin/sh
set -eu

VAULT_ADDR="${VAULT_ADDR:-http://vault:8200}"
export VAULT_ADDR
export VAULT_TOKEN="${VAULT_DEV_ROOT_TOKEN_ID:?Задай VAULT_DEV_ROOT_TOKEN_ID}"

PATH_KV="${VAULT_KV_PATH:-ml-lab}"

echo "Ожидание Vault: ${VAULT_ADDR}"
i=0
while ! vault status -address="${VAULT_ADDR}" >/dev/null 2>&1; do
  i=$((i + 1))
  if [ "$i" -gt 90 ]; then
    echo "Vault не поднялся за отведённое время"
    exit 1
  fi
  sleep 1
done

echo "Запись секретов в KV v2: secret/${PATH_KV}"

: "${POSTGRES_USER:?Задай POSTGRES_USER в .env}"
: "${POSTGRES_PASSWORD:?Задай POSTGRES_PASSWORD в .env}"
: "${POSTGRES_DB:?Задай POSTGRES_DB в .env}"
: "${JWT_SECRET_KEY:?Задай JWT_SECRET_KEY в .env}"
: "${API_USERNAME:?Задай API_USERNAME в .env}"
: "${API_PASSWORD:?Задай API_PASSWORD в .env}"
: "${KAFKA_BOOTSTRAP_SERVERS:?Задай KAFKA_BOOTSTRAP_SERVERS (или defaults в docker-compose для vault-init)}"
: "${KAFKA_TOPIC:?Задай KAFKA_TOPIC (или defaults в docker-compose для vault-init)}"

set +e
out="$(
  vault kv put "secret/${PATH_KV}" \
    POSTGRES_USER="${POSTGRES_USER}" \
    POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
    POSTGRES_DB="${POSTGRES_DB}" \
    JWT_SECRET_KEY="${JWT_SECRET_KEY}" \
    API_USERNAME="${API_USERNAME}" \
    API_PASSWORD="${API_PASSWORD}" \
    KAFKA_BOOTSTRAP_SERVERS="${KAFKA_BOOTSTRAP_SERVERS}" \
    KAFKA_TOPIC="${KAFKA_TOPIC}" 2>&1
)"
rc=$?
set -e
if [ "$rc" -ne 0 ]; then
  echo "$out"
  echo "vault kv put завершился с кодом $rc. Проверь токен (VAULT_DEV_ROOT_TOKEN_ID), KV secret и логи Vault."
  vault status -address="${VAULT_ADDR}" || true
  exit "$rc"
fi

echo "Готово: секреты записаны в Vault"
