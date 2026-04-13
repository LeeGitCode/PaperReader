from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.models import SeedResult
from app.seed import seed_database


router = APIRouter(prefix="/dev", tags=["dev"])


@router.post("/seed", response_model=SeedResult)
def seed_dev_data(
    include_sample_papers: bool = Query(default=False),
    session: Session = Depends(get_session),
) -> dict[str, int]:
    return seed_database(session, include_sample_papers=include_sample_papers)
