from collections.abc import Iterable

from azz.core.work_item import WorkItemState

type WIQLQuery = str


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

    fields = ", ".join((
        "[System.Id]",
        "[System.Title]",
        "[System.State]",
        "[System.AssignedTo]",
        "[System.Description]",
        "[System.WorkItemType]",
        "[System.IterationPath]",
        "[System.Parent]",
    ))
    return basic_wiql_query(fields, "workitems", where)


def basic_wiql_query(
    fields: str,
    table: str,
    where: str,
) -> WIQLQuery:
    return f"SELECT {fields} FROM {table} WHERE {where}"  # noqa: S608
