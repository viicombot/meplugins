



import asyncio
import os
import shutil
import traceback
import config

from pyrogram import enums
from pyrogram.errors import BadRequest, PeerIdInvalid, StickersetInvalid
from pyrogram.file_id import FileId
from pyrogram.raw.functions.messages import GetStickerSet, SendMedia
from pyrogram.raw.functions.stickers import (AddStickerToSet, CreateStickerSet,
                                             RemoveStickerFromSet)
from pyrogram.raw.types import (DocumentAttributeFilename, InputDocument,
                                InputMediaUploadedDocument,
                                InputStickerSetItem, InputStickerSetShortName)
from utils.functions import Tools
from pyrogram.helpers import ikb
from core import app
from pyrogram import filters


@app.on_message(filters.command("addpack") & ~config.BANNED_USERS)
async def make_pack(client, message):
    prog_msg = await message.reply(">⏳**Getting all stickers...**")
    reply = message.reply_to_message

    if not reply or not reply.sticker or not reply.sticker.set_name:
        return await prog_msg.edit(">⚠️**Please reply to message sticker!**")

    from_user = message.from_user
    user = await client.resolve_peer(from_user.id)

    animated = reply.sticker.is_animated
    videos = reply.sticker.is_video
    sticker_emoji = reply.sticker.emoji or "😄"

    pack_prefix = "anim" if animated else "vid" if videos else "a"
    packnum = 0

    if len(message.command) > 1:
        if message.command[1].isdigit():
            packnum = int(message.command[1])
        if len(message.command) > 2:
            sticker_emoji = (
                "".join(
                    set(Tools.get_emoji_regex().findall("".join(message.command[2:])))
                )
                or sticker_emoji
            )

    packname = f"{pack_prefix}_{packnum}_{from_user.id}_by_{client.me.username}"
    type_name = "AnimPack" if animated else "VidPack" if videos else "Pack"
    version = f" v{packnum}" if packnum > 0 else ""
    title = f"{from_user.first_name} {version}{type_name}"

    folder = f"downloads/stickers_pack/{from_user.id}"
    os.makedirs(folder, exist_ok=True)

    try:
        stickerset = await client.invoke(
            GetStickerSet(
                stickerset=InputStickerSetShortName(short_name=reply.sticker.set_name),
                hash=0,
            )
        )
        masks = stickerset.set.masks

        items = []
        count = 0
        for doc in stickerset.documents:
            items.append(
                InputStickerSetItem(
                    document=InputDocument(
                        id=doc.id,
                        access_hash=doc.access_hash,
                        file_reference=doc.file_reference,
                    ),
                    emoji=sticker_emoji,
                )
            )
            count += 1
            if count >= 120:
                break

        await prog_msg.edit(">**🚀 Making new pack...**")

        await client.invoke(
            CreateStickerSet(
                user_id=user,
                title=title,
                short_name=packname,
                stickers=items,
                masks=masks,
            )
        )
        reply_markup = ikb([[("👀 Click here to view pack", f"https://t.me/addstickers/{packname}", "url")]])
        await prog_msg.edit(">✅ <b>Succesfully making stickers pack!</b>\n", reply_markup=reply_markup, disable_web_page_preview=True)

    except Exception as e:
        print(traceback.format_exc())
        await prog_msg.edit(f">**❌ Failed to making pack:** <code>{e}</code>")

    finally:
        shutil.rmtree(folder, ignore_errors=True)


