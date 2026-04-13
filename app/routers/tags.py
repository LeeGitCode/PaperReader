import random

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlmodel import Session, select

from app.database import get_session
from app.models import SortOrder, Tag, TagCreate, TagGroup, TagListResponse, TagRead, TagUpdate
from app.pagination import build_pagination_meta


router = APIRouter(prefix="/tags", tags=["tags"])

TAG_COLOR_PALETTE = [
    "#DBEAFE",
    "#DCFCE7",
    "#EDE9FE",
    "#FFEDD5",
    "#FCE7F3",
    "#E0F2FE",
    "#FEF3C7",
]

TAG_SORT_FIELDS = {
    "name": Tag.name,
    "normalized_name": Tag.normalized_name,
    "created_at": Tag.created_at,
}


def normalize_tag_name(name: str) -> str:
    return "-".join(name.strip().lower().split())


@router.get("", response_model=TagListResponse)
def list_tags(
    session: Session = Depends(get_session),
    q: str | None = Query(default=None, description="Search by tag name."),
    tag_group_id: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=200),
    sort_by: str = Query(default="name"),
    sort_order: SortOrder = Query(default=SortOrder.ASC),
) -> TagListResponse:
    statement = select(Tag)
    count_statement = select(func.count(Tag.id))
    if q:
        pattern = f"%{q.strip()}%"
        search_filter = (Tag.name.ilike(pattern)) | (Tag.normalized_name.ilike(pattern))
        statement = statement.where(search_filter)
        count_statement = count_statement.where(search_filter)
    if tag_group_id is not None:
        statement = statement.where(Tag.tag_group_id == tag_group_id)
        count_statement = count_statement.where(Tag.tag_group_id == tag_group_id)

    sort_column = TAG_SORT_FIELDS.get(sort_by)
    if sort_column is None:
        raise HTTPException(
            status_code=422,
            detail={"field": "sort_by", "allowed_values": sorted(TAG_SORT_FIELDS)},
        )

    total = session.exec(count_statement).one()
    order_expression = sort_column.asc() if sort_order == SortOrder.ASC else sort_column.desc()
    statement = statement.order_by(order_expression, Tag.id.desc()).offset((page - 1) * per_page).limit(per_page)
    items = list(session.exec(statement))
    return TagListResponse(
        items=items,
        meta=build_pagination_meta(page=page, per_page=per_page, total=total),
    )


@router.post("", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(payload: TagCreate, session: Session = Depends(get_session)) -> Tag:
    normalized_name = payload.normalized_name or normalize_tag_name(payload.name)
    color = payload.color or random.choice(TAG_COLOR_PALETTE)
    if payload.tag_group_id is not None and not session.get(TagGroup, payload.tag_group_id):
        raise HTTPException(status_code=404, detail="Tag group not found.")

    duplicate = session.exec(
        select(Tag).where(
            Tag.normalized_name == normalized_name,
            Tag.tag_group_id == payload.tag_group_id,
        )
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="Tag already exists in this group.")

    tag = Tag.model_validate(payload, update={"normalized_name": normalized_name, "color": color})
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@router.get("/{tag_id}", response_model=TagRead)
def get_tag(tag_id: int, session: Session = Depends(get_session)) -> Tag:
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found.")
    return tag


@router.patch("/{tag_id}", response_model=TagRead)
def update_tag(tag_id: int, payload: TagUpdate, session: Session = Depends(get_session)) -> Tag:
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found.")

    updates = payload.model_dump(exclude_unset=True)
    target_group_id = updates.get("tag_group_id", tag.tag_group_id)
    target_name = updates.get("name", tag.name)
    target_normalized_name = updates.get("normalized_name", normalize_tag_name(target_name))

    if target_group_id is not None and not session.get(TagGroup, target_group_id):
        raise HTTPException(status_code=404, detail="Tag group not found.")

    duplicate = session.exec(
        select(Tag).where(
            Tag.id != tag_id,
            Tag.normalized_name == target_normalized_name,
            Tag.tag_group_id == target_group_id,
        )
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="Tag already exists in this group.")

    updates["normalized_name"] = target_normalized_name
    for field, value in updates.items():
        setattr(tag, field, value)

    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, session: Session = Depends(get_session)) -> None:
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found.")

    session.delete(tag)
    session.commit()
