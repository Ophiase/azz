from dataclasses import dataclass

from rich.style import Style

from azz.core.work_item.work_item import WorkItem

type RowGroup = tuple[DisplayRow, ...]
"""A top-level row followed by every row nested under it."""


@dataclass(frozen=True, slots=True)
class DisplayRow:
    """A work item as it sits in the table."""

    item: WorkItem
    branch: str = ""
    outside_filters: bool = False
    closes_band: bool = False
    folded_descendants: int = 0

    @property
    def style(self) -> Style:
        """Dim when only shown as a tree ancestor; underlined at a band's end."""
        return Style(
            dim=self.outside_filters or None,
            underline=self.closes_band or None,
        )
