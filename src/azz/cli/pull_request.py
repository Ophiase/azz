import sys
from pathlib import Path
from typing import Annotated, Final

import typer
from rich import print
from rich.markdown import Markdown

from azz.backend import WorkItemBackend
from azz.core.pull_request import (
    BranchPullRequest,
    GitCheckout,
    PullRequestDraft,
    PullRequestRequest,
)

STANDARD_INPUT: Final = "-"


def register(app: typer.Typer, engine: WorkItemBackend) -> None:
    pull_request_app = typer.Typer(help="Open pull requests on Azure DevOps.")

    def create(
        branch: Annotated[
            str | None, typer.Argument(help="Defaults to the current branch.")
        ] = None,
        target: Annotated[
            str | None,
            typer.Option("--target", "-t", help="Defaults to the repository's."),
        ] = None,
        title: Annotated[str | None, typer.Option("--title")] = None,
        description_file: Annotated[
            str | None,
            typer.Option(
                "--description-file", "-f", help="Markdown file, or - for stdin."
            ),
        ] = None,
        work_item_ids: Annotated[
            list[int] | None,
            typer.Option("--work-item", "-w", help="Linked on top of the branch's."),
        ] = None,
        reviewers: Annotated[
            list[str] | None,
            typer.Option("--reviewer", "-r", help="Defaults to you."),
        ] = None,
        is_draft: Annotated[bool, typer.Option("--draft")] = False,
        dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
    ) -> None:
        """Push a branch and open its pull request, or update the open one."""
        request = PullRequestRequest(
            branch=branch,
            target_branch=target,
            title=title,
            description=_read_description(description_file),
            extra_work_item_ids=tuple(work_item_ids or ()),
            reviewers=tuple(reviewers or ()),
            is_draft=is_draft,
        )
        try:
            _create(request, engine, dry_run)
        except (RuntimeError, ValueError) as error:
            print(f"[red]{error}[/red]")
            raise typer.Exit(code=1) from error

    pull_request_app.command("create")(create)
    app.add_typer(pull_request_app, name="pr")


def _create(
    request: PullRequestRequest, engine: WorkItemBackend, dry_run: bool
) -> None:
    pull_request = BranchPullRequest.resolve(GitCheckout(), request.branch)
    draft = pull_request.compose(request, engine)
    _show(pull_request, draft)
    if dry_run:
        print("\n[dim]Dry run: nothing pushed, nothing created.[/dim]")
        return
    published = pull_request.publish(draft)
    verb = "Created" if published.is_new else "Updated"
    print(f"\n[green]{verb} pull request {published.pull_request_id}[/green]")
    print(published.url)


def _show(pull_request: BranchPullRequest, draft: PullRequestDraft) -> None:
    repository = pull_request.repository
    print(f"[bold]{draft.title}[/bold]")
    print(
        f"[dim]{repository.project}/{repository.name}  "
        f"{draft.source_branch} → {draft.target_branch}[/dim]"
    )
    linked = ", ".join(map(str, draft.work_item_ids)) or "none"
    print(f"[dim]work items {linked}  reviewers {', '.join(draft.reviewers)}[/dim]")
    if draft.is_draft:
        print("[yellow]draft[/yellow]")
    print(Markdown(draft.description or "_no description_"))


def _read_description(source: str | None) -> str | None:
    if source is None:
        return None
    if source == STANDARD_INPUT:
        return sys.stdin.read()
    return Path(source).read_text()
