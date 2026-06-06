import asyncio
import logging
from aiogram import Bot
from database.engine import SessionFactory
from database import queries

logger = logging.getLogger(__name__)


async def notify_expiring(bot: Bot):
    """اشتراک‌هایی که ۲۴ ساعت دیگه منقضی می‌شن → پیام هشدار"""
    async with SessionFactory() as session:
        rows = await queries.get_expiring_subscriptions(session, hours=24)
        
        for sub, product, user in rows:
            hours_left = int((sub.expires_at - __import__('datetime').datetime.utcnow())
                            .total_seconds() / 3600)
            try:
                await bot.send_message(
                    chat_id=user.id,
                    text=(
                        f"⚠️ اشتراک «{product.name}» تو\n"
                        f"تا <b>{hours_left} ساعت دیگه</b> منقضی می‌شه!\n\n"
                        f"برای تمدید /start رو بزن."
                    ),
                    parse_mode="HTML"
                )
            except Exception as e:
                # کاربر ربات رو بلاک کرده یا پیدا نشد
                logger.warning(f"نتونستم به {user.id} پیام بدم: {e}")


async def deactivate_expired(bot: Bot):
    """اشتراک‌های منقضی شده رو غیرفعال کن و به کاربر خبر بده"""
    async with SessionFactory() as session:
        # اول لیست منقضی‌ها رو بگیر (قبل از غیرفعال کردن)
        from datetime import datetime
        from sqlalchemy import select
        from database.models import Subscription, Product, User
        
        result = await session.execute(
            select(Subscription, Product, User)
            .join(Product)
            .join(User)
            .where(
                Subscription.is_active == True,
                Subscription.expires_at <= datetime.utcnow()
            )
        )
        expired_rows = result.all()
        
        # غیرفعال کردن
        count = await queries.deactivate_expired_subscriptions(session)
        logger.info(f"{count} اشتراک منقضی شد")
        
        # اطلاع به کاربران
        for sub, product, user in expired_rows:
            try:
                await bot.send_message(
                    chat_id=user.id,
                    text=(
                        f"❌ اشتراک «{product.name}» تو منقضی شد.\n\n"
                        f"برای تمدید /start رو بزن."
                    )
                )
            except Exception as e:
                logger.warning(f"نتونستم به {user.id} پیام بدم: {e}")


async def run_scheduler(bot: Bot):
    """هر ۱ ساعت یه‌بار چک می‌کنه"""
    logger.info("Scheduler شروع به کار کرد")
    while True:
        try:
            await notify_expiring(bot)
            await deactivate_expired(bot)
        except Exception as e:
            logger.error(f"خطا در scheduler: {e}")
        
        await asyncio.sleep(60 * 60)  # هر ۱ ساعت
