

import asyncio
import traceback
import config

import hydrogram
from pyrogram import filters
from pyrogram.helpers import ikb
from pyrogram.errors import FloodWait, UserIsBlocked, UserAlreadyParticipant
from pyrogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                            KeyboardButton, ReplyKeyboardMarkup,
                            ReplyKeyboardRemove)
from hydrogram.errors.pyromod import ListenerStopped, ListenerTimeout
from telethon import TelegramClient
from telethon.errors import (ApiIdInvalidError, PasswordHashInvalidError,
                             PhoneCodeExpiredError, PhoneCodeInvalidError,
                             PhoneNumberInvalidError,
                             SessionPasswordNeededError)
from telethon.errors.rpcerrorlist import ChannelPrivateError
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest

from core import app



__MODULE__ = "String-Gen"
__HELP__ = """
<blockquote expandable>
<b>⚙️ /genstring</b> - Start the session string generation process via button.

After clicking, you can choose:
- Pyrogram V2
- Telethon

Then you'll be guided through steps to:
1. Input API ID and API Hash.
2. Submit your phone number.
3. Enter the OTP sent via Telegram.
4. (Optional) Enter 2FA password if enabled.

✅ At the end, your session string will be delivered to your <b>Saved Messages</b>.

<b>Session types supported:</b>
• Pyrogram V2  
• Telethon  

<b>❌ /cancel</b> - Cancel current session generation process anytime.

⚠️ Make sure not to share your session string with anyone.
</blockquote>
"""


chose_button = ikb([[("Telethon", "telethoncb"), ("Pyrogram V2", "pyrogramcb")], [("❎ Close", "close")]])


async def cancelled(message):
    if message.text.startswith("/"):
        await message.reply_text(">Cancelled the ongoing process.", reply_markup=chose_button)
        return True
    else:
        return False

@app.on_callback_query(filters.regex(r"^(pyrogramcb|telethoncb)") & ~config.BANNED_USERS)
async def cb_choose(client, callback):
    query = callback.data
    try:
        if query == "pyrogramcb":
            await gen_session(client, callback.message, callback.from_user.id)
        elif query == "telethoncb":
            await gen_session(client, callback.message, callback.from_user.id, telethon=True)
    except Exception:
        print(f"ERROR: {traceback.format_exc()}")


@app.on_message(filters.command("genstring") & filters.private & ~config.BANNED_USERS)
async def genstring(client, message):
    return await message.reply_text(
        text=f"""
Hello {message.from_user.mention},
I'm {client.mention}

Bot to help you generate your string session, i can generate Pyrogram and Telethon String.

Developed by @{config.OWNER_ANKES}
""",
        reply_markup=chose_button)



async def join_sini(client, telethon: bool = False):
    if config.MUST_JOIN is not None:
        try:
            if telethon:
                try:
                    await client(JoinChannelRequest(config.MUST_JOIN))
                except ChannelPrivateError:
                    pass
                except Exception:
                    pass
            else:
                try:
                    await client.join_chat(config.MUST_JOIN)
                except UserAlreadyParticipant:
                    pass
                except Exception:
                    pass
        except Exception:
            print(f"ERROR: {traceback.format_exc()}")


