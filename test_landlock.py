import ctypes
import errno
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

if platform.system() != "Linux" or platform.machine() != "x86_64":
    raise SystemExit("This test currently supports x86_64 Linux only.")

CHILD_CODE = r'''
import ctypes
import errno
import os
import sys
from pathlib import Path

libc = ctypes.CDLL("libc.so.6", use_errno=True)

CREATE_RULESET = 444
ADD_RULE = 445
RESTRICT_SELF = 446

WRITE_FILE = 1 << 1
REMOVE_DIR = 1 << 4
REMOVE_FILE = 1 << 5
MAKE_REG = 1 << 8
REFER = 1 << 13
TRUNCATE = 1 << 14

class RulesetAttr(ctypes.Structure):
    _fields_ = [("handled_access_fs", ctypes.c_uint64)]

class PathBeneathAttr(ctypes.Structure):
    _fields_ = [
        ("allowed_access", ctypes.c_uint64),
        ("parent_fd", ctypes.c_int),
    ]

workspace = Path(sys.argv[1])
outside = Path(sys.argv[2])

handled = (
    WRITE_FILE | REMOVE_DIR | REMOVE_FILE |
    MAKE_REG | REFER | TRUNCATE
)
ruleset_attr = RulesetAttr(handled_access_fs=handled)

ruleset_fd = libc.syscall(
    CREATE_RULESET,
    ctypes.byref(ruleset_attr),
    ctypes.sizeof(ruleset_attr),
    0,
)
if ruleset_fd < 0:
    err = ctypes.get_errno()
    raise OSError(err, os.strerror(err), "landlock_create_ruleset")

workspace_fd = os.open(workspace, os.O_PATH | os.O_CLOEXEC)
try:
    allowed = WRITE_FILE | MAKE_REG | TRUNCATE
    path_attr = PathBeneathAttr(allowed_access=allowed, parent_fd=workspace_fd)

    result = libc.syscall(
        ADD_RULE, ruleset_fd, 1, ctypes.byref(path_attr), 0
    )
    if result < 0:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err), "landlock_add_rule")

    if libc.prctl(38, 1, 0, 0, 0) != 0:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err), "prctl(PR_SET_NO_NEW_PRIVS)")

    result = libc.syscall(RESTRICT_SELF, ruleset_fd, 0)
    if result < 0:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err), "landlock_restrict_self")

    (workspace / "allowed.txt").write_text("allowed\n", encoding="utf-8")
    print("PASS: write inside workspace was allowed", flush=True)

    try:
        (outside / "denied.txt").write_text("should be blocked\n", encoding="utf-8")
    except PermissionError as exc:
        if exc.errno != errno.EACCES:
            raise
        print("PASS: write outside workspace was denied (EACCES)", flush=True)
    else:
        raise SystemExit("FAIL: outside write unexpectedly succeeded")
finally:
    os.close(workspace_fd)
    os.close(ruleset_fd)
'''

with tempfile.TemporaryDirectory(prefix="agentsentry-landlock-") as temp:
    root = Path(temp)
    workspace = root / "workspace"
    outside = root / "outside"
    workspace.mkdir()
    outside.mkdir()

    result = subprocess.run(
        [sys.executable, "-c", CHILD_CODE, str(workspace), str(outside)],
        text=True,
        capture_output=True,
        check=False,
    )

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    if result.returncode != 0:
        raise SystemExit(f"FAIL: sandbox child exited with code {result.returncode}")

print("PASS: temporary test directory cleaned up")
