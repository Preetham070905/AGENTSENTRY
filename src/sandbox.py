"""Linux Landlock filesystem restrictions for controlled agent processes."""

import ctypes
import errno
import os
import platform
from pathlib import Path


# Linux x86_64 syscall numbers. Other architectures must be mapped explicitly.
_SYS_LANDLOCK_CREATE_RULESET = 444
_SYS_LANDLOCK_ADD_RULE = 445
_SYS_LANDLOCK_RESTRICT_SELF = 446

_LANDLOCK_RULE_PATH_BENEATH = 1
_PR_SET_NO_NEW_PRIVS = 38

_ACCESS_FS_EXECUTE = 1 << 0
_ACCESS_FS_WRITE_FILE = 1 << 1
_ACCESS_FS_READ_FILE = 1 << 2
_ACCESS_FS_READ_DIR = 1 << 3
_ACCESS_FS_REMOVE_DIR = 1 << 4
_ACCESS_FS_REMOVE_FILE = 1 << 5
_ACCESS_FS_MAKE_CHAR = 1 << 6
_ACCESS_FS_MAKE_DIR = 1 << 7
_ACCESS_FS_MAKE_REG = 1 << 8
_ACCESS_FS_MAKE_SOCK = 1 << 9
_ACCESS_FS_MAKE_FIFO = 1 << 10
_ACCESS_FS_MAKE_BLOCK = 1 << 11
_ACCESS_FS_MAKE_SYM = 1 << 12
_ACCESS_FS_REFER = 1 << 13
_ACCESS_FS_TRUNCATE = 1 << 14


class _RulesetAttr(ctypes.Structure):
    _fields_ = [("handled_access_fs", ctypes.c_uint64)]


class _PathBeneathAttr(ctypes.Structure):
    _fields_ = [
        ("allowed_access", ctypes.c_uint64),
        ("parent_fd", ctypes.c_int),
    ]


def _raise_errno(operation: str) -> None:
    error_number = ctypes.get_errno()
    raise OSError(error_number, os.strerror(error_number), operation)


def landlock_abi_version() -> int:
    """Return the supported Landlock ABI version, or raise on failure."""
    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise RuntimeError("Landlock syscall mapping currently supports Linux x86_64 only.")

    libc = ctypes.CDLL("libc.so.6", use_errno=True)
    version = libc.syscall(
        _SYS_LANDLOCK_CREATE_RULESET,
        None,
        0,
        1,  # LANDLOCK_CREATE_RULESET_VERSION
    )
    if version < 0:
        _raise_errno("landlock_create_ruleset(version)")
    return int(version)


def restrict_current_process(workspace: str | Path) -> dict:
    """Restrict filesystem writes to workspace for this process and its descendants.

    Call this inside a dedicated child process before running agent-controlled code.
    This function does not change the parent process or system-wide security settings.
    """
    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise RuntimeError("Landlock syscall mapping currently supports Linux x86_64 only.")

    workspace_path = Path(workspace).resolve(strict=True)
    if not workspace_path.is_dir():
        raise ValueError("Workspace must be an existing directory.")

    libc = ctypes.CDLL("libc.so.6", use_errno=True)

    handled_access = (
        _ACCESS_FS_WRITE_FILE
        | _ACCESS_FS_REMOVE_DIR
        | _ACCESS_FS_REMOVE_FILE
        | _ACCESS_FS_MAKE_CHAR
        | _ACCESS_FS_MAKE_DIR
        | _ACCESS_FS_MAKE_REG
        | _ACCESS_FS_MAKE_SOCK
        | _ACCESS_FS_MAKE_FIFO
        | _ACCESS_FS_MAKE_BLOCK
        | _ACCESS_FS_MAKE_SYM
        | _ACCESS_FS_REFER
        | _ACCESS_FS_TRUNCATE
    )

    ruleset_attr = _RulesetAttr(handled_access_fs=handled_access)
    ruleset_fd = libc.syscall(
        _SYS_LANDLOCK_CREATE_RULESET,
        ctypes.byref(ruleset_attr),
        ctypes.sizeof(ruleset_attr),
        0,
    )
    if ruleset_fd < 0:
        _raise_errno("landlock_create_ruleset")

    workspace_fd = -1
    try:
        workspace_fd = os.open(workspace_path, os.O_PATH | os.O_CLOEXEC)

        # The agent can create, modify, rename, and delete files only under
        # the workspace. Existing file reads and execution remain available.
        allowed_access = (
            _ACCESS_FS_WRITE_FILE
            | _ACCESS_FS_REMOVE_DIR
            | _ACCESS_FS_REMOVE_FILE
            | _ACCESS_FS_MAKE_CHAR
            | _ACCESS_FS_MAKE_DIR
            | _ACCESS_FS_MAKE_REG
            | _ACCESS_FS_MAKE_SOCK
            | _ACCESS_FS_MAKE_FIFO
            | _ACCESS_FS_MAKE_BLOCK
            | _ACCESS_FS_MAKE_SYM
            | _ACCESS_FS_REFER
            | _ACCESS_FS_TRUNCATE
        )

        path_attr = _PathBeneathAttr(
            allowed_access=allowed_access,
            parent_fd=workspace_fd,
        )
        result = libc.syscall(
            _SYS_LANDLOCK_ADD_RULE,
            ruleset_fd,
            _LANDLOCK_RULE_PATH_BENEATH,
            ctypes.byref(path_attr),
            0,
        )
        if result < 0:
            _raise_errno("landlock_add_rule")

        if libc.prctl(_PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0:
            _raise_errno("prctl(PR_SET_NO_NEW_PRIVS)")

        result = libc.syscall(_SYS_LANDLOCK_RESTRICT_SELF, ruleset_fd, 0)
        if result < 0:
            _raise_errno("landlock_restrict_self")

        return {
            "enabled": True,
            "mechanism": "Landlock",
            "abi_version": landlock_abi_version(),
            "workspace": str(workspace_path),
            "policy": "Filesystem mutations restricted to the workspace",
        }
    finally:
        if workspace_fd >= 0:
            os.close(workspace_fd)
        os.close(ruleset_fd)
