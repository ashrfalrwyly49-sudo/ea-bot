import os
import time
import json
import urllib.request
import urllib.error

BOT_TOKEN = "8770824530:AAFqrPDiqQfKjYMgF9KWZ9H8sc9G8Rc8BAQ"

def send_message(chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = f"chat_id={chat_id}&text={text}&parse_mode=Markdown"
        req = urllib.request.Request(url, data=data.encode('utf-8'), method='POST')
        urllib.request.urlopen(req, timeout=10)
        return True
    except:
        return False

def get_updates(offset=None):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        if offset:
            url += f"?offset={offset}"
        req = urllib.request.Request(url, method='GET')
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return data.get('result', [])
    except:
        return []

print("🤖 البوت يعمل...")
last_id = 0

while True:
    try:
        updates = get_updates(last_id + 1)
        for u in updates:
            if u['update_id'] > last_id:
                last_id = u['update_id']
            msg = u.get('message', {})
            chat_id = msg.get('chat', {}).get('id')
            text = msg.get('text', '')
            if chat_id and text:
                print(f"📩 {text}")
                send_message(chat_id, f"✅ استلمت: {text}")
        time.sleep(2)
    except Exception as e:
        print(f"❌ {e}")
        time.sleep(5)
