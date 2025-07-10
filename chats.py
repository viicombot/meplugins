


import config
import asyncio
import traceback

from core import app, userbot
from pyrogram import filters, errors, enums

from utils.decorators import ONLY_GROUP, ONLY_ADMIN

__MODULE__ = "Group-Tools"
__HELP__ = """
<blockquote expandable>
<b>👥 Group Management Commands</b>

<b>★ /setgcname</b> (reply to text)  
Set the group title.

<b>★ /setgcdesc</b> (reply to text)  
Set the group description.

<b>★ /setgcpic</b> (reply to photo/video)  
Set group profile picture.

<b>★ /settitle</b> or <b>/title</b> (reply user or userID) (title)  
Set custom admin title for a user.

<b>★ /kickme</b>  
Leave the group (unless you're an admin/owner).

<b>★ /cc</b> (reply or userID)  
Clear message history of the replied user.

<b>★ /cekmember</b>  
Check total members in group.

<b>★ /cekonline</b>  
Check online members (userbot will be used).

<b>★ /cekmsg</b> (userID/username or reply)  
Check how many messages a user has sent in the group.
</blockquote>
"""

async def has_permission(client, chat_id):
    try:
        member = await client.get_chat_member(chat_id, client.me.id)
        return member.status == enums.ChatMemberStatus.ADMINISTRATOR
    except:
        return False


