"""Tool tests. No LLM needed.
Run one group:  python -m pytest tests -k get_facility_info
"""
from src.tools.calculator import calculate


# ---- Reused from café template ----
def test_calculate_ok():
    assert calculate("2 * 10000") == {"expression": "2 * 10000", "result": 20000.0}


def test_calculate_error_has_hint():
    assert "error" in calculate("import os")


def test_data_store_roundtrip():
    from src.tools import data_store
    data = data_store.load("facilities")
    data["임시실"] = {"capacity": 1, "open_time": "09:00", "close_time": "18:00", "equipment": [], "hourly_rate": 0}
    data_store.save("facilities", data)
    assert "임시실" in data_store.load("facilities")


# ---- get_facility_info ----
def test_get_facility_info_list_all():
    from src.tools.facility_tools import get_facility_info
    names = {f["facility_name"] for f in get_facility_info()["facilities"]}
    assert names == {"세미나실A", "세미나실B", "대강당", "동아리방", "스튜디오"}


def test_get_facility_info_one():
    from src.tools.facility_tools import get_facility_info
    info = get_facility_info("세미나실A")
    assert info["capacity"] == 20
    assert info["hourly_rate"] == 10000
    assert info["equipment"] == ["프로젝터", "화이트보드"]


def test_get_facility_info_not_found_hint():
    from src.tools.facility_tools import get_facility_info
    assert "get_facility_info" in get_facility_info("소강당")["error"]


# ---- check_schedule ----
def test_check_schedule_ok_sorted():
    from src.tools.schedule_tools import check_schedule
    res = check_schedule("세미나실A", "2026-10-02")["reservations"]
    start_times = [r["start_time"] for r in res]
    assert start_times == sorted(start_times)
    assert "10:00" in start_times and "14:00" in start_times


def test_check_schedule_empty_day():
    from src.tools.schedule_tools import check_schedule
    assert check_schedule("세미나실A", "2026-12-25")["reservations"] == []


def test_check_schedule_not_found_hint():
    from src.tools.schedule_tools import check_schedule
    assert "get_facility_info" in check_schedule("소강당", "2026-10-02")["error"]


# ---- find_available_slot ----
def test_find_available_slot_gap_between_bookings():
    from src.tools.schedule_tools import find_available_slot
    r = find_available_slot("세미나실A", "2026-10-02", 120)
    assert r["available_slot"] == {"start_time": "12:00", "end_time": "14:00"}


def test_find_available_slot_no_reservations_returns_open_time():
    from src.tools.schedule_tools import find_available_slot
    r = find_available_slot("세미나실A", "2026-12-25", 60)
    assert r["available_slot"] == {"start_time": "09:00", "end_time": "10:00"}


def test_find_available_slot_fully_booked_returns_none():
    from src.tools.schedule_tools import find_available_slot
    r = find_available_slot("세미나실A", "2026-10-02", 600)
    assert r["available_slot"] is None


def test_find_available_slot_bad_duration():
    from src.tools.schedule_tools import find_available_slot
    assert "error" in find_available_slot("세미나실A", "2026-10-02", 0)


def test_find_available_slot_not_found_hint():
    from src.tools.schedule_tools import find_available_slot
    assert "get_facility_info" in find_available_slot("소강당", "2026-10-02", 60)["error"]


# ---- reserve_facility ----
def test_reserve_facility_ok():
    from src.tools.schedule_tools import reserve_facility
    r = reserve_facility("세미나실A", "2026-10-02", "12:00", "13:00", "테스트동아리", "테스트 회의")
    assert r["estimated_cost"] == 10000


def test_reserve_facility_persists():
    from src.tools.schedule_tools import check_schedule, reserve_facility
    reserve_facility("세미나실A", "2026-10-02", "12:00", "13:00", "테스트동아리", "테스트 회의")
    res = check_schedule("세미나실A", "2026-10-02")["reservations"]
    assert any(r["club_name"] == "테스트동아리" for r in res)


def test_reserve_facility_conflict_hint():
    from src.tools.schedule_tools import reserve_facility
    r = reserve_facility("세미나실A", "2026-10-02", "10:30", "11:30", "테스트동아리", "테스트 회의")
    assert "find_available_slot" in r["error"]


def test_reserve_facility_outside_hours():
    from src.tools.schedule_tools import reserve_facility
    assert "error" in reserve_facility("세미나실A", "2026-10-02", "08:00", "09:00", "테스트동아리", "테스트 회의")


def test_reserve_facility_bad_time_range():
    from src.tools.schedule_tools import reserve_facility
    assert "error" in reserve_facility("세미나실A", "2026-10-02", "13:00", "12:00", "테스트동아리", "테스트 회의")


def test_reserve_facility_not_found_hint():
    from src.tools.schedule_tools import reserve_facility
    assert "get_facility_info" in reserve_facility("소강당", "2026-10-02", "12:00", "13:00", "테스트동아리", "테스트 회의")["error"]


# ---- cancel_reservation ----
def test_cancel_reservation_ok():
    from src.tools.schedule_tools import cancel_reservation
    r = cancel_reservation("세미나실A", "2026-10-02", "10:00")
    assert r["status"] == "cancelled"
    assert r["club_name"] == "컴퓨터공학회"


def test_cancel_reservation_removes_from_schedule():
    from src.tools.schedule_tools import cancel_reservation, check_schedule
    cancel_reservation("세미나실A", "2026-10-02", "10:00")
    res = check_schedule("세미나실A", "2026-10-02")["reservations"]
    assert all(r["start_time"] != "10:00" for r in res)


def test_cancel_reservation_frees_the_slot():
    from src.tools.schedule_tools import cancel_reservation, find_available_slot
    cancel_reservation("세미나실A", "2026-10-02", "10:00")
    r = find_available_slot("세미나실A", "2026-10-02", 120)
    assert r["available_slot"] == {"start_time": "09:00", "end_time": "11:00"}


def test_cancel_reservation_no_match_hint():
    from src.tools.schedule_tools import cancel_reservation
    r = cancel_reservation("세미나실A", "2026-10-02", "11:00")
    assert "check_schedule" in r["error"]


def test_cancel_reservation_not_found_hint():
    from src.tools.schedule_tools import cancel_reservation
    assert "get_facility_info" in cancel_reservation("소강당", "2026-10-02", "10:00")["error"]


# ---- Registry check ----
def test_registry_consistent():
    from src.tools import TOOL_FUNCTIONS, TOOL_SCHEMAS
    names = {s["function"]["name"] for s in TOOL_SCHEMAS}
    assert names == set(TOOL_FUNCTIONS)
    assert len(names) >= 5
