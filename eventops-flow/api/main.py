# api/main.py
import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import psycopg2
from psycopg2.extras import RealDictCursor
from common.kafka_io import make_consumer

PG = dict(
    dbname=os.getenv("PG_DB","eventops"),
    user=os.getenv("PG_USER","eventops"),
    password=os.getenv("PG_PASS","secret"),
    host=os.getenv("PG_HOST","postgres"),
    port=int(os.getenv("PG_PORT","5432")),
)
ALERTS_TOPIC = os.getenv("ALERTS_TOPIC", "ops.alert.v1")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8088"))

app = FastAPI(title="EventOps API (Postgres)")

def q(sql: str, params=()):
    con = psycopg2.connect(**PG)
    cur = con.cursor(cursor_factory=RealDictCursor)
    cur.execute(sql, params)
    rows = cur.fetchall()
    con.close()
    return rows

@app.get("/metrics/cpu")
def cpu_metrics(tenant: str, host: str):
    return q("""
        SELECT ts, value, unit, tags
        FROM metrics
        WHERE tenant=%s AND source_id=%s AND metric='cpu_load'
        ORDER BY ts DESC
        LIMIT 1000
    """, (tenant, host))

@app.get("/metrics/latest")
def latest(tenant: str, metric: str):
    return q("""
        SELECT ts, tenant, source_id, metric, value, unit, tags
        FROM metrics
        WHERE tenant=%s AND metric=%s
        ORDER BY ts DESC
        LIMIT 50
    """, (tenant, metric))

@app.get("/alerts/stream")
def alerts_stream():
    consumer = make_consumer("api-sse", [ALERTS_TOPIC])
    def gen():
        try:
            while True:
                msg = consumer.poll(1.0)
                if msg and not msg.error():
                    yield f"data: {msg.value().decode('utf-8')}\\n\\n"
        finally:
            consumer.close()
    return StreamingResponse(gen(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)

