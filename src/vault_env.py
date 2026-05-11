"""Загрузка секретов из HashiCorp Vault в os.environ до чтения настроек (ЛР3)."""

from __future__ import annotations

import os


def apply_vault_secrets_to_environ() -> None:
    """Если USE_VAULT=true, один раз подтягивает KV v2 и выставляет переменные для Settings."""
    raw = os.getenv("USE_VAULT", "").strip().lower()
    if raw not in ("1", "true", "yes", "on"):
        return
    if os.environ.get("_VAULT_SECRETS_LOADED") == "1":
        return

    import hvac

    url = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200").rstrip("/")
    token = os.getenv("VAULT_TOKEN")
    if not token:
        msg = "USE_VAULT=true, но не задан VAULT_TOKEN"
        raise RuntimeError(msg)

    mount_point = os.getenv("VAULT_KV_MOUNT", "secret")
    path = os.getenv("VAULT_KV_PATH", "ml-lab")

    client = hvac.Client(url=url, token=token)
    if not client.is_authenticated():
        msg = "Vault: токен не принят (проверь VAULT_ADDR и VAULT_TOKEN)"
        raise RuntimeError(msg)

    resp = client.secrets.kv.v2.read_secret_version(path=path, mount_point=mount_point)
    data = resp["data"]["data"]

    keys = (
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
        "JWT_SECRET_KEY",
        "API_USERNAME",
        "API_PASSWORD",
        "KAFKA_BOOTSTRAP_SERVERS",
        "KAFKA_TOPIC",
    )
    for key in keys:
        if key not in data or data[key] is None:
            msg = f"В Vault по пути {mount_point}/{path} нет ключа {key}"
            raise KeyError(msg)
        os.environ[key] = str(data[key])

    os.environ["_VAULT_SECRETS_LOADED"] = "1"
