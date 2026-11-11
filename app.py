import os
import asyncio
import random
import imaplib
import email
import re
import html
import time
import uuid
from flask import Flask, render_template_string, request, redirect, url_for
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import logging

# إعداد اللوغين لتتبع الأخطاء
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# --- إعدادات سعيد المؤتمتة بالكامل ---
BASE_EMAIL = "saeedosama921@gmail.com"
GMAIL_APP_PASSWORD = "lxowejdbwlrdtblc" # تأكد من تفعيل App Password في جوجل

# قائمة User-Agents حقيقية لتبدو وكأنك تتصفح من هواتف وحواسيب مختلفة
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
]

def fetch_verification_code(timeout=60):
    """جلب الرمز من Gmail باستخدام IMAP مع معالجة أخطاء أفضل"""
    print("📥 جاري الاتصال بـ Gmail للبحث عن رمز التفعيل...")
    start_time = time.time()
    
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(BASE_EMAIL, GMAIL_APP_PASSWORD)
        
        while time.time() - start_time < timeout:
            mail.select("inbox")
            status, messages = mail.search(None, '(UNSEEN FROM "tiktok.com")')
            
            if status == "OK" and messages[0]:
                msg_ids = messages[0].split()
                if msg_ids:
                    latest_message_id = msg_ids[-1]
                    status, data = mail.fetch(latest_message_id, '(RFC822)')
                    
                    for response_part in data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part)
                            subject = msg["subject"] or ""
                            body = ""
                            
                            # استخراج النص من الإيميل (يدعم HTML و Plain Text)
                            if msg.is_multipart():
                                for part in msg.walk():
                                    content_type = part.get_content_type()
                                    content_disposition = str(part.get("Content-Disposition"))
                                    
                                    if content_type == "text/plain" and "attachment" not in content_disposition:
                                        payload = part.get_payload(decode=True)
                                        if payload:
                                            body += payload.decode('utf-8', errors='ignore') + "\n"
                            else:
                                payload = msg.get_payload(decode=True)
                                if payload:
                                    body = payload.decode('utf-8', errors='ignore')
                            
                            # البحث عن الرقم المكون من 6 خانات
                            code_match = re.search(r'\b\d{6}\b', body + " " + subject)
                            if code_match:
                                code = code_match.group(0)
                                print(f"✅ تم التقاط الرمز بنجاح: {code}")
                                mail.store(latest_message_id, '+FLAGS', '\\Seen')
                                mail.logout()
                                return code
            time.sleep(3) # انتظار كل 3 ثواني فقط
            
        mail.logout()
    except Exception as e:
        print(f"❌ خطأ في الاتصال بالإيميل: {str(e)}")
    return None

def generate_dot_email():
    """إنشاء إيميل بتقنية النقاط لتجاوز حد التسجيل"""
    name, domain = BASE_EMAIL.split('@')
    name_list = list(name)
    # نضع نقطة واحدة فقط لتقليل فرص الحظر، ونوزعها عشوائياً
    num_dots = random.randint(1, 3)
    if len(name_list) > num_dots:
        positions = random.sample(range(1, len(name_list)), num_dots)
        for pos in sorted(positions, reverse=True):
            name_list.insert(pos, '.')
    return "".join(name_list) + "@" + domain

def generate_human_username():
    """اسم مستخدم يبدو طبيعياً جداً"""
    prefixes = ["saeed_", "osama.", "ahmed_v", "ali_k", "tech_guru", "pro_user"]
    suffixes = ["2024", "99", "live", "tv", "real", "official"]
    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)
    random_num = random.randint(10, 999)
    return f"{prefix}{suffix}{random_num}"

