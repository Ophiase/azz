import subprocess  # noqa: S404 - asking git one read-only question
from pathlib import Path

CHECK_IGNORE_TIMEOUT_SECONDS = 5


def is_ignored(path: Path) -> bool | None:
    """Whether git ignores `path`.

    `None` means the question has no answer here — no git, or not a working
    tree — which callers should treat as "say nothing" rather than as a
    warning.
    """
    try:
        completed = subprocess.run(  # noqa: S603
            ["git", "check-ignore", "--quiet", str(path)],  # noqa: S607
            cwd=path.parent if path.parent.is_dir() else Path.cwd(),
            capture_output=True,
            timeout=CHECK_IGNORE_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return _from_exit_code(completed.returncode)


def _from_exit_code(code: int) -> bool | None:
    """git check-ignore: 0 ignored, 1 not ignored, anything else undecided."""
    if code == 0:
        return True
    return False if code == 1 else None
