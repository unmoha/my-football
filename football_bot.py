import asyncio
import requests
import re
from telethon import TelegramClient
from googletrans import Translator

# ================= CONFIG =================
api_id = 37806549
api_hash = '0def3994b17eec4000f7eaf491158d71'

BOT_TOKEN = "8743984646:AAFk1VfO4uHcEHZ_8CO-Z-76AKHkj4YSzLo"
CHANNEL_ID = -1003946601319

# Mix of your Amharic + fast news sources
SOURCE_CHANNELS = [
    "bisrat_sport_433et",
    "Sport_433et",
    "tikvahethsport",
    "dailysportethiopia",
    "TheEuropeanLad",
    "footballinsider247"
]
# ==========================================

translator = Translator()
posted = set()

# 🚀 Send message
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

# 🌍 Translate to Amharic
def to_amharic(text):
    try:
        return translator.translate(text, dest='am').text
    except:
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

                        # Only translate if not already Amharic
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
            await asyncio.sleep(60)  # ⏱ 1 minute

asyncio.run(main())