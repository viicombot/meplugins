

from core import app
from pyrogram import filters, errors
from utils.database import dB, state
from pyrogram.types import InlineKeyboardButton as Ikb
from pyrogram.types import InlineKeyboardMarkup, InputMediaAnimation, InputMediaAudio, InputMediaDocument, InputMediaPhoto, InputMediaVideo
from utils.keyboard import Button
from utils.functions import Tools


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


@app.on_callback_query(filters.regex(r"^alertcb_"))
async def callback_alert(client, callback_query):
    uniq = callback_query.data.split("_")[1]
    alert_text = await dB.get_var(uniq, f"{uniq}")
    if len(alert_text) > 200:
        return await callback_query.answer(
            "Alert text is too long, please keep it under 200 characters.",
            show_alert=True,
        )
    if r"\n" in alert_text:
        alert_text = alert_text.replace(r"\n", "\n")
    return await callback_query.answer(text=alert_text, show_alert=True)


@app.on_callback_query(filters.regex(r"^nextpinterest_"))
async def nextpin_search(_, callback_query):
    data = callback_query.data.split("_")
    page = int(data[1])
    uniq = str(data[2])
    photos = state.get(uniq, "pinterest")
    if not photos:
        await callback_query.answer("Tidak ada foto untuk ditampilkan.", True)
        return
    total_photos = len(photos)
    if page < 0 or page >= total_photos:
        await callback_query.answer("Halaman tidak ditemukan.", True)
        return

    buttons = []
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            Ikb("⬅️ Prev", callback_data=f"nextpinterest_{page - 1}_{uniq}")
        )
    if page < total_photos - 1:
        nav_buttons.append(
            Ikb("➡️ Next", callback_data=f"nextpinterest_{page + 1}_{uniq}")
        )

    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append([Ikb("❌ Close", callback_data=f"close inline_pinsearch {uniq}")])

    reply_markup = InlineKeyboardMarkup(buttons)

    await callback_query.edit_message_media(
        media=InputMediaPhoto(media=photos[page]), reply_markup=reply_markup
    )



@app.on_callback_query(filters.regex(r"^cbnotes_"))
async def notes_callback(client, callback_query):
    data = callback_query.data.split("_")
    chat_id = callback_query.message.chat.id
    type_mapping = {
        "photo": InputMediaPhoto,
        "video": InputMediaVideo,
        "animation": InputMediaAnimation,
        "audio": InputMediaAudio,
        "document": InputMediaDocument,
    }
    try:
        notetag = data[-2].replace("cbnotes_", "")
        print(f"Tag: {notetag}")
        noteval = await dB.get_var(chat_id, notetag, "NOTES")
        if not noteval:
            await callback_query.answer("Catatan tidak ditemukan.", True)
            return
        
        original_text = noteval["result"]
        note_type = noteval["type"]
        file_id = noteval["file_id"]
        note, button = Button.parse_msg_buttons(original_text)
        formatted_text = await Tools.escape_filter(callback_query.message, note, Tools.parse_words)
        button = await Button.create_inline_keyboard(button, chat_id)
        try:
            if note_type == "text":
                await callback_query.edit_message_text(
                    text=formatted_text, reply_markup=button
                )

            elif note_type in type_mapping and file_id:
                InputMediaType = type_mapping[note_type]
                media = InputMediaType(media=file_id, caption=formatted_text)
                await callback_query.edit_message_media(
                    media=media, reply_markup=button
                )

            else:
                await callback_query.edit_message_caption(
                    caption=formatted_text, reply_markup=button
                )

        except errors.FloodWait as e:
            return await callback_query.answer(
                f"FloodWait {e}, Please Waiting!!", True
            )
        except errors.MessageNotModified:
            pass

    except Exception as e:
        print(f"Error in notes callback: {str(e)}")
        return await callback_query.answer(
            "Terjadi kesalahan saat memproses catatan.", True
        )