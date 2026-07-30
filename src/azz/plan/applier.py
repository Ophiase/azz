from dataclasses import replace
from logging import getLogger
from pathlib import Path

from azz.core.engine import Engine
from azz.core.timebox import Iteration
from azz.core.work_item import WorkItem
from azz.core.work_item.work_item_type import WorkItemType

from .comparison import UPDATABLE_FIELDS
from .models import ApplyOutcome, Change, ChangeType, LocalItem
from .writer import write_back

logger = getLogger(__name__)


class Applier:
    """Pushes a single `Change` to the remote. Never rolls back."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def apply(self, change: Change) -> ApplyOutcome:
        try:
            if change.change_type is ChangeType.CREATE:
                return self._create(change)
            return self._update(change)
        except (RuntimeError, ValueError) as error:
            return ApplyOutcome(change, str(error), succeeded=False)

    def _create(self, change: Change) -> ApplyOutcome:
        local_item = change.local_item
        if not local_item.title:
            raise ValueError("cannot create: 'title' is required")

        created = self._engine.create_work_item_helper(
            local_item.title,
            description=local_item.description,
            item_type=local_item.item_type or WorkItemType.TASK,
        )
        self._push_optional_fields(created.id, local_item)
        write_back(local_item.path, created.id, title=created.name)
        self._record_remote_timestamp(local_item.path, created.id)
        return ApplyOutcome(change, f"created #{created.id}", succeeded=True)

    def _update(self, change: Change) -> ApplyOutcome:
        local_item = change.local_item
        work_item_id = local_item.item_id
        remote_item = change.remote_item
        if work_item_id is None or remote_item is None:
            raise ValueError("cannot update: missing item_id or remote item")

        changed = change.changed_field_names
        if changed & {"title", "description"}:
            self._push_content(remote_item, local_item, changed)
        self._push_optional_fields(work_item_id, local_item, only=changed)
        self._record_remote_timestamp(local_item.path, work_item_id)
        return ApplyOutcome(
            change, _update_message(work_item_id, changed), succeeded=True
        )

    def _record_remote_timestamp(self, path: Path, work_item_id: int) -> None:
        """Best effort — the change is already applied, so a failure here must
        not turn a successful push into a reported error."""
        try:
            refreshed = self._engine.get_workitem(work_item_id)
            write_back(path, remote_changed_date=refreshed.changed_date)
        except (RuntimeError, OSError) as error:
            logger.debug("could not record remote timestamp for %s: %s", path, error)

    def _push_content(
        self, remote_item: WorkItem, local_item: LocalItem, changed: frozenset[str]
    ) -> None:
        target = remote_item
        if "title" in changed and local_item.title:
            target = replace(target, name=local_item.title)
        if "description" in changed and local_item.description is not None:
            target = replace(target, description=local_item.description)
        self._engine.update_workitem(target)

    def _push_optional_fields(
        self,
        work_item_id: int,
        local_item: LocalItem,
        only: frozenset[str] | None = None,
    ) -> None:
        def wanted(field_name: str) -> bool:
            return only is None or field_name in only

        if local_item.state is not None and wanted("state"):
            self._engine.update_work_item_state(work_item_id, local_item.state)
        if local_item.parent is not None and wanted("parent"):
            self._engine.link_parent(work_item_id, local_item.parent)
        if local_item.iteration is not None and wanted("iteration"):
            iteration = self._resolve_iteration(local_item.iteration)
            self._engine.set_timebox(work_item_id, iteration)

    def _resolve_iteration(self, name: str) -> Iteration:
        for timebox in self._engine.list_timeboxes():
            if name in (timebox.name, timebox.path.value.split("\\")[-1]):
                return timebox
        raise ValueError(f"unknown iteration '{name}'")


def _update_message(work_item_id: int, changed: frozenset[str]) -> str:
    applied = sorted(changed & UPDATABLE_FIELDS)
    skipped = sorted(changed - UPDATABLE_FIELDS)
    message = f"updated #{work_item_id}: {', '.join(applied) or 'nothing'}"
    if skipped:
        message += f" (skipped, not supported on update: {', '.join(skipped)})"
    return message
