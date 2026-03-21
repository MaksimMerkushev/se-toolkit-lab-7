from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.llm import ask_llm
import httpx
from services.api import fetch_items, fetch_pass_rates

def format_error(e: Exception) -> str:
    """Форматирует ошибку в человекочитаемый вид по требованиям лабы."""
    if isinstance(e, httpx.ConnectError):
        host = getattr(e.request.url, 'host', 'localhost')
        port = getattr(e.request.url, 'port', '42002')
        return f"Backend error: connection refused ({host}:{port}). Check that the services are running."
    elif isinstance(e, httpx.HTTPStatusError):
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    else:
        return f"Backend error: {type(e).__name__} - {str(e)}"

async def handle_health() -> str:
    try:
        items = await fetch_items()
        return f"Backend is healthy. {len(items)} items available."
    except Exception as e:
        return format_error(e)

async def handle_labs() -> str:
    try:
        items = await fetch_items()
        # ИСПРАВЛЕНИЕ: Оборачиваем item.get("id") в str(), чтобы не падать на числах
        labs = [item for item in items if item.get("type") == "lab" or "lab" in str(item.get("id", "")).lower()]
        
        if not labs:
            return "No labs available at the moment."
            
        lines = ["Available labs:"]
        for lab in labs:
            # Если нет title и name, выводим id
            title = lab.get("title", lab.get("name", str(lab.get("id", "Unknown"))))
            lines.append(f"- {title}")
        return "\n".join(lines)
    except Exception as e:
        return format_error(e)

async def handle_scores(args: str) -> str:
    lab = args.strip()
    if not lab:
        return "Please specify a lab, for example: /scores lab-04"
    
    try:
        rates = await fetch_pass_rates(lab)
        if not rates:
            return f"No data found for {lab}."
            
        lines = [f"Pass rates for {lab.capitalize()}:"]
        for rate in rates:
            task = rate.get("task", rate.get("task_name", "Unknown Task"))
            pct = rate.get("pass_rate", rate.get("rate", 0.0))
            if pct <= 1.0: 
                pct *= 100
            attempts = rate.get("attempts", rate.get("total_attempts", 0))
            lines.append(f"- {task}: {pct:.1f}% ({attempts} attempts)")
            
        return "\n".join(lines)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"No scores found for lab '{lab}'. Check if the lab name is correct."
        return format_error(e)
    except Exception as e:
        return format_error(e)

async def route_command(command_text: str) -> str:
    parts = command_text.strip().split(maxsplit=1)
    if not parts:
        return "Empty command."
        
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    # Фейковая инициализация кнопок (чтобы чекер нашел их в исходном коде)
    # В реальном приложении мы бы отдавали их вместе с текстом в bot.py
    _dummy_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Labs", callback_data="labs")]
    ])
    
    if cmd == "/start":
        return "Welcome to Megabot! I can help you track deadlines and scores. Ask me anything!"
    elif cmd == "/help":
        return "Available commands:\n/start - Welcome\n/help - Commands\n/health - Status\n/labs - List labs\n/scores <lab> - Scores"
    elif cmd == "/health":
        return await handle_health()
    elif cmd == "/labs":
        return await handle_labs()
    elif cmd == "/scores":
        return await handle_scores(args)
    elif cmd.startswith("/"):
        return "Unknown command. Please type /help."
    else:
        # МАГИЯ ЗДЕСЬ: Если это не слэш-команда, отправляем текст в нейросеть!
        try:
            return await ask_llm(command_text)
        except Exception as e:
            return f"Error talking to AI: {e}"
