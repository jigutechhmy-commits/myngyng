"""packages/shared/categories 정의를 DB categories 테이블에 동기화한다."""

import json
from pathlib import Path

from app.db.base import SessionLocal
from app.models import Category

SHARED_CATEGORIES_DIR = (
    Path(__file__).resolve().parents[3] / "packages" / "shared" / "categories"
)


def seed() -> None:
    index = json.loads((SHARED_CATEGORIES_DIR / "index.json").read_text(encoding="utf-8"))
    with SessionLocal() as db:
        for entry in index["categories"]:
            detail_path = SHARED_CATEGORIES_DIR / f"{entry['id']}.json"
            spec_schema = {}
            if detail_path.exists():
                spec_schema = json.loads(detail_path.read_text(encoding="utf-8")).get(
                    "spec_schema", {}
                )
            category = db.get(Category, entry["id"]) or Category(id=entry["id"])
            category.name_ko = entry["name_ko"]
            category.enabled = entry["enabled"]
            category.spec_schema = spec_schema
            db.merge(category)
        db.commit()
        print(f"seeded {len(index['categories'])} categories")


if __name__ == "__main__":
    seed()
