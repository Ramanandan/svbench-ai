"""Small subprocess helpers shared by the pipeline modules."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Console scripts (truvari, samplot) install alongside the running interpreter,
# in .venv/bin. When the app is launched via `./.venv/bin/svbench` without
# activating the venv, that directory is not on PATH -- so include it explicitly
# for every subprocess and tool check. NB: don't resolve() sys.executable -- in a
# venv it's a symlink to the base interpreter, which points away from .venv/bin.
_BIN_DIRS = []
for _d in (os.path.dirname(sys.executable), os.path.join(sys.prefix, "bin")):
    if _d and os.path.isdir(_d) and _d not in _BIN_DIRS:
        _BIN_DIRS.append(_d)


def _augmented_path() -> str:
    parts = os.environ.get("PATH", "").split(os.pathsep)
    extra = [d for d in _BIN_DIRS if d not in parts]
    return os.pathsep.join([*extra, *parts]) if extra else os.environ.get("PATH", "")


def require(*tools: str) -> None:
    """Fail early with a clear message if a CLI tool is missing."""
    path = _augmented_path()
    missing = [t for t in tools if shutil.which(t, path=path) is None]
    if missing:
        sys.exit(
            f"[svbench] missing required tools: {', '.join(missing)}\n"
            f"          install them (see the Makefile) and ensure they are on PATH."
        )


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a command, echoing it, and raise on non-zero exit.

    PATH is augmented with the interpreter's bin dir so venv-installed tools
    (truvari, samplot) resolve even when the venv isn't activated.
    """
    print("[run]", " ".join(str(c) for c in cmd), file=sys.stderr)
    if "env" not in kwargs:
        kwargs["env"] = {**os.environ, "PATH": _augmented_path()}
    return subprocess.run([str(c) for c in cmd], check=True, **kwargs)


def curl(url: str, dest: Path, resume: bool = True) -> Path:
    """Download `url` to `dest` with curl (resumable). Skips if already present
    and non-empty."""
    dest = Path(dest)
    if dest.exists() and dest.stat().st_size > 0:
        print(f"[skip] {dest.name} already present", file=sys.stderr)
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    cmd = ["curl", "-fL", "--retry", "3", "-o", str(tmp)]
    if resume:
        cmd += ["-C", "-"]
    cmd.append(url)
    run(cmd)
    tmp.replace(dest)
    return dest
