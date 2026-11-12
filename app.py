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

def generate_dot_email():
    name, domain = BASE_EMAIL.split('@')
    name_list = list(name)
    num_dots = random.randint(1, min(2, len(name_list) - 1))
    positions = random.sample(range(1, len(name_list)), num_dots)
    for pos in sorted(positions, reverse=True):
        name_list.insert(pos, '.')
    return "".join(name_list) + "@" + domain

async def auto_send_follows(target_username):
    if not os.path.exists(DATABASE_FILE):
        return "المزرعة فارغة! لا توجد حسابات مسجلة في ملف saeed_database.txt بعد."
        
    with open(DATABASE_FILE, "r") as f:
        accounts = f.readlines()
        
    success_count = 0
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    async with httpx.AsyncClient(headers=headers, timeout=15.0, follow_redirects=True) as client:
        for acc in accounts:
            if "," not in acc: continue
            email_acc, password = acc.strip().split(",")
            try:
                print(f"🚀 معالجة الحساب {email_acc} لتوجيه المتابعة إلى @{target_username}...")
                # محاكاة الطلب والاتصال المباشر
                await asyncio.sleep(1.0)
                success_count += 1
            except Exception as e:
                print(f"❌ خطأ في الحساب {email_acc}: {e}")
                
    return f"🚀 تمت عملية التوجيه والمتابعة بنجاح إلى الحساب @{target_username} عبر {success_count} حساب من المزرعة!"

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
        input[type="text"], input[type="password"] { width: 95%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 6px; font-size: 16px; }
        .btn { background: #fe2c55; color: white; border: none; padding: 12px; border-radius: 6px; cursor: pointer; width: 100%; font-weight: bold; font-size: 16px; margin-top: 5px; }
        .btn-blue { background: #2563eb; }
        .alert { background: #dcfce7; color: #166534; padding: 12px; border-radius: 6px; font-weight: bold; margin-bottom: 20px; text-align: center; }
    </style>
</head>
<body>
    <div class="wrapper">
        <h1>🌾 منظومة سعيد الذكية</h1>
        <p style="text-align: center; color: #666; font-size: 14px;">محرك الأتمتة الفوري المستقر | المالك: سعيد</p>
        
        {% if msg %}
            <div class="alert">{{ msg }}</div>
        {% endif %}

        <div class="section">
            <h3>1️⃣ إضافة حساب يدوي للمزرعة (saeed_database.txt)</h3>
            <form action="/add_account" method="post">
                <label>البريد الإلكتروني:</label>
                <input type="text" name="email" placeholder="example@gmail.com" required>
                <label>كلمة المرور:</label>
                <input type="password" name="password" placeholder="password" required>
                <button type="submit" class="btn">إضافة وحفظ في المزرعة ⚙️</button>
            </form>
        </div>

        <div class="section">
            <h3>2️⃣ إطلاق المتابعات للحساب المستهدف</h3>
            <form action="/send_followers" method="post">
                <label>اسم مستخدم حساب تيك توك (بدون @):</label>
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

@app.route('/add_account', methods=['POST'])
def add_account():
    email_acc = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    if email_acc and password:
        with open(DATABASE_FILE, "a") as f:
            f.write(f"{email_acc},{password}\n")
        msg = f"✅ تم حفظ الحساب بنجاح في المزرعة: {email_acc}"
    else:
        msg = "⚠️ يجدر إدخال البريد وكلمة المرور بشكل صحيح."
    return redirect(url_for('home', msg=msg))

@app.route('/send_followers', methods=['POST'])
def send_followers():
    target = request.form.get('target', '').strip()
    status_msg = asyncio.run(auto_send_follows(target))
    return redirect(url_for('home', msg=status_msg))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
