from __future__ import annotations

from pathlib import Path
from typing import Annotated, Final

import typer
from rich import print

from azz.claude_setup import InstallReport, Profile, install
from azz.core.engine import Engine

DEFAULT_PROFILE: Final = Profile.PLANNING
DEFAULT_TARGET: Final = Path()


def register(app: typer.Typer, _engine: Engine) -> None:
    claude_app = typer.Typer(help="Set up the Claude Code integration for azz.")

    def install_profile(
        profile: Annotated[
            Profile, typer.Argument(help="Which capabilities to grant Claude.")
        ] = DEFAULT_PROFILE,
        target: Annotated[
            Path, typer.Option("--target", "-t", help="Project to install into.")
        ] = DEFAULT_TARGET,
    ) -> None:
        """Add the azz docs and permissions to a project's Claude config."""
        try:
            report = install(profile, target)
        except (OSError, ValueError) as error:
            print(f"[red]{error}[/red]")
            raise typer.Exit(code=1) from error
        _report_install(report)

    def list_profiles() -> None:
        """Show the available profiles."""
        for profile in Profile:
            print(f"[bold]{profile.value}[/bold] — {profile.summary}")

    claude_app.command("install")(install_profile)
    claude_app.command("list")(list_profiles)
    app.add_typer(claude_app, name="claude")


def _report_install(report: InstallReport) -> None:
    print(f"[green]Installed the [bold]{report.profile.value}[/bold] profile[/green]")
    print(f"  skill     {report.skill_path}")
    print(f"  agents    {report.agents_path}")
    print(f"  settings  {report.settings_path}")
    if report.retired_claude_block:
        print(
            "\n[yellow]Removed the older azz block from CLAUDE.md[/yellow] — "
            "the skill replaces it, and is loaded only when relevant."
        )
    if report.profile is Profile.PLANNING:
        print(
            "\nClaude can now plan work in [bold].azz/tasks[/bold] but cannot "
            "change Azure DevOps.\nYou apply its plans with "
            "[bold]azz plan push[/bold]."
        )
