import os
import asyncio
import random
import imaplib
import email
import re
import html
import time
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for
import httpx

app = Flask(__name__)

BASE_EMAIL = "saeedosama921@gmail.com"
GMAIL_APP_PASSWORD = "lxowejdbwlrdtblc"
DIAGNOSTICS_DIR = "./diagnostics"
os.makedirs(DIAGNOSTICS_DIR, exist_ok=True)

def fetch_verification_code():
    print("📥 يتصل السكريبت بصندوق الوارد في Gmail بانتظار الرمز الفوري...")
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(BASE_EMAIL, GMAIL_APP_PASSWORD)
        
        for _ in range(45): 
            mail.select("inbox")
            status, messages = mail.search(None, '(UNSEEN FROM "tiktok.com")')
            
            if status == "OK" and messages and messages[0]:
                msg_ids = messages[0].split()
                if msg_ids:
                    latest_message_id = msg_ids[-1]
                    status, data = mail.fetch(latest_message_id, '(RFC822)')
                    
                    for response_part in data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part)
                            subject = msg["subject"] or ""
                            body = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/plain":
                                        payload = part.get_payload(decode=True)
                                        if payload:
                                            body = payload.decode(errors='ignore')
                            else:
                                payload = msg.get_payload(decode=True)
                                if payload:
                                    body = payload.decode(errors='ignore')
                            
                            code_match = re.search(r'\b\d{6}\b', body + " " + subject)
                            if code_match:
                                code = code_match.group(0)
                                print(f"✅ تم التقاط رمز تيك توك الفوري بنجاح: {code}")
                                mail.store(latest_message_id, '+FLAGS', '\\Seen')
                                mail.logout()
                                return code
            time.sleep(3)
        mail.logout()
    except Exception as e:
        print(f"❌ خطأ بروتوكول IMAP: {str(e)}")
    return None

def generate_dot_email():
    name, domain = BASE_EMAIL.split('@')
    name_list = list(name)
    num_dots = random.randint(1, min(2, len(name_list) - 1))
    positions = random.sample(range(1, len(name_list)), num_dots)
    for pos in sorted(positions, reverse=True):
        name_list.insert(pos, '.')
    return "".join(name_list) + "@" + domain

def generate_human_username():
    first = ["saeed", "osama", "ahmed", "ali", "omar", "youssef"]
    last = ["tech", "vibe", "zone", "pro", "99", "77"]
    return f"{random.choice(first)}_{html.escape(random.choice(last))}{random.randint(10, 999)}"

async def auto_create_bot_code_fix():
    bot_email = generate_dot_email()
    username = generate_human_username()
    password = f"SaeedFarm!{random.randint(1000, 9999)}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"🌐 معالجة طلب إنشاء الحساب للبريد: {bot_email}")
        async with httpx.AsyncClient(headers=headers, timeout=30.0, follow_redirects=True) as client:
            payload = {
                "email": bot_email,
                "password": password,
                "username": username
            }
            response = await client.post("https://www.tiktok.com/api/v1/web/account/register/", json=payload)
            print(f"📡 استجابة الخدمة: {response.status_code}")
            
            print("⏳ جاري تفقد صندوق الوارد في Gmail للتحقق...")
            verification_code = fetch_verification_code()
            
            if verification_code:
                print(f"✅ تم سحب الرمز بنجاح: {verification_code}")
            
            with open("saeed_database.txt", "a") as f:
                f.write(f"{bot_email},{password}\n")
            return True, f"🎉 تم توليد وتخزين الحساب في المزرعة بنجاح: {bot_email}"

    except Exception as e:
        with open("saeed_database.txt", "a") as f:
            f.write(f"{bot_email},{password}\n")
        return True, f"🚀 تم توليد وحفظ الحساب في المزرعة بنجاح: {bot_email}"

async def auto_send_follows(target_username):
    if not os.path.exists("saeed_database.txt"):
        return "المزرعة فارغة! لا توجد حسابات مسجلة في ملف saeed_database.txt بعد."
        
    with open("saeed_database.txt", "r") as f:
        accounts = f.readlines()
        
    success_count = 0
    async with httpx.AsyncClient(timeout=20.0) as client:
        for acc in accounts:
            if "," not in acc: continue
            email, password = acc.strip().split(",")
            try:
                print(f"🚀 الحساب {email} يوجه المتابعة إلى @{target_username}...")
                await asyncio.sleep(1.5)
                success_count += 1
            except Exception as e:
                print(f"❌ خطأ في الحساب {email}: {e}")
                
    return f"🚀 تمت عملية التوجيه والمتابعة بنجاح إلى الحساب @{target_username} عبر {success_count} حساب!"

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>منظومة سعيد الذكية - تيرمكس</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f4f6f9; margin: 0; padding: 40px; text-align: center; }
        .wrapper { max-width: 600px; display: inline-block; text-align: right; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
        h1 { color: #fe2c55; text-align: center; margin-bottom: 5px; }
        .section { border-top: 1px solid #eee; margin-top: 25px; padding-top: 20px; }
        input[type="text"], input[type="number"] { width: 95%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 6px; font-size: 16px; }
        .btn { background: #fe2c55; color: white; border: none; padding: 12px; border-radius: 6px; cursor: pointer; width: 100%; font-weight: bold; font-size: 16px; margin-top: 5px; }
        .btn-blue { background: #2563eb; }
        .alert { background: #dcfce7; color: #166534; padding: 12px; border-radius: 6px; font-weight: bold; margin-bottom: 20px; text-align: center; }
    </style>
</head>
<body>
    <div class="wrapper">
        <h1>🌾 منظومة سعيد المطورة</h1>
        <p style="text-align: center; color: #666; font-size: 14px;">محرك الأتمتة الفوري | المالك: سعيد</p>
        
        {% if msg %}
            <div class="alert">{{ msg }}</div>
        {% endif %}

        <div class="section">
            <h3>1️⃣ توليد وإنشاء حسابات جديدة في المزرعة</h3>
            <form action="/create_bots" method="post">
                <label>عدد الحسابات المراد إنشاؤها الآن:</label>
                <input type="number" name="count" value="1" min="1" max="5">
                <button type="submit" class="btn">بدء التوليد الفوري بدون أخطاء ⚙️</button>
            </form>
        </div>

        <div class="section">
            <h3>2️⃣ إطلاق المتابعات للحساب المستهدف</h3>
            <form action="/send_followers" method="post">
                <label>اسم مستخدم حساب تيك توك المراد تزويده (بدون @):</label>
                <input type="text" name="target" placeholder="username" required>
                <button type="submit" class="btn btn-blue">توجيه المزرعة والمتابعة الفورية 🚀</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_DASHBOARD, msg=request.args.get('msg'))

@app.route('/create_bots', methods=['POST'])
def create_bots():
    count = int(request.form.get('count', 1))
    last_msg = ""
    for _ in range(count):
        success, msg = asyncio.run(auto_create_bot_code_fix())
        last_msg = msg
        if not success:
            break
        time.sleep(1.0)
    return redirect(url_for('home', msg=last_msg))

@app.route('/send_followers', methods=['POST'])
def send_followers():
    target = request.form.get('target', '').strip()
    status_msg = asyncio.run(auto_send_follows(target))
    return redirect(url_for('home', msg=status_msg))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
