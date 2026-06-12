# GOOD CHOICE
## AI 의사결정 엔진 기반 구매 월드컵 서비스
### Product Requirement Document (PRD) v1.0

## 서비스 비전
GOOD CHOICE는 상품 추천 서비스가 아니다.
GOOD CHOICE는 사용자가 자신의 선택에 확신을 가질 수 있도록 돕는 AI 의사결정 플랫폼이다.

### 슬로건
> 비교는 AI가, 결정은 당신이.

---

# 1. 문제 정의

기존 비교 서비스는 스펙, 가격, 순위 중심이다.

하지만 실제 구매 과정은:

1. 내가 무엇을 원하는지 고민
2. 후보 조사
3. 후기 탐색
4. 비교
5. 자기 합리화
6. 구매 결정

GOOD CHOICE는 이 전 과정을 지원한다.

---

# 2. 핵심 철학

좋은 결정 = 좋은 자기합리화

최고의 제품은 존재하지 않는다.
가장 나에게 맞는 제품만 존재한다.

GOOD CHOICE는 사용자가 자신의 선택을 납득할 수 있도록 돕는다.

---

# 3. 사용자 플로우

## STEP 1. 카테고리 선택

예시

- 노트북
- 자동차
- 의자
- 모니터
- 여행지
- 카메라

## STEP 2. 예산 입력

- 목표 예산
- 허용 오차 (%)

예시

250만원 ±10%

## STEP 3. 용도 입력

자연어 입력

예시

- Fusion360 설계
- 소규모 바이브코딩
- 프레젠테이션
- 필기
- 휴대성
- 현장 사용

## STEP 4. 우선순위

1순위
2순위
3순위

## STEP 5. 토너먼트 규모

- 2강
- 4강
- 8강
- 16강
- Auto

---

# 4. Good Choice Engine

## Phase 1. PLAN

### 목적

사용자의 진짜 요구사항 분석

### 출력

최적 사양서

예시

- CPU
- RAM
- 저장장치
- 무게
- 배터리
- 필수 기능

---

## Phase 2. RESEARCH

### 목적

시장 전체 조사

### 출력

후보군 확보

예시

2in1 노트북 시장 내 전체 후보 수집

---

## Phase 3. REVIEW SCAN

### 목적

실사용자 후기 수집

### 우선순위

1. Reddit
2. Discord
3. 제조사 포럼
4. 전문 리뷰
5. Youtube
6. 커뮤니티
7. 쇼핑몰 리뷰

### 평가

- 요구사항 적합도
- 예산 적합도
- 만족도

각 1~5점

---

## Phase 4. LIST UP

### 목적

1차 후보 압축

### 자동 탈락

- 예산 초과
- 필수 기능 없음
- 치명적 결함
- 낮은 만족도

---

## Phase 5. DIGGING

### 핵심 차별화 포인트

단순 비교가 아니라
제품의 세계관을 조사한다.

### 조사 대상

- 탄생 배경
- 개발 철학
- 브랜드 철학
- 팬덤
- 커뮤니티 평가
- 경쟁 제품
- 역사
- 성공 사례
- 실패 사례
- 공급망
- 숨겨진 이야기

### 결과

Decision Narrative 생성

예시

Surface Pro

> 노트북과 태블릿의 경계를 없애기 위한 15년간의 실험

ThinkPad

> 전자제품이 아니라 공구를 만들겠다는 IBM 철학의 후계자

---

## Digging Score

### 항목

- 철학
- 역사성
- 팬덤
- 독창성
- 커뮤니티 평가
- 스토리성

각 10점

---

## Fact Shield

### 목적

허위 정보 차단

### 체크리스트

- 공식 출처
- 인터뷰 근거
- 리뷰 근거
- 출처 링크
- 왜곡 여부 검증
- AI 추론 표시

---

## Phase 6. FINAL ENTRY

### 최종 카드 구성

- 이미지
- 핵심 사양
- 장점
- 단점
- 후기 요약
- 세계관
- 추천 대상
- 비추천 대상
- 패키징 문구

---

## Phase 7. CHOICE

### 월드컵 진행

A vs B

사용자 선택

AI는 정답을 강요하지 않는다.

선택 이유를 분석하고 기록한다.

---

# 5. Decision Journal

사용자의 선택 기록

예시

- 선택 제품
- 선택 이유
- 선택 시점

6개월 후

만족도 재조사

---

# 6. Choice Confidence

최종 추천 신뢰도

예시

- 요구사항 적합도
- 예산 적합도
- 후기 만족도
- 장기 만족도

---

# 7. 기술 아키텍처 (초안)

Frontend
- Next.js
- Tailwind
- shadcn/ui

Backend
- FastAPI

AI Layer
- OpenAI
- Claude
- Deep Research Pipeline

Database
- PostgreSQL

Vector DB
- pgvector

Crawler
- Reddit
- Youtube
- Community Sources

---

# 8. 장기 비전

GOOD CHOICE는 구매 추천 서비스를 넘어

AI Decision Coach

로 진화한다.

목표는

"무엇을 살까?"

가 아니라

"어떤 선택을 할까?"

를 돕는 것이다.
