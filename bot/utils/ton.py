import aiohttp
from config import TON_WALLET

TONCENTER_API = "https://toncenter.com/api/v2"

async def get_recent_transactions(limit: int = 20) -> list[dict]:
    """آخرین تراکنش‌های کیف پول ما رو می‌گیره"""
    url = f"{TONCENTER_API}/getTransactions"
    params = {
        "address": TON_WALLET,
        "limit": limit
    }
    async with aiohttp.ClientSession() as client:
        async with client.get(url, params=params) as resp:
            data = await resp.json()
            if data.get("ok"):
                return data["result"]
            return []

async def find_payment(amount_ton: float, after_timestamp: int) -> str | None:
    """
    دنبال تراکنشی می‌گرده که:
    - مبلغش با amount_ton یکیه
    - بعد از زمان ساخت پرداخت اومده
    پیدا شد → tx_hash برمی‌گردونه
    """
    transactions = await get_recent_transactions()
    
    # TON مبلغ رو به nanoton ذخیره می‌کنه (۱ TON = 1,000,000,000 nanoton)
    expected_nano = int(amount_ton * 1_000_000_000)
    
    for tx in transactions:
        tx_time = tx.get("utime", 0)
        if tx_time < after_timestamp:
            continue  # تراکنش قدیمیه
            
        in_msg = tx.get("in_msg", {})
        value = int(in_msg.get("value", 0))
        
        # تولرانس ۱۰۰۰ nanoton برای کارمزد شبکه
        if abs(value - expected_nano) < 1000:
            return tx.get("transaction_id", {}).get("hash")
    
    return None

def generate_unique_amount(base_price: float, payment_id: int) -> float:
    """
    قیمت یکتا می‌سازه
    مثال: base=1.5, id=7  →  1.507
    """
    unique_decimal = payment_id % 1000  # سه رقم آخر payment_id
    return round(base_price + unique_decimal * 0.001, 3)
