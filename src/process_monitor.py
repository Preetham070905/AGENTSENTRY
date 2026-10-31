import os
import time
import psutil
import json
from datetime import datetime, timezone


def get_process_snapshot():
    """Collect basic information about running processes."""
    processes = []

    for process in psutil.process_iter(
        ["pid", "name", "username", "status", "cpu_percent", "memory_info"]
    ):
        try:
            info = process.info
            memory = info.get("memory_info")

            processes.append({
                "pid": info["pid"],
                "name": info.get("name"),
                "username": info.get("username"),
                "status": info.get("status"),
                "cpu_percent": info.get("cpu_percent"),
                "memory_rss_bytes": memory.rss if memory else None,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "monitor_pid": os.getpid(),
        "process_count": len(processes),
        "processes": processes,
    }


if __name__ == "__main__":
    snapshot = get_process_snapshot()
    print(json.dumps(snapshot, indent=2))
