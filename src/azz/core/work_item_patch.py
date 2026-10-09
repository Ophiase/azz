import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from .work_item.description_format import (
    DESCRIPTION_FIELD,
    FORMATS_KEY,
    DescriptionFormat,
)

AZURE_DEVOPS_RESOURCE: Final = "499b84ac-1321-427f-aa17-267ca6975798"
API_VERSION: Final = "7.1"
MARKDOWN_FORMAT: Final = "Markdown"
JSON_PATCH_HEADER: Final = "Content-Type=application/json-patch+json"

type FieldName = str
type JsonPatchOperation = dict[str, str]


@dataclass(frozen=True, slots=True)
class WorkItemPatch:
    """
    A work item update sent through `az rest`, so a description can be stored
    as Markdown.

    `az boards work-item update` cannot: the format is a separate
    `/multilineFieldsFormat` operation it never sends. Azure DevOps cannot turn
    a Markdown field back into HTML, so the operation is only added when the
    description is declared Markdown.
    """

    work_item_id: int
    fields: Mapping[FieldName, str]
    description_format: DescriptionFormat = DescriptionFormat.HTML

    @property
    def operations(self) -> tuple[JsonPatchOperation, ...]:
        field_operations = tuple(
            {"op": "add", "path": f"/fields/{name}", "value": value}
            for name, value in self.fields.items()
        )
        if not self._sets_markdown_description:
            return field_operations
        format_operation = {
            "op": "add",
            "path": f"/{FORMATS_KEY}/{DESCRIPTION_FIELD}",
            "value": MARKDOWN_FORMAT,
        }
        return (*field_operations, format_operation)

    @property
    def _sets_markdown_description(self) -> bool:
        return (
            DESCRIPTION_FIELD in self.fields
            and self.description_format is DescriptionFormat.MARKDOWN
        )

    def write_body(self, path: Path) -> None:
        path.write_text(json.dumps(self.operations))

    def az_arguments(self, org_url: str, body_path: Path) -> tuple[str, ...]:
        uri = (
            f"{org_url.rstrip('/')}/_apis/wit/workitems/{self.work_item_id}"
            f"?api-version={API_VERSION}"
        )
        return (
            "rest",
            "--method", "patch",
            "--resource", AZURE_DEVOPS_RESOURCE,
            "--uri", uri,
            "--headers", JSON_PATCH_HEADER,
            "--body", f"@{body_path}",
        )
