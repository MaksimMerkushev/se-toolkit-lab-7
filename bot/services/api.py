import httpx
from config import LMS_API_URL, LMS_API_KEY

def get_headers():
    return {"Authorization": f"Bearer {LMS_API_KEY}"}

async def fetch_data(method: str, endpoint: str, params=None):
    async with httpx.AsyncClient() as client:
        resp = await client.request(method, f"{LMS_API_URL}{endpoint}", params=params, headers=get_headers(), timeout=10.0)
        resp.raise_for_status()
        return resp.json()

# Старые функции для жестких команд (/labs, /scores)
async def fetch_items(): return await fetch_data("GET", "/items/")
async def fetch_pass_rates(lab: str): return await fetch_data("GET", "/analytics/pass-rates", {"lab": lab})

# Новые обертки для инструментов LLM
async def get_items(args: dict): return await fetch_data("GET", "/items/")
async def get_learners(args: dict): return await fetch_data("GET", "/learners/")
async def get_scores(args: dict): return await fetch_data("GET", "/analytics/scores", {"lab": args.get("lab")})
async def get_pass_rates_tool(args: dict): return await fetch_data("GET", "/analytics/pass-rates", {"lab": args.get("lab")})
async def get_timeline(args: dict): return await fetch_data("GET", "/analytics/timeline", {"lab": args.get("lab")})
async def get_groups(args: dict): return await fetch_data("GET", "/analytics/groups", {"lab": args.get("lab")})
async def get_top_learners(args: dict): return await fetch_data("GET", "/analytics/top-learners", {"lab": args.get("lab"), "limit": args.get("limit", 5)})
async def get_completion_rate(args: dict): return await fetch_data("GET", "/analytics/completion-rate", {"lab": args.get("lab")})
async def trigger_sync(args: dict): return await fetch_data("POST", "/pipeline/sync")

# Карта инструментов для вызова по имени
TOOL_MAP = {
    "get_items": get_items,
    "get_learners": get_learners,
    "get_scores": get_scores,
    "get_pass_rates": get_pass_rates_tool,
    "get_timeline": get_timeline,
    "get_groups": get_groups,
    "get_top_learners": get_top_learners,
    "get_completion_rate": get_completion_rate,
    "trigger_sync": trigger_sync
}
# Workflow verification for Task 2
