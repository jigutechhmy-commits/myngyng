# GOOD CHOICE — 작업 계획 (MVP 로드맵) v1

기준 문서: [`docs/PRD_v1.md`](./PRD_v1.md)

---

## 0. MVP 정의

PRD 전체 기능을 한 번에 구현하지 않고, **단일 카테고리(노트북)** 로
"STEP 1~5 입력 → Good Choice Engine Phase 1~7 → Decision Journal /
Choice Confidence" 까지의 **엔드투엔드 플로우**를 먼저 동작시킨다.

MVP 단계에서 단순화하는 부분:

- **크롤러 / Deep Research 파이프라인**: 실시간 크롤링 대신, AI(OpenAI/Claude) +
  외부 검색 API 결과를 활용한 "축약형 리서치"로 대체. 데이터 구조와
  인터페이스는 추후 실제 크롤러로 교체 가능하도록 설계.
- **카테고리**: 노트북 1종만 지원하되, 카테고리별 사양 스키마를
  데이터 기반으로 확장 가능하게 설계.
- **Fact Shield**: 출처 링크 수집 + "AI 추론 표시" 플래그 정도만 우선 구현.
  자동 왜곡 검증 로직은 Post-MVP.

---

## 1. 마일스톤 개요

상태 표기 원칙: 작업 착수 시 `progress`, 완료 시 `done`, 미착수는 `todo`.

| 마일스톤 | 내용 | PRD 매핑 | 상태 |
|---|---|---|---|
| M0 | 프로젝트 셋업 (모노레포, DB, 인프라 골격) | 7장 아키텍처 | done |
| M1 | 사용자 입력 플로우 UI | 3장 STEP 1~5 | progress |
| M2 | PLAN & RESEARCH (사양서 + 후보군) | 4장 Phase 1~2 | todo |
| M3 | REVIEW SCAN & LIST UP (후기 평가 + 1차 압축) | 4장 Phase 3~4 | todo |
| M4 | DIGGING & FINAL ENTRY (세계관/Decision Narrative + 카드) | 4장 Phase 5~6 | todo |
| M5 | CHOICE (토너먼트 UI) | 4장 Phase 7 | todo |
| M6 | Decision Journal & Choice Confidence | 5~6장 | todo |
| M7 | Post-MVP 고도화 (실 크롤러, 멀티 카테고리, Fact Shield 강화) | 장기 비전 | todo |

권장 진행 순서: M0 → M1 → M2 → M3 → M4 → M5 → M6 (순차), M7은 별도 백로그.

---

## 2. 기술 스택 & 레포 구조

PRD 7장 기준.

```
/apps
  /web        # Next.js + Tailwind + shadcn/ui
  /api        # FastAPI (Good Choice Engine)
/packages
  /shared     # 공통 타입/스키마 (카테고리 스펙, 카드 모델 등)
/docs
  PRD_v1.md
  PLAN.md
```

- DB: PostgreSQL + pgvector (제품/리뷰/후기 임베딩 검색용)
- AI Layer: OpenAI / Claude API 클라이언트 (Phase별 프롬프트 모듈화)

> 참고: 레포 루트에 있던 `project_manager.zip`은 본 프로젝트와 무관한
> 기존 산출물로 보이며, 본 로드맵에서는 다루지 않는다. 필요 시 별도
> 정리 여부를 확인할 것.

---

## 3. 마일스톤별 작업 항목

### M0. 프로젝트 셋업 — `done`
- [x] 모노레포 구조 생성 (`apps/web`, `apps/api`, `packages/shared`)
- [x] Next.js + Tailwind + shadcn/ui 초기화
  - shadcn 레지스트리(ui.shadcn.com)가 본 실행 환경에서 차단되어 components.json과
    기본 컴포넌트(button/card/input/label/badge/radio-group/progress)를 수동 작성
- [x] FastAPI 프로젝트 초기화 (uvicorn, 기본 라우팅, CORS)
- [x] PostgreSQL + pgvector 도커/마이그레이션 셋업 (Alembic, `0001_initial`)
- [x] 환경변수/시크릿 관리 구조 (.env.example, AI API 키 자리)
- [x] 카테고리 스펙 스키마 정의 (packages/shared/categories/laptop.json + 시드 스크립트)

### M1. 사용자 입력 플로우 (STEP 1~5)
- [ ] STEP1 카테고리 선택 UI (노트북만 활성)
- [ ] STEP2 예산 입력 (목표 예산 + 허용 오차 %)
- [ ] STEP3 용도 자연어 입력 UI
- [ ] STEP4 우선순위 선택 (1~3순위)
- [ ] STEP5 토너먼트 규모 선택 (2/4/8/16강, Auto)
- [ ] 입력값을 하나의 "요청 세션" 객체로 백엔드에 전달하는 API 설계

### M2. PLAN & RESEARCH (Phase 1~2)
- [ ] **PLAN**: 사용자 입력(예산/용도/우선순위) → AI 프롬프트로 "최적 사양서" 생성
  - 출력 스키마: CPU, RAM, 저장장치, 무게, 배터리, 필수 기능
