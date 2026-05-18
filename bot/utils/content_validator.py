import re
from typing import List, Optional, Tuple

# Phone patterns (international + local)
PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[\s\-]?)?(?:\(?\d{2,4}\)?[\s\-]?)?\d{3,4}[\s\-]?\d{3,4}(?:[\s\-]?\d{2,4})?"
)

# URL / link patterns
LINK_PATTERN = re.compile(
    r"(https?://|www\.|t\.me/|telegram\.me/|bit\.ly/|goo\.gl/|maps\.google|google\.com/maps)",
    re.IGNORECASE,
)

# Email
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# Social handles
SOCIAL_PATTERN = re.compile(
    r"(@[a-zA-Z0-9_]{3,}|instagram|facebook|snapchat|twitter|x\.com)",
    re.IGNORECASE,
)

NSFW_KEYWORDS = [
    "porn", "xxx", "nude", "naked", "sex", "escort", "hookup", "onlyfans",
    "hentai", "fetish", "bdsm", "orgy", "prostitut",
]

DEFAULT_BAD_WORDS = [
    "fuck", "shit", "bitch", "asshole", "bastard", "damn", "cunt", "dick",
    "kill yourself", "kys",
]


class ContentValidationResult:
    def __init__(self, valid: bool, reason: Optional[str] = None):
        self.valid = valid
        self.reason = reason


async def validate_feed_text(
    text: str,
    extra_blocked: Optional[List[str]] = None,
) -> ContentValidationResult:
    if not text or not text.strip():
        return ContentValidationResult(False, "Empty message is not allowed.")

    if len(text) > 500:
        return ContentValidationResult(False, "Message too long (max 500 characters).")

    if LINK_PATTERN.search(text):
        return ContentValidationResult(False, "Links are not allowed in the feed.")

    if PHONE_PATTERN.search(text):
        return ContentValidationResult(False, "Phone numbers are not allowed.")

    if EMAIL_PATTERN.search(text):
        return ContentValidationResult(False, "Email addresses are not allowed.")

    if SOCIAL_PATTERN.search(text):
        return ContentValidationResult(False, "Social media references are not allowed.")

    lowered = text.lower()
    blocked = set(DEFAULT_BAD_WORDS + NSFW_KEYWORDS)
    if extra_blocked:
        blocked.update(w.lower() for w in extra_blocked)

    for word in blocked:
        if word and word in lowered:
            return ContentValidationResult(False, "Inappropriate language detected.")

    return ContentValidationResult(True)


def validate_display_name(name: str) -> Tuple[bool, str]:
    if not name or len(name) < 3:
        return False, "Name must be at least 3 characters."
    if len(name) > 20:
        return False, "Name must be at most 20 characters."
    if not re.match(r"^[a-zA-Z0-9_]+$", name):
        return False, "Only letters, numbers, and underscore allowed."
    if PHONE_PATTERN.search(name) or LINK_PATTERN.search(name):
        return False, "Name cannot contain links or phone numbers."
    lowered = name.lower()
    for word in NSFW_KEYWORDS + DEFAULT_BAD_WORDS:
        if word in lowered:
            return False, "Name contains inappropriate content."
    return True, ""


def validate_whatsapp(number: str) -> bool:
    cleaned = re.sub(r"[\s\-+()]", "", number)
    return bool(re.match(r"^\d{10,15}$", cleaned))


def validate_maps_link(link: str) -> bool:
    return bool(
        link.startswith("http")
        and ("google.com/maps" in link.lower() or "goo.gl/maps" in link.lower() or "maps.app.goo.gl" in link.lower())
    )
