#!/usr/bin/env bash
set -euo pipefail
docker compose up -d --build
./scripts/init_topics.sh
./scripts/seed_example.sh
echo "✅ Ready:"
echo "API: http://localhost:8088/metrics/cpu?tenant=acme&host=host-a"
echo "UI:  http://localhost:8080"
