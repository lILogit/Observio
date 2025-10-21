import duckdb, os, pathlib

DUCKDB_PATH = os.getenv("DUCKDB_PATH", "/data/metrics.duckdb")
DATA_DIR    = os.getenv("DATA_DIR", "/data")
PARQUET_DIR = os.path.join(DATA_DIR, "parquet")

pathlib.Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
pathlib.Path(PARQUET_DIR).mkdir(parents=True, exist_ok=True)

def connect():
    con = duckdb.connect(DUCKDB_PATH)
    con.execute("""
    CREATE TABLE IF NOT EXISTS metrics (
        ts TIMESTAMP,
        tenant TEXT,
        source_id TEXT,
        metric TEXT,
        value DOUBLE,
        unit TEXT,
        tags MAP(TEXT, TEXT)
    );
    """)
    con.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        ts TIMESTAMP,
        tenant TEXT,
        source_id TEXT,
        metric TEXT,
        severity TEXT,
        rule TEXT,
        value DOUBLE,
        message TEXT,
        tags MAP(TEXT, TEXT)
    );
    """)
    return con
