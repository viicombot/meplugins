

__MODULE__ = "Pinterest"
__HELP__ = """
<blockquote expandable>
<b>📥 Pinterest Downloader</b>

<b>★ /pinterest</b> (query) – Search media from pinterest.</blockquote>
"""


import traceback
import config

from uuid import uuid4
from pyrogram import filters
from core import app
from utils.functions import Tools, update_user_data
from pyrogram.helpers import ikb
from utils.decorators import Checklimit
from utils.database import state


@app.on_message(filters.command(["pinterest"]) & ~config.BANNED_USERS)
@Checklimit("pinterestquery")
async def blackbox_cmd(client, message):
    proses = await message.reply(">**Proses your request...**")
    if len(message.command) < 2:
        return await proses.edit(">**Please give a query.\nExample: /pinterest kucing lucu.**")
    user_id = message.from_user.id
    prompt = client.get_text(message)
    url = f"https://api.betabotz.eu.org/api/search/pinterest?text1={prompt}&apikey={config.API_BOTCHAX}"
    response = await Tools.fetch.get(url)
    if response.status_code != 200:
        return await proses.edit(">**Please try again later, maybe server is down.**")
    data = response.json()
    uniq = f"{str(uuid4())}"
    uniq = uniq.split("-")[0]
    if len(data["result"]) == 0:
        buttons = ikb([[("❌ Close", "close")]])
        return await proses.edit(f">**Try another word, no data found `{prompt}`**", reply_markup=buttons)
    state.set(uniq, "pinterest", data["result"])
    await update_user_data(client, user_id, "pinterestquery", True)
    buttons = ikb([[("➡️ Next", f"nextpinterest_1_{uniq}")]])
    return await message.reply_photo(data["result"][0], reply_markup=buttons)
    