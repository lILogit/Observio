import json, os, collections
from statistics import mean
from confluent_kafka import Consumer, Producer

BROKERS = os.getenv("BROKERS","broker:9092")
WINDOW = int(os.getenv("WINDOW","12"))

def key(ev):
    return f"{ev['tenant_id']}|{ev['tags'].get('host','')}|{ev['attributes']['metric']}"

def main():
    c = Consumer({'bootstrap.servers':BROKERS,'group.id':'features','auto.offset.reset':'earliest'})
    p = Producer({'bootstrap.servers':BROKERS})
    c.subscribe(['signals.metric.v1'])
    windows = collections.defaultdict(lambda: collections.deque(maxlen=WINDOW))
    print("[feature-rules] consuming from signals.metric.v1")
    while True:
        m = c.poll(1.0)
        if not m:
            continue
        try:
            ev = json.loads(m.value())
            k = key(ev)
            windows[k].append(float(ev["attributes"]["value"]))
            if len(windows[k]) >= WINDOW:
                avg = mean(windows[k])
                if ev["attributes"]["metric"] == "cpu_load" and avg > 80:
                    alert = {
                        "alert_id": f"cpu-high:{k}",
                        "tenant_id": ev["tenant_id"],
                        "severity": "warning",
                        "reason": f"CPU avg {avg:.1f}% over last window",
                        "source": ev["source"], "tags": ev["tags"],
                        "ts_event": ev["ts_event"]
                    }
                    p.produce('ops.alert.v1', json.dumps(alert).encode('utf-8'))
        except Exception as e:
            print("[feature-rules] error:", e)

if __name__ == "__main__":
    main()
