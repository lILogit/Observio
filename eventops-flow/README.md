# EventOps Flow — Local Store MVP (GitHub-ready)

**Collect → Normalize → Enrich → Store → Automate → Serve** using Redpanda + Python + DuckDB/Parquet.

## Quick start
```bash
make up             # build & start all
make init           # create topics and send a sample event
make urls           # show API/UI URLs
```

## Manual start
```bash
docker compose up -d --build
./scripts/init_topics.sh    # create topics
./scripts/seed_example.sh   # send example event
```

## Explore
- API: `http://localhost:8088/metrics/cpu?tenant=acme&host=host-a`
- Alerts SSE: `curl -N http://localhost:8088/alerts/stream`
- UI: `http://localhost:8080`

## Local DuckDB
```bash
docker run --rm -it -v $(pwd)/data:/data ghcr.io/duckdb/duckdb:latest       /bin/sh -lc "duckdb /data/metrics.duckdb 'SELECT COUNT(*) FROM metrics;'"
```

## Repo layout
```
common/         # Kafka + DuckDB helpers
normalizer/     # raw -> envelope metric
enricher/       # add tags from tiny CMDB
feature-rules/  # thresholds -> alerts + local sink
api/            # FastAPI endpoints + SSE
ui/             # tiny static page
scripts/        # rpk/kcat helpers
```
