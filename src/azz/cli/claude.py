from __future__ import annotations

from pathlib import Path
from typing import Annotated, Final

import typer
from rich import print

from azz.claude_setup import InstallReport, InstallScope, Profile, install
from azz.claude_setup.git_ignore import is_ignored
from azz.core.engine import Engine

DEFAULT_PROFILE: Final = Profile.PLANNING
DEFAULT_SCOPE: Final = InstallScope.USER
DEFAULT_TARGET: Final = Path()


def register(app: typer.Typer, _engine: Engine) -> None:
    claude_app = typer.Typer(help="Set up the Claude Code integration for azz.")

    def install_profile(
        profile: Annotated[
            Profile, typer.Argument(help="Which capabilities to grant Claude.")
        ] = DEFAULT_PROFILE,
        scope: Annotated[
            InstallScope,
            typer.Option("--scope", "-s", help="Keep it personal, or share it."),
        ] = DEFAULT_SCOPE,
        target: Annotated[
            Path, typer.Option("--target", "-t", help="Project to install into.")
        ] = DEFAULT_TARGET,
    ) -> None:
        """Add the azz skill and permissions to a project's Claude config."""
        try:
            report = install(profile, target, scope)
        except (OSError, ValueError) as error:
            print(f"[red]{error}[/red]")
            raise typer.Exit(code=1) from error
        _report_install(report)

    def list_profiles() -> None:
        """Show the available profiles and scopes."""
        for profile in Profile:
            print(f"[bold]{profile.value}[/bold] — {profile.summary}")
        print()
        for scope in InstallScope:
            print(f"[bold]--scope {scope.value}[/bold] — {scope.summary}")

    claude_app.command("install")(install_profile)
    claude_app.command("list")(list_profiles)
    app.add_typer(claude_app, name="claude")


def _report_install(report: InstallReport) -> None:
    print(
        f"[green]Installed the [bold]{report.profile.value}[/bold] profile[/green] "
        f"([bold]{report.scope.value}[/bold] scope)"
    )
    print(f"  skill     {report.skill_path}")
    print(f"  settings  {report.settings_path}")
    if report.agents_path is not None:
        print(f"  agents    {report.agents_path}")
    if report.retired_claude_block:
        print(
            "\n[yellow]Removed the older azz block from CLAUDE.md[/yellow] — "
            "the skill replaces it, and is loaded only when relevant."
        )
    _report_sharing(report)
    if report.profile is Profile.PLANNING:
        print(
            "\nClaude can now plan work in [bold].azz/tasks[/bold] but cannot "
            "change Azure DevOps.\nYou apply its plans with "
            "[bold]azz plan push[/bold]."
        )


def _report_sharing(report: InstallReport) -> None:
    if report.scope.shares_with_the_repository:
        print("\nThese files belong in the repository — commit them.")
        return
    if report.excluded:
        print("\nHidden from the repository via [bold].git/info/exclude[/bold]:")
        for pattern in report.excluded:
            print(f"  {pattern}")
    elif is_ignored(report.settings_path) is not False:
        print("\nNothing was added to the repository.")
    else:
        print(
            "\n[yellow]Could not write .git/info/exclude[/yellow] — is this a "
            "git working tree?\nThese files would otherwise show up for your "
            "colleagues."
        )
    if report.already_tracked:
        print(
            "\n[yellow]Already committed, so no ignore rule can hide "
            "them:[/yellow]"
        )
        for pattern in report.already_tracked:
            print(f"  {pattern}")
        print("Remove them from the repository first, or use --scope project.")
