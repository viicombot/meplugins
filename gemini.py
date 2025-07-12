import traceback
import config

from pyrogram import filters
from core import app
from utils.functions import Tools, update_user_data
from utils.decorators import Checklimit
from logs import LOGGER

GEMINI_CHAT_URL = "https://api.maelyn.sbs/api/gemini/chat"
GEMINI_IMAGE_URL = "https://api.maelyn.sbs/api/gemini/image"
GEMINI_VIDEO_URL = "https://api.maelyn.sbs/api/gemini/video"

__MODULE__ = "Gemini"

__HELP__ = """
<blockquote expandable>

🧠 <b>Gemini Assistant</b>

• <b>/gemini</b> (question) – Ask any question and get answers.  
• <b>/gemini</b> (reply photo) (question) – Ask based on a photo.  
• <b>/gemini</b> (reply video) (prompt) – Ask based on a video.

</blockquote>
"""


@app.on_message(filters.command(["gemini"]) & ~config.BANNED_USERS)
@Checklimit("geminiquery")
async def gemini_cmd(client, message):
    proses = await message.reply(">**Proses your request...**")
    if len(message.command) < 2:
        return await proses.edit(">**Please give a question or reply with an image and question.**")
    prompt = client.get_text(message)

    try:
        headers = {"mg-apikey": config.API_MAELYN}

        if message.reply_to_message and message.reply_to_message.photo:
            if len(message.command) < 2:
                return await proses.edit(
                    ">**Please provide a question to analyze the image.**"
                )
            photo_url = await Tools.upload_media(message)

            params = {"url": photo_url, "q": prompt}
            r = await Tools.fetch.get(GEMINI_IMAGE_URL, headers=headers, params=params)
            if r.status_code != 200:
                return await proses.edit(">**Please try again later, maybe server is down.**")
            data = r.json()
            await update_user_data(client, message.from_user.id, "geminiquery", True)
            return await proses.edit(data.get("result"))
        elif message.reply_to_message and (
            message.reply_to_message.video,
            message.reply_to_message.animation,
        ):
            if len(message.command) < 2:
                return await proses.edit(
                    f">**Please provide a question to analyze the image.**"
                )
            video_url = await Tools.upload_media(message)

            params = {"url": video_url, "q": prompt}
            r = await Tools.fetch.get(GEMINI_VIDEO_URL, headers=headers, params=params)
            if r.status_code != 200:
                return await proses.edit(">**Please try again later, maybe server is down.**")
            data = r.json()
            await update_user_data(client, message.from_user.id, "geminiquery", True)
            return await proses.edit(data.get("result"))

        else:
            params = {"q": prompt}
            r = await Tools.fetch.get(GEMINI_CHAT_URL, headers=headers, params=params)
            if r.status_code != 200:
                return await proses.edit(">**Please try again later, maybe server is down.**")
            data = r.json()
            await update_user_data(client, message.from_user.id, "geminiquery", True)
            return await proses.edit(data.get("result"))

    except Exception as e:
        LOGGER.error(traceback.format_exc())
        return await proses.edit(f">**Terjadi kesalahan:**\n`{str(e)}`")
