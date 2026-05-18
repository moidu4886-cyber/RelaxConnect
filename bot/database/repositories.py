from datetime import datetime, date
from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from bot.database.connection import get_db
from bot.database.models import (
    ListingStatus,
    ReportStatus,
    feed_post_doc,
    listing_doc,
    oid_str,
    report_doc,
    user_doc,
)


class UserRepository:
  @staticmethod
  async def get_or_create(telegram_id: int) -> Dict[str, Any]:
    db = get_db()
    user = await db.users.find_one({"telegram_id": telegram_id})
    if user:
      return user
    doc = user_doc(telegram_id)
    await db.users.insert_one(doc)
    return doc

  @staticmethod
  async def get(telegram_id: int) -> Optional[Dict[str, Any]]:
    return await get_db().users.find_one({"telegram_id": telegram_id})

  @staticmethod
  async def update(telegram_id: int, **fields: Any) -> None:
    fields["updated_at"] = datetime.utcnow()
    await get_db().users.update_one({"telegram_id": telegram_id}, {"$set": fields})

  @staticmethod
  async def set_display_name(telegram_id: int, name: str) -> bool:
    existing = await get_db().users.find_one(
      {"display_name": name, "telegram_id": {"$ne": telegram_id}}
    )
    if existing:
      return False
    await UserRepository.update(telegram_id, display_name=name)
    return True

  @staticmethod
  async def agree_terms(telegram_id: int) -> None:
    await UserRepository.update(telegram_id, agreed_terms=True)

  @staticmethod
  async def add_warning(telegram_id: int) -> int:
    user = await UserRepository.get(telegram_id)
    warnings = (user or {}).get("warnings", 0) + 1
    await UserRepository.update(telegram_id, warnings=warnings)
    return warnings

  @staticmethod
  async def count() -> int:
    return await get_db().users.count_documents({})

  @staticmethod
  async def stats() -> Dict[str, int]:
    db = get_db()
    total = await db.users.count_documents({})
    agreed = await db.users.count_documents({"agreed_terms": True})
    banned = await db.users.count_documents({"is_banned": True})
    return {"total": total, "agreed_terms": agreed, "banned": banned}


