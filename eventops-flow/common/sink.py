import datetime as dt, pathlib
from .duck import connect, PARQUET_DIR

def write_metric_row(row: dict):
    con = connect()
    con.execute("""
        INSERT INTO metrics (ts, tenant, source_id, metric, value, unit, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        row["ts"], row["tenant"], row["source_id"], row["metric"],
        float(row["value"]), row.get("unit", ""), row.get("tags", {})
    ])
    date = row["ts"][:10]
    p = pathlib.Path(PARQUET_DIR) / f"tenant={row['tenant']}" / f"metric={row['metric']}" / f"date={date}"
    p.mkdir(parents=True, exist_ok=True)
    parquet_path = p / f"part-{int(dt.datetime.utcnow().timestamp())}.parquet"
    con.execute(f"""
        COPY (SELECT * FROM metrics
              WHERE tenant=? AND metric=? AND CAST(ts AS DATE)=?)
        TO '{parquet_path.as_posix()}'
        (FORMAT PARQUET);
    """, [row["tenant"], row["metric"], date])
    con.close()

def write_alert_row(row: dict):
    con = connect()
    con.execute("""
        INSERT INTO alerts (ts, tenant, source_id, metric, severity, rule, value, message, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        row["ts"], row["tenant"], row["source_id"], row["metric"],
        row["severity"], row["rule"], float(row["value"]), row["message"], row.get("tags", {})
    ])
    con.close()
