import time
import requests
import os

BOT_TOKEN = "7616722917:AAGGGLKc2SeLtFIU7CQHSgYM_QdeWVFXMz8"
CHAT_ID = "@AirAlertUA1"
API_URL = "https://api.alerts.in.ua/v1/alerts/active.json?token=eb0cb8aba6ea05112ac65b45f12f99bebfdb5210ab2203"
CACHE_FILE = "alerts_cache.txt"

def load_cache():
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    aid, loc = line.split("|", 1)
                    cache[aid] = loc
    return cache

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        for aid, loc in cache.items():
            f.write(f"{aid}|{loc}\n")

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    response = requests.post(url, data=data)
    if not response.ok:
        print("❌ Ошибка Telegram:", response.text)

print("🚨 Бот запущен — отслеживаю новые и отменённые тривоги...")

alert_cache = load_cache()

while True:
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        alerts = response.json().get("alerts", [])

        current_alerts = {str(alert['id']): alert['location_title'] for alert in alerts}

        new_alerts = {aid: loc for aid, loc in current_alerts.items() if aid not in alert_cache}
        ended_alerts = {aid: loc for aid, loc in alert_cache.items() if aid not in current_alerts}

        for loc in new_alerts.values():
            if loc.strip():
                send_message(f"🚨 Повітряна тривога: {loc}")
                print("🔔 Новый сигнал:", loc)

        for loc in ended_alerts.values():
            if loc.strip():
                send_message(f"✅ Відбій тривоги: {loc}")
                print("✅ Тривога відбита:", loc)

        alert_cache = current_alerts
        save_cache(alert_cache)

    except Exception as e:
        print("❌ Помилка:", e)

    time.sleep(40)

