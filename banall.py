import config
import asyncio

from core import app
from pyrogram import filters, errors, enums
from pyrogram.helpers import ikb

banned_task = {}


@app.on_message(filters.command("banall") & filters.user(config.OWNER_ID) & ~filters.via_bot)
async def exec_banall(client, message):
    if len(message.command) < 2:
        return await message.reply("🔺 **Please provide the chat ID.**")

    chat_id = message.command[1]
    try:
        chat_id = int(chat_id)
    except ValueError:
        return await message.reply("❌ **Invalid chat ID. Must be a number like -100xxxxxxxxxx.**")

    try:
        privileges = (await client.get_chat_member(chat_id, client.me.id)).privileges
        if not privileges or not privileges.can_restrict_members:
            return await message.reply("🔒 **I need ban permissions to perform this operation.**")

        total_members = (await client.get_chat(chat_id)).members_count
    except Exception as e:
        return await message.reply(f"⚠️ **Error:** `{e}`")

    msg = await message.reply(
        f"🚀 **Starting mass ban...**\nChat ID: `{chat_id}`\nEstimated members: `{total_members}`",
        reply_markup=ikb([[("🚫 Cancel Ban", f"BanallCancel:{chat_id}")]])
    )

    async def banall_members():
        banned = 0
        try:
            async for member in client.get_chat_members(chat_id):
                if member.user.id == client.me.id:
                    continue
                if member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                    continue
                try:
                    await client.ban_chat_member(chat_id, member.user.id)
                    banned += 1
                    await asyncio.sleep(0.5)
                except errors.FloodWait as e:
                    await asyncio.sleep(e.value)
                    await client.ban_chat_member(chat_id, member.user.id)
                    banned += 1
                except errors.UserAdminInvalid:
                    continue
                except Exception as e:
                    print(f"[ERROR] Ban {member.user.id}: {e}")
                    continue
            await msg.edit(f"✅ **Finished banning members.**\nTotal banned: `{banned}`")
        except asyncio.CancelledError:
            await msg.edit(f"❎ **Banall cancelled.**\nTotal banned: `{banned}`")
        finally:
            banned_task.pop(chat_id, None)

    banned_task[chat_id] = asyncio.create_task(banall_members())


@app.on_callback_query(filters.regex("^BanallCancel"))
async def cancel_banall(_, callback):
    try:
        chat_id = int(callback.data.split(":")[1])
    except:
        return await callback.answer("❌ Invalid Chat ID", show_alert=True)

    task = banned_task.get(chat_id)
    if isinstance(task, asyncio.Task) and not task.done():
        task.cancel()
        await callback.answer("🛑 Banall task cancelled.", show_alert=True)
    else:
        await callback.answer("⚠️ No active banall task for this chat.", show_alert=True)
