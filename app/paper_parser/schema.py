from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ParsedPaperDraft:
    title: str = ""
    authors: str = ""
    authors_display: str = ""
    year: int | None = None
    pub_year: int | None = None
    venue: str = ""
    pdf_path: str = ""
    pdf_url: str = ""
    status: str = "to_read"
    priority: int = 3
    arxiv_id: str | None = None
    doi: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_api_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "title": self.title,
            "authors": self.authors,
            "authors_display": self.authors_display,
            "year": self.year,
            "pub_year": self.pub_year,
            "venue": self.venue,
            "pdf_path": self.pdf_path,
            "pdf_url": self.pdf_url,
            "status": self.status,
            "priority": self.priority,
        }

        if self.arxiv_id:
            payload["arxiv_id"] = self.arxiv_id
        if self.doi:
            payload["doi"] = self.doi
        if self.extra:
            payload["extra"] = self.extra

        return payload