@app.on_message(filters.command("kang") & ~config.BANNED_USERS)
async def make_stickers(client, message):
    prog_msg = await message.reply(">**Making stickers...**")
    sticker_emojis = "🤔"
    sticker_emoji = message.command[1] if len(message.command) > 1 else sticker_emojis
    packnum = 0
    packname_found = False
    resize = False
    animated = False
    videos = False
    convert = False
    reply = message.reply_to_message
    user = await client.resolve_peer(message.from_user.username or message.from_user.id)

    if reply and reply.media:
        if reply.photo:
            resize = True
        elif reply.animation:
            videos = True
            convert = True
        elif reply.video:
            convert = True
            videos = True
        elif reply.document:
            if "image" in reply.document.mime_type:
                # mime_type: image/webp
                resize = True
            elif reply.document.mime_type in (
                enums.MessageMediaType.VIDEO,
                enums.MessageMediaType.ANIMATION,
            ):
                # mime_type: application/video
                videos = True
                convert = True
            elif "tgsticker" in reply.document.mime_type:
                # mime_type: application/x-tgsticker
                animated = True
        elif reply.sticker:
            if not reply.sticker.file_name:
                return await prog_msg.edit_text(">**Sticker name not found!**")
            if reply.sticker.emoji:
                sticker_emoji = reply.sticker.emoji
            animated = reply.sticker.is_animated
            videos = reply.sticker.is_video
            if videos:
                convert = False
            elif not reply.sticker.file_name.endswith(".tgs"):
                resize = True
        else:
            return await prog_msg.edit_text()

        pack_prefix = "anim" if animated else "vid" if videos else "a"
        packname = f"{pack_prefix}_{message.from_user.id}_by_{client.me.username}"

        if (
            len(message.command) > 1
            and message.command[1].isdigit()
            and int(message.command[1]) > 0
        ):
            # provide pack number to kang in desired pack
            packnum = message.command.pop(1)
            packname = (
                f"{pack_prefix}{packnum}_{message.from_user.id}_by_{client.me.username}"
            )
        if len(message.command) > 1:
            # matches all valid emojis in input
            sticker_emoji = (
                "".join(
                    set(Tools.get_emoji_regex().findall("".join(message.command[1:])))
                )
                or sticker_emoji
            )
        filename = await client.download_media(message.reply_to_message)
        if not filename:
            # Failed to download
            await prog_msg.delete()
            return
    elif message.entities and len(message.entities) > 1:
        pack_prefix = "a"
        filename = "sticker.png"
        packname = f"c{message.from_user.id}_by_{client.me.username}"
        img_url = next(
            (
                message.text[y.offset : (y.offset + y.length)]
                for y in message.entities
                if y.type == "url"
            ),
            None,
        )

        if not img_url:
            await prog_msg.delete()
            return
        try:
            r = await Tools.fetch.get(img_url)
            if r.status_code == 200:
                with open(filename, mode="wb") as f:
                    f.write(r.read())
        except Exception as r_e:
            return await prog_msg.edit_text(f"{r_e.__class__.__name__} : {r_e}")
        if len(message.command) > 2:
            # message.command[1] is image_url
            if message.command[2].isdigit() and int(message.command[2]) > 0:
                packnum = message.command.pop(2)
                packname = f"a{packnum}_{message.from_user.id}_by_{client.me.username}"
            if len(message.command) > 2:
                sticker_emoji = (
                    "".join(
                        set(
                            Tools.get_emoji_regex().findall(
                                "".join(message.command[2:])
                            )
                        )
                    )
                    or sticker_emoji
                )
            resize = True
    else:
        return await prog_msg.edit_text(">**Please reply to message sticker**")
    try:
        if resize:
            filename = Tools.resize_image(filename)
        elif convert:
            filename = await Tools.convert_video(filename)
            if filename is False:
                return await prog_msg.edit_text("Error")
        max_stickers = 50 if animated else 120
        while not packname_found:
            try:
                stickerset = await client.invoke(
                    GetStickerSet(
                        stickerset=InputStickerSetShortName(short_name=packname),
                        hash=0,
                    )
                )
                if stickerset.set.count >= max_stickers:
                    packnum += 1
                    packname = f"{pack_prefix}_{packnum}_{message.from_user.id}_by_{client.me.username}"
                else:
                    packname_found = True
            except StickersetInvalid:
                break
        file = await client.save_file(filename)
        media = await client.invoke(
            SendMedia(
                peer=(await client.resolve_peer(config.LOG_BACKUP)),
                media=InputMediaUploadedDocument(
                    file=file,
                    mime_type=client.guess_mime_type(filename),
                    attributes=[DocumentAttributeFilename(file_name=filename)],
                ),
                message=f"#Sticker kang by UserID -> {message.from_user.id}",
                random_id=client.rnd_id(),
            ),
        )
        msg_ = media.updates[-1].message
        stkr_file = msg_.media.document
        if packname_found:
            await prog_msg.edit_text(">**Add to existing sticker pack...**")
            await client.invoke(
                AddStickerToSet(
                    stickerset=InputStickerSetShortName(short_name=packname),
                    sticker=InputStickerSetItem(
                        document=InputDocument(
                            id=stkr_file.id,
                            access_hash=stkr_file.access_hash,
                            file_reference=stkr_file.file_reference,
                        ),
                        emoji=sticker_emoji,
                    ),
                )
            )
        else:
            await prog_msg.edit_text(">**Making new sticker pack...**")
            stkr_title = f"{message.from_user.first_name}"
            if animated:
                stkr_title += " AnimPack"
            elif videos:
                stkr_title += " VidPack"
            if packnum != 0:
                stkr_title += f" v{packnum}"
            try:
                await client.invoke(
                    CreateStickerSet(
                        user_id=user,
                        title=stkr_title,
                        short_name=packname,
                        stickers=[
                            InputStickerSetItem(
                                document=InputDocument(
                                    id=stkr_file.id,
                                    access_hash=stkr_file.access_hash,
                                    file_reference=stkr_file.file_reference,
                                ),
                                emoji=sticker_emoji,
                            )
                        ],
                        # animated=animated,
                        # videos=videos,
                    )
                )
            except PeerIdInvalid:
                reply_markup = ikb([[("👀 Click Here", f"https://t.me/{client.username}=start", "url")]])
                return await prog_msg.edit_text(">**Click button below**", reply_markup=reply_markup)
    except BadRequest:
        return await prog_msg.edit_text(">**Your Sticker Pack is full if your pack is not in Type v1 /kang 1, if not in Type v2 /kang 2 and soon.**")
    except Exception as all_e:
        return await prog_msg.edit_text(f"{all_e.__class__.__name__} : {all_e}")
    else:
        reply_markup = ikb([[("👀 Click here to view sticker", f"https://t.me/addstickers/{packname}", "url")]])
        await prog_msg.edit_text(f"<b>Succesfully making stickers!</b>\n<b>Emoji:</b> {sticker_emoji}", reply_markup=reply_markup)
        await client.delete_messages(chat_id=config.LOG_GROUP_ID, message_ids=msg_.id, revoke=True)
        try:
            os.remove(filename)
        except OSError:
            pass
    return


