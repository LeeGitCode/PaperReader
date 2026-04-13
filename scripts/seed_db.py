from argparse import ArgumentParser
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlmodel import Session

from app.database import create_db_and_tables, engine
from app.seed import seed_database


def main() -> None:
    parser = ArgumentParser(description="Seed PaperReader development data.")
    parser.add_argument(
        "--include-sample-papers",
        action="store_true",
        help="Also create a small set of sample paper records.",
    )
    args = parser.parse_args()

    create_db_and_tables()
    with Session(engine) as session:
        result = seed_database(session, include_sample_papers=args.include_sample_papers)

    print(result)


if __name__ == "__main__":
    main()
