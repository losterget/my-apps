import csv
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Глобальные переменные
USER_DATA_FILE = "user_data.csv"
IMAGE_DIR = "images"  # Папка с изображениями

# Создание файла для хранения данных пользователей
if not os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["user_id", "state", "timestamp"])

# Состояния игры
class GameState:
    START = "start"
    LEGGINGS = "leggings"
    BRA = "bra"
    GYM_OR_HOME = "gym_or_home"
    SWIMSUIT = "swimsuit"
    NEW_SWIMSUIT = "new_swimsuit"  # Новый шаг для второго выбора купальника
    POSE_WINDOW = "pose_window"
    JEANS = "jeans"
    FINAL_STEP = "final_step"

# Сохранение состояния пользователя
def save_user_state(user_id, state):
    with open(USER_DATA_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([user_id, state, datetime.now()])

# Загрузка состояния пользователя
def load_user_state(user_id):
    with open(USER_DATA_FILE, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == str(user_id):
                return {
                    "state": row[1],
                    "timestamp": datetime.fromisoformat(row[2])
                }
    return None

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    save_user_state(user_id, GameState.START)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Красотка собирается на вб", callback_data="start_game")]
    ])
    await update.message.reply_text("Добро пожаловать! 😊 Хочешь поиграть?", reply_markup=keyboard)

