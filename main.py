import os
import logging
import nest_asyncio
import asyncio
import openai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()


# 🔑 API-sleutels invullen
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# 🛠️ Setup
openai.api_key = OPENAI_API_KEY
nest_asyncio.apply()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 🤖 AI-generatie
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.caption:
        await update.message.reply_text("⚠️ Stuur een foto met een promotietekst in het bijschrift.")
        return

    promo_text = update.message.caption
    prompt = f"Schrijf een aantrekkelijke Instagram-post op basis van deze promotie: '{promo_text}'. Voeg relevante hashtags toe."

    try:
        # Aangepaste aanroep voor de nieuwe OpenAI API
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        ai_text = response.choices[0].message.content.strip()
        await update.message.reply_text("📢 Hier is je AI-marketingtekst:\n\n" + ai_text)
    except Exception as e:
        logging.error(f"Error in AI generation: {str(e)}")
        await update.message.reply_text(f"❌ Er ging iets mis: {str(e)}")

# 🚀 Bot starten
async def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO & filters.Caption(), handle_message))
    logging.info("✅ Bot draait. Stuur een foto met tekst naar je Telegram-bot.")
    await app.run_polling()

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
