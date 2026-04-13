from xml.etree import ElementTree

import httpx

from app.paper_parser.exceptions import PaperParseError
from app.paper_parser.resolvers import DEFAULT_RESOLVERS
from app.paper_parser.resolvers.base import PaperResolver
from app.paper_parser.schema import ParsedPaperDraft


class PaperParserRegistry:
    def __init__(self, resolvers: list[PaperResolver] | None = None) -> None:
        self._resolvers = resolvers or list(DEFAULT_RESOLVERS)

    @property
    def resolvers(self) -> list[PaperResolver]:
        return self._resolvers

    def register(self, resolver: PaperResolver) -> None:
        self._resolvers.append(resolver)

    async def parse_draft(self, source: str) -> ParsedPaperDraft:
        for resolver in self._resolvers:
            if not resolver.can_parse(source):
                continue

            try:
                return await resolver.parse(source)
            except (httpx.HTTPError, ElementTree.ParseError, ValueError, KeyError) as exc:
                raise PaperParseError("不支持的链接或解析失败") from exc

        raise PaperParseError("不支持的链接或解析失败")

    async def parse_url(self, source: str) -> dict:
        return (await self.parse_draft(source)).to_api_dict()


registry = PaperParserRegistry()


async def parse_url(source: str) -> dict:
    return await registry.parse_url(source)


async def extract_paper_info(source: str) -> ParsedPaperDraft:
    return await registry.parse_draft(source)