# Обработчик callback-кнопок
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    # Начало игры
    if data == "start_game":
        save_user_state(user_id, GameState.LEGGINGS)
        # Группировка фотографий одежды
        media_group = [
            open(f"{IMAGE_DIR}/dress.jpg", "rb"),
            open(f"{IMAGE_DIR}/shorts.jpg", "rb")
        ]
        await query.edit_message_text("Отлично! Во что мне сегодня пойти на вб? 🤔")
        await query.message.reply_media_group(media=[InputMediaPhoto(photo) for photo in media_group])
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Платье", callback_data="dress"),
             InlineKeyboardButton("Шортики", callback_data="shorts")]
        ])
        await query.message.reply_text("Выбери одежду:", reply_markup=keyboard)

    # Шаг 1: Выбор одежды
    elif data in ["dress", "shorts"]:
        save_user_state(user_id, GameState.LEGGINGS)
        # Группировка фотографий лосин
        media_group = [
            open(f"{IMAGE_DIR}/leggings_1.jpg", "rb"),
            open(f"{IMAGE_DIR}/leggings_2.jpg", "rb")
        ]
        await query.edit_message_text(f"Отлично! Я выбрала {data}. Теперь я пришла в магазин и заказала лосины. Какие тебе больше нравятся?")
        await query.message.reply_media_group(media=[InputMediaPhoto(photo) for photo in media_group])
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Лосины 1", callback_data="leggings_1"),
             InlineKeyboardButton("Лосины 2", callback_data="leggings_2")]
        ])
        await query.message.reply_text("Выбери лосины:", reply_markup=keyboard)

    # Шаг 2: Выбор лосин
    elif data.startswith("leggings"):
        save_user_state(user_id, GameState.BRA)
        # Группировка фотографий лифчиков
        media_group = [
            open(f"{IMAGE_DIR}/bra_1.jpg", "rb"),
            open(f"{IMAGE_DIR}/bra_2.jpg", "rb")
        ]
        await query.edit_message_text("Да, мне тоже этот понравился больше! 😊 Я ещё заказала лифчик. Какой заберем?")
        await query.message.reply_media_group(media=[InputMediaPhoto(photo) for photo in media_group])
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Лифчик 1", callback_data="bra_1"),
             InlineKeyboardButton("Лифчик 2", callback_data="bra_2")]
        ])
        await query.message.reply_text("Выбери лифчик:", reply_markup=keyboard)

    # Шаг 3: Выбор лифчика
    elif data.startswith("bra"):
        save_user_state(user_id, GameState.GYM_OR_HOME)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Домой померить", callback_data="home"),
             InlineKeyboardButton("В спортивный зал", callback_data="gym")]
        ])
        await query.edit_message_text("Классный выбор! 👌 Теперь решай: куда пойдем?")
        await query.message.reply_text("Куда пойдем?", reply_markup=keyboard)

    # Шаг 4: Выбор между домом и залом
    elif data == "home":
        save_user_state(user_id, GameState.SWIMSUIT)
        # Группировка фотографий купальников
        media_group = [
            open(f"{IMAGE_DIR}/swimsuit_1.jpg", "rb"),
            open(f"{IMAGE_DIR}/swimsuit_2.jpg", "rb")
        ]
        await query.edit_message_text("Дома уютнее! 😊 Давай померим купальники.")
        await query.message.reply_media_group(media=[InputMediaPhoto(photo) for photo in media_group])
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Купальник 1", callback_data="swimsuit_1"),
             InlineKeyboardButton("Купальник 2", callback_data="swimsuit_2")]
        ])
        await query.message.reply_text("Выбери купальник:", reply_markup=keyboard)

    elif data == "gym":
        save_user_state(user_id, GameState.POSE_WINDOW)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Да", callback_data="pose_window"),
             InlineKeyboardButton("Нет", callback_data="end")]
        ])
        await query.edit_message_text("В зале всегда весело! 💪")
        await query.message.reply_photo(photo=open(f"{IMAGE_DIR}/elevator.jpg", "rb"), caption="Фото в лифте. Пойти позировать на окно?")
        await query.message.reply_text("Пойти позировать на окно?", reply_markup=keyboard)

    # Шаг 5: Первый выбор купальника
    elif data in ["swimsuit_1", "swimsuit_2"]:
        save_user_state(user_id, GameState.POSE_WINDOW)
        await query.edit_message_text("Отличный выбор купальника! 🏖️ Теперь самое время отправиться в зал!")
        await query.message.reply_photo(photo=open(f"{IMAGE_DIR}/gym_entrance.jpg", "rb"), caption="Мы пришли в зал! 💪")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Да", callback_data="pose_window"),
             InlineKeyboardButton("Нет", callback_data="end")]
        ])
        await query.message.reply_text("Пойти позировать на окно?", reply_markup=keyboard)

    # Шаг 6: Позирование на окне
    elif data == "pose_window":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Да", callback_data="more_photos"),
             InlineKeyboardButton("Нет", callback_data="end")]
        ])
        await query.edit_message_text("На окне получилось круто!")
        await query.message.reply_photo(photo=open(f"{IMAGE_DIR}/window_pose.jpg", "rb"), caption="На окне получилось круто!")
        await query.message.reply_text("Покажу ещё?", reply_markup=keyboard)

    elif data == "more_photos":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Купальник", callback_data="new_swimsuit"),
             InlineKeyboardButton("Джинсы", callback_data="jeans")]
        ])
        await query.edit_message_text("Ещё одна фотка!")
        await query.message.reply_photo(photo=open(f"{IMAGE_DIR}/photo_2.jpg", "rb"), caption="Ещё одна фотка!")
        await query.message.reply_text("Хватит, пойдем домой мерить купальник или наденем джинсы?", reply_markup=keyboard)

    # Новый шаг: Второй выбор купальника ("Левый" или "Правый")
    elif data == "new_swimsuit":
        save_user_state(user_id, GameState.NEW_SWIMSUIT)
        # Группировка фотографий купальников
        media_group = [
            open(f"{IMAGE_DIR}/swimsuit_left.jpg", "rb"),
            open(f"{IMAGE_DIR}/swimsuit_right.jpg", "rb")
        ]
        await query.edit_message_text("Давай выберем новый купальник! Какой тебе больше нравится?")
        await query.message.reply_media_group(media=[InputMediaPhoto(photo) for photo in media_group])
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Левый", callback_data="swimsuit_left"),
             InlineKeyboardButton("Правый", callback_data="swimsuit_right")]
        ])
        await query.message.reply_text("Выбери купальник:", reply_markup=keyboard)

    elif data in ["swimsuit_left", "swimsuit_right"]:
        save_user_state(user_id, GameState.FINAL_STEP)
        # Группировка фотографий топика и джинсов
        media_group = [
            open(f"{IMAGE_DIR}/top.jpg", "rb"),
            open(f"{IMAGE_DIR}/jeans_with_top.jpg", "rb")
        ]
        await query.edit_message_text("Хороший купальник, решила надеть для тебя ещё этот топик и джинсы, как тебе?")
        await query.message.reply_media_group(media=[InputMediaPhoto(photo) for photo in media_group])
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Огонь", callback_data="final_like")]
        ])
        await query.message.reply_text("Как тебе?", reply_markup=keyboard)

    elif data == "jeans":
        save_user_state(user_id, GameState.JEANS)
        # Группировка фотографий джинсов
        media_group = [
            open(f"{IMAGE_DIR}/jeans_1.jpg", "rb"),
            open(f"{IMAGE_DIR}/jeans_2.jpg", "rb")
        ]
        await query.edit_message_text("Джинсы всегда в моде! 👖 Как тебе моя попка?")
        await query.message.reply_media_group(media=[InputMediaPhoto(photo) for photo in media_group])
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Очень нравится", callback_data="final_like"),
             InlineKeyboardButton("Покажи попу в лосинах", callback_data="show_leggings")]
        ])
        await query.message.reply_text("Как тебе моя попка?", reply_markup=keyboard)

    elif data == "final_like":
        await query.edit_message_text(
            "Спасибо за игру! Если тебе нравятся такие обзоры - подписывайся на второй канал https://t.me/swbfoto_bot"
        )

    elif data == "show_leggings":
        # Группировка фотографий попы в лосинах
        media_group = [
            open(f"{IMAGE_DIR}/leggings_pose.jpg", "rb"),
            open(f"{IMAGE_DIR}/leggings_pose_1.jpg", "rb")
        ]
        await query.edit_message_text("Как тебе такой вид?")
        await query.message.reply_media_group(media=[InputMediaPhoto(photo) for photo in media_group])
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Прекрасно", callback_data="final_like")]
        ])
        await query.message.reply_text("Как тебе?", reply_markup=keyboard)

    elif data == "end":
        await query.edit_message_text("Спасибо за игру! До встречи! 😊")

# Запуск бота
if __name__ == "__main__":
    from config import TELEGRAM_BOT_TOKEN  # Импортируем токен из config.py

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))

    application.run_polling()