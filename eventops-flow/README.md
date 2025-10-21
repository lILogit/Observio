# ⚙️ EventOps Flow — Local Store Edition
Collect → Normalize → Enrich → Store → Automate → Process → Serve

Minimal, event-driven pipeline with **DuckDB + Parquet** local storage and a tiny FastAPI.
See README in chat for full details.

## Quick start
```bash
docker compose up -d

# simulate an agent event (requires kcat on host)
kcat -b localhost:9092 -t ingest.raw.agent -P <<EOF
{"tenant_id":"acme","host":"host-a","metric":"cpu_load","value":92,
 "ts_event":"2025-10-16T09:00:00Z","unit":"percent","tags":{"env":"prod"}}
EOF

# query
curl "http://localhost:8088/metrics/cpu?tenant=acme&host=host-a"
# alerts stream
curl -N http://localhost:8088/alerts/stream
```
