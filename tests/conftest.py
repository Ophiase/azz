from collections.abc import Callable
from pathlib import Path

import pytest

from azz.core.iteration_path import IterationPath
from azz.core.work_item import WorkItem, WorkItemState

type RemoteFactory = Callable[..., WorkItem]
type IntentFactory = Callable[[str], Path]


@pytest.fixture
def remote_item() -> RemoteFactory:
    """Build a remote work item, overriding only the fields under test."""

    def build(
        item_id: int = 1,
        name: str = "Remote title",
        state: WorkItemState = WorkItemState.NEW,
        description: str | None = None,
        iteration_path: str | None = None,
        parent_id: int | None = None,
    ) -> WorkItem:
        return WorkItem(
            id=item_id,
            name=name,
            state=state,
            project="Project",
            description=description,
            iteration_path=(
                IterationPath(iteration_path, normalized=True)
                if iteration_path is not None
                else None
            ),
            parent_id=parent_id,
        )

    return build


@pytest.fixture
def intent_file(tmp_path: Path) -> IntentFactory:
    """Write an intent file and return its path."""

    def build(text: str) -> Path:
        path = tmp_path / "item.md"
        path.write_text(text)
        return path

    return build
