


import os
import config
import asyncio

from core import app
from pyrogram import filters, errors, types, enums

from utils.decorators import ONLY_GROUP, ONLY_ADMIN

__MODULE__ = "Zombies"
__HELP__ = """
<blockquote expandable>
<b>💀 Zombie Cleaner</b>

<b>★ /zombies</b> or <b>/zombie</b> - Scan and ban all deleted accounts (zombie users) from the group.

<i>Only group admins can run this command.</i>
</blockquote>
"""


@app.on_message(filters.command(["zombies", "zombie"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def zombies_cmd(client, message):
    chat_id = message.chat.id
    deleted_users = []
    banned_users = 0
    failed = 0
    mt = await message.reply(">**Please wait...**")

    async for i in client.get_chat_members(chat_id):
        if i.user.is_deleted:
            deleted_users.append(i.user.id)
    if len(deleted_users) > 0:
        for deleted_user in deleted_users:
            try:
                await message.chat.ban_member(deleted_user)
                banned_users += 1
            except errors.FloodWait as e:
                await asyncio.sleep(e.value)
                await mt.edit(f">**FloodWait waiting for `{e.value}` seconds!**")
            except Exception:
                failed += 1
        return await mt.edit(f">**Succesfuly banned deleted account: `{banned_users}`, failed: `{failed}`")
    else:
        return await mt.edit(">**No deleted accounts here!**")
    
