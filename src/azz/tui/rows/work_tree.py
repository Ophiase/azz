from collections.abc import Iterator, Mapping, Sequence
from typing import Final

from azz.core.work_item.work_item import WorkItem

from .display_row import DisplayRow, RowGroup

_MIDDLE_CHILD: Final = "├─ "
_LAST_CHILD: Final = "└─ "
_NESTED_LEAD: Final[Mapping[str, str]] = {
    "": "",
    _MIDDLE_CHILD: "│  ",
    _LAST_CHILD: "   ",
}


class WorkTree:
    """
    Items nested under their parents, siblings kept in the order given.

    A parent missing from `items` is borrowed from `pool` and flagged
    `outside_filters`, so a task keeps its user story even when the story sits
    in another timebox. The descendants of a `folded` item are left out.
    """

    def __init__(
        self,
        items: Sequence[WorkItem],
        pool: Sequence[WorkItem],
        folded: frozenset[int] = frozenset(),
    ) -> None:
        self._matching_ids = frozenset(item.id for item in items)
        self._folded = folded
        nodes = _with_ancestors(items, {item.id: item for item in pool})
        self._children: dict[int | None, list[WorkItem]] = {}
        for node in nodes.values():
            parent_id = node.parent_id if node.parent_id in nodes else None
            self._children.setdefault(parent_id, []).append(node)

    @property
    def groups(self) -> tuple[RowGroup, ...]:
        return tuple(
            tuple(self._rows(root, lead="", connector=""))
            for root in self._children.get(None, ())
        )

    def _rows(self, node: WorkItem, lead: str, connector: str) -> Iterator[DisplayRow]:
        folded = node.id in self._folded
        yield DisplayRow(
            node,
            branch=lead + connector,
            outside_filters=node.id not in self._matching_ids,
            folded_descendants=self._descendant_count(node.id) if folded else 0,
        )
        if folded:
            return
        children = self._children.get(node.id, ())
        nested_lead = lead + _NESTED_LEAD[connector]
        for position, child in enumerate(children, start=1):
            is_last = position == len(children)
            child_connector = _LAST_CHILD if is_last else _MIDDLE_CHILD
            yield from self._rows(child, nested_lead, child_connector)

    def _descendant_count(self, node_id: int) -> int:
        return sum(
            1 + self._descendant_count(child.id)
            for child in self._children.get(node_id, ())
        )


def _with_ancestors(
    items: Sequence[WorkItem], pool: Mapping[int, WorkItem]
) -> dict[int, WorkItem]:
    """The items in order, each followed by those of its ancestors that only
    `pool` holds."""
    matching = {item.id: item for item in items}
    nodes: dict[int, WorkItem] = {}
    for item in items:
        nodes[item.id] = item
        parent_id = item.parent_id
        while (
            parent_id in pool and parent_id not in matching and parent_id not in nodes
        ):
            nodes[parent_id] = pool[parent_id]
            parent_id = nodes[parent_id].parent_id
    return nodes
