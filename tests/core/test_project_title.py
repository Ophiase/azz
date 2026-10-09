"""A title copied from a pulled file already carries `[project] - `; creating
it must not add a second one."""

import pytest

from azz.core.engine_config import EngineConfig


def _config(prepend_project_name: bool = True) -> EngineConfig:
    return EngineConfig(
        org_url="https://example.invalid",
        default_project="LotomateAIV3",
        management_project="Management",
        default_repo="repo",
        prepend_project_name=prepend_project_name,
    )


@pytest.mark.parametrize(
    "name", ["[OCR] split a batch", "[LotomateAIV3] - [OCR] split a batch"]
)
def test_the_project_marker_appears_once(name: str) -> None:
    title = _config().project_title(name, "LotomateAIV3")
    assert title == "[LotomateAIV3] - [OCR] split a batch"


def test_no_marker_when_titles_do_not_carry_their_project() -> None:
    assert _config(False).project_title("A task", "LotomateAIV3") == "A task"
