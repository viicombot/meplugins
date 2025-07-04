import json
import random
from pyrogram import filters
from core import app
from config import BANNED_USERS
from utils.database import dB

chat_asah_otak = {}

with open("assets/asah_otak.json", encoding="utf-8") as f:
    SOAL_ASAH_OTAK = json.load(f)


@app.on_message(filters.command(["asahotak", "asah-otak"]) & ~BANNED_USERS)
async def start_asah_otak(client, message):
    chat_id = message.chat.id
    soal = random.choice(SOAL_ASAH_OTAK)
    chat_asah_otak[chat_id] = soal
    return await message.reply_text(f"🧠 Asah Otak:\n\n{soal['soal']}\n\nSilahkan jawab pertanyaan diatas!\n\nKetik `nyerah` jika tidak tahu\nKetik `skip-asahotak` untuk melewati soal.")


@app.on_message(filters.incoming & filters.group & ~BANNED_USERS, group=4)
async def jawab_asah_otak(_, message):
    chat_id = message.chat.id
    if chat_id not in chat_asah_otak:
        return
    text = message.text
    if not text:
        return
    if message.sender_chat:
        return

    soal = chat_asah_otak[chat_id]
    jawaban_benar = soal["jawaban"].lower()
    user_id = message.from_user.id
    point_user = await dB.get_var(user_id, "POINT_ASAHOTAK") or 0

    if text.lower() == "nyerah":
        del chat_asah_otak[chat_id]
        return await message.reply_text(
            f"😢 Jawaban yang benar:\n**{soal['jawaban']}**\n\nSoal tadi:\n{soal['soal']}"
        )

    elif text.lower() == "skip-asahotak":
        soal_baru = random.choice(SOAL_ASAH_OTAK)
        while soal_baru["index"] == soal["index"]:
            soal_baru = random.choice(SOAL_ASAH_OTAK)
        chat_asah_otak[chat_id] = soal_baru
        return await message.reply_text(
            f"➡️ Soal baru:\n\n{soal_baru['soal']}\n\nSilahkan jawab pertanyaan diatas!\n\nKetik `nyerah` jika tidak tahu\nKetik `skip-asahotak` untuk melewati soal."
        )

    elif text.lower() == jawaban_benar.lower():
        del chat_asah_otak[chat_id]
        point = 5 + point_user
        await dB.set_var(user_id, "POINT_ASAHOTAK", point)
        return await message.reply_text(f"✅ Jawaban kamu **benar!** dan mendapatkan {point} point.\nKetik /asahotak buat soal berikutnya.")
    else:
        return await message.reply_text("❌ Jawaban kamu salah, coba mikir lagi yang bener.")
