from typing import Any, Dict, List, Optional

from bot.database.models import ListingCategory, oid_str


def category_label(category: str) -> str:
    if category == ListingCategory.SPA.value:
        return "Spa"
    if category == ListingCategory.MASSAGE.value:
        return "Massage Center"
    return category


def format_listing_card(listing: Dict[str, Any], index: int = 0) -> str:
    stars = "⭐" * min(5, int(listing.get("rating", 0)))
    return (
        f"<b>{index}. {listing['business_name']}</b>\n"
        f"📍 {listing.get('area', '')}, {listing.get('city', '').title()}\n"
        f"🏷 {category_label(listing.get('category', ''))}\n"
        f"💰 {listing.get('price_range', 'N/A')}\n"
        f"{stars} ({listing.get('rating', 0):.1f})\n"
        f"🕐 {listing.get('working_hours', 'N/A')}\n"
        f"<i>{listing.get('description', '')[:120]}</i>"
    )


def format_listing_detail(listing: Dict[str, Any]) -> str:
    lid = oid_str(listing["_id"])
    return (
        f"<b>✨ {listing['business_name']}</b>\n\n"
        f"📍 <b>Location:</b> {listing.get('area', '')}, {listing.get('city', '').title()}\n"
        f"🏷 <b>Category:</b> {category_label(listing.get('category', ''))}\n"
        f"💰 <b>Price:</b> {listing.get('price_range', 'N/A')}\n"
        f"⭐ <b>Rating:</b> {listing.get('rating', 0):.1f}\n"
        f"🕐 <b>Hours:</b> {listing.get('working_hours', 'N/A')}\n\n"
        f"📝 {listing.get('description', '')}\n\n"
        f"<code>ID: {lid}</code>"
    )


def format_feed_post(
    post: Dict[str, Any],
    display_name: str,
    page_index: int = 0,
) -> str:
    reactions = post.get("reaction_counts", {})
    reply_note = ""
    if post.get("reply_to"):
        reply_note = "\n↩️ <i>Reply to another post</i>"
    return (
        f"<b>🎭 {display_name}</b>{reply_note}\n"
        f"━━━━━━━━━━━━━━\n"
        f"{post.get('text', '')}\n"
        f"━━━━━━━━━━━━━━\n"
        f"❤️ {reactions.get('love', 0)}  👍 {reactions.get('like', 0)}  🔥 {reactions.get('fire', 0)}"
    )


def format_profile(user: Dict[str, Any]) -> str:
    name = user.get("display_name") or "Not set"
    warnings = user.get("warnings", 0)
    posts = user.get("feed_posts_count", 0)
    agreed = "✅" if user.get("agreed_terms") else "❌"
    return (
        f"<b>🎭 My Profile</b>\n\n"
        f"<b>Display Name:</b> {name}\n"
        f"<b>Feed Posts:</b> {posts}\n"
        f"<b>Community Agreement:</b> {agreed}\n"
        f"<b>Warnings:</b> {warnings}/3\n\n"
        f"<i>Your real Telegram identity is never shown publicly.</i>"
    )


def format_analytics(data: Dict[str, Any]) -> str:
    today = data.get("today", {})
    return (
        f"<b>📊 Analytics Dashboard</b>\n\n"
        f"👥 Users: <b>{data.get('users', 0)}</b>\n"
        f"📝 Feed Posts: <b>{data.get('posts', 0)}</b>\n"
        f"🏪 Approved Listings: <b>{data.get('listings', 0)}</b>\n"
        f"⏳ Pending Listings: <b>{data.get('pending_listings', 0)}</b>\n"
        f"🚨 Open Reports: <b>{data.get('open_reports', 0)}</b>\n\n"
        f"<b>Today</b>\n"
        f"• Posts: {today.get('posts_created', 0)}\n"
        f"• Reports: {today.get('reports_created', 0)}\n"
        f"• Actions: {today.get('total_actions', 0)}"
    )


def format_disclaimer() -> str:
    return (
        "<b>⚠️ Community Safety Disclaimer</b>\n\n"
        "RelaxConnect is a <b>safe anonymous community</b>. By continuing you agree:\n\n"
        "• No personal information\n"
        "• No phone numbers\n"
        "• No social media IDs\n"
        "• No links in feed posts\n"
        "• Text-only content\n"
        "• No illegal activity\n\n"
        "Violations may result in warnings or <b>permanent ban</b>.\n\n"
        "Tap <b>I Agree</b> to enter the Anonymous Feed."
    )


def format_main_menu() -> str:
    return (
        "<b>✨ RelaxConnect</b>\n"
        "<i>Your safe wellness community</i>\n\n"
        "1️⃣ Find Spa & Massage\n"
        "2️⃣ Add Your Spa Listing\n"
        "3️⃣ Anonymous Community Feed\n"
        "4️⃣ My Profile\n"
        "5️⃣ Settings\n"
        "6️⃣ Support"
    )
