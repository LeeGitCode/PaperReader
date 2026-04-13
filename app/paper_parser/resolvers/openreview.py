from datetime import datetime, timezone
import re
from typing import Any
from urllib.parse import unquote

import httpx

from app.paper_parser.exceptions import PaperParseError
from app.paper_parser.schema import ParsedPaperDraft
from app.paper_parser.utils import extract_year, format_authors_display, normalize_space


OPENREVIEW_API_URL = "https://api.openreview.net/notes"
OPENREVIEW_URL_PATTERN = re.compile(
    r"openreview\.net/(?:forum|pdf)\b.*[?&]id=(?P<id>[^&#]+)",
    re.IGNORECASE,
)


class OpenReviewResolver:
    name = "openreview"

    def can_handle(self, source: str) -> bool:
        return extract_openreview_id(source) is not None

    def can_parse(self, source: str) -> bool:
        return self.can_handle(source)

    async def parse(self, source: str) -> ParsedPaperDraft:
        note_id = extract_openreview_id(source)
        if not note_id:
            raise PaperParseError("不支持的链接或解析失败")

        async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
            response = await client.get(OPENREVIEW_API_URL, params={"id": note_id})
            response.raise_for_status()

        notes = response.json().get("notes") or []
        if not notes:
            raise PaperParseError("不支持的链接或解析失败")

        note = notes[0]
        content = note.get("content") or {}
        title = normalize_space(_content_value(content, "title"))
        if not title:
            raise PaperParseError("不支持的链接或解析失败")

        authors = _content_list(content, "authors")
        year = _extract_openreview_year(note, content)
        venue = normalize_space(
            _content_value(content, "venue")
            or _content_value(content, "venueid")
            or _content_value(content, "conference")
        )

        pdf_url = f"https://openreview.net/pdf?id={note_id}"

        return ParsedPaperDraft(
            title=title,
            authors=", ".join(authors),
            authors_display=format_authors_display(authors),
            year=year,
            pub_year=year,
            venue=venue,
            pdf_path=pdf_url,
            pdf_url=pdf_url,
            extra={"openreview_id": note_id},
        )


def extract_openreview_id(source: str) -> str | None:
    match = OPENREVIEW_URL_PATTERN.search(source.strip())
    if not match:
        return None

    return unquote(match.group("id"))


def _content_value(content: dict[str, Any], key: str) -> str:
    value = content.get(key)
    if isinstance(value, dict):
        value = value.get("value")
    if isinstance(value, list):
        return ", ".join(str(item) for item in value if item)
    return str(value) if value else ""


def _content_list(content: dict[str, Any], key: str) -> list[str]:
    value = content.get(key)
    if isinstance(value, dict):
        value = value.get("value")
    if isinstance(value, str):
        return [normalize_space(value)] if value.strip() else []
    if isinstance(value, list):
        return [normalize_space(str(item)) for item in value if str(item).strip()]
    return []


def _extract_openreview_year(note: dict[str, Any], content: dict[str, Any]) -> int | None:
    for key in ("year", "publication_date", "venue"):
        year = extract_year(_content_value(content, key))
        if year:
            return year

    cdate = note.get("cdate")
    if isinstance(cdate, (int, float)):
        return extract_year_from_timestamp(cdate)
    if isinstance(cdate, str) and cdate.isdigit():
        return extract_year_from_timestamp(float(cdate))

    return extract_year(str(cdate or ""))


def extract_year_from_timestamp(timestamp: int | float) -> int | None:
    if timestamp > 10_000_000_000:
        timestamp = timestamp / 1000
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).year
