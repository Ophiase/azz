# Demo mode

Every work item on a real board tends to be confidential, which makes the
tool awkward to screenshot, record, or show to anyone. Demo mode runs
everything against a bundled fictional board instead.

```bash
azz --demo interactive        # the TUI, on fake data
azz --demo list
AZZ_DEMO=1 azz list           # same, via the environment
```

It needs no Azure DevOps account and no environment variables at all: it
never reads your config and never touches the network, so it works on a fresh
machine immediately after installing.

## Notes

- `--demo` must come *before* the subcommand: `azz --demo list`, not
  `azz list --demo`. It is detected from the tokens preceding the subcommand,
  so an argument that merely contains the word cannot swap a real board for
  the fake one.
- Changes are discarded on exit, so every recording starts from the same
  state. Set `AZZ_DEMO_DIR=<path>` to keep them instead.
- The TUI subtitle reads `DEMO DATA` so a recording can never be mistaken for
  a real board.
- The fictional product is an invented streaming toolkit. Nothing in the
  fixture resembles a real organisation.

## How it works

Demo mode is a `CacheBackend` over a bundled fixture — the same machinery
that makes `azz plan status` work offline. `AzzApp` picks the backend before
`EngineConfig.from_env()` runs, which is what lets it start with no
credentials present.

See [2026-07-31-plan-cache.md](decisions/2026-07-31-plan-cache.md) for why
the cache is a second backend rather than a plan-engine detail.

## Regenerating the README recording

The GIF in the README is generated from demo mode, so it cannot drift from
the real behaviour:

```bash
just gif    # -> docs/media/azz-demo.gif
```

`tools/record_demo.py` stages a throwaway project, runs `plan init` /
`fetch` / `pull` against the demo backend so the plan gutter has something to
show, edits one intent file so a local-ahead glyph appears, then drives the
TUI headlessly and captures Textual's own SVG export for each frame.
`cairosvg` rasterizes them and ImageMagick assembles the GIF.

The recorder fails if the legend does not open, so a mute recording cannot
ship. It needs ImageMagick's `convert` on PATH; `just gif` supplies the
Python side.

ImageMagick was tried alone first: it renders the window chrome and silently
drops every character of terminal text, which is why a real SVG rasterizer is
in the loop.
