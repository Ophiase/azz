from pathlib import Path

from pydantic import BaseModel

from azz.core.work_item import WorkItemState
from azz.core.work_item.helper import Markdown
from azz.core.work_item.work_item_type import WorkItemType


class LocalItem(BaseModel):
    """
    A single `.azz/tasks/*.md` intent file.

    A field left at `None` is absent from the frontmatter: it is never
    compared against the remote and never written to it. Every field here is
    the human's to edit — the merge base in `.azz/cache/` carries the
    tool-managed state.
    """

    path: Path
    item_id: int | None = None
    title: str | None = None
    state: WorkItemState | None = None
    item_type: WorkItemType | None = None
    parent: int | None = None
    iteration: str | None = None
    description: Markdown | None = None

    @property
    def is_new(self) -> bool:
        return self.item_id is None
