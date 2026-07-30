from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Annotated

import typer
from rich import print

from azz.core.engine import Engine
from azz.core.work_item import WorkItem, WorkItemState
from azz.plan import (
    Applier,
    Changeset,
    Fetcher,
    IntentFileError,
    LocalItem,
    compute_changeset,
    find_plan_root,
    initialize_plan_directory,
    intent_file_paths,
    parse_intent_files,
    tasks_directory,
)
from azz.plan.renderer import (
    render_changeset,
    render_fetch_outcome,
    render_fetch_summary,
    render_outcome,
    render_prompt,
    render_summary,
)

ALL_STATES = frozenset({
    WorkItemState.ACTIVE,
    WorkItemState.NEW,
    WorkItemState.RESOLVED,
    WorkItemState.CLOSED,
})


def register(app: typer.Typer, engine: Engine) -> None:
    plan_app = typer.Typer(
        help="Manage local task intents in .azz/tasks and sync them to the remote."
    )

    def init() -> None:
        """Create the local, gitignored .azz plan directory."""
        existing = find_plan_root()
        plan_root = initialize_plan_directory().resolve()
        if existing is not None and existing != plan_root:
            print(f"[yellow]Note: a plan directory already exists at {existing}")
        print(f"[green]Ready:[/green] {tasks_directory(plan_root)}")
        print("Pull existing work items with [bold]azz plan fetch[/bold]")

    def fetch(
        work_item_ids: Annotated[list[int] | None, typer.Argument()] = None,
        limit: int = typer.Option(20, "--limit", "-l"),
        include_closed: bool = typer.Option(False, "--all", "-a"),
        current_timebox_only: bool = typer.Option(False, "--current-timebox", "-c"),
        force: bool = typer.Option(False, "--force", "-f"),
    ) -> None:
        """Mirror remote work items into .azz/tasks as Markdown intent files."""
        plan_root = _require_plan_root()
        remote_items = _select_remote_items(
            engine, work_item_ids, limit, include_closed, current_timebox_only
        )
        if not remote_items:
            print("[yellow]No work items matched[/yellow]")
            return

        fetcher = Fetcher(plan_root, _load_local_items(plan_root))
        outcomes = tuple(fetcher.fetch(item, force=force) for item in remote_items)
        for outcome in outcomes:
            print(render_fetch_outcome(outcome))
        print(render_fetch_summary(outcomes))

    def status() -> None:
        """Show the drift between .azz/tasks and the remote (read-only)."""
        _report(_load_changeset(engine))

    def resolve(
        assume_yes: bool = typer.Option(False, "--yes", "-y"),
        dry_run: bool = typer.Option(False, "--dry-run"),
    ) -> None:
        """Apply local intents to the remote, confirming each change."""
        changeset = _load_changeset(engine)
        if dry_run:
            _report(changeset)
            return
        _apply(changeset, engine, assume_yes)

    plan_app.command("init")(init)
    plan_app.command("fetch")(fetch)
    plan_app.command("status")(status)
    plan_app.command("resolve")(resolve)
    app.add_typer(plan_app, name="plan")


def _require_plan_root() -> Path:
    plan_root = find_plan_root()
    if plan_root is None:
        print("[red]No .azz directory found — run [bold]azz plan init[/bold] first")
        raise typer.Exit(code=1)
    return plan_root


def _load_local_items(plan_root: Path) -> tuple[LocalItem, ...]:
    try:
        return parse_intent_files(intent_file_paths(plan_root))
    except IntentFileError as error:
        print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error


def _select_remote_items(
    engine: Engine,
    work_item_ids: Sequence[int] | None,
    limit: int,
    include_closed: bool,
    current_timebox_only: bool,
) -> tuple[WorkItem, ...]:
    if work_item_ids:
        return tuple(engine.get_workitem(item_id) for item_id in work_item_ids)
    items = engine.list_work_items(
        states=ALL_STATES if include_closed else None,
        current_timebox_only=current_timebox_only,
    )
    return tuple(sorted(items, key=_changed_timestamp)[-limit:])


def _changed_timestamp(work_item: WorkItem) -> float:
    return work_item.changed_date.timestamp() if work_item.changed_date else 0.0


def _report(changeset: Changeset) -> None:
    print(render_changeset(changeset))
    print(render_summary(changeset))


def _load_changeset(engine: Engine) -> Changeset:
    plan_root = _require_plan_root()
    paths = intent_file_paths(plan_root)
    if not paths:
        print(f"[yellow]No intent files in {tasks_directory(plan_root)}[/yellow]")
        print("Pull existing work items with [bold]azz plan fetch[/bold]")
        raise typer.Exit()
    return compute_changeset(_load_local_items(plan_root), engine)


def _apply(changeset: Changeset, engine: Engine, assume_yes: bool) -> None:
    applicable = changeset.applicable
    if not applicable:
        print("[green]Nothing to resolve[/green]")
        return

    applier = Applier(engine)
    for change in applicable:
        if not assume_yes and not typer.confirm(render_prompt(change)):
            print("  [grey50]skipped[/grey50]")
            continue
        print(render_outcome(applier.apply(change)))
