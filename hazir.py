from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random
from db import get_coins, add_coins, remove_coins

TOKEN = "8046324632:AAF1wG7hSkQ8Mi3AKBRxd9UwaCRf1e3VGWY"  # Öz bot tokenini buraya qoy

shop_items = {
    "Netflix 1 otaq": 1600,
    "10x cc": 2000,
    "1x live": 5000
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salam! 👋 Coin botuna xoş gəldin.\n/coinflip, /spin, /balance və /shop əmrlərindən istifadə et.")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    coins = get_coins(user_id)
    await update.message.reply_text(f"💰 Balansın: {coins} coin")

async def coinflip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    result = random.choice(["yazı", "tura"])
    if result == "yazı":
        add_coins(user_id, 10)
        await update.message.reply_text("🪙 Yazı gəldi! +10 coin")
    else:
        await update.message.reply_text("🔄 Tura gəldi! Təəssüf...")

async def spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    emojis = ["🌺", "🌷", "🪷"]
    result = [random.choice(emojis) for _ in range(3)]
    res_str = " ".join(result)
    if result[0] == result[1] == result[2]:
        add_coins(user_id, 30)
        await update.message.reply_text(f"{res_str}\n🎉 Təbriklər! +30 coin qazandın!")
    else:
        await update.message.reply_text(f"{res_str}\n😢 Təəssüf, bu dəfə olmadı...")

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🛒 Mövcud məhsullar:\n"
    for name, price in shop_items.items():
        text += f"• {name} — {price} coin\n"
    await update.message.reply_text(text)

if _name_ == "_main_":
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler(["coinflip", "flip"], coinflip))
    app.add_handler(CommandHandler("spin", spin))
    app.add_handler(CommandHandler("shop", shop))
    
    print("Bot işə düşür...")
    app.run_polling()
