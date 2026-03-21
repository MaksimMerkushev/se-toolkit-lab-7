import sys
import socket
import asyncio
import argparse
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.client.session.aiohttp import AiohttpSession

from config import BOT_TOKEN
from handlers.common.base import route_command

async def run_telegram_bot():
    token = BOT_TOKEN.strip()
    
    # Создаем сессию aiogram
    session = AiohttpSession()
    
    # Внедряем настройки напрямую в инициализатор коннектора, 
    # чтобы избежать TypeError и форсировать IPv4 + отключить SSL-чек
    session._connector_init["family"] = socket.AF_INET
    session._connector_init["ssl"] = False
    
    bot = Bot(token=token, session=session)
    dp = Dispatcher()

    @dp.message()
    async def universal_handler(message: types.Message):
        text = message.text or ""
        # ДОБАВИТЬ AWAIT:
        response = await route_command(text)
        await message.answer(response)

    print("Bot is starting polling (IPv4 + NoSSL mode)...")
    try:
        # skip_updates=True поможет быстрее стартануть, игнорируя старые сообщения
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        print(f"\n[!] Connection Error: {e}")
    finally:
        await session.close()

async def run_test_mode(command: str):
    response = await route_command(command)
    print(response)
    sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LMS Bot")
    parser.add_argument("--test", type=str, help="Run in offline test mode")
    args = parser.parse_args()

    if args.test:
        # ЗАПУСТИТЬ ЧЕРЕЗ ASYNCIO:
        asyncio.run(run_test_mode(args.test))
    else:
        asyncio.run(run_telegram_bot())
# Workflow verification for Task 1
