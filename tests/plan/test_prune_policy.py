"""Prune deletes local files, so what counts as inactive must be exactly what
was asked for — Closed by default, each option widening it."""

from dataclasses import replace

import pytest

from azz.core.iteration_path import IterationPath
from azz.core.work_item import WorkItemState
from azz.plan.models import PrunePolicy
from tests.conftest import RemoteFactory

CURRENT = "Project\\TimeBox 2"
CURRENT_TIMEBOX = PrunePolicy(current_timebox=IterationPath(CURRENT, normalized=True))
MINE = PrunePolicy(owner="Me")


def test_by_default_only_closed_items_are_inactive(
    remote_item: RemoteFactory,
) -> None:
    policy = PrunePolicy()
    assert policy.is_inactive(remote_item(state=WorkItemState.CLOSED))
    assert not policy.is_inactive(remote_item(iteration_path="Project\\TimeBox 1"))


@pytest.mark.parametrize(
    ("iteration_path", "inactive"),
    [(CURRENT, False), ("Project\\TimeBox 1", True), (None, True)],
)
def test_outside_the_current_timebox(
    remote_item: RemoteFactory, iteration_path: str | None, inactive: bool
) -> None:
    item = remote_item(iteration_path=iteration_path)
    assert CURRENT_TIMEBOX.is_inactive(item) is inactive


@pytest.mark.parametrize(
    ("assignee", "inactive"), [("Me", False), ("Someone", True), (None, True)]
)
def test_not_assigned_to_me(
    remote_item: RemoteFactory, assignee: str | None, inactive: bool
) -> None:
    item = replace(remote_item(), assigned_to=assignee)
    assert MINE.is_inactive(item) is inactive
