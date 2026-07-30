import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Final

from .profile import PERMISSION_KEYS

AZZ_RULE_PREFIX: Final = "Bash(azz"


def install_settings(
    settings_path: Path, permissions: Mapping[str, Sequence[str]]
) -> None:
    """Merge the profile's rules into settings.json.

    Rules the user wrote for other tools are preserved; previous `azz` rules
    are dropped first, so switching profiles never leaves stale entries.
    """
    document = _read_document(settings_path)
    block = document.setdefault("permissions", {})
    for key in PERMISSION_KEYS:
        merged = _merge(block.get(key), permissions.get(key, ()))
        if merged:
            block[key] = merged
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(document, indent=2) + "\n")


def _merge(existing: Any, profile_rules: Sequence[str]) -> list[str]:
    foreign = [
        rule
        for rule in (existing if isinstance(existing, list) else [])
        if not (isinstance(rule, str) and rule.startswith(AZZ_RULE_PREFIX))
    ]
    return [*foreign, *profile_rules]


def _read_document(settings_path: Path) -> dict[str, Any]:
    if not settings_path.exists():
        return {}
    try:
        document = json.loads(settings_path.read_text())
    except json.JSONDecodeError as error:
        raise ValueError(f"{settings_path} is not valid JSON: {error}") from error
    if not isinstance(document, dict):
        raise ValueError(f"{settings_path} must contain a JSON object")
    return document
