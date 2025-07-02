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
    if message.sender_chat:
        return
    userid = message.from_user.id
    user_name = message.from_user.mention
    if message.entities:
        possible = ["/afk", f"/afk@{client.me.username}", "!afk"]
        message_text = message.text or message.caption
        for entity in message.entities:
            if entity.type == enums.MessageEntityType.BOT_COMMAND:
                if (message_text[0 : 0 + entity.length]).lower() in possible:
                    return

    msg = ""
    replied_user_id = 0

    # client AFK
    verifier = await dB.get_var(user_id, "AFK")
    if verifier:
        try:
            afktype = verifier["type"]
            timeafk = verifier["time"]
            data = verifier["data"]
            reasonafk = verifier["reason"]
            seenago = get_readable_time((int(time.time() - timeafk)))
            if afktype == "text":
                msg += _["afk_2"].format(a=user_name, b=seenago)
            if afktype == "text_reason":
                msg += _["afk_3"].format(a=user_name, b=seenago, c=reasonafk)
            if afktype == "animation":
                if str(reasonafk) == "None":
                    send = await message.reply_animation(
                        data,
                        caption=_["afk_2"].format(a=user_name, b=seenago),
                    )
                else:
                    send = await message.reply_animation(
                        data,
                        caption=_["afk_3"].format(a=user_name, b=seenago, c=reasonafk),
                    )
            if afktype == "photo":
                if str(reasonafk) == "None":
                    send = await message.reply_photo(
                        photo=f"downloads/{userid}.jpg",
                        caption=_["afk_2"].format(a=user_name, b=seenago),
                    )
                else:
                    send = await message.reply_photo(
                        photo=f"downloads/{userid}.jpg",
                        caption=_["afk_3"].format(a=user_name, b=seenago, c=reasonafk),
                    )

            if afktype == "video":
                if str(reasonafk) == "None":
                    send = await message.reply_video(
                        video=f"downloads/{userid}.mp4",
                        caption=_["afk_2"].format(a=user_name, b=seenago),
                    )
                else:
                    send = await message.reply_video(
                        video=f"downloads/{userid}.mp4",
                        caption=_["afk_3"].format(a=user_name, b=seenago, c=reasonafk),
                    )
        except:
            msg += _["afk_4"].format(a=user_name)

    if message.reply_to_message:
        try:
            replied_first_name = message.reply_to_message.from_user.mention
            replied_user_id = message.reply_to_message.from_user.id
            verifier = await dB.get_var(replied_user_id, "AFK")
            if verifier:
                try:
                    afktype = verifier["type"]
                    timeafk = verifier["time"]
                    data = verifier["data"]
                    reasonafk = verifier["reason"]
                    seenago = get_readable_time((int(time.time() - timeafk)))
                    if afktype == "text":
                        msg += _["afk_8"].format(a=replied_first_name, b=seenago)
                    if afktype == "text_reason":
                        msg += _["afk_10"].format(
                            a=replied_first_name, b=seenago, c=reasonafk
                        )
                    if afktype == "animation":
                        if str(reasonafk) == "None":
                            send = await message.reply_animation(
                                data,
                                caption=_["afk_8"].format(
                                    a=replied_first_name, b=seenago
                                ),
                            )
                        else:
                            send = await message.reply_animation(
                                data,
                                caption=_["afk_10"].format(
                                    a=replied_first_name, b=seenago, c=reasonafk
                                ),
                            )
                    if afktype == "photo":
                        if str(reasonafk) == "None":
                            send = await message.reply_photo(
                                photo=f"downloads/{replied_user_id}.jpg",
                                caption=_["afk_8"].format(
                                    a=replied_first_name,
                                    b=seenago,
                                ),
                            )
                        else:
                            send = await message.reply_photo(
                                photo=f"downloads/{replied_user_id}.jpg",
                                caption=_["afk_10"].format(
                                    a=replied_first_name,
                                    b=seenago,
                                    c=reasonafk,
                                ),
                            )
                    if afktype == "video":
                        if str(reasonafk) == "None":
                            send = await message.reply_video(
                                video=f"downloads/{replied_user_id}.mp4",
                                caption=_["afk_8"].format(
                                    a=replied_first_name,
                                    b=seenago,
                                ),
                            )
                        else:
                            send = await message.reply_video(
                                video=f"downloads/{replied_user_id}.mp4",
                                caption=_["afk_10"].format(
                                    a=replied_first_name,
                                    b=seenago,
                                    c=reasonafk,
                                ),
                            )
                except Exception:
                    msg += _["afk_10"].format(a=replied_first_name, b=replied_user_id)
        except:
            pass

    # If username or mentioned user is AFK
    if message.entities:
        entity = message.entities
        j = 0
        for x in range(len(entity)):
            if (entity[j].type) == enums.MessageEntityType.MENTION:
                found = re.findall("@([_0-9a-zA-Z]+)", message.text)
                try:
                    get_user = found[j]
                    user = await app.get_users(get_user)
                    if user.id == replied_user_id:
                        j += 1
                        continue
                except:
                    j += 1
                    continue
                verifier = await dB.get_var(user.id, "AFK")
                if verifier:
                    try:
                        afktype = verifier["type"]
                        timeafk = verifier["time"]
                        data = verifier["data"]
                        reasonafk = verifier["reason"]
                        seenago = get_readable_time((int(time.time() - timeafk)))
                        if afktype == "text":
                            msg += _["afk_8"].format(
                                a=user.first_name[:25],
                                b=seenago,
                            )
                        if afktype == "text_reason":
                            msg += _["afk_10"].format(
                                a=user.first_name[:25],
                                b=seenago,
                                c=reasonafk,
                            )
                        if afktype == "animation":
                            if str(reasonafk) == "None":
                                send = await message.reply_animation(
                                    data,
                                    caption=_["afk_8"].format(
                                        a=user.first_name[:25],
                                        b=seenago,
                                    ),
                                )
                            else:
                                send = await message.reply_animation(
                                    data,
                                    caption=_["afk_10"].format(
                                        a=user.first_name[:25],
                                        b=seenago,
                                        c=reasonafk,
                                    ),
                                )
                        if afktype == "photo":
                            if str(reasonafk) == "None":
                                send = await message.reply_photo(
                                    photo=f"downloads/{user.id}.jpg",
                                    caption=_["afk_8"].format(
                                        a=user.first_name[:25],
                                        b=seenago,
                                    ),
                                )
                            else:
                                send = await message.reply_photo(
                                    photo=f"downloads/{user.id}.jpg",
                                    caption=_["afk_10"].format(
                                        a=user.first_name[:25],
                                        b=seenago,
                                        c=reasonafk,
                                    ),
                                )
                        if afktype == "video":
                            if str(reasonafk) == "None":
                                send = await message.reply_video(
                                    video=f"downloads/{user.id}.mp4",
                                    caption=_["afk_8"].format(
                                        a=user.first_name[:25],
                                        b=seenago,
                                    ),
                                )
                            else:
                                send = await message.reply_video(
                                    video=f"downloads/{user.id}.mp4",
                                    caption=_["afk_10"].format(
                                        a=user.first_name[:25],
                                        b=seenago,
                                        c=reasonafk,
                                    ),
                                )
                    except:
                        msg += _["afk_9"].format(a=user.first_name[:25])
            elif (entity[j].type) == enums.MessageEntityType.TEXT_MENTION:
                try:
                    user_id = entity[j].user.id
                    if user_id == replied_user_id:
                        j += 1
                        continue
                    first_name = entity[j].user.first_name
                except:
                    j += 1
                    continue
                verifier = await dB.get_var(user_id, "AFK")
                if verifier:
                    try:
                        afktype = verifier["type"]
                        timeafk = verifier["time"]
                        data = verifier["data"]
                        reasonafk = verifier["reason"]
                        seenago = get_readable_time((int(time.time() - timeafk)))
                        if afktype == "text":
                            msg += _["afk_8"].format(
                                a=first_name[:25],
                                b=seenago,
                            )
                        if afktype == "text_reason":
                            msg += _["afk_10"].format(
                                a=first_name[:25],
                                b=seenago,
                                c=reasonafk,
                            )
                        if afktype == "animation":
                            if str(reasonafk) == "None":
                                send = await message.reply_animation(
                                    data,
                                    caption=_["afk_8"].format(
                                        a=first_name[:25],
                                        b=seenago,
                                    ),
                                )
                            else:
                                send = await message.reply_animation(
                                    data,
                                    caption=_["afk_10"].format(
                                        a=first_name[:25],
                                        b=seenago,
                                        c=reasonafk,
                                    ),
                                )
                        if afktype == "photo":
                            if str(reasonafk) == "None":
                                send = await message.reply_photo(
                                    photo=f"downloads/{user_id}.jpg",
                                    caption=_["afk_8"].format(
                                        a=first_name[:25],
                                        b=seenago,
                                    ),
                                )
                            else:
                                send = await message.reply_photo(
                                    photo=f"downloads/{user_id}.jpg",
                                    caption=_["afk_10"].format(
                                        a=first_name[:25],
                                        b=seenago,
                                        c=reasonafk,
                                    ),
                                )
                        if afktype == "video":
                            if str(reasonafk) == "None":
                                send = await message.reply_video(
                                    video=f"downloads/{user_id}.mp4",
                                    caption=_["afk_8"].format(
                                        a=first_name[:25],
                                        b=seenago,
                                    ),
                                )
                            else:
                                send = await message.reply_video(
                                    video=f"downloads/{user_id}.mp4",
                                    caption=_["afk_10"].format(
                                        a=first_name[:25],
                                        b=seenago,
                                        c=reasonafk,
                                    ),
                                )
                    except:
                        msg += _["afk_10"].format(a=first_name[:25])
            j += 1
    if msg != "":
        try:
            send = await message.reply_text(msg, disable_web_page_preview=True)
        except:
            pass
    try:
        await put_cleanmode(message.chat.id, send.id)
    except:
        pass

