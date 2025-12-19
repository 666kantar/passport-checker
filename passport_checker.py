import requests
import re
from datetime import datetime
import os


# 🔐 Твої ключі
ZENROWS_API_KEY = os.getenv("ZENROWS_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("📬 Повідомлення надіслано в Telegram")
    except Exception as e:
        print("❗️ Помилка надсилання в Telegram:", e)

def get_token_from_html():
    url = "https://toronto.pasport.org.ua/solutions/e-queue"
    params = {
        "apikey": ZENROWS_API_KEY,
        "url": url,
        "js_render": "true",
        "premium_proxy": "true",
        "antibot": "true",
        "wait": "20000"
    }
    response = requests.get("https://api.zenrows.com/v1/", params=params)
    response.raise_for_status()
    html = response.text

    with open("zenrows_response.html", "w", encoding="utf-8") as f:
        f.write(html)

    match = re.search(r"token\s*:\s*'([^']+)'", html)
    if match:
        return match.group(1)
    else:
        raise Exception("❌ Токен не знайдено в HTML")

def fetch_days(token):
    url = "https://qs.pasport.org.ua/api/v1/PreReg/GetDays?LangId=1&ServiceCenterId=46&ServiceId=4"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {token}",
        "organisation": "3ef9db45-e8d8-40e2-bf70-21e9f91b4cc9",
        "Origin": "https://toronto.pasport.org.ua",
        "Referer": "https://toronto.pasport.org.ua/",
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    print("🔐 Отримуємо токен через ZenRows...")
    try:
        token = get_token_from_html()
        print("✅ Токен отримано!")

        print("📅 Отримуємо доступні дати...")
        data = fetch_days(token)
        available = [
            d["datePart"][:10]
            for d in data.get("days", [])
            if d.get("isAllowed") is True
        ]

        if available:
            message = f"✅ Вільні дати для запису:\n<b>{', '.join(available)}</b>"
        else:
            message = f"❌ Немає вільних дат на {datetime.now().strftime('%Y-%m-%d')}"

        print(message)
        send_telegram_message(message)

    except Exception as e:
        print("❗️ Помилка:", e)
        send_telegram_message(f"❗️ Помилка в скрипті: {e}")

if __name__ == "__main__":
    main()
