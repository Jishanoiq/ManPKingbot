import logging
from aiogram import Bot, Dispatcher, executor, types
import sqlite3

API_TOKEN = '8134639452:AAE0hur_h7ZlFK7sT4ua6GrC1kbtKO2-Ze0'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    referrer_id INTEGER,
    balance REAL DEFAULT 0
)''')
conn.commit()

def add_user(user_id, referrer_id=None):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (user_id, referrer_id) VALUES (?, ?)", (user_id, referrer_id))
        conn.commit()

def add_balance(user_id, amount):
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    conn.commit()

def get_balance(user_id):
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    args = message.get_args()
    referrer_id = int(args) if args.isdigit() else None
    add_user(message.from_user.id, referrer_id)
    await message.reply("👋 Welcome to ManPKing Bot! Use /ads to earn by viewing ads.")

@dp.message_handler(commands=['ads'])
async def send_ad(message: types.Message):
    add_balance(message.from_user.id, 0.10)
    await message.answer("📺 Ad watched! $0.10 added to your balance.")

@dp.message_handler(commands=['balance'])
async def check_balance(message: types.Message):
    bal = get_balance(message.from_user.id)
    await message.reply(f"💰 Your balance: ${bal:.2f}")

@dp.message_handler(commands=['referral'])
async def referral_link(message: types.Message):
    user_id = message.from_user.id
    await message.reply(f"🔗 Your referral link: https://t.me/ManPKing_bot?start={user_id}")

@dp.message_handler(commands=['withdraw'])
async def withdraw_request(message: types.Message):
    bal = get_balance(message.from_user.id)
    if bal >= 5:
        await message.reply("✅ Withdrawal request sent! Our admin will contact you.")
    else:
        await message.reply("❌ Minimum $5 required to withdraw.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
