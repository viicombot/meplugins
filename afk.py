import re
import time
from datetime import datetime, timedelta
from pyrogram import filters, enums

from config import BANNED_USERS
from core import app
from utils import get_readable_time
from utils.database import dB, cleanmode, cleanmode_on, cleanmode_off
from utils.decorators import language
from strings import command

__MODULE__ = "Afk"
__HELP__ = """
• /afk [reason optional] - Afk from the chat.

You can use sticker/foto/video.
"""



async def put_cleanmode(chat_id, message_id):
    if chat_id not in cleanmode:
        cleanmode[chat_id] = []
    time_now = datetime.now()
    put = {
        "msg_id": message_id,
        "timer_after": time_now + timedelta(minutes=1),
    }
    cleanmode[chat_id].append(put)


def format_afk_caption(afktype, user_mention, seenago, reasonafk, lang):
    if afktype in ["animation", "photo", "video"]:
        return (
            lang["afk_2"].format(user_mention, seenago)
            if str(reasonafk) == "None"
            else lang["afk_3"].format(a=user_mention, b=seenago, c=reasonafk)
        )
    elif afktype == "text":
        return lang["afk_2"].format(user_mention, seenago)
    elif afktype == "text_reason":
        return lang["afk_3"].format(a=user_mention, b=seenago, c=reasonafk)
    return None

def get_media_path(user_id, afktype):
    ext = {"photo": "jpg", "video": "mp4"}.get(afktype)
    return f"downloads/{user_id}.{ext}" if ext else None

async def reply_afk_message(message, afktype, data, caption, user_id):
    if afktype == "animation":
        return await message.reply_animation(data, caption=caption)
    elif afktype == "photo":
        return await message.reply_photo(photo=get_media_path(user_id, afktype), caption=caption)
    elif afktype == "video":
        return await message.reply_video(video=get_media_path(user_id, afktype), caption=caption)
    else:
        return await message.reply_text(caption, disable_web_page_preview=True)


@app.on_message(command("AFK_COMMAND") & ~BANNED_USERS)
@language
async def active_afk(client, message, _):
    if message.sender_chat:
        return await message.reply_text(_["afk_1"])

    user_id = message.from_user.id
    verifier = await dB.get_var(user_id, "AFK")
    if verifier:
        try:
            afktype = verifier["type"]
            timeafk = verifier["time"]
            data = verifier["data"]
            reasonafk = verifier["reason"]
            seenago = get_readable_time(int(time.time() - timeafk))
            caption = format_afk_caption(afktype, message.from_user.mention, seenago, reasonafk, _)
            send = await reply_afk_message(message, afktype, data, caption, user_id)
        except Exception:
            send = await message.reply_text(_["afk_10"].format(message.from_user.first_name, message.from_user.id))
        await put_cleanmode(message.chat.id, send.id)
        return

    reason = None
    data = None
    afk_type = "text"

    if message.reply_to_message:
        reply = message.reply_to_message
        if reply.animation:
            data = reply.animation.file_id
            afk_type = "animation"
        elif reply.photo:
            await app.download_media(reply, file_name=f"{user_id}.jpg")
            afk_type = "photo"
        elif reply.video:
            await app.download_media(reply, file_name=f"{user_id}.mp4")
            afk_type = "video"
        elif reply.sticker:
            if reply.sticker.is_animated:
                afk_type = "text"
            else:
                await app.download_media(reply, file_name=f"{user_id}.mp4")
                afk_type = "video"

    if len(message.command) > 1:
        reason = message.text.split(None, 1)[1].strip()[:100]
        if afk_type == "text":
            afk_type = "text_reason"

    details = {
        "type": afk_type,
        "time": time.time(),
        "data": data,
        "reason": reason,
    }

    await dB.set_var(user_id, "AFK", details)
    send = await message.reply_text(
        _["afk_11"].format(a=message.from_user.mention, b=message.from_user.id)
    )
    await put_cleanmode(message.chat.id, send.id)

@app.on_message(filters.group & ~filters.bot & ~filters.via_bot, group=3)
@language
async def afk_watcher_func(client, message, _):
    if message.sender_chat:
        return

    async def handle_afk_user(user_id, user_mention):
        msg = ""
        verifier= await dB.get_var(user_id, "AFK")
        if not verifier:
            return
        try:
            afktype = verifier["type"]
            timeafk = verifier["time"]
            data = verifier["data"]
            reasonafk = verifier["reason"]
            seenago = get_readable_time(int(time.time() - timeafk))
            caption = format_afk_caption(afktype, user_mention, seenago, reasonafk, _)
            if afktype in ["animation", "photo", "video"]:
                send = await reply_afk_message(message, afktype, data, caption, user_id)
            else:
                msg += caption
                send = None
            return msg, send
        except:
            return _["afk_4"].format(a=user_mention), None

    text = message.text or message.caption or ""
    all_mentions = set()
    if message.entities:
        for entity in message.entities:
            if entity.type in [enums.MessageEntityType.MENTION, enums.MessageEntityType.TEXT_MENTION]:
                try:
                    if entity.type == enums.MessageEntityType.MENTION:
                        username = text[entity.offset + 1 : entity.offset + entity.length]
                        user = await app.get_users(username)
                    else:
                        user = entity.user
                    all_mentions.add((user.id, user.first_name[:25]))
                except:
                    continue

    replied_user = message.reply_to_message.from_user if message.reply_to_message and message.reply_to_message.from_user else None
    if replied_user:
        all_mentions.add((replied_user.id, replied_user.first_name[:25]))

    afk_messages = []
    send_msg = None
    for uid, uname in all_mentions:
        msg, send = await handle_afk_user(uid, uname)
        if msg:
            afk_messages.append(msg)
        if send:
            send_msg = send

    if afk_messages:
        try:
            msg_sent = await message.reply_text("\n".join(afk_messages), disable_web_page_preview=True)
            await put_cleanmode(message.chat.id, msg_sent.id)
        except:
            pass
    elif send_msg:
        try:
            await put_cleanmode(message.chat.id, send_msg.id)
        except:
            pass

@app.on_message(command("AFKDEL_COMMAND") & filters.group)
@language
async def afkdel_state(client, message, _):
    if not message.from_user:
        return
    if len(message.command) < 2:
        return await message.reply_text(_["afk_5"].format(message.text.split()[0]))

    state = message.text.split(None, 1)[1].strip().lower()
    if state == "enable":
        await cleanmode_on(message.chat.id)
        await message.reply_text(_["afk_6"])
    elif state == "disable":
        await cleanmode_off(message.chat.id)
        await message.reply_text(_["afk_7"])
    else:
        await message.reply_text(_["afk_5"].format(message.command[0]))

