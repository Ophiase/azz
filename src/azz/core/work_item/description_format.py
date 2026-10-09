import re
from collections.abc import Mapping
from enum import StrEnum
from typing import Any, Final

from .helper import Markdown, html_to_markdown

DESCRIPTION_FIELD: Final = "System.Description"
FORMATS_KEY: Final = "multilineFieldsFormat"
HTML_TAG: Final = re.compile(r"</?[a-zA-Z][a-zA-Z0-9]*(\s[^<>]*)?/?>")


class DescriptionFormat(StrEnum):
    """How Azure DevOps stores a description: rendered HTML, or Markdown kept
    verbatim. Converting HTML twice, or Markdown at all, mangles it."""

    HTML = "html"
    MARKDOWN = "markdown"

    @classmethod
    def of_payload(cls, data: Mapping[str, Any]) -> DescriptionFormat:
        """
        The format a work item response declares, else a guess from the text.

        `az boards work-item show` declares it; `az boards query` returns an
        empty mapping even for Markdown items. The rich-text editor always
        emits tags, so a description without any is taken as Markdown.
        """
        declared = (data.get(FORMATS_KEY) or {}).get(DESCRIPTION_FIELD)
        if declared:
            return cls.MARKDOWN if declared.lower() == cls.MARKDOWN else cls.HTML
        description = (data.get("fields") or {}).get(DESCRIPTION_FIELD) or ""
        return cls.HTML if HTML_TAG.search(description) else cls.MARKDOWN

    def to_markdown(self, description: str | None) -> Markdown:
        if self is DescriptionFormat.MARKDOWN:
            return (description or "").strip()
        return html_to_markdown(description)
