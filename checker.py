import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
import os

# 🔐 Дані Telegram-бота з GitHub Secrets
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Перевірка, чи токен і chat_id передані
if not BOT_TOKEN or not CHAT_ID:
    print("❌ Не передано TELEGRAM_BOT_TOKEN або TELEGRAM_CHAT_ID")
    exit(1)

# Налаштування Chrome для GitHub Actions
options = uc.ChromeOptions()
options.headless = True
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-software-rasterizer")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920,1080")

with uc.Chrome(options=options) as driver:
    wait = WebDriverWait(driver, 20)

    try:
        print("🚀 Відкриваємо сайт...")
        driver.get("https://pasport.org.ua/solutions/e-queue")

        print("🌍 Вибираємо країну 'Канада'")
        Select(wait.until(EC.presence_of_element_located((By.ID, "country")))).select_by_visible_text("Канада")
        time.sleep(2)

        print("🏢 Вибираємо центр")
        Select(wait.until(EC.presence_of_element_located((By.ID, "center")))).select_by_index(1)
        time.sleep(2)

        print("➡️ Натискаємо 'Продовжити'")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Продовжити')]"))).click()
        time.sleep(10)

        print("📝 Вибираємо послугу")
        Select(wait.until(EC.presence_of_element_located((By.ID, "service")))).select_by_index(1)
        time.sleep(2)

        print("🔍 Перевіряємо статус...")
        try:
            driver.find_element(By.XPATH, "//*[contains(text(),'Вибачте, на даний момент всі місця зайняті')]")
            status = "Місця зайняті"
        except:
            status = "Є вільні слоти"

        print("📋 Статус:", status)

        # Надсилання повідомлення у Telegram
        message = f"📢 Статус запису: {status}"
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message}
        )

        if response.status_code == 200:
            print("📨 Повідомлення успішно надіслано у Telegram")
        else:
            print("⚠️ Помилка надсилання у Telegram:", response.text)

    except Exception as e:
        print("❌ Помилка виконання:", repr(e))
