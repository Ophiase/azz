import re

from azz.core.work_item.work_item import WorkItem


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
