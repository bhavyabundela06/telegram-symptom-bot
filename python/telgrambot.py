
from typing import Final
from pathlib import Path
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from dotenv import load_dotenv
import mysql.connector
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)


ENV_PATH = Path(__file__).with_name(".env")
try:
    load_dotenv(ENV_PATH)
except PermissionError:
    fallback_env_path = Path.cwd() / ".env"
    print(f"Could not read {ENV_PATH}. Trying {fallback_env_path} instead.")
    if fallback_env_path != ENV_PATH and fallback_env_path.exists():
        load_dotenv(fallback_env_path)


def get_db_connection():
    """Establishes a secure connection to the Aiven MySQL database."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
    )


def init_db():
    """Creates the symptom_logs table if it does not already exist."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS symptom_logs (
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT,
                symptom VARCHAR(255),
                log_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        print("Database connected and table is ready!")

    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")

    finally:
        if "conn" in locals() and conn.is_connected():
            cursor.close()
            conn.close()


TOKEN: Final = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN is missing! Check your .env file.")

BOT_USERNAME: Final = "@ssymptom_bot"


SYMPTOM_CATEGORIES = {
    "Pain & Aches": [
        "headache", "migraine", "joint pain", "muscle ache", "knee pain",
        "shoulder pain", "neck pain", "hip pain", "wrist pain", "ankle pain",
        "lower back pain", "upper back pain", "chest pain", "earache",
    ],
    "Stomach & Digestion": [
        "stomachache", "nausea", "vomiting", "diarrhea", "constipation",
        "heartburn", "indigestion", "bloating", "loss of appetite",
    ],
    "Cold, Flu & Respiratory": [
        "fever", "cough", "sore throat", "runny nose", "stuffy nose",
        "shortness of breath", "wheezing", "chills", "sneezing",
    ],
    "General & Neurological": [
        "fatigue", "weakness", "dizziness", "trouble sleeping", "confusion",
        "numbness", "tingling", "blurry vision", "ringing in ears",
    ],
    "Skin": [
        "rash", "itching", "bruising", "swelling",
    ],
}


SYMPTOM_ADVICE = {
    "headache": "Drink a large glass of water, rest in a quiet, dark room, and apply a cold compress to your forehead.",
    "migraine": "Drink a large glass of water, rest in a quiet, dark room, and apply a cold compress to your forehead.",
    "stomachache": "Drink warm water or peppermint tea, and try to sit upright.",
    "bloating": "Drink warm water or peppermint tea, and try to sit upright.",
    "constipation": "Drink warm water or peppermint tea, and try to sit upright.",
    "heartburn": "Sip a small amount of water, stay strictly upright, and avoid eating anything else for a bit.",
    "muscle ache": "Stay hydrated, do some very gentle stretching, and apply a warm heating pad to the area.",
    "joint pain": "Stay hydrated, do some very gentle stretching, and apply a warm heating pad to the area.",
    "knee pain": "Stay hydrated, do some very gentle stretching, and apply a warm heating pad to the area.",
    "dizziness": "Please sit or lie down immediately. Sip water slowly and have a small sugary snack if you have not eaten.",
    "confusion": "Please sit or lie down immediately. Sip water slowly and have a small sugary snack if you have not eaten.",
    "fever": "Drink plenty of fluids to stay hydrated and get into bed to rest.",
    "chills": "Drink plenty of fluids to stay hydrated and get into bed to rest.",
}


