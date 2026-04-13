from math import ceil

from app.models import PaginationMeta


def build_pagination_meta(*, page: int, per_page: int, total: int) -> PaginationMeta:
    total_pages = ceil(total / per_page) if total else 0
    return PaginationMeta(page=page, per_page=per_page, total=total, total_pages=total_pages)
