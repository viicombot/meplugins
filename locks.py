import asyncio


import config
from core import app
from pyrogram import filters, enums, types, errors
from utils.decorators import ONLY_GROUP, ONLY_ADMIN
from utils.database import dB
from utils.misc import SUDOERS

l_t = """<blockquote expandable>
**Lock Types:**
- `all` = Everything
- `msg` = Messages
- `media` = Media, such as Photo and Video.
- `polls` = Polls
- `invite` = Add users to Group
- `pin` = Pin Messages
- `info` = Change Group Info
- `webprev` = Web Page Previews
- `inline` = Inline bots
- `games` = Game Bots
- `stickers` = Stickers
- `topic` = Manage Topics
- `gifs` = Gifs
- `audio` = Audio
- `document` = Document
- `photo` = Photo
- `plain` = Plain Text
- `video_note` = Video Note
- `video` = Video
- `voice` = Voice Messages
- `anonchannel` = Send as chat will be locked
- `forwardall` = Forwarding from channel and user
- `forwardu` = Forwarding from user
- `forwardc` = Forwarding from channel
- `links | url` = Lock links</blockquote>"""


WHITELIST_USER = set()

@app.on_message(filters.command("locktypes") & ~config.BANNED_USERS)
async def lock_types(_, message):
    return await message.reply(l_t)
    


