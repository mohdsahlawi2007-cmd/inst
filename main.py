# insta_checker.py
import asyncio
import logging
import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

# ===================== إعداداتك =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")        # بوت تيليجرام
CHAT_ID = int(os.getenv("CHAT_ID"))           # أرسل /id لـ @userinfobot
CHECK_DELAY = 45                          # ثواني بين كل فحص (آمن جدًا)

# ملفات
USERNAMES_FILE = "insta_usernames.txt"
AVAILABLE_FILE = "insta_available.txt"

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def send_telegram_alert(username):
    message = f"""
🔥 يوزر إنستغرام نادر صار متاح الحين!

@{username}

رابط الحجز الفوري:
https://instagram.com/{username}

#متاح #يوزر_انستا #نادر
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": True
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload) as resp:
            if resp.status == 200:
                logging.info(f"تم إرسال تنبيه لـ @{username}")
            else:
                logging.error(f"فشل إرسال التنبيه: {await resp.text()}")

async def is_username_available(username):
    url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
    headers = {
        "User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.get(url, timeout=15) as resp:
                if resp.status == 404:
                    return True   # متاح 100%
                if resp.status == 200:
                    return False  # مأخوذ
                return None       # خطأ غريب
        except asyncio.TimeoutError:
            return None
        except Exception:
            return None

async def main():
    if not BOT_TOKEN or CHAT_ID == 0:
        logging.error("حط BOT_TOKEN و CHAT_ID في ملف .env صح!")
        return

    if not os.path.exists(USERNAMES_FILE):
        logging.error(f"ملف {USERNAMES_FILE} مو موجود!")
        return

    with open(USERNAMES_FILE, 'r', encoding='utf-8') as f:
        usernames = [line.strip().replace('@', '') for line in f if line.strip() and not line.startswith('#')]

    logging.info(f"بدأ فحص {len(usernames)} يوزر إنستغرام...")

    while True:  # يفحص 24 ساعة بدون توقف
        for i, username in enumerate(usernames, 1):
            print(f"[{i}/{len(usernames)}] جاري فحص @{username}...")
            available = await is_username_available(username)
            
            if available is True:
                print(f"✅ @{username} → متاح الحين!")
                await send_telegram_alert(username)
                
                with open(AVAILABLE_FILE, 'a', encoding='utf-8') as f:
                    f.write(f"@{username} - {asyncio.get_event_loop().time():.0f}\n")
                
                # اختياري: احذفه من القائمة عشان ما يفحصه مرة ثانية
                # usernames.remove(username)
                
            elif available is False:
                print(f"❌ @{username} → مأخوذ")
            else:
                print(f"⚠️ @{username} → خطأ في الاتصال، بنعاد المحاولة...")
            
            await asyncio.sleep(CHECK_DELAY)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("تم إيقاف الفاحص يدويًا")
