"""LLM 프로바이더 추상화.

ANTHROPIC_API_KEY가 설정되면 Claude를 사용하고, 없으면 개발/테스트용
MockProvider로 폴백한다. 모든 호출은 JSON 스키마 기반 구조화 출력을 받는다.
"""

import json
from typing import Protocol

from app.core.config import settings


class LLMProvider(Protocol):
    def complete_json(self, *, system: str, user: str, schema: dict) -> dict:
        """system/user 프롬프트로 schema를 만족하는 JSON 응답을 반환한다."""
        ...


class AnthropicProvider:
    def __init__(self, api_key: str, model: str) -> None:
        import anthropic

        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def complete_json(self, *, system: str, user: str, schema: dict) -> dict:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=8192,
            thinking={"type": "adaptive"},
            system=system,
            messages=[{"role": "user", "content": user}],
            output_config={"format": {"type": "json_schema", "schema": schema}},
        )
        text = next(block.text for block in response.content if block.type == "text")
        return json.loads(text)


class MockProvider:
    """API 키 없이 전체 플로우를 검증하기 위한 결정적 응답 프로바이더."""

    def complete_json(self, *, system: str, user: str, schema: dict) -> dict:
        from app.ai import mock_data

        properties = schema.get("properties", {})
        if "reviews" in properties:
            return mock_data.LAPTOP_REVIEWS
        if "candidates" in properties:
            return mock_data.LAPTOP_CANDIDATES
        if "fields" in properties:
            return mock_data.LAPTOP_SPEC_SHEET
        raise ValueError("MockProvider: unknown schema shape")


def get_provider() -> LLMProvider:
    if settings.anthropic_api_key:
        return AnthropicProvider(
            api_key=settings.anthropic_api_key,
            model=settings.anthropic_model,
        )
    return MockProvider()
