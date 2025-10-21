import os
from common.kafka_io import make_consumer, make_producer, stream_forever, send_json
from common.sink import write_metric_row, write_alert_row

IN_TOPIC  = os.getenv("IN_TOPIC", "signals.metric.v1")
OUT_TOPIC = os.getenv("OUT_TOPIC", "ops.alert.v1")

THRESHOLDS = {
    "cpu_load": (80.0, 90.0),
}

def to_metric_row(env: dict):
    attrs = env.get("attributes", {})
    return {
        "ts": env.get("ts_event"),
        "tenant": env.get("tenant_id"),
        "source_id": env.get("source", {}).get("source_id"),
        "metric": attrs.get("metric"),
        "value": float(attrs.get("value", "0")),
        "unit": attrs.get("unit", ""),
        "tags": env.get("tags", {}),
    }

def maybe_alert(metric_row: dict):
    metric = metric_row["metric"]
    value  = float(metric_row["value"])
    if metric not in THRESHOLDS:
        return None
    warn, crit = THRESHOLDS[metric]
    if value >= crit:
        sev = "critical"
    elif value >= warn:
        sev = "warning"
    else:
        return None
    return {
        "ts": metric_row["ts"],
        "tenant": metric_row["tenant"],
        "source_id": metric_row["source_id"],
        "metric": metric_row["metric"],
        "severity": sev,
        "rule": f"{metric}_threshold",
        "value": value,
        "message": f"{metric}={value} exceeds {sev} threshold",
        "tags": metric_row.get("tags", {})
    }

producer = make_producer()
consumer = make_consumer("feature-rules", [IN_TOPIC])

def handler(env: dict):
    row = to_metric_row(env)
    write_metric_row(row)
    alert = maybe_alert(row)
    if alert:
        write_alert_row(alert)
        send_json(producer, OUT_TOPIC, alert, key=alert["tenant"])

if __name__ == "__main__":
    stream_forever(consumer, handler)
