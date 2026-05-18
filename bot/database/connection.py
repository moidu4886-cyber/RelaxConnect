from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from bot.config import config

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect_db() -> AsyncIOMotorDatabase:
    global _client, _db
    if _db is not None:
        return _db
    _client = AsyncIOMotorClient(config.mongodb_uri)
    _db = _client[config.mongodb_db]
    await _ensure_indexes(_db)
    return _db


async def close_db() -> None:
    global _client, _db
    if _client is not None:
        _client.close()
    _client = None
    _db = None


def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("Database not connected. Call connect_db() first.")
    return _db


async def _ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    await db.users.create_index("telegram_id", unique=True)
    await db.users.create_index("display_name")
    await db.listings.create_index([("status", 1), ("city", 1)])
    await db.listings.create_index("category")
    await db.feed_posts.create_index([("created_at", -1)])
    await db.feed_posts.create_index("author_id")
    await db.feed_reactions.create_index(
        [("post_id", 1), ("user_id", 1)], unique=True
    )
    await db.bans.create_index("telegram_id", unique=True)
    await db.reports.create_index([("status", 1), ("created_at", -1)])
    await db.analytics.create_index("date", unique=True)
