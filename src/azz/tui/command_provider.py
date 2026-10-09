from functools import partial

from textual.command import DiscoveryHit, Hit, Hits, Provider

from .palette_entry import PaletteEntry


class WorkItemCommands(Provider):
    """
    Puts every key binding in the command palette.

    Twelve of them are `show=False`, so the footer never mentions them. Read
    from `BINDINGS` rather than restated, so a new key appears here on its own.
    """

    async def discover(self) -> Hits:
        for entry in self._entries():
            yield DiscoveryHit(entry.name, self._runner(entry), help=entry.help)

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)
        for entry in self._entries():
            score = matcher.match(entry.name)
            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(entry.name),
                    self._runner(entry),
                    help=entry.help,
                )

    def _entries(self) -> tuple[PaletteEntry, ...]:
        return PaletteEntry.from_bindings(type(self.app).BINDINGS)

    def _runner(self, entry: PaletteEntry) -> partial:
        return partial(self.app.run_action, entry.action)
