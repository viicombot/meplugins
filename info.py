import asyncio
import io
import traceback
import asyncio
import config

from datetime import datetime
from time import time

from pyrogram import filters, enums, raw, errors
from pyrogram.types import Chat, User
from pyrogram.file_id import FileId, FileType, ThumbnailSource
from pyrogram.helpers import ikb
from core import app, userbot
from utils.database import is_banned_user
from logs import LOGGER

interact_with_to_delete = []


async def interact_with(message):
    await asyncio.sleep(1)
    response = [
        msg
        async for msg in message._client.get_chat_history(message.chat.id, limit=1)
    ]
    seconds_waiting = 0

    while response[0].from_user.is_self:
        seconds_waiting += 1
        if seconds_waiting >= 5:
            raise RuntimeError("bot didn't answer in 5 seconds")

        await asyncio.sleep(1)
        response = [
            msg
            async for msg in message._client.get_chat_history(
                message.chat.id, limit=1
            )
        ]

    interact_with_to_delete.append(message.id)
    interact_with_to_delete.append(response[0].id)

    return response[0]

def is_valid(message):
    user_id = None
    user_first_name = None
    user = None

    if message.from_user:
        user = message.from_user
        user_id = user.id
        user_first_name = user.first_name

    elif message.sender_chat:
        user = message.sender_chat
        user_id = user.id
        user_first_name = user.title

    return (user_id, user_first_name, user)

def extract_user(message):
    user_id = None
    user_first_name = None
    user = None

    if len(message.command) > 1:
        entities = message.entities or []
        if (
            len(entities) > 1
            and entities[1].type == enums.MessageEntityType.TEXT_MENTION
        ):
            required_entity = message.entities[1]
            user_id = required_entity.user.id
            user_first_name = required_entity.user.first_name
            user = required_entity.user
        else:
            user_id = message.command[1]
            user_first_name = user_id
            user = True

        try:
            user_id = int(user_id)
        except ValueError:
            pass

    elif message.reply_to_message:
        user_id, user_first_name, user = is_valid(message.reply_to_message)

    elif message:
        user_id, user_first_name, user = is_valid(message)

    return (user_id, user_first_name, user)


@app.on_message(filters.command("id") & ~config.BANNED_USERS)
async def id_cmd(client, message):
    chat = message.chat
    your_id = message.from_user if message.from_user else message.sender_chat
    message_id = message.id
    reply = message.reply_to_message

    text = f"**Message ID:** `{message_id}`\n"
    text += f"**Your ID:** `{your_id.id}`\n"
    text += f"**Chat ID:** `{chat.id}`\n"

    if reply:
        replied_user_id = (
            reply.from_user.id
            if reply.from_user
            else reply.sender_chat.id if reply.sender_chat else None
        )
        text += "\n**Replied Message Information:**\n"
        text += f"**├ Message ID:** `{reply.id}`\n"
        if replied_user_id:
            text += f"**├ User ID:** `{replied_user_id}`\n"

        if reply.entities:
            for entity in reply.entities:
                if entity.custom_emoji_id:
                    text += f"**╰ Emoji ID:** `{entity.custom_emoji_id}`\n"

        if reply.photo:
            text += f"**╰ Photo File ID:** `{reply.photo.file_id}`\n"
        elif reply.video:
            text += f"**╰ Video File ID:** `{reply.video.file_id}`\n"
        elif reply.sticker:
            text += f"**╰ Sticker File ID:** `{reply.sticker.file_id}`\n"
        elif reply.animation:
            text += f"**╰ GIF File ID:** `{reply.animation.file_id}`\n"
        elif reply.document:
            text += f"**╰ Document File ID:** `{reply.document.file_id}`\n"

    if len(message.command) == 2:
        try:
            split = message.text.split(None, 1)[1].strip()
            user_id = (await client.get_users(split)).id
            text += f"\n**Mentioned User ID:** `{user_id}`\n"
        except Exception:
            LOGGER.error(f"ERROR: {traceback.format_exc()}")
            return await message.reply_text(f"**User tidak ditemukan.**")

    return await message.reply_text(
        text,
        disable_web_page_preview=True,
        parse_mode=enums.ParseMode.MARKDOWN,
    )


