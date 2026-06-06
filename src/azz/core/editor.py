import subprocess  # noqa: S404
import tempfile
from dataclasses import replace
from pathlib import Path

from .work_item import WorkItem


def edit_in_editor(content: str, editor="nvim") -> str:
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        path = Path(f.name)
        path.write_text(content)

    subprocess.run([editor, str(path)])  # noqa: S603

    return path.read_text()


def edit_task_content_in_editor(task: WorkItem) -> WorkItem:
    content = task.description or ""
    return replace(task, description=edit_in_editor(content))


def edit_task_title_in_editor(task: WorkItem) -> WorkItem:
    new_name = edit_in_editor(task.name)
    return replace(task, name=new_name.strip())


def edit_work_item_in_editor(work_item: WorkItem, edit_title: bool) -> WorkItem:
    if edit_title:
        return edit_task_title_in_editor(work_item)
    return edit_task_content_in_editor(work_item)
