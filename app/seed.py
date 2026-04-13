from sqlmodel import Session, select

from app.models import Paper, PaperStatus, Tag, TagGroup
from app.routers.tags import normalize_tag_name


SEED_TAG_GROUPS = [
    {"code": "area", "display_name": "Research Area", "description": "High-level research directions."},
    {"code": "method", "display_name": "Method", "description": "Algorithms, model families, and techniques."},
    {"code": "system", "display_name": "System", "description": "Training systems and infrastructure topics."},
    {"code": "task", "display_name": "Task", "description": "Concrete tasks or evaluation targets."},
]

SEED_TAGS = [
    {"group_code": "area", "name": "Anomaly Detection", "color": "#2563eb"},
    {"group_code": "area", "name": "Distributed Training", "color": "#16a34a"},
    {"group_code": "area", "name": "LLM", "color": "#dc2626"},
    {"group_code": "method", "name": "Representation Learning", "color": "#7c3aed"},
    {"group_code": "method", "name": "Self-Supervised Learning", "color": "#0891b2"},
    {"group_code": "method", "name": "MoE", "color": "#ea580c"},
    {"group_code": "system", "name": "FSDP", "color": "#4b5563"},
    {"group_code": "system", "name": "Megatron-LM", "color": "#0f766e"},
    {"group_code": "task", "name": "Defect Detection", "color": "#be123c"},
]

SAMPLE_PAPERS = [
    {
        "title": "Attention Is All You Need",
        "aka_name": "Transformer",
        "authors_display": "Vaswani et al.",
        "venue": "NeurIPS",
        "pub_year": 2017,
        "status": PaperStatus.COMPLETED,
        "priority": 5,
        "pdf_url": "https://arxiv.org/abs/1706.03762",
        "arxiv_id": "1706.03762",
        "tag_names": ["LLM", "Representation Learning"],
    },
    {
        "title": "Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism",
        "aka_name": "Megatron-LM",
        "authors_display": "Shoeybi et al.",
        "venue": "arXiv",
        "pub_year": 2019,
        "status": PaperStatus.TO_READ,
        "priority": 5,
        "pdf_url": "https://arxiv.org/abs/1909.08053",
        "code_url": "https://github.com/NVIDIA/Megatron-LM",
        "arxiv_id": "1909.08053",
        "tag_names": ["Distributed Training", "Megatron-LM", "LLM"],
    },
]


def seed_database(session: Session, *, include_sample_papers: bool = False) -> dict[str, int]:
    result = {"tag_groups_created": 0, "tags_created": 0, "papers_created": 0}

    groups_by_code: dict[str, TagGroup] = {}
    for group_data in SEED_TAG_GROUPS:
        group = session.exec(select(TagGroup).where(TagGroup.code == group_data["code"])).first()
        if not group:
            group = TagGroup(**group_data)
            session.add(group)
            session.commit()
            session.refresh(group)
            result["tag_groups_created"] += 1
        groups_by_code[group.code] = group

    tags_by_name: dict[str, Tag] = {}
    for tag_data in SEED_TAGS:
        group = groups_by_code[tag_data["group_code"]]
        normalized_name = normalize_tag_name(tag_data["name"])
        tag = session.exec(
            select(Tag).where(Tag.tag_group_id == group.id, Tag.normalized_name == normalized_name)
        ).first()
        if not tag:
            tag = Tag(
                name=tag_data["name"],
                normalized_name=normalized_name,
                color=tag_data["color"],
                tag_group_id=group.id,
            )
            session.add(tag)
            session.commit()
            session.refresh(tag)
            result["tags_created"] += 1
        tags_by_name[tag.name] = tag
    if include_sample_papers:
        for sample_paper in SAMPLE_PAPERS:
            paper_data = sample_paper.copy()
            arxiv_id = paper_data["arxiv_id"]
            existing = session.exec(select(Paper).where(Paper.arxiv_id == arxiv_id)).first()
            if existing:
                continue

            tag_names = paper_data.pop("tag_names")
            paper = Paper(**paper_data)
            paper.tags = [tags_by_name[name] for name in tag_names if name in tags_by_name]
            session.add(paper)
            session.commit()
            result["papers_created"] += 1

    return result
