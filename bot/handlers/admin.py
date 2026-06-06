from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from config import ADMIN_IDS
from database import queries
from database.models import Product
from bot.keyboards.inline import admin_kb

router = Router()

# فقط ادمین‌ها
router.message.filter(F.from_user.id.in_(ADMIN_IDS))
router.callback_query.filter(F.from_user.id.in_(ADMIN_IDS))


class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    duration = State()
    product_type = State()
    delivery_data = State()


@router.message(Command("admin"))
async def admin_panel(message: Message):
    await message.answer("⚙️ پنل ادمین:", reply_markup=admin_kb())


@router.callback_query(F.data == "admin_add_product")
async def add_product_start(call: CallbackQuery, state: FSMContext):
    await call.message.answer("📝 اسم محصول رو بنویس:")
    await state.set_state(AddProduct.name)


@router.message(AddProduct.name)
async def add_product_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📄 توضیحات محصول:")
    await state.set_state(AddProduct.description)


@router.message(AddProduct.description)
async def add_product_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("💎 قیمت به TON (مثال: 1.5):")
    await state.set_state(AddProduct.price)


@router.message(AddProduct.price)
async def add_product_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("❌ عدد وارد کن!")
        return
    await state.update_data(price=price)
    await message.answer("📅 مدت اشتراک (روز):")
    await state.set_state(AddProduct.duration)


@router.message(AddProduct.duration)
async def add_product_duration(message: Message, state: FSMContext):
    try:
        days = int(message.text)
    except ValueError:
        await message.answer("❌ عدد صحیح وارد کن!")
        return
    await state.update_data(duration=days)
    await message.answer("🏷 نوع محصول:\nvpn | channel | software")
    await state.set_state(AddProduct.product_type)


@router.message(AddProduct.product_type)
async def add_product_type(message: Message, state: FSMContext):
    if message.text not in ["vpn", "channel", "software"]:
        await message.answer("❌ فقط vpn یا channel یا software")
        return
    await state.update_data(product_type=message.text)
    await message.answer("📦 اطلاعات تحویل:\n(کانفیگ VPN / لینک کانال / لینک دانلود)")
    await state.set_state(AddProduct.delivery_data)


@router.message(AddProduct.delivery_data)
async def add_product_finish(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    product = Product(
        name=data["name"],
        description=data["description"],
        price_ton=data["price"],
        duration_days=data["duration"],
        product_type=data["product_type"],
        delivery_data=message.text
    )
    session.add(product)
    await session.commit()
    await state.clear()
    await message.answer(f"✅ محصول «{product.name}» اضافه شد!", reply_markup=admin_kb())
