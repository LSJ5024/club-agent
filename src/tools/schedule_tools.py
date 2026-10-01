"""Scheduling tools: check bookings, find a free slot, reserve a facility."""
from src.tools import data_store

_UNKNOWN_FACILITY = "Facility '{name}' not found. Call get_facility_info with no arguments to see valid names."


def _to_minutes(hhmm: str) -> int:
    """Convert 'HH:MM' to minutes since midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def _to_hhmm(minutes: int) -> str:
    """Convert minutes since midnight back to 'HH:MM'."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _reservations_for(facility_name: str, date: str) -> list[dict]:
    """Return this facility's reservations on this date, sorted by start time."""
    records = data_store.load("reservations")["records"]
    matches = [r for r in records if r["facility"] == facility_name and r["date"] == date]
    return sorted(matches, key=lambda r: _to_minutes(r["start_time"]))


def check_schedule(facility_name: str, date: str) -> dict:
    """List a facility's reservations on a given date, sorted by start time."""
    facilities = data_store.load("facilities")
    if facility_name not in facilities:
        return {"error": _UNKNOWN_FACILITY.format(name=facility_name)}

    reservations = _reservations_for(facility_name, date)
    return {
        "facility_name": facility_name,
        "date": date,
        "reservations": [
            {"start_time": r["start_time"], "end_time": r["end_time"], "club_name": r["club_name"], "purpose": r["purpose"]}
            for r in reservations
        ],
    }


def find_available_slot(facility_name: str, date: str, duration_minutes: int) -> dict:
    """Find the next free time slot of the given length on a date, honoring operating hours and existing bookings."""
    facilities = data_store.load("facilities")
    if facility_name not in facilities:
        return {"error": _UNKNOWN_FACILITY.format(name=facility_name)}
    if duration_minutes < 1:
        return {"error": "duration_minutes must be at least 1."}

    info = facilities[facility_name]
    open_min = _to_minutes(info["open_time"])
    close_min = _to_minutes(info["close_time"])

    # Walk the day's reservations left to right, looking for the first gap
    # (between "cursor" and the next booking, or between "cursor" and closing
    # time) that is at least duration_minutes long.
    cursor = open_min
    for r in _reservations_for(facility_name, date):
        r_start, r_end = _to_minutes(r["start_time"]), _to_minutes(r["end_time"])
        if r_start - cursor >= duration_minutes:
            slot = {"start_time": _to_hhmm(cursor), "end_time": _to_hhmm(cursor + duration_minutes)}
            return {"facility_name": facility_name, "date": date, "duration_minutes": duration_minutes, "available_slot": slot}
        cursor = max(cursor, r_end)

    if close_min - cursor >= duration_minutes:
        slot = {"start_time": _to_hhmm(cursor), "end_time": _to_hhmm(cursor + duration_minutes)}
        return {"facility_name": facility_name, "date": date, "duration_minutes": duration_minutes, "available_slot": slot}

    return {
        "facility_name": facility_name,
        "date": date,
        "duration_minutes": duration_minutes,
        "available_slot": None,
        "message": "No slot of that length is free that day.",
    }


def reserve_facility(facility_name: str, date: str, start_time: str, end_time: str, club_name: str, purpose: str) -> dict:
    """Reserve a facility for a time range after checking operating hours and conflicts. Call only after user confirmation."""
    facilities = data_store.load("facilities")
    if facility_name not in facilities:
        return {"error": _UNKNOWN_FACILITY.format(name=facility_name)}

    start_min, end_min = _to_minutes(start_time), _to_minutes(end_time)
    if end_min <= start_min:
        return {"error": "end_time must be after start_time."}

    info = facilities[facility_name]
    open_min, close_min = _to_minutes(info["open_time"]), _to_minutes(info["close_time"])
    if start_min < open_min or end_min > close_min:
        return {"error": f"{facility_name} operates {info['open_time']}-{info['close_time']}. Requested time is outside operating hours."}

    for r in _reservations_for(facility_name, date):
        r_start, r_end = _to_minutes(r["start_time"]), _to_minutes(r["end_time"])
        if start_min < r_end and end_min > r_start:
            return {
                "error": (
                    f"{facility_name} is already booked {r['start_time']}-{r['end_time']} on {date} "
                    f"by {r['club_name']}. Call find_available_slot for a free time."
                )
            }

    duration_hours = (end_min - start_min) / 60
    estimated_cost = round(info["hourly_rate"] * duration_hours)

    reservations = data_store.load("reservations")
    reservations["records"].append({
        "facility": facility_name,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "club_name": club_name,
        "purpose": purpose,
    })
    data_store.save("reservations", reservations)

    return {
        "facility_name": facility_name,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "club_name": club_name,
        "purpose": purpose,
        "estimated_cost": estimated_cost,
    }