- [ ] **RESEARCH**: 사양서 기반 시장 후보군 수집
  - MVP: AI + 검색 API로 후보 리스트(이름/스펙/가격) 생성, DB에 저장
  - 후보 데이터 모델 정의 (제품 마스터 테이블)
- [ ] PLAN/RESEARCH 결과를 사용자에게 중간 확인용으로 노출하는 화면(선택)

### M3. REVIEW SCAN & LIST UP (Phase 3~4)
- [ ] **REVIEW SCAN**: 후보별 후기 수집/요약 (MVP: AI 기반 요약 + 출처 링크)
  - 우선순위 소스(Reddit/커뮤니티/리뷰 등)는 Post-MVP에서 실제 크롤러로 대체
  - 요구사항 적합도 / 예산 적합도 / 만족도 (각 1~5점) 산출
- [ ] **LIST UP**: 자동 탈락 로직 구현
  - 예산 초과 / 필수 기능 없음 / 치명적 결함 / 낮은 만족도 기준 필터
- [ ] 1차 후보 리스트 결과 화면

### M4. DIGGING & FINAL ENTRY (Phase 5~6)
- [ ] **DIGGING**: 제품별 "세계관" 조사 → Decision Narrative 생성
  - 조사 항목: 탄생 배경/개발철학/브랜드철학/팬덤/커뮤니티평가/경쟁제품/역사/성공·실패사례/공급망/숨겨진 이야기
  - Digging Score 산출 (철학/역사성/팬덤/독창성/커뮤니티평가/스토리성, 각 10점)
- [ ] **Fact Shield (1차)**: 출처 링크 수집 + AI 추론 여부 표시 플래그
- [ ] **FINAL ENTRY**: 최종 카드 데이터 모델 및 UI
  - 이미지/핵심 사양/장점/단점/후기 요약/세계관/추천 대상/비추천 대상/패키징 문구

### M5. CHOICE — 토너먼트 (Phase 7)
- [ ] 토너먼트 브래킷 UI (선택된 강수에 따라 동적 생성)
- [ ] A vs B 카드 비교 화면
- [ ] 사용자 선택 입력 + "선택 이유" 기록(선택형 또는 자유 입력)
- [ ] 토너먼트 진행/결과 상태 관리 (백엔드 세션)

### M6. Decision Journal & Choice Confidence
- [ ] Decision Journal 데이터 모델: 선택 제품/선택 이유/선택 시점
- [ ] Choice Confidence 점수 계산: 요구사항 적합도/예산 적합도/후기 만족도/장기 만족도
- [ ] 최종 추천 결과 화면(Choice Confidence 표시 포함)
- [ ] 6개월 후 만족도 재조사 트리거 설계 (알림/스케줄러는 Post-MVP 가능)

### M7. Post-MVP 백로그
- [ ] 실제 크롤러 파이프라인 (Reddit/Discord/제조사 포럼/Youtube/커뮤니티/쇼핑몰 리뷰)
- [ ] Deep Research Pipeline 고도화 (자동 출처 검증 포함 Fact Shield)
- [ ] 멀티 카테고리 확장 (자동차/의자/모니터/여행지/카메라)
- [ ] 6개월 후 만족도 재조사 알림 시스템
- [ ] AI Decision Coach 방향성 (대화형 의사결정 코칭)

---

## 4. 핵심 데이터 모델 (초안)

- `category`: 카테고리별 사양 스키마 정의
- `request_session`: 사용자 입력(예산/용도/우선순위/토너먼트 규모)
- `candidate_product`: RESEARCH 단계에서 수집된 후보 제품
- `review_summary`: 후보별 후기 요약 + 적합도/예산/만족도 점수
- `decision_narrative`: DIGGING 결과(세계관, Digging Score, Fact Shield 메타)
- `final_entry_card`: FINAL ENTRY 카드 데이터
- `tournament`: 토너먼트 진행 상태 및 라운드별 선택 기록
- `decision_journal_entry`: 최종 선택/이유/시점 + Choice Confidence 점수

---

## 5. 의사결정이 필요한 항목 (선결정 권장)

- AI Provider 우선순위 및 비용 한도 (OpenAI vs Claude, Phase별 모델 선택)
- MVP에서 "실제 시장 데이터" 신뢰도 수준 (AI 생성 데이터 vs 실 검색 결과 혼합 비율)
- 외부 검색 API 선정 (예: 네이버/구글 검색 API 등)
- pgvector 활용 범위 (리뷰 임베딩 검색을 MVP에 포함할지 여부)

---

## 6. MVP Definition of Done

- 사용자가 STEP1~5 입력을 완료하면, 노트북 카테고리 기준으로
  Good Choice Engine이 Phase1~7을 거쳐 토너먼트를 생성한다.
- 토너먼트 진행 후 Decision Journal에 선택 결과/이유가 저장되고,
  Choice Confidence 점수가 함께 표시된다.
- 모든 후보/카드 데이터에 출처(AI 생성 여부 포함) 정보가 표기된다.
