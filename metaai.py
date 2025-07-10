

import traceback
import config

from uuid import uuid4
from pyrogram.types import InputMediaAnimation, InputMediaPhoto
from core import app
from pyrogram import filters
from utils.functions import Tools, Sosmed, update_user_data
from utils.decorators import Checklimit
from logs import LOGGER

META_AI_CHAT_URL = "https://api.maelyn.sbs/api/metaai/chat"
META_AI_IMAGINE_URL = "https://api.maelyn.sbs/api/metaai/art"

__MODULE__ = "Meta-AI"
__HELP__ = """
<blockquote expandable>
<b>🧠 Meta AI Assistant</b>

<b>★ /metaai</b> (question) – Ask a question to Meta AI.  
<b>★ /metaai generate</b> (prompt) – Generate images using Meta AI.
</blockquote>
"""



@app.on_message(filters.command(["metaai"]) & ~config.BANNED_USERS)
@Checklimit("metaaiquery")
async def metaai_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply(">**Please give a prompt or question.**")
    proses = await message.reply(">**Proses your request...**")
    prompt = client.get_text(message)
    try:
        foto, video = 0, 0
        err = ""
        headers = {"mg-apikey": config.API_MAELYN}

        if prompt.lower().startswith("generate "):
            if len(message.command) < 3:
                return await proses.edit(
                    f">**Please reply to a message prompt or give the prompt!\nExample: `{message.text.split()[0]} cute cats`**"
                )
            prompt = prompt[9:].strip()
            params = {"prompt": prompt}
            r = await Tools.fetch.get(
                META_AI_IMAGINE_URL, headers=headers, params=params
            )
            data = r.json()
            results = data.get("result", [])
            if not results:
                return await proses.edit(">**No media found.**")
            await proses.edit(f">**Preparing media for sending...**")
            photo_group = []
            video_group = []

            for item in results:
                photo_url = item.get("ImageUrl")
                video_url = item.get("VideoUrl")

                if photo_url:
                    _photo = await Tools.get_media_data(photo_url, "jpg")
                    if _photo and _photo.getbuffer().nbytes > 0:
                        _photo.name = f"{uuid4()}.jpg"
                        photo_group.append(InputMediaPhoto(media=_photo))
                        foto += 1

                if video_url:
                    _video = await Tools.get_media_data(video_url, "mp4")
                    if _video and _video.getbuffer().nbytes > 0:
                        _video.name = f"{uuid4()}.mp4"
                        video_group.append(InputMediaAnimation(media=_video))
                        video += 1
            if photo_group:
                photo_chunks = Sosmed.chunk_media_group(photo_group)
                for i, chunk in enumerate(photo_chunks, 1):
                    try:
                        await client.send_media_group(
                            chat_id=message.chat.id, media=chunk
                        )
                    except Exception as e:
                        err += f"Error sending photo chunk {i}: {str(e)}\n"
            if video_group:
                for i, animation in enumerate(video_group, 1):
                    try:
                        await client.send_animation(
                            chat_id=message.chat.id,
                            animation=animation.media,
                        )
                    except Exception as e:
                        err += f"Error sending video {i}: {str(e)}\n"

            if not photo_group and not video_group:
                return await proses.edit(">**No media found.**")
            await update_user_data(client, message.from_user.id, "metaaiquery", True)
            await proses.delete()
            return await message.reply(
                f">**Successfully sent {foto + video} media**\n📸 Photos: `{foto}` | 🎥 Videos: `{video}`\n{err}"
            )

        else:
            params = {"q": prompt}
            r = await Tools.fetch.get(META_AI_CHAT_URL, headers=headers, params=params)
            if r.status_code != 200:
                return await message.reply(">**Please try again later, maybe server is down.**")
            data = r.json()
            await update_user_data(client, message.from_user.id, "metaaiquery", True)
            await proses.delete()
            return await message.reply(data.get("result"))

    except Exception as e:
        LOGGER.error(traceback.format_exc())
        return await proses.edit(f">**Terjadi kesalahan:**\n`{e}`")
