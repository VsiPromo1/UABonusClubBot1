from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_TOKEN, CHANNELS, ADMIN_ID, MIN_WITHDRAW
from database import register_user, get_user_balance, save_withdrawal

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(KeyboardButton("Запросити друзів"))
menu.add(KeyboardButton("Баланс"), KeyboardButton("Вивід коштів"))

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    args = message.get_args()
    referrer_id = int(args) if args.isdigit() and int(args) != user_id else None

    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=f"@{ch['name']}", user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                kb = InlineKeyboardMarkup().add(InlineKeyboardButton("Підписатись", url=ch["url"]))
                await message.answer("Підпишіться на канал, щоб продовжити.", reply_markup=kb)
                return
        except:
            await message.answer("Помилка перевірки підписки.")
            return

    register_user(user_id, referrer_id)
    await message.answer("Вітаємо! Ви зареєстровані в системі.", reply_markup=menu)

@dp.message_handler(lambda msg: msg.text == "Запросити друзів")
async def invite(message: types.Message):
    user_id = message.from_user.id
    link = f"https://t.me/YOUR_BOT_USERNAME?start={user_id}"
    await message.answer(f"Ваше реферальне посилання:
{link}")

@dp.message_handler(lambda msg: msg.text == "Баланс")
async def balance(message: types.Message):
    balance = get_user_balance(message.from_user.id)
    await message.answer(f"Ваш баланс: {balance:.2f} грн")

@dp.message_handler(lambda msg: msg.text == "Вивід коштів")
async def withdraw(message: types.Message):
    user_id = message.from_user.id
    balance = get_user_balance(user_id)
    if balance < MIN_WITHDRAW:
        await message.answer("Мінімальна сума для виводу — 150 грн")
        return
    await message.answer("Введіть номер банківської картки:")

    @dp.message_handler()
    async def get_card(msg: types.Message):
        card = msg.text.strip().replace(" ", "")
        if not card.isdigit() or len(card) not in [16, 19]:
            await msg.answer("Невірний формат картки.")
            return
        save_withdrawal(user_id, card, balance)
        await msg.answer("Заявка на вивід надіслана.")
        await bot.send_message(
            ADMIN_ID,
            f"Нова заявка на виплату:\nID: {user_id}\nСума: {balance:.2f} грн\nКартка: {card}"
        )

if __name__ == "__main__":
    executor.start_polling(dp)
