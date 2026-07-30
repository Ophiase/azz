from azz.core.work_item import WorkItem
from azz.core.work_item.helper import html_to_markdown

from .comparison import iteration_name, normalize_markdown


def remote_advanced(base: WorkItem, later: WorkItem) -> bool:
    """
    Whether the remote moved between two snapshots of the same work item.

    Content, not timestamps: Azure DevOps bumps `System.ChangedDate` for fields
    the plan does not track, and reporting those as a remote change would send
    the user to `azz plan pull` for a rewrite that changes nothing.
    """
    return _signature(base) != _signature(later)


def _signature(work_item: WorkItem) -> tuple[str, ...]:
    """Exactly the fields an intent file can express."""
    return (
        work_item.name,
        str(work_item.state),
        str(work_item.item_type),
        str(work_item.parent_id or ""),
        iteration_name(work_item) or "",
        normalize_markdown(html_to_markdown(work_item.description)),
    )
