import pytest

from azz.plan.frontmatter import DELIMITER, QUOTE_TRIGGERS, Frontmatter, quote_scalar

BODY = "First line.\n\nSecond paragraph."


def test_splits_metadata_from_body() -> None:
    frontmatter = Frontmatter.from_text(
        f"{DELIMITER}\nitem_id: 7\ntitle: A title\n{DELIMITER}\n\n{BODY}\n"
    )
    assert frontmatter.metadata == {"item_id": 7, "title": "A title"}
    assert frontmatter.body == BODY


def test_empty_metadata_block_is_not_an_error() -> None:
    frontmatter = Frontmatter.from_text(f"{DELIMITER}\n{DELIMITER}\n{BODY}\n")
    assert frontmatter.metadata == {}
    assert frontmatter.body == BODY


@pytest.mark.parametrize(
    "text",
    [
        f"{BODY}\n",
        f"{DELIMITER}\nitem_id: 7\n",
        f"{DELIMITER}\n- not\n- a mapping\n{DELIMITER}\n",
        f"{DELIMITER}\ntitle: [unclosed\n{DELIMITER}\n",
    ],
    ids=["no opening", "unterminated", "not a mapping", "invalid yaml"],
)
def test_rejects_malformed_frontmatter(text: str) -> None:
    with pytest.raises(ValueError):
        Frontmatter.from_text(text)


@pytest.mark.parametrize("trigger", QUOTE_TRIGGERS)
def test_quotes_every_value_yaml_could_misread(trigger: str) -> None:
    quoted = quote_scalar(f"before{trigger}after")
    assert quoted.startswith('"')
    assert quoted.endswith('"')


def test_leaves_a_plain_value_unquoted() -> None:
    assert quote_scalar("Implement the login page") == "Implement the login page"


def test_quotes_an_empty_value() -> None:
    assert quote_scalar("") == '""'


def test_a_quoted_title_survives_the_round_trip() -> None:
    title = 'Fix: the "hard" case'
    frontmatter = Frontmatter.from_text(
        f"{DELIMITER}\ntitle: {quote_scalar(title)}\n{DELIMITER}\n"
    )
    assert frontmatter.metadata["title"] == title
