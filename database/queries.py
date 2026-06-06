from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timedelta
from .models import User, Product, Subscription, Payment
from datetime import datetime, timedelta


# ── Users ──────────────────────────────────────────────

async def get_or_create_user(session: AsyncSession, user_id: int, 
                              username: str, full_name: str) -> User:
    result = await session.get(User, user_id)
    if not result:
        result = User(id=user_id, username=username, full_name=full_name)
        session.add(result)
        await session.commit()
    return result


# ── Products ───────────────────────────────────────────

async def get_active_products(session: AsyncSession) -> list[Product]:
    result = await session.execute(
        select(Product).where(Product.is_active == True)
    )
    return result.scalars().all()

async def get_product(session: AsyncSession, product_id: int) -> Product | None:
    return await session.get(Product, product_id)


# ── Subscriptions ──────────────────────────────────────

async def get_active_subscription(session: AsyncSession, 
                                   user_id: int, product_id: int) -> Subscription | None:
    result = await session.execute(
        select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.product_id == product_id,
            Subscription.is_active == True,
            Subscription.expires_at > datetime.utcnow()
        )
    )
    return result.scalar_one_or_none()

async def create_subscription(session: AsyncSession,
                               user_id: int, product_id: int, days: int) -> Subscription:
    sub = Subscription(
        user_id=user_id,
        product_id=product_id,
        expires_at=datetime.utcnow() + timedelta(days=days)
    )
    session.add(sub)
    await session.commit()
    return sub


# ── Payments ───────────────────────────────────────────

async def create_payment(session: AsyncSession,
                          user_id: int, product_id: int, amount: float) -> Payment:
    payment = Payment(user_id=user_id, product_id=product_id, amount_ton=amount)
    session.add(payment)
    await session.commit()
    return payment

async def confirm_payment(session: AsyncSession, 
                           payment_id: int, tx_hash: str) -> None:
    await session.execute(
        update(Payment)
        .where(Payment.id == payment_id)
        .values(status="confirmed", tx_hash=tx_hash)
    )
    await session.commit()

# ── Scheduler ───────────────────────────────────────────

async def get_expiring_subscriptions(session: AsyncSession, hours: int = 24) -> list:
    """اشتراک‌هایی که تا X ساعت دیگه منقضی می‌شن"""
    from sqlalchemy import select
    from database.models import Subscription, Product, User
    
    deadline = datetime.utcnow() + timedelta(hours=hours)
    
    result = await session.execute(
        select(Subscription, Product, User)
        .join(Product)
        .join(User)
        .where(
            Subscription.is_active == True,
            Subscription.expires_at <= deadline,
            Subscription.expires_at > datetime.utcnow()
        )
    )
    return result.all()

async def deactivate_expired_subscriptions(session: AsyncSession) -> int:
    """اشتراک‌های منقضی شده رو غیرفعال می‌کنه، تعداد رو برمی‌گردونه"""
    from sqlalchemy import update
    
    result = await session.execute(
        update(Subscription)
        .where(
            Subscription.is_active == True,
            Subscription.expires_at <= datetime.utcnow()
        )
        .values(is_active=False)
    )
    await session.commit()
    return result.rowcount