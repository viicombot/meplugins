import traceback
import config

from pyrogram import filters
from core import app
from utils.functions import Tools, update_user_data
from utils.decorators import Checklimit
from logs import LOGGER
from utils import pastebin


__MODULE__ = "Deepseek AI"

__HELP__ = """
<blockquote expandable>

🧠 <b>Ask Deepseek AI</b>

• <b>/deepseek</b> (question) – Ask questions and get answers from Deepseek AI.

</blockquote>
"""



@app.on_message(filters.command(["deepseek"]) & ~config.BANNED_USERS)
@Checklimit("deepseekquery")
async def deepseek_cmd(client, message):
    proses = await message.reply(">**Proses your request...**")
    prompt = client.get_text(message)
    if not prompt:
        return await proses.edit(f">**Please give a prompt or reply with an image and prompt.**")
    chat_id = message.chat.id
    try:
        headers = {"mg-apikey": config.API_MAELYN}
        params = {
            "q": prompt,
            "roleplay": "Kamu adalah asisten paling canggih yang berbahasa Indonesia gaul, dan jangan gunakan bahasa inggris sebelum saya memulai duluan",
            "uuid": chat_id,
        }
        url = "https://api.maelyn.sbs/api/deepseek/chat"
        r = await Tools.fetch.get(url, headers=headers, params=params)
        if r.status_code != 200:
            return await proses.edit(">**Please try again later, maybe server is down.**")
        result = r.json()["result"].get("content")
        if len(result) > 4096:
            link = await pastebin.paste(result)
            await update_user_data(client, message.from_user.id, "deepseekquery", True)
            return await proses.edit(f"<b><u>Chat with DeepSeek</u></b>\n<b>Question:\n<blockquote>{prompt}</blockquote>\n\nAnswer:\n</b>{link}", disable_web_page_preview=True)
        else:
            if len(result) > 496:
                caption = f"<blockquote expandable>{result}</blockquote>"
            else:
                caption = f"<blockquote>{result}</blockquote>"
                await update_user_data(client, message.from_user.id, "deepseekquery", True)
            return await proses.edit(f"<b><u>Chat with DeepSeek</u></b>\n<b>Question:\n<blockquote>{prompt}</blockquote>\n\nAnswer:\n</b>{caption}")
    except Exception:
        LOGGER.error(traceback.format_exc())
        return await proses.edit(">**Please try again later, maybe server is down.**")
