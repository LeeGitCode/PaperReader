from app.paper_parser.exceptions import PaperParseError
from app.paper_parser.schema import ParsedPaperDraft


class UnsupportedURLError(PaperParseError):
    """Raised for known sources that require manual input."""


class IEEEResolver:
    name = "ieee"

    def can_handle(self, source: str) -> bool:
        return "ieeexplore.ieee.org" in source.lower()

    def can_parse(self, source: str) -> bool:
        return self.can_handle(source)

    async def parse(self, source: str) -> ParsedPaperDraft:
        raise UnsupportedURLError("IEEE 存在强反爬机制，请手动输入 DOI 或使用手动录入。")
