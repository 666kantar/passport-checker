import requests
from datetime import datetime
import os

# 🔐 Telegram
BOT_TOKEN = "8517457735:AAF-gOPxf8_Rwbj7jT0v6B2P7Y4EwjbvGwU"
CHAT_ID = "481185396"

# 🔐 Авторизація
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJPcmdhbmlzYXRpb25HdWlkIjoiM2VmOWRiNDUtZThkOC00MGUyLWJmNzAtMjFlOWY5MWI0Y2M5IiwibmJmIjoxNzY2MDIxOTAwLCJleHAiOjE3NjYwMjI1MDAsImlhdCI6MTc2NjAyMTkwMH0._z_X9al_Y1so3SRFJ2aA6cjOHin4LcoowKL0FusxocM"
ORGANISATION_ID = "3ef9db45-e8d8-40e2-bf70-21e9f91b4cc9"

# 🌐 API-запит
url = "https://qs.pasport.org.ua/api/v1/PreReg/GetDays"
params = {
    "LangId": 1,
    "ServiceCenterId": 46,  # Заміни на інший ID, якщо потрібно
    "ServiceId": 4          # ID послуги: 4 = "Закордонний паспорт або ID-картка"
}
headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "organisation": ORGANISATION_ID,
    "Accept": "application/json"
}

# 🕒 Мітка часу
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

try:
    print("🌐 Надсилаємо запит до API...")
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()

    # 📁 Створити папку для логів
    os.makedirs("logs", exist_ok=True)

    # 💾 Зберегти JSON
    json_filename = f"logs/api_response_{timestamp}.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        f.write(response.text)
        print(f"💾 Збережено JSON у файл: {json_filename}")

    # 🔍 Аналіз відповіді
    available_dates = [
        d["datePart"][:10]
        for d in data.get("days", [])
        if d.get("isAllowed") is True
    ]

    if available_dates:
        status = f"✅ Є вільні дати: {', '.join(available_dates)}"
    else:
        status = "❌ Всі місця зайняті (жодна дата не дозволена для запису)"

    print(f"🟢 Статус: {status}")

    # 📬 Надсилання у Telegram
    message = f"📋 Статус запису:\n{status}"
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    telegram_data = {"chat_id": CHAT_ID, "text": message}
    telegram_response = requests.post(telegram_url, data=telegram_data)

    if telegram_response.status_code == 200:
        print("📨 Повідомлення надіслано у Telegram")
    else:
        print("❌ Помилка надсилання:", telegram_response.text)

    # 🧾 Зберегти лог
    log_filename = f"logs/log_{timestamp}.txt"
    with open(log_filename, "w", encoding="utf-8") as log_file:
        log_file.write(f"Час: {timestamp}\n")
        log_file.write(f"Статус: {status}\n")
        log_file.write(f"JSON файл: {json_filename}\n")

except Exception as e:
    print("❌ Помилка:", repr(e))
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": f"❗️ Помилка в скрипті: {repr(e)}"}
        )
    except:
        print("⚠️ Не вдалося надіслати повідомлення про помилку")
