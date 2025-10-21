import os, copy
from common.kafka_io import make_consumer, make_producer, stream_forever, send_json

IN_TOPIC  = os.getenv("IN_TOPIC", "signals.metric.v1")
OUT_TOPIC = os.getenv("OUT_TOPIC", "signals.metric.v1")

CMDB = {
    "host-a": {"env":"prod", "team":"core"},
    "host-b": {"env":"dev", "team":"mlops"},
}

def handler(env):
    enriched = copy.deepcopy(env)
    src = env.get("source", {}).get("source_id", "")
    cmdb_tags = CMDB.get(src, {})
    enriched["tags"] = {**cmdb_tags, **(env.get("tags") or {})}
    send_json(producer, OUT_TOPIC, enriched, key=enriched["tenant_id"])

producer = make_producer()
consumer = make_consumer("enricher", [IN_TOPIC])

if __name__ == "__main__":
    stream_forever(consumer, handler)