@app.on_message(filters.command("info") & ~config.BANNED_USERS)
async def user_info(client, message):
    try:
        from_user_id, from_user_name, user = extract_user(message)
        from_user = None
        small_user = None
        full_user = None
        creation_date = "-"
        dc_id = "-"
        gbanned = False
        is_bot = False
        premium = False
        client2 = userbot.clients[0]
        try:
            if user or isinstance(user, User):
                from_user = await client.invoke(
                    raw.functions.users.GetFullUser(id=(await client.resolve_peer(from_user_id)))
                )
                if from_user:
                    await client2.unblock_user("creationdatebot")
                    xin = await client2.resolve_peer("creationdatebot")
                    try:
                        created = await interact_with(
                            await client2.send_message(
                                "creationdatebot", f"/id {user.id}"
                            )
                        )
                        creation_date = created.text
                    except RuntimeError:
                        creation_date = "-"
                    interact_with_to_delete.clear()
                    small_user = from_user.users[0]
                    full_user = from_user.full_user
                    dc_id = getattr(small_user.photo, "dc_id", "-")
                    gbanned = await is_banned_user(small_user.id)
                    is_bot = small_user.bot
                    premium = small_user.premium
                    from_user = User._parse(client, small_user)
                    await client2.invoke(
                        raw.functions.messages.DeleteHistory(
                            peer=xin, max_id=0, revoke=True
                        )
                    )
        except Exception:
            #LOGGER.error(f"ERROR: {traceback.format_exc()}")
            from_user = None

        if from_user is None:
            try:
                from_user = await client.invoke(
                    raw.functions.channels.GetFullChannel(channel=(await client.resolve_peer(from_user_id)))
                )
                small_user = from_user.chats[0]
                full_user = from_user.full_chat
                dc_id = getattr(full_user.chat_photo, "dc_id", "-")
                from_user = Chat._parse_channel_chat(client, small_user)
            except Exception:
                #LOGGER.error(f"ERROR: {traceback.format_exc()}")
                from_user = None

        if not from_user:
            return await message.reply(
                "**Gagal mengambil info. Silakan periksa kembali user atau chat target.**"
            )

        first_name = getattr(from_user, "title", getattr(from_user, "first_name", ) or "")
        last_name = getattr(from_user, "last_name") or ""
        username = from_user.username or ""
        msg = ""

        if isinstance(from_user, User):
            msg += "<blockquote expandable><b>UserInfo:</b>\n"
            msg += f"   <b>name:</b> <b><a href='tg://user?id={from_user.id}'>{first_name} {last_name}</a></b>\n"
            msg += f"      <b>id:</b> <code>{from_user.id}</code>\n"
            msg += f"      <b>dc_id:</b> <code>{dc_id}</code>\n"
            msg += f"      <b>created_at:</b> <code>{creation_date}</code>\n"
            msg += f"      <b>is_bot:</b> <code>{is_bot}</code>\n"
            msg += f"      <b>is_gbanned:</b> <code>{gbanned}</code>\n"
            msg += f"      <b>is_premium:</b> <b>{premium}</b>\n"
            buttons = ikb(
                [
                    [
                        (
                            "User Link",
                            f"https://t.me/{username}" if username else from_user_id,
                            "url" if username else "user_id",
                        ),
                    ],
                    [("Close", "close")],
                ]
            )
        elif isinstance(from_user, Chat):
            msg += "<blockquote expandable><b>ChatInfo:</b>\n"
            msg += f"   <b>name:</b> <b><a href='https://t.me/c/{full_user.id}'>{first_name}</a></b>\n"
            msg += f"      <b>dc_id:</b> <code>{dc_id}</code>\n"
            msg += f"      <b>id:</b> <code>{from_user.id}</code>\n"
            buttons = ikb(
                [
                    [
                        (
                            "Chat Link",
                            (
                                f"https://t.me/{username}"
                                if username
                                else f"https://t.me/c/{full_user.id}"
                            ),
                            "url",
                        ),
                    ],
                    [("Close", f"close")],
                ]
            )

        if getattr(full_user, "about", None):
            msg += f"      <b>about :</b> <code>{full_user.about}</code>\n"

        if getattr(full_user, "common_chats_count", None):
            msg += f"      <b>same_group:</b> <code>{full_user.common_chats_count}</code>\n"

        if isinstance(from_user, User) and message.chat.type in [
            enums.ChatType.SUPERGROUP,
            enums.ChatType.CHANNEL,
        ]:
            try:
                chat_member_p = await message.chat.get_member(small_user.id)
                joined_date = (
                    chat_member_p.joined_date or datetime.fromtimestamp(time())
                ).strftime("%d-%m-%Y %H:%M:%S")
                msg += f"      <b>joinned:</b> <code>{joined_date}</code>\n"
            except errors.UserNotParticipant:
                pass

        if len(msg) < 334:
            polos = getattr(
                full_user, "settings", getattr(full_user, "available_reactions", None)
            )
            if polos:
                msg += f"      <b>reactions:</b> <code>{len(polos)}</code>\n"

        if getattr(full_user, "online_count", None):
            msg += f"      <b>online_count:</b> <code>{full_user.online_count}</code>\n"

        if getattr(full_user, "pinned_msg_id", None):
            url_pin = (
                f"tg://openmessage?user_id={full_user.id}&message_id={full_user.pinned_msg_id}"
                if isinstance(full_user, raw.types.UserFull)
                else f"https://t.me/c/{full_user.id}/{full_user.pinned_msg_id}"
            )
            msg += (
                f"      <b>pinned:</b> <b><a href='{url_pin}'>Pinned Message</a></b>\n"
            )

        if getattr(full_user, "linked_chat_id", None):
            msg += f"      <b>linked_chat:</b> <b><a href='https://t.me/c/{full_user.linked_chat_id}/1'>Linked Chat</a></b>\n"
        chat_photo = from_user.photo
        if chat_photo:
            photo_date = None
            profile_photo = getattr(
                full_user, "profile_photo", getattr(full_user, "chat_photo", None)
            )
            if profile_photo:
                profile_vid = profile_photo.video_sizes[0] if profile_photo.video_sizes else None
                photo_date = datetime.fromtimestamp(profile_photo.date).strftime("%d-%m-%Y %H:%M:%S")
            if photo_date:
                msg += f"      <b>upload_date:</b>: `{photo_date}`\n"
            if profile_vid:
                file_obj = io.BytesIO()
                async for chunk in client.stream_media(
                    message=FileId(
                        file_type=FileType.PHOTO,
                        dc_id=profile_photo.dc_id,
                        media_id=profile_photo.id,
                        access_hash=profile_photo.access_hash,
                        file_reference=profile_photo.file_reference,
                        thumbnail_source=ThumbnailSource.THUMBNAIL,
                        thumbnail_file_type=FileType.PHOTO,
                        thumbnail_size=profile_vid.type,
                        volume_id=0,
                        local_id=0,
                    ).encode(),
                ):
                    file_obj.write(chunk)
                file_obj.name = "profile_vid_.mp4"
                msg += "</blockquote>"
                return await message.reply_video(
                    video=file_obj,
                    caption=msg,
                    reply_markup=buttons,
                )
            else:
                file_obj = io.BytesIO()
                async for chunk in client.stream_media(
                    message=chat_photo.big_file_id,
                ):
                    file_obj.write(chunk)
                file_obj.name = "profile_pic_.jpg"
                msg += "</blockquote>"
                return await message.reply_photo(
                    photo=file_obj,
                    caption=msg,
                    reply_markup=buttons,
                )
        else:
            msg += "</blockquote>"
            return await message.reply(msg, reply_markup=buttons)
    except Exception:
        LOGGER.error(f"ERROR: {traceback.format_exc()}")


__MODULE__ = "Info"
__HELP__ = """
<blockquote expandable>
<b>ℹ️ User & Chat Info</b>

<b>★ /id</b> [reply or @username] – Get the user's or chat’s ID.  
<b>★ /info</b> [reply or @username/userID] – Get full info about a user or chat.
</blockquote>
"""
