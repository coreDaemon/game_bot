import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import BOT_TOKEN
from steam_api import extract_app_id, get_price
from database import engine, SessionLocal
from models import Base, TrackedGame
from scheduler import start_scheduler


# ------------------ BUTTON HELPER ------------------


def build_buttons(app_id, game_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🎮 View on Steam",
                url=f"https://store.steampowered.com/app/{app_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ Stop Tracking",
                callback_data=f"remove_{game_id}"
            )
        ]
    ])


# ------------------ BASIC COMMANDS ------------------


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is alive.")


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pong.")


# ------------------ TRACK COMMAND ------------------


async def track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /track <steam_url>")
        return

    url = context.args[0]
    app_id = extract_app_id(url)

    if not app_id:
        await update.message.reply_text("Invalid Steam URL.")
        return

    result = get_price(app_id)

    if not result:
        await update.message.reply_text("Could not fetch game info.")
        return

    name, price_text = result

    price_value = 0.0
    if price_text.startswith("₹"):
        price_value = float(price_text.replace("₹", ""))

    db = SessionLocal()

    existing = db.query(TrackedGame).filter_by(
        app_id=app_id,
        chat_id=update.message.chat_id
    ).first()

    if existing:
        await update.message.reply_text("Already tracking this game.")
        db.close()
        return

    game = TrackedGame(
        app_id=app_id,
        name=name,
        current_price=price_value,
        chat_id=update.message.chat_id,
    )

    db.add(game)
    db.commit()
    game_id = game.id
    db.close()

    buttons = build_buttons(app_id, game_id)

    await update.message.reply_text(
        f"🎮 *{name}*\n💰 Price: {price_text}\n📉 You'll be notified on drops.",
        reply_markup=buttons,
        parse_mode="Markdown"
    )


# ------------------ LIST COMMAND ------------------


async def list_games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()

    games = db.query(TrackedGame).filter_by(
        chat_id=update.message.chat_id
    ).all()

    if not games:
        await update.message.reply_text("No tracked games.")
        db.close()
        return

    msg = "📋 *Tracked Games:*\n\n"

    for game in games:
        msg += f"*{game.id}.* {game.name} — ₹{game.current_price}\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

    db.close()


# ------------------ REMOVE COMMAND ------------------


async def remove_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /remove <id>")
        return

    try:
        game_id = int(context.args[0])
    except:
        await update.message.reply_text("Invalid ID.")
        return

    db = SessionLocal()

    game = db.query(TrackedGame).filter_by(
        id=game_id,
        chat_id=update.message.chat_id
    ).first()

    if not game:
        await update.message.reply_text("Game not found.")
        db.close()
        return

    db.delete(game)
    db.commit()
    db.close()

    await update.message.reply_text("❌ Tracking removed.")


# ------------------ BUTTON CALLBACK ------------------


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("remove_"):
        game_id = int(data.split("_")[1])

        db = SessionLocal()

        game = db.query(TrackedGame).filter_by(
            id=game_id,
            chat_id=query.message.chat_id
        ).first()

        if not game:
            await query.edit_message_text("Already removed.")
            db.close()
            return

        db.delete(game)
        db.commit()
        db.close()

        await query.edit_message_text("❌ Tracking removed.")


# ------------------ AUTO LINK DETECTION ------------------


async def auto_detect_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not text.startswith("https://store.steampowered.com/app/"):
        return

    app_id = extract_app_id(text)
    if not app_id:
        return

    result = get_price(app_id)
    if not result:
        return

    name, price_text = result

    price_value = 0.0
    if price_text.startswith("₹"):
        price_value = float(price_text.replace("₹", ""))

    db = SessionLocal()

    existing = db.query(TrackedGame).filter_by(
        app_id=app_id,
        chat_id=update.message.chat_id
    ).first()

    if existing:
        await update.message.reply_text("Already tracking this game.")
        db.close()
        return

    game = TrackedGame(
        app_id=app_id,
        name=name,
        current_price=price_value,
        chat_id=update.message.chat_id,
    )

    db.add(game)
    db.commit()
    game_id = game.id
    db.close()

    buttons = build_buttons(app_id, game_id)

    await update.message.reply_text(
        f"🎮 *{name}*\n💰 Price: {price_text}\n📉 Tracking started automatically.",
        reply_markup=buttons,
        parse_mode="Markdown"
    )


# ------------------ MAIN APP ------------------


async def main():
    Base.metadata.create_all(bind=engine)

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("track", track))
    app.add_handler(CommandHandler("list", list_games))
    app.add_handler(CommandHandler("remove", remove_game))

    app.add_handler(CallbackQueryHandler(button_callback))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, auto_detect_link)
    )

    print("Bot running...")

    await app.initialize()
    await app.start()

    start_scheduler(app)

    await app.updater.start_polling()

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())