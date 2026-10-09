"""A title copied from a pulled file already carries `[project] - `; creating
it must not add a second one."""

import pytest

from azz.core.engine_config import EngineConfig


def _config(prepend_project_name: bool = True) -> EngineConfig:
    return EngineConfig(
        org_url="https://example.invalid",
        default_project="TIDEPOOL",
        management_project="Management",
        default_repo="repo",
        prepend_project_name=prepend_project_name,
    )


@pytest.mark.parametrize(
    "name", ["[STREAM] buffer late events", "[TIDEPOOL] - [STREAM] buffer late events"]
)
def test_the_project_marker_appears_once(name: str) -> None:
    title = _config().project_title(name, "TIDEPOOL")
    assert title == "[TIDEPOOL] - [STREAM] buffer late events"


def test_no_marker_when_titles_do_not_carry_their_project() -> None:
    assert _config(False).project_title("A task", "TIDEPOOL") == "A task"
