import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import httpx

from app.paper_parser.exceptions import PaperParseError
from app.paper_parser.resolvers.html_meta_parser import _meta_content
from app.paper_parser.schema import ParsedPaperDraft
from app.paper_parser.utils import extract_year, format_authors_display, normalize_space


DOI_PATTERN = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)


class ACLResolver:
    name = "acl"

    def can_handle(self, source: str) -> bool:
        return "aclanthology.org" in source.lower()

    def can_parse(self, source: str) -> bool:
        return self.can_handle(source)

    async def parse(self, source: str) -> ParsedPaperDraft:
        async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
            response = await client.get(source)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        doi = _extract_acl_doi(soup)
        if doi:
            from app.paper_parser import extract_paper_info

            return await extract_paper_info(f"https://doi.org/{doi}")

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
        year = extract_year(publication_date)

        return ParsedPaperDraft(
            title=title,
            authors=", ".join(authors),
            authors_display=format_authors_display(authors),
            year=year,
            pub_year=year,
            venue=normalize_space(
                _meta_content(soup, "citation_conference_title")
                or _meta_content(soup, "citation_journal_title")
                or "ACL Anthology"
            ),
            pdf_path=pdf_url,
            pdf_url=pdf_url,
        )


def _extract_acl_doi(soup: BeautifulSoup) -> str:
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        if "doi.org/10." in href.lower():
            doi = _extract_doi(href)
            if doi:
                return doi

    for name in ("citation_doi", "dc.identifier", "DC.Identifier"):
        doi = _extract_doi(_meta_content(soup, name))
        if doi:
            return doi

    for meta in soup.find_all("meta"):
        content = meta.get("content", "")
        doi = _extract_doi(content)
        if doi:
            return doi

    return ""


def _extract_doi(value: str) -> str:
    match = DOI_PATTERN.search(value)
    if not match:
        return ""
    return match.group(0).rstrip(".,;)")
