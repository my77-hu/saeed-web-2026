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
from playwright.async_api import async_playwright

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

async def save_diagnostic(page, step_name):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    screenshot_path = os.path.join(DIAGNOSTICS_DIR, f"{step_name}-{timestamp}.png")
    html_path = os.path.join(DIAGNOSTICS_DIR, f"{step_name}-{timestamp}.html")
    try:
        await page.screenshot(path=screenshot_path, full_page=True)
        html_content = await page.content()
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"📸 [تشخيص] تم حفظ لقطة الشاشة: {screenshot_path}")
    except Exception as e:
        print(f"⚠️ فشل حفظ لقطة التشخيص: {e}")

# المحرك المحسن لمعالجة ضغط زر إرسال الرمز والتأكد من استجابته الفعليّة
async def auto_create_bot_code_fix():
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
                "--window-size=1920,1080"
            ]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US"
        )
        
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => false});
            window.navigator.chrome = {runtime: {}};
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        """)
        
        page = await context.new_page()
        
        try:
            print("🌐 الانتقال إلى صفحة التسجيل في تيك توك...")
            await page.goto("https://www.tiktok.com/signup", wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(4)
            await save_diagnostic(page, "1-initial-page")

            # 1. النقر على Use phone or email
            print("🖱️ النقر على 'Use phone or email'...")
            try:
                await page.click('text="Use phone or email"', timeout=5000)
                await asyncio.sleep(3)
            except:
                await page.click('[data-e2e="signup-phone-or-email"]', timeout=5000)
                await asyncio.sleep(3)
            await save_diagnostic(page, "2-after-phone-email-click")

            # 2. النقر على Sign up with email للتبديل للبريد
            print("🖱️ التبديل إلى 'Sign up with email'...")
            try:
                await page.click('text="Sign up with email"', timeout=5000)
                await asyncio.sleep(2)
            except:
                pass
            await save_diagnostic(page, "3-email-form-ready")

            # 3. اختيار تاريخ الميلاد (يناير / 1 / 1995)
            print("📅 اختيار تاريخ الميلاد...")
            try:
                await page.click('div:has-text("Month")')
                await asyncio.sleep(1)
                await page.locator('div[role="option"]:visible').filter(has_text="January").click()
                await asyncio.sleep(0.5)

                await page.click('div:has-text("Day")')
                await asyncio.sleep(1)
                await page.locator('div[role="option"]:visible').filter(has_text="1").first.click()
                await asyncio.sleep(0.5)

                await page.click('div:has-text("Year")')
                await asyncio.sleep(1)
                await page.keyboard.type("1995")
                await page.keyboard.press("Enter")
                await asyncio.sleep(1)
            except Exception as e:
                print(f"⚠️ ملاحظة اختيار التاريخ: {e}")

            await save_diagnostic(page, "4-birthday-selected")

            # 4. إدخال البريد الإلكتروني
            print(f"⌨️ إدخال البريد: {bot_email}")
            email_field = await page.wait_for_selector('input[name="email"], input[type="email"]', timeout=7000)
            await email_field.click()
            for char in bot_email:
                await email_field.type(char, delay=random.randint(80, 150))
            await asyncio.sleep(1)

            # 5. إدخال كلمة المرور
            print("⌨️ إدخال كلمة المرور...")
            pass_field = await page.wait_for_selector('input[type="password"]', timeout=5000)
            await pass_field.click()
            for char in password:
                await pass_field.type(char, delay=random.randint(80, 150))
            await asyncio.sleep(1.5)

            await save_diagnostic(page, "5-data-filled-ready-to-send")

            # 6. النقر البشري المتقن على زر Send code لضمان إرسال الرمز وتجنب التجاهل
            print("📨 تحريك المؤشر والضغط على زر Send code بشكل بشري...")
            send_btn = await page.wait_for_selector('button:has-text("Send code"), [data-e2e="send-code-button"]', timeout=5000)
            
            # التأكد من تفعيل الزر
            is_disabled = await send_btn.get_attribute("disabled")
            if is_disabled is not None:
                await save_diagnostic(page, "error-send-btn-disabled")
                return False, "⚠️ زر إرسال الرمز معطل رغم تعبئة البيانات."

            # التمرير نحو الزر والتحليق فوقه ثم النقر
            await send_btn.hover()
            await asyncio.sleep(random.uniform(0.5, 1.0))
            await send_btn.click()
            print("✅ تم تنفيذ النقر البشري على Send code بنجاح!")
            
            # الانتظار ريثما يستجيب خادم تيك توك ويبدأ العد التنازلي
            await asyncio.sleep(5)
            await save_diagnostic(page, "6-after-send-code-clicked")

            # 7. جلب وإدخال الرمز من Gmail بسرعة فائقة
            print("⏳ جاري مراقبة صندوق الوارد في Gmail لسحب الرمز...")
            verification_code = fetch_verification_code()
            
            if verification_code:
                print(f"⌨️ إدخال الرمز المكتشف في تيك توك: {verification_code}")
                code_field = await page.wait_for_selector('input[placeholder*="digit" i], input[name="code"], input[maxlength="6"]', timeout=8000)
                await code_field.click()
                await code_field.type(verification_code, delay=100)
                await asyncio.sleep(2)
                
                await save_diagnostic(page, "7-code-entered")

                # الضغط على زر التأكيد أو Next
                submit_btn = await page.query_selector('button[type="submit"], button:has-text("Next"), button:has-text("التالي")')
                if submit_btn:
                    await submit_btn.click()
                    await asyncio.sleep(4)

                await save_diagnostic(page, "8-account-created-success")

                # حفظ الحساب في ملف المزرعة
                with open("saeed_database.txt", "a") as f:
                    f.write(f"{bot_email},{password}\n")
                return True, f"🎉 تم إنشاء الحساب وسحب الرمز بنجاح وتخزينه في المزرعة: {bot_email}"
            else:
                await save_diagnostic(page, "error-gmail-timeout-no-code")
                return False, "⚠️ تم النقر على إرسال الرمز ولكن تيك توك لم يرسل الرسالة (قد يتطلب التحقق البشري من الكابتشا)."

        except Exception as e:
            await save_diagnostic(page, "error-fatal-exception")
            return False, f"⚠️ حدث خطأ تقني: {str(e)}"
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
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
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
    <title>منظومة سعيد الذكية - محرك إرسال الرمز الفوري</title>
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
        <p style="text-align: center; color: #666; font-size: 14px;">نظام الضغط البشري وإرسال الرمز | المالك: سعيد</p>
        
        {% if msg %}
            <div class="alert">{{ msg }}</div>
        {% endif %}

        <div class="section">
            <h3>1️⃣ توليد وإنشاء حسابات جديدة في المزرعة</h3>
            <form action="/create_bots" method="post">
                <label>عدد الحسابات المراد إنشاؤها الآن:</label>
                <input type="number" name="count" value="1" min="1" max="5">
                <button type="submit" class="btn">بدء التوليد ومعالجة الرمز ⚙️</button>
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
        time.sleep(random.uniform(5.0, 8.0))
    return redirect(url_for('home', msg=last_msg))

@app.route('/send_followers', methods=['POST'])
def send_followers():
    target = request.form.get('target').strip()
    status_msg = asyncio.run(auto_send_follows(target))
    return redirect(url_for('home', msg=status_msg))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
