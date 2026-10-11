import random
import telebot
from telebot import types

TOKEN = "8944937820:AAGTuY1unmTLnBirMs6HDJVHS4Y8KCXr1uw"
bot = telebot.TeleBot(TOKEN)

TRIGGER_WORDS = ["/mem", "mem", "мем", "/мем", "meme"]


@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id

    # 1. Создаем блок инлайн-кнопок для закрепленного сообщения (только мемы)
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    btn_next = types.InlineKeyboardButton("🎲 Случайный мем", callback_data="next_meme")
    btn_all = types.InlineKeyboardButton("🗂️ Вся коллекция", callback_data="all_memes")

    # Распределяем две кнопки в один ряд
    inline_markup.add(btn_next, btn_all)

    # 2. Отправляем сообщение-навигацию
    navigation_text = (
        "📌 *Навигация по боту*\n\n"
        "Используйте кнопки ниже, чтобы управлять ботом в любой момент. "
        "Это сообщение закреплено вверху экрана для вашего удобства! 👇"
    )

    sent_msg = bot.send_message(
        chat_id=chat_id,
        text=navigation_text,
        parse_mode="Markdown",
        reply_markup=inline_markup
    )

    # 3. Закрепляем сообщение без лишних звуков уведомлений
    try:
        bot.pin_chat_message(
            chat_id=chat_id,
            message_id=sent_msg.message_id,
            disable_notification=True
        )
    except telebot.apihelper.ApiTelegramException:
        pass

    # 4. Включаем обычную нижнюю кнопку "Мем" в поле ввода для подстраховки
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    reply_markup.add(types.KeyboardButton("Мем"))

    bot.send_message(
        chat_id=chat_id,
        text="Нижняя панель управления тоже активирована! ⌨️",
        reply_markup=reply_markup
    )


@bot.message_handler(func=lambda m: m.text and m.text.lower() in TRIGGER_WORDS)
def send_first_meme(message):
    chat_id = message.chat.id

    try:
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)
    except telebot.apihelper.ApiTelegramException:
        pass

    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    btn_next = types.InlineKeyboardButton("🔥 Еще мем!", callback_data="next_meme")
    btn_all = types.InlineKeyboardButton("🗂️ Показать все", callback_data="all_memes")
    inline_markup.add(btn_next, btn_all)

    memes = ['mem1.png', 'mem2.png', 'mem3.png']
    random_meme = random.choice(memes)

    try:
        bot.send_photo(
            chat_id=chat_id,
            photo=open(random_meme, 'rb'),
            caption="Держи мем! Теперь используй кнопки снизу 👇",
            reply_markup=inline_markup
        )
        bot.send_message(chat_id, "Нижняя панель скрыта.", reply_markup=types.ReplyKeyboardRemove())
    except FileNotFoundError:
        bot.reply_to(message, f"Ошибка: Файл '{random_meme}' не найден!")


@bot.callback_query_handler(func=lambda call: call.data == "next_meme")
def callback_next_meme(call):
    bot.answer_callback_query(call.id)

    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    btn_next = types.InlineKeyboardButton("🔥 Еще мем!", callback_data="next_meme")
    btn_all = types.InlineKeyboardButton("🗂️ Показать все", callback_data="all_memes")
    inline_markup.add(btn_next, btn_all)

    memes = ['mem1.png', 'mem2.png', 'mem3.png']
    random_meme = random.choice(memes)

    try:
        bot.edit_message_media(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            media=types.InputMediaPhoto(
                media=open(random_meme, 'rb'),
                caption="Мем обновился! 🔄🎲"
            ),
            reply_markup=inline_markup
        )
    except FileNotFoundError:
        bot.send_message(call.message.chat.id, f"Ошибка: Файл '{random_meme}' не найден!")
    except telebot.apihelper.ApiTelegramException as e:
        if "message is not modified" in str(e):
            bot.answer_callback_query(call.id, text="Выпал тот же самый мем! Нажми еще раз 😉", show_alert=False)


@bot.callback_query_handler(func=lambda call: call.data == "all_memes")
def callback_all_memes(call):
    bot.answer_callback_query(call.id, text="Отправляю всю коллекцию! 📦")

    try:
        media_group = [
            types.InputMediaPhoto(open('mem1.png', 'rb'), caption="Вся коллекция мемов! 🎉"),
            types.InputMediaPhoto(open('mem2.png', 'rb')),
            types.InputMediaPhoto(open('mem3.png', 'rb'))
        ]
        bot.send_media_group(chat_id=call.message.chat.id, media=media_group)
    except FileNotFoundError:
        bot.send_message(call.message.chat.id, "Ошибка: Один из файлов коллекции (mem1-3.png) не найден!")


if __name__ == "__main__":
    print("Бот запущен!")
    bot.infinity_polling()
