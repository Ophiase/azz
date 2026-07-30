"""The load-bearing invariant: a field absent from the frontmatter stays
`None`, so it is never compared and never pushed."""

import pytest

from azz.core.work_item import WorkItemState
from azz.plan.errors import IntentFileError
from azz.plan.frontmatter import DELIMITER
from azz.plan.models import LocalItem
from azz.plan.parser import KNOWN_FIELDS, parse_intent_file
from tests.conftest import IntentFactory

ALWAYS_SET = frozenset({"path", "title"})
OPTIONAL_FIELDS = sorted(set(LocalItem.model_fields) - ALWAYS_SET)
LEGACY_FIELDS = sorted(KNOWN_FIELDS - set(LocalItem.model_fields) - {"type"})


@pytest.mark.parametrize("field_name", OPTIONAL_FIELDS)
def test_a_field_absent_from_the_frontmatter_stays_none(
    field_name: str, intent_file: IntentFactory
) -> None:
    path = intent_file(f"{DELIMITER}\ntitle: Only a title\n{DELIMITER}\n")
    assert getattr(parse_intent_file(path), field_name) is None


@pytest.mark.parametrize("field_name", LEGACY_FIELDS)
def test_a_retired_field_is_accepted_and_ignored(
    field_name: str, intent_file: IntentFactory
) -> None:
    """Retired keys stay in KNOWN_FIELDS for a release so an old `.azz/` still
    parses. Dropping them from KNOWN_FIELDS turns every existing file into an
    unknown-field error."""
    path = intent_file(
        f"{DELIMITER}\nitem_id: 7\n{field_name}: anything\n{DELIMITER}\n"
    )
    assert not hasattr(parse_intent_file(path), field_name)


def test_a_file_without_an_item_id_is_new(intent_file: IntentFactory) -> None:
    path = intent_file(f"{DELIMITER}\ntitle: Only a title\n{DELIMITER}\n")
    assert parse_intent_file(path).is_new


def test_an_empty_body_is_none_rather_than_an_empty_description(
    intent_file: IntentFactory,
) -> None:
    path = intent_file(f"{DELIMITER}\nitem_id: 7\n{DELIMITER}\n\n\n")
    assert parse_intent_file(path).description is None


def test_the_body_becomes_the_description(intent_file: IntentFactory) -> None:
    body = "What to do.\n\nAnd why."
    path = intent_file(f"{DELIMITER}\nitem_id: 7\n{DELIMITER}\n\n{body}\n")
    assert parse_intent_file(path).description == body


def test_state_is_parsed_from_user_input(intent_file: IntentFactory) -> None:
    path = intent_file(f"{DELIMITER}\nitem_id: 7\nstate: active\n{DELIMITER}\n")
    assert parse_intent_file(path).state == WorkItemState.ACTIVE


def test_rejects_an_unknown_field(intent_file: IntentFactory) -> None:
    path = intent_file(f"{DELIMITER}\nitem_id: 7\nassignee: someone\n{DELIMITER}\n")
    with pytest.raises(IntentFileError, match="assignee"):
        parse_intent_file(path)


def test_reports_the_path_when_the_file_is_malformed(
    intent_file: IntentFactory,
) -> None:
    path = intent_file("no frontmatter at all\n")
    with pytest.raises(IntentFileError, match=path.name):
        parse_intent_file(path)
