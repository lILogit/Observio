#!/usr/bin/env bash
set -euo pipefail
BROKER_CONTAINER=$(docker ps -qf name=broker)
if [ -z "$BROKER_CONTAINER" ]; then
  echo "Broker not running yet"; exit 1
fi
docker exec -it "$BROKER_CONTAINER" rpk topic create ingest.raw.agent signals.metric.v1 ops.alert.v1 --brokers=broker:9092 || true

# Optional: tune retention (demo-friendly)
docker exec -it "$BROKER_CONTAINER" rpk topic alter-config ingest.raw.agent --set retention.ms=259200000 --brokers=broker:9092 || true
docker exec -it "$BROKER_CONTAINER" rpk topic alter-config signals.metric.v1 --set retention.ms=1209600000 --brokers=broker:9092 || true
docker exec -it "$BROKER_CONTAINER" rpk topic alter-config ops.alert.v1 --set cleanup.policy=compact,delete --brokers=broker:9092 || true

echo "✅ Topics ready"
