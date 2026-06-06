from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from database import queries
from database.models import Payment
from bot.keyboards.inline import confirm_payment_kb, main_menu_kb
from bot.utils.ton import find_payment, generate_unique_amount
from config import TON_WALLET

router = Router()


@router.callback_query(F.data.startswith("buy_"))
async def buy_product(call: CallbackQuery, session: AsyncSession):
    product_id = int(call.data.split("_")[1])
    product = await queries.get_product(session, product_id)

    if not product:
        await call.answer("محصول پیدا نشد!", show_alert=True)
        return

    # چک کن اشتراک فعال نداشته باشه
    existing = await queries.get_active_subscription(
        session, call.from_user.id, product_id
    )
    if existing:
        await call.answer(
            f"اشتراک فعال داری! تا {existing.expires_at.strftime('%Y-%m-%d')} معتبره.",
            show_alert=True
        )
        return

    # ساخت پرداخت pending
    payment = await queries.create_payment(
        session,
        user_id=call.from_user.id,
        product_id=product_id,
        amount_ton=product.price_ton
    )

    # مبلغ یکتا برای شناسایی این پرداخت
    unique_amount = generate_unique_amount(product.price_ton, payment.id)

    # ذخیره مبلغ یکتا توی payment
    payment.amount_ton = unique_amount
    await session.commit()

    text = (
        f"🛒 <b>{product.name}</b>\n\n"
        f"📅 مدت: {product.duration_days} روز\n"
        f"💎 مبلغ: <code>{unique_amount}</code> TON\n\n"
        f"👛 آدرس کیف پول:\n<code>{TON_WALLET}</code>\n\n"
        f"⚠️ <b>دقیقاً همین مبلغ رو بفرست</b> تا پرداختت شناسایی بشه.\n"
        f"بعد از ارسال، دکمه زیر رو بزن."
    )
    await call.message.edit_text(
        text,
        reply_markup=confirm_payment_kb(product_id, payment.id),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("check_payment_"))
async def check_payment(call: CallbackQuery, session: AsyncSession):
    _, _, product_id, payment_id = call.data.split("_")
    product_id, payment_id = int(product_id), int(payment_id)

    # گرفتن پرداخت از دیتابیس
    payment = await session.get(Payment, payment_id)
    if not payment or payment.user_id != call.from_user.id:
        await call.answer("پرداخت پیدا نشد!", show_alert=True)
        return

    if payment.status == "confirmed":
        await call.answer("این پرداخت قبلاً تایید شده!", show_alert=True)
        return

    await call.answer("⏳ در حال بررسی...")

    # زمان ساخت پرداخت به timestamp
    created_timestamp = int(payment.created_at.timestamp())

    # جستجو در تراکنش‌های بلاکچین
    tx_hash = await find_payment(payment.amount_ton, created_timestamp)

    if not tx_hash:
        await call.message.answer(
            "❌ تراکنش پیدا نشد.\n\n"
            "• مطمئن شو دقیقاً همون مبلغ رو فرستادی\n"
            "• شبکه TON کمی طول می‌کشه، چند دقیقه صبر کن و دوباره امتحان کن"
        )
        return

    # تایید پرداخت
    await queries.confirm_payment(session, payment_id, tx_hash)

    # فعال‌سازی اشتراک
    product = await queries.get_product(session, product_id)
    subscription = await queries.create_subscription(
        session,
        user_id=call.from_user.id,
        product_id=product_id,
        days=product.duration_days
    )

    # تحویل محصول
    await deliver_product(call, product)


async def deliver_product(call: CallbackQuery, product):
    """بسته به نوع محصول، اطلاعات تحویل داده می‌شه"""
    
    if product.product_type == "vpn":
        text = (
            f"✅ اشتراک فعال شد!\n\n"
            f"🔐 کانفیگ VPN:\n<code>{product.delivery_data}</code>"
        )
    elif product.product_type == "channel":
        text = (
            f"✅ اشتراک فعال شد!\n\n"
            f"📢 لینک ورود به کانال:\n{product.delivery_data}"
        )
    else:
        text = (
            f"✅ اشتراک فعال شد!\n\n"
            f"📥 لینک دانلود:\n{product.delivery_data}"
        )

    await call.message.answer(text, parse_mode="HTML", reply_markup=main_menu_kb())
