from dataclasses import dataclass
from typing import Final

from textual.fuzzy import Matcher

from azz.core.work_item.work_item import WorkItem

ID_PREFIX_BONUS: Final = 1.0
"""Above any fuzzy score, which tops out at 1: typing an id finds that item."""


@dataclass(frozen=True, slots=True)
class ItemSearch:
    """Fuzzy-ranks work items by id and title, best match first."""

    items: tuple[WorkItem, ...]

    def matches(self, query: str) -> tuple[WorkItem, ...]:
        """Every item for an empty query, in the given order; otherwise only
        the items that match, best first."""
        stripped = query.strip()
        if not stripped:
            return self.items
        matcher = Matcher(stripped)
        scored = ((self._score(matcher, item), item) for item in self.items)
        ranked = sorted(
            (pair for pair in scored if pair[0] > 0),
            key=lambda pair: pair[0],
            reverse=True,
        )
        return tuple(item for _, item in ranked)

    @staticmethod
    def _score(matcher: Matcher, item: WorkItem) -> float:
        bonus = ID_PREFIX_BONUS if str(item.id).startswith(matcher.query) else 0.0
        return bonus + matcher.match(search_label(item))


def search_label(item: WorkItem) -> str:
    return f"{item.id} {item.stripped_name}"