@app.on_message(filters.command("lock") & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def lock_perm(client, message):
    if len(message.command) < 2:
        await message.reply(">**Please enter a permission to lock!**")
        return
    lock_type = message.text.split(None, 1)[1]
    chat_id = message.chat.id

    if not lock_type:
        await message.reply(">**Specify a permission to lock!**")
        return
    get_perm = message.chat.permissions

    msg = get_perm.can_send_messages
    media = get_perm.can_send_media_messages
    webprev = get_perm.can_add_web_page_previews
    polls = get_perm.can_send_polls
    info = get_perm.can_change_info
    invite = get_perm.can_invite_users
    pin = get_perm.can_pin_messages
    stickers = get_perm.can_send_stickers
    gifs = get_perm.can_send_gifs
    games= get_perm.can_send_games
    inline = get_perm.can_send_inline
    topic = get_perm.can_manage_topics
    audio = get_perm.can_send_audios
    document = get_perm.can_send_docs
    photo = get_perm.can_send_photos
    plain = get_perm.can_send_plain
    video_note = get_perm.can_send_roundvideos
    video = get_perm.can_send_videos
    voice = get_perm.can_send_voices

    if lock_type == "all":
        try:
            await client.set_chat_permissions(chat_id, types.ChatPermissions(all_perms=False))
        except errors.ChatNotModified:
            pass
        except errors.ChatAdminRequired:
            return await message.reply(">**I don't have permission to do that.**")
        return await message.reply(">**🔒 ~~Locked all~~ permission from this Chat!**")

    if lock_type == "msg":
        msg = False
        perm = "messages"

    elif lock_type == "media":
        media = False
        perm = "audios, documents, photos, videos, video notes, voice notes"

    elif lock_type == "stickers":
        stickers = False
        perm = "stickers"

    elif lock_type == "gifs":
        gifs = False
        perm = "gifs"

    elif lock_type == "games":
        games = False
        perm = "games"

    elif lock_type == "inline":
        inline = False
        perm = "inline bots"

    elif lock_type == "webprev":
        webprev = False
        perm = "web page previews"

    elif lock_type == "polls":
        polls = False
        perm = "polls"

    elif lock_type == "info":
        info = False
        perm = "info"

    elif lock_type == "invite":
        invite = False
        perm = "invite"

    elif lock_type == "pin":
        pin = False
        perm = "pin"

    elif lock_type == "topic":
        topic = False
        perm = "topic"

    elif lock_type == "audio":
        audio = False
        perm = "audio"
    elif lock_type == "document":
        document = False
        perm = "document"
    elif lock_type == "photo":
        photo = False
        perm = "photo"
    elif lock_type == "plain":
        plain = False
        perm = "plain"

    elif lock_type == "video_note":
        video_note = False
        perm = "video note"
    elif lock_type == "video":
        video = False
        perm = "video"
    elif lock_type == "voice":
        voice = False
        perm = "voice"



    elif lock_type in ["links", "url"]:
        curr = await dB.get_var(chat_id, "anti_links")
        if curr:
            return await message.reply(">** antilink it is already on**")
        await dB.set_var(chat_id, "anti_links", True)
        return await message.reply(">**Locked links in the chat**")
    elif lock_type == "anonchannel":
        curr = await dB.get_var(chat_id, "anti_channel")
        if curr:
            return await message.reply(">**Anti channel it is already on")
        await dB.set_var(chat_id, "anti_channel", True)
        return await message.reply(">**Locked Send As Channel**")
    elif lock_type == "forwardall":
        curr = await dB.get_var(chat_id, "anti_forwardall")
        if curr:
            return await message.reply(">**Anti-forward from user and channel is already on.**")
        await dB.set_var(chat_id, "anti_forwardall", True)
        return await message.reply(">**Locked Forward from user as well as channel.**")
    elif lock_type == "forwardu":
        curr = await dB.get_var(chat_id, "anti_forward_user")
        if curr:
            return await message.reply(">**Anti-forward user is already on**")
        await dB.set_var(chat_id, "anti_forward_user", True)
        return await message.reply(">**Locked Forward message from user**")
    elif lock_type == "forwardc":
        curr = await dB.get_var(chat_id, "anti_forward_channel")
        if curr:
            return await message.reply(">**Anti-forward channel is already on")
        await dB.set_var(chat_id, "anti_forward_channel", True)
        return await message.reply(">**Locked Forward message from channel.**")
    else:
        return await message.reply(">**Invalid Lock Type!Use <code>/locktypes</code> to get the lock types.**")

    try:
        await client.set_chat_permissions(
            chat_id,
            types.ChatPermissions(
                can_send_messages=msg,
                can_send_media_messages=media,
                can_send_polls=polls,
                can_add_web_page_previews=webprev,
                can_change_info=info,
                can_invite_users=invite,
                can_pin_messages=pin,
                can_send_stickers=stickers,
                can_send_gifs=gifs,
                can_send_games=games,
                can_send_inline=inline,
                can_manage_topics=topic,
                can_send_audios=audio,
                can_send_docs=document,
                can_send_photos=photo,
                can_send_plain=plain,
                can_send_roundvideos=video_note,
                can_send_videos=video,
                can_send_voices=voice

            ),
        )
    except errors.ChatNotModified:
        pass
    except errors.ChatAdminRequired:
        return await message.reply(">**I don't have permission to do that**")
    return await message.reply(f">**🔒 Locked <b>{perm}</b> for this Chat.**")
    


@app.on_message(filters.command("locks"))
@ONLY_GROUP
async def view_locks(_, message):
    chkmsg = await message.reply(">**Please wait checking chat permissions...**")
    v_perm = message.chat.permissions
    chat_id = message.chat.id

    async def convert_to_emoji(val: bool):
        if val:
            return "✅"
        return "❌"

    anti_c_send = await dB.get_var(chat_id, "anti_channel")
    anti_forward = await dB.get_var(chat_id, "anti_forwardall")
    anti_forward_u = await dB.get_var(chat_id, "anti_forward_user")
    anti_forward_c = await dB.get_var(chat_id, "anti_forward_channel")
    anti_links = await dB.get_var(chat_id, "anti_links")
    anon = False
    if anti_c_send:
        anon = True
    anti_f = anti_f_u = anti_f_c = False
    if anti_forward:
        anti_f = True
    if anti_forward_u:
        anti_f_u = True
    if anti_forward_c:
        anti_f_c = True
    antil = False
    if anti_links:
        antil = True
    vmsg = await convert_to_emoji(v_perm.can_send_messages)
    vmedia = await convert_to_emoji(v_perm.can_send_media_messages)
    vwebprev = await convert_to_emoji(v_perm.can_add_web_page_previews)
    vstickers = convert_to_emoji(v_perm.can_send_stickers)
    vpolls = await convert_to_emoji(v_perm.can_send_polls)
    vinfo = await convert_to_emoji(v_perm.can_change_info)
    vinvite = await convert_to_emoji(v_perm.can_invite_users)
    vpin = await convert_to_emoji(v_perm.can_pin_messages)

    vgifs = convert_to_emoji(v_perm.can_send_gifs)
    vgames = convert_to_emoji(v_perm.can_send_games)
    vinline = convert_to_emoji(v_perm.can_send_inline)
    vtopic = convert_to_emoji(v_perm.can_manage_topics)
    vaudio = convert_to_emoji(v_perm.can_send_audios)
    vdocument = convert_to_emoji(v_perm.can_send_docs)
    vphoto = convert_to_emoji(v_perm.can_send_photos)
    vplain = convert_to_emoji(v_perm.can_send_plain)
    vvideo_note = convert_to_emoji(v_perm.can_send_roundvideos)
    vvideo = convert_to_emoji(v_perm.can_send_videos)
    vvoice = convert_to_emoji(v_perm.can_send_voices)

    vanon = await convert_to_emoji(anon)
    vanti = await convert_to_emoji(anti_f)
    vantiu = await convert_to_emoji(anti_f_u)
    vantic = await convert_to_emoji(anti_f_c)
    await convert_to_emoji(antil)

    if v_perm is not None:
        try:
            permission_view_str = f"""
<blockquote expandable><b>Chat Permissions:</b>

<b>Webpage Preview:</b> {vwebprev}
<b>Invite Users:</b> {vinvite}
<b>Pin Messages:</b> {vpin}
<b>Change Topic:</b> {vtopic}
<b>Change Info:</b> {vinfo}

<b>Send Messages:</b> {vmsg}
<b>Send Media:</b> {vmedia}
<b>Send Stickers:</b> {vstickers}
<b>Send Polls:</b> {vpolls}

<b>Send Gifs:</b> {vgifs}
<b>Send Games:</b> {vgames}
<b>Send Inline:</b> {vinline}
<b>Send Audio:</b> {vaudio}
<b>Send Document:</b> {vdocument}

<b>Send Photo:</b> {vphoto}
<b>Send Plan:</b> {vplain}
<b>Send Video Note:</b> {vvideo_note}
<b>Send Video:</b> {vvideo}
<b>Send Voice:</b> {vvoice}
<b>Send as chat:</b> {vanon}

<b>Can forward:</b> {vanti}
<b>Can forward from user:</b> {vantiu}
<b>Can forward from channel and chats:</b> {vantic}
<b>Can send links:</b> {antil}</blockquote>
"""
            return await chkmsg.edit(permission_view_str)

        except Exception as e_f:
            await chkmsg.edit(">**Something went wrong!**")
            return await message.reply(f">**ERROR: `{str(e_f)}`**")
    

@app.on_message(filters.command("unlock") & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def unlock_perm(client, message):
    if len(message.command) < 2:
        await message.reply(">**Please enter a permission to unlock!**")
        return
    unlock_type = message.text.split(None, 1)[1]
    chat_id = message.chat.id

    if not unlock_type:
        await message.reply(">**Specify a permission to unlock!**")
        return
    get_perm = message.chat.permissions

    msg = get_perm.can_send_messages
    media = get_perm.can_send_media_messages
    webprev = get_perm.can_add_web_page_previews
    polls = get_perm.can_send_polls
    info = get_perm.can_change_info
    invite = get_perm.can_invite_users
    pin = get_perm.can_pin_messages
    stickers = get_perm.can_send_stickers
    gifs = get_perm.can_send_gifs
    games= get_perm.can_send_games
    inline = get_perm.can_send_inline
    topic = get_perm.can_manage_topics
    audio = get_perm.can_send_audios
    document = get_perm.can_send_docs
    photo = get_perm.can_send_photos
    plain = get_perm.can_send_plain
    video_note = get_perm.can_send_roundvideos
    video = get_perm.can_send_videos
    voice = get_perm.can_send_voices

    if unlock_type == "all":
        try:
            await client.set_chat_permissions(chat_id, types.ChatPermissions(all_perms=True))
        except errors.ChatNotModified:
            pass
        except errors.ChatAdminRequired:
            return await message.reply(">**I don't have permission to do that.**")
        return await message.reply(">**🔒 ~~Unlocked all~~ permission from this Chat!**")

    if unlock_type == "msg":
        msg = True
        perm = "messages"

    elif unlock_type == "media":
        media = True
        perm = "audios, documents, photos, videos, video notes, voice notes"

    elif unlock_type == "stickers":
        stickers = True
        perm = "stickers"

    elif unlock_type == "gifs":
        gifs = True
        perm = "gifs"

    elif unlock_type == "games":
        games = True
        perm = "games"

    elif unlock_type == "inline":
        inline = True
        perm = "inline bots"

    elif unlock_type == "webprev":
        webprev = True
        perm = "web page previews"

    elif unlock_type == "polls":
        polls = True
        perm = "polls"

    elif unlock_type == "info":
        info = True
        perm = "info"

    elif unlock_type == "invite":
        invite = True
        perm = "invite"

    elif unlock_type == "pin":
        pin = True
        perm = "pin"

    elif unlock_type == "topic":
        topic = True
        perm = "topic"

    elif unlock_type == "audio":
        audio = True
        perm = "audio"
    elif unlock_type == "document":
        document = True
        perm = "document"
    elif unlock_type == "photo":
        photo = True
        perm = "photo"
    elif unlock_type == "plain":
        plain = True
        perm = "plain"

    elif unlock_type == "video_note":
        video_note = True
        perm = "video note"
    elif unlock_type == "video":
        video = True
        perm = "video"
    elif unlock_type == "voice":
        voice = True
        perm = "voice"



    elif unlock_type in ["links", "url"]:
        curr = await dB.get_var(chat_id, "anti_links")
        if not curr:
            return await message.reply(">** antilink it is already on**")
        await dB.remove_var(chat_id, "anti_links")
        return await message.reply(">**Unlocked links in the chat**")
    elif unlock_type == "anonchannel":
        curr = await dB.get_var(chat_id, "anti_channel")
        if not curr:
            return await message.reply(">**Anti channel it is already on")
        await dB.remove_var(chat_id, "anti_channel")
        return await message.reply(">**Unlocked Send As Channel**")
    elif unlock_type == "forwardall":
        curr = await dB.get_var(chat_id, "anti_forwardall")
        if not curr:
            return await message.reply(">**Anti-forward from user and channel is already on.**")
        await dB.remove_var(chat_id, "anti_forwardall")
        return await message.reply(">**Unlocked Forward from user as well as channel.**")
    elif unlock_type == "forwardu":
        curr = await dB.get_var(chat_id, "anti_forward_user")
        if not curr:
            return await message.reply(">**Anti-forward user is already on**")
        await dB.remove_var(chat_id, "anti_forward_user")
        return await message.reply(">**Unlocked Forward message from user**")
    elif unlock_type == "forwardc":
        curr = await dB.get_var(chat_id, "anti_forward_channel")
        if not curr:
            return await message.reply(">**Anti-forward channel is already on")
        await dB.remove_var(chat_id, "anti_forward_channel")
        return await message.reply(">**Unlocked Forward message from channel.**")
    else:
        return await message.reply(">**Invalid Lock Type!Use <code>/unlocktypes</code> to get the unlock types.**")

    try:
        await client.set_chat_permissions(
            chat_id,
            types.ChatPermissions(
                can_send_messages=msg,
                can_send_media_messages=media,
                can_send_polls=polls,
                can_add_web_page_previews=webprev,
                can_change_info=info,
                can_invite_users=invite,
                can_pin_messages=pin,
                can_send_stickers=stickers,
                can_send_gifs=gifs,
                can_send_games=games,
                can_send_inline=inline,
                can_manage_topics=topic,
                can_send_audios=audio,
                can_send_docs=document,
                can_send_photos=photo,
                can_send_plain=plain,
                can_send_roundvideos=video_note,
                can_send_videos=video,
                can_send_voices=voice

            ),
        )
    except errors.ChatNotModified:
        pass
    except errors.ChatAdminRequired:
        return await message.reply(">**I don't have permission to do that**")
    return await message.reply(f">**🔒 Unlocked <b>{perm}</b> for this Chat.**")


async def delete_messages(message):
    try:
        return await message.delete()
    except errors.FloodWait as e:
        await asyncio.sleep(e.value)
        return await message.delete()
    except Exception:
        return


async def is_approved_user(client, message):
    approved_users = await dB.get_list_from_var(message.chat.id, "APPROVED_USERS")
    chat_id = message.chat.id
    if config.adminlist.get(message.chat.id) is None:
        async for member in client.get_chat_members(
                chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS
            ):
                WHITELIST_USER.add(member.user.id)
                for a in approved_users:
                    WHITELIST_USER.add(a)
                for b in SUDOERS:
                    WHITELIST_USER.add(b)
                WHITELIST_USER.add(client.me.id)
    else:
        for a in config.adminlist.get(message.chat.id):
            WHITELIST_USER.add(a)
        for b in approved_users:
            WHITELIST_USER.add(b)
        for c in SUDOERS:
            WHITELIST_USER.add(c)
        WHITELIST_USER.add(client.me.id)

    if message.forward_from:
        if message.from_user.id in WHITELIST_USER:
            return True
        return False
    elif message.forward_from_chat:
        x_chat = (await client.get_chat(message.forward_from_chat.id)).linked_chat
        if message.from_user.id in WHITELIST_USER:
            return True
        if not x_chat:
            return False
        elif x_chat and x_chat.id == message.chat.id:
            return True
    elif message.from_user:
        if message.from_user.id in WHITELIST_USER:
            return True
        return False


@app.on_message(filters.group & ~filters.me, group=18)
async def lock_del_mess(client, message):
    if message.sender_chat and not (message.forward_from_chat or message.forward_from):
        if message.sender_chat.id == message.chat.id:
            return
        await delete_messages(message)
    is_approved = await is_approved_user(client, message)
    entity = message.entities if message.text else message.caption_entities
    if entity:
        for i in entity:
            if i.type in [enums.MessageEntityType.URL or enums.MessageEntityType.TEXT_LINK]:
                if await dB.get_var(message.chat.id, "anti_links"):
                    if not is_approved:
                        await delete_messages(message)
    elif message.forward_from or message.forward_from_chat:
        if not is_approved:
            if await dB.get_var(message.chat.id, "anti_forwardall"):
                await delete_messages(message)
            elif (await dB.get_var(message.chat.id, "anti_forward_user") and not message.forward_from_chat):
                await delete_messages(message)
            elif (await dB.get_var(message.chat.id, "anti_forward_channel") and message.forward_from_chat):
                await delete_messages(message)


__MODULE__ = "Locks"
__HELP__ = """
<blockquote expandable>
<b>★ /lock [type]</b> - Restrict a specific feature in the group.  
<b>★ /unlock [type]</b> - Remove restriction from a specific feature.  
<b>★ /locks</b> - View current active restrictions in the group.  
<b>★ /locktypes</b> - Show available lock types.

✅ Supported lock types:
<code>
all - Everything
msg - Messages
media - All media types
polls - Polls
invite - Adding users
pin - Pinning messages
info - Group info editing
webprev - Web previews
inline - Inline bots
games - Game bots
stickers - Stickers
topic - Manage topics
gifs - GIFs
audio - Audio files
document - Documents
photo - Photos
plain - Plain text
video_note - Video notes
video - Videos
voice - Voice messages
anonchannel - Send as channel
forwardall - Forwards from all sources
forwardu - Forwards from users
forwardc - Forwards from channels
links | url - Web links
</code>

🔐 Use these to prevent spam, unwanted forwards, bots, or link sharing.

💡 Example usage:
<code>/lock media</code> - Locks all media types  
<code>/unlock video</code> - Unlocks video messages  
<code>/lock forwardall</code> - Blocks all forwards
</blockquote>
"""
