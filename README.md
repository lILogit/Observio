---

````markdown
# ⚙️ EventOps Flow — Local Store MVP

> **Collect → Normalize → Enrich → Store → Automate → Serve**

A minimal **event-driven observability pipeline** built with  
🦄 **Redpanda**, 🐍 **Python micro-services**, and 🪶 **DuckDB + Parquet** for local persistence.
---

## 🧭 Overview

**EventOps Flow** demonstrates how to transform raw telemetry into intelligent actions using lightweight, modular services.

- **Local-store edition:** zero external DB, instant analytics via DuckDB  
- **Ideal for:** demos, edge nodes, developer laptops, or PoC pipelines  
- **Architecture:** loosely coupled Python micro-services connected by a Redpanda event bus

---

## 🧩 Architecture at a Glance

```mermaid
flowchart LR
  subgraph Ingest
    Agent["Events"]
  end

  subgraph Core["Event Core"]
    Bus[(Redpanda Broker)]
    Reg[(Schema Registry built-in)]
    Reg --> Bus
  end

  subgraph Stream["Stream Apps"]
    Norm[Normalizer]
    Enr[Enricher]
    Feat[Feature + Rules]
  end

  subgraph Storage
    LS[(DuckDB + Parquet)]
  end

  subgraph Serve["Serve / UI"]
    API[FastAPI + SSE]
    UI[Grafana-lite / HTML]
  end

  Agent --> Bus
  Bus --> Norm --> Bus
  Bus --> Enr --> Bus
  Bus --> Feat --> Bus
  Bus --> LS
  API --> LS
  API --> Bus
  Bus --> UI
  UI --> API
````

---

## 📦 Components

| Service           | Purpose                           | Stack / Tech             |
| ----------------- | --------------------------------- | ------------------------ |
| **broker**        | Event transport + schema registry | 🦄 Redpanda (latest)     |
| **normalizer**    | Clean & standardize incoming JSON | Python + confluent-kafka |
| **enricher**      | Add context (tiny CMDB tags)      | Python                   |
| **feature-rules** | Derive features / alerts / store  | Python + DuckDB          |
| **api**           | Query metrics & SSE alerts        | FastAPI + DuckDB         |
| **ui**            | Minimal web dashboard             | Nginx + Vanilla JS       |

---

## 🚀 Quick Start

### 1️⃣  Clone & build

```bash
git clone https://github.com/YOUR_USERNAME/eventops-flow.git
cd eventops-flow
make up
```

### 2️⃣  Initialize topics & seed example

```bash
make init      # create topics
make seed      # send example event
make urls      # show API & UI endpoints
```

### 3️⃣  Inspect running stack

```bash
docker compose ps
```

---

## 🧪 Ingest Sample Events

Send telemetry to the broker:

```bash
# CPU warning
kcat -b localhost:9092 -t ingest.raw.agent -P <<'EOF'
{"tenant_id":"acme","host":"host-a","metric":"cpu_load","value":85,"ts_event":"2025-10-21T10:00:00Z","unit":"percent","tags":{"env":"prod"}}
EOF

# CPU critical
kcat -b localhost:9092 -t ingest.raw.agent -P <<'EOF'
{"tenant_id":"acme","host":"host-a","metric":"cpu_load","value":97,"ts_event":"2025-10-21T10:05:00Z","unit":"percent","tags":{"env":"prod"}}
EOF
```

---

## 🔍 Explore the Data

**API**

```bash
curl "http://localhost:8088/metrics/cpu?tenant=acme&host=host-a"
curl -N http://localhost:8088/alerts/stream
```

**UI**

```
http://localhost:8080
```

**DuckDB (inside feature-rules container)**

```bash
docker exec -it $(docker ps -qf name=feature-rules) \
  duckdb /data/metrics.duckdb "SELECT * FROM metrics ORDER BY ts DESC LIMIT 5;"
```

---

## 🗃️ Local Store Layout

```
/data/
  metrics.duckdb
  parquet/
    tenant=acme/metric=cpu_load/date=2025-10-21/part-0001.parquet
```

---

## 🧰 Repository Layout

```
eventops-flow/
├── docker-compose.yml
├── Makefile
├── build.sh
├── common/
│   ├── kafka_io.py        # Kafka I/O helpers
│   ├── duck.py            # DuckDB helpers
│   └── sink.py            # Insert & parquet export
├── normalizer/
├── enricher/
├── feature-rules/
├── api/
├── ui/
├── scripts/
│   ├── init_topics.sh
│   └── seed_example.sh
└── schemas/envelope.avsc
```

---

## ⚡ Why DuckDB + Parquet

* 🔌 No external DB required
* ⚡ Vectorized query engine (super fast analytics)
* 📂 Portable & human-readable storage
* 🧠 Perfect for edge, PoC, or local analytics

---

## 🧠 Extend & Customize

| Extension            | How                                                          |
| -------------------- | ------------------------------------------------------------ |
| **More metrics**     | Add new metric types & thresholds in `feature-rules/main.py` |
| **External DB**      | Swap `common/sink.py` to use ClickHouse / Postgres / Qdrant  |
| **Automation**       | Hook alerts to n8n, Flink, or Temporal                       |
| **Schema evolution** | Keep envelope schema versioned under `schemas/envelope.avsc` |

---

## 🛡️ Troubleshooting

| Symptom                                  | Fix                                                                               |
| ---------------------------------------- | --------------------------------------------------------------------------------- |
| `KafkaError{code=UNKNOWN_TOPIC_OR_PART}` | Run `make init` or the `scripts/init_topics.sh` script                            |
| `COPY ../common not found`               | Ensure `build.context` is `.` in `docker-compose.yml`                             |
| Schema registry 404                      | Use broker’s **embedded schema registry** (`--schema-registry-addr=0.0.0.0:8081`) |

---

## 📜 License

MIT License — free to use, modify, and extend.

---

## ✨ Vision

> **EventOps Flow** bridges raw data and intelligent automation.
> From lightweight local demos to enterprise data fabrics,
> the same pattern scales — **one envelope, one bus, infinite possibilities.**

```


