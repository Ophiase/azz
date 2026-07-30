from collections.abc import Iterable, Sequence
from operator import index
from typing import Final

from azz.core.work_item import WorkItemState

type WIQLQuery = str

WORK_ITEM_TABLE: Final = "workitems"

WORK_ITEM_FIELDS: Final = ", ".join((
    "[System.Id]",
    "[System.Title]",
    "[System.State]",
    "[System.AssignedTo]",
    "[System.Description]",
    "[System.WorkItemType]",
    "[System.IterationPath]",
    "[System.Parent]",
    "[System.ChangedDate]",
))


def build_wiql_query(
    assigned_to: str | None = None,
    states: Iterable[WorkItemState] | None = None,
) -> WIQLQuery:
    def build_state_condition(states: Iterable[WorkItemState]) -> str:
        values = ", ".join(f"'{s.value}'" for s in states)
        return f"[System.State] IN ({values})"

    if states is None:
        states = frozenset({WorkItemState.ACTIVE, WorkItemState.NEW})

    where_clauses = [build_state_condition(states)]

    if assigned_to:
        if assigned_to == "@me":
            where_clauses.append(f"[System.AssignedTo] = {assigned_to}")
        else:
            where_clauses.append(f"[System.AssignedTo] = '{assigned_to}'")

    where = " AND ".join(where_clauses)

    return basic_wiql_query(WORK_ITEM_FIELDS, WORK_ITEM_TABLE, where)


def build_id_query(work_item_ids: Sequence[int]) -> WIQLQuery:
    """
    Every listed item, whatever its state, assignee or timebox.

    Deliberately unfiltered: it exists to resolve ids a local plan already
    references, and a Closed item assigned to someone else must still resolve.
    """
    return basic_wiql_query(
        WORK_ITEM_FIELDS, WORK_ITEM_TABLE, _identifier_condition(work_item_ids)
    )


def basic_wiql_query(
    fields: str,
    table: str,
    where: str,
) -> WIQLQuery:
    return f"SELECT {fields} FROM {table} WHERE {where}"  # noqa: S608


def _identifier_condition(work_item_ids: Sequence[int]) -> str:
    if not work_item_ids:
        raise ValueError("an id query needs at least one work item id")
    values = ", ".join(str(_validated_identifier(one)) for one in work_item_ids)
    return f"[System.Id] IN ({values})"


def _validated_identifier(work_item_id: int) -> int:
    """Integers only — this value is interpolated straight into the query."""
    try:
        return index(work_item_id)
    except TypeError as error:
        raise ValueError(
            f"work item id must be an integer: {work_item_id!r}"
        ) from error
