from collections.abc import Sequence
from dataclasses import replace
from itertools import chain

from azz.core.work_item.priority import Priority
from azz.core.work_item.work_item_state import WorkItemState

from .display_row import DisplayRow, RowGroup

type Band = Priority | None
"""A priority, or None for the groups with nothing left open."""


def priority_bands(groups: Sequence[RowGroup]) -> tuple[DisplayRow, ...]:
    """The groups split into bands by the priority of their top row, most
    urgent first and fully Closed groups last, each band keeping the order
    given and closing on an underline."""
    bands: dict[Band, list[RowGroup]] = {}
    for group in groups:
        bands.setdefault(_band_of(group), []).append(group)
    ordered = tuple(
        tuple(chain.from_iterable(bands[band]))
        for band in sorted(bands, key=_band_order)
    )
    closed = tuple(_closed(band) for band in ordered[:-1])
    return tuple(chain(*closed, *ordered[-1:]))


def _band_of(group: RowGroup) -> Band:
    if all(row.item.state is WorkItemState.CLOSED for row in group):
        return None
    return Priority.or_lowest(group[0].item.priority)


def _band_order(band: Band) -> tuple[bool, int]:
    return (band is None, band or 0)


def _closed(band: Sequence[DisplayRow]) -> tuple[DisplayRow, ...]:
    return (*band[:-1], replace(band[-1], closes_band=True))
