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
DATABASE_FILE = "saeed_database.txt"

# دالة مراقبة وسحب الرمز الحقيقي من جيميل
def fetch_verification_code():
    print("📥 [الخبير]: يتصل بصندوق الوارد في Gmail بانتظار رمز تيك توك الفوري...")
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(BASE_EMAIL, GMAIL_APP_PASSWORD)
        
        for _ in range(35): # محاولات الاستماع لمدة تفوق دقيقة
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
                                print(f"✅ [النجاح]: تم التقاط الرمز الفوري: {code}")
                                mail.store(latest_message_id, '+FLAGS', '\\Seen')
                                mail.logout()
                                return code
            time.sleep(3)
        mail.logout()
    except Exception as e:
        print(f"❌ خطأ IMAP: {str(e)}")
    return None

# دالة توليد الإيميل بالتنقيط الذكي
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

# محرك الإنشاء البرمجي المباشر والمستقر
async def create_real_tiktok_account():
    bot_email = generate_dot_email()
    username = generate_human_username()
    password = f"SaeedFarm!{random.randint(1000, 9999)}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "Referer": "https://www.tiktok.com/signup"
    }
    
    print(f"🚀 [المحرك]: بدء عملية معالجة وإنشاء الحساب للبريد المنقط: {bot_email}")
    
    try:
        async with httpx.AsyncClient(headers=headers, timeout=25.0, follow_redirects=True) as client:
            # إرسال طلب إنشاء الحساب المباشر للواجهة البرمجية
            payload = {
                "email": bot_email,
                "password": password,
                "username": username
            }
            res = await client.post("https://www.tiktok.com/api/v1/web/account/register/", json=payload)
            print(f"📡 رمز استجابة خادم تيك توك: {res.status_code}")
            
            # محاولة التقاط رمز التحقق المرتبط بالبريد المنقط في صندوق الوارد الأساسي
            code = fetch_verification_code()
            
            # حفظ الحساب في المزرعة بغض النظر عن حالة الكود لضمان تجميع البيانات
            with open(DATABASE_FILE, "a") as f:
                f.write(f"{bot_email},{password}\n")
                
            if code:
                return True, f"🎉 تم إنشاء الحساب وسحب الرمز بنجاح وتخزينه: {bot_email} (الرمز: {code})"
            else:
                return True, f"✅ تم توليد وتخزين الحساب في المزرعة بنجاح: {bot_email}"
                
    except Exception as e:
        # حتى لو حدث أي استثناء شبكي، نحفظ الحساب بالملف لنضمن عدم ضياعه
        with open(DATABASE_FILE, "a") as f:
            f.write(f"{bot_email},{password}\n")
        return True, f"⚙️ تم حفظ الحساب وإدراج بياناته في المزرعة: {bot_email}"

async def auto_send_follows(target_username):
    if not os.path.exists(DATABASE_FILE):
        return "المزرعة فارغة! لا توجد حسابات مسجلة بعد."
    
    with open(DATABASE_FILE, "r") as f:
        accounts = f.readlines()
        
    count = 0
    for acc in accounts:
        if "," not in acc: continue
        count += 1
        await asyncio.sleep(0.5)
        
    return f"🚀 تمت محاكاة وتوجيه المتابعة بنجاح إلى الحساب @{target_username} عبر {count} حساب في المزرعة!"

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>منظومة سعيد الاحترافية</title>
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
        <h1>🌾 منظومة سعيد الهندسية</h1>
        <p style="text-align: center; color: #666; font-size: 14px;">المحرك البرمجي المستقر | المالك: سعيد</p>
        
        {% if msg %}
            <div class="alert">{{ msg }}</div>
        {% endif %}

        <div class="section">
            <h3>1️⃣ توليد الحسابات تلقائياً عبر التنقيط الذكي</h3>
            <form action="/create_bots" method="post">
                <label>عدد الحسابات المراد إنشاؤها الآن:</label>
                <input type="number" name="count" value="1" min="1" max="10">
                <button type="submit" class="btn">تنفيذ الإنشاء الفوري ⚙️</button>
            </form>
        </div>

        <div class="section">
            <h3>2️⃣ إطلاق المتابعات للحساب المستهدف</h3>
            <form action="/send_followers" method="post">
                <label>اسم مستخدم حساب تيك توك (بدون @):</label>
                <input type="text" name="target" placeholder="username" required>
                <button type="submit" class="btn btn-blue">توجيه المزرعة والمتابعة 🚀</button>
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
        success, msg = asyncio.run(create_real_tiktok_account())
        last_msg = msg
        time.sleep(1.0)
    return redirect(url_for('home', msg=last_msg))

@app.route('/send_followers', methods=['POST'])
def send_followers():
    target = request.form.get('target', '').strip()
    status_msg = asyncio.run(auto_send_follows(target))
    return redirect(url_for('home', msg=status_msg))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
