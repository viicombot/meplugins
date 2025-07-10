import aiofiles
import aiohttp
import os
import io
import random
import config

from core import app
from pyrogram import filters
from utils.functions import Tools

class QuotlyException(Exception):
    pass


class Quotly:
    colors = [
        "White",
        "Navy",
        "DarkBlue",
        "MediumBlue",
        "Blue",
        "DarkGreen",
        "Green",
        "Teal",
        "DarkCyan",
        "DeepSkyBlue",
        "DarkTurquoise",
        "MediumSpringGreen",
        "Lime",
        "SpringGreen",
        "Aqua",
        "Cyan",
        "MidnightBlue",
        "DodgerBlue",
        "LightSeaGreen",
        "ForestGreen",
        "SeaGreen",
        "DarkSlateGray",
        "DarkSlateGrey",
        "LimeGreen",
        "MediumSeaGreen",
        "Turquoise",
        "RoyalBlue",
        "SteelBlue",
        "DarkSlateBlue",
        "MediumTurquoise",
        "Indigo  ",
        "DarkOliveGreen",
        "CadetBlue",
        "CornflowerBlue",
        "RebeccaPurple",
        "MediumAquaMarine",
        "DimGray",
        "DimGrey",
        "SlateBlue",
        "OliveDrab",
        "SlateGray",
        "SlateGrey",
        "LightSlateGray",
        "LightSlateGrey",
        "MediumSlateBlue",
        "LawnGreen",
        "Chartreuse",
        "Aquamarine",
        "Maroon",
        "Purple",
        "Olive",
        "Gray",
        "Grey",
        "SkyBlue",
        "LightSkyBlue",
        "BlueViolet",
        "DarkRed",
        "DarkMagenta",
        "SaddleBrown",
        "DarkSeaGreen",
        "LightGreen",
        "MediumPurple",
        "DarkViolet",
        "PaleGreen",
        "DarkOrchid",
        "YellowGreen",
        "Sienna",
        "Brown",
        "DarkGray",
        "DarkGrey",
        "LightBlue",
        "GreenYellow",
        "PaleTurquoise",
        "LightSteelBlue",
        "PowderBlue",
        "FireBrick",
        "DarkGoldenRod",
        "MediumOrchid",
        "RosyBrown",
        "DarkKhaki",
        "Silver",
        "MediumVioletRed",
        "IndianRed ",
        "Peru",
        "Chocolate",
        "Tan",
        "LightGray",
        "LightGrey",
        "Thistle",
        "Orchid",
        "GoldenRod",
        "PaleVioletRed",
        "Crimson",
        "Gainsboro",
        "Plum",
        "BurlyWood",
        "LightCyan",
        "Lavender",
        "DarkSalmon",
        "Violet",
        "PaleGoldenRod",
        "LightCoral",
        "Khaki",
        "AliceBlue",
        "HoneyDew",
        "Azure",
        "SandyBrown",
        "Wheat",
        "Beige",
        "WhiteSmoke",
        "MintCream",
        "GhostWhite",
        "Salmon",
        "AntiqueWhite",
        "Linen",
        "LightGoldenRodYellow",
        "OldLace",
        "Red",
        "Fuchsia",
        "Magenta",
        "DeepPink",
        "OrangeRed",
        "Tomato",
        "HotPink",
        "Coral",
        "DarkOrange",
        "LightSalmon",
        "Orange",
        "LightPink",
        "Pink",
        "Gold",
        "PeachPuff",
        "NavajoWhite",
        "Moccasin",
        "Bisque",
        "MistyRose",
        "BlanchedAlmond",
        "PapayaWhip",
        "LavenderBlush",
        "SeaShell",
        "Cornsilk",
        "LemonChiffon",
        "FloralWhite",
        "Snow",
        "Yellow",
        "LightYellow",
        "Ivory",
        "Black",
    ]

    async def forward_info(reply):
        if reply.forward_from_chat:
            sid = reply.forward_from_chat.id
            title = reply.forward_from_chat.title
            name = title
        elif reply.forward_from:
            sid = reply.forward_from.id
            try:
                try:
                    name = first_name = reply.forward_from.first_name
                except TypeError:
                    name = "Unknown"
                if reply.forward_from.last_name:
                    last_name = reply.forward_from.last_name
                    name = f"{first_name} {last_name}"
            except AttributeError:
                pass
            title = name
        elif reply.forward_sender_name:
            title = name = sender_name = reply.forward_sender_name
            sid = 0
        elif reply.from_user:
            try:
                sid = reply.from_user.id
                try:
                    name = first_name = reply.from_user.first_name
                except TypeError:
                    name = "Unknown"
                if reply.from_user.last_name:
                    last_name = reply.from_user.last_name
                    name = f"{first_name} {last_name}"
            except AttributeError:
                pass
            title = name
        return sid, title, name

    async def t_or_c(message):
        if message.text:
            return message.text
        elif message.caption:
            return message.caption
        else:
            return ""

    async def get_emoji(message):
        if message.from_user.emoji_status:
            emoji_status = str(message.from_user.emoji_status.custom_emoji_id)
        else:
            emoji_status = ""
        return emoji_status

    async def quotly(payload):
        r = await Tools.fetch.post(
            "https://bot.lyo.su/quote/generate.png", json=payload
        )

        if not r.is_error:
            return r.read()
        else:
            raise QuotlyException(r.json())

    @staticmethod
    async def make_carbonara(
        code: str, bg_color: str, theme: str, language: str
    ):
        url = "https://carbonara.solopov.dev/api/cook"
        json_data = {
            "code": code,
            "paddingVertical": "56px",
            "paddingHorizontal": "56px",
            "backgroundMode": "color",
            "backgroundColor": bg_color,
            "theme": theme,
            "language": language,
            "fontFamily": "Cascadia Code",
            "fontSize": "14px",
            "windowControls": True,
            "widthAdjustment": True,
            "lineNumbers": True,
            "firstLineNumber": 1,
            "name": f"{app.name}-Carbon",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json_data) as resp:
                return io.BytesIO(await resp.read())

    @staticmethod
    async def get_message_content(message):
        if message.text:
            return message.text, "text"
        elif message.document:
            doc = await message.download()
            async with aiofiles.open(doc, mode="r") as f:
                content = await f.read()
            os.remove(doc)
            return content, "document"
        return None, None


