import os
import asyncio
import random
import imaplib
import email
import re
import html
import time
from flask import Flask, render_template_string, request, redirect, url_for
from playwright.async_api import async_playwright

app = Flask(__name__)

# --- إعدادات سعيد المؤتمتة بالكامل ---
BASE_EMAIL = "saeedosama921@gmail.com"
GMAIL_APP_PASSWORD = "lxowejdbwlrdtblc"

def fetch_verification_code():
    print("📥 يتصل السكريبت بصندوق الوارد في Gmail بانتظار الرمز تلقائياً...")
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(BASE_EMAIL, GMAIL_APP_PASSWORD)
        
        for _ in range(35): 
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
                                print(f"✅ تم التقاط رمز تيك توك بنجاح: {code}")
                                mail.store(latest_message_id, '+FLAGS', '\\Seen')
                                mail.logout()
                                return code
            time.sleep(5)
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

async def auto_create_bot():
    bot_email = generate_dot_email()
    username = generate_human_username()
    password = f"SaeedFarm!{random.randint(1000, 9999)}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, 
            args=[
                "--disable-blink-features=AutomationControlled", 
                "--no-sandbox", 
                "--disable-infobars",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-setuid-sandbox",
                "--no-first-run",
                "--no-service-autorun",
                "--password-store=basic",
                "--window-size=1366,768"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
            locale="en-US",
            timezone_id="Asia/Riyadh",
            permissions=["geolocation"]
        )
        
        # حقن مكثف لتخطي كشف الأتمتة
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => false});
            window.navigator.chrome = {runtime: {}};
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        """)
        
        page = await context.new_page()
        
        try:
            print("🌐 الدخول المتدرج لتجاوز الفحص الأمني...")
            await page.goto("https://www.tiktok.com/login", wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(random.uniform(3, 5))
            
            # محاكاة سلوك بشري حقيقي (تحريك عشوائي للفأرة)
            await page.mouse.move(200, 300)
            await page.mouse.down()
            await page.mouse.up()
            await asyncio.sleep(2)

            print("🌐 الانتقال المباشر لصفحة التسجيل الآمنة...")
            await page.goto("https://www.tiktok.com/signup", wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(random.uniform(5, 7))
            
            # الانتظار حتى تظهر حقول الإدخال مع مهلة مرنة
            print("⌨️ البحث عن حقول الإدخال...")
            
            email_selectors = [
                'input[type="email"]', 
                'input[name="email"]', 
                'input[placeholder*="email" i]', 
                'input[placeholder*="البريد" i]',
                'input[autocomplete="username"]'
            ]
            
            email_field = None
            for sel in email_selectors:
                try:
                    email_field = await page.wait_for_selector(sel, timeout=10000)
                    if email_field:
                        print(f"✅ تم العثور على حقل البريد بنجاح عبر المحدد: {sel}")
                        break
                except:
                    continue
            
            if not email_field:
                return False, "⚠️ تم حظر الطلب مؤقتًا من قِبل نظام حماية تيك توك (Cloudflare Challenge)."

            # الكتابة بسرعة بشرية متقطعة
            await email_field.click()
            for char in bot_email:
                await email_field.type(char, delay=random.randint(80, 180))
            await asyncio.sleep(1)

            # إدخال كلمة المرور
            pass_selectors = ['input[type="password"]', 'input[name="password"]', 'input[placeholder*="password" i]']
            pass_field = None
            for sel in pass_selectors:
                try:
                    pass_field = await page.wait_for_selector(sel, timeout=5000)
                    if pass_field:
                        break
                except:
                    continue

            if pass_field:
                await pass_field.click()
                for char in password:
                    await pass_field.type(char, delay=random.randint(80, 180))
                await asyncio.sleep(1.5)

            # النقر على زر إرسال الرمز
            send_btn_selectors = [
                'button:has-text("Send code")', 
                'button:has-text("إرسال الرمز")', 
                'button[type="submit"]', 
                '[data-e2e="send-code-button"]',
                'button:has-text("Send")'
            ]
            clicked_send = False
            for sel in send_btn_selectors:
                try:
                    btn = await page.query_selector(sel)
                    if btn:
                        await btn.click()
                        clicked_send = True
                        print("📨 تم النقر على زر إرسال الرمز بنجاح تام!")
                        break
                except:
                    continue

            if not clicked_send:
                return False, "⚠️ لم يتم العثور على زر إرسال رمز التحقق في الصفحة."

            print("⏳ الانتظار حتى يصل الرمز إلى Gmail...")
            await asyncio.sleep(8)
            
            # سحب الرمز البرمجي من Gmail تلقائياً
            verification_code = fetch_verification_code()
            if verification_code:
                code_selectors = ['input[placeholder*="digit" i]', 'input[placeholder*="رمز" i]', 'input[name="code"]', 'input[maxlength="6"]']
                code_field = None
                for sel in code_selectors:
                    try:
                        code_field = await page.wait_for_selector(sel, timeout=5000)
                        if code_field:
                            break
                    except:
                        continue
                
                if code_field:
                    await code_field.click()
                    await code_field.type(verification_code, delay=120)
                    await asyncio.sleep(2)
                    
                    submit_selectors = ['button[type="submit"]', 'button:has-text("Next")', 'button:has-text("التالي")']
                    for sel in submit_selectors:
                        try:
                            sub_btn = await page.query_selector(sel)
                            if sub_btn:
                                await sub_btn.click()
                                await asyncio.sleep(4)
                                break
                        except:
                            continue

                with open("saeed_database.txt", "a") as f:
                    f.write(f"{bot_email},{password}\n")
                return True, f"🎉 تم إنشاء الحساب وحفظه في المزرعة بنجاح: {bot_email}"
            else:
                return False, "⚠️ لم يتم استقبال رمز التفعيل من تيك توك في البريد الإلكتروني (تأكد من عدم ظهور كابتشا يدوية)."

        except Exception as e:
            return False, f"⚠️ حدث خطأ أثناء التشغيل: {str(e)}"
        finally:
            await browser.close()

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
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            try:
                await page.goto("https://www.tiktok.com/login", wait_until="domcontentloaded")
                await asyncio.sleep(3)
                await page.type('input[type="text"], input[name="username"]', email, delay=100)
                await page.type('input[type="password"]', password, delay=100)
                await page.click('button[type="submit"]')
                await asyncio.sleep(6)
                
                await page.goto(f"https://www.tiktok.com/@{target_username}", wait_until="domcontentloaded")
                await asyncio.sleep(4)
                
                follow_btn = await page.query_selector('button[data-e2e="follow-button"], button:has-text("Follow"), button:has-text("متابعة")')
                if follow_btn:
                    await follow_btn.click()
                    print(f"✅ الحساب {email} تابع بنجاح @{target_username}")
                    await asyncio.sleep(3)
            except Exception as e:
                print(f"❌ خطأ في الحساب {email}: {e}")
            finally:
                await context.close()
                await asyncio.sleep(random.uniform(5.0, 10.0))
        await browser.close()
    return f"🚀 تم تنفيذ المتابعات بنجاح إلى الحساب @{target_username}"

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>منظومة سعيد الذكية - النسخة الخارقة</title>
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
        <h1>🌾 منظومة سعيد الخارقة</h1>
        <p style="text-align: center; color: #666; font-size: 14px;">نظام التمويب وتجاوز الفحص المتقدم | المالك: سعيد</p>
        
        {% if msg %}
            <div class="alert">{{ msg }}</div>
        {% endif %}

        <div class="section">
            <h3>1️⃣ توليد وإنشاء حسابات جديدة في المزرعة</h3>
            <form action="/create_bots" method="post">
                <label>عدد الحسابات المراد إنشاؤها الآن:</label>
                <input type="number" name="count" value="1" min="1" max="5">
                <button type="submit" class="btn">بدء التوليد الذكي الخارق ⚙️</button>
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
        success, msg = asyncio.run(auto_create_bot())
        last_msg = msg
        if not success:
            break
        time.sleep(random.uniform(5.0, 8.0))
    return redirect(url_for('home', msg=last_msg))

@app.route('/send_followers', methods=['POST'])
def send_followers():
    target = request.form.get('target').strip()
    status_msg = asyncio.run(auto_send_follows(target))
    return redirect(url_for('home', msg=status_msg))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
