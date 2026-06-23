from __future__ import annotations

from textual.widgets import Label


class FilterBar(Label):
    DEFAULT_CSS = "FilterBar { height: 1; padding: 0 1; }"

    def update_filters(
        self,
        *,
        include_closed: bool,
        show_others: bool,
        show_project: bool,
        item_count: int,
    ) -> None:
        closed = "[green]ON[/green]" if include_closed else "off"
        others = "[green]ON[/green]" if show_others else "off"
        project = "[green]ON[/green]" if show_project else "off"
        self.update(
            f"[a] closed: {closed}  ·  [A] others: {others}"
            f"  ·  [p] project: {project}  ·  {item_count} items"
        )
