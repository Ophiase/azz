"""Record `azz interactive` on the demo board as a GIF.

Development tooling, deliberately outside `src/azz`: it is not part of the
installed package. Needs ImageMagick's `convert` on PATH; run it through
`just gif`, which supplies the `cairosvg` dependency.
"""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Final

REPOSITORY: Final = Path(__file__).resolve().parent.parent
TERMINAL_SIZE: Final = (124, 30)
GIF_WIDTH: Final = 1100
FRAME_DELAY_CENTISECONDS: Final = 15
DRIFT_NOTE: Final = (
    "\n\n## Plan\n\n- drain the late-event buffer first\n- then emit the watermark\n"
)


@dataclass(frozen=True, slots=True)
class DemoStage:
    """A throwaway project with a populated `.azz/`, so the plan gutter has
    something to show."""

    workdir: Path
    state_dir: Path

    @property
    def environment(self) -> dict[str, str]:
        return {**os.environ, "AZZ_DEMO": "1", "AZZ_DEMO_DIR": str(self.state_dir)}

    def prepare(self, tracked_items: int = 6) -> None:
        self._azz("plan", "init")
        self._azz("plan", "fetch", "-l", str(tracked_items))
        self._azz("plan", "pull")
        self._introduce_local_drift()

    def _introduce_local_drift(self) -> None:
        """One file edited locally, so a `local ahead` glyph appears."""
        intent_files = sorted((self.workdir / ".azz" / "tasks").glob("*.md"))
        if not intent_files:
            raise RuntimeError("no intent files were pulled")
        target = intent_files[0]
        target.write_text(target.read_text().rstrip() + DRIFT_NOTE)

    def _azz(self, *arguments: str) -> None:
        subprocess.run(
            ["uv", "run", "--project", str(REPOSITORY), "azz", *arguments],
            cwd=self.workdir,
            env=self.environment,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )


class FrameRecorder:
    """Drives the TUI headlessly and writes one SVG per frame."""

    def __init__(self, frame_dir: Path) -> None:
        self._frame_dir = frame_dir
        self._index = 0

    async def record(self) -> int:
        from azz.demo import DemoSession
        from azz.tui.app import AzzTUI

        session = DemoSession.start()
        app = AzzTUI(session.backend)
        app.sub_title = session.notice
        async with app.run_test(size=TERMINAL_SIZE) as pilot:
            await self._play(app, pilot)
        return self._index

    async def _play(self, app, pilot) -> None:
        await self._capture(app, pilot, hold=6)
        for _ in range(3):
            await pilot.press("j")
            await self._capture(app, pilot)
        await self._capture(app, pilot, hold=3)
        await pilot.press("?")
        if len(app.screen_stack) <= 1:
            raise RuntimeError("the legend did not open")
        await self._capture(app, pilot, hold=10)
        await pilot.press("escape")
        await self._capture(app, pilot, hold=2)
        await pilot.press("a")
        await self._capture(app, pilot, hold=8)

    async def _capture(self, app, pilot, hold: int = 1) -> None:
        """`hold` repeats the frame, which is how a still moment is timed."""
        await pilot.pause()
        await app.workers.wait_for_complete()
        await pilot.pause()
        screenshot = app.export_screenshot()
        for _ in range(hold):
            (self._frame_dir / f"{self._index:03d}.svg").write_text(screenshot)
            self._index += 1


@dataclass(frozen=True, slots=True)
class GifBuilder:
    frame_dir: Path
    png_dir: Path

    def build(self, destination: Path) -> None:
        self._rasterize()
        destination.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                "convert",
                "-delay", str(FRAME_DELAY_CENTISECONDS),
                "-loop", "0",
                *[str(path) for path in sorted(self.png_dir.glob("*.png"))],
                "-layers", "optimize",
                str(destination),
            ],
            check=True,
        )

    def _rasterize(self) -> None:
        import cairosvg  # ty: ignore[unresolved-import]  (supplied by `just gif`)

        self.png_dir.mkdir(parents=True, exist_ok=True)
        for svg in sorted(self.frame_dir.glob("*.svg")):
            cairosvg.svg2png(
                url=str(svg),
                write_to=str(self.png_dir / f"{svg.stem}.png"),
                output_width=GIF_WIDTH,
            )


def main() -> None:
    destination = Path(sys.argv[1] if len(sys.argv) > 1 else "docs/media/azz-demo.gif")
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch)
        stage = DemoStage(workdir=root / "project", state_dir=root / "state")
        stage.workdir.mkdir()
        stage.prepare()

        frame_dir = root / "frames"
        frame_dir.mkdir()
        os.chdir(stage.workdir)
        os.environ.update(stage.environment)
        frames = asyncio.run(FrameRecorder(frame_dir).record())

        os.chdir(REPOSITORY)
        GifBuilder(frame_dir, root / "png").build(destination)
    print(f"{frames} frames -> {destination}")


main()
