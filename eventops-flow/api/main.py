from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from confluent_kafka import Consumer
import duckdb, os, asyncio

app = FastAPI(title="EventOps Flow API")
DUCK = os.getenv("DUCKDB_PATH", "/data/metrics.duckdb")
BROKERS = os.getenv("BROKERS","broker:9092")

con = duckdb.connect(DUCK, read_only=False)
con.execute("""CREATE TABLE IF NOT EXISTS metrics (
  tenant_id TEXT,
  metric TEXT,
  host TEXT,
  ts_event TIMESTAMP,
  value DOUBLE,
  tags JSON
);
""")

@app.get("/healthz")
def healthz():
    try:
        con.execute("SELECT 1").fetchone()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "err": str(e)}

@app.get("/metrics/cpu")
def cpu(tenant: str = "default", host: str | None = None, minutes: int = 10):
    q = f"""      SELECT ts_event, value
      FROM metrics
      WHERE tenant_id = ? AND metric = 'cpu_load'
      { "AND host = ?" if host else "" }
        AND ts_event >= now() - INTERVAL {minutes} MINUTE
      ORDER BY ts_event
    """
    params = [tenant] + ([host] if host else [])
    rows = con.execute(q, params).fetchall()
    return [{"t": str(t), "v": v} for (t, v) in rows]

@app.get("/alerts/stream")
def alerts_stream():
    c = Consumer({'bootstrap.servers': BROKERS,
                  'group.id':'api-sse','auto.offset.reset':'latest'})
    c.subscribe(['ops.alert.v1'])
    async def gen():
        while True:
            msg = c.poll(1.0)
            if msg:
                yield f"data: {msg.value().decode()}\n\n"
            await asyncio.sleep(0.1)
    return StreamingResponse(gen(), media_type="text/event-stream")
