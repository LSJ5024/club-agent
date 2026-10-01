# Tool Specifications

Write the spec BEFORE implementing a tool. The "Purpose" line becomes the tool description the LLM reads.

## Tool map

| Tool | Type | Owner | File |
|---|---|---|---|
| get_facility_info | read | 이상준 | src/tools/facility_tools.py |
| find_available_slot | compute | 이상준 | src/tools/schedule_tools.py |
| check_schedule | read | 이한들 | src/tools/schedule_tools.py |
| reserve_facility | write | 이한들 | src/tools/schedule_tools.py |
| cancel_reservation | write | 이한들 | src/tools/schedule_tools.py |
| calculate | compute | (reused, already in template) | src/tools/calculator.py |

## Template
```
## Tool: <name>
- File: src/tools/<file>.py
- Purpose: <one clear sentence — this is what the LLM sees>
- Type: read | write | compute
- Parameters: <name> (<type>, required|optional) — <description>
- Returns: <example JSON>
- Errors: <when> → <example error JSON with a hint>
- Example request: "<a user sentence that should trigger this tool>"
```

---

## Tool: get_facility_info
- File: src/tools/facility_tools.py
- Purpose: Get a facility's capacity, operating hours, equipment, and hourly rental rate. Omit facility_name to list all facilities.
- Type: read
- Parameters: facility_name (string, optional) — exact facility name, e.g. "세미나실A"
- Returns (one facility): `{"facility_name": "세미나실A", "capacity": 20, "open_time": "09:00", "close_time": "22:00", "equipment": ["프로젝터", "화이트보드"], "hourly_rate": 10000}`
- Returns (no facility_name): `{"facilities": [{"facility_name": "세미나실A", "capacity": 20, "hourly_rate": 10000}, ...]}`
- Errors: unknown facility → `{"error": "Facility '소강당' not found. Call get_facility_info with no arguments to see valid names."}`
- Example request: "대강당은 몇 명까지 들어갈 수 있어?"

## Tool: check_schedule
- File: src/tools/schedule_tools.py
- Purpose: Check existing reservations for a facility on a given date, sorted by start time.
- Type: read
- Parameters:
  - facility_name (string, required) — exact facility name, e.g. "세미나실A"
  - date (string, required) — "YYYY-MM-DD"
- Returns: `{"facility_name": "세미나실A", "date": "2026-10-02", "reservations": [{"start_time": "10:00", "end_time": "12:00", "club_name": "컴퓨터공학회", "purpose": "스터디 모임"}]}`
- Errors: unknown facility → `{"error": "Facility '소강당' not found. Call get_facility_info with no arguments to see valid names."}`
- Example request: "세미나실A는 10월 2일에 언제 예약돼 있어?"

## Tool: find_available_slot
- File: src/tools/schedule_tools.py
- Purpose: Find the next available time slot of the requested length on a given date, avoiding conflicts with existing reservations and staying within operating hours. Use this before reserving instead of guessing a free time.
- Type: compute
- Parameters:
  - facility_name (string, required)
  - date (string, required) — "YYYY-MM-DD"
  - duration_minutes (integer, required) — length of the slot needed, must be ≥ 1
- Returns (found): `{"facility_name": "세미나실A", "date": "2026-10-02", "duration_minutes": 60, "available_slot": {"start_time": "12:00", "end_time": "13:00"}}`
- Returns (not found): `{"facility_name": "세미나실A", "date": "2026-10-02", "duration_minutes": 480, "available_slot": null, "message": "No slot of that length is free that day."}`
- Errors:
  - unknown facility → `{"error": "Facility '소강당' not found. Call get_facility_info with no arguments to see valid names."}`
  - duration_minutes < 1 → `{"error": "duration_minutes must be at least 1."}`
- Example request: "세미나실A에서 10월 2일에 2시간 비는 시간 있어?"

## Tool: reserve_facility
- File: src/tools/schedule_tools.py
- Purpose: Reserve a facility for a time range. Rejects the booking if it falls outside operating hours or conflicts with an existing reservation. Only call after the user confirms.
- Type: write
- Parameters:
  - facility_name (string, required)
  - date (string, required) — "YYYY-MM-DD"
  - start_time (string, required) — "HH:MM"
  - end_time (string, required) — "HH:MM", must be after start_time
  - club_name (string, required)
  - purpose (string, required)
- Returns: `{"facility_name": "세미나실A", "date": "2026-10-02", "start_time": "12:00", "end_time": "13:00", "club_name": "토론동아리", "purpose": "회의", "estimated_cost": 10000}`
- Errors:
  - unknown facility → `{"error": "Facility '소강당' not found. Call get_facility_info with no arguments to see valid names."}`
  - end_time ≤ start_time → `{"error": "end_time must be after start_time."}`
  - outside operating hours → `{"error": "세미나실A operates 09:00–22:00. Requested time is outside operating hours."}`
  - time conflict → `{"error": "세미나실A is already booked 10:00-12:00 on 2026-10-02 by 컴퓨터공학회. Call find_available_slot for a free time."}`
- Example request: "세미나실A를 10월 2일 12시부터 1시간 동안 토론동아리 회의로 예약해 줘."

## Tool: cancel_reservation
- File: src/tools/schedule_tools.py
- Purpose: Cancel an existing reservation identified by facility, date, and start time. Only call after the user confirms.
- Type: write
- Parameters:
  - facility_name (string, required)
  - date (string, required) — "YYYY-MM-DD"
  - start_time (string, required) — "HH:MM", must match an existing reservation's start time
- Returns: `{"facility_name": "세미나실A", "date": "2026-10-02", "start_time": "10:00", "end_time": "12:00", "club_name": "컴퓨터공학회", "purpose": "스터디 모임", "status": "cancelled"}`
- Errors:
  - unknown facility → `{"error": "Facility '소강당' not found. Call get_facility_info with no arguments to see valid names."}`
  - no matching reservation → `{"error": "No reservation found for 세미나실A on 2026-10-02 starting at 11:00. Call check_schedule to see current bookings."}`
- Example request: "세미나실A 10월 2일 10시 예약 취소해 줘."