async def gen_session(client, message, user_id: int, telethon: bool = False):
    await message.delete()
    try:
        if telethon:
            ty = f"Telethon"
        else:
            ty = f"Pyrogram V2"

        try:
            api_id = await client.ask(
                user_id,
                text=">Please send your Api_id to continue\n\npress /cancel for cancel the progress",
                filters=filters.text,
                timeout=300,
            )
        except (ListenerStopped, ListenerTimeout):
            return await client.send_message(
                user_id,
                ">Time limit reached of 5 minutes.\n\nPlease start generating session again.",
                reply_markup=chose_button,
            )

        if await cancelled(api_id):
            return

        try:
            api_id = int(api_id.text)
        except ValueError:
            return await client.send_message(
                user_id,
                ">The Api_id is invalid.\n\nPlease start generating session again.",
                reply_markup=chose_button,
            )

        try:
            api_hash = await client.ask(
                user_id,
                text=">Now send your Api_hash.",
                filters=filters.text,
                timeout=300,
            )
        except (ListenerStopped, ListenerTimeout):
            return await client.send_message(
                user_id,
                ">Time limit reached of 5 minutes.\n\nPlease start generating session again.",
                reply_markup=chose_button,
            )

        api_hash = api_hash.text

        if len(api_hash) < 30:
            return await client.send_message(
                user_id,
                ">The Api_hash is invalid.\n\nPlease start generating session again.",
                reply_markup=chose_button,
            )

        try:
            buttons = ReplyKeyboardMarkup(
                [
                    [KeyboardButton(text="Kontak Saya", request_contact=True)],
                ],
                resize_keyboard=True,
                one_time_keyboard=True,
            )
            phone = await client.ask(
                user_id,
                text=">Please send your phone number click button bellow.",
                filters=filters.contact,
                timeout=300,
                reply_markup=buttons,
            )
            if not phone.contact:
                phone = await client.ask(
                    user_id,
                    text=">Please send your phone number click button bellow.",
                    timeout=300,
                    reply_markup=buttons,
                )
        except (ListenerStopped, ListenerTimeout):
            return await client.send_message(
                user_id,
                ">Time limit reached of 5 minutes.\n\nPlease start generating session again.",
                reply_markup=chose_button,
            )
        phone_number = phone.contact.phone_number

        await client.send_message(
            user_id,
            ">Sending the OTP to your account...",
            reply_markup=ReplyKeyboardRemove(),
        )
        if telethon:
            new_client = TelegramClient(StringSession(), api_id, api_hash, device_model=f"{client.name}")
        else:
            new_client = hydrogram.Client(
                name=user_id,
                api_id=api_id,
                api_hash=api_hash,
                in_memory=True,
                device_model=f"{client.name}",
            )
        await new_client.connect()

        try:
            if telethon:
                code = await new_client.send_code_request(phone_number)
            else:
                code = await new_client.send_code(phone_number)
            await asyncio.sleep(1)

        except FloodWait as f:
            return await client.send_message(
                user_id,
                f">Failed to send the code to you account.\n\nPlease wait for {f.value or f.x} seconds and try again.",
                reply_markup=chose_button,
            )
        except (
            hydrogram.errors.exceptions.bad_request_400.ApiIdInvalid,
            ApiIdInvalidError,
        ):
            return await client.send_message(
                user_id,
                ">The combination of Api_id and Api_hash is invalid.\n\nPlease start generating your session again.",
                reply_markup=chose_button,
            )
        except (
            hydrogram.errors.exceptions.bad_request_400.PhoneNumberInvalid,
            PhoneNumberInvalidError,
        ):
            return await client.send_message(
                user_id,
                ">The Phone number is invalid.\n\nPlease start generating your session again.",
                reply_markup=chose_button,
            )

        try:
            otp = await client.ask(
                user_id,
                text=f">Please send the OTP code that has been sent to {phone_number} in telegram. \nPlease send the code with spaces as in the example, \nExample : <code>1 2 3 4 5</code>.",
                filters=filters.text,
                timeout=600,
            )
            if await cancelled(otp):
                return
        except (ListenerStopped, ListenerTimeout):
            return await client.send_message(
                user_id,
                ">Time limit reached of 10 minutes.\n\nPlease start generating your session again.",
                reply_markup=chose_button,
            )

        otp = otp.text.replace(" ", "")
        try:
            if telethon:
                await new_client.sign_in(phone_number, otp, password=None)
            else:
                await new_client.sign_in(phone_number, code.phone_code_hash, otp)
        except (
            hydrogram.errors.exceptions.bad_request_400.PhoneCodeInvalid,
            PhoneCodeInvalidError,
        ):
            return await client.send_message(
                user_id,
                ">The OTP you send is <b>Wrong.</b>\n\nPlease start generating your session again.",
                reply_markup=chose_button,
            )
        except (
            hydrogram.errors.exceptions.bad_request_400.PhoneCodeExpired,
            PhoneCodeExpiredError,
        ):
            return await client.send_message(
                user_id,
                ">The OTP you send is <b>expired.</b>Make sure you send the otp with the right format.\n\nPlease start generating your session again.",
                reply_markup=chose_button,
            )
        except (
            hydrogram.errors.exceptions.unauthorized_401.SessionPasswordNeeded,
            SessionPasswordNeededError,
        ):
            try:
                pwd = await client.ask(
                    user_id,
                    text=">Please send your two-step verification password to continue.",
                    filters=filters.text,
                    timeout=300,
                )
            except (ListenerStopped, ListenerTimeout):
                return client.send_message(
                    user_id,
                    ">Time limit reached of 5 minutes.\n\nPlease start generating session again.",
                    reply_markup=chose_button,
                )

            if await cancelled(pwd):
                return
            pwd = pwd.text

            try:
                if telethon:
                    await new_client.sign_in(password=pwd)
                else:
                    await new_client.check_password(password=pwd)
            except (
                hydrogram.errors.exceptions.bad_request_400.PasswordHashInvalid,
                PasswordHashInvalidError,
            ):
                return await client.send_message(
                    user_id,
                    ">The password is wrong.\n\nPlease start generating session again.",
                    reply_markup=chose_button,
                )

        except Exception as ex:
            return await client.send_message(user_id, f"Error : <code>{str(ex)}</code>")
        try:
            if "pwd" in locals() and pwd is not None:
                pwds = True
                txt = "📚 <b>Here Is Your {0} String</b>\n\n<b>API_ID</b>:\n<code>{1}</code>\n<b>API_HASH</b>:\n<code>{2}</code>\n<b>PHONE NUMBER</b>:\n<code>{3}</code>\n<b>PASSWORD</b>:\n<code>{4}</code>\n<b>STRING SESSION</b>:\n<code>{5}</code>\n\n<b>Generated by @{6}</b>\n<b>NOTE :</b> Don't share the code to anyone.\n© Credit (@{7})"
            else:
                pwds = False
                txt = "📚 <b>Here Is Your {0} String</b>\n\n<b>API_ID</b>:\n<code>{1}</code>\n<b>API_HASH</b>:\n<code>{2}</code>\n<b>PHONE NUMBER</b>:\n<code>{3}</code>\n<b>STRING SESSION</b>:\n<code>{4}</code>\n\n<b>Generated by @{5}</b>\n<b>NOTE :</b> Don't share the code to anyone.\n© Credit (@{6})"
            usn = "KynanSupport"
            if telethon:
                string_session = new_client.session.save()
                await join_sini(new_client, telethon=True)
                if pwds:
                    await new_client.send_message(
                        "me",
                        txt.format(
                            ty, api_id, api_hash, phone_number, pwd, string_session, usn, config.OWNER_ANKES
                        ),
                        link_preview=False,
                        parse_mode="html",
                    )
                else:
                    await new_client.send_message(
                        "me",
                        txt.format(
                            ty, api_id, api_hash, phone_number, string_session, usn, config.OWNER_ANKES
                        ),
                        link_preview=False,
                        parse_mode="html",
                    )
            else:
                string_session = await new_client.export_session_string()
                await join_sini(new_client)
                if pwds:
                    await new_client.send_message(
                        "me",
                        txt.format(
                            ty, api_id, api_hash, phone_number, pwd, string_session, usn, config.OWNER_ANKES
                        ),
                    )
                else:
                    await new_client.send_message(
                        "me",
                        txt.format(
                            ty, api_id, api_hash, phone_number, string_session, usn, config.OWNER_ANKES
                        ),
                    )
        except KeyError:
            pass
        try:
            await new_client.disconnect()
            await client.send_message(
                chat_id=user_id,
                text=f"<b>Successfully generated your {ty} String Session.</b>\n\nPlease check your Saved Message.\n\n <b>Generated by</b> @{client.username}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Saved Messages",
                                url=f"tg://openmessage?user_id={user_id}",
                            )
                        ]
                    ]
                ),
                disable_web_page_preview=True,
            )
        except Exception as e:
            await client.send_message(chat_id=user_id, text=f"Error occurred: {str(e)}")
    except Exception:
        print(f"ERROR {traceback.format_exc()}")