@app.on_message(filters.command("unkang") & ~config.BANNED_USERS)
async def remove_stickers(client, message):
    rep = message.reply_to_message.sticker

    try:
        sticker_id = rep.file_id
        decoded = FileId.decode(sticker_id)
        sticker = InputDocument(
            id=decoded.media_id,
            access_hash=decoded.access_hash,
            file_reference=decoded.file_reference,
        )
        await client.invoke(RemoveStickerFromSet(sticker=sticker))
        await message.reply(">**Succesfully deleted sticker.**")
        return
    except Exception as e:
        await message.reply(f">**Failed to delete sticker from your pack.\n\nError:** <code>{e}</code>")
        return


async def download_and_reply(client, message, stick, file_extension):
    pat = await client.download_media(
        stick, file_name=f"{stick.set_name}.{file_extension}"
    )
    await message.reply_to_message.reply_document(
        document=pat,
        caption=f"📂 **File Name:** `{stick.set_name}.{file_extension}`\n📦 **File Size:** `{stick.file_size}`\n📆 **File Date:** `{stick.date}`\n📤 **File ID:** `{stick.file_id}`",
    )


@app.on_message(filters.command(["gstick", "gstik"]) & ~config.BANNED_USERS)
async def gstick_cmd(client, message):
    reply = message.reply_to_message
    if not reply:
        return await message.reply(">**Reply to a sticker to get its information.**")
    if reply and reply.sticker:
        stick = reply.sticker
        if stick.is_video:
            return await download_and_reply(client, message, stick, "mp4")
        elif stick.is_animated:
            return await message.reply(">**Animated stickers are not supported.**")
        else:
            return await download_and_reply(client, message, stick, "png")
    else:
        return await message.reply(">**Reply to a sticker to get its information.**")


__MODULE__ = "Sticker"
__HELP__ = """
**Add sticker to your pack**
    /kang (reply sticker)

**Add pack to new your pack**
    /addpack (reply sticker)

**Delete sticker from your pack**
    /unkang (reply sticker)

**Get information from sticker with this command**
    /gstik (reply sticker)</blockquote>
"""
