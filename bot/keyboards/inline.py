from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.models import Product

def main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🛒 محصولات", callback_data="products")
    builder.button(text="👤 اشتراک‌های من", callback_data="my_subscriptions")
    builder.adjust(1)
    return builder.as_markup()

def products_kb(products: list[Product]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for p in products:
        builder.button(
            text=f"{p.name} — {p.price_ton} TON",
            callback_data=f"buy_{p.id}"
        )
    builder.button(text="🔙 بازگشت", callback_data="back_main")
    builder.adjust(1)
    return builder.as_markup()

def confirm_payment_kb(product_id: int, payment_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ پرداخت کردم",
        callback_data=f"check_payment_{product_id}_{payment_id}"
    )
    builder.button(text="❌ انصراف", callback_data="products")
    builder.adjust(1)
    return builder.as_markup()

def admin_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ محصول جدید", callback_data="admin_add_product")
    builder.button(text="📦 لیست محصولات", callback_data="admin_list_products")
    builder.button(text="📊 آمار", callback_data="admin_stats")
    builder.adjust(1)
    return builder.as_markup()
