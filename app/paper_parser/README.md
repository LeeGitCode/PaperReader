# Paper Parser Domain

This package owns paper-link parsing as an isolated business domain.

When adding support for a new paper source, you should only need to read this
directory:

```text
app/paper_parser/
```

You do not need to understand the Paper CRUD, Tags, frontend components, or the
database schema to add a parser.

## Public API

The rest of the backend should use:

```python
from app.paper_parser import parse_url, router
```

- `parse_url(source: str) -> dict`
- `router`: exposes `/api/tasks/parse` and `/api/tasks/{task_id}`

The old `app.parser` module is only a compatibility shim.

## Returned Draft Shape

Every parser must return a `ParsedPaperDraft`:

```python
ParsedPaperDraft(
    title="...",
    authors="Alice, Bob",
    authors_display="Alice et al.",
    year=2026,
    pub_year=2026,
    venue="arXiv",
    pdf_path="",
    pdf_url="https://...",
    status="to_read",
    priority=3,
)
```

Use `status="to_read"` because this is the backend enum value. UI may display it
as `ToRead`.

## Add A New Resolver

1. Create a new file under `app/paper_parser/resolvers/`.

Example:

```python
from app.paper_parser.schema import ParsedPaperDraft


class OpenReviewResolver:
    name = "openreview"

    def can_parse(self, source: str) -> bool:
        return "openreview.net" in source

    async def parse(self, source: str) -> ParsedPaperDraft:
        return ParsedPaperDraft(
            title="...",
            authors="...",
            authors_display="...",
            year=2026,
            pub_year=2026,
            venue="OpenReview",
            pdf_url="...",
        )
```

2. Register it in `app/paper_parser/resolvers/__init__.py`:

```python
from app.paper_parser.resolvers.openreview import OpenReviewResolver

DEFAULT_RESOLVERS = [ArxivResolver(), CrossrefDoiResolver(), OpenReviewResolver()]
```

3. Run:

```bash
.venv/bin/python -m compileall app
```

4. Smoke test:

```bash
.venv/bin/python - <<'PY'
import asyncio
from app.paper_parser import parse_url

async def main():
    print(await parse_url("YOUR_TEST_URL"))

asyncio.run(main())
PY
```

## Task System

`tasks.py` intentionally uses an in-memory dictionary. This keeps the feature
lightweight and avoids Celery/Redis.

Tradeoffs:

- Tasks are lost on backend restart.
- Tasks are local to one process.
- This is fine for the current local-first MVP.

If this app becomes multi-user or deployed across multiple workers, replace
`app/paper_parser/tasks.py` behind the same function names:

- `create_task`
- `get_task`
- `run_parse_task`

The router can stay unchanged.
