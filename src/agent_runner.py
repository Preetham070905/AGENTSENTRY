"""Controlled Landlock test-agent runner for AGENTSENTRY_V2."""

import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from src.sandbox import landlock_abi_version

BASE_DIR = Path(__file__).resolve().parent.parent
WORKSPACE = BASE_DIR / "sandbox_workspace"
LOG_FILE = BASE_DIR / "logs" / "enforcement_events.jsonl"

CHILD_WORKFLOW = r'''
import errno
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from src.sandbox import restrict_current_process

workspace = Path(sys.argv[1]).resolve()
outside = Path(sys.argv[2]).resolve()
execution_id = sys.argv[3]

sandbox = restrict_current_process(workspace)
print(json.dumps({
    "kind": "sandbox_enabled",
    "execution_id": execution_id,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "pid": __import__("os").getpid(),
    "sandbox": sandbox,
}), flush=True)

def record(operation, target, outcome, enforcement, error=None):
    print(json.dumps({
        "kind": "enforcement_event",
        "execution_id": execution_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pid": __import__("os").getpid(),
        "operation": operation,
        "path": str(target),
        "outcome": outcome,
        "enforcement": enforcement,
        "error": error,
    }), flush=True)

inside_file = workspace / ("agent-" + execution_id + ".txt")
try:
    inside_file.write_text("controlled test\n", encoding="utf-8")
    record("write", inside_file, "allowed", "operation_succeeded")
except OSError as exc:
    record("write", inside_file, "failed", "not_confirmed_blocked",
           {"errno": exc.errno, "message": str(exc)})
    raise

outside_file = outside / ("agent-" + execution_id + ".txt")
try:
    outside_file.write_text("this should be denied\n", encoding="utf-8")
except PermissionError as exc:
    record("write", outside_file, "denied", "kernel_denial_confirmed",
           {"errno": exc.errno, "message": str(exc)})
    if exc.errno != errno.EACCES:
        raise
else:
    record("write", outside_file, "allowed", "unexpected_success")
    raise SystemExit("Security test failed: outside write succeeded")
'''


def append_record(record: dict) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as output:
        output.write(json.dumps(record) + "\n")


def run_controlled_test() -> dict:
    """Run the fixed test workflow; never accepts arbitrary shell commands."""
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    execution_id = str(uuid.uuid4())
    started = datetime.now(timezone.utc).isoformat()

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            CHILD_WORKFLOW,
            str(WORKSPACE),
            str(BASE_DIR),
            execution_id,
        ],
        cwd=str(BASE_DIR),
        text=True,
        capture_output=True,
        timeout=15,
        check=False,
    )

    parsed = []
    for line in result.stdout.splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        parsed.append(item)
        append_record(item)

    summary = {
        "kind": "execution_summary",
        "execution_id": execution_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "started_at": started,
        "exit_code": result.returncode,
        "status": "completed" if result.returncode == 0 else "failed",
        "landlock_abi": landlock_abi_version(),
        "evidence_records": len(parsed),
        "stderr": result.stderr[-2000:] if result.stderr else None,
    }
    append_record(summary)

    return {
        "execution_id": execution_id,
        "status": summary["status"],
        "exit_code": result.returncode,
        "landlock_abi": summary["landlock_abi"],
        "events": parsed,
        "stderr": summary["stderr"],
    }


if __name__ == "__main__":
    print(json.dumps(run_controlled_test(), indent=2))