class ListingRepository:
  @staticmethod
  async def create(**kwargs: Any) -> str:
    doc = listing_doc(**kwargs)
    result = await get_db().listings.insert_one(doc)
    return oid_str(result.inserted_id)

  @staticmethod
  async def get(listing_id: str) -> Optional[Dict[str, Any]]:
    return await get_db().listings.find_one({"_id": ObjectId(listing_id)})

  @staticmethod
  async def search(
    city: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 5,
  ) -> List[Dict[str, Any]]:
    query: Dict[str, Any] = {"status": ListingStatus.APPROVED.value}
    if city:
      query["city"] = city.lower().strip()
    if category:
      query["category"] = category
    cursor = (
      get_db()
      .listings.find(query)
      .sort("rating", -1)
      .skip(skip)
      .limit(limit)
    )
    return await cursor.to_list(length=limit)

  @staticmethod
  async def count_search(city: Optional[str] = None, category: Optional[str] = None) -> int:
    query: Dict[str, Any] = {"status": ListingStatus.APPROVED.value}
    if city:
      query["city"] = city.lower().strip()
    if category:
      query["category"] = category
    return await get_db().listings.count_documents(query)

  @staticmethod
  async def pending(skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
    cursor = (
      get_db()
      .listings.find({"status": ListingStatus.PENDING.value})
      .sort("created_at", 1)
      .skip(skip)
      .limit(limit)
    )
    return await cursor.to_list(length=limit)

  @staticmethod
  async def pending_count() -> int:
    return await get_db().listings.count_documents({"status": ListingStatus.PENDING.value})

  @staticmethod
  async def approve(listing_id: str, admin_id: int) -> None:
    await get_db().listings.update_one(
      {"_id": ObjectId(listing_id)},
      {
        "$set": {
          "status": ListingStatus.APPROVED.value,
          "reviewed_by": admin_id,
          "updated_at": datetime.utcnow(),
        }
      },
    )

  @staticmethod
  async def reject(listing_id: str, admin_id: int, note: str = "") -> None:
    await get_db().listings.update_one(
      {"_id": ObjectId(listing_id)},
      {
        "$set": {
          "status": ListingStatus.REJECTED.value,
          "reviewed_by": admin_id,
          "review_note": note,
          "updated_at": datetime.utcnow(),
        }
      },
    )


class FeedRepository:
  @staticmethod
  async def create_post(author_id: int, text: str, reply_to: Optional[str] = None) -> str:
    doc = feed_post_doc(author_id, text, reply_to)
    result = await get_db().feed_posts.insert_one(doc)
    await get_db().users.update_one(
      {"telegram_id": author_id},
      {"$inc": {"feed_posts_count": 1}, "$set": {"updated_at": datetime.utcnow()}},
    )
    await AnalyticsRepository.increment("posts_created")
    return oid_str(result.inserted_id)

  @staticmethod
  async def get_post(post_id: str) -> Optional[Dict[str, Any]]:
    return await get_db().feed_posts.find_one(
      {"_id": ObjectId(post_id), "is_deleted": False}
    )

  @staticmethod
  async def feed(skip: int = 0, limit: int = 5) -> List[Dict[str, Any]]:
    cursor = (
      get_db()
      .feed_posts.find({"is_deleted": False})
      .sort("created_at", -1)
      .skip(skip)
      .limit(limit)
    )
    return await cursor.to_list(length=limit)

  @staticmethod
  async def feed_count() -> int:
    return await get_db().feed_posts.count_documents({"is_deleted": False})

  @staticmethod
  async def delete_post(post_id: str) -> None:
    await get_db().feed_posts.update_one(
      {"_id": ObjectId(post_id)},
      {"$set": {"is_deleted": True}},
    )

  @staticmethod
  async def increment_report(post_id: str) -> None:
    await get_db().feed_posts.update_one(
      {"_id": ObjectId(post_id)},
      {"$inc": {"report_count": 1}},
    )

  @staticmethod
  async def add_reaction(post_id: str, user_id: int, reaction: str) -> bool:
    db = get_db()
    existing = await db.feed_reactions.find_one(
      {"post_id": post_id, "user_id": user_id}
    )
    if existing:
      if existing.get("reaction") == reaction:
        return False
      old = existing.get("reaction")
      await db.feed_reactions.update_one(
        {"_id": existing["_id"]},
        {"$set": {"reaction": reaction}},
      )
      await db.feed_posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$inc": {f"reaction_counts.{old}": -1, f"reaction_counts.{reaction}": 1}},
      )
      return True
    await db.feed_reactions.insert_one(
      {"post_id": post_id, "user_id": user_id, "reaction": reaction}
    )
    await db.feed_posts.update_one(
      {"_id": ObjectId(post_id)},
      {"$inc": {f"reaction_counts.{reaction}": 1}},
    )
    return True


class BanRepository:
  @staticmethod
  async def ban(telegram_id: int, reason: str, admin_id: int) -> None:
    db = get_db()
    await db.bans.update_one(
      {"telegram_id": telegram_id},
      {
        "$set": {
          "telegram_id": telegram_id,
          "reason": reason,
          "banned_by": admin_id,
          "created_at": datetime.utcnow(),
        }
      },
      upsert=True,
    )
    await db.users.update_one(
      {"telegram_id": telegram_id},
      {"$set": {"is_banned": True, "updated_at": datetime.utcnow()}},
    )

  @staticmethod
  async def unban(telegram_id: int) -> None:
    db = get_db()
    await db.bans.delete_one({"telegram_id": telegram_id})
    await db.users.update_one(
      {"telegram_id": telegram_id},
      {"$set": {"is_banned": False, "warnings": 0, "updated_at": datetime.utcnow()}},
    )

  @staticmethod
  async def is_banned(telegram_id: int) -> bool:
    ban = await get_db().bans.find_one({"telegram_id": telegram_id})
    return ban is not None


