from collections.abc import Sequence
from dataclasses import replace
from itertools import chain

from azz.core.work_item.priority import Priority

from .display_row import DisplayRow, RowGroup


def priority_bands(groups: Sequence[RowGroup]) -> tuple[DisplayRow, ...]:
    """The groups split into bands by the priority of their top row, most
    urgent first, each band keeping the order given and closing on an
    underline."""
    bands: dict[Priority, list[RowGroup]] = {}
    for group in groups:
        bands.setdefault(Priority.or_lowest(group[0].item.priority), []).append(group)
    ordered = tuple(tuple(chain.from_iterable(bands[key])) for key in sorted(bands))
    closed = tuple(_closed(band) for band in ordered[:-1])
    return tuple(chain(*closed, *ordered[-1:]))


def _closed(band: Sequence[DisplayRow]) -> tuple[DisplayRow, ...]:
    return (*band[:-1], replace(band[-1], closes_band=True))
