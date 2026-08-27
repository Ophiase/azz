import subprocess  # noqa: S404 - asking git about its own ignore rules
from collections.abc import Sequence
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


def is_tracked(repository: Path, path: Path) -> bool:
    """A tracked file cannot be hidden by an ignore rule — git ignores only
    apply to untracked paths."""
    completed = _git(repository, "ls-files", "--error-unmatch", str(path))
    return completed is not None and completed.returncode == 0


def local_exclude_file(repository: Path) -> Path | None:
    """`.git/info/exclude`: per-clone ignores that are never committed."""
    completed = _git(repository, "rev-parse", "--absolute-git-dir")
    if completed is None or completed.returncode != 0:
        return None
    return Path(completed.stdout.decode().strip()) / "info" / "exclude"


def add_local_excludes(repository: Path, patterns: Sequence[str]) -> tuple[str, ...]:
    """Append the patterns that are not already there. Reports what it added."""
    exclude_file = local_exclude_file(repository)
    if exclude_file is None:
        return ()
    existing = (
        exclude_file.read_text().splitlines() if exclude_file.is_file() else []
    )
    missing = tuple(pattern for pattern in patterns if pattern not in existing)
    if not missing:
        return ()
    exclude_file.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join([*existing, "", "# Added by azz claude install", *missing])
    exclude_file.write_text(body.strip() + "\n")
    return missing


def _git(repository: Path, *arguments: str) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(  # noqa: S603
            ["git", *arguments],  # noqa: S607
            cwd=repository,
            capture_output=True,
            timeout=CHECK_IGNORE_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
