# common/sink.py
import json
from .db_postgres import get_conn, init_schema

# Ensure tables on import
init_schema()

def write_metric_row(row: dict):
    con = get_conn()
    cur = con.cursor()
    cur.execute(
        """INSERT INTO metrics (ts, tenant, source_id, metric, value, unit, tags)
           VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)""",
        (row["ts"], row["tenant"], row["source_id"], row["metric"],
         float(row["value"]), row.get("unit",""), json.dumps(row.get("tags", {})))
    )
    con.commit(); con.close()

def write_alert_row(row: dict):
    con = get_conn()
    cur = con.cursor()
    cur.execute(
        """INSERT INTO alerts (ts, tenant, source_id, metric, severity, rule, value, message, tags)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)""",
        (row["ts"], row["tenant"], row["source_id"], row["metric"],
         row["severity"], row["rule"], float(row["value"]), row["message"],
         json.dumps(row.get("tags", {})))
    )
    con.commit(); con.close()