@app.on_message(filters.command(["setgcname", "setgcdesc", "setgcpic"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def group_cmd(client, message):
    command = message.command
    reply = message.reply_to_message
    chat = await client.get_chat(message.chat.id)
    if command[0] == "setgcname":
        if reply and not (reply.text or reply.caption):
            return await message.reply(f">**Example: `setgcname` [reply to text]!**")
        content = reply.text or reply.caption
        await message.chat.set_title(content.strip())
        return await message.reply(f">**Successfully set title group: `{chat.title}` to: `{content}`**")
    elif command[0] == "setgcdesc":
        if reply and not (reply.text or reply.caption):
            return await message.reply(f">**Example: `setgcdesc` [reply to text]!**")
        content = reply.text or reply.caption
        await message.chat.set_description(content.strip())
        return await message.reply(f">**Successfully set description group: `{chat.description}` to: `{content}`**")
    elif command[0] == "setgcpic":
        if reply and not (reply.photo or reply.video):
            return await message.reply(f">**Example: `setgcpic` [reply to foto or video]!**")
        if not (reply.photo or reply.video):
            return await message.reply(">**Only photo/video allowed, not documents!**")
        media = reply.photo or reply.video
        kwargs = {"photo": media.file_id} if reply.photo else {"video": media.file_id}
        await client.set_chat_photo(message.chat.id, **kwargs)
        return await message.reply(f"><b>Successfully changed [media]({reply.link}) to profile group!</b>", disable_web_page_preview=True)
    

@app.on_message(filters.command(["settitle", "title"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def handle_title(client, message):
    reply = message.reply_to_message
    if reply and reply.sender_chat:
        return await message.reply(">**Please reply to user.**")
    user_id = None
    title = None
    if reply:
        user_id = reply.from_user.id
        if len(message.command) > 1:
            title = message.text.split(None, 1)[1]
    elif len(message.command) > 2:
        user_id = message.text.split()[1]
        title = message.text.split(None, 2)[2]
    if not all([user_id, title]):
        return await message.reply(f">**Please give me title to set. Example: `/title [username/reply user] [title]` or reply to user with title!**")
    try:
        user = await client.get_users(user_id)
        current_title = (
            await client.get_chat_member(message.chat.id, user.id)
        ).custom_title
        mention = user.mention
        await client.set_administrator_title(message.chat.id, user.id, title)
        return await message.reply(f"><b>Successfully set title user: {mention} `{current_title}` to: `{title}`</b>")
    except Exception as e:
        return await message.reply(f"**ERROR: `{str(e)}`**")


@app.on_message(filters.command(["kickme"]) & ~config.BANNED_USERS)
async def kickme_cmd(client, message):
    chat_id = message.chat.id
    status = None
    user_id = message.from_user.id
    mention = message.from_user.mention
    try:
        chat_id = int(chat_id)
    except ValueError:
        chat_id = str(chat_id)
    try:
        chat_member = await client.get_chat_member(chat_id, user_id)
        if chat_member.status == enums.ChatMemberStatus.ADMINISTRATOR:
            status = "admin"
        elif chat_member.status == enums.ChatMemberStatus.OWNER:
            status = "owner"
        elif chat_member.status == enums.ChatMemberStatus.MEMBER:
            status = "member"
    except Exception as er:
        return await message.edit(f">**Error:** {str(er)}")
    if status in ["admin", "owner"]:
        return await message.reply(f">**Sorry you cant leave this chat because you as: {status} in this chat.!**")
    else:
        await message.chat.ban_member(user_id)
        await asyncio.sleep(0.5)
        await message.chat.unban_member(user_id)
        return await message.reply(f">**Sepertinya dia {mention} depresi, ingin bunuh diri.**")


@app.on_message(filters.command(["cc"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def cc_cmd(client, message):
    reply = message.reply_to_message
    if reply and reply.sender_chat and reply.sender_chat != message.chat.id:
        return  await message.reply_text(f">**Please reply to valid user_id!**")
    try:
        target = reply.from_user.id or reply.sender_chat.id if reply else message.text.split()[1]
    except (AttributeError, IndexError):
        return await message.reply(">**Please reply to valid user_id!**")
    try:
        user = await client.get_users(target)
    except (errors.PeerIdInvalid, KeyError, errors.UsernameInvalid, errors.UsernameNotOccupied):
        return await message.reply(">**Please reply to valid user_id!**")
    user_id = user.id
    try:
        await client.delete_user_history(message.chat.id, user_id)
        return await message.reply(">**Succesfully delete message from user.**")
    except Exception:
        return await message.reply(">**I dont have enough permission.**")


@app.on_message(filters.command(["cekmember"]) & ~config.BANNED_USERS)
async def cekmember_cmd(client, message):
    chat_id = message.chat.id if len(message.command) < 2 else message.text.split()[1]
    proses = await message.reply(">**Please wait...*")
    try:
        member_count = await client.get_chat_members_count(chat_id)
        await asyncio.sleep(1)
        return await proses.edit(f"**Total members in group: {chat_id} is `{member_count}` members.**")
    except Exception as e:
        return await proses.edit(f">**ERROR:** {str(e)}")


@app.on_message(filters.command(["cekonline"]) & ~config.BANNED_USERS)
async def cekonline_cmd(client, message):
    proses = await message.reply(">**Please wait ...**")
    client2 = userbot.clients[0]
    chat_id = message.command[1] if len(message.command) > 1 else message.chat.id
    isbot_admin = await has_permission(client, chat_id)
    if not isbot_admin:
        return await proses.edit(f">**Failed, maybe i dont have enough permission")
    get = await client.get_chat_member(chat_id, client2.me.id)
    if get.status in [
        enums.ChatMemberStatus.BANNED,
        enums.ChatMemberStatus.RESTRICTED,
    ]:
        await client.unban_chat_member(chat_id, client2.me.id)
    try:
        link = await client.get_chat_invite_link(chat_id)
        await client2.join_chat(link)
    except Exception as err:
        print(f"ERROR: {traceback.format_exc()}")
        return await proses.edit(f">**Failed, maybe i dont have enough permission: {str(err)}")

    try:
        member_online = await client2.get_chat_online_count(chat_id)
        await asyncio.sleep(1)
        return await proses.edit(f">**Total members online in group: {chat_id} is `{member_online}` members.**")
    except Exception as e:
        return await proses.edit(f">**ERROR:** {str(e)}")


@app.on_message(filters.command(["cekmsg"]) & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def cekmsg_cmd(client, message):
    proses = await message.reply(">**Please wait ...**")
    chat_id = None
    user_id = None
    client2 = userbot.clients[0]

    if len(message.command) > 1:
        chat_id = message.command[1] if message.command[1].isdigit() else chat_id
        user_id = message.command[2] if len(message.command) > 2 else message.command[1]
    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        chat_id = message.chat.id

    if not user_id:
        return await message.reply_text("**Please reply to a user or provide a username/ID!**")
    isbot_admin = await has_permission(client, chat_id)
    if not isbot_admin:
        return await proses.edit(f">**Failed, maybe i dont have enough permission")
    get = await client.get_chat_member(chat_id, client2.me.id)
    if get.status in [
        enums.ChatMemberStatus.BANNED,
        enums.ChatMemberStatus.RESTRICTED,
    ]:
            await client.unban_chat_member(chat_id, client2.me.id)
    try:
        link = await client.get_chat_invite_link(chat_id)
        await client2.join_chat(link)
    except Exception as err:
        print(f"ERROR: {traceback.format_exc()}")
        return await proses.edit(f">**Failed, maybe i dont have enough permission: {str(err)}")

    try:
        user = await client2.get_users(user_id)
        umention = user.mention
    except (errors.PeerIdInvalid, KeyError):
        return await message.reply_text(f">**Error: PeerIdInvalid or invalid user ID/username.**")
    try:

        total_msg = await client2.search_messages_count(chat_id, from_user=user.id)
        await asyncio.sleep(1)
        await proses.edit(f">**Total messages by {umention} in chat `{chat_id}`: `{total_msg}` messages.**")
    except Exception as e:
        await proses.edit(f">**Error:** `{str(e)}`")