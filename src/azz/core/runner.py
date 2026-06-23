import asyncio
import json
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from logging import getLogger
from typing import Any

type AzCommand = str


logger = getLogger(__name__)


def normalize_command_arg(arg: str) -> str:
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


def _run_in_thread(coro: Any) -> Any:
    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


def run_az_command_sync(*args: str) -> list | dict:
    try:
        return asyncio.run(run_az_command(*args))
    except RuntimeError:
        return _run_in_thread(run_az_command(*args))


def run_az_void_sync(*args: str) -> None:
    try:
        asyncio.run(run_az_void(*args))
    except RuntimeError:
        _run_in_thread(run_az_void(*args))
