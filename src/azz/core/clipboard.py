import os
import subprocess  # noqa: S404
from collections.abc import Sequence


def copy_to_clipboard(text: str) -> bool:
    """Attempt to copy text to the system clipboard. Returns True on success."""
    if os.environ.get("WAYLAND_DISPLAY") and _run_copy_command(["wl-copy"], text):
        return True
    return (
        _run_copy_command(["xclip", "-selection", "clipboard"], text)
        or _run_copy_command(["xsel", "--clipboard", "--input"], text)
    )


def _run_copy_command(command: Sequence[str], text: str) -> bool:
    try:
        subprocess.run(  # noqa: S603
            command, input=text.encode(), check=True, capture_output=True
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False
