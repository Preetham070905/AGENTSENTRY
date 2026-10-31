import json
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path.home() / "AGENTSENTRY_V2"
LOG_FILE = BASE_DIR / "logs" / "file_events.jsonl"
ALERT_FILE = BASE_DIR / "logs" / "security_alerts.jsonl"


def analyze_event(event):
    event_type = event.get("event", "")
    path = event.get("path", "")
    alerts = []

    if event_type in {"deleted", "moved"}:
        alerts.append({
            "rule": "FILE_CHANGE",
            "severity": "MEDIUM",
            "message": f"File {event_type}: {path}"
        })

    if "/etc/" in path or path.startswith("/root/"):
        alerts.append({
            "rule": "SENSITIVE_PATH",
            "severity": "HIGH",
            "message": f"Activity involving a sensitive path: {path}"
        })

    return alerts


def main():
    if not LOG_FILE.exists():
        print("No file-event log found. Start the file monitor first.")
        return

    events = [
        json.loads(line)
        for line in LOG_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    alert_count = 0

    with ALERT_FILE.open("a", encoding="utf-8") as output:
        for event in events:
            for alert in analyze_event(event):
                record = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source_event": event,
                    **alert
                }
                output.write(json.dumps(record) + "\n")
                print(json.dumps(record, indent=2))
                alert_count += 1

    print(f"Analysis complete. Alerts generated: {alert_count}")
    print(f"Alert log: {ALERT_FILE}")


if __name__ == "__main__":
    main()
