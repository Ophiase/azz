from azz.core.work_item import WorkItem

from .comparison import iteration_name
from .frontmatter import DELIMITER, quote_scalar


def render_intent_file(work_item: WorkItem) -> str:
    """A remote work item as a `.azz/tasks/*.md` intent file."""
    lines = [DELIMITER, *_frontmatter_lines(work_item), DELIMITER, ""]
    body = work_item.markdown_description
    if body:
        lines.extend([body, ""])
    return "\n".join(lines)


def _frontmatter_lines(work_item: WorkItem) -> list[str]:
    entries = (
        ("item_id", work_item.id),
        ("title", work_item.name),
        ("type", work_item.item_type),
        ("state", work_item.state),
        ("parent", work_item.parent_id),
        ("iteration", iteration_name(work_item)),
        ("priority", work_item.priority),
    )
    return [
        f"{key}: {quote_scalar(str(value))}"
        for key, value in entries
        if value is not None
    ]
