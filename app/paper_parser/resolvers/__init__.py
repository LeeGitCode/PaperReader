from app.paper_parser.resolvers.acl import ACLResolver
from app.paper_parser.resolvers.acm import ACMResolver
from app.paper_parser.resolvers.arxiv import ArxivResolver
from app.paper_parser.resolvers.crossref import CrossrefDoiResolver
from app.paper_parser.resolvers.html_meta_parser import CVFParser, NeurIPSParser, PMLRParser
from app.paper_parser.resolvers.ieee import IEEEResolver
from app.paper_parser.resolvers.openreview import OpenReviewResolver


DEFAULT_RESOLVERS = [
    IEEEResolver(),
    ACMResolver(),
    ACLResolver(),
    OpenReviewResolver(),
    CVFParser(),
    PMLRParser(),
    NeurIPSParser(),
    ArxivResolver(),
    CrossrefDoiResolver(),
]

__all__ = [
    "ACLResolver",
    "ACMResolver",
    "ArxivResolver",
    "CVFParser",
    "CrossrefDoiResolver",
    "DEFAULT_RESOLVERS",
    "IEEEResolver",
    "NeurIPSParser",
    "OpenReviewResolver",
    "PMLRParser",
]
