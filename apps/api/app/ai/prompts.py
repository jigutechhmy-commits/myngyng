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


# Phase 3. REVIEW SCAN — 실사용자 후기 수집/평가
REVIEW_SCAN_SYSTEM = """\
당신은 GOOD CHOICE의 후기 분석 엔진이다.
각 후보 제품에 대해 실사용자 후기(Reddit, 커뮤니티, 전문 리뷰, 쇼핑몰 리뷰 등)를
바탕으로 요약과 평가를 작성한다.
평가 항목: 요구사항 적합도 / 예산 적합도 / 만족도 — 각 1~5점 정수.
필수 기능 누락 여부와 치명적 결함(있다면 한 문장)을 함께 판단한다.
sources에는 참고한 출처 유형이나 커뮤니티 이름을 기재한다(실제 링크가 없으면 출처 유형명).
모든 후보에 대해 하나씩, 입력된 name과 정확히 동일한 name으로 반환한다.
모든 텍스트는 한국어로 작성한다.
"""

REVIEW_SCAN_SCHEMA = {
    "type": "object",
    "properties": {
        "reviews": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "후보 제품명 (입력과 동일)"},
                    "summary": {"type": "string", "description": "후기 요약 (2~4문장)"},
                    "sources": {"type": "array", "items": {"type": "string"}},
                    "fit_score": {"type": "integer", "enum": [1, 2, 3, 4, 5]},
                    "budget_score": {"type": "integer", "enum": [1, 2, 3, 4, 5]},
                    "satisfaction_score": {"type": "integer", "enum": [1, 2, 3, 4, 5]},
                    "missing_required": {"type": "boolean"},
                    "critical_flaw": {"type": ["string", "null"]},
                },
                "required": [
                    "name", "summary", "sources", "fit_score", "budget_score",
                    "satisfaction_score", "missing_required", "critical_flaw",
                ],
                "additionalProperties": False,
            },
        }
    },
    "required": ["reviews"],
    "additionalProperties": False,
}


def review_scan_user_prompt(category_name: str, spec_sheet: dict, budget: int,
                            tolerance_pct: int, usage_text: str,
                            candidates: list[dict]) -> str:
    return f"""\
카테고리: {category_name}
사용자 용도: {usage_text}
최적 사양서: {json.dumps(spec_sheet, ensure_ascii=False)}
예산: {budget:,}원 (±{tolerance_pct}%)

후보 목록:
{json.dumps(candidates, ensure_ascii=False, indent=2)}

각 후보의 실사용 후기를 요약하고 평가하라.
"""


# Phase 5. DIGGING — 제품 세계관 조사 → Decision Narrative
DIGGING_SYSTEM = """\
당신은 GOOD CHOICE의 세계관 조사 엔진이다.
단순 스펙 비교가 아니라 각 제품의 '세계관'을 조사한다:
탄생 배경, 개발 철학, 브랜드 철학, 팬덤, 커뮤니티 평가, 역사, 성공/실패 사례, 숨겨진 이야기.

각 제품에 대해:
- narrative: 제품의 정체성을 한 문장으로 압축한 Decision Narrative
  (예: ThinkPad → "전자제품이 아니라 공구를 만들겠다는 IBM 철학의 후계자")
- story: 세계관 서술 3~6문장
- digging_scores: 철학/역사성/팬덤/독창성/커뮤니티평가/스토리성 각 0~10점 정수
- sources: 근거 출처(공식 자료/인터뷰/커뮤니티 등, 링크가 없으면 출처 유형명)

사실에 근거하되 확인 불가한 내용은 쓰지 않는다. 입력된 name과 동일한 name으로 반환한다.
모든 텍스트는 한국어로 작성한다.
"""

DIGGING_SCHEMA = {
    "type": "object",
    "properties": {
        "narratives": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "narrative": {"type": "string", "description": "한 줄 Decision Narrative"},
                    "story": {"type": "string", "description": "세계관 서술"},
                    "digging_scores": {
                        "type": "object",
                        "properties": {
                            "philosophy": {"type": "integer"},
                            "history": {"type": "integer"},
                            "fandom": {"type": "integer"},
                            "originality": {"type": "integer"},
                            "community": {"type": "integer"},
                            "story": {"type": "integer"},
                        },
                        "required": [
                            "philosophy", "history", "fandom",
                            "originality", "community", "story",
                        ],
                        "additionalProperties": False,
                    },
                    "sources": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["name", "narrative", "story", "digging_scores", "sources"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["narratives"],
    "additionalProperties": False,
}


def digging_user_prompt(category_name: str, candidates: list[dict]) -> str:
    return f"""\
카테고리: {category_name}

1차 통과 후보:
{json.dumps(candidates, ensure_ascii=False, indent=2)}

각 후보 제품의 세계관을 조사하고 Decision Narrative를 작성하라.
"""


# Phase 6. FINAL ENTRY — 최종 카드 구성
FINAL_ENTRY_SYSTEM = """\
당신은 GOOD CHOICE의 최종 카드 작성 엔진이다.
각 후보의 사양, 후기 요약, 세계관(Decision Narrative)을 종합해
월드컵 토너먼트에서 사용자가 비교할 '최종 카드'를 작성한다.

각 카드:
- headline: 제품을 한 문장으로 포장하는 패키징 문구 (광고 카피처럼 매력적으로)
- key_specs: 핵심 사양 요약 3~5개 (짧은 구문)
- pros / cons: 장점/단점 각 2~4개
- review_digest: 실사용 후기 요약 1~2문장
- worldview: 세계관 요약 1~2문장
- recommended_for / not_recommended_for: 추천/비추천 대상 각 1~3개

사용자의 용도와 우선순위 관점에서 작성한다. 입력된 name과 동일한 name으로 반환한다.
모든 텍스트는 한국어로 작성한다.
"""

FINAL_ENTRY_SCHEMA = {
    "type": "object",
    "properties": {
        "cards": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "headline": {"type": "string"},
                    "key_specs": {"type": "array", "items": {"type": "string"}},
                    "pros": {"type": "array", "items": {"type": "string"}},
                    "cons": {"type": "array", "items": {"type": "string"}},
                    "review_digest": {"type": "string"},
                    "worldview": {"type": "string"},
                    "recommended_for": {"type": "array", "items": {"type": "string"}},
                    "not_recommended_for": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "name", "headline", "key_specs", "pros", "cons",
                    "review_digest", "worldview",
                    "recommended_for", "not_recommended_for",
                ],
                "additionalProperties": False,
            },
        }
    },
    "required": ["cards"],
    "additionalProperties": False,
}


def final_entry_user_prompt(usage_text: str, priorities: list[str],
                            candidates: list[dict]) -> str:
    return f"""\
사용자 용도: {usage_text}
우선순위: {", ".join(priorities) if priorities else "미지정"}

후보 정보(사양/후기/세계관 포함):
{json.dumps(candidates, ensure_ascii=False, indent=2)}

각 후보의 최종 카드를 작성하라.
"""
