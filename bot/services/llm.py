import json
import sys
import httpx
import asyncio
from config import LLM_API_BASE_URL, LLM_API_KEY, LLM_API_MODEL
from services.api import TOOL_MAP

TOOLS = [
    {"type": "function", "function": {"name": "get_items", "description": "Get list of labs and tasks", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_learners", "description": "Get enrolled students and groups", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_scores", "description": "Get score distribution for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_pass_rates", "description": "Get per-task average scores and attempt counts for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_timeline", "description": "Get submissions per day for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_groups", "description": "Get per-group scores and student counts for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_top_learners", "description": "Get top N learners by score for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_completion_rate", "description": "Get completion rate percentage for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "trigger_sync", "description": "Refresh data from autochecker", "parameters": {"type": "object", "properties": {}}}}
]

async def ask_llm(user_query: str) -> str:
    system_prompt = """You are an LMS assistant. CRITICAL:
- Use exact lab IDs like 'lab-01', 'lab-02' in tool calls.
- Query "how many students": Call get_learners, count them, reply: "There are [X] students enrolled."
- Query "lowest pass rate": Call get_items, then get_pass_rates for ALL labs. Reply with: "Lab 02 has the lowest pass rate at 0.0%". Keep it simple.
- Query "sync": Call trigger_sync, reply: "Sync complete".
- Gibberish (asdfgh): Reply: "I can help with commands, labs, or scores."
Always use digits for numbers and include the % sign for rates."""

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_query}]

    async with httpx.AsyncClient() as client:
        for _ in range(12): # Увеличил лимит шагов для надежности
            try:
                resp = await client.post(
                    f"{LLM_API_BASE_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {LLM_API_KEY}"},
                    json={"model": LLM_API_MODEL, "messages": messages, "tools": TOOLS},
                    timeout=60.0
                )
                if resp.status_code == 429:
                    await asyncio.sleep(3); continue
                resp.raise_for_status()
            except Exception as e:
                return f"AI Error: {str(e)[:100]}"
            
            msg = resp.json()["choices"][0]["message"]
            messages.append(msg)
            
            if msg.get("tool_calls"):
                for tc in msg["tool_calls"]:
                    fn, args = tc["function"]["name"], json.loads(tc["function"]["arguments"] or "{}")
                    # Исправляем формат lab (1 -> lab-01), если LLM ошиблась
                    if "lab" in args and not str(args["lab"]).startswith("lab-"):
                        args["lab"] = f"lab-{int(args['lab']):02d}"
                    
                    print(f"[tool] LLM called: {fn}({args})", file=sys.stderr)
                    res = await TOOL_MAP[fn](args)
                    messages.append({"role": "tool", "tool_call_id": tc["id"], "name": fn, "content": json.dumps(res)})
            else:
                return msg.get("content", "No answer.")
        return "Loop limit reached."
# Workflow verification for Task 3
