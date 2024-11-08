import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)
import psycopg2
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Other parts of the code...

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Введите номер своей группы:")

# Handle messages
def handle_message(update: Update, context: CallbackContext) -> None:
    group_number = update.message.text.strip()
    context.user_data['group_number'] = group_number

    # Show today's timetable
    today = datetime.now().date()
    timetable = fetch_timetable(group_number, today)
    send_timetable(update, context, timetable, today)

# Send timetable function
def send_timetable(update, context, timetable, date):
    if not timetable:
        update.message.reply_text("Пары на сегодня не обнаружены.")
        return

    message = f"Timetable for {date}:\n"
    for subject, time in timetable:
        message += f"{time}: {subject}\n"

    update.message.reply_text(message)
    # Set up quick buttons
    buttons = [
        KeyboardButton("Вчера"),
        KeyboardButton("Сегодня"),
        KeyboardButton("Завтра"),
    ]
    reply_markup = ReplyKeyboardMarkup([buttons], one_time_keyboard=True)
    update.message.reply_text("Выбери дату:", reply_markup=reply_markup)

# Handle date selection
def handle_date_selection(update: Update, context: CallbackContext) -> None:
    group_number = context.user_data.get('group_number')

    if not group_number:
        update.message.reply_text("Введите номер своей группы.")
        return

    choice = update.message.text.strip()
    today = datetime.now().date()

    if choice == "Вчера":
        date = today - timedelta(days=1)
    elif choice == "Завтра":
        date = today + timedelta(days=1)
    else:  # Today
        date = today

    timetable = fetch_timetable(group_number, date)
    send_timetable(update, context, timetable, date)

def main() -> None:
    application = ApplicationBuilder().token("7594024235:AAHYdCtFUFn7E1x4yMe1weYaJvMKzToeR7g").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date_selection))

    application.run_polling()

if __name__ == '__main__':
    main()
