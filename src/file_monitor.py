import json
import time
from datetime import datetime, timezone
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

BASE_DIR = Path.home() / "AGENTSENTRY_V2"
WATCH_DIR = BASE_DIR / "test_files"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "file_events.jsonl"


class FileMonitor(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event.event_type,
            "path": str(event.src_path),
        }

        if event.event_type == "moved":
            record["destination"] = str(event.dest_path)

        with LOG_FILE.open("a", encoding="utf-8") as log:
            log.write(json.dumps(record) + "\n")

        print(json.dumps(record), flush=True)


if __name__ == "__main__":
    WATCH_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    observer = Observer()
    observer.schedule(FileMonitor(), str(WATCH_DIR), recursive=True)
    observer.start()

    print(f"Monitoring: {WATCH_DIR}")
    print(f"Event log: {LOG_FILE}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    finally:
        observer.join()
