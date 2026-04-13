from datetime import datetime
import re


def normalize_space(value: str) -> str:
    return " ".join(value.split())


def extract_year(value: str) -> int | None:
    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).year
    except ValueError:
        match = re.search(r"\d{4}", value)
        return int(match.group(0)) if match else None


def format_authors_display(authors: list[str]) -> str:
    if not authors:
        return ""

    if len(authors) == 1:
        return authors[0]

    return f"{authors[0]} et al."
