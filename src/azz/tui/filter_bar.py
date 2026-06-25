from __future__ import annotations

from textual.widgets import Label


class FilterBar(Label):
    DEFAULT_CSS = "FilterBar { height: 1; padding: 0 1; }"

    def update_filters(
        self,
        *,
        include_closed: bool,
        show_others: bool,
        current_timebox_only: bool,
        show_project: bool,
        item_count: int,
        visual_mode: bool = False,
        selection_count: int = 0,
    ) -> None:
        closed = "[green]ON[/green]" if include_closed else "off"
        others = "[green]ON[/green]" if show_others else "off"
        current = "[green]ON[/green]" if current_timebox_only else "off"
        project = "[green]ON[/green]" if show_project else "off"
        if visual_mode:
            mode = f"  [bold cyan]VISUAL {selection_count}[/bold cyan]"
        elif selection_count > 0:
            mode = f"  [cyan]{selection_count} selected[/cyan]"
        else:
            mode = ""
        self.update(
            f"[a] closed: {closed}  ·  [A] others: {others}"
            f"  ·  [c] current: {current}  ·  [p] project: {project}"
            f"  ·  {item_count} items{mode}"
        )
