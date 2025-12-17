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

options = uc.ChromeOptions()
options.headless = True
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")

with uc.Chrome(options=options) as driver:
    wait = WebDriverWait(driver, 20)

    try:
        driver.get("https://pasport.org.ua/solutions/e-queue")
        Select(wait.until(EC.presence_of_element_located((By.ID, "country")))).select_by_visible_text("Канада")
        time.sleep(2)
        Select(wait.until(EC.presence_of_element_located((By.ID, "center")))).select_by_index(1)
        time.sleep(2)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Продовжити')]"))).click()
        time.sleep(10)
        Select(wait.until(EC.presence_of_element_located((By.ID, "service")))).select_by_index(1)
        time.sleep(2)

        try:
            driver.find_element(By.XPATH, "//*[contains(text(),'Вибачте, на даний момент всі місця зайняті')]")
            status = "Місця зайняті"
        except:
            status = "Є вільні слоти"

        message = f"📢 Статус запису: {status}"
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message}
        )

    except Exception as e:
        print("❌ Помилка:", e)
