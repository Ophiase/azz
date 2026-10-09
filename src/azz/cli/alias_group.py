import click
from typer.core import TyperGroup

ALIAS_SEPARATOR = " | "


class AliasGroup(TyperGroup):
    """
    Lets one command answer to several names.

    Register it as `app.command("list | l")` and both `azz list` and `azz l`
    reach it, while `--help` shows a single entry instead of one undocumented
    line per alias.
    """

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        return super().get_command(ctx, self._registered_name(cmd_name))

    def _registered_name(self, cmd_name: str) -> str:
        for registered in self.commands:
            if cmd_name in registered.split(ALIAS_SEPARATOR):
                return registered
        return cmd_name
