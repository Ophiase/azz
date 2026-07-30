from dataclasses import dataclass
from typing import Any, Final, Self

import yaml

DELIMITER: Final = "---"
QUOTE_TRIGGERS: Final = (":", "#", "'", '"', "[", "]", "{", "}", "\n")


def quote_scalar(value: str) -> str:
    if not value or any(trigger in value for trigger in QUOTE_TRIGGERS):
        return '"{}"'.format(value.replace('"', '\\"'))
    return value


@dataclass(frozen=True, slots=True)
class Frontmatter:
    metadata: dict[str, Any]
    body: str

    @classmethod
    def from_text(cls, text: str) -> Self:
        lines = text.splitlines()
        if not lines or lines[0].strip() != DELIMITER:
            raise ValueError(f"missing frontmatter: file must start with '{DELIMITER}'")
        closing_index = _closing_delimiter_index(lines)
        metadata = _load_metadata("\n".join(lines[1:closing_index]))
        body = "\n".join(lines[closing_index + 1 :]).strip()
        return cls(metadata=metadata, body=body)


def _closing_delimiter_index(lines: list[str]) -> int:
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == DELIMITER:
            return index
    raise ValueError(f"unterminated frontmatter: no closing '{DELIMITER}'")


def _load_metadata(block: str) -> dict[str, Any]:
    try:
        metadata = yaml.safe_load(block)
    except yaml.YAMLError as error:
        raise ValueError(f"invalid YAML frontmatter: {error}") from error
    if metadata is None:
        return {}
    if not isinstance(metadata, dict):
        raise ValueError("frontmatter must be a mapping of fields")
    return metadata
