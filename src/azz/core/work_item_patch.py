import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

from .work_item.description_format import FORMATS_KEY

AZURE_DEVOPS_RESOURCE: Final = "499b84ac-1321-427f-aa17-267ca6975798"
API_VERSION: Final = "7.1"
MARKDOWN_FORMAT: Final = "Markdown"
JSON_PATCH_HEADER: Final = "Content-Type=application/json-patch+json"

type FieldName = str
type JsonPatchOperation = dict[str, str]


@dataclass(frozen=True, slots=True)
class WorkItemPatch:
    """
    A work item update sent through `az rest`, so a body can be stored as
    Markdown.

    `az boards work-item update` cannot: the format is a separate
    `/multilineFieldsFormat` operation it never sends. Azure DevOps cannot turn
    a Markdown field back into HTML, so the operation is only added for the
    fields listed in `markdown_fields`.
    """

    work_item_id: int
    fields: Mapping[FieldName, str]
    markdown_fields: frozenset[FieldName] = field(default=frozenset())

    @property
    def operations(self) -> tuple[JsonPatchOperation, ...]:
        values = tuple(
            _add(f"/fields/{name}", self._value(name, value))
            for name, value in self.fields.items()
        )
        formats = tuple(
            _add(f"/{FORMATS_KEY}/{name}", MARKDOWN_FORMAT)
            for name in self.fields
            if name in self.markdown_fields
        )
        return values + formats

    def _value(self, name: FieldName, value: str) -> str:
        """Azure DevOps ignores the format operation when the value equals the
        stored one — exactly the case of plain text `az` stored as HTML. Ending
        Markdown with one newline makes the value differ, and renders the same."""
        if name not in self.markdown_fields:
            return value
        return value.rstrip("\n") + "\n"

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


def _add(path: str, value: str) -> JsonPatchOperation:
    return {"op": "add", "path": path, "value": value}
