#hello world
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update

# لاگ‌ها برای دیدن وضعیت در سرور ابری بسیار مهمن
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "GAPGPTMASKTOKENlxa4e34cdkX0X"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام طاها! ربات مستقیم از سرور ابری در حال پاسخگویی است 🚀")

if __name__ == '__main__':
    print("در حال راه‌اندازی ربات...")
    # اتصال مستقیم بدون نیاز به هیچ ورکر یا پروکسی!
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    
    print("🤖 ربات با موفقیت فعال شد و در حال گوش دادن به پیام‌هاست!")
    app.run_polling()
