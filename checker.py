import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
import os

# 🔐 Отримання секретів з середовища
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Перевірка наявності секретів
if not BOT_TOKEN or not CHAT_ID:
    print("❌ Не передано TELEGRAM_BOT_TOKEN або TELEGRAM_CHAT_ID")
    exit(1)

# Налаштування Chrome для headless-режиму на GitHub Actions
options = uc.ChromeOptions()
options.headless = True
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-software-rasterizer")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920,1080")

try:
    with uc.Chrome(options=options) as driver:
        wait = WebDriverWait(driver, 40)

        print("🚀 Відкриваємо сайт...")
        driver.get("https://pasport.org.ua/solutions/e-queue")
        time.sleep(5)

        # 🔍 Перевірка на CAPTCHA або Cloudflare
        if "cf-turnstile" in driver.page_source or "Cloudflare" in driver.page_source or "Attention Required!" in driver.title:
            print("🛑 CAPTCHA або Cloudflare Challenge виявлено")
            raise Exception("Cloudflare block detected")

        print("🌍 Вибираємо країну 'Канада'")
        try:
            country_select = wait.until(EC.presence_of_element_located((By.ID, "country")))
            Select(country_select).select_by_visible_text("Канада")
        except:
            raise Exception("❌ Елемент #country не знайдено — можливо, CAPTCHA або зміни на сайті")
        time.sleep(2)

        print("🏢 Вибираємо центр")
        center_select = wait.until(EC.presence_of_element_located((By.ID, "center")))
        Select(center_select).select_by_index(1)
        time.sleep(2)

        print("➡️ Натискаємо 'Продовжити'")
        continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Продовжити')]")))
        continue_button.click()
        time.sleep(10)

        print("📝 Вибираємо послугу")
        service_select = wait.until(EC.presence_of_element_located((By.ID, "service")))
        Select(service_select).select_by_index(1)
        time.sleep(2)

        print("🔍 Перевіряємо статус...")
        try:
            driver.find_element(By.XPATH, "//*[contains(text(),'Вибачте, на даний момент всі місця зайняті')]")
            status = "Місця зайняті"
        except:
            status = "Є вільні слоти"

        print("📋 Статус:", status)

        # 📬 Надсилання повідомлення у Telegram
        message = f"📢 Статус запису: {status}"
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message}
        )

        if response.status_code == 200:
            print("📨 Повідомлення успішно надіслано у Telegram")
        else:
            print("⚠️ Помилка надсилання у Telegram:", response.text)

        # ✅ Повідомлення про успішне завершення
        test_message = "✅ Скрипт завершився успішно (навіть якщо слотів немає)"
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": test_message}
        )

except Exception as e:
    print("❌ Помилка виконання:", repr(e))
    # Надсилаємо повідомлення про помилку
    error_message = f"❗️ Помилка в скрипті: {repr(e)}"
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": error_message}
        )
    except:
        print("⚠️ Не вдалося надіслати повідомлення про помилку у Telegram")
