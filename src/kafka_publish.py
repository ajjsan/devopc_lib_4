"""ЛР4: Kafka Producer — публикация результата инференса (после записи в БД)."""

from __future__ import annotations

import json
import logging
from functools import lru_cache
from typing import Any

from kafka import KafkaProducer
from kafka.errors import KafkaError

from .settings import get_settings

log = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _producer() -> KafkaProducer | None:
    settings = get_settings()
    bootstrap = (settings.kafka_bootstrap_servers or "").strip()
    if not bootstrap:
        return None
    servers = [h.strip() for h in bootstrap.split(",") if h.strip()]
    if not servers:
        return None
    return KafkaProducer(
        bootstrap_servers=servers,
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
        acks=1,
        request_timeout_ms=15000,
    )


def publish_prediction_result(payload: dict[str, Any]) -> None:
    """Отправляет JSON-сообщение в топик; при отсутствии настроек Kafka или ошибке не ломает API."""
    settings = get_settings()
    topic = (settings.kafka_topic or "").strip()
    producer = _producer()
    if producer is None or not topic:
        return
    try:
        producer.send(topic, payload)
        producer.flush(timeout=8)
    except KafkaError as exc:
        log.warning("Kafka: не удалось отправить сообщение: %s", exc)
    except Exception as exc:  # noqa: BLE001 — не роняем предсказание из-за брокера
        log.warning("Kafka: ошибка публикации: %s", exc)
