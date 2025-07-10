
import config
import asyncio

from core import app
from pyrogram import filters, errors, types, enums
from pyrogram.helpers import ikb

from utils.decorators import ONLY_GROUP, ONLY_ADMIN
from utils.misc import SUDOERS

__MODULE__ = "Moderation"
__HELP__ = """
<blockquote expandable>

🔨 <b>Moderation Commands</b>

• <b>/ban [user]</b>  
Ban a user. Can be used by replying to a message or by specifying user ID/username.

• <b>/delban [user]</b>  
Ban the user and delete the command + replied message.

• <b>/unban [user]</b>  
Unban a user manually.

• <b>/kick [user]</b>  
Kick a user (banned & unbanned instantly).

• <b>/delkick [user]</b>  
Kick and delete the messages involved (cleaner version).

• <b>/mute [user]</b>  
Mute a user (restrict all permissions).

• <b>/delmute [user]</b>  
Mute and delete the messages involved.

• <b>/unmute [user]</b>  
Unmute a previously muted user.

📣 <b>/report</b>  
Report a user to group admins. Use it by replying to someone's message.

</blockquote>
"""


async def admin_check(message, user_id):
    c = message._client
    status = (await c.get_chat_member(message.chat.id, user_id)).status
    admins = [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    if status not in admins:
        return False
    return True


async def member_check(message, user_id):
    client = message._client
    check_user = (await client.get_chat_member(message.chat.id, user_id)).privileges
    user_type = check_user.status
    if user_type == enums.ChatMemberStatus.MEMBER:
        return False
    if user_type == enums.ChatMemberStatus.ADMINISTRATORS:
        add_adminperm = check_user.can_promote_members
        return bool(add_adminperm)
    return True


@app.on_message(filters.command(["kick", "delkick"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def kick_cmd(client, message):
    reply = message.reply_to_message
    if reply and reply.sender_chat:
        return await message.reply(">**Please reply userID not anonymous account.**")
    try:
        target = reply.from_user.id if reply else message.text.split()[1].strip()
    except (AttributeError, IndexError):
        return await message.reply("><b>You need to specify a user (either by reply or username/ID)!</b>")

    try:
        user = await client.get_users(target)
    except (errors.PeerIdInvalid, KeyError, errors.UsernameInvalid, errors.UsernameNotOccupied, IndexError):
        return await message.reply("><b>User invalid!!</b>")

    mention = user.mention
    user_id = user.id
    if user_id == client.me.id or user_id in SUDOERS:
        return await message.reply_text(f"><b>Go to the heal now!!</b>")
    msg = f"><b>Kicked user {mention}</b>"
    if message.command[0][0] == "d":
        await message.reply_to_message.delete()
        await message.delete()
    try:
        await message.chat.ban_member(user_id)
    except Exception as er:
        return await message.reply_text(f"**ERROR:** {str(er)}")
    teks = await message.reply_text(msg)
    await message.chat.unban_member(user_id)
    await asyncio.sleep(1)
    return await teks.delete()


@app.on_message(filters.command(["ban", "delban", "unban"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def ban_cmd(client, message):
    reply = message.reply_to_message
    if reply and reply.sender_chat:
        return await message.reply(">**Please reply userID not anonymous account.**")
    try:
        target = reply.from_user.id if reply else message.text.split()[1]
    except (AttributeError, IndexError):
        return await message.reply("><b>You need to specify a user (either by reply or username/ID)!</b>")
    try:
        user = await client.get_users(target)
    except (errors.PeerIdInvalid, KeyError, errors.UsernameInvalid, errors.UsernameNotOccupied, IndexError):
        return await message.reply("><b>You need meet before interact!!</b>")
    mention = user.mention
    user_id = user.id
    if user_id == client.me.id or user_id in SUDOERS:
        return await message.reply_text("><b>Go to the heal now!!</b>")
    reply_markup = ikb([[("↩️ Unban", f"unban_{user_id}")]])
    if message.command[0] == "unban":
        try:
            await message.chat.unban_member(user_id)
        except Exception as er:
            return await message.reply_text(f"**ERROR:** {str(er)}")
        teks = await message.reply_text(f"><b>Unbanned: {mention}!</b>")
        await asyncio.sleep(1)
        return await teks.delete()
    else:
        msg = f"<b>Banned user {mention}</b>"
        if message.command[0][0] == "d":
            await message.reply_to_message.delete()
            await message.delete()
        try:
            await message.chat.ban_member(user_id)
        except Exception as er:
            return await message.reply_text(f">**ERROR:** {str(er)}")
        return await message.reply_text(msg, reply_markup=reply_markup)


@app.on_callback_query(filters.regex(r"^(unban|unmute)"))
async def callback_restrict(_, callback):
    try:
        query = callback.data.split("_")
        user_id = int(query[1])
        admins = callback.from_user.mention
        text = "Unbanned" if query[0] == "unban" else "Unmuted"
        await callback.message.chat.unban_member(user_id)
        msg = f"**User {text} by** {admins}"
        return await callback.edit_message_text(msg)
    except Exception as err:
        return await callback.edit_message_text(f"**ERROR:** {str(err)}")


@app.on_message(filters.command(["mute", "delmute", "unmute"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def mute_cmd(client, message):
    reply = message.reply_to_message
    if reply and reply.sender_chat:
        return await message.reply(">**Please reply userID not anonymous account.**")
    try:
        target = reply.from_user.id if reply else message.text.split()[1]
    except (AttributeError, IndexError):
        return await message.reply("><b>You need to specify a user (either by reply or username/ID)!</b>")
    try:
        user = await client.get_users(target)
    except (errors.PeerIdInvalid, KeyError, errors.UsernameInvalid, errors.UsernameNotOccupied, IndexError):
        return await message.reply("><b>You need meet before interact!!</b>")
    mention = user.mention
    user_id = user.id
    if user_id == client.me.id or user_id in SUDOERS:
        return await message.reply_text(f"><b>Go to the heal now!!</b>")
    reply_markup = ikb([[("🔊 Unmute", f"unmute_{user_id}")]])
    if message.command[0] == "unmute":
        try:
            await message.chat.unban_member(user_id)
            teks = await message.reply_text(f"><b>Unmuted user {mention}</b>")
            await asyncio.sleep(1)
            return await teks.delete()
        except Exception as er:
            return await message.reply_text(f">**ERROR:** {str(er)}")
    else:
        msg = f"><b>Muted user {mention}</b>"
        if message.command[0][0] == "d":
            await message.reply_to_message.delete()
            await message.delete()
        try:
            await message.chat.restrict_member(user_id, permissions=types.ChatPermissions())
            return await message.reply_text(msg, reply_markup=reply_markup)
        except Exception as er:
            return await message.reply_text(f">**ERROR:** {str(er)}")



@app.on_message(filters.command(["report"]) & ~config.BANNED_USERS)
async def report_cmd(client, message):
    if not message.reply_to_message:
        return await message.reply_text(f">**Please reply to message!**")

    reply = message.reply_to_message
    reply_id = reply.from_user.id if reply.from_user else reply.sender_chat.id
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    if reply_id == user_id:
        return await message.reply_text(
            f">**Please reply to message to member!**"
        )

    list_of_admins = await admin_check(message, user_id)
    linked_chat = (await client.get_chat(message.chat.id)).linked_chat
    if linked_chat is not None:
        if (
            list_of_admins is True
            and reply_id == message.chat.id
            or reply_id == linked_chat.id
        ):
            return await message.reply_text("**Please reply to message to member!**")
    else:
        if list_of_admins is True and reply_id == message.chat.id:
            return await message.reply_text("**Please reply to message to member!**")

    user_mention = (
        reply.from_user.mention if reply.from_user else reply.sender_chat.title
    )
    text = f"><b>Reported to admins, user: {user_mention}!</b>"
    admin_data = [
        i
        async for i in client.get_chat_members(
            chat_id=message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS
        )
    ]
    for admin in admin_data:
        if admin.user.is_bot or admin.user.is_deleted:
            continue
        text += f"[\u2063](tg://user?id={admin.user.id})"
    return await message.reply_to_message.reply_text(text)


