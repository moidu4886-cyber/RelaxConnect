import asyncio
import logging
import sys

from aiohttp import web

from bot.config import config
from bot.database.connection import close_db, connect_db
from bot.handlers import setup_routers
from bot.admin import admin_router
from bot.loader import bot, dp
from bot.middlewares import (
BanMiddleware,
FloodMiddleware,
MaintenanceMiddleware,
MediaBlockMiddleware,
UserMiddleware,
)

async def health_check(request):
return web.Response(text="Bot is running")

async def start_webserver():
app = web.Application()
app.router.add_get("/", health_check)

```
runner = web.AppRunner(app)
await runner.setup()

site = web.TCPSite(runner, "0.0.0.0", 8000)
await site.start()
```

async def on_startup() -> None:
config.validate()
await connect_db()
logging.info("RelaxConnect bot started")

async def on_shutdown() -> None:
await close_db()
logging.info("RelaxConnect bot stopped")

async def main() -> None:
logging.basicConfig(
level=logging.INFO,
format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
stream=sys.stdout,
)

```
dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)

dp.update.middleware(UserMiddleware())
dp.update.middleware(BanMiddleware())
dp.update.middleware(MaintenanceMiddleware())
dp.update.middleware(FloodMiddleware())
dp.update.middleware(MediaBlockMiddleware())

root = setup_routers()
root.include_router(admin_router)
dp.include_router(root)

await start_webserver()

await dp.start_polling(
    bot,
    allowed_updates=dp.resolve_used_update_types()
)
```

if **name** == "**main**":
asyncio.run(main())

