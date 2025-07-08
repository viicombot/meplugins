import asyncio
import random
import config


from core import app, userbot
from pyrogram import filters, raw
from utils.query_group import sangmata_group
from utils.database import dB
from utils.decorators import ONLY_ADMIN, ONLY_GROUP

@app.on_message(
    filters.group & ~filters.bot & ~filters.via_bot,
    group=sangmata_group,
)
async def sang_mata(client, message):
    if message.sender_chat or await dB.get_var(message.chat.id, "SICEPU"):
        return
    if not await dB.cek_userdata(message.from_user.id):
        return await dB.add_userdata(
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.last_name,
            message.from_user.username,
        )
    _, usernamebefore, first_name, lastname_before = await dB.get_userdata(message.from_user.id)
    msg = ""
    if (
        usernamebefore != message.from_user.username
        or first_name != message.from_user.first_name
        or lastname_before != message.from_user.last_name
    ):
        msg += f"<b>👀 {client.mention} SangMata\n\nPengguna : {message.from_user.mention} [<code>{message.from_user.id}</code>]</b>\n"
    if usernamebefore != message.from_user.username:
        usernamebefore = f"@{usernamebefore}" if usernamebefore else "<b>Tanpa Username</b>\n"
        usernameafter = (
            f"@{message.from_user.username}" if message.from_user.username else "<b>Tanpa Username</b>\n"
        )
        msg += f"<b>Mengubah username dari <code>{usernamebefore}</code> ke <code>{usernameafter}</code></b>.\n"
        await dB.add_userdata(
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.last_name,
            message.from_user.username,
        )
    if first_name != message.from_user.first_name:
        msg += f"<b>Mengubah nama depan dari <code>{first_name}</code> menjadi <code>{message.from_user.first_name}</code>.</b>\n"
        await dB.add_userdata(
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.last_name,
            message.from_user.username,
        )
    if lastname_before != message.from_user.last_name:
        lastname_before = lastname_before or "<b>Tanpa Nama Belakang</b>\n"
        lastname_after = message.from_user.last_name or "<b>Tanpa Nama Belakang</b>\n"
        msg += f"<b>Mengubah nama belakang dari <code>{lastname_before}</code> menjadi <code>{lastname_after}</code>.</b>\n"
        await dB.add_userdata(
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.last_name,
            message.from_user.username,
        )
    if msg != "":
        await message.reply_text(msg, quote=True)


@app.on_message(filters.command("sangmata") & ~filters.bot & ~filters.via_bot)
@ONLY_ADMIN
@ONLY_GROUP
async def sangmata_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("><b>Gunakan format <code>/sangmata on</code>, untuk mengaktifkan sangmata.\nJika Anda ingin menonaktifkan, Anda dapat menggunakan perintah <code>/sangmata off</code>.</b>")
    state = message.command[1].lower()
    if state not in ["on", "off"]:
        return await message.reply_text("><b>Gunakan format <code>/sangmata on</code>, untuk mengaktifkan sangmata.\nJika Anda ingin menonaktifkan, Anda dapat menggunakan perintah <code>/sangmata off</code>.</b>")
    if state == "on":
        if not await dB.get_var(message.chat.id, "SICEPU"):
            return await message.reply_text(">**Sangmata sudah diaktifkan**")
        else:
            await dB.remove_var(message.chat.id, "SICEPU")
            return await message.reply_text(">**Sangmata berhasil diaktifkan.**")
    else:
        if await dB.get_var(message.chat.id, "SICEPU"):
            return await message.reply_text(">**Sangmata sudah dinonaktifkan**")
        else:
            await dB.set_var(message.chat.id, "SICEPU", False)
            return await message.reply_text(">**Sangmata berhasil dinonaktifkan.**")


@app.on_message(filters.command(["sg"]) & ~config.BANNED_USERS)
async def history(client, message):
    reply = message.reply_to_message
    try:
        target = reply.from_user.id if reply else message.text.split()[1]
    except (AttributeError, IndexError):
        return await message.reply(">**Balas pesan pengguna atau berikan username pengguna.**")
    try:
        user_id = (await client.get_users(target)).id
    except Exception:
        user_id = int(message.command[1])
    proses = await message.reply(">**Please wait...**")
    bot = ["@Sangmata_bot", "@SangMata_beta_bot"]
    babu = userbot.clients[0]
    getbot = random.choice(bot)
    await babu.unblock_user(getbot)
    txt = await babu.send_message(getbot, user_id)
    await asyncio.sleep(4)
    await txt.delete()
    await proses.delete()
    async for name in babu.search_messages(getbot, limit=2):
        if not name.text:
            await message.reply(f"<b>❌ {getbot} ERROR, Silahkan kirim manual id pengguna ke {''.join(bot)}!</b>")
        else:
            await message.reply(name.text)
    user_info = await babu.resolve_peer(getbot)
    return await babu.invoke(raw.functions.messagesDeleteHistory(peer=user_info, max_id=0, revoke=True))


__MODULE__ = "SangMata"
__HELP__ = """
<blockquote expandable>
**Get notification if user changed name on group** 
    <b>★ /sangmata</b> [on/off]

**You can get history name user** 
    <b>★ /sg</b> (userID/reply user)</blockquote>
"""
