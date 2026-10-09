"""`push` sends only what the file itself changed: a field that moved on the
remote alone, or any difference without a merge base, must never be pushed
back — that would silently revert someone else's edit."""

from pathlib import Path

import pytest

from azz.cache import CacheStore, ItemPayload
from azz.cache.backend import CacheBackend
from azz.core.engine_config import EngineConfig
from azz.core.work_item import WorkItem
from azz.plan import ChangeType, LocalItem, Snapshots, compute_changeset
from tests.conftest import RemoteFactory

BASE_ITERATION = "Project\\TimeBox 1"
MOVED_ITERATION = "Project\\TimeBox 2"


@pytest.fixture
def snapshots(tmp_path: Path) -> Snapshots:
    return Snapshots.for_plan(tmp_path / ".azz")


def _remote(tmp_path: Path, work_item: WorkItem) -> CacheBackend:
    store = CacheStore(tmp_path / "remote")
    store.write_item(ItemPayload.from_work_item(work_item))
    config = EngineConfig(
        org_url="https://example.invalid",
        default_project="Project",
        management_project="Project",
        default_repo="repo",
        prepend_project_name=False,
    )
    return CacheBackend(store, config)


def _local(tmp_path: Path, title: str, iteration: str | None = None) -> LocalItem:
    return LocalItem(
        path=tmp_path / "item.md", item_id=1, title=title, iteration=iteration
    )


def test_a_remote_only_move_is_behind_and_never_pushed(
    tmp_path: Path, snapshots: Snapshots, remote_item: RemoteFactory
) -> None:
    snapshots.record_base(remote_item(iteration_path=BASE_ITERATION))
    remote = _remote(tmp_path, remote_item(iteration_path=MOVED_ITERATION))
    local = _local(tmp_path, title="Remote title", iteration="TimeBox 1")

    changeset = compute_changeset((local,), remote, snapshots)

    assert changeset.changes[0].change_type is ChangeType.BEHIND
    assert changeset.applicable == ()


def test_only_the_files_own_edit_is_pushed(
    tmp_path: Path, snapshots: Snapshots, remote_item: RemoteFactory
) -> None:
    snapshots.record_base(remote_item(iteration_path=BASE_ITERATION))
    remote = _remote(tmp_path, remote_item(iteration_path=MOVED_ITERATION))
    local = _local(tmp_path, title="Edited title", iteration="TimeBox 1")

    (change,) = compute_changeset((local,), remote, snapshots).applicable

    assert change.change_type is ChangeType.UPDATE
    assert change.changed_field_names == {"title"}


@pytest.mark.parametrize(
    ("title", "expected"),
    [("Edited title", ChangeType.NO_BASE), ("Remote title", ChangeType.NOOP)],
)
def test_without_a_base_nothing_is_pushed(
    tmp_path: Path,
    snapshots: Snapshots,
    remote_item: RemoteFactory,
    title: str,
    expected: ChangeType,
) -> None:
    remote = _remote(tmp_path, remote_item())
    local = _local(tmp_path, title=title)

    changeset = compute_changeset((local,), remote, snapshots)

    assert changeset.changes[0].change_type is expected
    assert changeset.applicable == ()
