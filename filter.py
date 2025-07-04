import re
import traceback

from pyrogram import enums, filters

from core import app
from utils.database import dB
from utils.functions import Tools
from utils.keyboard import Button
from logs import LOGGER
from utils.decorators import ONLY_GROUP

from config import BANNED_USERS

@app.on_message(filters.command(["savefilter", "addfilter", "filter"]) & ~BANNED_USERS)
@ONLY_GROUP
async def filter_cmd(_, message):
    xx = await message.reply(">**Please wait...**")
    rep = message.reply_to_message
    if len(message.command) < 2 or not rep:
        return await xx.edit(f">**Please reply message and give filter name**")
    nama = message.text.split()[1]
    getfilter = await dB.get_var(message.chat.id, nama, "FILTER")
    if getfilter:
        return await xx.edit(f">**Filter {nama} already exist!**")
    value = None

    text = rep.text or rep.caption or ""
    if rep.media and rep.media != enums.MessageMediaType.WEB_PAGE_PREVIEW:
        media = Tools.get_file_id(rep)
        value = {
            "type": media["message_type"],
            "file_id": media["file_id"],
            "result": text,
        }
    else:
        value = {"type": "text", "file_id": "", "result": text}
    if value:
        await dB.set_var(message.chat.id, nama, value, "FILTER")
        return await xx.edit(f">**Saved {nama} filter!!**")
    else:
        return await xx.edit(f">**Please reply message and give filter name**")

@app.on_message(filters.command(["getfilter"]) & ~BANNED_USERS)
@ONLY_GROUP
async def getfilter_cmd(client, message):
    xx = await message.reply(">**Please wait...**")
    try:
        if len(message.text.split()) == 3 and (message.text.split())[2] in [
            "noformat",
            "raw",
        ]:
            filter = message.text.split()[1]
            data = await dB.get_var(message.chat.id, filter, "FILTER")
            if not data:
                return await xx.edit(f">**Filter {filter} not found!**")
            return await get_raw_filter(client, message, xx, data)
        else:
            return await xx.edit(
                f">**Please valid command.\nExample: `{message.text.split()[0]} ciah noformat`.**"
            )
    except Exception as e:
        return await xx.edit(f">**ERROR**: {str(e)}")


async def get_raw_filter(_, message, xx, data):
    try:
        teks = data["result"]
        type = data["type"]
        file_id = data["file_id"]

        if type == "text":
            await message.reply(
                teks,
                parse_mode=enums.ParseMode.DISABLED,
            )
        elif type == "sticker":
            await message.reply_sticker(
                file_id,
            )
        elif type == "video_note":
            await message.reply_video_note(
                file_id,
            )
        else:
            kwargs = {
                "photo": message.reply_photo,
                "voice": message.reply_voice,
                "audio": message.reply_audio,
                "video": message.reply_video,
                "animation": message.reply_animation,
                "document": message.reply_document,
            }

            if type in kwargs:
                await kwargs[type](
                    file_id,
                    caption=teks,
                    parse_mode=enums.ParseMode.DISABLED,
                )
    except Exception as er:
        LOGGER.info(f"ERROR: {traceback.format_exc()}")
        return await message.reply(f">**ERROR**: {str(er)}")
    return await xx.delete()

@app.on_message(filters.command(["filters", "allfilter"]) & ~BANNED_USERS)
@ONLY_GROUP
async def filters_cmd(_, message):
    xx = await message.reply(">**Please wait...**")
    getfilter = await dB.all_var(message.chat.id, "FILTER")
    if not getfilter:
        return await xx.edit(f">**Thits chat dont have any filter!**")
    rply = f">**List of Filters:**\n\n"
    for x, data in getfilter.items():
        type = await dB.get_var(message.chat.id, x, "FILTER")
        rply += f"**• Name: `{x}` | Type: `{type['type']}`**\n"
    return await xx.edit(rply)

