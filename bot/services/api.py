import httpx
from config import LMS_API_URL, LMS_API_KEY

def get_headers():
    return {"Authorization": f"Bearer {LMS_API_KEY}"}

async def fetch_items() -> list:
    """Получает список всех элементов (лаб и тасок)."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{LMS_API_URL}/items/", headers=get_headers(), timeout=5.0)
        resp.raise_for_status()
        return resp.json()

async def fetch_pass_rates(lab_id: str) -> list:
    """Получает статистику по конкретной лабе."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{LMS_API_URL}/analytics/pass-rates", params={"lab": lab_id}, headers=get_headers(), timeout=5.0)
        resp.raise_for_status()
        return resp.json()
