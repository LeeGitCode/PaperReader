from urllib.parse import urljoin

from bs4 import BeautifulSoup
import httpx

from app.paper_parser.exceptions import PaperParseError
from app.paper_parser.schema import ParsedPaperDraft
from app.paper_parser.utils import extract_year, format_authors_display, normalize_space


class HtmlMetaParser:
    name = "html_meta"

    def can_handle(self, source: str) -> bool:
        return False

    def can_parse(self, source: str) -> bool:
        return self.can_handle(source)

    async def parse(self, source: str) -> ParsedPaperDraft:
        async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
            response = await client.get(source)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        title = normalize_space(_meta_content(soup, "citation_title"))
        if not title:
            raise PaperParseError("不支持的链接或解析失败")

        authors = [
            normalize_space(meta.get("content", ""))
            for meta in soup.find_all("meta", attrs={"name": "citation_author"})
        ]
        authors = [author for author in authors if author]

        publication_date = _meta_content(soup, "citation_publication_date")
        pdf_url = _meta_content(soup, "citation_pdf_url")
        if pdf_url:
            pdf_url = urljoin(str(response.url), pdf_url)

        venue = (
            _meta_content(soup, "citation_conference_title")
            or _meta_content(soup, "citation_journal_title")
            or _meta_content(soup, "citation_book_title")
            or _meta_content(soup, "citation_inproceedings_title")
        )
        year = extract_year(publication_date)

        return ParsedPaperDraft(
            title=title,
            authors=", ".join(authors),
            authors_display=format_authors_display(authors),
            year=year,
            pub_year=year,
            venue=normalize_space(venue),
            pdf_path=pdf_url,
            pdf_url=pdf_url,
        )


class CVFParser(HtmlMetaParser):
    name = "cvf"

    def can_handle(self, source: str) -> bool:
        return "thecvf.com" in source.lower()


class PMLRParser(HtmlMetaParser):
    name = "pmlr"

    def can_handle(self, source: str) -> bool:
        return "proceedings.mlr.press" in source.lower()


class NeurIPSParser(HtmlMetaParser):
    name = "neurips"

    def can_handle(self, source: str) -> bool:
        return "proceedings.neurips.cc" in source.lower()


def _meta_content(soup: BeautifulSoup, name: str) -> str:
    meta = soup.find("meta", attrs={"name": name})
    if not meta:
        return ""
    return normalize_space(meta.get("content", ""))
