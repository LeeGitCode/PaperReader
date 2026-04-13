import re

from app.paper_parser.exceptions import PaperParseError
from app.paper_parser.schema import ParsedPaperDraft


ACM_DOI_PATTERN = re.compile(
    r"dl\.acm\.org/doi/(?:abs/|pdf/)?(?P<doi>10\.\d{4,9}/[-._;()/:A-Z0-9]+)",
    re.IGNORECASE,
)


class ACMResolver:
    name = "acm"

    def can_handle(self, source: str) -> bool:
        return "dl.acm.org/doi/" in source.lower()

    def can_parse(self, source: str) -> bool:
        return self.can_handle(source)

    async def parse(self, source: str) -> ParsedPaperDraft:
        match = ACM_DOI_PATTERN.search(source)
        if not match:
            raise PaperParseError("不支持的链接或解析失败")

        from app.paper_parser import extract_paper_info

        doi_url = f"https://doi.org/{match.group('doi').rstrip('.,;)')}"
        return await extract_paper_info(doi_url)
