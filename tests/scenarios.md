# Test Scenarios

Run `python -m src.main` and type each prompt. Compare the tool calls with the expected ones.
The exact order may vary slightly; what matters is that the agent uses tools instead of guessing.

| # | Prompt | Expected tool calls | What to check |
|---|---|---|---|
| A | 대강당은 몇 명까지 들어갈 수 있고 시간당 얼마야? | `get_facility_info("대강당")` | capacity 200, hourly_rate 50,000 |
| B | 세미나실A는 10월 2일에 언제 비어 있어? 2시간짜리로. | `get_facility_info` or `check_schedule` → `find_available_slot` | Free slot avoids 10:00-12:00 and 14:00-16:00, e.g. 12:00-14:00 or 16:00-18:00 |
| C (3-tool chain) | 세미나실A 10월 2일 2시간 빈 시간에 토론동아리 이름으로 예약해 줘. 대관료도 알려줘. | `find_available_slot` → (asks to confirm) → `reserve_facility` | Confirms first; books the found slot; estimated_cost matches hourly_rate × 2 |
| D (error recovery) | 소강당 10월 2일 일정 알려줘. (no such facility) | `check_schedule` → error → `get_facility_info` | Recovers, lists valid facility names, then answers |
| E (confirm before write) | 대강당을 10월 3일 18시~21시에 총학생회 이름으로 예약해 줘. | (asks to confirm) → `check_schedule` or `reserve_facility` → conflict error → explains | Existing 18:00-21:00 booking causes a conflict error; agent explains instead of double-booking |
| F | Chat for 15+ turns, then ask "내가 제일 처음에 뭐라고 물어봤지?" | — | No crash; notice what the agent forgets after trimming |
| G (cancel) | 세미나실A 10월 2일 14시 예약 취소해 줘. | (asks to confirm) → `cancel_reservation` | Confirms first; the 14:00-16:00 토론동아리 booking disappears from check_schedule |

> After testing C, reset data: remove the new record from `data/reservations.json`.
