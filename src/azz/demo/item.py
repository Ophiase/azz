from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel

from azz.cache import AzureField, ItemPayload
from azz.core.work_item import WorkItemState
from azz.core.work_item.work_item_type import WorkItemType


class DemoItem(BaseModel):
    """One fictional work item, as authored in the packaged board fixture."""

    id: int
    title: str
    item_type: WorkItemType
    state: WorkItemState
    changed_days_ago: float
    timebox_number: int | None = None
    parent_id: int | None = None
    assignee: str | None = None
    description: str | None = None

    def to_payload(
        self,
        project: str,
        assignee: str,
        timebox_path: str | None,
        reference: datetime,
    ) -> ItemPayload:
        changed = reference - timedelta(days=self.changed_days_ago)
        fields: dict[str, Any] = {
            AzureField.TITLE.value: self.title,
            AzureField.STATE.value: self.state.value,
            AzureField.PROJECT.value: project,
            AzureField.WORK_ITEM_TYPE.value: self.item_type.value,
            AzureField.ASSIGNED_TO.value: {"displayName": self.assignee or assignee},
            AzureField.CHANGED_DATE.value: changed.isoformat(),
        }
        if timebox_path:
            fields[AzureField.ITERATION_PATH.value] = timebox_path
        if self.parent_id is not None:
            fields[AzureField.PARENT.value] = self.parent_id
        if self.description:
            fields[AzureField.DESCRIPTION.value] = self.description
        return ItemPayload({"id": self.id, "fields": fields})
