import json, os
from confluent_kafka import Consumer, Producer

BROKERS = os.getenv("BROKERS","broker:9092")

# Minimal CMDB
CMDB = {"host-a":{"owner":"team-core","tier":"gold"},
        "host-b":{"owner":"team-ml","tier":"silver"}}

def main():
    c = Consumer({'bootstrap.servers':BROKERS,'group.id':'enricher','auto.offset.reset':'earliest'})
    p = Producer({'bootstrap.servers':BROKERS})
    c.subscribe(['signals.metric.v1'])
    print("[enricher] consuming from signals.metric.v1")
    while True:
        m = c.poll(1.0)
        if not m:
            continue
        try:
            ev = json.loads(m.value())
            h = ev.get("tags",{}).get("host","unknown")
            ev.setdefault("tags",{}).update(CMDB.get(h, {}))
            # MVP: re-emit to same topic (could use signals.enriched.v1 later)
            p.produce('signals.metric.v1', json.dumps(ev).encode('utf-8'))
        except Exception as e:
            print("[enricher] error:", e)

if __name__ == "__main__":
    main()
