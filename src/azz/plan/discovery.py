from pathlib import Path
from typing import Final

PLAN_DIRECTORY_NAME: Final = ".azz"
TASKS_DIRECTORY_NAME: Final = "tasks"
CACHE_DIRECTORY_NAME: Final = "cache"


def find_plan_root(start: Path | None = None) -> Path | None:
    """Walk up from `start` looking for a `.azz` directory, like git does."""
    current = (start or Path.cwd()).resolve()
    for directory in (current, *current.parents):
        candidate = directory / PLAN_DIRECTORY_NAME
        if candidate.is_dir():
            return candidate
    return None


def tasks_directory(plan_root: Path) -> Path:
    """The working tree — human and agent owned."""
    return plan_root / TASKS_DIRECTORY_NAME


def cache_directory(plan_root: Path) -> Path:
    """Our knowledge of the remote — machine owned. Never edited by hand."""
    return plan_root / CACHE_DIRECTORY_NAME


def intent_file_paths(plan_root: Path) -> tuple[Path, ...]:
    directory = tasks_directory(plan_root)
    if not directory.is_dir():
        return ()
    return tuple(sorted(directory.glob("*.md")))
