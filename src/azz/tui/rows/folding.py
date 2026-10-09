from collections.abc import Sequence

from .display_row import DisplayRow


def fold_target(rows: Sequence[DisplayRow], index: int) -> int | None:
    """The item a fold at `index` acts on: the row itself when it has
    children, else its parent on screen, else None."""
    row = rows[index]
    following = rows[index + 1] if index + 1 < len(rows) else None
    has_children = following is not None and following.item.parent_id == row.item.id
    if has_children or row.folded_descendants:
        return row.item.id
    shown = frozenset(other.item.id for other in rows)
    return row.item.parent_id if row.item.parent_id in shown else None


def parent_ids(rows: Sequence[DisplayRow]) -> frozenset[int]:
    """Every row on screen with at least one child on screen."""
    shown = frozenset(row.item.id for row in rows)
    return frozenset(
        row.item.parent_id for row in rows if row.item.parent_id in shown
    )