@app.on_message(filters.command("q") & ~config.BANNED_USERS)
async def qoutly_cmd(client, message):
    if not message.reply_to_message:
        return await message.reply(f">**Please reply to a message!**")

    pros = await message.reply(">**Please wait making your quotly...**")
    reply_msg = message.reply_to_message
    cmd = message.command[1:]
    print(f"Cmd: {cmd}")

    def get_color(index=0):
        return cmd[index] if len(cmd) > index else random.choice(Quotly.colors)

    try:
        if not cmd:
            payload = {
                "type": "quote",
                "format": "png",
                "backgroundColor": get_color(),
                "messages": [],
            }
            sid, title, name = await Quotly.forward_info(reply_msg)
            messages_json = {
                "entities": Tools.get_msg_entities(reply_msg),
                "avatar": True,
                "from": {
                    "id": sid,
                    "title": title,
                    "name": name,
                    "emoji_status": await Quotly.get_emoji(reply_msg),
                },
                "text": await Quotly.t_or_c(reply_msg),
                "replyMessage": {},
            }
            payload["messages"].append(messages_json)
        elif cmd[0].startswith("@"):
            color = get_color(1)
            include_reply = len(cmd) > 2 and cmd[2] == "-r"
            payload = {
                "type": "quote",
                "format": "png",
                "backgroundColor": color,
                "messages": [],
            }
            username = cmd[0][1:]
            user = await client.get_users(username)
            if user.id in config.OWNER_ID:
                return await pros.edit(f">**You can't quote this user**")

            fake_msg = user
            name = fake_msg.first_name
            if fake_msg.last_name:
                name += f" {fake_msg.last_name}"

            emoji_status = None
            if fake_msg.emoji_status:
                emoji_status = str(fake_msg.emoji_status.custom_emoji_id)

            reply_message = {}
            if include_reply:
                replied = reply_msg.reply_to_message
                replied_name = replied.from_user.first_name
                if replied.from_user.last_name:
                    replied_name += f" {replied.from_user.last_name}"
                emoji_status_reply = None
                if replied.from_user.emoji_status:
                    emoji_status_reply = str(
                        replied.from_user.emoji_status.custom_emoji_id
                    )

                reply_message = {
                    "chatId": replied.from_user.id,
                    "entities": Tools.get_msg_entities(replied),
                    "name": replied_name,
                    "text": replied.text or replied.caption or "",
                    "emoji_status": emoji_status_reply,
                }

            messages_json = {
                "entities": Tools.get_msg_entities(reply_msg),
                "avatar": True,
                "from": {
                    "id": fake_msg.id,
                    "title": name,
                    "name": name,
                    "emoji_status": emoji_status,
                },
                "text": await Quotly.t_or_c(reply_msg),
                "replyMessage": reply_message,
            }

            payload["messages"].append(messages_json)
        elif cmd[0].startswith("-r"):
            replied = reply_msg.reply_to_message
            replied_name = replied.from_user.first_name
            if replied.from_user.last_name:
                replied_name += f" {replied.from_user.last_name}"
            emoji_status = None
            if replied.from_user.emoji_status:
                emoji_status = str(replied.from_user.emoji_status.custom_emoji_id)
            reply_message = {
                "chatId": replied.from_user.id,
                "entities": Tools.get_msg_entities(replied),
                "name": replied_name,
                "text": replied.text or replied.caption or "",
                "emoji_status": emoji_status,
            }
            payload = {
                "type": "quote",
                "format": "png",
                "backgroundColor": get_color(1),
                "messages": [],
            }
            sid, title, name = await Quotly.forward_info(reply_msg)
            messages_json = {
                "entities": Tools.get_msg_entities(reply_msg),
                "avatar": True,
                "from": {
                    "id": sid,
                    "title": title,
                    "name": name,
                    "emoji_status": await Quotly.get_emoji(reply_msg),
                },
                "text": await Quotly.t_or_c(reply_msg),
                "replyMessage": reply_message,
            }
            payload["messages"].append(messages_json)
        elif cmd[0].isdigit():
            payload = {
                "type": "quote",
                "format": "png",
                "backgroundColor": get_color(1),
                "messages": [],
                "scale": 2,
            }
            sid, title, name = await Quotly.forward_info(reply_msg)
            messages_json = {
                "entities": Tools.get_msg_entities(reply_msg),
                "avatar": True,
                "from": {
                    "id": sid,
                    "title": title,
                    "name": name,
                    "emoji_status": await Quotly.get_emoji(reply_msg),
                },
                "text": await Quotly.t_or_c(reply_msg),
                "replyMessage": {},
            }
            payload["messages"].append(messages_json)
            count = int(cmd[0])
            if count > 10:
                return await pros.edit(f">**Max 10 messages**")
            async for msg in client.get_chat_history(
                reply_msg.chat.id, limit=count, offset_id=reply_msg.id
            ):
                sid, title, name = await Quotly.forward_info(msg)
                messages_json = {
                    "entities": Tools.get_msg_entities(msg),
                    "avatar": True,
                    "from": {
                        "id": sid,
                        "title": title,
                        "name": name,
                        "emoji_status": await Quotly.get_emoji(msg),
                    },
                    "text": await Quotly.t_or_c(msg),
                    "replyMessage": {},
                }
                payload["messages"].append(messages_json)
            payload["messages"].reverse()
        else:
            payload = {
                "type": "quote",
                "format": "png",
                "backgroundColor": cmd[0],
                "messages": [],
            }
            sid, title, name = await Quotly.forward_info(reply_msg)
            messages_json = {
                "entities": Tools.get_msg_entities(reply_msg),
                "avatar": True,
                "from": {
                    "id": sid,
                    "title": title,
                    "name": name,
                    "emoji_status": await Quotly.get_emoji(reply_msg),
                },
                "text": await Quotly.t_or_c(reply_msg),
            }
            payload["messages"].append(messages_json)
        hasil = await Quotly.quotly(payload)
        bio_sticker = io.BytesIO(hasil)
        bio_sticker.name = "biosticker.webp"
        await message.reply_sticker(bio_sticker)
        await pros.delete()

    except Exception as e:
        await pros.edit(f">**ERROR:** `{str(e)}`")

