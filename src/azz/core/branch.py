import re
from typing import Final

from azz.core.work_item.work_item import WorkItem

WORK_ITEM_ID_IN_BRANCH: Final = re.compile(r"^(?:[^/]+/)?(?:tb-\d+-)?(\d+)(?:-|$)")


def work_item_id_from_branch(name: str) -> int | None:
    """The id `branch_name` put in a branch: `dev/tb-46-8049-fix-x` -> 8049."""
    match = WORK_ITEM_ID_IN_BRANCH.match(name)
    return int(match.group(1)) if match else None


def branch_name(work_item: WorkItem, count: int = 5) -> str:
    """Generate a branch name: dev/tb-<TB>-<ID>-<word1>-<word2>-<word3>"""
    timebox = (
        work_item.iteration_path.optional_number
        if work_item.iteration_path
        else None
    )
    item_id = work_item.id

    name = work_item.name
    if work_item.name_project:
        prefix = f"[{work_item.name_project}]"
        name = name[len(prefix):]
        name = re.sub(r"^[\s\-]+", "", name)

    words = re.findall(r"[a-zA-Z]+", name)[:count]
    words_part = "-".join(w.lower() for w in words)

    tb_part = f"tb-{timebox}-" if timebox is not None else ""
    return f"dev/{tb_part}{item_id}-{words_part}"
