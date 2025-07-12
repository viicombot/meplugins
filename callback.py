

from core import app
from pyrogram import filters
from utils.database import dB, state
from pyrogram.types import InlineKeyboardButton as Ikb
from pyrogram.types import InlineKeyboardMarkup, InputMediaPhoto


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