def handle_start() -> str:
    return "Hello! I am your LMS bot. I can help you track deadlines and scores. Type /help to see available commands."

def handle_help() -> str:
    return "Available commands:\n/start - Welcome message\n/help - This message\n/health - Check backend status\n/labs - List available labs"

def handle_health() -> str:
    return "Backend status: OK (Placeholder)"

def handle_labs() -> str:
    return "Available labs: Lab 1, Lab 2, Lab 3 (Placeholder)"

def route_command(command_text: str) -> str:
    """Маршрутизатор: принимает текст, отдает текст ответа."""
    cmd = command_text.strip().split()[0].lower()
    
    if cmd == "/start":
        return handle_start()
    elif cmd == "/help":
        return handle_help()
    elif cmd == "/health":
        return handle_health()
    elif cmd in ["/labs", "what"]: # Заглушка для "what labs are available"
        return handle_labs()
    else:
        return f"Echo (Not implemented yet): {command_text}"
