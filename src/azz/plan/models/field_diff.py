from dataclasses import dataclass

from rich.markup import escape


@dataclass(frozen=True, slots=True)
class FieldDiff:
    field_name: str
    local_value: str
    remote_value: str

    def render(self) -> str:
        return (
            f"{self.field_name + ':':<13}"
            f"[green]{escape(self.local_value)}[/green] (local) "
            f"≠ [red]{escape(self.remote_value)}[/red] (remote)"
        )
