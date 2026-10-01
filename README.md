# 🏫 Club Facility Booking Agent

An AI assistant for student club officers who need to reserve shared campus facilities
(seminar rooms, the auditorium, the club room, the studio). Uses **many tools**
(facility info, schedule check, free-slot finder, reservation, cancellation, calculator) to
answer questions and take actions — without ever double-booking a room.

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

## Deploy the web UI (Streamlit Community Cloud)
`app.py` needs a long-lived WebSocket connection, so it belongs on a platform built for
that — not a serverless host like Vercel. [share.streamlit.io](https://share.streamlit.io) is
free and made for exactly this.

1. Push this repo to GitHub (already done for `club-agent`).
2. Go to share.streamlit.io, sign in with GitHub, click **New app**.
3. Pick the repo, branch `main`, main file path `app.py`.
4. Under **Advanced settings → Secrets**, paste the contents of
   `.streamlit/secrets.toml.example` with your real API key filled in. (This replaces
   `.env`, which only exists locally and is never pushed.)
5. Click **Deploy**. You get a public `https://<name>.streamlit.app` URL.

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
