# Tasks

Do ONE task at a time. After each task: run tests, try the scenario, and make sure you understand the code.

Prompt for your AI assistant:
> Read AGENTS.md. Then do Task N from docs/04_tasks.md using docs/03_tool_spec.md. Only touch the files needed.

## Part 1 — Foundation
- [x] **1. Config & LLM client.** `src/config.py` and `src/llm_client.py`, copied unchanged from the café agent. Check: `python -m src.llm_client` prints a reply to "Hello".
- [x] **2. Data store.** `load()` / `save()` in `src/tools/data_store.py`, copied unchanged. Check: `pytest tests -k data_store`.

## Part 2 — First tool & the agent loop
- [x] **3. get_facility_info.** Implemented in `facility_tools.py`, registered in `tools/__init__.py`. Check: `pytest -k get_facility_info`.
- [x] **4. Agent loop.** `src/agent.py` and `src/main.py`, copied unchanged from the café agent — the loop itself knows nothing about facilities. Check: Scenario A.

## Part 3 — Many tools
- [x] **5. check_schedule + calculate.** Implemented and registered. Check: `pytest -k "schedule or calculate"`, Scenario B (first half).
- [x] **6. find_available_slot.** The one tool with no café equivalent — an interval-scheduling search. Implemented and registered. Check: `pytest -k find_available_slot`, Scenario B.
- [x] **7. reserve_facility.** Checks operating hours and conflicts before writing. Implemented and registered. Check: `pytest -k reserve_facility`, Scenario C.
- [x] **8. Make the agent visible.** `agent.py` already prints each tool call and a short result like `🔧 find_available_slot(...) → {"available_slot": {...}}`. Check: run Scenario C and read the steps.

## Part 4 — Context engineering
- [ ] **9. Robustness.** Run Scenario D (unknown facility) and Scenario E (conflict). If the agent fails to recover, improve the tool error messages or `prompts/system_prompt.md` (not the code).
- [ ] **10. History trimming.** Confirm `MAX_HISTORY_MESSAGES` trimming in `agent.py` never cuts between an assistant tool_call message and its tool results. Check: Scenario F.
- [ ] **11. Description experiment.** Change `find_available_slot`'s description to "does stuff". Run Scenario B. What happens? Restore it and write 2 sentences about why in `tests/scenarios.md`.

## Part 5 — Stretch (optional)
- [x] **12. cancel_reservation.** Designed in `docs/03_tool_spec.md` first (type: write), implemented in `schedule_tools.py`, registered, tested (`pytest -k cancel_reservation`).
