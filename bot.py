import os
import urllib.parse
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

client = genai.Client(api_key=GEMINI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "হ্যালো! আমি আপনার অল-ইন-ওয়ান AI Assistant। 🤖\n\n"
        "আমি যা যা করতে পারি:\n"
        "১. যেকোনো প্রশ্নের উত্তর বা কথা বলা (সাধারণ টেক্সট লিখুন)\n"
        "২. ছবি তৈরি করতে: `image: আপনার আইডিয়া` (যেমন: image: a cute cat)\n"
        "৩. ভিডিও/জিফ তৈরি করতে: `video: আপনার আইডিয়া` (যেমন: video: running dog)"
    )
    await update.message.reply_text(welcome_msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_text_lower = user_text.lower()
    
    # ১. ছবি তৈরি করার জন্য (image: বা photo: দিয়ে শুরু হলে)
    if user_text_lower.startswith("image:") or user_text_lower.startswith("photo:") or user_text_lower.startswith("ছবি:"):
        await update.message.reply_chat_action("upload_photo")
        prompt = user_text.split(":", 1)[1].strip()
        encoded_prompt = urllib.parse.quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        
        try:
            await update.message.reply_photo(photo=image_url, caption=f"🎨 আপনার তৈরি ছবি: {prompt}")
        except Exception as e:
            await update.message.reply_text(f"ছবি তৈরিতে সমস্যা হয়েছে: {str(e)}")

    # ২. ভিডিও / শর্ট অ্যানিমেশন তৈরি করার জন্য (video: বা ভিডিও: দিয়ে শুরু হলে)
    elif user_text_lower.startswith("video:") or user_text_lower.startswith("ভিডিও:"):
        await update.message.reply_chat_action("upload_video")
        prompt = user_text.split(":", 1)[1].strip()
        encoded_prompt = urllib.parse.quote(prompt)
        # Pollinations AI animation URL
        video_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model=flux&nologo=true&private=true&enhance=false"
        
        try:
            await update.message.reply_animation(animation=video_url, caption=f"🎬 আপনার ভিডিও অ্যানিমেশন: {prompt}")
        except Exception as e:
            await update.message.reply_text(f"ভিডিও তৈরিতে সমস্যা হয়েছে: {str(e)}")

    # ৩. সাধারণ কথাবার্তা ও টেক্সটের উত্তরের জন্য (Gemini AI)
    else:
        await update.message.reply_chat_action("typing")
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_text,
            )
            await update.message.reply_text(response.text)
        except Exception as e:
            await update.message.reply_text(f"সমস্যা হয়েছে: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
