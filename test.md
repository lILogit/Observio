
docker exec -it $(docker ps -qf name=broker) \
  rpk topic list --brokers=broker:9092

Send a sample event into the pipeline

docker exec -i $(docker ps -qf name=broker) \
  rpk topic produce ingest.raw.agent --brokers=broker:9092 <<'EOF'
{"tenant_id":"acme","host":"host-a","metric":"cpu_load","value":92,"ts_event":"2025-10-21T10:00:00Z","unit":"percent","tags":{"env":"prod"}}
EOF

Observe pipeline flow

docker compose logs -f normalizer enricher feature-rules api

Query stored data

curl "http://localhost:8088/metrics/cpu?tenant=acme&host=host-a"

[
  {
    "ts": "2025-10-21T10:00:00Z",
    "value": 92.0,
    "unit": "percent",
    "tags": {"env": "prod"}
  }
]

Live alert stream (if thresholds triggered):

curl -N http://localhost:8088/alerts/stream

Verify directly in Postgres

docker exec -it $(docker ps -qf name=postgres) \
  psql -U eventops -d eventops -c \
  "SELECT tenant, source_id, metric, value, ts FROM metrics ORDER BY ts DESC LIMIT 5;"


| Stage                    | Expected Outcome                       |
| ------------------------ | -------------------------------------- |
| `ingest.raw.agent`       | Receives raw JSON                      |
| `signals.metric.v1`      | Contains normalized event              |
| `ops.alert.v1`           | Contains alert (if any rule triggered) |
| Postgres `metrics` table | Row appears                            |
| API `/metrics/cpu`       | Returns JSON result                    |

