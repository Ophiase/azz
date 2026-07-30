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
    Change,
    Changeset,
    FetchClock,
    Fetcher,
    IntentFileError,
    LocalItem,
    Puller,
    PullOutcome,
    SyncInspector,
    SyncReport,
    cache_directory,
    compute_changeset,
    find_plan_root,
    initialize_plan_directory,
    intent_file_paths,
    parse_intent_files,
    prunable_changes,
    prune_intent_file,
    tasks_directory,
)
from azz.plan.renderer import (
    render_changeset,
    render_fetch_outcome,
    render_fetch_summary,
    render_outcome,
    render_prompt,
    render_prune_candidate,
    render_prune_prompt,
    render_prune_summary,
    render_summary,
)
from azz.plan.sync_renderer import (
    render_cache_age,
    render_pull_outcome,
    render_pull_summary,
    render_sync_notices,
    render_sync_report,
    render_sync_summary,
)

ALL_STATES = frozenset({
    WorkItemState.ACTIVE,
    WorkItemState.NEW,
    WorkItemState.RESOLVED,
    WorkItemState.CLOSED,
})

DEFAULT_FETCH_LIMIT = 20
UNLIMITED = 0
LIMIT_HELP = "How many of the most recently changed items to fetch (0 = all)."


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
        limit: int = typer.Option(
            DEFAULT_FETCH_LIMIT, "--limit", "-l", help=LIMIT_HELP
        ),
        include_closed: bool = typer.Option(False, "--all", "-a"),
        current_timebox_only: bool = typer.Option(False, "--current-timebox", "-c"),
    ) -> None:
        """Record remote work items in .azz/cache. Does not touch .azz/tasks.

        Like `git fetch`: it updates our knowledge of the remote and leaves the
        working tree alone. Run `azz plan pull` to write the files.

        `--limit 0` lifts the cap: combined with `--all`, it archives every
        work item `azz list -a` reports, Closed ones included.
        """
        plan_root = _require_plan_root()
        remote_items = _select_remote_items(
            engine, work_item_ids, limit, include_closed, current_timebox_only
        )
        if not remote_items:
            print("[yellow]No work items matched[/yellow]")
            return

        fetcher = Fetcher(plan_root)
        outcomes = tuple(fetcher.fetch(item) for item in remote_items)
        _cache_timeboxes(fetcher, engine)
        fetcher.record_fetch_time()
        for outcome in outcomes:
            print(render_fetch_outcome(outcome))
        print(render_fetch_summary(outcomes))
        print("Write the files with [bold]azz plan pull[/bold]")

    def status() -> None:
        """Compare .azz/tasks with .azz/cache. Offline: never calls the remote.

        Three-way, so local edits, remote edits and genuine conflicts are told
        apart. Run `azz plan fetch` to refresh what it compares against.
        """
        _report_sync(_load_sync_report())

    def pull(
        force: bool = typer.Option(
            False, "--force", "-f", help="Overwrite local changes with the cache."
        ),
        dry_run: bool = typer.Option(False, "--dry-run"),
    ) -> None:
        """Write .azz/cache into .azz/tasks, fast-forward only. Offline.

        Files whose local side is untouched are replaced by the fetched state.
        Files where both sides moved are refused and listed — resolve them by
        hand, or take the remote with `--force`.
        """
        plan_root = _require_plan_root()
        report = _load_sync_report()
        if dry_run:
            _report_sync(report)
            return
        _pull(Puller(plan_root).pull(report, force=force))

    def push(
        assume_yes: bool = typer.Option(False, "--yes", "-y"),
        dry_run: bool = typer.Option(False, "--dry-run"),
    ) -> None:
        """Apply local intents to the remote, confirming each change."""
        changeset = _load_changeset(engine)
        if dry_run:
            _report(changeset)
            return
        _apply(changeset, engine, assume_yes)

    def prune(
        assume_yes: bool = typer.Option(False, "--yes", "-y"),
        dry_run: bool = typer.Option(False, "--dry-run"),
    ) -> None:
        """Delete the local files of Closed items that are in sync.

        Local only: the Azure DevOps work items are never touched. Files with
        drift, files without an item_id, and files whose item is gone from the
        remote are always kept.
        """
        _prune(prunable_changes(_load_changeset(engine)), assume_yes, dry_run)

    plan_app.command("init")(init)
    plan_app.command("fetch")(fetch)
    plan_app.command("pull")(pull)
    plan_app.command("status")(status)
    plan_app.command("push")(push)
    plan_app.command("prune")(prune)
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


def _cache_timeboxes(fetcher: Fetcher, engine: Engine) -> None:
    """Best effort — a plan fetch is about work items, not iterations."""
    try:
        fetcher.record_timeboxes(engine.list_timeboxes())
    except (RuntimeError, OSError) as error:
        print(f"[yellow]Could not cache the timebox list: {error}[/yellow]")


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
    return _most_recent(items, limit)


def _most_recent(items: Sequence[WorkItem], limit: int) -> tuple[WorkItem, ...]:
    ordered = tuple(sorted(items, key=_changed_timestamp))
    return ordered if limit <= UNLIMITED else ordered[-limit:]


def _changed_timestamp(work_item: WorkItem) -> float:
    return work_item.changed_date.timestamp() if work_item.changed_date else 0.0


def _report(changeset: Changeset) -> None:
    print(render_changeset(changeset))
    print(render_summary(changeset))


def _report_sync(report: SyncReport) -> None:
    print(render_sync_report(report))
    print(render_sync_summary(report))
    notices = render_sync_notices(report)
    if notices:
        print(notices)


def _pull(outcomes: Sequence[PullOutcome]) -> None:
    for outcome in outcomes:
        if not outcome.status.is_quiet:
            print(render_pull_outcome(outcome))
    print(render_pull_summary(outcomes))


def _load_sync_report() -> SyncReport:
    plan_root = _require_plan_root()
    local_items = _load_local_items(plan_root)
    report = SyncInspector(plan_root).inspect(local_items)
    if not local_items and not report.incoming:
        print(f"[yellow]No intent files in {tasks_directory(plan_root)}[/yellow]")
        print("Record the remote with [bold]azz plan fetch[/bold]")
        raise typer.Exit()
    clock = FetchClock(cache_directory(plan_root))
    print(render_cache_age(clock.age, clock.is_stale))
    return report


def _load_changeset(engine: Engine) -> Changeset:
    plan_root = _require_plan_root()
    paths = intent_file_paths(plan_root)
    if not paths:
        print(f"[yellow]No intent files in {tasks_directory(plan_root)}[/yellow]")
        print("Record the remote with [bold]azz plan fetch[/bold]")
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


def _prune(
    candidates: Sequence[Change], assume_yes: bool, dry_run: bool
) -> None:
    if not candidates:
        print("[green]Nothing to prune[/green]")
        return

    for change in candidates:
        print(render_prune_candidate(change))
    print(render_prune_summary(candidates))

    if dry_run:
        return
    if not assume_yes and not typer.confirm(render_prune_prompt(candidates)):
        print("[grey50]skipped[/grey50]")
        return
    for change in candidates:
        print(render_outcome(prune_intent_file(change)))
