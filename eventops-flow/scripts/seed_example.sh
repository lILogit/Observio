#!/usr/bin/env bash
set -euo pipefail
# Try sending via rpk (inside broker)
BROKER_CONTAINER=$(docker ps -qf name=broker)
if [ -z "$BROKER_CONTAINER" ]; then
  echo "Broker not running yet"; exit 1
fi

PAYLOAD='{"tenant_id":"acme","host":"host-a","metric":"cpu_load","value":92,"ts_event":"2025-10-16T09:00:00Z","unit":"percent","tags":{"env":"prod"}}'
echo "$PAYLOAD" | docker exec -i "$BROKER_CONTAINER" rpk topic produce ingest.raw.agent --brokers=broker:9092 >/dev/null || true

echo "✅ Seed event sent"
