import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter()

# 모노레포 공통 카테고리 정의 (packages/shared/categories)
SHARED_CATEGORIES_DIR = Path(__file__).resolve().parents[4] / "packages" / "shared" / "categories"


@router.get("")
def list_categories() -> dict:
    index = json.loads((SHARED_CATEGORIES_DIR / "index.json").read_text(encoding="utf-8"))
    return index


@router.get("/{category_id}")
def get_category(category_id: str) -> dict:
    path = SHARED_CATEGORIES_DIR / f"{category_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="category not found")
    return json.loads(path.read_text(encoding="utf-8"))
