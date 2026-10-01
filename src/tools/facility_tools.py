"""Facility info tools."""
from src.tools import data_store


def get_facility_info(facility_name: str | None = None) -> dict:
    """Get one facility's details, or list all facilities if facility_name is omitted."""
    facilities = data_store.load("facilities")

    if facility_name is None:
        return {
            "facilities": [
                {"facility_name": name, "capacity": info["capacity"], "hourly_rate": info["hourly_rate"]}
                for name, info in facilities.items()
            ]
        }

    if facility_name not in facilities:
        return {"error": f"Facility '{facility_name}' not found. Call get_facility_info with no arguments to see valid names."}

    info = facilities[facility_name]
    return {
        "facility_name": facility_name,
        "capacity": info["capacity"],
        "open_time": info["open_time"],
        "close_time": info["close_time"],
        "equipment": info["equipment"],
        "hourly_rate": info["hourly_rate"],
    }


GET_FACILITY_INFO_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_facility_info",
        "description": "Get a facility's capacity, operating hours, equipment, and hourly rental rate. Omit facility_name to list all facilities.",
        "parameters": {
            "type": "object",
            "properties": {
                "facility_name": {
                    "type": "string",
                    "description": "Exact facility name, e.g. '세미나실A'. Omit to list all facilities.",
                }
            },
            "required": [],
        },
    },
}
