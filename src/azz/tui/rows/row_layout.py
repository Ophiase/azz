from collections.abc import Sequence
from dataclasses import dataclass, replace
from itertools import chain
from typing import Self

from azz.core.work_item.work_item import WorkItem

from .display_row import DisplayRow, RowGroup
from .priority_bands import priority_bands
from .work_tree import WorkTree


@dataclass(frozen=True, slots=True)
class RowLayout:
    """How the filtered, sorted items are laid out as table rows."""

    tree: bool = True
    split_by_priority: bool = True
    folded: frozenset[int] = frozenset()

    def with_tree_toggled(self) -> Self:
        return replace(self, tree=not self.tree)

    def with_split_toggled(self) -> Self:
        return replace(self, split_by_priority=not self.split_by_priority)

    def with_fold_toggled(self, item_id: int) -> Self:
        return replace(self, folded=self.folded ^ {item_id})

    def with_folded(self, item_ids: frozenset[int]) -> Self:
        return replace(self, folded=item_ids)

    def arrange(
        self, items: Sequence[WorkItem], pool: Sequence[WorkItem]
    ) -> tuple[DisplayRow, ...]:
        """`pool` supplies the tree ancestors that `items` filtered out."""
        groups = self._groups(items, pool)
        if self.split_by_priority:
            return priority_bands(groups)
        return tuple(chain.from_iterable(groups))

    def _groups(
        self, items: Sequence[WorkItem], pool: Sequence[WorkItem]
    ) -> tuple[RowGroup, ...]:
        if self.tree:
            return WorkTree(items, pool, self.folded).groups
        return tuple((DisplayRow(item),) for item in items)
