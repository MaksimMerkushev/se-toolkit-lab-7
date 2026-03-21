import json
import sys
import httpx
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
    messages = [
        {"role": "system", "content": "You are a helpful teaching assistant bot. Use tools to fetch data from the LMS to answer student questions. Always identify labs correctly (e.g., 'lab-01', 'lab-04'). Keep answers concise."},
        {"role": "user", "content": user_query}
    ]

    async with httpx.AsyncClient() as client:
        for _ in range(5):
            try:
                resp = await client.post(
                    f"{LLM_API_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {LLM_API_KEY}",
                        "HTTP-Referer": "https://github.com/innopolis", # Обязательно для OpenRouter
                        "X-Title": "LMS Bot" # Обязательно для OpenRouter
                    },
                    json={"model": LLM_API_MODEL, "messages": messages, "tools": TOOLS, "tool_choice": "auto"},
                    timeout=30.0
                )
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                print(f"[LLM Error] Status {e.response.status_code}: {e.response.text}", file=sys.stderr)
                return f"Error talking to AI: OpenRouter returned {e.response.status_code}. Check console."
            except Exception as e:
                return f"Network Error: {e}"
            
            message = resp.json()["choices"][0]["message"]
            messages.append(message)
            
            if "tool_calls" in message and message["tool_calls"]:
                for tool_call in message["tool_calls"]:
                    fn_name = tool_call["function"]["name"]
                    fn_args = json.loads(tool_call["function"]["arguments"] or "{}")
                    
                    print(f"[tool] LLM called: {fn_name}({json.dumps(fn_args, separators=(',', ':'))})", file=sys.stderr)
                    
                    try:
                        result = await TOOL_MAP[fn_name](fn_args)
                        list_len = len(result) if isinstance(result, list) else 1
                        print(f"[tool] Result: {list_len} items", file=sys.stderr)
                        content = json.dumps(result)
                    except Exception as e:
                        print(f"[tool] Error: {e}", file=sys.stderr)
                        content = json.dumps({"error": str(e)})
                        
                    messages.append({"role": "tool", "tool_call_id": tool_call["id"], "name": fn_name, "content": content})
                
                print(f"[summary] Feeding {len(message['tool_calls'])} tool results back to LLM", file=sys.stderr)
            else:
                return message.get("content", "I couldn't find an answer.")
                
        return "I had to stop thinking to prevent an infinite loop."
