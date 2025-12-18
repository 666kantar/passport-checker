import requests
from bs4 import BeautifulSoup
import os

# 🔐 Секрети
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ABSTRACT_API_KEY = "fc69147f86a84a53ba4cc18bb2ef67bd"

if not BOT_TOKEN or not CHAT_ID:
    print("❌ Не передано TELEGRAM_BOT_TOKEN або TELEGRAM_CHAT_ID")
    exit(1)

try:
    print("🌐 Надсилаємо запит через Abstract Web Scraping API...")
    url = "https://pasport.org.ua/solutions/e-queue"
    api_url = f"https://scrape.abstractapi.com/v1/?api_key={ABSTRACT_API_KEY}&url={url}"

    response = requests.get(api_url)
    if response.status_code != 200:
        raise Exception(f"❌ Abstract API error: {response.status_code}")

    html = response.text
    with open("page.html", "w", encoding="utf-8") as f:
        f.write(html)
        print("💾 Збережено page.html для діагностики")

    soup = BeautifulSoup(html, "html.parser")

    # 🔍 Перевірка на повідомлення про відсутність місць
    if soup.find(string=lambda t: "всі місця зайняті" in t.lower()):
        status = "Місця зайняті"
    else:
        status = "Є вільні слоти або змінився інтерфейс"

    print("📋 Статус:", status)

    # 📬 Надсилання повідомлення у Telegram
    message = f"📢 Статус запису: {status}"
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    telegram_data = {"chat_id": CHAT_ID, "text": message}
    telegram_response = requests.post(telegram_url, data=telegram_data)

    if telegram_response.status_code == 200:
        print("📨 Повідомлення успішно надіслано у Telegram")
    else:
        print("⚠️ Помилка надсилання у Telegram:", telegram_response.text)

except Exception as e:
    print("❌ Помилка виконання:", repr(e))
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": f"❗️ Помилка в скрипті: {repr(e)}"}
        )
    except:
        print("⚠️ Не вдалося надіслати повідомлення про помилку у Telegram")
