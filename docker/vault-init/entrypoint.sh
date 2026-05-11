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
vault kv put "secret/${PATH_KV}" \
  POSTGRES_USER="${POSTGRES_USER:?}" \
  POSTGRES_PASSWORD="${POSTGRES_PASSWORD:?}" \
  POSTGRES_DB="${POSTGRES_DB:?}" \
  JWT_SECRET_KEY="${JWT_SECRET_KEY:?}" \
  API_USERNAME="${API_USERNAME:?}" \
  API_PASSWORD="${API_PASSWORD:?}" \
  KAFKA_BOOTSTRAP_SERVERS="${KAFKA_BOOTSTRAP_SERVERS:?}" \
  KAFKA_TOPIC="${KAFKA_TOPIC:?}"

echo "Готово: секреты записаны в Vault"
