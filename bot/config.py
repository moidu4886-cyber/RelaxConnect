import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv

load_dotenv()


def _parse_admin_ids() -> List[int]:
    raw = os.getenv("ADMIN_IDS", "")
    return [int(x.strip()) for x in raw.split(",") if x.strip().isdigit()]


@dataclass
class Config:
    bot_token: str
    admin_ids: List[int]
    mongodb_uri: str
    mongodb_db: str
    support_username: str
    flood_limit: int
    flood_window_seconds: int
    spam_warn_threshold: int
    feed_page_size: int
    listings_page_size: int

    def validate(self) -> None:
        if not self.bot_token:
            raise ValueError("BOT_TOKEN is required")
        if not self.mongodb_uri:
            raise ValueError("MONGODB_URI is required")
        if not self.admin_ids:
            raise ValueError("At least one ADMIN_IDS entry is required")


config = Config(
    bot_token=os.getenv("BOT_TOKEN", ""),
    admin_ids=_parse_admin_ids(),
    mongodb_uri=os.getenv("MONGODB_URI", ""),
    mongodb_db=os.getenv("MONGODB_DB", "relaxconnect"),
    support_username=os.getenv("SUPPORT_USERNAME", "relaxconnect_support"),
    flood_limit=int(os.getenv("FLOOD_LIMIT", "5")),
    flood_window_seconds=int(os.getenv("FLOOD_WINDOW_SECONDS", "10")),
    spam_warn_threshold=int(os.getenv("SPAM_WARN_THRESHOLD", "3")),
    feed_page_size=int(os.getenv("FEED_PAGE_SIZE", "5")),
    listings_page_size=int(os.getenv("LISTINGS_PAGE_SIZE", "5")),
)
