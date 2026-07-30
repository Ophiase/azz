"""`write_back` must leave everything it was not asked to change untouched —
otherwise a create silently rewrites the description the user just authored."""

import pytest

from azz.plan.errors import IntentFileError
from azz.plan.frontmatter import DELIMITER, Frontmatter
from azz.plan.writer import write_back
from tests.conftest import IntentFactory

BODY = "The description.\n\nWith a second paragraph."


def test_inserts_a_key_that_was_absent(intent_file: IntentFactory) -> None:
    path = intent_file(f"{DELIMITER}\ntitle: A title\n{DELIMITER}\n\n{BODY}\n")
    write_back(path, item_id=7)
    assert Frontmatter.from_text(path.read_text()).metadata["item_id"] == 7


def test_overwrites_a_key_that_was_present(intent_file: IntentFactory) -> None:
    path = intent_file(f"{DELIMITER}\nitem_id: 1\ntitle: Old\n{DELIMITER}\n\n{BODY}\n")
    write_back(path, item_id=7, title="New")
    metadata = Frontmatter.from_text(path.read_text()).metadata
    assert metadata == {"item_id": 7, "title": "New"}


def test_preserves_the_body_verbatim(intent_file: IntentFactory) -> None:
    path = intent_file(f"{DELIMITER}\ntitle: A title\n{DELIMITER}\n\n{BODY}\n")
    write_back(path, item_id=7)
    assert Frontmatter.from_text(path.read_text()).body == BODY


def test_leaves_untouched_keys_alone(intent_file: IntentFactory) -> None:
    path = intent_file(
        f"{DELIMITER}\nitem_id: 7\nstate: Active\niteration: Sprint 42\n{DELIMITER}\n"
    )
    write_back(path, title="A title")
    metadata = Frontmatter.from_text(path.read_text()).metadata
    assert metadata["state"] == "Active"
    assert metadata["iteration"] == "Sprint 42"


def test_a_title_needing_quotes_stays_parseable(intent_file: IntentFactory) -> None:
    path = intent_file(f"{DELIMITER}\nitem_id: 7\n{DELIMITER}\n")
    title = "[Project] Fix: the hard case"
    write_back(path, title=title)
    assert Frontmatter.from_text(path.read_text()).metadata["title"] == title


def test_reports_the_file_when_the_frontmatter_is_unterminated(
    intent_file: IntentFactory,
) -> None:
    path = intent_file(f"{DELIMITER}\nitem_id: 7\n")
    with pytest.raises(IntentFileError):
        write_back(path, title="A title")
