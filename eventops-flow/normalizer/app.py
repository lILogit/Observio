import json, os, uuid
from datetime import datetime, timezone
from confluent_kafka import Consumer, Producer

BROKERS = os.getenv("BROKERS","broker:9092")

def main():
    c = Consumer({'bootstrap.servers':BROKERS,'group.id':'normalizer','auto.offset.reset':'earliest'})
    p = Producer({'bootstrap.servers':BROKERS})
    c.subscribe(['ingest.raw.agent'])
    print("[normalizer] consuming from ingest.raw.agent")
    while True:
        msg = c.poll(1.0)
        if not msg:
            continue
        try:
            raw = json.loads(msg.value())
            out = {
                "event_id": str(uuid.uuid4()),
                "ts_event": raw.get("ts_event") or datetime.now(timezone.utc).isoformat(),
                "ts_ingest": datetime.now(timezone.utc).isoformat(),
                "tenant_id": raw.get("tenant_id","default"),
                "source": {"type": raw.get("source","agent"), "source_id": raw.get("host","unknown")},
                "schema_name": "signals.metric", "schema_version": 1,
                "attributes": {
                    "metric": raw["metric"],
                    "unit": raw.get("unit",""),
                    "value": str(float(raw["value"])),
                },
                "tags": {"host": raw.get("host","unknown"), **raw.get("tags",{})}
            }
            p.produce('signals.metric.v1', json.dumps(out).encode('utf-8'))
        except Exception as e:
            print("[normalizer] error:", e)

if __name__ == "__main__":
    main()