def cancel_reservation(facility_name: str, date: str, start_time: str) -> dict:
    """Cancel the reservation at a facility/date/start_time. Call only after user confirmation."""
    facilities = data_store.load("facilities")
    if facility_name not in facilities:
        return {"error": _UNKNOWN_FACILITY.format(name=facility_name)}

    reservations = data_store.load("reservations")
    records = reservations["records"]
    for i, r in enumerate(records):
        if r["facility"] == facility_name and r["date"] == date and r["start_time"] == start_time:
            cancelled = records.pop(i)
            data_store.save("reservations", reservations)
            return {
                "facility_name": cancelled["facility"],
                "date": cancelled["date"],
                "start_time": cancelled["start_time"],
                "end_time": cancelled["end_time"],
                "club_name": cancelled["club_name"],
                "purpose": cancelled["purpose"],
                "status": "cancelled",
            }

    return {
        "error": (
            f"No reservation found for {facility_name} on {date} starting at {start_time}. "
            "Call check_schedule to see current bookings."
        )
    }


CHECK_SCHEDULE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "check_schedule",
        "description": "Check existing reservations for a facility on a given date, sorted by start time.",
        "parameters": {
            "type": "object",
            "properties": {
                "facility_name": {"type": "string", "description": "Exact facility name, e.g. '세미나실A'."},
                "date": {"type": "string", "description": "Date as 'YYYY-MM-DD'."},
            },
            "required": ["facility_name", "date"],
        },
    },
}

FIND_AVAILABLE_SLOT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "find_available_slot",
        "description": (
            "Find the next available time slot of the requested length on a given date, avoiding conflicts "
            "with existing reservations and staying within operating hours. Use this before reserving instead "
            "of guessing a free time."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "facility_name": {"type": "string", "description": "Exact facility name, e.g. '세미나실A'."},
                "date": {"type": "string", "description": "Date as 'YYYY-MM-DD'."},
                "duration_minutes": {"type": "integer", "description": "Length of the slot needed, in minutes, at least 1."},
            },
            "required": ["facility_name", "date", "duration_minutes"],
        },
    },
}

RESERVE_FACILITY_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reserve_facility",
        "description": (
            "Reserve a facility for a time range. Rejects the booking if it falls outside operating hours or "
            "conflicts with an existing reservation. Only call after the user confirms."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "facility_name": {"type": "string", "description": "Exact facility name, e.g. '세미나실A'."},
                "date": {"type": "string", "description": "Date as 'YYYY-MM-DD'."},
                "start_time": {"type": "string", "description": "Start time as 'HH:MM'."},
                "end_time": {"type": "string", "description": "End time as 'HH:MM', must be after start_time."},
                "club_name": {"type": "string", "description": "Name of the club making the reservation."},
                "purpose": {"type": "string", "description": "Short reason for the reservation, e.g. '정기 회의'."},
            },
            "required": ["facility_name", "date", "start_time", "end_time", "club_name", "purpose"],
        },
    },
}

CANCEL_RESERVATION_SCHEMA = {
    "type": "function",
    "function": {
        "name": "cancel_reservation",
        "description": "Cancel an existing reservation identified by facility, date, and start time. Only call after the user confirms.",
        "parameters": {
            "type": "object",
            "properties": {
                "facility_name": {"type": "string", "description": "Exact facility name, e.g. '세미나실A'."},
                "date": {"type": "string", "description": "Date as 'YYYY-MM-DD'."},
                "start_time": {"type": "string", "description": "Start time as 'HH:MM', must match an existing reservation."},
            },
            "required": ["facility_name", "date", "start_time"],
        },
    },
}
