from azz.core.work_item import WorkItem, WorkItemState
from azz.core.work_item.priority import Priority
from azz.tui.rows import RowLayout, fold_target


def _item(
    item_id: int,
    parent_id: int | None = None,
    priority: Priority | None = None,
    state: WorkItemState = WorkItemState.NEW,
) -> WorkItem:
    return WorkItem(
        id=item_id,
        name=f"item {item_id}",
        state=state,
        project="Project",
        parent_id=parent_id,
        priority=priority,
    )


def test_children_nest_under_their_parent_in_the_given_order() -> None:
    items = (_item(3, parent_id=1), _item(1), _item(2, parent_id=1), _item(4))
    rows = RowLayout(split_by_priority=False).arrange(items, pool=items)
    assert [(row.item.id, row.branch) for row in rows] == [
        (1, ""),
        (3, "├─ "),
        (2, "└─ "),
        (4, ""),
    ]


def test_a_filtered_out_ancestor_is_borrowed_from_the_pool() -> None:
    story = _item(1)
    task = _item(2, parent_id=1)
    rows = RowLayout(split_by_priority=False).arrange((task,), pool=(story, task))
    assert [(row.item.id, row.outside_filters) for row in rows] == [
        (1, True),
        (2, False),
    ]


def test_bands_keep_the_order_and_close_on_their_last_row() -> None:
    items = (
        _item(1, priority=Priority.HIGH),
        _item(2, priority=Priority.CRITICAL),
        _item(3, priority=Priority.HIGH),
    )
    rows = RowLayout(tree=False).arrange(items, pool=items)
    assert [(row.item.id, row.closes_band) for row in rows] == [
        (2, True),
        (1, False),
        (3, False),
    ]


def test_in_a_tree_a_subtree_follows_the_band_of_its_root() -> None:
    items = (
        _item(1, priority=Priority.LOW),
        _item(2, parent_id=1, priority=Priority.CRITICAL),
        _item(3, priority=Priority.HIGH),
    )
    rows = RowLayout().arrange(items, pool=items)
    assert [row.item.id for row in rows] == [3, 1, 2]


def _deep_tree() -> tuple[WorkItem, ...]:
    """Epic 1 > story 2 > task 3 > subtask 4, and task 5 under story 2."""
    return (
        _item(1),
        _item(2, parent_id=1),
        _item(3, parent_id=2),
        _item(4, parent_id=3),
        _item(5, parent_id=2),
    )


def test_a_fold_hides_every_level_below_and_counts_it() -> None:
    items = _deep_tree()
    rows = RowLayout(folded=frozenset({2})).arrange(items, pool=items)
    assert [(row.item.id, row.folded_descendants) for row in rows] == [
        (1, 0),
        (2, 3),
    ]


def test_a_nested_fold_survives_unfolding_its_ancestor() -> None:
    items = _deep_tree()
    layout = RowLayout(folded=frozenset({2, 3})).with_fold_toggled(2)
    rows = layout.arrange(items, pool=items)
    assert [(row.item.id, row.folded_descendants) for row in rows] == [
        (1, 0),
        (2, 0),
        (3, 1),
        (5, 0),
    ]


def test_a_fold_on_a_leaf_targets_its_parent() -> None:
    items = _deep_tree()
    rows = RowLayout().arrange(items, pool=items)
    targets = [fold_target(rows, index) for index in range(len(rows))]
    assert targets == [1, 2, 3, 3, 2]


def test_a_lone_top_level_row_has_nothing_to_fold() -> None:
    items = (_item(1),)
    assert fold_target(RowLayout().arrange(items, pool=items), 0) is None


def test_closed_groups_sink_below_every_priority_band() -> None:
    closed = WorkItemState.CLOSED
    items = (
        _item(1, priority=Priority.CRITICAL, state=closed),
        _item(2, priority=Priority.LOW),
        _item(3, parent_id=2, state=closed),
        _item(4, priority=Priority.HIGH, state=closed),
    )
    rows = RowLayout().arrange(items, pool=items)
    assert [(row.item.id, row.closes_band) for row in rows] == [
        (2, False),
        (3, True),
        (1, False),
        (4, False),
    ]