@app.on_message(filters.command("qcolor") & ~config.BANNED_USERS)
async def qcolor_cmd(_, message):
    iymek = f"\n•".join(Quotly.colors)
    jadi = f">**Color for quotly**\n•"
    if len(iymek) > 4096:
        with open("qcolor.txt", "w") as file:
            file.write(iymek)
        await message.reply_document(
            "qcolor.txt", caption=f">**Color for quotly**"
        )
        os.remove("qcolor.txt")
        return
    else:
        return await message.reply(jadi + iymek)
    

__MODULE__ = "Quotly"
__HELP__ = """
<blockquote expandable>
<b>📝 Quote Generator</b>

<b>★ /q</b> [reply] – Quote message with random color.  
<b>★ /q pink</b> [reply] – Quote message with custom color.  
<b>★ /q</b> @username [reply] – Fake quote for a specific user.  
<b>★ /q</b> @username pink -r [reply] – Fake quote with reply & color.  
<b>★ /q</b> -r [reply] – Quote with replies.  
<b>★ /q</b> -r pink [reply] – Quote with replies & color.  
<b>★ /q</b> 5 [reply] – Quote multiple messages.  
<b>★ /q</b> 5 pink [reply] – Multiple quotes with custom color.

<b>★ /qcolor</b> – Show all available quote colors.
</blockquote>
"""
