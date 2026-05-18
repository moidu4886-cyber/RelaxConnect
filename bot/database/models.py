from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from bson import ObjectId


class ListingStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ListingCategory(str, Enum):
    SPA = "spa"
    MASSAGE = "massage_center"


class ReportStatus(str, Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


def oid_str(value: Any) -> str:
    if isinstance(value, ObjectId):
        return str(value)
    return str(value)


def user_doc(
    telegram_id: int,
    display_name: Optional[str] = None,
    agreed_terms: bool = False,
    warnings: int = 0,
) -> Dict[str, Any]:
    return {
        "telegram_id": telegram_id,
        "display_name": display_name,
        "agreed_terms": agreed_terms,
        "warnings": warnings,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "feed_posts_count": 0,
        "is_banned": False,
    }


def listing_doc(
    submitter_id: int,
    business_name: str,
    city: str,
    area: str,
    category: str,
    price_range: str,
    whatsapp: str,
    maps_link: str,
    description: str,
    working_hours: str,
    rating: float = 0.0,
) -> Dict[str, Any]:
    return {
        "submitter_id": submitter_id,
        "business_name": business_name,
        "city": city.lower().strip(),
        "area": area,
        "category": category,
        "price_range": price_range,
        "whatsapp": whatsapp,
        "maps_link": maps_link,
        "description": description,
        "working_hours": working_hours,
        "rating": rating,
        "status": ListingStatus.PENDING.value,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "reviewed_by": None,
        "review_note": None,
    }


def feed_post_doc(author_id: int, text: str, reply_to: Optional[str] = None) -> Dict[str, Any]:
    return {
        "author_id": author_id,
        "text": text,
        "reply_to": reply_to,
        "reaction_counts": {"like": 0, "love": 0, "fire": 0},
        "report_count": 0,
        "is_deleted": False,
        "created_at": datetime.utcnow(),
    }


def report_doc(
    reporter_id: int,
    target_type: str,
    target_id: str,
    reason: str,
) -> Dict[str, Any]:
    return {
        "reporter_id": reporter_id,
        "target_type": target_type,
        "target_id": target_id,
        "reason": reason,
        "status": ReportStatus.OPEN.value,
        "created_at": datetime.utcnow(),
        "resolved_at": None,
        "resolved_by": None,
    }
