from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from logging import getLogger
from typing import Any, Final

from azz.core.editor import edit_work_item_in_editor
from azz.core.engine_config import EngineConfig
from azz.core.timebox import Iteration
from azz.core.work_item import WorkItem, WorkItemFilter, WorkItemState
from azz.core.work_item.work_item_filter import IterationPathFilter, StateFilter
from azz.core.work_item.work_item_type import WorkItemType

from .assignee_filter import AssigneeFilter, DisplayName
from .payload import AzureField, ItemPayload
from .store import CacheStore

logger = getLogger(__name__)

CURRENT_USER_ALIAS: Final = "@me"
DEFAULT_STATES: Final = frozenset({WorkItemState.ACTIVE, WorkItemState.NEW})


class CacheBackend:
    """
    A `WorkItemBackend` served entirely by a `CacheStore`.

    Reads answer from the cached JSON; mutations rewrite it and bump
    `System.ChangedDate`, so ordering by change date stays meaningful in the
    TUI. Nothing here shells out to `az` or opens a socket, which is what makes
    offline browsing and demo mode possible.

    Two parameters cannot mean here what they mean on the remote:

    - `project_filter` is ignored. The cache only ever holds the projects that
      were fetched into it, so there is nothing left to filter out.
    - `list_timeboxes(project=...)` is ignored for the same reason: one cache
      holds one project's iterations.
    """

    def __init__(
        self,
        store: CacheStore,
        config: EngineConfig,
        owner: DisplayName | None = None,
        now: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._store = store
        self._config = config
        self._owner = owner
        self._now = now

    @property
    def config(self) -> EngineConfig:
        return self._config

    @property
    def store(self) -> CacheStore:
        return self._store

    # --- Reads ---

    def list_work_items(
        self,
        assigned_to: str = CURRENT_USER_ALIAS,
        states: frozenset[WorkItemState] | None = None,
        show_others: bool = False,
        project_filter: bool = True,  # noqa: ARG002 - see class docstring
        current_timebox_only: bool = False,
    ) -> tuple[WorkItem, ...]:
        # StateFilter annotates its states as WorkItem where it means
        # WorkItemState; it compares against WorkItemState at runtime.
        state_filter = StateFilter(
            tuple(states or DEFAULT_STATES)  # ty: ignore[invalid-argument-type]
        )
        filters: list[WorkItemFilter] = [state_filter]
        if not show_others:
            filters.append(AssigneeFilter(self._resolve_owner(assigned_to)))
        if current_timebox_only:
            filters.append(IterationPathFilter(self.get_current_timebox().path))
        return WorkItemFilter.apply_filters(self._store.read_all_items(), *filters)

    def get_workitem(self, work_item_id: int) -> WorkItem:
        return self._require_payload(work_item_id).to_work_item()

    def list_timeboxes(
        self,
        project: str | None = None,  # noqa: ARG002 - see class docstring
    ) -> tuple[Iteration, ...]:
        return self._store.read_timeboxes()

    def get_current_timebox(self, project: str | None = None) -> Iteration:
        """
        The cached iteration covering today, else the last one cached.

        Azure lists iterations chronologically, so the fallback is the latest
        sprint we know of — the useful answer for a cache whose sprints have
        all ended.
        """
        timeboxes = self.list_timeboxes(project)
        if not timeboxes:
            raise RuntimeError("Current timebox not found: the cache holds none")
        current = next((timebox for timebox in timeboxes if timebox.is_current), None)
        return current or timeboxes[-1]

    # --- Mutations ---

    def update_workitem(self, work_item: WorkItem) -> None:
        self._rewrite(
            work_item.id,
            {
                AzureField.TITLE: work_item.name,
                AzureField.DESCRIPTION: work_item.description or None,
            },
        )

    def update_work_item_state(
        self, work_item_id: int, new_state: WorkItemState
    ) -> None:
        self._rewrite(work_item_id, {AzureField.STATE: new_state.value})

    def update_work_item_title(self, work_item_id: int, new_title: str) -> None:
        self._rewrite(work_item_id, {AzureField.TITLE: new_title})

    def set_timebox(self, task_id: int, timebox: Iteration) -> None:
        if not timebox.path.normalized:
            raise ValueError("Invalid timebox path")
        self._rewrite(task_id, {AzureField.ITERATION_PATH: timebox.path.value})

    def link_parent(self, child_id: int, parent_id: int) -> None:
        self._require_payload(parent_id)
        self._rewrite(child_id, {AzureField.PARENT: parent_id})

    def create_work_item_helper(
        self,
        name: str,
        description: str | None = None,
        project: str | None = None,
        item_type: WorkItemType = WorkItemType.TASK,
    ) -> WorkItem:
        payload = ItemPayload({
            "id": self._store.next_item_id(),
            "fields": self._new_item_fields(name, description, project, item_type),
        })
        self._store.write_item(payload)
        return payload.to_work_item()

    def delete_workitem_helper(self, work_item_id: int) -> None:
        if not self._store.delete_item(work_item_id):
            logger.debug("work item %s was already absent from the cache", work_item_id)

    def edit_work_item(self, work_item_id: int, edit_title: bool) -> WorkItem:
        edited = edit_work_item_in_editor(self.get_workitem(work_item_id), edit_title)
        self.update_workitem(edited)
        return edited

    # --- Internals ---

    def _resolve_owner(self, assigned_to: str) -> DisplayName | None:
        return self._owner if assigned_to == CURRENT_USER_ALIAS else assigned_to

    def _require_payload(self, work_item_id: int) -> ItemPayload:
        payload = self._store.read_payload(work_item_id)
        if payload is None:
            raise RuntimeError(
                f"work item {work_item_id} is not in the cache "
                f"at {self._store.root}"
            )
        return payload

    def _rewrite(self, work_item_id: int, updates: Mapping[AzureField, Any]) -> None:
        payload = self._require_payload(work_item_id)
        self._store.write_item(
            payload.with_fields(updates).with_change_stamp(self._now())
        )

    def _new_item_fields(
        self,
        name: str,
        description: str | None,
        project: str | None,
        item_type: WorkItemType,
    ) -> dict[str, Any]:
        title = self._decorated_title(name, project or self._config.default_project)
        fields: dict[str, Any] = {
            AzureField.TITLE.value: title,
            AzureField.STATE.value: WorkItemState.NEW.value,
            AzureField.PROJECT.value: self._config.management_project,
            AzureField.WORK_ITEM_TYPE.value: item_type.value,
            AzureField.CHANGED_DATE.value: self._now().isoformat(),
        }
        if description:
            fields[AzureField.DESCRIPTION.value] = description
        if self._owner:
            fields[AzureField.ASSIGNED_TO.value] = {"displayName": self._owner}
        timebox_path = self._new_item_timebox_path()
        if timebox_path:
            fields[AzureField.ITERATION_PATH.value] = timebox_path
        return fields

    def _decorated_title(self, name: str, project: str) -> str:
        return f"[{project}] - {name}" if self._config.prepend_project_name else name

    def _new_item_timebox_path(self) -> str | None:
        try:
            return self.get_current_timebox().path.value or None
        except RuntimeError:
            return None
