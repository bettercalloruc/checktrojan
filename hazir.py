import telebot
import random
import sqlite3
import time

TOKEN = "8046324632:AAF1wG7hSkQ8Mi3AKBRxd9UwaCRf1e3VGWY"   # Bot tokenini buraya yaz
ADMIN_ID = 7966095564          # Sənin Telegram admin ID-n (dəyişdir)

bot = telebot.TeleBot(TOKEN)

# Verilənlər bazasının qurulması
conn = sqlite3.connect("coin_game.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER,
    last_daily INTEGER DEFAULT 0
)
""")
conn.commit()
coin_game.db.setup()

# /start: İstifadəçini qeydiyyata alır və balansı 100 coin edir
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, 100))
        conn.commit()
        bot.send_message(user_id, "Xoş gəldin! Balansın 100 coinlə başladı.\n /spin  Spin edir. \n /shop Magazani acir \n /flip yazi tura edir. \n /balance Balansdaki pul. \n /daily Gunluk gelir.\n /leaderbord En yuksek coinli 5 user. ")
    else:
        bot.send_message(user_id, "Sən artıq qeydiyyatdasan.")

# /balance: İstifadəçinin balansını göstərir
@bot.message_handler(commands=['balance'])
def balance(message):
    user_id = message.from_user.id
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result:
        bot.send_message(user_id, f"Balansın: {result[0]} coin")
    else:
        bot.send_message(user_id, "Əvvəlcə /start yazmalısan.")

# /flip: Yazı-tura oyunu; düzgün təxmin +10, səhv təxmin -10 coin
@bot.message_handler(commands=['flip'])
def flip(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add("yazı", "tura")
    bot.send_message(message.chat.id, "Yazı ya tura? Seç:", reply_markup=markup)
    bot.register_next_step_handler(message, process_flip)

def process_flip(message):
    user_id = message.from_user.id
    user_choice = message.text.lower()
    if user_choice not in ["yazı", "tura"]:
        bot.send_message(user_id, "Yalnız 'yazı' və ya 'tura' yaz.")
        return

    result = random.choice(["yazı", "tura"])
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        bot.send_message(user_id, "Əvvəlcə /start yazmalısan.")
        return

    balance_val = row[0]
    if user_choice == result:
        balance_val += 10
        bot.send_message(user_id, f"Uğur! {result} gəldi. +10 coin qazandın.")
    else:
        balance_val -= 10
        bot.send_message(user_id, f"Təəssüf! {result} gəldi. -10 coin itirdin.")

    cursor.execute("UPDATE users SET balance=? WHERE user_id=?", (balance_val, user_id))
    conn.commit()

# /daily: Hər 24 saatda bir 50 coin bonus verir
@bot.message_handler(commands=['daily'])
def daily(message):
    user_id = message.from_user.id
    now = int(time.time())
    cursor.execute("SELECT balance, last_daily FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if row:
        balance_val, last_daily = row
        if now - last_daily >= 86400:
            balance_val += 50
            cursor.execute("UPDATE users SET balance=?, last_daily=? WHERE user_id=?", (balance_val, now, user_id))
            conn.commit()
            bot.send_message(user_id, "🎁 Gündəlik bonus: +50 coin!")
        else:
            qalan = 86400 - (now - last_daily)
            saat = qalan // 3600
            deqiqe = (qalan % 3600) // 60
            bot.send_message(user_id, f"⏳ Gündəlik bonus üçün {saat} saat {deqiqe} dəqiqə qalıb.")
    else:
        bot.send_message(user_id, "Əvvəlcə /start yazmalısan.")

# /leaderboard: Ən yüksək balanslı 5 istifadəçini sıralayır
@bot.message_handler(commands=['leaderboard'])
def leaderboard(message):
    cursor.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 5")
    rows = cursor.fetchall()
    response = "🏆 Ən varlı 5 oyunçu:\n\n"
    for i, (uid, balance_val) in enumerate(rows, 1):
        response += f"{i}. ID: {uid} — {balance_val} coin\n"
    bot.send_message(message.chat.id, response)

# /shop: Mağazadakı item-ləri göstərir (hal-hazırda sadəcə mətn)
@bot.message_handler(commands=['shop'])
def shop(message):
    response = ("🛒 Mağaza:\n\n"
                "- 🔑 'Premium rozet' – 1000 coin\n"
                "- 🎲 'Şans artırıcı' – 500 coin\n\n"
                "(Almaq funksiyası tezliklə gələcək!)")
    bot.send_message(message.chat.id, response)

# /spin: 3 ədəd random emoji seçilir; əgər 3-ü eynidirsə, +30 coin qazandırır
@bot.message_handler(commands=['spin'])
def spin(message):
    user_id = message.from_user.id
    emojis = ['🌺', '🌷', '🪷']
    result_emojis = [random.choice(emojis) for _ in range(3)]
    result_text = ' | '.join(result_emojis)
    if result_emojis[0] == result_emojis[1] == result_emojis[2]:
        cursor.execute("UPDATE users SET balance = balance + 30 WHERE user_id = ?", (user_id,))
        conn.commit()
        bot.send_message(user_id, f"{result_text}\n🎉 Təbriklər! 30 coin qazandın!")
    else:
        bot.send_message(user_id, f"{result_text}\n😢 Təəssüf, bu dəfə olmadı.")

# Admin əmrləri: Yalnız ADMIN_ID olan istifadəçi tərəfindən icazə verilmiş əmrlər

# /admincoin: Başqa bir istifadəçinin balansına coin əlavə edir
@bot.message_handler(commands=['admincoin'])
def admincoin(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Bu əmri istifadə etmək icazəniz yoxdur.")
        return
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.send_message(message.chat.id, "İstifadə: /admincoin <user_id> <miqdar>")
            return
        target_id = int(parts[1])
        coin_amount = int(parts[2])
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (coin_amount, target_id))
        conn.commit()
        bot.send_message(message.chat.id, f"User {target_id} üçün {coin_amount} coin əlavə edildi.")
    except Exception:
        bot.send_message(message.chat.id, "Xəta baş verdi. Əmr formatını yoxlayın.")

# /delcoin: Başqa bir istifadəçinin balansından coin çıxır
@bot.message_handler(commands=['delcoin'])
def delcoin(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Bu əmri istifadə etmək icazəniz yoxdur.")
        return
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.send_message(message.chat.id, "İstifadə: /delcoin <user_id> <miqdar>")
            return
        target_id = int(parts[1])
        coin_amount = int(parts[2])
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (coin_amount, target_id))
        conn.commit()
        bot.send_message(message.chat.id, f"User {target_id} üçün {coin_amount} coin çıxıldı.")
    except Exception:
        bot.send_message(message.chat.id, "Xəta baş verdi. Əmr formatını yoxlayın.")

bot.polling()
