from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_cors_origins
from app.database import create_db_and_tables
from app.errors import register_exception_handlers
from app.paper_parser import router as paper_parser_router
from app.routers import dev, papers, tag_groups, tags


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="PaperReader API",
    version="0.1.0",
    description="Development API for managing papers, tags, and reading workflow.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(dev.router, prefix="/api")
app.include_router(paper_parser_router, prefix="/api")
app.include_router(tag_groups.router, prefix="/api")
app.include_router(tags.router, prefix="/api")
app.include_router(papers.router, prefix="/api")
