from app.paper_parser.exceptions import PaperParseError
from app.paper_parser.registry import parse_url
from app.paper_parser.resolvers.arxiv import ArxivResolver, extract_arxiv_id
from app.paper_parser.resolvers.crossref import CrossrefDoiResolver, extract_doi


async def parse_arxiv(source: str) -> dict:
    return (await ArxivResolver().parse(source)).to_api_dict()


async def parse_doi(source: str) -> dict:
    return (await CrossrefDoiResolver().parse(source)).to_api_dict()


__all__ = [
    "PaperParseError",
    "extract_arxiv_id",
    "extract_doi",
    "parse_arxiv",
    "parse_doi",
    "parse_url",
]
