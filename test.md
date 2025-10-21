Perfect ✅ — your stack is now wired (Redpanda + Postgres).
Let’s test the **full ingestion path** — from producing a raw event → normalization → enrichment → feature rules → Postgres → API.

---

## 🧪 Step 1. Verify services are up

```bash
docker compose ps
```

Expected running services:

```
broker, topics-init, postgres, normalizer, enricher, feature-rules, api, ui
```

Make sure `topics-init` printed “Topics ready” and exited (it’s one-shot).

---

## 🧪 Step 2. List topics

```bash
docker exec -it $(docker ps -qf name=broker) \
  rpk topic list --brokers=broker:9092
```

✅ Should list:

```
ingest.raw.agent
signals.metric.v1
ops.alert.v1
```

---

## 🧪 Step 3. Send a sample event into the pipeline

Use **kcat** (on your host or inside a container):

```bash
kcat -b localhost:9092 -t ingest.raw.agent -P <<'EOF'
{"tenant_id":"acme",
 "host":"host-a",
 "metric":"cpu_load",
 "value":92,
 "ts_event":"2025-10-21T10:00:00Z",
 "unit":"percent",
 "tags":{"env":"prod"}}
EOF
```

✅ This sends one **raw event** to `ingest.raw.agent`.

If you don’t have `kcat` installed locally:

```bash
docker exec -i $(docker ps -qf name=broker) \
  rpk topic produce ingest.raw.agent --brokers=broker:9092 <<'EOF'
{"tenant_id":"acme","host":"host-a","metric":"cpu_load","value":92,"ts_event":"2025-10-21T10:00:00Z","unit":"percent","tags":{"env":"prod"}}
EOF
```

---

## 🧩 Step 4. Observe pipeline flow

Watch the container logs (tail mode):

```bash
docker compose logs -f normalizer enricher feature-rules api
```

You should see something like:

```
[topics] created: signals.metric.v1
[normalizer] normalized event ...
[enricher] enriched event ...
[feature-rules] stored metric in Postgres
```

---

## 🧠 Step 5. Query stored data

### From the API:

```bash
curl "http://localhost:8088/metrics/cpu?tenant=acme&host=host-a"
```

→ Expected JSON:

```json
[
  {
    "ts": "2025-10-21T10:00:00Z",
    "value": 92.0,
    "unit": "percent",
    "tags": {"env": "prod"}
  }
]
```

### Or live alert stream (if thresholds triggered):

```bash
curl -N http://localhost:8088/alerts/stream
```

---

## 🧰 Step 6. Verify directly in Postgres

```bash
docker exec -it $(docker ps -qf name=postgres) \
  psql -U eventops -d eventops -c \
  "SELECT tenant, source_id, metric, value, ts FROM metrics ORDER BY ts DESC LIMIT 5;"
```

You should see a recent record for `cpu_load`.

---

## ✅ Result

| Stage                    | Expected Outcome                       |
| ------------------------ | -------------------------------------- |
| `ingest.raw.agent`       | Receives raw JSON                      |
| `signals.metric.v1`      | Contains normalized event              |
| `ops.alert.v1`           | Contains alert (if any rule triggered) |
| Postgres `metrics` table | Row appears                            |
| API `/metrics/cpu`       | Returns JSON result                    |

---

If you see the event reaching `normalizer` but not stored, send me the last few lines of `feature-rules` logs — that’s where the DuckDB→Postgres change may need tuning.
