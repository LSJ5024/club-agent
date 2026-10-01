# 🏫 Club Facility Booking Agent

An AI assistant for student club officers who need to reserve shared campus facilities
(seminar rooms, the auditorium, the club room, the studio). Uses **many tools**
(facility info, schedule check, free-slot finder, reservation, calculator) to answer
questions and take actions — without ever double-booking a room.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then put your API key in .env
```

## Run
```bash
python -m src.main               # chat with the agent
python -m pytest tests           # test tools (no LLM needed)
```

## How to work on this project (vibe coding)
1. Open `docs/04_tasks.md` and pick the next unchecked task.
2. Ask your AI coding assistant:
   > Read AGENTS.md. Then do Task N from docs/04_tasks.md using docs/03_tool_spec.md. Only touch the files needed.
3. Verify: run the tests and try the matching prompt in `tests/scenarios.md`.
4. Understand the code before moving on. You will be asked to explain it.

## Where is the "context"?
| For the coding assistant | For the agent (runtime) |
|---|---|
| `AGENTS.md`, `docs/` | `prompts/system_prompt.md`, tool descriptions, tool results, message history |
