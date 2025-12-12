# main.py
import asyncio
import logging
from telethon import TelegramClient
from telethon.tl.functions.contacts import ResolveUsernameRequest
import time
import os

# إعداداتك (غيّرها)

BOT_TOKEN = 'YOUR_BOT_TOKEN'    # بوت من @BotFather
CHAT_ID = YOUR_CHAT_ID          # أرسل /id لبوت @userinfobot

client = TelegramClient('checker_session', API_ID, API_HASH)

async def send_alert(username):
    message = f"🚀 آيدي متاح الحين!\n\n@{username}\n\nحجزه فورًا: https://t.me/{username}"
    await client.send_message(CHAT_ID, message)

async def check_usernames():
    await client.start(bot_token=BOT_TOKEN)
    print("البوت شغال.. يفحص الآيديات")
    
    with open('usernames.txt', 'r', encoding='utf-8') as f:
        usernames = [line.strip().replace('@', '') for line in f if line.strip()]
    
    for username in usernames:
        try:
            # محاولة resolve الآيدي
            result = await client(ResolveUsernameRequest(username))
            print(f"❌ @{username} - مأخوذ")
            time.sleep(20)  # بطيء جدًا عشان ما تنحظر
        except Exception as e:
            if "USERNAME_NOT_OCCUPIED" in str(e):
                print(f"✅ @{username} - متاح 100%!")
                await send_alert(username)
                # احفظ المتاحين في ملف منفصل
                with open('available.txt', 'a') as avail:
                    avail.write(f"@{username}\n")
            else:
                print(f"⚠️ @{username} - خطأ غريب")
        
        time.sleep(25)  # زيادة الأمان

    print("خلص الفحص كامل!")

with client:
    client.loop.run_until_complete(check_usernames())
