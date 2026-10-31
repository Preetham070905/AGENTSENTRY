import json
from pathlib import Path

import psutil
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path.home() / "AGENTSENTRY_V2"
LOG_DIR = BASE_DIR / "logs"

app = FastAPI(
    title="AGENTSENTRY API",
    description="AI-agent monitoring and security analysis dashboard API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def read_jsonl(filename):
    path = LOG_DIR / filename

    if not path.exists():
        return []

    records = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return records


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "AGENTSENTRY API"}


@app.get("/api/dashboard")
def dashboard():
    events = read_jsonl("file_events.jsonl")
    alerts = read_jsonl("security_alerts.jsonl")

    return {
        "process_count": len(psutil.pids()),
        "file_event_count": len(events),
        "alert_count": len(alerts),
        "high_alert_count": sum(
            1 for alert in alerts
            if alert.get("severity") == "HIGH"
        ),
        "recent_events": events[-10:][::-1],
        "recent_alerts": alerts[-10:][::-1],
    }


@app.get("/api/processes")
def processes():
    result = []

    for process in psutil.process_iter(
        ["pid", "name", "username", "status", "memory_info"]
    ):
        try:
            info = process.info
            memory = info.pop("memory_info", None)

            result.append({
                **info,
                "memory_rss_bytes": memory.rss if memory else 0,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return {"count": len(result), "processes": result}


@app.get("/api/events")
def events(limit: int = Query(default=100, ge=1, le=1000)):
    records = read_jsonl("file_events.jsonl")
    return {"count": len(records), "events": records[-limit:][::-1]}


@app.get("/api/alerts")
def alerts(limit: int = Query(default=100, ge=1, le=1000)):
    records = read_jsonl("security_alerts.jsonl")
    return {"count": len(records), "alerts": records[-limit:][::-1]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


@app.get("/api/enforcement-events")
def enforcement_events(limit: int = Query(default=100, ge=1, le=1000)):
    """Return recorded sandbox enforcement evidence, newest first."""
    records = read_jsonl("enforcement_events.jsonl")
    return {
        "count": len(records),
        "events": records[-limit:][::-1],
        "confirmed_denials": sum(
            1 for record in records
            if record.get("enforcement") == "kernel_denial_confirmed"
        ),
    }


@app.get("/api/agents")
def agents():
    """Return executions reconstructed from persisted enforcement evidence."""
    records = read_jsonl("enforcement_events.jsonl")
    executions = {}

    for record in records:
        execution_id = record.get("execution_id")
        if not execution_id:
            continue

        item = executions.setdefault(execution_id, {
            "execution_id": execution_id,
            "pid": None,
            "status": "unknown",
            "landlock_abi": None,
            "workspace": None,
            "events": [],
            "confirmed_denials": 0,
        })

        if record.get("kind") == "sandbox_enabled":
            item["pid"] = record.get("pid")
            sandbox = record.get("sandbox", {})
            item["landlock_abi"] = sandbox.get("abi_version")
            item["workspace"] = sandbox.get("workspace")
            item["status"] = "sandbox_enabled"

        elif record.get("kind") == "enforcement_event":
            item["events"].append(record)
            if record.get("enforcement") == "kernel_denial_confirmed":
                item["confirmed_denials"] += 1

        elif record.get("kind") == "execution_summary":
            item["status"] = record.get("status", "unknown")
            item["exit_code"] = record.get("exit_code")
            item["timestamp"] = record.get("timestamp")

    result = sorted(
        executions.values(),
        key=lambda item: item.get("timestamp", ""),
        reverse=True,
    )
    return {"count": len(result), "agents": result}


@app.get("/api/xai-explanations")
def xai_explanations(limit: int = Query(default=100, ge=1, le=1000)):
    """Return evidence-based explanations, newest first."""
    records = read_jsonl("xai_explanations.jsonl")
    return {
        "count": len(records),
        "explanations": records[-limit:][::-1],
    }
