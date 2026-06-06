from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from database import queries
from bot.keyboards.inline import main_menu_kb, products_kb

router = Router()


@router.message(CommandStart())
async def start(message: Message, session: AsyncSession):
    # ثبت یا بازیابی کاربر
    await queries.get_or_create_user(
        session,
        user_id=message.from_user.id,
        username=message.from_user.username or "",
        full_name=message.from_user.full_name
    )
    await message.answer(
        f"👋 سلام {message.from_user.first_name}!\n\n"
        "به ربات اشتراک خوش اومدی.\n"
        "از منوی زیر انتخاب کن:",
        reply_markup=main_menu_kb()
    )


@router.callback_query(F.data == "products")
async def show_products(call: CallbackQuery, session: AsyncSession):
    products = await queries.get_active_products(session)
    if not products:
        await call.answer("محصولی موجود نیست!", show_alert=True)
        return
    await call.message.edit_text(
        "📦 محصولات موجود:",
        reply_markup=products_kb(products)
    )


@router.callback_query(F.data == "my_subscriptions")
async def my_subscriptions(call: CallbackQuery, session: AsyncSession):
    from sqlalchemy import select
    from database.models import Subscription, Product

    result = await session.execute(
        select(Subscription, Product)
        .join(Product)
        .where(
            Subscription.user_id == call.from_user.id,
            Subscription.is_active == True,
            Subscription.expires_at > datetime.utcnow()
        )
    )
    rows = result.all()

    if not rows:
        await call.message.edit_text(
            "❌ اشتراک فعالی نداری.",
            reply_markup=main_menu_kb()
        )
        return

    text = "✅ اشتراک‌های فعال تو:\n\n"
    for sub, product in rows:
        days_left = (sub.expires_at - datetime.utcnow()).days
        text += f"• {product.name} — {days_left} روز مانده\n"

    await call.message.edit_text(text, reply_markup=main_menu_kb())


@router.callback_query(F.data == "back_main")
async def back_main(call: CallbackQuery):
    await call.message.edit_text(
        "از منوی زیر انتخاب کن:",
        reply_markup=main_menu_kb()
    )
