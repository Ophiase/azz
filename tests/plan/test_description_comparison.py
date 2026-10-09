"""A Markdown description compares verbatim, and a file pulled before its
format was known — escaped by the HTML converter — still holds no edit."""

from dataclasses import replace
from pathlib import Path

from azz.core.work_item import WorkItem
from azz.core.work_item.description_format import DescriptionFormat
from azz.core.work_item.helper import html_to_markdown
from azz.plan.comparison import field_diffs
from azz.plan.models import LocalItem
from tests.conftest import RemoteFactory

MARKDOWN = "- a **bold** step\n- snake_case_name"


def _markdown_remote(remote_item: RemoteFactory) -> WorkItem:
    return replace(
        remote_item(description=MARKDOWN),
        description_format=DescriptionFormat.MARKDOWN,
    )


def test_a_verbatim_copy_is_in_sync(remote_item: RemoteFactory) -> None:
    local = LocalItem(path=Path("item.md"), description=MARKDOWN)
    assert field_diffs(local, _markdown_remote(remote_item)) == ()


def test_an_escaped_copy_from_an_older_pull_is_in_sync(
    remote_item: RemoteFactory,
) -> None:
    escaped = html_to_markdown(MARKDOWN)
    assert escaped != MARKDOWN
    local = LocalItem(path=Path("item.md"), description=escaped)
    assert field_diffs(local, _markdown_remote(remote_item)) == ()


def test_a_real_edit_is_still_a_difference(remote_item: RemoteFactory) -> None:
    local = LocalItem(path=Path("item.md"), description=MARKDOWN + "\n- new step")
    (diff,) = field_diffs(local, _markdown_remote(remote_item))
    assert diff.field_name == "description"
