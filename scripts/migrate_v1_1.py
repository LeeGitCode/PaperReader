from pathlib import Path
import sqlite3
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import DATA_DIR


DATABASE_PATH = DATA_DIR / "paper_reader.db"
DEFAULT_TAG_COLOR = "#E2E8F0"


def column_exists(conn: sqlite3.Connection, table_name: str, column_name: str) -> bool:
    columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return any(column[1] == column_name for column in columns)


def main() -> None:
    if not DATABASE_PATH.exists():
        raise SystemExit(f"Database not found: {DATABASE_PATH}")

    with sqlite3.connect(DATABASE_PATH) as conn:
        if not column_exists(conn, "papers", "last_read_at"):
            conn.execute("ALTER TABLE papers ADD COLUMN last_read_at TEXT")
            print("Added papers.last_read_at")
        else:
            print("papers.last_read_at already exists")

        conn.execute(
            "UPDATE tags SET color = ? WHERE color IS NULL OR trim(color) = ''",
            (DEFAULT_TAG_COLOR,),
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_papers_last_read_at ON papers(last_read_at DESC)"
        )
        conn.commit()

    print("V1.1 migration completed")


if __name__ == "__main__":
    main()
