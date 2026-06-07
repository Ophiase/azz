import asyncio
import json
from logging import getLogger

type AzCommand = str


logger = getLogger(__name__)


def normalize_command_arg(arg: str) -> str:
    """
    Normalize command arguments for cross-platform subprocess usage.
    """
    return arg.replace("\\", "/")


async def run_command(*cmd: str) -> tuple[str, str]:
    logger.debug("Running command: %s", " ".join(cmd))
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()
    logger.debug("Result: %s", stdout.decode())

    return stdout.decode(), stderr.decode()


async def run_az_command(*args: str) -> list | dict:
    cmd = ["az", *args]

    stdout, stderr = await run_command(*cmd)

    if stderr.strip():
        logger.debug("az stderr: %s", stderr)

    if not stdout.strip():
        stderr_msg = f" stderr: {stderr}" if stderr.strip() else ""
        raise RuntimeError(
            f"az command returned empty output: {' '.join(cmd)}{stderr_msg}"
        )

    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid JSON from az command: {' '.join(cmd)}") from exc


async def run_az_void(*args: str) -> None:
    cmd = ["az", *args]

    _, stderr = await run_command(*cmd)

    if stderr.strip():
        logger.debug(stderr)

    return None


def run_az_void_sync(*args: str) -> None:
    """
    Sync wrapper for CLI usage.
    Ensures proper event loop handling.
    """
    try:
        return asyncio.run(run_az_void(*args))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_az_void(*args))


def run_az_command_sync(*args: str) -> list | dict:
    """
    Sync wrapper for CLI usage.
    Ensures proper event loop handling.
    """
    try:
        return asyncio.run(run_az_command(*args))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(run_az_command(*args))
