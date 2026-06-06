# 🤖 Crypto Subscription Bot

A production-ready Telegram bot for selling digital subscriptions (VPN, VIP channels, software) with **TON blockchain payments**.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![aiogram](https://img.shields.io/badge/aiogram-3.7-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?logo=postgresql)
![TON](https://img.shields.io/badge/TON-Blockchain-0098EA?logo=telegram)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

- 💎 **TON Payments** — On-chain payment verification via TON Center API
- 📦 **Multi-product Support** — VPN configs, VIP channels, software licenses
- 👤 **User Management** — Subscription tracking, expiry notifications
- ⚙️ **Admin Panel** — Add/manage products directly from Telegram
- 🔔 **Auto Notifications** — Alerts 24h before expiry, auto-deactivation on expiry
- 🛡 **Fraud Prevention** — Unique payment amounts per transaction for on-chain verification

---

## 🏗 Architecture

```
crypto-subscription-bot/
├── bot/
│   ├── handlers/
│   │   ├── user.py        # Start, products, subscriptions
│   │   ├── admin.py       # Admin panel, add products (FSM)
│   │   └── payment.py     # TON payment flow, delivery
│   ├── keyboards/
│   │   └── inline.py      # All inline keyboards
│   ├── middlewares/
│   │   └── db.py          # Auto DB session injection
│   ├── utils/
│   │   └── ton.py         # TON Center API, tx verification
│   └── scheduler.py       # Expiry notifications (runs every 1h)
├── database/
│   ├── models.py          # SQLAlchemy models
│   ├── queries.py         # Async DB queries
│   └── engine.py          # DB connection & session factory
├── config.py
├── main.py
└── .env
```

---

## 💳 Payment Flow

```
User selects product
       ↓
Bot creates pending payment with unique amount
(e.g. base 1.5 TON → unique 1.507 TON)
       ↓
User sends exact amount to bot's TON wallet
       ↓
User clicks "I paid" button
       ↓
Bot queries TON Center API for recent transactions
       ↓
Matching tx found → subscription activated → product delivered
```

> **Why unique amounts?** Each payment gets a distinct decimal (1.501, 1.502 ...) so the bot can identify which user sent which transaction on-chain — no custodial solution needed.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- A Telegram Bot Token ([@BotFather](https://t.me/BotFather))
- A TON wallet address

### Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/crypto-subscription-bot.git
cd crypto-subscription-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
```

Edit `.env`:

```env
BOT_TOKEN=your_telegram_bot_token
ADMIN_IDS=123456789,987654321
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/subscription_bot
TON_WALLET=your_ton_wallet_address
```

### Database Setup

```bash
# Create the database
createdb subscription_bot

# Tables are created automatically on first run
python main.py
```

---

## ⚙️ Usage

### Admin Commands

| Command | Description |
|---------|-------------|
| `/admin` | Open admin panel |

From the admin panel you can:
- ➕ Add new products (name, price, duration, delivery data)
- 📦 List all products
- 📊 View stats

### Product Types

| Type | Delivery |
|------|----------|
| `vpn` | Sends VPN config string to user |
| `channel` | Sends private channel invite link |
| `software` | Sends download link |

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|------------|
| Bot Framework | [aiogram 3](https://docs.aiogram.dev/) |
| Database | PostgreSQL + SQLAlchemy (async) |
| Blockchain | [TON Center API](https://toncenter.com/api/v2/) |
| HTTP Client | aiohttp |
| Config | python-dotenv |

---

## 📋 Requirements

```
aiogram==3.7.0
asyncpg
SQLAlchemy[asyncio]
alembic
python-dotenv
aiohttp
```

---

## 🗺 Roadmap

- [ ] TON Connect integration (in-app wallet)
- [ ] Redis storage for FSM persistence
- [ ] Multi-language support
- [ ] Referral system
- [ ] Admin statistics dashboard
- [ ] Webhook mode for production

---

## 📄 License

MIT — feel free to use and modify.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.
