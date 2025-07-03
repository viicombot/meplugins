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
<blockquote expandable>/afk [reason optional] - Afk from the chat.

You can use sticker/foto/video.

If you want unafk, just type any text.</blockquote>
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


def format_afk_caption(afktype, user_mention, seenago, reasonafk, lang_key, lang):
    if afktype in ["text", "photo", "video", "animation"] and not reasonafk:
        return lang[lang_key].format(a=user_mention, b=seenago)
    return lang[lang_key.replace("2", "3")].format(a=user_mention, b=seenago, c=reasonafk)


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

async def handle_afk_reply(message, afktype, user_id, user_mention, timeafk, data, reasonafk, lang_key, lang):
    seenago = get_readable_time(int(time.time() - timeafk))
    caption = format_afk_caption(afktype, user_mention, seenago, reasonafk, lang_key, lang)
    return await reply_afk_message(message, afktype, data, caption, user_id)

@app.on_message(filters.command("afk") & ~BANNED_USERS)
@language
async def active_afk(client, message, _):
    if message.sender_chat:
        return await message.reply_text(_["afk_1"])

    user_id = message.from_user.id
    user_mention = message.from_user.mention
    user_firstname = message.from_user.first_name

    # Check if user already AFK
    afk_data = await dB.get_var(user_id, "AFK")
    if afk_data:
        try:
            send = await handle_afk_reply(
                message,
                afk_data["type"],
                user_id,
                user_mention,
                afk_data["time"],
                afk_data["data"],
                afk_data["reason"],
                "afk_2",
                _
            )
        except Exception:
            send = await message.reply_text(_["afk_10"].format(user_firstname, user_id))

        await put_cleanmode(message.chat.id, send.id)
        await dB.remove_var(user_id, "AFK")
        return

    # Setup new AFK
    reason = "Berak dulu"
    data = None
    afk_type = "text"

    if message.reply_to_message:
        reply = message.reply_to_message
        if reply.animation:
            data = reply.animation.file_id
            afk_type = "animation"
            reason = reply.caption or ""
        elif reply.photo:
            await app.download_media(reply, file_name=f"{user_id}.jpg")
            afk_type = "photo"
            reason = reply.caption or ""
        elif reply.video:
            await app.download_media(reply, file_name=f"{user_id}.mp4")
            afk_type = "video"
            reason = reply.caption or ""
        elif reply.sticker:
            if reply.sticker.is_animated:
                afk_type = "text"
            else:
                await app.download_media(reply, file_name=f"{user_id}.mp4")
                afk_type = "video"
                reason = reply.caption or ""

    if afk_type == "text":
        if len(message.command) > 1:
            reason = message.text.split(None, 1)[1].strip()[:100]
            afk_type = "text"
    else:
        if len(message.command) > 1:
            reason = message.text.split(None, 1)[1].strip()[:100]


    details = {
        "type": afk_type,
        "time": time.time(),
        "data": data,
        "reason": reason,
    }
    await dB.set_var(user_id, "AFK", details)

    send = await message.reply_text(_["afk_11"].format(a=user_mention, b=user_id))
    await put_cleanmode(message.chat.id, send.id)


    
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

@app.on_message(filters.group & ~filters.bot & ~filters.via_bot, group=3)
@language
async def afk_watcher_func(client, message, _):
    if message.sender_chat:
        return

    msg = ""
    send = None
    user_id = message.from_user.id
    user_mention = message.from_user.mention

    if message.entities:
        possible = ["/afk", f"/afk@{client.me.username}", "afk"]
        message_text = message.text or message.caption
        for entity in message.entities:
            if entity.type == enums.MessageEntityType.BOT_COMMAND:
                if message_text[:entity.length].lower() in possible:
                    return

    # AFK Checker untuk Pengirim Pesan
    afk_data = await dB.get_var(user_id, "AFK")
    if afk_data:
        try:
            send = await handle_afk_reply(
                message,
                afk_data["type"],
                user_id,
                user_mention,
                afk_data["time"],
                afk_data["data"],
                afk_data["reason"],
                "afk_2",
                _
            )
        except:
            msg += _["afk_4"].format(a=user_mention)
        await dB.remove_var(user_id, "AFK")

    # AFK Checker untuk user yang di-reply
    if message.reply_to_message and message.reply_to_message.from_user:
        r_user = message.reply_to_message.from_user
        r_id = r_user.id
        r_mention = r_user.mention
        afk_data = await dB.get_var(r_id, "AFK")
        if afk_data:
            try:
                send = await handle_afk_reply(
                    message,
                    afk_data["type"],
                    r_id,
                    r_mention,
                    afk_data["time"],
                    afk_data["data"],
                    afk_data["reason"],
                    "afk_10",
                    _
                )
            except:
                msg += _["afk_10"].format(a=r_mention, b=r_id)

    # AFK Checker via @mention dan text_mention
    if message.entities:
        for ent in message.entities:
            if ent.type in [enums.MessageEntityType.MENTION, enums.MessageEntityType.TEXT_MENTION]:
                try:
                    if ent.type == enums.MessageEntityType.MENTION:
                        username = message.text[ent.offset: ent.offset + ent.length].lstrip("@")
                        user = await client.get_users(username)
                    else:
                        user = ent.user
                    if user.id == message.from_user.id:
                        continue
                except:
                    continue

                afk_data = await dB.get_var(user.id, "AFK")
                if afk_data:
                    try:
                        send = await handle_afk_reply(
                            message,
                            afk_data["type"],
                            user.id,
                            user.first_name[:25],
                            afk_data["time"],
                            afk_data["data"],
                            afk_data["reason"],
                            "afk_10",
                            _
                        )
                    except:
                        msg += _["afk_9"].format(a=user.first_name[:25])

    if msg:
        try:
            send = await message.reply_text(msg, disable_web_page_preview=True)
        except:
            pass

    if send:
        try:
            await put_cleanmode(message.chat.id, send.id)
        except:
            pass
