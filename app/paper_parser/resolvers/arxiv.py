import re
from xml.etree import ElementTree

import httpx

from app.paper_parser.exceptions import PaperParseError
from app.paper_parser.schema import ParsedPaperDraft
from app.paper_parser.utils import extract_year, format_authors_display, normalize_space


ARXIV_API_URL = "https://export.arxiv.org/api/query"
ARXIV_ID_PATTERN = re.compile(
    r"arxiv\.org/(?:abs|pdf)/(?P<id>\d{4}\.\d{4,5}(?:v\d+)?|[a-z-]+(?:\.[A-Z]{2})?/\d{7}(?:v\d+)?)",
    re.IGNORECASE,
)


class ArxivResolver:
    name = "arxiv"

    def can_parse(self, source: str) -> bool:
        return extract_arxiv_id(source) is not None

    async def parse(self, source: str) -> ParsedPaperDraft:
        arxiv_id = extract_arxiv_id(source)
        if not arxiv_id:
            raise PaperParseError("不支持的链接或解析失败")

        async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
            response = await client.get(ARXIV_API_URL, params={"id_list": arxiv_id})
            response.raise_for_status()

        root = ElementTree.fromstring(response.text)
        namespace = {"atom": "http://www.w3.org/2005/Atom"}
        entry = root.find("atom:entry", namespace)
        if entry is None:
            raise PaperParseError("不支持的链接或解析失败")

        title = normalize_space(_required_text(entry, "atom:title", namespace))
        authors = [
            normalize_space(author.findtext("atom:name", default="", namespaces=namespace))
            for author in entry.findall("atom:author", namespace)
        ]
        authors = [author for author in authors if author]
        year = extract_year(entry.findtext("atom:published", default="", namespaces=namespace))

        return ParsedPaperDraft(
            title=title,
            authors=", ".join(authors),
            authors_display=format_authors_display(authors),
            year=year,
            pub_year=year,
            venue="arXiv",
            pdf_path=f"https://arxiv.org/pdf/{arxiv_id}",
            pdf_url=f"https://arxiv.org/pdf/{arxiv_id}",
            arxiv_id=arxiv_id,
        )


def extract_arxiv_id(source: str) -> str | None:
    match = ARXIV_ID_PATTERN.search(source)
    if not match:
        return None

    return match.group("id").removesuffix(".pdf")


def _required_text(element: ElementTree.Element, path: str, namespace: dict[str, str]) -> str:
    value = element.findtext(path, default="", namespaces=namespace)
    if not value:
        raise PaperParseError("不支持的链接或解析失败")
    return value
