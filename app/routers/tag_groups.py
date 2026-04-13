from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlmodel import Session, select

from app.database import get_session
from app.models import SortOrder, TagGroup, TagGroupCreate, TagGroupListResponse, TagGroupRead, TagGroupUpdate
from app.pagination import build_pagination_meta


router = APIRouter(prefix="/tag-groups", tags=["tag-groups"])

TAG_GROUP_SORT_FIELDS = {
    "code": TagGroup.code,
    "display_name": TagGroup.display_name,
    "created_at": TagGroup.created_at,
}


@router.get("", response_model=TagGroupListResponse)
def list_tag_groups(
    session: Session = Depends(get_session),
    q: str | None = Query(default=None, description="Search by code or display name."),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=200),
    sort_by: str = Query(default="display_name"),
    sort_order: SortOrder = Query(default=SortOrder.ASC),
) -> TagGroupListResponse:
    statement = select(TagGroup)
    count_statement = select(func.count(TagGroup.id))
    if q:
        pattern = f"%{q.strip()}%"
        search_filter = (TagGroup.code.ilike(pattern)) | (TagGroup.display_name.ilike(pattern))
        statement = statement.where(search_filter)
        count_statement = count_statement.where(search_filter)

    sort_column = TAG_GROUP_SORT_FIELDS.get(sort_by)
    if sort_column is None:
        raise HTTPException(
            status_code=422,
            detail={"field": "sort_by", "allowed_values": sorted(TAG_GROUP_SORT_FIELDS)},
        )

    total = session.exec(count_statement).one()
    order_expression = sort_column.asc() if sort_order == SortOrder.ASC else sort_column.desc()
    statement = statement.order_by(order_expression, TagGroup.id.desc()).offset((page - 1) * per_page).limit(per_page)
    items = list(session.exec(statement))
    return TagGroupListResponse(
        items=items,
        meta=build_pagination_meta(page=page, per_page=per_page, total=total),
    )


@router.post("", response_model=TagGroupRead, status_code=status.HTTP_201_CREATED)
def create_tag_group(payload: TagGroupCreate, session: Session = Depends(get_session)) -> TagGroup:
    existing = session.exec(select(TagGroup).where(TagGroup.code == payload.code)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Tag group code already exists.")

    tag_group = TagGroup.model_validate(payload)
    session.add(tag_group)
    session.commit()
    session.refresh(tag_group)
    return tag_group


@router.get("/{tag_group_id}", response_model=TagGroupRead)
def get_tag_group(tag_group_id: int, session: Session = Depends(get_session)) -> TagGroup:
    tag_group = session.get(TagGroup, tag_group_id)
    if not tag_group:
        raise HTTPException(status_code=404, detail="Tag group not found.")
    return tag_group


@router.patch("/{tag_group_id}", response_model=TagGroupRead)
def update_tag_group(
    tag_group_id: int,
    payload: TagGroupUpdate,
    session: Session = Depends(get_session),
) -> TagGroup:
    tag_group = session.get(TagGroup, tag_group_id)
    if not tag_group:
        raise HTTPException(status_code=404, detail="Tag group not found.")

    updates = payload.model_dump(exclude_unset=True)
    if "code" in updates:
        duplicate = session.exec(
            select(TagGroup).where(TagGroup.code == updates["code"], TagGroup.id != tag_group_id)
        ).first()
        if duplicate:
            raise HTTPException(status_code=409, detail="Tag group code already exists.")

    for field, value in updates.items():
        setattr(tag_group, field, value)

    session.add(tag_group)
    session.commit()
    session.refresh(tag_group)
    return tag_group


@router.delete("/{tag_group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag_group(tag_group_id: int, session: Session = Depends(get_session)) -> None:
    tag_group = session.get(TagGroup, tag_group_id)
    if not tag_group:
        raise HTTPException(status_code=404, detail="Tag group not found.")

    session.delete(tag_group)
    session.commit()
