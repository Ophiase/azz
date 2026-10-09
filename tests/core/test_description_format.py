"""A Markdown description must be read verbatim: the HTML converter escapes
it, and a pushed escape then shows as literal text on the board."""

from typing import Any

import pytest

from azz.core.work_item.description_format import (
    DESCRIPTION_FIELD,
    FORMATS_KEY,
    DescriptionFormat,
)
from azz.core.work_item_patch import WorkItemPatch

MARKDOWN = "# Plan\n\n- a **bold** step\n- snake_case_name"


def _payload(description: str, declared: str | None = None) -> dict[str, Any]:
    formats = {DESCRIPTION_FIELD: declared} if declared else {}
    return {"id": 1, "fields": {DESCRIPTION_FIELD: description}, FORMATS_KEY: formats}


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        (_payload(MARKDOWN, "markdown"), DescriptionFormat.MARKDOWN),
        (_payload("<div>x</div>", "html"), DescriptionFormat.HTML),
        (_payload("<div>x</div>"), DescriptionFormat.HTML),
        (_payload(MARKDOWN), DescriptionFormat.MARKDOWN),
    ],
)
def test_the_declared_format_wins_and_tags_decide_otherwise(
    payload: dict[str, Any], expected: DescriptionFormat
) -> None:
    assert DescriptionFormat.of_payload(payload) is expected


def test_markdown_is_read_verbatim() -> None:
    assert DescriptionFormat.MARKDOWN.to_markdown(MARKDOWN) == MARKDOWN


def test_html_is_converted() -> None:
    converted = DescriptionFormat.HTML.to_markdown("<p><strong>bold</strong></p>")
    assert converted == "**bold**"


@pytest.mark.parametrize(
    ("description_format", "sets_format"),
    [(DescriptionFormat.MARKDOWN, True), (DescriptionFormat.HTML, False)],
)
def test_only_a_markdown_description_switches_the_field_format(
    description_format: DescriptionFormat, sets_format: bool
) -> None:
    patch = WorkItemPatch(1, {DESCRIPTION_FIELD: MARKDOWN}, description_format)
    paths = {operation["path"] for operation in patch.operations}
    assert (f"/{FORMATS_KEY}/{DESCRIPTION_FIELD}" in paths) is sets_format


def test_a_title_only_patch_never_switches_the_field_format() -> None:
    patch = WorkItemPatch(1, {"System.Title": "x"}, DescriptionFormat.MARKDOWN)
    assert len(patch.operations) == 1
