from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlmodel import Session, select

from app.database import get_session
from app.models import (
    Paper,
    PaperCreate,
    PaperListResponse,
    PaperRead,
    PaperStatus,
    PaperUpdate,
    SortOrder,
    Tag,
    utcnow,
)
from app.pagination import build_pagination_meta


router = APIRouter(prefix="/papers", tags=["papers"])

PAPER_SORT_FIELDS = {
    "priority": Paper.priority,
    "updated_at": Paper.updated_at,
    "created_at": Paper.created_at,
    "pub_year": Paper.pub_year,
    "year": Paper.pub_year,
    "year_desc": Paper.pub_year,
    "last_read_at": Paper.last_read_at,
    "last_read_desc": Paper.last_read_at,
    "title": Paper.title,
    "aka_name": Paper.aka_name,
    "status": Paper.status,
}

DESC_ONLY_SORTS = {"year_desc", "last_read_desc"}


def get_tags_by_ids(session: Session, tag_ids: list[int]) -> list[Tag]:
    if not tag_ids:
        return []

    tags = list(session.exec(select(Tag).where(Tag.id.in_(tag_ids))))
    found_ids = {tag.id for tag in tags}
    missing_ids = sorted(set(tag_ids) - found_ids)
    if missing_ids:
        raise HTTPException(status_code=404, detail=f"Tags not found: {missing_ids}")
    return tags


def validate_paper_identifiers(
    session: Session,
    *,
    arxiv_id: str | None,
    doi: str | None,
    exclude_paper_id: int | None = None,
) -> None:
    if arxiv_id:
        statement = select(Paper).where(Paper.arxiv_id == arxiv_id)
        if exclude_paper_id is not None:
            statement = statement.where(Paper.id != exclude_paper_id)
        if session.exec(statement).first():
            raise HTTPException(status_code=409, detail="arXiv ID already exists.")

    if doi:
        statement = select(Paper).where(Paper.doi == doi)
        if exclude_paper_id is not None:
            statement = statement.where(Paper.id != exclude_paper_id)
        if session.exec(statement).first():
            raise HTTPException(status_code=409, detail="DOI already exists.")


@router.get("", response_model=PaperListResponse)
def list_papers(
    session: Session = Depends(get_session),
    q: str | None = Query(default=None, description="Search title, AKA, author, venue, arXiv ID, or DOI."),
    status_filter: PaperStatus | None = Query(default=None, alias="status"),
    priority: int | None = Query(default=None, ge=1, le=5),
    tag_id: list[int] = Query(default_factory=list),
    is_archived: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="updated_at"),
    sort_order: SortOrder = Query(default=SortOrder.DESC),
) -> PaperListResponse:
    statement = select(Paper).distinct()
    count_statement = select(func.count(func.distinct(Paper.id)))

    if q:
        pattern = f"%{q.strip()}%"
        search_filter = or_(
            Paper.title.ilike(pattern),
            Paper.aka_name.ilike(pattern),
            Paper.authors_display.ilike(pattern),
            Paper.venue.ilike(pattern),
            Paper.arxiv_id.ilike(pattern),
            Paper.doi.ilike(pattern),
        )
        statement = statement.where(search_filter)
        count_statement = count_statement.where(search_filter)
    if status_filter is not None:
        statement = statement.where(Paper.status == status_filter)
        count_statement = count_statement.where(Paper.status == status_filter)
    if priority is not None:
        statement = statement.where(Paper.priority == priority)
        count_statement = count_statement.where(Paper.priority == priority)
    if is_archived is not None:
        statement = statement.where(Paper.is_archived == is_archived)
        count_statement = count_statement.where(Paper.is_archived == is_archived)
    if tag_id:
        statement = statement.join(Paper.tags).where(Tag.id.in_(tag_id))
        count_statement = count_statement.join(Paper.tags).where(Tag.id.in_(tag_id))

    sort_column = PAPER_SORT_FIELDS.get(sort_by)
    if sort_column is None:
        raise HTTPException(
            status_code=422,
            detail={
                "field": "sort_by",
                "allowed_values": sorted(PAPER_SORT_FIELDS),
            },
        )

    total = session.exec(count_statement).one()
    should_sort_desc = sort_order == SortOrder.DESC or sort_by in DESC_ONLY_SORTS
    order_expression = sort_column.desc() if should_sort_desc else sort_column.asc()
    statement = (
        statement.order_by(order_expression, Paper.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    items = list(session.exec(statement))
    return PaperListResponse(
        items=items,
        meta=build_pagination_meta(page=page, per_page=per_page, total=total),
    )


@router.post("", response_model=PaperRead, status_code=status.HTTP_201_CREATED)
def create_paper(payload: PaperCreate, session: Session = Depends(get_session)) -> Paper:
    paper_data = payload.model_dump(exclude={"tag_ids"})
    validate_paper_identifiers(
        session,
        arxiv_id=paper_data.get("arxiv_id"),
        doi=paper_data.get("doi"),
    )
    paper = Paper.model_validate(paper_data)
    paper.tags = get_tags_by_ids(session, payload.tag_ids)

    session.add(paper)
    session.commit()
    session.refresh(paper)
    return paper


@router.get("/{paper_id}", response_model=PaperRead)
def get_paper(paper_id: int, session: Session = Depends(get_session)) -> Paper:
    paper = session.get(Paper, paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
    return paper


@router.patch("/{paper_id}", response_model=PaperRead)
@router.put("/{paper_id}", response_model=PaperRead)
def update_paper(paper_id: int, payload: PaperUpdate, session: Session = Depends(get_session)) -> Paper:
    paper = session.get(Paper, paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")

    updates = payload.model_dump(exclude_unset=True)
    tag_ids = updates.pop("tag_ids", None)
    previous_status = paper.status
    next_status = updates.get("status")
    validate_paper_identifiers(
        session,
        arxiv_id=updates.get("arxiv_id", paper.arxiv_id),
        doi=updates.get("doi", paper.doi),
        exclude_paper_id=paper_id,
    )

    for field, value in updates.items():
        setattr(paper, field, value)

    if tag_ids is not None:
        paper.tags = get_tags_by_ids(session, tag_ids)

    if (
        next_status in {PaperStatus.READING, PaperStatus.COMPLETED}
        and previous_status != next_status
    ):
        paper.last_read_at = utcnow()

    paper.updated_at = utcnow()
    session.add(paper)
    session.commit()
    session.refresh(paper)
    return paper


@router.delete("/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_paper(paper_id: int, session: Session = Depends(get_session)) -> None:
    paper = session.get(Paper, paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")

    session.delete(paper)
    session.commit()
