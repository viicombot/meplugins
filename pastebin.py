# Ported from MissKatyPyro
# Original code here https://github.com/yasirarism/MissKatyPyro/blob/master/misskaty/plugins/paste.py


import privatebinapi
import traceback
import config

from telegraph.aio import Telegraph


from os import remove
from re import compile as compiles

from pyrogram import filters
from pyrogram.helpers import ikb

from core import app
from utils.functions import Tools
from platforms import youtube


__MODULE__ = "Paste"
__HELP__ = """
<blockquote expandable>
<b>★ /paste</b> [Text/Reply To Message] - Post text to My Pastebin.
<b>★ /tg</b> [Text/Reply To Message] - Post text to Telegraph.
<b>★ /upl</b> [Images] - Upload image to ImgBB.
"""


pattern = compiles(r"^text/|json$|yaml$|xml$|toml$|x-sh$|x-shellscript$|x-subrip$")


async def post_to_telegraph(is_media: bool, title=None, content=None, media=None):
    telegraph = Telegraph()
    if telegraph.get_access_token() is None:
        await telegraph.create_account(short_name=app.username)
    if is_media:
        # Create a Telegram Post Foto/Video
        response = await telegraph.upload_file(media)
        return f"https://img.yasirweb.eu.org{response[0]['src']}"
    # Create a Telegram Post using HTML Content
    response = await telegraph.create_page(
        title,
        html_content=content,
        author_url=f"https://t.me/{app.username}",
        author_name=app.username,
    )
    return f"https://te.legra.ph/{response['path']}"


@app.on_message(filters.command(["tgraph", "tg"]) & ~config.BANNED_USERS)
async def telegraph_paste(_, message):
    try:
        reply = message.reply_to_message
        if not reply and len(message.command) < 2:
            return await message.reply(f"**Reply To A Message With /{message.command[0]} or with command**")

        if message.from_user:
            if message.from_user.username:
                uname = f"@{message.from_user.username} [{message.from_user.id}]"
            else:
                uname = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id}) [{message.from_user.id}]"
        else:
            uname = message.sender_chat.title
        msg = await message.reply("`Pasting to Telegraph...`")
        data = ""
        limit = 1024 * 1024
        if reply and not (reply.text or reply.document):
            return await msg.edit("**Telegraph upload has been disabled by Durov, use ImgBB command instead.**")
        if reply and reply.document:
            if reply.document.file_size > limit:
                return await msg.edit(
                    f"**You can only paste files smaller than {youtube.humanbytes(limit)}.**"
                )
            if not pattern.search(reply.document.mime_type):
                return await msg.edit("**Only text files can be pasted.**")
            file = await reply.download()
            title = (
                message.text.split(None, 1)[1]
                if len(message.command) > 1
                else "MissKaty Paste"
            )
            try:
                with open(file, "r") as text:
                    data = text.read()
                remove(file)
            except UnicodeDecodeError:
                try:
                    remove(file)
                except:
                    pass
                return await msg.edit("`File Not Supported !`")
        elif reply and (reply.text or reply.caption):
            title = (
                message.text.split(None, 1)[1]
                if len(message.command) > 1
                else "MissKaty Paste"
            )
            data = reply.text.html.replace("\n", "<br>") or reply.caption.html.replace(
                "\n", "<br>"
            )
        elif not reply and len(message.command) >= 2:
            title = "MissKaty Paste"
            data = message.text.split(None, 1)[1]

        try:
            url = await post_to_telegraph(False, title, data)
        except Exception as e:
            return await msg.edit(f"ERROR: {e}")

        if not url:
            return await msg.edit("Text Too Short Or File Problems")
        button = ikb([[("Open Link", f"{url}", "url")], [("Share Link", f"https://telegram.me/share/url?url={url}", "url")]])
        pasted = f"**Successfully pasted your data to Telegraph<a href='{url}'>.</a>\n\nPaste by {uname}**"
        return await msg.edit(pasted, reply_markup=button, disable_web_page_preview=True)
    except Exception:
        print(f"ERROR: {traceback.format_exc()}")


