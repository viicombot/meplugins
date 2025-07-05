

from core import app
from utils import pastebin
from utils.deleter import Deleter, VerifyAnkes
from utils.decorators import ONLY_GROUP, ONLY_ADMIN
from utils.database import dB
from .query_group import ankes_group
from config import BANNED_USERS
from utils.misc import SUDOERS

from pyrogram import filters, enums, errors



@app.on_message(filters.command(["protect", "antigacst"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def ankestools(_, message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        return await message.reply(">**Gunakan format `/protect [on/off]`**")
    jk = message.command[1]
    status = await dB.get_var(chat_id, "PROTECT")
    if jk.lower() in ["On", "on"]:
        if status:
            return await message.reply(">**Protect sudah diaktifkan**")
        await dB.set_var(chat_id, "PROTECT", jk)
        return await message.reply(f">**Berhasil mengatur protect menjadi {jk}.**")
    elif jk in ["Off", "off"]:
        if status is None:
            return await message.reply(">**Protect belum aktif**")
        await dB.remove_var(chat_id, "PROTECT")
        return await message.reply(f">**Berhasil mengatur protect menjadi {jk}.**")
    else:
        return await message.reply(f">**{jk} Format salah, Gunakan `/protect [on/off]`.**")
    

@app.on_message(filters.command(["clearfree", "clearapproved"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def clear_approved(_, message):
    chat_id = message.chat.id
    users = await dB.get_list_from_var(chat_id, "APPROVED_USERS")
    for user in users:
        await dB.remove_from_var(chat_id, "APPROVED_USERS", user)
    return await message.reply(">**Berhasil menghapus semua pengguna approved.**")

@app.on_message(filters.command(["clearblack"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def clear_blackuser(_, message):
    chat_id = message.chat.id
    cekpre = await dB.get_list_from_var(chat_id, "SILENT_USER")
    for pre in cekpre:
        await dB.remove_from_var(chat_id, "SILENT_USER", pre)
    return await message.reply(">**Berhasil menghapus list black pengguna.**")

@app.on_message(filters.command(["free", "approve", "addwhite"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def add_approve(client, message):
    reply = message.reply_to_message
    chat_id = message.chat.id
    if reply.sender_chat:
        return await message.reply(">**Gunakan perintah ini dengan membalas pesan pengguna!! Bukan akun anonymous.**")
    try:
        target = reply.from_user.id if reply else message.text.split()[1]
    except (AttributeError, IndexError):
        return await message.reply(">**Balas pesan pengguna atau berikan username pengguna.**")
    try:
        user = await client.get_users(target)
    except (errors.PeerIdInvalid, KeyError, errors.UsernameInvalid, errors.UsernameNotOccupied):
        return await message.reply(">**Silahkan berikan id pengguna yang valid!!**")
    ids = user.id
    if ids in SUDOERS:
        return await message.reply(">**Pengguna adalah SUDOERS bot!!**")
    freedom = await dB.get_list_from_var(chat_id, "APPROVED_USERS")
    if ids in freedom:
        return await message.reply_text(">**Pengguna sudah disetujui.**")
    await dB.add_to_var(chat_id, "APPROVED_USERS", ids)
    return await message.reply(f">**Pengguna: {user.mention} telah disetujui tidak akan terkena antigcast.")


@app.on_message(filters.command(["unfree", "unapprove", "delwhite"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def un_approve(client, message):
    reply = message.reply_to_message
    chat_id = message.chat.id
    if reply.sender_chat:
        return await message.reply(">**Gunakan perintah ini dengan membalas pesan pengguna!! Bukan akun anonymous.**")
    try:
        target = reply.from_user.id if reply else message.text.split()[1]
    except (AttributeError, IndexError):
        return await message.reply(
            ">**Balas pesan pengguna atau berikan username pengguna.**"
        )
    try:
        user = await client.get_users(target)
    except (errors.PeerIdInvalid, KeyError, errors.UsernameInvalid, errors.UsernameNotOccupied):
        return await message.reply(">**Silahkan berikan id pengguna yang valid!!**")
    ids = user.id
    freedom = await dB.get_list_from_var(chat_id, "APPROVED_USERS")
    if ids not in freedom:
        return await message.reply_text(">**Pengguna memang belum disetujui.**")
    else:
        await dB.remove_from_var(chat_id, "APPROVED_USERS", ids)
        return await message.reply(f">**Pengguna: {user.mention} telah dihapus dari daftar approved.**")

@app.on_message(filters.command(["listwhite", "approved"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def listapproved(_, message):
    chat_id = message.chat.id
    approved = await dB.get_list_from_var(chat_id, "APPROVED_USERS")
    if len(approved) == 0:
        return await message.reply(">**Belum ada pengguna yang disetujui.**")
    msg = f"<blockquote expandable>**Pengguna Approved Di {message.chat.title}:**\n\n"
    for count, user in enumerate(approved, 1):
        msg += f"**•**{count} -> {user}\n"
    msg += "</blockquote>"
    try:
        return await message.reply(msg)
    except errors.MessageTooLong:
        link = await pastebin.paste(msg)
        return await message.reply(link, disable_web_page_preview=True)

@app.on_message(filters.command(["listblack"]) & ~BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def listblack(_, message):
    chat_id = message.chat.id
    blacklist = await dB.get_list_from_var(chat_id, "SILENT_USER")
    if len(blacklist) == 0:
        return await message.reply(">**Belum ada pengguna yang diblacklist.**")
    msg = f"Pengguna Blackist Di {message.chat.title}:\n\n"
    for count, org in enumerate(cekpre, 1):
        msg += f"**•**{count} -> {org}\n"
    if cekpre == []:
        return await message.reply("Tidak ada pengguna!!")
    else:
        try:
            return await message.reply(msg)
        except MessageTooLong:
            with io.BytesIO(str.encode(msg)) as out_file:
                out_file.name = "blacklist-user.txt"
                return await message.reply_document(document=out_file)


@CMD.BOT("addblack", FILTERS.GROUP_ADMIN)
@CMD.EXPIRED
@ONLY_ADMIN
async def _(client, message):
    reply = message.reply_to_message
    chat_id = message.chat.id
    if message.chat.type == enums.ChatType.PRIVATE:
        return await message.reply("**Silahkan gunakan perintah ini didalam grup.**")
    try:
        target = reply.from_user.id if reply else message.text.split()[1]
    except (AttributeError, IndexError):
        return await message.reply(
            "Balas pesan pengguna atau berikan username pengguna."
        )
    try:
        user = await client.get_users(target)
    except (PeerIdInvalid, KeyError, UsernameInvalid, UsernameNotOccupied):
        return await message.reply("Silahkan berikan id pengguna!!")
    ids = user.id
    if ids in ADMIN_IDS:
        return await message.reply("Pengguna adalah owner!!")
    dicekah = await dB.get_list_from_var(chat_id, "SILENT_USER")
    if ids in dicekah:
        return await message.reply_text("User already blacklist.")
    else:
        await dB.add_to_var(chat_id, "SILENT_USER", ids)
        return await message.reply(f"User : {ids} added to blacklist.")


@CMD.BOT("remblack", FILTERS.GROUP_ADMIN)
@CMD.EXPIRED
@ONLY_ADMIN
async def _(client, message):
    reply = message.reply_to_message
    chat_id = message.chat.id
    if message.chat.type == enums.ChatType.PRIVATE:
        return await message.reply("**Silahkan gunakan perintah ini didalam grup.**")
    try:
        target = reply.from_user.id if reply else message.text.split()[1]
    except (AttributeError, IndexError):
        return await message.reply(
            "Balas pesan pengguna atau berikan username pengguna."
        )
    try:
        user = await client.get_users(target)
    except (PeerIdInvalid, KeyError, UsernameInvalid, UsernameNotOccupied):
        return await message.reply("Silahkan berikan id pengguna!!")
    ids = user.id
    if ids in ADMIN_IDS:
        return await message.reply("Pengguna adalah owner!!")
    dicekah = await dB.get_list_from_var(chat_id, "SILENT_USER")
    if ids in dicekah:
        await dB.remove_from_var(chat_id, "SILENT_USER", ids)
        return await message.reply(f"User : {ids} deleted from blacklist.")
    else:
        return await message.reply_text("User not in blacklist.")