@app.on_message(filters.command(["stopfilter", "clearfilter"]) & ~BANNED_USERS)
@ONLY_GROUP
async def stopfilter_cmd(client, message):
    args = client.get_arg(message).split(",")
    xx = await message.reply(">**Please wait...**")
    if len(args) == 0 or (len(args) == 1 and args[0].strip() == ""):
        return await xx.edit(f">**Which filter do you want to delete?**")
    if message.command[1] == "all":
        if not await dB.all_var(message.chat.id, "FILTER"):
            return await xx.edit(f">**You dont have any filter!**")
        for nama in await dB.all_var(message.chat.id, "FILTER"):
            data = await dB.get_var(message.chat.id, nama, "FILTER")
            await dB.remove_var(message.chat.id, nama, "FILTER")
        return await xx.edit(f">**Succesfully deleted all filter!**")
    else:
        gagal_list = []
        sukses_list = []

        for arg in args:
            arg = arg.strip()
            if not arg:
                continue
            data = await dB.get_var(message.chat.id, arg, "FILTER")
            if not data:
                gagal_list.append(arg)
            else:
                await dB.remove_var(message.chat.id, arg, "FILTER")
                sukses_list.append(arg)

        if sukses_list:
            return await xx.edit(
                f">**Filter `{', '.join(sukses_list)}` successfully deleted.**"
            )

        if gagal_list:
            return await xx.edit(
                f">**Filter `{', '.join(gagal_list)}` not found!**"
            )

@app.on_message(filters.incoming & filters.group & ~filters.bot & ~filters.via_bot & ~BANNED_USERS, group=4)
async def FILTERS(_, message):
    try:
        text = message.text or message.caption
        if not text:
            return

        getfilter = await dB.all_var(message.chat.id, "FILTER")
        if not getfilter:
            return
        #reply = message.from_user or message.sender_chat
        for word in getfilter:
            pattern = rf"\b{re.escape(word)}\b"
            if not re.search(pattern, text, flags=re.IGNORECASE):
                continue

            _filter = await dB.get_var(message.chat.id, word, "FILTER")
            data_type, file_id = _filter["type"], _filter.get("file_id")
            data = _filter["result"]
            if data_type != "text" and not file_id:
                continue
            teks, button = Button.parse_msg_buttons(data)
            teks_formated = await Tools.escape_filter(message, teks, Tools.parse_words)
            if button:
                reply_markup = await Button.create_inline_keyboard(button)
                if data_type == "text":
                    await message.reply(
                        teks_formated,
                        reply_markup=reply_markup,
                        disable_web_page_preview=True,
                        parse_mode=enums.ParseMode.HTML,
                    )
                else:
                    reply_senders = {
                        "photo": message.reply_photo,
                        "voice": message.reply_voice,
                        "audio": message.reply_audio,
                        "video": message.reply_video,
                        "animation": message.reply_animation,
                        "document": message.reply_document,
                        "sticker": message.reply_sticker,
                        "video_note": message.reply_video_note,
                    }
                    kwargs = {"reply_to_message_id": message.id}
                    if data_type not in ["sticker", "video_note"]:
                        kwargs["caption"] = teks_formated
                        kwargs["parse_mode"] = enums.ParseMode.HTML

                    await reply_senders[data_type](file_id, **kwargs)
            else:
                if data_type == "text":
                    await message.reply(
                        teks_formated,
                        reply_markup=reply_markup,
                        disable_web_page_preview=True,
                        parse_mode=enums.ParseMode.HTML,
                    )
                else:
                    reply_senders = {
                        "photo": message.reply_photo,
                        "voice": message.reply_voice,
                        "audio": message.reply_audio,
                        "video": message.reply_video,
                        "animation": message.reply_animation,
                        "document": message.reply_document,
                        "sticker": message.reply_sticker,
                        "video_note": message.reply_video_note,
                    }
                    
                    kwargs = {"reply_to_message_id": message.id}
                    if data_type not in ["sticker", "video_note"]:
                        kwargs["caption"] = teks_formated
                        kwargs["parse_mode"] = enums.ParseMode.HTML

                    await reply_senders[data_type](file_id, **kwargs)
    except Exception:
        LOGGER.error(
            f"Eror filter pada pesan: {message.text}\n{traceback.format_exc()}"
        )


__MODULE__ = "Filters"
__HELP__ = """
<blockquote expandable>
**You can active auto reply message from this command**
    /savefilter (name) (reply message)

**View all saved filters message from your account** 
    /filters

**You can get the filter format from this command**
    /getfilter (name) raw

**You can stop filters message on chat if you want**
    /stopfilter (name)

**This command easy to delete all saved filters messages**
    /stopfilter all </blockquote>
"""
