from pyrogram import Client, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import json
import aiohttp
from scraper.twitter_scraper import get_latest_tweets
from helpers.cache import get_video_cache, set_video_cache
from handlers.admin import *
from configs.settings import BOT_TOKEN, ADMIN_ID, TWITTER_ACCOUNTS

app = Client("goalbot", bot_token=BOT_TOKEN)

# دیتابیس
DB_FILE = "database/db.json"

def load_db():
    try:
        with open(DB_FILE) as f:
            return json.load(f)
    except:
        return {"groups": {}, "enabled_groups": [], "twitter_sources": TWITTER_ACCOUNTS[:]}

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

# وقتی گروه جدید اضافه شد
@app.on_message(filters.group & filters.new_chat_members)
async def auto_enable(client, message):
    if message.new_chat_members and app.get_me().id in [u.id for u in message.new_chat_members]:
        db = load_db()
        group_id = str(message.chat.id)
        if group_id not in db["enabled_groups"]:
            db["enabled_groups"].append(group_id)
            db["groups"][group_id] = 0
            save_db(db)
            await message.reply("ربات فعال شد ✅\nویدیوهای گل به‌زودی اینجاست ⚽")

# تابع اصلی چک کردن توییت‌ها
async def check_new_goals():
    db = load_db()
    sources = db.get("twitter_sources", TWITTER_ACCOUNTS[:])
    
    all_new_tweets = []
    for username in sources:
        last_id = 0  # ما از همه گروه‌ها آخرین آیدی رو نمی‌گیریم، فقط جدیدها رو می‌گیریم
        tweets = await get_latest_tweets(username, since_id=0)
        all_new_tweets.extend(tweets)
    
    if not all_new_tweets:
        return
    
    # جدیدترین‌ها رو بگیریم
    all_new_tweets.sort(key=lambda x: x["id"], reverse=True)
    
    for tweet in all_new_tweets:
        tweet_id = tweet["id"]
        video_url = tweet["video_url"]
        caption = tweet["caption"]
        
        # کش تلگرام file_id
        file_id = get_video_cache(video_url)
        
        sent_to_any = False
        for group_id_str in db["enabled_groups"]:
            last_seen = db["groups"].get(group_id_str, 0)
            if tweet_id <= last_seen:
                continue
                
            try:
                if file_id:
                    await app.send_video(int(group_id_str), file_id, caption=caption)
                else:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(video_url) as resp:
                            if resp.status == 200:
                                video_bytes = await resp.read()
                                sent_msg = await app.send_video(
                                    int(group_id_str),
                                    video_bytes,
                                    caption=caption
                                )
                                # کش کنیم برای گروه‌های بعدی
                                set_video_cache(video_url, sent_msg.video.file_id)
                                file_id = sent_msg.video.file_id
                # آپدیت آخرین آیدی برای این گروه
                db["groups"][group_id_str] = tweet_id
                sent_to_any = True
            except Exception as e:
                print(f"Error sending to {group_id_str}: {e}")
        
        if sent_to_any:
            save_db(db)

# استارت scheduler
scheduler = AsyncIOScheduler()
scheduler.add_job(check_new_goals, "interval", seconds=60, id="check_goals")
scheduler.start()

print("ربات گل‌ها روشن شد ⚽🔥")
app.run()
