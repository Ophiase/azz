import re
from collections.abc import Mapping
from enum import StrEnum
from typing import Any, Final

from .helper import Markdown, html_to_markdown
from .work_item_type import (
    DESCRIPTION_FIELD,
    REPRO_STEPS_FIELD,
    WorkItemType,
)

FORMATS_KEY: Final = "multilineFieldsFormat"
HTML_TAG: Final = re.compile(r"</?[a-zA-Z][a-zA-Z0-9]*(\s[^<>]*)?/?>")


class DescriptionFormat(StrEnum):
    """How Azure DevOps stores a body field: rendered HTML, or Markdown kept
    verbatim. Converting HTML twice, or Markdown at all, mangles it."""

    HTML = "html"
    MARKDOWN = "markdown"

    @classmethod
    def of_payload(cls, data: Mapping[str, Any]) -> DescriptionFormat:
        """
        The format a work item response declares, else a guess from the text.

        `az boards work-item show` declares it; `az boards query` returns an
        empty mapping even for Markdown items. The rich-text editor always
        emits tags, so a body without any is taken as Markdown.
        """
        field_name = body_field_of(data)
        declared = (data.get(FORMATS_KEY) or {}).get(field_name)
        if declared:
            return cls.MARKDOWN if declared.lower() == cls.MARKDOWN else cls.HTML
        return cls.HTML if _has_tags(body_of(data)) else cls.MARKDOWN

    def to_markdown(self, description: str | None) -> Markdown:
        """Text without a single tag is read as it is, whatever the declared
        format: plain text in an HTML field is what `az` stores, and the
        converter would only escape it."""
        if self is DescriptionFormat.HTML and _has_tags(description):
            return html_to_markdown(description)
        return (description or "").strip()


def body_field_of(data: Mapping[str, Any]) -> str:
    """Repro Steps for a Bug that has any, the Description otherwise — older
    Bugs were written to the Description."""
    fields = data.get("fields") or {}
    is_bug = WorkItemType.type_from_fields(dict(data)) is WorkItemType.BUG
    if is_bug and fields.get(REPRO_STEPS_FIELD):
        return REPRO_STEPS_FIELD
    return DESCRIPTION_FIELD


def body_of(data: Mapping[str, Any]) -> str | None:
    return (data.get("fields") or {}).get(body_field_of(data))


def _has_tags(text: str | None) -> bool:
    return bool(text) and HTML_TAG.search(text or "") is not None
