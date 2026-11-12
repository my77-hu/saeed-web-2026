import os
import time
import requests
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

DATABASE_FILE = "saeed_database.txt"

# دالة توليد بريد مؤقت حقيقي جديد عبر API مجاني (1secmail)
def generate_temp_email():
    try:
        response = requests.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1")
        if response.status_code == 200:
            emails = response.json()
            if emails:
                return emails[0]
    except Exception as e:
        print(f"⚠️ خطأ في توليد البريد المؤقت: {e}")
    # بريد احتياطي في حال انقطع اتصال الـ API المؤقت
    return "saeed.bot.2026@esiix.com"

# دالة فحص وسحب الرمز من صندوق البريد المؤقت
def fetch_temp_mail_code(email_address):
    try:
        login, domain = email_address.split('@')
        url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
        
        print(جاري مراقبة صندوق الوارد للبريد المؤقت: {email_address}...)
        for _ in range(20): # محاولات الاستماع لمدة دقيقة تقريباً
            response = requests.get(url)
            if response.status_code == 200:
                messages = response.json()
                if messages:
                    # جلب تفاصيل الرسالة الأحدث
                    msg_id = messages[0]['id']
                    msg_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={msg_id}"
                    msg_res = requests.get(msg_url)
                    if msg_res.status_code == 200:
                        msg_data = msg_res.json()
                        body = msg_data.get('body', '')
                        subject = msg_data.get('subject', '')
                        
                        # البحث عن رمز مكون من 6 أرقام
                        import re
                        code_match = re.search(r'\b\d{6}\b', body + " " + subject)
                        if code_match:
                            return code_match.group(0)
            time.sleep(3)
    except Exception as e:
        print(f"❌ خطأ في فحص البريد المؤقت: {e}")
    return None

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>مزرعة سعيد - البريد المؤقت الحقيقي</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f4f6f9; margin: 0; padding: 30px; text-align: center; }
        .wrapper { max-width: 650px; display: inline-block; text-align: right; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); width: 100%; box-sizing: border-box; }
        h1 { color: #fe2c55; text-align: center; margin-bottom: 5px; }
        .section { border-top: 1px solid #eee; margin-top: 25px; padding-top: 20px; }
        input[type="text"], input[type="password"] { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 6px; font-size: 16px; box-sizing: border-box; }
        .btn { background: #fe2c55; color: white; border: none; padding: 12px; border-radius: 6px; cursor: pointer; width: 100%; font-weight: bold; font-size: 16px; margin-top: 5px; }
        .btn-blue { background: #2563eb; }
        .btn-copy { background: #10b981; margin-bottom: 10px; }
        .btn-refresh { background: #f59e0b; margin-bottom: 10px; }
        .alert { background: #dcfce7; color: #166534; padding: 12px; border-radius: 6px; font-weight: bold; margin-bottom: 20px; text-align: center; }
        .box-email { background: #eff6ff; border: 1px dashed #3b82f6; padding: 12px; border-radius: 6px; text-align: center; font-size: 18px; font-weight: bold; color: #1e40af; margin: 10px 0; word-break: break-all; }
        .accounts-list { background: #f8fafc; border: 1px solid #e2e8f0; padding: 10px; border-radius: 6px; max-height: 150px; overflow-y: auto; font-family: monospace; font-size: 14px; text-align: left; direction: ltr; }
    </style>
    <script>
        function copyEmail() {
            var emailText = document.getElementById("tempEmail").innerText;
            navigator.clipboard.writeText(emailText).then(function() {
                alert("✅ تم نسخ البريد المؤقت بنجاح!");
            });
        }
    </script>
</head>
<body>
    <div class="wrapper">
        <h1>🌾 مزرعة حسابات سعيد</h1>
        <p style="text-align: center; color: #666; font-size: 14px;">نظام توليد البريد المؤقت الذكي والآمن</p>
        
        {% if msg %}
            <div class="alert">{{ msg }}</div>
        {% endif %}

        <!-- الخطوة 1: البريد المؤقت الحالي -->
        <div class="section">
            <h3>1️⃣ البريد المؤقت المخصص لتسجيل حساب جديد</h3>
            <p style="font-size: 14px; color: #555;">انسخ هذا البريد وسجل به يدوياً في تيك توك:</p>
            <div class="box-email" id="tempEmail">{{ temp_email }}</div>
            <button type="button" class="btn btn-copy" onclick="copyEmail()">📋 نسخ البريد المؤقت</button>
            <form action="/" method="get">
                <button type="submit" class="btn btn-refresh">🔄 توليد بريد مؤقت جديد آخر</button>
            </form>
        </div>

        <!-- الخطوة 2: فحص الرمز أو حفظ الحساب -->
        <div class="section">
            <h3>2️⃣ فحص وصول الرمز الحقيقي للبريد المؤقت</h3>
            <form action="/check_code" method="post">
                <input type="hidden" name="email" value="{{ temp_email }}">
                <button type="submit" class="btn btn-blue">🔍 جلب رمز التحقق من تيك توك الآن</button>
            </form>
        </div>

        <div class="section">
            <h3>3️⃣ حفظ الحساب في المزرعة (saeed_database.txt)</h3>
            <form action="/save_account" method="post">
                <label>البريد المؤقت الذي سجلت به:</label>
                <input type="text" name="email" value="{{ temp_email }}" required>
                <label>كلمة المرور للحساب:</label>
                <input type="password" name="password" placeholder="أدخل كلمة المرور" required>
                <button type="submit" class="btn">💾 حفظ الحساب في المزرعة</button>
            </form>
        </div>

        <!-- الحسابات المخزنة -->
        <div class="section">
            <h3>📂 الحسابات الجاهزة في المزرعة ({{ accounts_count }})</h3>
            <div class="accounts-list">
                {% if accounts_list %}
                    {% for acc in accounts_list %}
                        {{ acc }}<br>
                    {% endfor %}
                {% else %}
                    المزرعة فارغة حالياً.
                {% endif %}
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    temp_email = generate_temp_email()
    accounts_list = []
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as f:
            accounts_list = [line.strip() for line in f.readlines() if line.strip()]
            
    return render_template_string(
        HTML_DASHBOARD, 
        temp_email=temp_email, 
        accounts_list=accounts_list, 
        accounts_count=len(accounts_list),
        msg=request.args.get('msg')
    )

@app.route('/check_code', methods=['POST'])
def check_code():
    email_acc = request.form.get('email', '').strip()
    code = fetch_temp_mail_code(email_acc)
    if code:
        msg = f"🎉 تم العثور على رمز التحقق بنجاح للبريد {email_acc}: [ {code} ]"
    else:
        msg = f"⚠️ لم يتم العثور على رسالة تحقق جديدة بعد للبريد {email_acc}. تأكد من إرسال الرمز من تيك توك وحاول مرة أخرى."
    return redirect(url_for('home', msg=msg))

@app.route('/save_account', methods=['POST'])
def save_account():
    email_acc = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    
    if email_acc and password:
        with open(DATABASE_FILE, "a") as f:
            f.write(f"{email_acc},{password}\n")
        msg = f"✅ تم حفظ الحساب بنجاح في المزرعة: {email_acc}"
    else:
        msg = "⚠️ يرجى التأكد من إدخال البريد وكلمة المرور."
        
    return redirect(url_for('home', msg=msg))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
