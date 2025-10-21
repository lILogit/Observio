# common/db_postgres.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor

DB = dict(
    dbname=os.getenv("PG_DB", "eventops"),
    user=os.getenv("PG_USER", "eventops"),
    password=os.getenv("PG_PASS", "secret"),
    host=os.getenv("PG_HOST", "postgres"),
    port=int(os.getenv("PG_PORT", "5432")),
)

def get_conn(autocommit=False):
    con = psycopg2.connect(**DB)
    con.autocommit = autocommit
    return con

def init_schema():
    con = get_conn()
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS metrics (
      id SERIAL PRIMARY KEY,
      ts TIMESTAMPTZ,
      tenant TEXT,
      source_id TEXT,
      metric TEXT,
      value DOUBLE PRECISION,
      unit TEXT,
      tags JSONB
    );
    CREATE INDEX IF NOT EXISTS idx_metrics_tmts ON metrics(tenant, metric, ts DESC);
    CREATE INDEX IF NOT EXISTS idx_metrics_src_ts ON metrics(source_id, ts DESC);

    CREATE TABLE IF NOT EXISTS alerts (
      id SERIAL PRIMARY KEY,
      ts TIMESTAMPTZ,
      tenant TEXT,
      source_id TEXT,
      metric TEXT,
      severity TEXT,
      rule TEXT,
      value DOUBLE PRECISION,
      message TEXT,
      tags JSONB
    );
    CREATE INDEX IF NOT EXISTS idx_alerts_tmts ON alerts(tenant, metric, ts DESC);
    """)
    con.commit()
    con.close()
