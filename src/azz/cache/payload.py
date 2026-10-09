from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Self

from azz.core.work_item import WorkItem
from azz.core.work_item.description_format import (
    FORMATS_KEY,
    DescriptionFormat,
    body_field_of,
)
from azz.core.work_item.work_item import work_item_factory


class AzureField(StrEnum):
    """The `System.*` field names an `az` work item response uses."""

    TITLE = "System.Title"
    STATE = "System.State"
    PROJECT = "System.TeamProject"
    DESCRIPTION = "System.Description"
    REPRO_STEPS = "Microsoft.VSTS.TCM.ReproSteps"
    PRIORITY = "Microsoft.VSTS.Common.Priority"
    ASSIGNED_TO = "System.AssignedTo"
    ITERATION_PATH = "System.IterationPath"
    PARENT = "System.Parent"
    CHANGED_DATE = "System.ChangedDate"
    WORK_ITEM_TYPE = "System.WorkItemType"


@dataclass(frozen=True, slots=True)
class ItemPayload:
    """
    One work item in the shape `az` returned it.

    Kept verbatim so the cache stays an honest record of what the remote said,
    and so `work_item_factory` rehydrates it without a second lossy
    conversion. This is the only class besides `WorkItem` itself that needs to
    know Azure's field names.
    """

    data: dict[str, Any]

    @property
    def item_id(self) -> int:
        return int(self.data["id"])

    @property
    def fields(self) -> Mapping[str, Any]:
        return self.data.get("fields", {})

    def to_work_item(self) -> WorkItem:
        return work_item_factory(self.data)

    def with_fields(self, updates: Mapping[AzureField, Any]) -> Self:
        """A copy with those fields set. A `None` value removes the field."""
        fields = dict(self.fields)
        for field, value in updates.items():
            if value is None:
                fields.pop(field.value, None)
            else:
                fields[field.value] = value
        return type(self)({**self.data, "fields": fields})

    def with_description_format(self, description_format: DescriptionFormat) -> Self:
        formats = {
            **(self.data.get(FORMATS_KEY) or {}),
            body_field_of(self.data): description_format.value,
        }
        return type(self)({**self.data, FORMATS_KEY: formats})

    def with_change_stamp(self, moment: datetime) -> Self:
        return self.with_fields({AzureField.CHANGED_DATE: moment.isoformat()})

    @classmethod
    def from_work_item(cls, work_item: WorkItem) -> Self:
        """Synthesise a payload — for locally created items and demo fixtures."""
        required: dict[str, Any] = {
            AzureField.TITLE.value: work_item.name,
            AzureField.STATE.value: work_item.state.value,
            AzureField.PROJECT.value: work_item.project,
            AzureField.WORK_ITEM_TYPE.value: work_item.item_type.value,
        }
        payload = cls({"id": work_item.id, "fields": required | _optional(work_item)})
        return payload.with_description_format(work_item.description_format)


def _optional(work_item: WorkItem) -> dict[str, Any]:
    assigned_to = (
        {"displayName": work_item.assigned_to} if work_item.assigned_to else None
    )
    iteration_path = (
        work_item.iteration_path.value
        if work_item.iteration_path and work_item.iteration_path.value
        else None
    )
    changed_date = (
        work_item.changed_date.isoformat() if work_item.changed_date else None
    )
    candidates = {
        AzureField.DESCRIPTION.value: work_item.description,
        AzureField.ASSIGNED_TO.value: assigned_to,
        AzureField.ITERATION_PATH.value: iteration_path,
        AzureField.PARENT.value: work_item.parent_id,
        AzureField.CHANGED_DATE.value: changed_date,
        AzureField.PRIORITY.value: (
            int(work_item.priority) if work_item.priority is not None else None
        ),
    }
    return {key: value for key, value in candidates.items() if value is not None}
