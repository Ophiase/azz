from bs4 import BeautifulSoup
from markdownify import markdownify as md

type Html = str
type Markdown = str


def html_to_text(html: Html | None) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text("\n").strip()


def html_to_markdown(html: Html | None) -> Markdown:
    if not html:
        return ""
    return md(html).strip()
