import os
import asyncio
import random
import imaplib
import email
import re
import html
from flask import Flask, render_template_string, request, redirect, url_for
from playwright.async_api import async_playwright

app = Flask(__name__)

# --- إعدادات سعيد المؤتمتة بالكامل ---
BASE_EMAIL = "saeedosama921@gmail.com"
GMAIL_APP_PASSWORD = "lxowejdbwlrdtblc" # تم دمج رمز الأمان الخاص بك بنجاح

# دالة قراءة وسحب الرمز تلقائياً من Gmail في الخلفية
def fetch_verification_code():
    print("📥 يتصل السكريبت بصندوق الوارد في Gmail بانتظار الرمز تلقائياً...")
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(BASE_EMAIL, GMAIL_APP_PASSWORD)
        
        for _ in range(25): # الفحص الدوري لمدة دقيقتين تقريباً
            mail.select("inbox")
            status, messages = mail.search(None, '(UNSEEN FROM "tiktok.com")')
            
            if status == "OK" and messages:
                latest_message_id = messages[0].split()[-1]
                status, data = mail.fetch(latest_message_id, '(RFC822)')
                
                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = msg["subject"]
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode(errors='ignore')
                        else:
                            body = msg.get_payload(decode=True).decode(errors='ignore')
                        
                        code_match = re.search(r'\b\d{6}\b', body or subject)
                        if code_match:
                            code = code_match.group(0)
                            print(f"✅ تم التقاط رمز تيك توك بنجاح: {code}")
                            mail.store(latest_message_id, '+FLAGS', '\\Seen')
                            mail.logout()
                            return code
            time.sleep(5)
        mail.logout()
    except Exception as e:
        print(f"❌ خطأ بروتوكول IMAP: {str(e)}")
    return None

# دالة توليد تنوعات الإيميل بنقاط عشوائية لتيك توك
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

# محرك الإنشاء الأوتوماتيكي للحسابات مع تكتيكات الحذر والتمويه
async def auto_create_bot():
    bot_email = generate_dot_email()
    username = generate_human_username()
    password = f"SaeedFarm!{random.randint(1000, 9999)}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, 
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-infobars"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            await page.goto("https://www.tiktok.com/signup", wait_until="networkidle")
            await asyncio.sleep(random.uniform(2, 4))
            
            # إدخال عشوائي ببطء يحاكي حركة البشر
            await page.select_option('div[data-e2e="month-select"] select', index=random.randint(1, 12))
            await asyncio.sleep(random.uniform(0.5, 1.2))
            await page.select_option('div[data-e2e="day-select"] select', index=random.randint(1, 28))
            await asyncio.sleep(random.uniform(0.5, 1.2))
            await page.select_option('div[data-e2e="year-select"] select', value=str(random.randint(1995, 2003)))
            
            await page.type('input[type="email"]', bot_email, delay=random.randint(70, 150))
            await page.type('input[type="password"]', password, delay=random.randint(70, 150))
            await asyncio.sleep(random.uniform(1.5, 3.0))
            
            send_code_btn = await page.query_selector('button:has-text("Send code"), button:has-text("إرسال الرمز")')
            if send_code_btn:
                await send_code_btn.click()
                await asyncio.sleep(6)
                
                verification_code = fetch_verification_code()
                if verification_code:
                    code_input = await page.query_selector('input[placeholder*="digit"], input[placeholder*="رمز"]')
                    if code_input:
                        await code_input.type(verification_code, delay=120)
                        await asyncio.sleep(random.uniform(2.0, 4.0))
                        
                        submit_btn = await page.query_selector('button[type="submit"]')
                        if submit_btn:
                            await submit_btn.click()
                            await asyncio.sleep(5)
                    
                    with open("saeed_database.txt", "a") as f:
                        f.write(f"{bot_email},{password}\n")
                    print(f"🎉 تم حفظ الحساب الجديد بنجاح في المزرعة: {bot_email}")
        except Exception as e:
            print(f"⚠️ فشل التسجيل التلقائي: {e}")
        finally:
            await browser.close()

# محرك توجيه المتابعات الفورية لحساب العميل بأسلوب إنساني
async def auto_send_follows(target_username):
    if not os.path.exists("saeed_database.txt"):
        return "المزرعة فارغة! لا توجد حسابات مسجلة في ملف saeed_database.txt بعد."
        
    with open("saeed_database.txt", "r") as f:
        accounts = f.readlines()
        
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        for acc in accounts:
            if "," not in acc: continue
            email, password = acc.strip().split(",")
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            try:
                await page.goto("https://www.tiktok.com/login")
                await asyncio.sleep(3)
                await page.type('input[type="text"]', email, delay=100)
                await page.type('input[type="password"]', password, delay=100)
                await page.click('button[type="submit"]')
                await asyncio.sleep(random.uniform(5.0, 7.0))
                
                await page.goto(f"https://www.tiktok.com/@{target_username}")
                await asyncio.sleep(random.uniform(3.0, 5.0))
                
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 4);")
                await asyncio.sleep(random.uniform(1.0, 2.0))
                
                follow_button = await page.query_selector('button[data-e2e="follow-button"]')
                if follow_button:
                    await follow_button.click()
                    print(f"✅ الحساب {email} تابع الآن @{target_username}")
                    await asyncio.sleep(random.uniform(2.0, 4.0))
            except Exception as e:
                print(f"❌ خطأ مع الحساب {email}: {e}")
            finally:
                await context.close()
                await asyncio.sleep(random.uniform(8.0, 15.0))
        await browser.close()
    return f"🚀 تم إطلاق الحسابات وتوجيه المتابعات بنجاح إلى @{target_username}"

# واجهة لوحة تحكم الويب الرسومية المباشرة لسعيد
HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>منظومة سعيد لمزرعة تيك توك</title>
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
        <h1>🌾 لوحة تحكم الخدمة الشاملة</h1>
        <p style="text-align: center; color: #666; font-size: 14px;">نظام إدارة الحسابات المؤتمت المحمي | المالك: سعيد</p>
        
        {% if msg %}
            <div class="alert">{{ msg }}</div>
        {% endif %}

        <div class="section">
            <h3>1️⃣ توليد وإنشاء حسابات جديدة في المزرعة</h3>
            <form action="/create_bots" method="post">
                <label>عدد الحسابات المراد إنشاؤها الآن تلقائياً وبحذر:</label>
                <input type="number" name="count" value="1" min="1" max="10">
                <button type="submit" class="btn">بدء التوليد الآلي الآمن ⚙️</button>
            </form>
        </div>

        <div class="section">
            <h3>2️⃣ إطلاق المتابعات للحساب المستهدف (زيادة المتابعين)</h3>
            <form action="/send_followers" method="post">
                <label>اسم مستخدم حساب تيك توك المراد تزويده (بدون @):</label>
                <input type="text" name="target" placeholder="username" required>
                <button type="submit" class="btn btn-blue">توجيه المزرعة والمتابعة الفورية تلقائياً 🚀</button>
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
    for _ in range(count):
        asyncio.run(auto_create_bot())
        import time
        time.sleep(random.uniform(5.0, 10.0))
    return redirect(url_for('home', msg=f"🎉 تم الانتهاء من محاولة توليد {count} حساب وإضافتهم للمزرعة تلقائياً وبأمان!"))

@app.route('/send_followers', methods=['POST'])
def send_followers():
    target = request.form.get('target').strip()
    status_msg = asyncio.run(auto_send_follows(target))
    return redirect(url_for('home', msg=status_msg))

if __name__ == "__main__":
    import time
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
