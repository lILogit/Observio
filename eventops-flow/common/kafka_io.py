import json, os
from typing import Callable, Iterable
from confluent_kafka import Producer, Consumer, KafkaException

BROKERS = os.getenv("BROKERS", "broker:9092")

def make_producer():
    return Producer({"bootstrap.servers": BROKERS, "linger.ms": 10})

def make_consumer(group_id: str, topics: Iterable[str]):
    c = Consumer({
        "bootstrap.servers": BROKERS,
        "group.id": group_id,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
    })
    c.subscribe(list(topics))
    return c

def stream_forever(consumer: Consumer, handler: Callable[[dict], None]):
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            handler(json.loads(msg.value().decode("utf-8")))
    finally:
        consumer.close()

def send_json(producer: Producer, topic: str, payload: dict, key: str | None = None):
    producer.produce(topic, json.dumps(payload).encode("utf-8"), key=key)
    producer.poll(0)
