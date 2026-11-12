import os
import random
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

BASE_EMAIL = "saeedosama921@gmail.com"
DATABASE_FILE = "saeed_database.txt"

# دالة توليد البريد المنقط الذكي
def generate_dot_email():
    name, domain = BASE_EMAIL.split('@')
    name_list = list(name)
    num_dots = random.randint(1, min(2, len(name_list) - 1))
    positions = random.sample(range(1, len(name_list)), num_dots)
    for pos in sorted(positions, reverse=True):
        name_list.insert(pos, '.')
    return "".join(name_list) + "@" + domain

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>منظومة إدارة مزرعة الحسابات - سعيد</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f4f6f9; margin: 0; padding: 30px; text-align: center; }
        .wrapper { max-width: 650px; display: inline-block; text-align: right; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); width: 100%; box-sizing: border-box; }
        h1 { color: #fe2c55; text-align: center; margin-bottom: 5px; }
        .section { border-top: 1px solid #eee; margin-top: 25px; padding-top: 20px; }
        input[type="text"], input[type="password"] { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 6px; font-size: 16px; box-sizing: border-box; }
        .btn { background: #fe2c55; color: white; border: none; padding: 12px; border-radius: 6px; cursor: pointer; width: 100%; font-weight: bold; font-size: 16px; margin-top: 5px; }
        .btn-blue { background: #2563eb; }
        .btn-copy { background: #10b981; margin-bottom: 10px; }
        .alert { background: #dcfce7; color: #166534; padding: 12px; border-radius: 6px; font-weight: bold; margin-bottom: 20px; text-align: center; }
        .box-email { background: #eff6ff; border: 1px dashed #3b82f6; padding: 12px; border-radius: 6px; text-align: center; font-size: 18px; font-weight: bold; color: #1e40af; margin: 10px 0; word-break: break-all; }
        .accounts-list { background: #f8fafc; border: 1px solid #e2e8f0; padding: 10px; border-radius: 6px; max-height: 150px; overflow-y: auto; font-family: monospace; font-size: 14px; text-align: left; direction: ltr; }
    </style>
    <script>
        function copyEmail() {
            var emailText = document.getElementById("generatedEmail").innerText;
            navigator.clipboard.writeText(emailText).then(function() {
                alert("✅ تم نسخ البريد المنقط إلى الحافظة بنجاح!");
            });
        }
    </script>
</head>
<body>
    <div class="wrapper">
        <h1>🌾 مزرعة حسابات سعيد</h1>
        <p style="text-align: center; color: #666; font-size: 14px;">النظام اليدوي الآمن للإدارة والتوجيه الحقيقي</p>
        
        {% if msg %}
            <div class="alert">{{ msg }}</div>
        {% endif %}

        <!-- الخطوة 1: مولد البريدات المنقطة -->
        <div class="section">
            <h3>1️⃣ توليد بريد منقط جديد للتسجيل اليدوي</h3>
            <p style="font-size: 14px; color: #555;">انسخ هذا البريد وسجل به يدوياً في تيك توك، وسيصلك الرمز فوراً على بريدك الأساسي:</p>
            <div class="box-email" id="generatedEmail">{{ current_dot_email }}</div>
            <button type="button" class="btn btn-copy" onclick="copyEmail()">📋 نسخ البريد المنقط</button>
        </div>

        <!-- الخطوة 2: حفظ الحساب المسجل -->
        <div class="section">
            <h3>2️⃣ حفظ الحساب في قاعدة البيانات (saeed_database.txt)</h3>
            <form action="/save_account" method="post">
                <label>البريد الإلكتروني الذي سجلت به:</label>
                <input type="text" name="email" value="{{ current_dot_email }}" required>
                <label>كلمة المرور للحساب:</label>
                <input type="password" name="password" placeholder="أدخل كلمة المرور" required>
                <button type="submit" class="btn">💾 حفظ الحساب في المزرعة</button>
            </form>
        </div>

        <!-- عرض الحسابات المخزنة حالياً -->
        <div class="section">
            <h3>📂 الحسابات الجاهزة حالياً في المزرعة ({{ accounts_count }})</h3>
            <div class="accounts-list">
                {% if accounts_list %}
                    {% for acc in accounts_list %}
                        {{ acc }}<br>
                    {% endfor %}
                {% else %}
                    المزرعة فارغة حالياً. أضف حسابات للبدء!
                {% endif %}
            </div>
        </div>

        <!-- الخطوة 3: التوجيه للمتابعة (المرحلة الثانية) -->
        <div class="section">
            <h3>3️⃣ إطلاق المتابعات للحساب المستهدف</h3>
            <form action="/send_followers" method="post">
                <label>اسم مستخدم حساب تيك توك (بدون @):</label>
                <input type="text" name="target" placeholder="username" required>
                <button type="submit" class="btn btn-blue">🚀 توجيه المزرعة والمتابعة الفورية</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    # توليد بريد منقط جديد لكل زفرة للصفحة
    dot_email = generate_dot_email()
    
    # قراءة الحسابات الحالية المخزنة
    accounts_list = []
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as f:
            accounts_list = [line.strip() for line in f.readlines() if line.strip()]
            
    return render_template_string(
        HTML_DASHBOARD, 
        current_dot_email=dot_email, 
        accounts_list=accounts_list, 
        accounts_count=len(accounts_list),
        msg=request.args.get('msg')
    )

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

@app.route('/send_followers', methods=['POST'])
def send_followers():
    target = request.form.get('target', '').strip()
    if not os.path.exists(DATABASE_FILE):
        return redirect(url_for('home', msg="⚠️ المزرعة فارغة! لا توجد حسابات مسجلة بعد."))
        
    with open(DATABASE_FILE, "r") as f:
        accounts = f.readlines()
        
    valid_accounts = [acc.strip() for acc in accounts if "," in acc]
    
    # هنا ستكون منطق المتابعة الحقيقية بالمرحلة الثانية
    return redirect(url_for('home', msg=f"🚀 جاهز لتنفيذ المتابعات إلى @{target} باستخدام {len(valid_accounts)} حساب مسجل!"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
