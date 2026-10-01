"""The agent: keeps conversation history and runs the tool-calling loop."""
import json

from src import config
from src.llm_client import chat
from src.tools import TOOL_FUNCTIONS, TOOL_SCHEMAS


class CafeAgent:
    def __init__(self):
        self.system_prompt = config.SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
        self.history: list = []  # user, assistant, and tool messages (NOT the system prompt)

    def _build_context(self) -> list:
        """Return the messages to send to the LLM: system prompt + (trimmed) history."""
        cutoff = max(0, len(self.history) - config.MAX_HISTORY_MESSAGES)
        # never start the window on a tool result — back up to its assistant tool_call message
        while cutoff > 0 and self.history[cutoff]["role"] == "tool":
            cutoff -= 1
        trimmed = self.history[cutoff:]
        return [{"role": "system", "content": self.system_prompt}] + trimmed

    def _execute_tool(self, name: str, arguments_json: str) -> dict:
        """Run one tool safely. Never raise: return {"error": ...} on any problem."""
        if name not in TOOL_FUNCTIONS:
            return {"error": f"Unknown tool '{name}'."}
        try:
            arguments = json.loads(arguments_json) if arguments_json else {}
            return TOOL_FUNCTIONS[name](**arguments)
        except Exception as e:
            return {"error": f"Tool '{name}' failed: {e}"}

    def run(self, user_input: str) -> str:
        """Handle one user message and return the final answer text."""
        self.history.append({"role": "user", "content": user_input})

        for _ in range(config.MAX_TOOL_ROUNDS):
            response = chat(self._build_context(), TOOL_SCHEMAS)
            self.history.append(response.model_dump(exclude_none=True))

            if not response.tool_calls:
                return response.content

            for call in response.tool_calls:
                result = self._execute_tool(call.function.name, call.function.arguments)
                print(f"🔧 {call.function.name}({call.function.arguments}) → {json.dumps(result)}")
                self.history.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result),
                })

        return "Sorry, I could not finish this request."
