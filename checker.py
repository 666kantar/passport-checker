import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
import os
import pickle

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    print("❌ Не передано TELEGRAM_BOT_TOKEN або TELEGRAM_CHAT_ID")
    exit(1)

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
        wait = WebDriverWait(driver, 60)

        print("🚀 Відкриваємо сайт для встановлення cookies...")
        driver.get("https://pasport.org.ua")
        time.sleep(3)

        try:
            with open("cookies.pkl", "rb") as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    driver.add_cookie(cookie)
            print("🍪 Cookies завантажено")
        except Exception as e:
            print("⚠️ Не вдалося завантажити cookies:", repr(e))
            raise Exception("Cookies not found or invalid")

        print("🌐 Переходимо на сторінку черги")
        driver.get("https://pasport.org.ua/solutions/e-queue")
        time.sleep(5)

        # Збереження HTML для діагностики
        with open("page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
            print("💾 Збережено page.html для діагностики")

        # Перевірка на CAPTCHA
        if "cf-turnstile" in driver.page_source or "Cloudflare" in driver.page_source or "Attention Required!" in driver.title:
            raise Exception("Cloudflare still blocking — cookies may be expired")

        print("🌍 Вибираємо країну 'Канада'")
        country_select = wait.until(EC.presence_of_element_located((By.ID, "country")))
        Select(country_select).select_by_visible_text("Канада")
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

        message = f"📢 Статус запису: {status}"
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message}
        )

        if response.status_code == 200:
            print("📨 Повідомлення успішно надіслано у Telegram")
        else:
            print("⚠️ Помилка надсилання у Telegram:", response.text)

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": "✅ Скрипт завершився успішно (з cookies)"}
        )

except Exception as e:
    print("❌ Помилка виконання:", repr(e))
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": f"❗️ Помилка в скрипті: {repr(e)}"}
        )
    except:
        print("⚠️ Не вдалося надіслати повідомлення про помилку у Telegram")
