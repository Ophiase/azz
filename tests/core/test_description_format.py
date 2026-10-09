"""A Markdown body must be read verbatim and written with its format: the HTML
converter escapes Markdown, and a body Azure DevOps keeps as HTML shows its
asterisks and backticks literally on the board."""

from typing import Any

import pytest

from azz.core.work_item.description_format import (
    FORMATS_KEY,
    DescriptionFormat,
    body_field_of,
)
from azz.core.work_item.work_item_type import (
    DESCRIPTION_FIELD,
    REPRO_STEPS_FIELD,
    WorkItemType,
)
from azz.core.work_item_patch import WorkItemPatch

MARKDOWN = "# Plan\n\n- a **bold** step\n- `snake_case_name`"


def _payload(
    description: str, declared: str | None = None, item_type: str = "Task"
) -> dict[str, Any]:
    formats = {DESCRIPTION_FIELD: declared} if declared else {}
    fields = {DESCRIPTION_FIELD: description, "System.WorkItemType": item_type}
    return {"id": 1, "fields": fields, FORMATS_KEY: formats}


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


@pytest.mark.parametrize("description_format", list(DescriptionFormat))
def test_text_without_tags_reads_verbatim_whatever_the_format(
    description_format: DescriptionFormat,
) -> None:
    assert description_format.to_markdown(MARKDOWN) == MARKDOWN


def test_html_is_converted() -> None:
    converted = DescriptionFormat.HTML.to_markdown("<p><strong>bold</strong></p>")
    assert converted == "**bold**"


def test_a_bug_reads_its_repro_steps_and_falls_back_to_the_description() -> None:
    older_bug = _payload("body", item_type="Bug")
    assert body_field_of(older_bug) == DESCRIPTION_FIELD
    older_bug["fields"][REPRO_STEPS_FIELD] = "steps"
    assert body_field_of(older_bug) == REPRO_STEPS_FIELD


@pytest.mark.parametrize("item_type", list(WorkItemType))
def test_only_a_bug_writes_its_body_to_repro_steps(item_type: WorkItemType) -> None:
    expected = REPRO_STEPS_FIELD if item_type is WorkItemType.BUG else DESCRIPTION_FIELD
    assert item_type.body_field == expected


def test_a_markdown_field_gets_its_format_and_a_value_that_differs() -> None:
    """Azure DevOps ignores the format when the value equals the stored one."""
    patch = WorkItemPatch(
        1,
        {"System.Title": "x", DESCRIPTION_FIELD: MARKDOWN},
        frozenset({DESCRIPTION_FIELD}),
    )
    by_path = {operation["path"]: operation["value"] for operation in patch.operations}
    assert by_path[f"/{FORMATS_KEY}/{DESCRIPTION_FIELD}"] == "Markdown"
    assert by_path[f"/fields/{DESCRIPTION_FIELD}"] == MARKDOWN + "\n"
    assert by_path["/fields/System.Title"] == "x"
    assert f"/{FORMATS_KEY}/System.Title" not in by_path


def test_a_field_not_declared_markdown_is_sent_untouched() -> None:
    patch = WorkItemPatch(1, {DESCRIPTION_FIELD: MARKDOWN})
    assert patch.operations == (
        {"op": "add", "path": f"/fields/{DESCRIPTION_FIELD}", "value": MARKDOWN},
    )
