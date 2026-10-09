"""Priority steps stay on Azure DevOps' 1 to 4 scale, and the threshold filter
never shows an item less urgent than asked."""

from dataclasses import replace

import pytest

from azz.core.work_item.priority import PRIORITY_FIELD, Priority
from azz.core.work_item.work_item_type import WorkItemType
from azz.tui.priority_threshold import PriorityThreshold
from azz.tui.row_tint import RowTint
from tests.conftest import RemoteFactory


@pytest.mark.parametrize(
    ("start", "step", "expected"),
    [
        (Priority.HIGH, -1, Priority.CRITICAL),
        (Priority.CRITICAL, -1, Priority.CRITICAL),
        (Priority.LOW, +1, Priority.LOW),
        (Priority.MEDIUM, +1, Priority.LOW),
    ],
)
def test_a_step_holds_at_the_ends_of_the_scale(
    start: Priority, step: int, expected: Priority
) -> None:
    assert start.shifted(step) is expected


@pytest.mark.parametrize("value", [None, 0, 5, "high"])
def test_an_unknown_value_reads_as_no_priority(value: object) -> None:
    assert Priority.of_fields({PRIORITY_FIELD: value}) is None


@pytest.mark.parametrize(
    ("priority", "shown"),
    [
        (Priority.CRITICAL, True),
        (Priority.HIGH, True),
        (Priority.MEDIUM, False),
        (None, False),
    ],
)
def test_the_threshold_keeps_only_items_at_least_as_urgent(
    remote_item: RemoteFactory, priority: Priority | None, shown: bool
) -> None:
    item = replace(remote_item(), priority=priority)
    assert PriorityThreshold(Priority.HIGH).admits(item) is shown
    assert PriorityThreshold().admits(item)


@pytest.mark.parametrize("item_type", list(WorkItemType))
def test_a_type_label_fits_its_column(item_type: WorkItemType) -> None:
    assert 0 < len(item_type.short_label) <= 4


@pytest.mark.parametrize(
    ("priority", "tint"),
    [
        (Priority.CRITICAL, RowTint.CRITICAL),
        (Priority.HIGH, None),
        (Priority.MEDIUM, RowTint.MINOR),
        (Priority.LOW, RowTint.MINOR),
        (None, None),
    ],
)
def test_only_critical_and_below_high_are_tinted(
    priority: Priority | None, tint: RowTint | None
) -> None:
    assert RowTint.of(priority) is tint
