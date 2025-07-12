



import config

from pyrogram import enums, filters

from core import app
from utils.functions import Tools
from utils.keyboard import Button


@app.on_message(filters.command(["buttons", "button"]) & ~config.BANNED_USERS)
async def make_buttons(_, message):
    if not message.reply_to_message:
        return await message.reply(">**Please reply to message with formatted buttons.**")
    reply = message.reply_to_message
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    original_text = reply.text or reply.caption
    if reply.media and reply.media != enums.MessageMediaType.WEB_PAGE_PREVIEW:
        media = Tools.get_file_id(reply)
        type = media["message_type"]
        file_id = media["file_id"]
    else:
        type = "text"
    main_text, button = Button.parse_msg_buttons(original_text)
    formatted_text = await Tools.escape_filter(message, main_text, Tools.parse_words)
    if button:
        button = await Button.create_inline_keyboard(button, user_id)
    else:
        button = None
    if type == "text":
        return await message.reply(formatted_text, reply_markup=button)
    else:
        type_mapping = {
            "photo": message.reply_photo,
            "voice": message.reply_voice,
            "audio": message.reply_audio,
            "video": message.reply_video,
            "animation": message.reply_animation,
            "document": message.reply_document,
            "sticker": message.reply_sticker,
            "video_note": message.reply_video_note,
        }
        kwargs = {"reply_to_message_id": message.id, "reply_markup": button}
        if type not in ["sticker", "video_note"]:
            kwargs["caption"] = formatted_text
            kwargs["parse_mode"] = enums.ParseMode.HTML
        return await type_mapping[type](file_id, **kwargs)
    

__MODULE__ = "Buttons"
__HELP__ = """
<blockquote expandable>
**Generate buttons from text**  
<b>★ /buttons</b> (reply to message)  

<i>Supports markdown & custom response formatting.</i>

Bot akan otomatis membalas dengan tombol inline di bawah pesan yang sesuai.

✅ Bisa digunakan untuk media (photo, video, file, dll).  
</blockquote>
"""
