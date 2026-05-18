from aiogram import Router

from bot.handlers.feed import router as feed_router
from bot.handlers.listing_submit import router as listing_router
from bot.handlers.menu import router as menu_router
from bot.handlers.profile import router as profile_router
from bot.handlers.settings import router as settings_router
from bot.handlers.spa_finder import router as spa_router
from bot.handlers.start import router as start_router
from bot.handlers.support import router as support_router


def setup_routers() -> Router:
    root = Router()
    root.include_router(start_router)
    root.include_router(menu_router)
    root.include_router(spa_router)
    root.include_router(listing_router)
    root.include_router(feed_router)
    root.include_router(profile_router)
    root.include_router(settings_router)
    root.include_router(support_router)
    return root
