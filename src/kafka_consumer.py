"""ЛР4: Kafka Consumer — приём сообщений с результатом работы модели (отдельный процесс/контейнер)."""

from __future__ import annotations

import json
import logging
import sys

from kafka import KafkaConsumer
from kafka.errors import KafkaError

from .settings import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


def main() -> None:
    settings = get_settings()
    bootstrap = (settings.kafka_bootstrap_servers or "").strip()
    topic = (settings.kafka_topic or "").strip()
    if not bootstrap or not topic:
        log.error("Задай KAFKA_BOOTSTRAP_SERVERS и KAFKA_TOPIC (например из Vault при USE_VAULT=true)")
        sys.exit(1)
    servers = [h.strip() for h in bootstrap.split(",") if h.strip()]
    log.info("Consumer: bootstrap=%s topic=%s", servers, topic)
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=servers,
            group_id="sentiment-prediction-consumer",
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda b: json.loads(b.decode("utf-8")),
        )
    except KafkaError as exc:
        log.error("Не удалось подключиться к Kafka: %s", exc)
        sys.exit(1)

    log.info("Ожидание сообщений…")
    try:
        for msg in consumer:
            log.info(
                "Получено: partition=%s offset=%s payload=%s",
                msg.partition,
                msg.offset,
                msg.value,
            )
    except KeyboardInterrupt:
        log.info("Останов по Ctrl+C")
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
