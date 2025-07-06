import config
import pytz
import traceback

from pyrogram.helpers import ikb
from pyrogram import filters
from datetime import datetime, timedelta

from utils.decorators import ONLY_GROUP, ONLY_ADMIN
from core import app

data_dict = {}

def format_absen_list(data):
    if not data:
        return "Belum ada yang hadir."
    return "\n".join([
        f"{i+1}. {u['name']}  ({u['time']})." for i, u in enumerate(data)
    ])


def format_tanggal_indo(dt: datetime) -> str:
    hari = {
        "Monday": "Senin",
        "Tuesday": "Selasa",
        "Wednesday": "Rabu",
        "Thursday": "Kamis",
        "Friday": "Jumat",
        "Saturday": "Sabtu",
        "Sunday": "Minggu",
    }
    bulan = {
        "January": "Januari",
        "February": "Februari",
        "March": "Maret",
        "April": "April",
        "May": "Mei",
        "June": "Juni",
        "July": "Juli",
        "August": "Agustus",
        "September": "September",
        "October": "Oktober",
        "November": "November",
        "December": "Desember",
    }

    nama_hari = hari[dt.strftime("%A")]
    nama_bulan = bulan[dt.strftime("%B")]
    return f"{nama_hari}, tanggal {dt.day} {nama_bulan} {dt.year}"


@app.on_message(filters.command("mulaiabsen") & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def mulai_absen(_, message):
    now = datetime.now(pytz.timezone("Asia/Jakarta"))
    date_str = format_tanggal_indo(now)
    absen_text = f"""{message.chat.title}
Daftar hadir hari {date_str}.


Waktu dalam timezone WIB (UTC+7).
Yang telah hadir, silakan klik tombol HADIR di bawah ini."""
    keyboard = ikb([[("☑️  Hadir", "Hadir")]])
    return await message.reply(absen_text, reply_markup=keyboard)



@app.on_callback_query(filters.regex(r"^Hadir"))
async def hadir_callback(client, callback_query):
    user = callback_query.from_user
    user_id = user.id
    name = user.first_name if not user.last_name else f"{user.first_name} {user.last_name}"
    chat_id = callback_query.message.chat.id
    data = data_dict.get(chat_id)
    existing = next((u for u in data if u["user_id"] == user_id), None)
    if existing:
        data = [u for u in data if u["user_id"] != user_id]
    else:
        now_time = datetime.now(pytz.timezone("Asia/Jakarta")).strftime("%H:%M")
        data_dict[chat_id].append({"user_id": user_id, "name": name, "time": now_time})

    data = sorted(data, key=lambda x: x["time"])
    try:
        now = datetime.now(pytz.timezone("Asia/Jakarta"))
        date_str = format_tanggal_indo(now)
        text = f"""{callback_query.message.chat.title}
Daftar hadir hari {date_str}.

{format_absen_list(data)}

Waktu dalam timezone WIB (UTC+7).
Yang telah hadir, silakan klik tombol HADIR di bawah ini."""

        keyboard = ikb([[("☑️  Hadir", "Hadir")]])
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    except Exception:
        print(f"ERROR: {traceback.format_exc()}")


@app.on_message(filters.command("refresh") & ~config.BANNED_USERS)
@ONLY_GROUP
@ONLY_ADMIN
async def refresh_absen(_, message):
    now = datetime.now(pytz.timezone("Asia/Jakarta"))
    date_str = format_tanggal_indo(now)
    chat_id = message.chat.id
    data = data_dict.get(chat_id)
    data = sorted(data, key=lambda x: x["time"])
    absen_text = f"""{message.chat.title}
Daftar hadir hari {date_str}.


Waktu dalam timezone WIB (UTC+7).
Yang telah hadir, silakan klik tombol HADIR di bawah ini."""
    keyboard = ikb([[("☑️  Hadir", "Hadir")]])
    return await message.reply(absen_text, reply_markup=keyboard)
