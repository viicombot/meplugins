import json
import random
from pyrogram import filters
from core import app
from config import BANNED_USERS

chat_asah_otak = {}

with open("assets/asah_otak.json", encoding="utf-8") as f:
    SOAL_ASAH_OTAK = json.load(f)
chat_asah_otak = {}

@app.on_message(filters.command(["asahotak", "asah-otak"]) & ~BANNED_USERS)
async def start_asah_otak(client, message):
    chat_id = message.chat.id
    soal = random.choice(SOAL_ASAH_OTAK)
    chat_asah_otak[chat_id] = soal
    return await message.reply_text(f"🧠 Asah Otak:\n\n{soal['soal']}\n\nBalas dengan jawaban kamu!")


@app.on_message(filters.incoming & filters.group & ~BANNED_USERS)
async def jawab_asah_otak(_, message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in chat_asah_otak:
        return

    soal = chat_asah_otak[chat_id]
    jawaban_benar = soal["jawaban"].lower()

    if text.lower() == "nyerah":
        del chat_asah_otak[chat_id]
        return await message.reply_text(
            f"😢 Jawaban yang benar:\n**{soal['jawaban']}**\n\nSoalnya tadi:\n{soal['soal']}"
        )

    elif text.lower() == "skip-asahotak":
        soal_baru = random.choice(SOAL_ASAH_OTAK)
        while soal_baru["index"] == soal["index"]:
            soal_baru = random.choice(SOAL_ASAH_OTAK)
        chat_asah_otak[chat_id] = soal_baru
        return await message.reply_text(
            f"➡️ Soal baru:\n\n{soal_baru['soal']}\n\nBalas dengan jawaban kamu!"
        )

    elif text.lower() == jawaban_benar.lower():
        del chat_asah_otak[chat_id]
        return await message.reply_text("✅ Jawaban kamu **benar!**\nKetik /asahotak buat soal berikutnya.")
    else:
        return await message.reply_text("❌ Jawaban kamu salah, coba mikir lagi yang bener.")
