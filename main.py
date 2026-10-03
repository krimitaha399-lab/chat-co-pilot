import os
import re
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# تنظیم لاگ‌ها
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# خواندن توکن از متغیرهای محیطی یا مقدار پیش‌فرض لوکال
TOKEN = os.getenv("BOT_TOKEN", "GAPGPTMASKTOKENdib10yeocboX0X")

# دیکشنری موقت برای شمارش اخطارهای کاربران (در رم)
# ساختار: {user_id: warning_count}
user_warnings = {}

# پترن تشخیص لینک و آیدی تلگرام برای آنتی‌اسپم
LINK_REGEX = re.compile(r'(https?://[^\s]+|t\.me/[^\s]+|@[a-zA-Z0-9_]{5,})', re.IGNORECASE)

# لیست کلمات ممنوعه (می‌تونی هر کلمه‌ای خواستی اضافه کنی)
BAD_WORDS = [
    "فحش1", "فحش2", "قمار", "بت", "صیغه"  # نمونه کلمات غیراخلاقی یا اسپم
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پیام خوش‌آمدگویی"""
    await update.message.reply_text("سلام! ربات مدیریت گروه و ضداسپم فعال است 🛡️")

async def moderate_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بررسی و مانیتور کردن پیام‌های گروه برای اسپم، لینک و محتوای غیراخلاقی"""
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    # اگر پیام متنی نبود یا از طرف خود ربات/کانال ناشناس بود رد شود
    if not message or not message.text or not user:
        return

    # بررسی آیا کاربر ادمین است؟ (ادمین‌ها نباید اخطار بگیرند)
    try:
        member = await chat.get_member(user.id)
        if member.status in ['administrator', 'creator']:
            return
    except Exception as e:
        logger.error(f"خطا در دریافت وضعیت کاربر: {e}")

    text = message.text.lower()
    violation = False
    reason = ""

    # ۱. بررسی وجود لینک و آیدی تبلیغاتی
    if LINK_REGEX.search(text):
        violation = True
        reason = "ارسال لینک یا آیدی تبلیغاتی ممنوع است."

    # ۲. بررسی کلمات ممنوعه / غیراخلاقی
    elif any(bad_word in text for bad_word in BAD_WORDS):
        violation = True
        reason = "استفاده از کلمات نامناسب و غیراخلاقی ممنوع است."

    # در صورت وجود تخلف
    if violation:
        # ۱. حذف پیام نامناسب
        try:
            await message.delete()
        except Exception as e:
            logger.error(f"خطا در پاک کردن پیام: {e}")

        # ۲. سیستم اخطار و بن
        user_id = user.id
        user_warnings[user_id] = user_warnings.get(user_id, 0) + 1
        current_warnings = user_warnings[user_id]

        if current_warnings >= 3:
            # اخراج کاربر بعد از ۳ اخطار
            try:
                await chat.ban_member(user_id)
                await chat.send_message(
                    f"⛔️ کاربر {user.mention_html()} به دلیل دریافت ۳ اخطار ({reason}) از گروه اخراج شد.",
                    parse_mode='HTML'
                )
                user_warnings[user_id] = 0  # ریست اخطارها
            except Exception as e:
                logger.error(f"خطا در بن کردن: {e}")
        else:
            # ارسال پیام اخطار
            await chat.send_message(
                f"⚠️ کاربر {user.mention_html()}، {reason}\n"
                f"تعداد اخطارها: {current_warnings}/3",
                parse_mode='HTML'
            )

if __name__ == '__main__':
    if not TOKEN:
        raise ValueError("توکن ربات یافت نشد! متغیر BOT_TOKEN را تنظیم کنید.")

    print("در حال راه‌اندازی ربات مدیریتی...")
    app = ApplicationBuilder().token(TOKEN).build()

    # هندلر دستور استارت
    app.add_handler(CommandHandler('start', start))

    # هندلر فیلتر تمام پیام‌های متنی در گروه‌ها و سوپرگروه‌ها
    app.add_handler(MessageHandler(
        filters.TEXT & (filters.ChatType.GROUPS),
        moderate_messages
    ))

    print("🤖 ربات با موفقیت فعال شد و در حال محافظت از چت است!")
    app.run_polling()
