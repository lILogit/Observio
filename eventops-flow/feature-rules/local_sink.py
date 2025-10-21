import os, json, pathlib
import duckdb
from confluent_kafka import Consumer

DATA_DIR = os.getenv("DATA_DIR", "/data")
DUCK = os.getenv("DUCKDB_PATH", f"{DATA_DIR}/metrics.duckdb")

pathlib.Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
con = duckdb.connect(DUCK)
con.execute("""CREATE TABLE IF NOT EXISTS metrics (
  tenant_id TEXT,
  metric TEXT,
  host TEXT,
  ts_event TIMESTAMP,
  value DOUBLE,
  tags JSON
);
""")

c = Consumer({'bootstrap.servers': os.getenv("BROKERS","broker:9092"),
              'group.id':'local-sink','auto.offset.reset':'earliest'})
c.subscribe(['signals.metric.v1'])

def as_row(rec: dict):
    attrs, tags = rec["attributes"], rec.get("tags", {})
    ts = rec["ts_event"].replace('Z','')
    return [
        rec.get("tenant_id","default"),
        attrs["metric"],
        tags.get("host","unknown"),
        ts,
        float(attrs["value"]),
        json.dumps(tags)
    ]

print("[local-sink] writing to", DUCK)
while True:
    m = c.poll(1.0)
    if not m:
        continue
    try:
        rec = json.loads(m.value())
        row = as_row(rec)
        con.execute("INSERT INTO metrics VALUES (?, ?, ?, ?, ?, ?)", row)
    except Exception as e:
        print("[local-sink] error:", e)
