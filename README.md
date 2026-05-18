# RelaxConnect

A production-ready Telegram community bot built with **Python 3.12**, **Aiogram 3**, and **MongoDB Motor**.

RelaxConnect is a **safe anonymous-style wellness community platform** with moderation — not a random private matching bot.

## Features

- **Spa & Massage Finder** — search by city/category, ratings, pricing, WhatsApp & Google Maps links
- **User Submitted Listings** — admin approval queue (no auto-approve)
- **Anonymous Community Feed** — text-only posts, reactions, replies, reports
- **Custom Profile Names** — public display names only (Telegram usernames/IDs never shown)
- **Safety & Privacy** — disclaimer, flood control, bad-word/NSFW filters, link/phone blocking, bans
- **Advanced Admin Panel** — listings, reports, broadcast, analytics, maintenance mode

## Project Structure

```
RelaxConnect/
├── bot/
│   ├── admin/           # Admin panel handlers
│   ├── database/        # MongoDB connection, models, repositories
│   ├── filters/         # Admin filter
│   ├── handlers/        # User-facing handlers
│   ├── keyboards/       # Inline keyboards
│   ├── middlewares/     # Ban, flood, media block, maintenance
│   ├── states/          # FSM states
│   ├── utils/           # Validators & formatters
│   ├── config.py
│   ├── loader.py
│   └── main.py
├── run.py
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

## Quick Start (Local)

### 1. BotFather Setup

1. Open [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow prompts
3. Copy the **HTTP API token**
4. Get your Telegram user ID (e.g. [@userinfobot](https://t.me/userinfobot))

### 2. MongoDB Atlas Setup

1. Create a free cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a database user with read/write access
3. Add your IP (or `0.0.0.0/0` for cloud deploy) under **Network Access**
4. Copy the connection string:
   `mongodb+srv://USER:PASSWORD@cluster.mongodb.net/?retryWrites=true&w=majority`

Collections are created automatically with indexes on first run:

- `users`, `listings`, `feed_posts`, `feed_reactions`, `bans`, `reports`, `settings`, `analytics`

### 3. Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
BOT_TOKEN=123456:ABC-DEF...
ADMIN_IDS=your_telegram_user_id
MONGODB_URI=mongodb+srv://...
MONGODB_DB=relaxconnect
```

### 4. Install & Run

```bash
cd RelaxConnect
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate       # Linux/macOS
pip install -r requirements.txt
python run.py
```

## Admin Commands

| Command   | Description        |
|-----------|--------------------|
| `/start`  | Main menu          |
| `/menu`   | Return to menu     |
| `/admin`  | Admin panel        |
| `/addword <word>` | Add blocked word |
| `/removeword <word>` | Remove blocked word |

## Deployment on Koyeb

### Option A: Dockerfile (recommended)

1. Push this repo to GitHub
2. Sign up at [Koyeb](https://www.koyeb.com)
3. **Create App** → **GitHub** → select repository
4. Build: **Dockerfile**
5. Instance type: Nano (or higher for broadcast-heavy usage)
6. Add environment variables from `.env.example`
7. Deploy — Koyeb runs `python run.py` via Dockerfile `CMD`

### Option B: Buildpack

1. Create app from GitHub
2. Build command: `pip install -r requirements.txt`
3. Run command: `python run.py`
4. Set all env vars in Koyeb dashboard

### Koyeb Environment Variables

| Variable | Required |
|----------|----------|
| `BOT_TOKEN` | Yes |
| `ADMIN_IDS` | Yes |
| `MONGODB_URI` | Yes |
| `MONGODB_DB` | No (default: relaxconnect) |
| `SUPPORT_USERNAME` | No |
| `FLOOD_LIMIT` | No |
| `FLOOD_WINDOW_SECONDS` | No |
| `SPAM_WARN_THRESHOLD` | No |

### MongoDB for Production

- Use a dedicated Atlas cluster (M10+ for high traffic)
- Restrict network access to Koyeb egress IPs when possible
- Enable backup & monitoring in Atlas

## Safety Rules (Enforced)

- Feed: **text only** — no media, stickers, links, phone numbers
- Disclaimer required before feed access
- Flood protection & warning system (3 warnings → ban path)
- Configurable blocked words via admin panel
- All spa listings require **manual admin approval**

## License

MIT — use and modify freely for your community.
