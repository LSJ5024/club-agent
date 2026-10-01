"""Tool registry: the single place where tools are connected to the agent.

TOOL_SCHEMAS   -> sent to the LLM (what the model can SEE)
TOOL_FUNCTIONS -> used by agent.py (what actually RUNS)

When you add a tool: import its function and schema, then add both below.
"""
from src.tools.calculator import CALCULATE_SCHEMA, calculate
from src.tools.facility_tools import GET_FACILITY_INFO_SCHEMA, get_facility_info
from src.tools.schedule_tools import (
    CHECK_SCHEDULE_SCHEMA,
    FIND_AVAILABLE_SLOT_SCHEMA,
    RESERVE_FACILITY_SCHEMA,
    check_schedule,
    find_available_slot,
    reserve_facility,
)

TOOL_SCHEMAS = [
    CALCULATE_SCHEMA,
    GET_FACILITY_INFO_SCHEMA,
    CHECK_SCHEDULE_SCHEMA,
    FIND_AVAILABLE_SLOT_SCHEMA,
    RESERVE_FACILITY_SCHEMA,
]

TOOL_FUNCTIONS = {
    "calculate": calculate,
    "get_facility_info": get_facility_info,
    "check_schedule": check_schedule,
    "find_available_slot": find_available_slot,
    "reserve_facility": reserve_facility,
}
