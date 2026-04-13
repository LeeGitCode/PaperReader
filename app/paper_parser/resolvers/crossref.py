import re
from typing import Any
from urllib.parse import unquote, urlparse

import httpx

from app.paper_parser.exceptions import PaperParseError
from app.paper_parser.schema import ParsedPaperDraft
from app.paper_parser.utils import format_authors_display, normalize_space


CROSSREF_API_URL = "https://api.crossref.org/works/{doi}"
DOI_URL_PATTERN = re.compile(r"(?:doi\.org/|dx\.doi\.org/)(?P<doi>10\.\S+)", re.IGNORECASE)
DOI_PATTERN = re.compile(r"(?P<doi>10\.\d{4,9}/[-._;()/:A-Z0-9]+)", re.IGNORECASE)


class CrossrefDoiResolver:
    name = "crossref_doi"

    def can_parse(self, source: str) -> bool:
        return extract_doi(source) is not None

    async def parse(self, source: str) -> ParsedPaperDraft:
        doi = extract_doi(source)
        if not doi:
            raise PaperParseError("不支持的链接或解析失败")

        async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
            response = await client.get(
                CROSSREF_API_URL.format(doi=doi),
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()

        message = response.json().get("message") or {}
        titles = message.get("title") or []
        title = normalize_space(titles[0]) if titles else ""
        if not title:
            raise PaperParseError("不支持的链接或解析失败")

        authors = [_format_crossref_author(author) for author in message.get("author", [])]
        authors = [author for author in authors if author]
        year = _extract_crossref_year(message)
        container_titles = message.get("container-title") or []

        return ParsedPaperDraft(
            title=title,
            authors=", ".join(authors),
            authors_display=format_authors_display(authors),
            year=year,
            pub_year=year,
            venue=normalize_space(container_titles[0]) if container_titles else "",
            pdf_url=_extract_crossref_pdf_url(message),
            doi=doi,
        )


def extract_doi(source: str) -> str | None:
    decoded = unquote(source.strip())
    parsed = urlparse(decoded)
    target = decoded

    if parsed.netloc:
        target = f"{parsed.netloc}{parsed.path}"
        if parsed.query:
            target = f"{target}?{parsed.query}"

    url_match = DOI_URL_PATTERN.search(decoded)
    if url_match:
        return _clean_doi(url_match.group("doi"))

    doi_match = DOI_PATTERN.search(target)
    if doi_match:
        return _clean_doi(doi_match.group("doi"))

    return None


def _clean_doi(doi: str) -> str:
    return doi.strip().rstrip(".,;)")


def _extract_crossref_year(message: dict[str, Any]) -> int | None:
    for field in ("published-print", "published-online", "published", "issued", "created"):
        date_parts = message.get(field, {}).get("date-parts", [])
        if date_parts and date_parts[0]:
            return int(date_parts[0][0])
    return None


def _format_crossref_author(author: dict[str, Any]) -> str:
    given = author.get("given", "")
    family = author.get("family", "")
    literal = author.get("name", "")
    return normalize_space(f"{given} {family}" if family else literal)


def _extract_crossref_pdf_url(message: dict[str, Any]) -> str:
    links = message.get("link") or []
    for link in links:
        content_type = link.get("content-type", "")
        url = link.get("URL", "")
        if "pdf" in content_type.lower() and url:
            return url
    return ""
