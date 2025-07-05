
import traceback
from pyrogram import filters
from core import app
from utils.functions import Sosmed
import config
from logs import LOGGER


@app.on_message(filters.command(["dl", "download"]) & ~config.BANNED_USERS)
async def downloader_cmd(client, message):
    arg = client.get_text(message)
    if not arg:
        return await message.reply(
            f"<b>Please give a link!\nExample: `{message.text.split()[0]} https://x.com/eskacangkhu/status/1921732123213398212?t=72ASOxnYYvYCltwOHzuXrw&s=19`</b>"
        )
    if not arg.startswith("https"):
        return await message.reply("><b>Only link supported.</b>")
    if message.sender_chat:
        return await message.reply(">**Dont use anonymous account.**")
    proses = await message.reply(">**Getting request url...**")
    await proses.edit(">**Wait a minute this takes some time...**")

    try:
        # INSTAGRAM
        if "instagram.com" in arg:
            await proses.edit(">**Detected Instagram link...**")
            return await Sosmed.instadl_cmd(client, message, proses, arg)

        # PINTEREST
        elif "pin.it" in arg or "id.pinterest" in arg:
            await proses.edit(f">**Detected Pinterest link...**")
            return await Sosmed.pindl_cmd(client, message, proses, arg)

        # TWITTER
        elif "x.com" in arg or "twitter.com" in arg:
            await proses.edit(f">**Detected Twitter link...**")
            return await Sosmed.twitter_cmd(client, message, proses, arg)

        # TELEGRAM
        elif "t.me" in arg:
            await proses.edit(f">**Detected Telegram link...**")
            return await Sosmed.teledl_cmd(client, message, proses, arg)

        # TIKTOK
        elif "tiktok.com" in arg or "vt.tiktok.com" in arg:
            await proses.edit(f">**Detected TikTok link...**")
            return await Sosmed.ttdl_cmd(client, message, proses, arg)

        # SPOTIFY
        elif "spotify.com" in arg:
            await proses.edit(f">**Detected Spotify link...**")
            return await Sosmed.spotdl_cmd(client, message, proses, arg)

        # YOUTUBE
        elif "youtube.com" in arg or "youtu.be" in arg:
            await proses.edit(f">**Detected YouTube link...**")
            return await Sosmed.ytvideo_cmd(client, message, proses, arg)

        elif "threads.com" in arg or "threads" in arg:
            await proses.edit(f"**Detected YouTube link...**")
            return await Sosmed.thread_cmd(client, message, proses, arg)

        else:
            return await proses.edit(
                f"**Unsupported link detected! Only support:**\n• Instagram\n• TikTok\n• Spotify\n• YouTube"
            )

    except Exception as er:
        LOGGER.error(f"sosmeddl: {traceback.format_exc()}")
        return await proses.edit(f"**An error occurred:** `{str(er)}`")
    

__MODULE__ = "Downloader"
__HELP__ = """
<blockquote expandable>

**You can download any media from sosial media link**
    <b>★ /dl</b> (url)

**Supported links**:
    - instagram
    - pinterest
    - twitter
    - tiktok
    - spotify
    - threads
    - youtube</blockquote>
"""