async def auto_create_bot_browser():
    """المحرك الرئيسي المحسن"""
    bot_email = generate_dot_email()
    username = generate_human_username()
    password = f"Saeed!{random.randint(1000, 9999)}"
    user_agent = random.choice(USER_AGENTS)
    
    print(f"🚀 بدء إنشاء حساب جديد: {username} | {bot_email}")

    async with async_playwright() as p:
        # تشغيل المتصفح بوضع Headless ولكن بخداع الكشف
        browser = await p.chromium.launch(
            headless=True, 
            args=[
                "--disable-blink-features=AutomationControlled", 
                "--no-sandbox",
                "--disable-dev-shm-usage",
                f"--user-agent={user_agent}",
                "--window-size=1920,1080"
            ]
        )
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="Asia/Riyadh", # تغيير المنطقة الزمنية حسب رغبتك
            user_agent=user_agent,
            permissions=['geolocation'],
            geolocation={"longitude": 46.6753, "latitude": 24.7136} # إحداثيات الرياض كمثال
        )
        
        page = await context.new_page()
        
        # تطبيق تقنيات التخفي المتقدمة
        await stealth_async(page)
        
        # محاكاة سلوك بشري (تحريك الماوس، التمرير)
        await page.evaluate("""
            window.scrollTo(0, document.body.scrollHeight);
            setTimeout(() => window.scrollTo(0, 0), 1000);
        """)

        try:
            # 1. الذهاب لصفحة التسجيل
            await page.goto("https://www.tiktok.com/signup", wait_until="domcontentloaded", timeout=30000)
            
            # الانتظار حتى تختفي شاشة التحميل الأولية
            await page.wait_for_timeout(2000)
            
            # 2. النقر على زر الإيميل (إذا وجد)
            # ملاحظة: قد يتغير الـ Selector، لذا نستخدم بحث ذكي
            email_btn = await page.query_selector('button:has-text("Email")') or await page.query_selector('div:has-text("Sign up with email")')
            if email_btn:
                await email_btn.click()
                await page.wait_for_timeout(1000)

            # 3. ملء بيانات التسجيل
            # حقول الإدخال الشائعة في تيك توك
            inputs = await page.query_selector_all('input')
            for inp in inputs:
                placeholder = await inp.get_attribute("placeholder")
                type_attr = await inp.get_attribute("type")
                
                if placeholder and "email" in placeholder.lower():
                    await inp.fill(bot_email)
                    await page.wait_for_timeout(random.uniform(0.5, 1.5)) # تأخير عشوائي بين الكتابة
                
                elif placeholder and "password" in placeholder.lower():
                    await inp.fill(password)
                    await page.wait_for_timeout(random.uniform(0.5, 1.5))
                
                elif placeholder and "phone" in placeholder.lower():
                    # نملئ الإيميل هنا أيضاً أحياناً كخدعة
                    await inp.fill(bot_email)

            # محاولة الضغط على زر التالي/التالي
            next_btn = await page.query_selector('button[type="submit"], button:has-text("Next"), button:has-text("Sign Up")')
            if next_btn:
                await next_btn.click()
            
            # 3. التعامل مع تحدي Cloudflare (إذا ظهر)
            # نتحقق مما إذا كنا في صفحة تسجيل الدخول العادية أم واجهة التسجيل
            current_url = page.url
            if "signup" in current_url or "login" in current_url:
                 print("⏳ جاري انتظار تحميل نموذج التسجيل الكامل...")
                 await page.wait_for_timeout(5000) # وقت كافٍ لاختبار الحماية

            # 4. جلب الرمز
            code = await asyncio.to_thread(fetch_verification_code, timeout=90)
            
            if code:
                print(f"🔑 تم إدخال الرمز: {code}")
                # البحث عن حقل الرمز
                code_input = await page.query_selector('input[name="code"], input[type="tel"], input[name="verificationCode"]')
                if code_input:
                    await code_input.fill(code)
                    await page.wait_for_timeout(1000)
                    
                    # الضغط على زر التحقق
                    verify_btn = await page.query_selector('button:has-text("Verify"), button:has-text("Submit")')
                    if verify_btn:
                        await verify_btn.click()
                        
                        # انتظار النجاح
                        await page.wait_for_timeout(5000)
                        
                        # التحقق هل نجح؟ (نتحقق من وجود شريط التنقل السفلي أو رسالة ترحيب)
                        if await page.locator('nav').count() > 0 or "home" in page.url:
                            print(f"🎉 نجاح! الحساب {username} تم إنشاؤه والتحقق منه.")
                            return {"status": "success", "email": bot_email, "pass": password}
                        else:
                            print("⚠️ الرمز صحيح لكن لم يكتمل التسجيل بعد.")
                            return {"status": "pending", "email": bot_email, "pass": password}
                else:
                    print("❌ لم يتم العثور على حقل إدخال الرمز.")
            else:
                print("❌ فشل جلب الرمز.")

        except Exception as e:
            print(f"💥 خطأ أثناء التشغيل: {e}")
            # لقطة شاشة عند الفشل للمساعدة في التصحيح
            await page.screenshot(path=f"error_{uuid.uuid4().hex}.png")
            
        finally:
            await browser.close()
            
    return {"status": "failed"}

# --- واجهة الويب البسيطة لتشغيل السكربت ---
@app.route('/')
def index():
    return render_template_string('''
    <h1>منظومة سعيد النهائية 🌟</h1>
    <p>اضغط الزر لإنشاء حساب آمن واحترافي:</p>
    <form action="/run" method="post">
        <button type="submit">بدء التوليد الآمن</button>
    </form>
    ''')

@app.route('/run', methods=['POST'])
def run_bot():
    result = asyncio.run(auto_create_bot_browser())
    return f'''
    <h2>النتيجة: {result['status']}</h2>
    <p>الإيميل: {result.get('email', 'N/A')}</p>
    <p>الباسورد: {result.get('pass', 'N/A')}</p>
    <a href="/">عودة</a>
    '''

if __name__ == '__main__':
    app.run(debug=True, port=5000)
