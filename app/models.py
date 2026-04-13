from datetime import datetime, timezone
from enum import Enum
from typing import Any
from typing import List

from sqlalchemy import JSON, Column, Index, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PaperStatus(str, Enum):
    TO_READ = "to_read"
    READING = "reading"
    COMPLETED = "completed"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class PaperTagLink(SQLModel, table=True):
    __tablename__ = "paper_tags"

    paper_id: int | None = Field(default=None, foreign_key="papers.id", primary_key=True)
    tag_id: int | None = Field(default=None, foreign_key="tags.id", primary_key=True)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)


class TagGroupBase(SQLModel):
    code: str = Field(index=True, unique=True, max_length=64)
    display_name: str = Field(max_length=100)
    description: str | None = None


class TagGroup(TagGroupBase, table=True):
    __tablename__ = "tag_groups"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)

    tags: List["Tag"] = Relationship(back_populates="tag_group")


class TagBase(SQLModel):
    name: str = Field(max_length=100)
    normalized_name: str = Field(index=True, max_length=100)
    color: str = Field(default="#E2E8F0", max_length=32)
    description: str | None = None
    tag_group_id: int | None = Field(default=None, foreign_key="tag_groups.id")


class Tag(TagBase, table=True):
    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint("tag_group_id", "normalized_name", name="uq_tags_group_normalized_name"),
    )

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)

    tag_group: TagGroup | None = Relationship(back_populates="tags")
    papers: List["Paper"] = Relationship(back_populates="tags", link_model=PaperTagLink)


class PaperBase(SQLModel):
    title: str
    aka_name: str | None = None
    authors_display: str | None = None
    venue: str | None = None
    pub_year: int | None = Field(default=None, ge=1900, le=3000)
    pub_month: int | None = Field(default=None, ge=1, le=12)
    status: PaperStatus = Field(default=PaperStatus.TO_READ)
    priority: int = Field(default=3, ge=1, le=5)
    pdf_path: str | None = None
    pdf_url: str | None = None
    code_url: str | None = None
    notes: str | None = None
    last_read_at: datetime | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    arxiv_id: str | None = None
    doi: str | None = None
    is_archived: bool = False


class Paper(PaperBase, table=True):
    __tablename__ = "papers"
    __table_args__ = (
        Index("idx_papers_status_priority_updated", "status", "priority", "updated_at"),
        Index("idx_papers_pub_year", "pub_year"),
        Index("idx_papers_last_read_at", "last_read_at"),
        Index("idx_papers_aka_name", "aka_name"),
    )

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)

    tags: List[Tag] = Relationship(back_populates="papers", link_model=PaperTagLink)


class TagGroupCreate(TagGroupBase):
    pass


class TagGroupUpdate(SQLModel):
    code: str | None = Field(default=None, max_length=64)
    display_name: str | None = Field(default=None, max_length=100)
    description: str | None = None


class TagGroupRead(TagGroupBase):
    id: int
    created_at: datetime


class TagCreate(SQLModel):
    name: str = Field(max_length=100)
    normalized_name: str | None = Field(default=None, max_length=100)
    color: str | None = Field(default=None, max_length=32)
    description: str | None = None
    tag_group_id: int | None = None


class TagUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=100)
    normalized_name: str | None = Field(default=None, max_length=100)
    color: str | None = Field(default=None, max_length=32)
    description: str | None = None
    tag_group_id: int | None = None


class TagRead(SQLModel):
    id: int
    name: str
    normalized_name: str
    color: str
    description: str | None
    created_at: datetime
    tag_group: TagGroupRead | None = None


class PaperCreate(PaperBase):
    tag_ids: list[int] = Field(default_factory=list)


class PaperUpdate(SQLModel):
    title: str | None = None
    aka_name: str | None = None
    authors_display: str | None = None
    venue: str | None = None
    pub_year: int | None = Field(default=None, ge=1900, le=3000)
    pub_month: int | None = Field(default=None, ge=1, le=12)
    status: PaperStatus | None = None
    priority: int | None = Field(default=None, ge=1, le=5)
    pdf_path: str | None = None
    pdf_url: str | None = None
    code_url: str | None = None
    notes: str | None = None
    last_read_at: datetime | None = None
    metadata_json: dict[str, Any] | None = None
    arxiv_id: str | None = None
    doi: str | None = None
    is_archived: bool | None = None
    tag_ids: list[int] | None = None


class PaperRead(SQLModel):
    id: int
    title: str
    aka_name: str | None
    authors_display: str | None
    venue: str | None
    pub_year: int | None
    pub_month: int | None
    status: PaperStatus
    priority: int
    pdf_path: str | None
    pdf_url: str | None
    code_url: str | None
    notes: str | None
    last_read_at: datetime | None
    metadata_json: dict[str, Any]
    arxiv_id: str | None
    doi: str | None
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    tags: list[TagRead] = Field(default_factory=list)


class PaginationMeta(SQLModel):
    page: int
    per_page: int
    total: int
    total_pages: int


class PaperListResponse(SQLModel):
    items: list[PaperRead]
    meta: PaginationMeta


class TagListResponse(SQLModel):
    items: list[TagRead]
    meta: PaginationMeta


class TagGroupListResponse(SQLModel):
    items: list[TagGroupRead]
    meta: PaginationMeta


class SeedResult(SQLModel):
    tag_groups_created: int
    tags_created: int
    papers_created: int
