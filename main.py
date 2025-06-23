
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
FORCE_CHANNEL = "@InstaSaverX"

async def is_user_joined_channel(user_id: int, bot) -> bool:
    try:
        member = await bot.get_chat_member(FORCE_CHANNEL, user_id)
        return member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_joined_channel(update.effective_user.id, context.bot):
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("✨ Join Channel", url=f"https://t.me/{FORCE_CHANNEL.strip('@')}")]])
        await update.message.reply_text("🔐 Please join our channel to use this bot.", reply_markup=btn)
        return

    await update.message.reply_text("✅ Send any Instagram reel/post/story URL to download.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_joined_channel(update.effective_user.id, context.bot):
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("✨ Join Channel", url=f"https://t.me/{FORCE_CHANNEL.strip('@')}")]])
        await update.message.reply_text("🔐 Please join our channel to use this bot.", reply_markup=btn)
        return

    url = update.message.text.strip()
    if not url.startswith("https://www.instagram.com"):
        await update.message.reply_text("⚠️ Please send a valid Instagram URL.")
        return

    await update.message.reply_text("⏳ Downloading, please wait...")

    api_url = "https://instagram-downloader-download-instagram-stories-videos4.p.rapidapi.com/convert"
    querystring = {"url": url}
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "instagram-downloader-download-instagram-stories-videos4.p.rapidapi.com"
    }

    try:
        response = requests.get(api_url, headers=headers, params=querystring)
        data = response.json()
        media = data.get("media")

        if isinstance(media, list) and media:
            video_url = media[0].get("url")
            if video_url:
                video_data = requests.get(video_url, stream=True)
                with open("insta_video.mp4", "wb") as f:
                    f.write(video_data.content)

                await update.message.reply_video(video=open("insta_video.mp4", "rb"))
                os.remove("insta_video.mp4")
                return

        await update.message.reply_text("⚠️ Could not fetch video. Please send a public link.")
    except Exception as e:
        print("ERROR:", e)
        await update.message.reply_text("❌ Something went wrong.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("⚡ InstaSaverX Bot is running...")
    app.run_polling()
