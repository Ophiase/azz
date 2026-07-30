from pathlib import Path
from typing import Final

from .discovery import PLAN_DIRECTORY_NAME, tasks_directory

GITIGNORE_CONTENT: Final = """\
# Planned work items are local by default.
# Un-ignore selectively (e.g. !shared-story.md) to share them with your team.
*
"""


def initialize_plan_directory(start: Path | None = None) -> Path:
    """Create `.azz/tasks/` and make the directory ignore itself. Idempotent."""
    plan_root = (start or Path.cwd()) / PLAN_DIRECTORY_NAME
    tasks_directory(plan_root).mkdir(parents=True, exist_ok=True)
    gitignore = plan_root / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(GITIGNORE_CONTENT)
    return plan_root
