from pyrogram import Client, filters
from configs.settings import ADMIN_ID
import json

def load_db():
    with open("database/db.json") as f:
        return json.load(f)

def save_db(data):
    with open("database/db.json", "w") as f:
        json.dump(data, f, indent=2)

@Client.on_message(filters.command("addsource") & filters.user(ADMIN_ID))
async def add_source(client, message):
    if len(message.command) < 2:
        return await message.reply("استفاده: /addsource username")
    
    username = message.command[1].lstrip("@")
    db = load_db()
    if username not in db["twitter_sources"]:
        db["twitter_sources"].append(username)
        save_db(db)
        await message.reply(f"✅ @{username} اضافه شد.")
    else:
        await message.reply("قبلاً اضافه شده.")

@Client.on_message(filters.command("removesource") & filters.user(ADMIN_ID))
async def remove_source(client, message):
    if len(message.command) < 2:
        return await message.reply("استفاده: /removesource username")
    
    username = message.command[1].lstrip("@")
    db = load_db()
    if username in db["twitter_sources"]:
        db["twitter_sources"].remove(username)
        save_db(db)
        await message.reply(f"حذف شد.")
    else:
        await message.reply("پیدا نشد.")

@Client.on_message(filters.command("disable") & filters.user(ADMIN_ID))
async def disable_group(client, message):
    db = load_db()
    group_id = str(message.chat.id)
    if group_id in db["enabled_groups"]:
        db["enabled_groups"].remove(group_id)
        if group_id in db["groups"]:
            del db["groups"][group_id]
        save_db(db)
        await message.reply("گروه غیرفعال شد.")
