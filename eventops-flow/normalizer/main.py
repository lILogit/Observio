import os, uuid, datetime as dt
from common.kafka_io import make_consumer, make_producer, stream_forever, send_json

IN_TOPIC  = os.getenv("IN_TOPIC", "ingest.raw.agent")
OUT_TOPIC = os.getenv("OUT_TOPIC", "signals.metric.v1")

def normalize(raw: dict) -> dict:
    now = dt.datetime.utcnow().isoformat() + "Z"
    tenant = raw.get("tenant_id", "default")
    source_id = raw.get("host") or raw.get("source_id", "unknown")
    metric = raw.get("metric", "unknown")
    value = float(raw.get("value", 0))
    unit = raw.get("unit", "")
    tags = raw.get("tags", {})
    return {
        "event_id": str(uuid.uuid4()),
        "ts_event": raw.get("ts_event", now),
        "ts_ingest": now,
        "tenant_id": tenant,
        "source": {"type":"host","source_id": source_id},
        "schema_name":"signals.metric",
        "schema_version":1,
        "attributes":{
            "metric": metric,
            "value": str(value),
            "unit": unit
        },
        "tags": tags
    }

def handler(msg: dict):
    norm = normalize(msg)
    send_json(producer, OUT_TOPIC, norm, key=norm["tenant_id"])

producer = make_producer()
consumer = make_consumer("normalizer", [IN_TOPIC])

if __name__ == "__main__":
    stream_forever(consumer, handler)
