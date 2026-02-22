from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import SessionLocal
from models import TrackedGame
from steam_api import get_price

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def start_scheduler(app):

    scheduler = AsyncIOScheduler()

    async def check_prices():
        db = SessionLocal()

        games = db.query(TrackedGame).all()

        for game in games:
            result = get_price(game.app_id)

            if not result:
                continue

            name, price_text = result

            # Skip free/unpriced games
            if not price_text.startswith("₹"):
                continue

            new_price = float(price_text.replace("₹", ""))

            # PRICE DROP DETECTED
            if new_price < game.current_price:

                buttons = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "🎮 Open Store",
                            url=f"https://store.steampowered.com/app/{game.app_id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "❌ Stop Tracking",
                            callback_data=f"remove_{game.id}"
                        )
                    ]
                ])

                await app.bot.send_message(
                    chat_id=game.chat_id,
                    text=(
                        f"🔥 *PRICE DROP!*\n\n"
                        f"🎮 *{name}*\n"
                        f"💰 Old Price: ₹{game.current_price}\n"
                        f"💸 New Price: {price_text}"
                    ),
                    reply_markup=buttons,
                    parse_mode="Markdown"
                )

                # Update stored price
                game.current_price = new_price

        db.commit()
        db.close()

    # Check every hour (change to minutes=1 for testing)
    scheduler.add_job(check_prices, "interval", minutes=1)

    scheduler.start()