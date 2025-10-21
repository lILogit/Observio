import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import duckdb
from common.kafka_io import make_consumer

DUCKDB_PATH = os.getenv("DUCKDB_PATH", "/data/metrics.duckdb")
ALERTS_TOPIC = os.getenv("ALERTS_TOPIC", "ops.alert.v1")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8088"))

app = FastAPI(title="EventOps API")

def q(sql: str, params=()):
    con = duckdb.connect(DUCKDB_PATH, read_only=True)
    res = con.execute(sql, params).fetchall()
    cols = [d[0] for d in con.description]
    con.close()
    return [dict(zip(cols, r)) for r in res]

@app.get("/metrics/cpu")
def cpu_metrics(tenant: str, host: str):
    rows = q("""
        SELECT ts, value, unit, tags
        FROM metrics
        WHERE tenant=? AND source_id=? AND metric='cpu_load'
        ORDER BY ts DESC LIMIT 1000
    """, (tenant, host))
    return rows

@app.get("/metrics/latest")
def latest(tenant: str, metric: str):
    rows = q("""
        SELECT ts, tenant, source_id, metric, value, unit, tags
        FROM metrics
        WHERE tenant=? AND metric=?
        ORDER BY ts DESC LIMIT 50
    """, (tenant, metric))
    return rows

@app.get("/alerts/stream")
def alerts_stream():
    consumer = make_consumer("api-sse", [ALERTS_TOPIC])
    def gen():
        try:
            while True:
                msg = consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    continue
                payload = msg.value().decode("utf-8")
                yield f"data: {payload}\n\n"
        finally:
            consumer.close()
    return StreamingResponse(gen(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
