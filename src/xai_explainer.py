"""Evidence-based explanations for AGENTSENTRY enforcement events.

This module explains recorded results. It does not make enforcement decisions.
"""

import json
from pathlib import Path

BASE_DIR = Path.home() / "AGENTSENTRY_V2"
LOG_FILE = BASE_DIR / "logs" / "enforcement_events.jsonl"
OUTPUT_FILE = BASE_DIR / "logs" / "xai_explanations.jsonl"


def explain_event(event):
    """Return an explanation grounded in the supplied event fields."""
    kind = event.get("kind")
    outcome = event.get("outcome")
    operation = event.get("operation", "operation")
    path = event.get("path", "an unspecified path")
    enforcement = event.get("enforcement")
    error = event.get("error") or {}

    if kind == "sandbox_enabled":
        sandbox = event.get("sandbox") or {}
        workspace = sandbox.get("workspace", "the configured workspace")
        mechanism = sandbox.get("mechanism", "unknown mechanism")
        return {
            "title": "Sandbox enabled",
            "explanation": (
                f"{mechanism} sandboxing was enabled for this execution. "
                f"The recorded policy states: "
                f"{sandbox.get('policy', 'No policy description recorded')}."
            ),
            "evidence": {
                "workspace": workspace,
                "abi_version": sandbox.get("abi_version"),
                "pid": event.get("pid"),
            },
        }

    if kind == "enforcement_event" and outcome == "denied":
        if enforcement == "kernel_denial_confirmed":
            explanation = (
                f"The {operation} operation on {path} was denied. "
                "The event records a kernel-enforced denial. "
            )
            if error.get("errno") == 13:
                explanation += (
                    "Error 13 (EACCES) indicates permission was denied. "
                )
            explanation += (
                "This is consistent with the sandbox restricting filesystem "
                "mutations to its permitted workspace."
            )
        else:
            explanation = (
                f"The {operation} operation on {path} was recorded as denied, "
                "but the log does not confirm a kernel denial."
            )

        return {
            "title": "Filesystem operation denied",
            "explanation": explanation,
            "evidence": {
                "outcome": outcome,
                "enforcement": enforcement,
                "errno": error.get("errno"),
                "path": path,
            },
        }

    if kind == "enforcement_event" and outcome == "allowed":
        return {
            "title": "Filesystem operation succeeded",
            "explanation": (
                f"The {operation} operation on {path} succeeded. "
                "This records a successful operation; it does not establish "
                "that every other filesystem operation is permitted."
            ),
            "evidence": {
                "outcome": outcome,
                "enforcement": enforcement,
                "path": path,
            },
        }

    if kind == "execution_summary":
        return {
            "title": "Execution summary",
            "explanation": (
                f"The recorded execution status is {event.get('status', 'unknown')}, "
                f"with exit code {event.get('exit_code', 'not recorded')}."
            ),
            "evidence": {
                "execution_id": event.get("execution_id"),
                "status": event.get("status"),
                "exit_code": event.get("exit_code"),
                "landlock_abi": event.get("landlock_abi"),
            },
        }

    return {
        "title": "Insufficient evidence",
        "explanation": (
            "The event does not contain enough recognized fields to generate "
            "a specific explanation. No enforcement conclusion was inferred."
        ),
        "evidence": {
            "kind": kind,
            "execution_id": event.get("execution_id"),
        },
    }


def main():
    if not LOG_FILE.exists():
        print(f"No enforcement log found: {LOG_FILE}")
        return

    records = []
    for line in LOG_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        records.append({
            "timestamp": event.get("timestamp"),
            "execution_id": event.get("execution_id"),
            "source_kind": event.get("kind"),
            **explain_event(event),
        })

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as output:
        for record in records:
            output.write(json.dumps(record) + "\n")

    print(f"Explanations generated: {len(records)}")
    print(f"Explanation log: {OUTPUT_FILE}")
    for record in records:
        print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