DEFAULT_ADVICE = (
    "Please drink a glass of water and make sure you are resting comfortably. "
    "If unsure, consult a doctor."
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("Hello, thanks for chatting with me. How can I help you?")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("You can type your symptoms, or use /log_symptoms.")


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("This is a custom command.")


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user:
        return

    user_id = update.message.from_user.id

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT symptom,
                   DATE_FORMAT(
                       DATE_ADD(log_date, INTERVAL '5:30' HOUR_MINUTE),
                       '%b %d, %Y - %h:%i %p'
                   )
            FROM symptom_logs
            WHERE user_id = %s
            ORDER BY log_date DESC
        """, (user_id,))

        records = cursor.fetchall()
        cursor.close()
        conn.close()

        if not records:
            await update.message.reply_text("You do not have any logged symptoms yet.")
            return

        report = "Your Symptom History:\n\n"

        for symptom_val, date_val in records:
            symptom_name = str(symptom_val).title()
            date_logged = str(date_val)
            report += f"- {date_logged} - {symptom_name}\n"

        await update.message.reply_text(report)

    except Exception as e:
        print(f"Database error: {e}")
        await update.message.reply_text("Sorry, there was an error retrieving your history.")


async def log_symptoms_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []

    for category in SYMPTOM_CATEGORIES:
        keyboard.append([InlineKeyboardButton(category, callback_data=f"category_{category}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(
            "Please select what you are feeling right now:",
            reply_markup=reply_markup,
        )


def handle_response(text: str) -> str:
    processed = text.lower()

    if "hello" in processed:
        return "Hey there!"

    if "how are you" in processed:
        return "I am good."

    if "sick" in processed:
        return "Can you describe what symptoms you are feeling?"

    symptoms = []

    for category_symptoms in SYMPTOM_CATEGORIES.values():
        symptoms.extend(category_symptoms)

    for symptom in symptoms:
        if symptom in processed:
            return f"Noted, logging {symptom}."

    if "back pain" in processed:
        return "Noted. Is it lower or upper back pain?"

    return "I do not understand, sorry. You can use /log_symptoms."


async def button_click_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if not query:
        return

    await query.answer()
    data = str(query.data)

    if data.startswith("category_"):
        category_name = data.replace("category_", "")
        symptoms_in_category = SYMPTOM_CATEGORIES.get(category_name, [])

        keyboard = []

        for i in range(0, len(symptoms_in_category), 2):
            row = []

            symptom1 = symptoms_in_category[i]
            row.append(InlineKeyboardButton(symptom1.title(), callback_data=symptom1))

            if i + 1 < len(symptoms_in_category):
                symptom2 = symptoms_in_category[i + 1]
                row.append(InlineKeyboardButton(symptom2.title(), callback_data=symptom2))

            keyboard.append(row)

        keyboard.append([InlineKeyboardButton("Back", callback_data="back_to_categories")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"Select a symptom under {category_name}:",
            reply_markup=reply_markup,
        )
        return

    if data == "back_to_categories":
        keyboard = []

        for category in SYMPTOM_CATEGORIES:
            keyboard.append([InlineKeyboardButton(category, callback_data=f"category_{category}")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "Please select a category:",
            reply_markup=reply_markup,
        )
        return

    selected_symptom = data
    specific_advice = SYMPTOM_ADVICE.get(selected_symptom, DEFAULT_ADVICE)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO symptom_logs (user_id, symptom) VALUES (%s, %s)",
            (query.from_user.id, selected_symptom),
        )

        conn.commit()
        cursor.close()
        conn.close()

        print(f"Successfully saved {selected_symptom} to database.")

    except Exception as e:
        print(f"Database error: {e}")

    final_message = (
        f"Noted. Logging your {selected_symptom}.\n\n"
        f"Quick Tip: {specific_advice}\n\n"
        "Disclaimer: I am just a bot. Please consult a doctor immediately "
        "if your symptoms persist or worsen."
    )

    print(f"Logged: {selected_symptom}")
    await query.edit_message_text(text=final_message)


class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is awake and running!")


def keep_alive():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    message_type = update.message.chat.type
    text = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == "group":
        if BOT_USERNAME in text:
            new_text = text.replace(BOT_USERNAME, " ").strip()
            response = handle_response(new_text)
        else:
            return
    else:
        response = handle_response(text)

    if response.startswith("Noted, logging"):
        detected_symptom = response.replace("Noted, logging ", "").replace(".", "")

        user = update.message.from_user

        if user:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()

                cursor.execute(
                    "INSERT INTO symptom_logs (user_id, symptom) VALUES (%s, %s)",
                    (user.id, detected_symptom),
                )

                conn.commit()
                cursor.close()
                conn.close()

                print(f"Successfully saved text symptom: {detected_symptom}")

            except Exception as e:
                print(f"Database error on text input: {e}")

    print("Bot:", response)
    await update.message.reply_text(response)


async def error(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")


if __name__ == "__main__":
    print("Starting bot....")

    init_db()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("custom", custom_command))
    app.add_handler(CommandHandler("log_symptoms", log_symptoms_command))
    app.add_handler(CommandHandler("history", history_command))

    app.add_handler(CallbackQueryHandler(button_click_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.add_error_handler(error)

    threading.Thread(target=keep_alive, daemon=True).start()

    print("Polling...")
    app.run_polling(poll_interval=5)
