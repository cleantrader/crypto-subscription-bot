import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database.engine import create_tables
from bot.handlers import user, admin, payment
from bot.middlewares.db import DbSessionMiddleware
from bot.scheduler import run_scheduler          # ← اضافه شد
from database.engine import SessionFactory

logging.basicConfig(level=logging.INFO)

async def main():
    await create_tables()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.update.middleware(DbSessionMiddleware(SessionFactory))

    dp.include_router(admin.router)
    dp.include_router(payment.router)
    dp.include_router(user.router)

    # ربات و scheduler رو همزمان اجرا کن
    await asyncio.gather(
        dp.start_polling(bot),
        run_scheduler(bot)               # ← اضافه شد
    )

if __name__ == "__main__":
    asyncio.run(main())