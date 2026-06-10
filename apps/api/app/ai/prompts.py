"""Good Choice Engine Phase별 프롬프트와 출력 스키마."""

import json

# Phase 1. PLAN — 사용자의 진짜 요구사항 분석 → 최적 사양서
PLAN_SYSTEM = """\
당신은 GOOD CHOICE의 구매 의사결정 엔진이다.
사용자의 예산, 용도, 우선순위를 분석해 해당 카테고리의 '최적 사양서'를 작성한다.
스펙 나열이 아니라 사용자의 진짜 요구사항(spec sheet)을 도출하는 것이 목적이다.
각 사양 항목에는 구체적인 권장 값을 제시하고, 마지막에 근거를 요약한다.
모든 텍스트는 한국어로 작성한다.
"""

PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string", "description": "사양서 한 줄 요약"},
        "fields": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "label_ko": {"type": "string"},
                    "value": {"type": "string", "description": "권장 사양 값"},
                },
                "required": ["key", "label_ko", "value"],
                "additionalProperties": False,
            },
        },
        "rationale": {"type": "string", "description": "권장 근거 요약"},
    },
    "required": ["summary", "fields", "rationale"],
    "additionalProperties": False,
}


def plan_user_prompt(category_name: str, spec_fields: list, budget: int,
                     tolerance_pct: int, usage_text: str, priorities: list[str]) -> str:
    return f"""\
카테고리: {category_name}
사양 항목 정의: {json.dumps(spec_fields, ensure_ascii=False)}
목표 예산: {budget:,}원 (허용 오차 ±{tolerance_pct}%)
용도(사용자 입력 원문): {usage_text}
우선순위(1~3순위): {", ".join(priorities) if priorities else "미지정"}

위 입력을 바탕으로 최적 사양서를 작성하라.
"""


# Phase 2. RESEARCH — 시장 전체 조사 → 후보군 확보
RESEARCH_SYSTEM = """\
당신은 GOOD CHOICE의 시장 조사 엔진이다.
주어진 최적 사양서와 예산을 기준으로 현재 시장에서 구할 수 있는 후보(candidate) 제품을
폭넓게 수집한다. 특정 브랜드에 치우치지 말고 시장 전체를 커버하라.
가격은 한국 시장 기준 원화로 추정하고, 확실하지 않은 값은 보수적으로 추정한다.
8~16개의 후보를 반환한다. 모든 텍스트는 한국어로 작성한다.
"""

RESEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "candidates": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "brand": {"type": "string"},
                    "price": {"type": "integer", "description": "예상 가격(원)"},
                    "specs": {
                        "type": "object",
                        "description": "사양 항목 key → 값",
                        "additionalProperties": False,
                        "properties": {
                            "cpu": {"type": "string"},
                            "ram_gb": {"type": "number"},
                            "storage_gb": {"type": "number"},
                            "weight_kg": {"type": "number"},
                            "battery_hours": {"type": "number"},
                        },
                    },
                },
                "required": ["name", "brand", "price", "specs"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["candidates"],
    "additionalProperties": False,
}


def research_user_prompt(category_name: str, spec_sheet: dict, budget: int,
                         tolerance_pct: int) -> str:
    return f"""\
카테고리: {category_name}
최적 사양서: {json.dumps(spec_sheet, ensure_ascii=False)}
예산: {budget:,}원 (±{tolerance_pct}%)

이 사양서에 부합하는 시장 후보군을 수집하라.
예산을 크게 벗어나는 제품은 제외하되, 허용 오차 범위의 제품은 포함한다.
"""
