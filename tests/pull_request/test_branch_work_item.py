import pytest

from azz.core.branch import branch_name, work_item_id_from_branch
from tests.conftest import RemoteFactory


@pytest.mark.parametrize(
    ("iteration_path", "name"),
    [
        ("Project\\TB 46", "[LotomateAIV3] - Monitoring elastic normalization"),
        (None, "Fix 2 bugs in 3 places"),
    ],
)
def test_the_id_survives_a_round_trip_through_the_branch_name(
    remote_item: RemoteFactory, iteration_path: str | None, name: str
) -> None:
    work_item = remote_item(item_id=8049, name=name, iteration_path=iteration_path)
    assert work_item_id_from_branch(branch_name(work_item)) == 8049


@pytest.mark.parametrize(
    "branch", ["main", "dev/tb-46-monitoring", "dev/plan-engine-auto"]
)
def test_a_branch_without_an_id_yields_none(branch: str) -> None:
    assert work_item_id_from_branch(branch) is None
