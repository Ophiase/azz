from azz.core.work_item import WorkItem, WorkItemFilter

type DisplayName = str


class AssigneeFilter(WorkItemFilter):
    """
    Keeps the items belonging to one person, cache-style.

    A cached payload often has no `System.AssignedTo` at all — either the
    remote query already restricted the assignee, or the item was created
    locally. Such an item is treated as the owner's rather than dropped,
    which mirrors what `az boards query --assigned-to` would have returned.
    """

    def __init__(self, owner: DisplayName | None) -> None:
        self.owner = owner

    def __call__(self, task: WorkItem) -> bool:
        if task.assigned_to is None or self.owner is None:
            return True
        return task.assigned_to == self.owner
