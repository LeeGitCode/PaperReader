from typing import Protocol

from app.paper_parser.schema import ParsedPaperDraft


class PaperResolver(Protocol):
    name: str

    def can_parse(self, source: str) -> bool:
        """Return True when this resolver knows how to parse the input source."""

    async def parse(self, source: str) -> ParsedPaperDraft:
        """Parse source into a normalized paper draft."""