@app.on_message(filters.command(["paste"]) & ~config.BANNED_USERS)
async def wastepaste(_, message):
    try:
        reply = message.reply_to_message
        target = str(message.command[0]).split("@", maxsplit=1)[0]
        if not reply and len(message.command) < 2:
            return await message.reply(
                f"**Reply To A Message With /{target} or with command**", del_in=6
            )

        msg = await message.reply("`Pasting to YasirBin...`")
        data = ""
        limit = 1024 * 1024
        if reply and reply.document:
            if reply.document.file_size > limit:
                return await msg.edit(
                    f"**You can only paste files smaller than {youtube.humanbytes(limit)}.**"
                )
            if not pattern.search(reply.document.mime_type):
                return await msg.edit("**Only text files can be pasted.**")
            file = await reply.download()
            try:
                with open(file, "r") as text:
                    data = text.read()
                remove(file)
            except UnicodeDecodeError:
                try:
                    remove(file)
                except:
                    pass
                return await msg.edit("`File Not Supported !`")
        elif reply and (reply.text or reply.caption):
            data = reply.text or reply.caption
        elif not reply and len(message.command) >= 2:
            data = message.text.split(None, 1)[1]

        if message.from_user:
            if message.from_user.username:
                uname = f"@{message.from_user.username} [{message.from_user.id}]"
            else:
                uname = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id}) [{message.from_user.id}]"
        else:
            uname = message.sender_chat.title

        try:
            url = await privatebinapi.send_async("https://bin.yasirweb.eu.org", text=data, expiration="1week", formatting="markdown")
        except Exception as e:
            return await msg.edit(f"ERROR: {e}")

        if not url:
            return await msg.edit("Text Too Short Or File Problems")
        button = ikb([[("Open Link", f"url['full_url']", "url")], [("Share Link", f"https://telegram.me/share/url?url={url['full_url']}", "url")]])

        pasted = f"**Successfully pasted your data to YasirBin<a href='{url}'>.</a>\n\nPaste by {uname}**"
        return await msg.edit(pasted, reply_markup=button, disable_web_page_preview=True)
    except Exception:
        print(f"ERROR: {traceback.format_exc()}")


# ImgBB Upload
@app.on_message(filters.command(["imgbb", "upl"]) & ~config.BANNED_USERS)
async def imgbb_upload(_, message):
    try:
        reply = message.reply_to_message
        if not reply and len(message.command) == 1:
            return await message.reply(
                f"**Reply to a photo with /{message.command[0]} command to upload image on ImgBB.**", del_in=6
            )
        if not (reply.photo or (reply.document and reply.document.mime_type.startswith("image"))):
            return await message.reply("This command only support upload photo")
        msg = await message.reply("`Uploading image to ImgBB...`")
        if message.from_user:
            if message.from_user.username:
                uname = f"@{message.from_user.username}"
            else:
                uname = (
                    f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
                )
        else:
            uname = message.sender_chat.title

        try:
            path = await reply.download()
            data = {"type": "file", "action": "upload"}
            files = {"source": (path, open(path, "rb"), "images/jpeg")}
            headers = {"origin": "https://imgbb.com", "referer": "https://imgbb.com/upload", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42"}
            res = await Tools.fetch.post("https://imgbb.com/json", files=files, data=data, headers=headers)
            remove(path)
            url = f"https://ibb.co.com/{res.json()['image']['id_encoded']}"
            button = ikb([[("Open Link", f"{url}", "url")], [("Share Link", f"https://telegram.me/share/url?url={url}", "url")]])
        
            pasted = f"**Successfully pasted your images to ImgBB<a href='{url}'>.</a>\n\nPaste by {uname}**"
            return await msg.edit(pasted, reply_markup=button, disable_web_page_preview=True)
        except Exception as e:
            return await msg.edit(f"ERROR: {e}")
    except Exception:
        print(f"ERROR: {traceback.format_exc()}")