class ReportRepository:
  @staticmethod
  async def create(reporter_id: int, target_type: str, target_id: str, reason: str) -> str:
    doc = report_doc(reporter_id, target_type, target_id, reason)
    result = await get_db().reports.insert_one(doc)
    await AnalyticsRepository.increment("reports_created")
    return oid_str(result.inserted_id)

  @staticmethod
  async def open_reports(skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
    cursor = (
      get_db()
      .reports.find({"status": ReportStatus.OPEN.value})
      .sort("created_at", -1)
      .skip(skip)
      .limit(limit)
    )
    return await cursor.to_list(length=limit)

  @staticmethod
  async def open_count() -> int:
    return await get_db().reports.count_documents({"status": ReportStatus.OPEN.value})

  @staticmethod
  async def resolve(report_id: str, admin_id: int, status: str = ReportStatus.RESOLVED.value) -> None:
    await get_db().reports.update_one(
      {"_id": ObjectId(report_id)},
      {
        "$set": {
          "status": status,
          "resolved_by": admin_id,
          "resolved_at": datetime.utcnow(),
        }
      },
    )


class SettingsRepository:
  @staticmethod
  async def get() -> Dict[str, Any]:
    settings = await get_db().settings.find_one({"_id": "global"})
    if not settings:
      default = {
        "_id": "global",
        "maintenance_mode": False,
        "blocked_words": [
          "porn", "xxx", "nude", "naked", "sex", "escort", "drugs", "cocaine",
        ],
        "broadcast_enabled": True,
      }
      await get_db().settings.insert_one(default)
      return default
    return settings

  @staticmethod
  async def set_maintenance(enabled: bool) -> None:
    await get_db().settings.update_one(
      {"_id": "global"},
      {"$set": {"maintenance_mode": enabled}},
      upsert=True,
    )

  @staticmethod
  async def get_blocked_words() -> List[str]:
    s = await SettingsRepository.get()
    return s.get("blocked_words", [])

  @staticmethod
  async def add_blocked_word(word: str) -> None:
    await get_db().settings.update_one(
      {"_id": "global"},
      {"$addToSet": {"blocked_words": word.lower().strip()}},
      upsert=True,
    )

  @staticmethod
  async def remove_blocked_word(word: str) -> None:
    await get_db().settings.update_one(
      {"_id": "global"},
      {"$pull": {"blocked_words": word.lower().strip()}},
    )

  @staticmethod
  async def is_maintenance() -> bool:
    s = await SettingsRepository.get()
    return bool(s.get("maintenance_mode", False))


class AnalyticsRepository:
  @staticmethod
  async def increment(field: str, amount: int = 1) -> None:
    today = date.today().isoformat()
    await get_db().analytics.update_one(
      {"date": today},
      {
        "$inc": {field: amount, "total_actions": amount},
        "$setOnInsert": {"date": today},
      },
      upsert=True,
    )

  @staticmethod
  async def dashboard() -> Dict[str, Any]:
    db = get_db()
    users = await db.users.count_documents({})
    posts = await db.feed_posts.count_documents({"is_deleted": False})
    listings = await db.listings.count_documents({"status": ListingStatus.APPROVED.value})
    pending = await db.listings.count_documents({"status": ListingStatus.PENDING.value})
    reports = await db.reports.count_documents({"status": ReportStatus.OPEN.value})
    today = date.today().isoformat()
    today_stats = await db.analytics.find_one({"date": today}) or {}
    return {
      "users": users,
      "posts": posts,
      "listings": listings,
      "pending_listings": pending,
      "open_reports": reports,
      "today": today_stats,
    }
