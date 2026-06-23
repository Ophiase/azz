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
    # Clipboard daemons (wl-copy, xclip) never exit — they stay alive to serve
    # paste requests. Use Popen without waiting so we return immediately.
    try:
        proc = subprocess.Popen(  # noqa: S603
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )
        if proc.stdin is not None:
            proc.stdin.write(text.encode())
            proc.stdin.close()
        return True
    except (FileNotFoundError, OSError):
        return False
