import requests
import os
import config

from core import app
from utils.functions import Tools

from pyrogram import filters

__MODULE__ = "OCR"
__HELP__ = """
<blockquote expandable>
<b>🖼️ Optical Character Recognition</b>

<b>★ /ocr</b> (reply image/sticker/gif)  
Extracts text from an image, sticker, or animation.

Just reply to a media message and use this command to get the text content.
</blockquote>
"""



@app.on_message(filters.command(["ocr"]) & ~config.BANNED_USERS)
async def ocr_cmd(_, message):
    reply = message.reply_to_message
    if not reply or not reply.photo and not reply.sticker and not reply.animation:
        return await message.reply_text(
            f">`{message.text.split()[0]}` **reply to media!**"
        )
    proses = await message.reply(">**Please wait...**")
    try:
        path = await reply.download()
        data = {"type": "file", "action": "upload"}
        files = {"source": (path, open(path, "rb"), "images/jpeg")}
        headers = {"origin": "https://imgbb.com", "referer": "https://imgbb.com/upload", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42"}
        res = await Tools.fetch.post("https://imgbb.com/json", files=files, data=data, headers=headers)
        os.remove(path)
        url = f"https://ibb.co.com/{res.json()['image']['id_encoded']}"
        req = requests.get(
            f"https://script.google.com/macros/s/AKfycbwURISN0wjazeJTMHTPAtxkrZTWTpsWIef5kxqVGoXqnrzdLdIQIfLO7jsR5OQ5GO16/exec?url={url}"
        ).json()
        return await proses.edit(f"><code>{req['text']}</code>")
    except Exception as e:
        return await proses.edit(f">**ERROR:** {str(e)}")