import asyncio
import os
import re
import requests
from telethon import TelegramClient
from deep_translator import GoogleTranslator

# ================= CONFIG =================
api_id = int(os.getenv('TELEGRAM_API_ID'))
api_hash = os.getenv('TELEGRAM_API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

# Mix of Amharic + fast news sources
SOURCE_CHANNELS = [
    "bisrat_sport_433et",
    "Sport_433et",
    "tikvahethsport",
    "dailysportethiopia",
    "TheEuropeanLad",
    "footballinsider247"
]
# ==========================================

posted = set()

# 🚀 Send message to Telegram channel
def send_to_channel(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text
    }
    r = requests.post(url, data=data)
    print("✅ SEND:", r.text)

# 🧹 Clean text
def clean_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    return text.strip()

# 🌍 Translate to Amharic (FIXED)
def to_amharic(text):
    try:
        return GoogleTranslator(source='auto', target='am').translate(text)
    except Exception as e:
        print("⚠️ Translation failed:", e)
        return text

# 🔥 Filter important news
def is_important(text):
    keywords = [
        "here we go",
        "confirmed",
        "deal",
        "official",
        "transfer",
        "agreement",
        "sign",
        "medical"
    ]
    return any(k in text.lower() for k in keywords)

# 🔁 Main bot
async def main():
    async with TelegramClient('session', api_id, api_hash) as client:
        print("✅ Logged in as USER")
        print("🚀 Bot started...")

        while True:
            print("\n📡 FETCHING...\n")

            for channel in SOURCE_CHANNELS:
                try:
                    print(f"➡️ {channel}")

                    entity = await client.get_entity(channel)
                    messages = await client.get_messages(entity, limit=5)

                    for msg in messages:
                        if not msg.text:
                            continue

                        original = msg.text.strip()

                        if original in posted:
                            continue

                        posted.add(original)

                        cleaned = clean_text(original)

                        # Translate only if not Amharic already
                        if not any('\u1200' <= c <= '\u137F' for c in cleaned):
                            if is_important(cleaned):
                                cleaned = to_amharic(cleaned)

                        final_text = f"""❗️ ሰበር ዜና

{cleaned}

📢 @ethio4213"""

                        send_to_channel(final_text)
                        await asyncio.sleep(2)

                except Exception as e:
                    print(f"❌ {channel}:", e)

            print("\n⏳ Waiting 1 minute...\n")
            await asyncio.sleep(60)

# 🚀 RUN BOT
asyncio.run(main())
