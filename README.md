

# ⚙️ EventOps MVP framework

> **Collect → Normalize → Enrich → Store → Automate → Serve**

A minimal **event-driven observability pipeline** built with  
🦄 **Redpanda (broker + schema registry)**, 🐍 **Python micro-services**,  
and 🐘 **PostgreSQL (JSONB storage)** for concurrent local persistence.


## 🧭 Overview

**EventOps Flow** demonstrates how to transform raw telemetry into intelligent actions using lightweight, modular services.

- **PostgreSQL edition:** full ACID DB with concurrent readers/writers  
- **Ideal for:** demos, edge nodes, developer laptops, or PoC pipelines  
- **Architecture:** loosely coupled Python micro-services connected by a Redpanda event bus


## 🧩 Architecture at a Glance

```mermaid
flowchart LR
  subgraph Ingest
    Agent["Events"]
  end

  subgraph Core["Event Core"]
    Bus[(Redpanda Broker + Schema Registry)]
  end

  subgraph Stream["Stream Apps"]
    Norm[Normalizer]
    Enr[Enricher]
    Feat[Feature + Rules]
  end

  subgraph Storage
    PG[(PostgreSQL JSONB Store)]
  end

  subgraph Serve["Serve / UI"]
    API[FastAPI + SSE]
    UI[Grafana-lite / HTML]
  end

  Agent --> Bus
  Bus --> Norm --> Bus
  Bus --> Enr --> Bus
  Bus --> Feat --> Bus
  Bus --> PG
  API --> PG
  API --> Bus
  Bus --> UI
  UI --> API
````

---

## 📦 Core Components

| Service           | Purpose                           | Stack / Tech             |
| ----------------- | --------------------------------- | ------------------------ |
| **broker**        | Event transport + schema registry | 🦄 Redpanda (latest)     |
| **topics-init**   | Pre-creates Kafka topics          | Redpanda CLI (`rpk`)     |
| **normalizer**    | Clean & standardize incoming JSON | Python + confluent-kafka |
| **enricher**      | Add context (tags, metadata)      | Python                   |
| **feature-rules** | Apply rules + store in Postgres   | Python + psycopg2        |
| **postgres**      | Local relational store (JSONB)    | PostgreSQL 16            |
| **api**           | Query metrics + SSE alerts        | FastAPI + Postgres       |
| **ui**            | Minimal web dashboard             | Nginx + Vanilla JS       |

---

## 🚀 Quick Start

### 1️⃣ Clone & launch

```bash
git clone https://github.com/YOUR_USERNAME/eventops-flow.git
cd eventops-flow
docker compose up -d --build
```

### 2️⃣ Confirm topics

```bash
docker exec -it $(docker ps -qf name=broker) \
  rpk topic list --brokers=broker:9092
```

Expected:

```
ingest.raw.agent
signals.metric.v1
ops.alert.v1
```

### 3️⃣ Send sample telemetry

```bash
kcat -b localhost:9092 -t ingest.raw.agent -P <<'EOF'
{"tenant_id":"acme","host":"host-a","metric":"cpu_load","value":92,
 "ts_event":"2025-10-21T10:00:00Z","unit":"percent","tags":{"env":"prod"}}
EOF
```

### 4️⃣ Query data

```bash
curl "http://localhost:8088/metrics/cpu?tenant=acme&host=host-a"
curl -N http://localhost:8088/alerts/stream
```

### 5️⃣ Inspect Postgres manually

```bash
docker exec -it $(docker ps -qf name=postgres) \
  psql -U eventops -d eventops -c \
  "SELECT tenant, source_id, metric, value, ts FROM metrics ORDER BY ts DESC LIMIT 5;"
```

---

## 🗃️ Local Store Schema (PostgreSQL)

```sql
CREATE TABLE metrics (
  id SERIAL PRIMARY KEY,
  ts TIMESTAMPTZ,
  tenant TEXT,
  source_id TEXT,
  metric TEXT,
  value DOUBLE PRECISION,
  unit TEXT,
  tags JSONB
);
CREATE TABLE alerts (
  id SERIAL PRIMARY KEY,
  ts TIMESTAMPTZ,
  tenant TEXT,
  source_id TEXT,
  metric TEXT,
  severity TEXT,
  rule TEXT,
  value DOUBLE PRECISION,
  message TEXT,
  tags JSONB
);
```

---

## 🧰 Repository Layout

```
eventops-flow/
├── docker-compose.yml
├── common/
│   ├── kafka_io.py        # Kafka I/O helpers + ensure_topics()
│   ├── db_postgres.py     # Postgres connector + schema init
│   └── sink.py            # Insert metrics + alerts
├── normalizer/
├── enricher/
├── feature-rules/
├── api/
├── ui/
├── scripts/
│   └── seed_example.sh
└── README.md
```

---

## ⚡ Why PostgreSQL (JSONB)

* 🧩 Concurrent read/write safe (ACID)
* 💡 Schema-flexible (JSONB tags)
* 🪶 Easy migration from DuckDB / Parquet
* 🧠 Perfect for edge + PoC deployments

---

## 🧠 Extend & Customize

| Extension              | How                                                |
| ---------------------- | -------------------------------------------------- |
| **More metrics**       | Edit `feature-rules/main.py` thresholds            |
| **Extra topics**       | Add to `topics-init` command or `ensure_topics()`  |
| **External analytics** | Mirror metrics to ClickHouse / Qdrant              |
| **Automation**         | Trigger n8n / Flink / Temporal from `ops.alert.v1` |
| **Schema evolution**   | Keep envelope schema under `schemas/envelope.avsc` |

---

## 🛡️ Troubleshooting

| Symptom                                        | Fix                                                    |                       |
| ---------------------------------------------- | ------------------------------------------------------ | --------------------- |
| `UNKNOWN_TOPIC_OR_PART`                        | Re-run `topics-init` or call `ensure_topics()` in code |                       |
| `topics-init error: Bad for loop`              | Use POSIX `while` loop variant                         |                       |
| `decoding failed: invalid command line string` | Use list-form YAML with `                              | -` block for commands |
| `Could not set lock on file`                   | Old DuckDB residue — now fixed with Postgres           |                       |
| `psycopg2 OperationalError`                    | Check Postgres container is healthy                    |                       |

---

## 📜 License

MIT License — free to use, modify, and extend.

---

## ✨ Vision

> **EventOps Flow** bridges raw data and intelligent automation.
> From lightweight local demos to enterprise data fabrics,
> the same pattern scales — **one envelope, one bus, infinite possibilities.**

```

