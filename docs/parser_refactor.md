# Parser Refactor Notes

The paper-link parsing business has been moved out of the main app flow.

## New Ownership Boundary

Parser-specific code now lives in:

```text
app/paper_parser/
```

This includes:

- normalized draft schema
- parser exceptions
- parser resolver protocol
- ArXiv resolver
- Crossref DOI resolver
- resolver registry
- in-memory async task state machine
- FastAPI task router

## Compatibility

The old modules remain as thin compatibility shims:

- `app/parser.py`
- `app/routers/tasks.py`

New code should prefer:

```python
from app.paper_parser import parse_url
```

and:

```python
from app.paper_parser import router as paper_parser_router
```

## Why This Helps Codex

Future parser work can be scoped to:

```text
app/paper_parser/README.md
app/paper_parser/resolvers/
app/paper_parser/registry.py
```

Codex does not need to inspect:

- frontend components
- Paper CRUD routes
- Tag CRUD routes
- database migrations
- UI state management

unless the task explicitly changes those areas.
