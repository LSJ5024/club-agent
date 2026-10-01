# 프로젝트 브리프 — 동아리 시설 예약 에이전트

> Advanced Business Programming · Week 5 · Team Practice
> 카페 에이전트의 형식을 그대로 가져오고, 아이디어만 "동아리 시설 예약"으로 바꾼 프로젝트입니다.
>
> 🔗 **배포 링크**: https://club-agent-gyzwxho2qpq3k9tetz7bcj.streamlit.app/

---

## 1. 팀

| 역할 | 담당자 | 담당 도구 | 담당 파일 |
|---|---|---|---|
| Lead + Designer | 이상준 | `get_facility_info`, `find_available_slot` | `docs/01_brief.md`, `docs/03_tool_spec.md`, `src/tools/facility_tools.py`, `src/tools/schedule_tools.py`(find_available_slot) |
| Driver + Tester | 이한들 | `check_schedule`, `reserve_facility`, `cancel_reservation` | `src/tools/schedule_tools.py`(check_schedule, reserve_facility, cancel_reservation), `tests/scenarios.md`, `tests/test_tools.py` |

> `schedule_tools.py`는 두 사람의 도구가 함께 들어 있는 파일입니다 — 수정 전 서로 공유하고 작업하세요.
> 두 사람 모두 어시스턴트가 쓴 코드를 전부 읽고, 자기 담당 도구는 시연에서 직접 설명할 수 있어야 합니다.

---

## 2. 목표

동아리 임원(총무/대표)이 학교 시설(세미나실, 대강당, 동아리방, 스튜디오)을 예약할 때 쓰는
커맨드라인·웹 비서를 만든다. 임원이 자연어로 질문하면, 어시스턴트는 **도구**를 호출해
시설 정보를 확인하고, 기존 예약과 겹치지 않는 빈 시간을 찾고, 예약을 기록한다.

---

## 3. 사용자

동아리 임원 1명. 비기술적 사용자. "지금 이 시간 비어 있어?", "언제가 비어 있어?" 같은
질문에 빠르고 정확하게 답해야 한다.

---

## 4. 어시스턴트가 할 수 있는 일

- 시설 정보 조회: 수용 인원, 운영 시간, 설비, 시간당 대관료 (`get_facility_info`)
- 특정 날짜의 기존 예약 현황 조회 (`check_schedule`)
- 기존 예약과 겹치지 않는 빈 시간대 탐색 (`find_available_slot`)
- 대관료 등 금액 계산 (`calculate`, 카페 템플릿에서 재사용)
- 운영시간·충돌 여부를 검증한 뒤 예약 기록, **사용자 확인 후에만 실행** (`reserve_facility`)
- 기존 예약 취소, **사용자 확인 후에만 실행** (`cancel_reservation`)

---

## 5. 범위 밖

- 웹 UI 외의 실제 배포(인증, 다중 사용자 동시 접속)
- 실제 데이터베이스, 실제 결제, 외부 캘린더 API 연동
- 동시에 여러 임원이 예약하는 동시성 처리

---

## 6. 성공 기준

- 빈 시간/충돌 여부를 절대 추측하지 않는다 — 모든 판단은 도구 결과에서 나온다.
- 2~3개 도구가 연쇄로 필요한 질문에 답할 수 있다 (정보 조회 → 빈 시간 탐색 → 예약).
- 존재하지 않는 시설명처럼 도구 오류가 나도 당황하지 않고 회복한다.
- 데이터를 바꾸는 `reserve_facility`는 실행 전 반드시 사용자 확인을 거친다.

---

## 7. 카페 에이전트와 다른 점

"이름만 바꾸기" 테스트 기준으로, `find_available_slot`은 카페로 바꿔 말하면 의미가 통하지
않는 유일한 도구다 (`check_schedule`도 마찬가지). 카페는 "같은 시간에 같은 자리를 두 손님이
다툰다"는 문제가 없지만, 시설 예약은 **시간 구간 사이의 충돌**을 계산해야 한다는 점이
근본적으로 다르다. 자세한 비교는 `docs/03_tool_spec.md`와 발표 브리핑 참고.

---

## 8. 기술 스택 / 아키텍처

- Python 3.11, `openai` SDK (OpenAI 호환 API — Groq)
- 모델: `openai/gpt-oss-120b` (처음 쓴 `gpt-oss-20b`는 확인 후에도 쓰기 도구를 호출하지 않거나
  오류 회복 중 시설명을 지어내는 문제가 있어 교체함)
- 인터페이스: CLI (`src/main.py`) + Streamlit 웹 UI (`app.py`, `streamlit run app.py`)
- 데이터: `data/facilities.json`, `data/reservations.json` (로컬 JSON, 가짜 데이터)
- 에이전트 루프·설정·LLM 클라이언트는 카페 에이전트에서 그대로 복사 (도메인 지식 없음)

---

## 9. 프로젝트 구조

```
club-facility-agent/
├── AGENTS.md                 # AI 코딩 어시스턴트 지침
├── README.md                 # 설치·실행 방법
├── PROJECT_BRIEF.md          # 이 파일
├── app.py                    # Streamlit 웹 UI
├── docs/
│   ├── 01_brief.md           # 과제 템플릿 형식의 브리프
│   ├── 02_architecture.md    # 아키텍처 문서
│   ├── 03_tool_spec.md       # 도구 명세 (코드보다 먼저 작성)
│   └── 04_tasks.md           # 구현 태스크 체크리스트
├── data/
│   ├── facilities.json
│   └── reservations.json
├── prompts/
│   └── system_prompt.md
├── src/
│   ├── agent.py / config.py / llm_client.py / main.py   # 카페 템플릿 그대로
│   └── tools/
│       ├── calculator.py         # 재사용
│       ├── facility_tools.py     # 신규
│       └── schedule_tools.py     # 신규
└── tests/
    ├── scenarios.md
    └── test_tools.py
```

---

## 10. 실행 방법

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # API 키 입력

python -m src.main               # CLI로 대화
streamlit run app.py             # 웹 UI
python -m pytest tests           # 도구 테스트 (LLM 불필요)
```

---

## 11. 진행 상황

- [x] 도구 5개 설계 및 구현 (read 2, write 2, compute 1) — 전부 완료, pytest 26개 통과
- [x] 시나리오 3개(연쇄 호출 / 쓰기 전 확인 / 오류 회복) + 취소 시나리오 라이브 검증 완료
- [x] Streamlit 웹 UI 추가 구현 (Streamlit Community Cloud 배포 준비 완료)
- [x] 스트레치: `cancel_reservation` 도구
- [ ] Task 9~11: 강건성 실험, 히스토리 트리밍 확인, description 실험 (`docs/04_tasks.md` 참고)

---

## 12. 참고 자료

- **배포된 에이전트(웹 UI)**: https://club-agent-gyzwxho2qpq3k9tetz7bcj.streamlit.app/
- GitHub 저장소: https://github.com/LSJ5024/club-agent
- 도구 명세: `docs/03_tool_spec.md`
- 테스트 시나리오: `tests/scenarios.md`
- 발표 브리핑(비교·데모 스크립트): https://claude.ai/artifact/7rRb9z2nsdzZx9SkSoFnvH
