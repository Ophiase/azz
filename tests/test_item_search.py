"""`/` in the TUI: typing an id must land on that item, whatever the titles."""

from azz.tui.item_search import ItemSearch
from tests.conftest import RemoteFactory


def test_an_empty_query_keeps_every_item_in_order(
    remote_item: RemoteFactory,
) -> None:
    items = (remote_item(item_id=2), remote_item(item_id=1))
    assert ItemSearch(items).matches("  ") == items


def test_an_id_prefix_ranks_first(remote_item: RemoteFactory) -> None:
    items = (
        remote_item(item_id=1, name="Fix 8040 regression"),
        remote_item(item_id=8040, name="Unrelated"),
    )
    assert ItemSearch(items).matches("8040")[0].id == 8040


def test_a_title_fragment_filters(remote_item: RemoteFactory) -> None:
    items = (
        remote_item(item_id=1, name="Langfuse trace"),
        remote_item(item_id=2, name="Minio switch"),
    )
    assert [item.id for item in ItemSearch(items).matches("langf")] == [1]
