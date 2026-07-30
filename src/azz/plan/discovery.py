from pathlib import Path
from typing import Final

PLAN_DIRECTORY_NAME: Final = ".azz"
TASKS_DIRECTORY_NAME: Final = "tasks"
CACHE_DIRECTORY_NAME: Final = "cache"
FETCHED_DIRECTORY_NAME: Final = "fetched"


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
    """
    The merge base: the remote state each intent file was last synced from.

    Machine owned, never edited by hand. `azz plan pull` and `azz plan push`
    advance it, because both leave the working tree agreeing with the remote.
    """
    return plan_root / CACHE_DIRECTORY_NAME


def fetched_cache_directory(plan_root: Path) -> Path:
    """
    The newest remote state `azz plan fetch` saw, which may be ahead of the
    working tree. Kept apart from the merge base so a fetch cannot destroy the
    only record of what the files were synced from.
    """
    return cache_directory(plan_root) / FETCHED_DIRECTORY_NAME


def intent_file_paths(plan_root: Path) -> tuple[Path, ...]:
    directory = tasks_directory(plan_root)
    if not directory.is_dir():
        return ()
    return tuple(sorted(directory.glob("*.md")))
