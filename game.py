import json
import random
from pyrogram import filters
from core import app
from config import BANNED_USERS
from utils.database import dB
from utils.query_group import game_group, tlirik_group, tbendera_group, tkalimat_group, ttekateki_group

__MODULE__ = "Game"
__HELP__ = """
<blockquote expandable>
<b>★ /asahotak</b> - Play asah otak game, test your brains.

<b>★ /tebakkalimat</b> - Play tebak kalimat game, test your brains.

<b>★ /tekateki</b> - Play teka teki game, test your brains.

<b>★ /tebaklirik</b> - Play tebak lirik game, test your brains.

<b>★ /tebakbendera</b> - Play tebak bendera game, test your brains.

<b>★ /pointgame</b> - Check 10 top score game. 

Type `nyerah` if you fool
Type `skip-game` for next question</blockquote>
"""

chat_asah_otak = {}
chat_tebak_lirik = {}
chat_teka_teki = {}
chat_tebak_kalimat = {}
chat_tebak_bendera = {}


with open("assets/asah_otak.json", encoding="utf-8") as f:
    SOAL_ASAH_OTAK = json.load(f)

with open("assets/lirik.json", encoding="utf-8") as f:
    LIRIK_SOAL = json.load(f)

with open("assets/tebak_bendera.json", encoding="utf-8") as f:
    BENDERA_SOAL = json.load(f)

with open("assets/tebak_kalimat.json", encoding="utf-8") as f:
    KALIMAT_SOAL = json.load(f)

with open("assets/tekateki.json", encoding="utf-8") as f:
    TEKATEKI_SOAL = [item["data"] for item in json.load(f) if item["status"]]

async def update_point_user(client, chat_dict, chat_id, user_id, point_key, point_now, command):
    await dB.set_var(user_id, point_key, point_now)
    if user_id not in await dB.get_list_from_var(client.me.id, "DATAGAME"):
        await dB.add_to_var(client.me.id, "DATAGAME", user_id)
    del chat_dict[chat_id]
    return f">✅ Jawaban kamu **benar!** dan mendapatkan {point_now} point.\nKetik /{command} buat soal berikutnya."


@app.on_message(filters.command(["tebakkalimat"]) & ~BANNED_USERS)
async def tebak_kalimat(client, message):
    chat_id = message.chat.id
    soal = random.choice(KALIMAT_SOAL)
    chat_tebak_kalimat[chat_id] = soal
    return await message.reply_text(f">💬 **Tebak Kalimat:**\n\n{soal['soal']}\n\n__Silahkan jawab pertanyaan diatas!\n\nKetik `nyerah` jika tidak tahu\nKetik `skip-tebakkalimat` untuk melewati soal.__")


@app.on_message(filters.command(["tekateki"]) & ~BANNED_USERS)
async def teka_teki(client, message):
    chat_id = message.chat.id
    soal = random.choice(TEKATEKI_SOAL)
    chat_teka_teki[chat_id] = soal
    return await message.reply_text(f">🧩 **Teka-Teki:**\n\n{soal['pertanyaan']}\n\n__Silahkan jawab pertanyaan diatas!\n\nKetik `nyerah` jika tidak tahu\nKetik `skip-tekateki` untuk melewati soal.__")


@app.on_message(filters.command(["tebaklirik"]) & ~BANNED_USERS)
async def tebak_lirik(client, message):
    chat_id = message.chat.id
    soal = random.choice(LIRIK_SOAL)
    chat_tebak_lirik[chat_id] = soal
    return await message.reply_text(f">🎵 **Tebak Lirik:**\n\n{soal['soal']}\n\n__Silahkan jawab pertanyaan diatas!\n\nKetik `nyerah` jika tidak tahu\nKetik `skip-tebaklirik` untuk melewati soal.__")


@app.on_message(filters.command(["tebakbendera"]) & ~BANNED_USERS)
async def tebak_bendera(client, message):
    chat_id = message.chat.id
    soal = random.choice(BENDERA_SOAL)
    chat_tebak_bendera[chat_id] = soal
    return await message.reply_text(f">🚩 **Tebak Bendera:**\n\n{soal['bendera']}\n\n__Silahkan jawab pertanyaan diatas!\n\nKetik `nyerah` jika tidak tahu\nKetik `skip-tebakbendera` untuk melewati soal.__")


@app.on_message(filters.command(["asahotak", "asah-otak"]) & ~BANNED_USERS)
async def start_asah_otak(client, message):
    chat_id = message.chat.id
    soal = random.choice(SOAL_ASAH_OTAK)
    chat_asah_otak[chat_id] = soal
    return await message.reply_text(f">🧠 **Asah Otak:**\n\n{soal['soal']}\n\n__Silahkan jawab pertanyaan diatas!\n\nKetik `nyerah` jika tidak tahu\nKetik `skip-asahotak` untuk melewati soal.__")


@app.on_message(filters.incoming & filters.group & ~BANNED_USERS, group=game_group)
async def jawab_asah_otak(client , message):
    chat_id = message.chat.id
    if chat_id not in chat_asah_otak or not message.text:
        return
    if message.sender_chat:
        return

    soal = chat_asah_otak[chat_id]
    jawaban_benar = soal["jawaban"].lower()
    user_id = message.from_user.id
    point_user = await dB.get_var(user_id, "POINT_ASAHOTAK") or 0
    if message.text.startswith("/"):
        return
    if message.text.lower() == "nyerah":
        del chat_asah_otak[chat_id]
        return await message.reply_text(
            f">😢 **Jawaban yang benar:**\n__{soal['jawaban']}__\n\n**Pertanyaan:**\n__{soal['soal']}__"
        )

    elif message.text.lower() == "skip-asahotak":
        soal_baru = random.choice(SOAL_ASAH_OTAK)
        while soal_baru["index"] == soal["index"]:
            soal_baru = random.choice(SOAL_ASAH_OTAK)
        chat_asah_otak[chat_id] = soal_baru
        return await message.reply_text(
            f">➡️ **Soal baru:**\n\n{soal_baru['soal']}\n\n__Silahkan jawab pertanyaan diatas!\n\nKetik `nyerah` jika tidak tahu\nKetik `skip-asahotak` untuk melewati soal.__"
        )
    elif message.text.lower() == jawaban_benar:
        point = 5 + point_user
        msg = await update_point_user(client, chat_asah_otak, chat_id, user_id, "POINT_ASAHOTAK", point, "asahotak")
        return await message.reply_text(msg)
    else:
        return await message.reply_text(">**❌ Jawaban kamu salah, coba mikir lagi yang bener.**")


@app.on_message(filters.incoming & filters.group & ~BANNED_USERS, group=tlirik_group)
async def jawab_lirik(client, message):
    chat_id = message.chat.id
    if chat_id not in chat_tebak_lirik or not message.text:
        return
    if message.sender_chat:
        return

    text = message.text.lower()
    soal = chat_tebak_lirik[chat_id]
    user_id = message.from_user.id
    if text.startswith("/"):
        return
    if text == "nyerah":
        del chat_tebak_lirik[chat_id]
        return await message.reply_text(
            f">😢 **Jawaban yang benar:**\n__{soal['jawaban']}__\n\n**Pertanyaan:\n**__{soal['soal']}__"
        )
    elif text == "skip-tebaklirik":
        soal_baru = random.choice(LIRIK_SOAL)
        while soal_baru["soal"] == soal["soal"]:
            soal_baru = random.choice(LIRIK_SOAL)
        chat_tebak_lirik[chat_id] = soal_baru
        return await message.reply_text(
            f">**➡️ Soal baru:**\n\n{soal_baru['soal']}\n\n__Ketik `nyerah` jika tidak tahu\nKetik `skip-tebaklirik` untuk lewati soal.__"
        )
    elif text == soal["jawaban"].lower():
        point = 5 + (await dB.get_var(user_id, "POINT_LIRIK") or 0)
        msg = await update_point_user(client, chat_tebak_lirik, chat_id, user_id, "POINT_LIRIK", point, "tebaklirik")
        return await message.reply_text(msg)
    else:
        await message.reply_text(">**❌ Jawaban kamu salah, coba mikir lagi yang bener.**")

@app.on_message(filters.incoming & filters.group & ~BANNED_USERS, group=tbendera_group)
async def jawab_bendera(client, message):
    chat_id = message.chat.id
    if chat_id not in chat_tebak_bendera or not message.text:
        return
    if message.sender_chat:
        return
    text = message.text.lower()
    soal = chat_tebak_bendera[chat_id]
    if text.startswith("/"):
        return
    if text == "nyerah":
        del chat_tebak_bendera[chat_id]
        return await message.reply_text(
            f">😢 Jawaban yang benar:\n**{soal['nama']}**\n\nPertanyaan:\n**{soal['bendera']}**"
        )
    elif text == "skip-tebakbendera":
        soal_baru = random.choice(BENDERA_SOAL)
        while soal_baru["bendera"] == soal["bendera"]:
            soal_baru = random.choice(BENDERA_SOAL)
        chat_tebak_bendera[chat_id] = soal_baru
        return await message.reply_text(
            f">**➡️ Soal baru:**\n\n{soal_baru['bendera']}\n\n__Ketik `nyerah` jika tidak tahu\nKetik `skip-tebakbendera` untuk lewati soal.__"
        )
    elif text == soal["nama"].lower():
        user_id = message.from_user.id
        point = 5 + (await dB.get_var(user_id, "POINT_BENDERA") or 0)
        msg = await update_point_user(client, chat_tebak_bendera, chat_id, user_id, "POINT_BENDERA", point, "tebakbendera")
        return await message.reply_text(msg)
    else:
        await message.reply_text(">**❌ Jawaban kamu salah, coba mikir lagi yang bener.**")


@app.on_message(filters.incoming & filters.group & ~BANNED_USERS, group=tkalimat_group)
async def jawab_kalimat(client, message):
    chat_id = message.chat.id
    if chat_id not in chat_tebak_kalimat or not message.text:
        return
    if message.sender_chat:
        return
    soal = chat_tebak_kalimat[chat_id]
    text = message.text.lower()
    if text.startswith("/"):
        return
    if text == "nyerah":
        del chat_tebak_kalimat[chat_id]
        return await message.reply_text(
            f">😢 **Jawaban yang benar:**\n__{soal['jawaban']}__\n\n**Pertanyaan:**\n__{soal['soal']}__"
        )
    elif text == "skip-tebakkalimat":
        soal_baru = random.choice(KALIMAT_SOAL)
        while soal_baru["index"] == soal["index"]:
            soal_baru = random.choice(KALIMAT_SOAL)
        chat_tebak_kalimat[chat_id] = soal_baru
        return await message.reply_text(
            f">➡️ **Soal baru:**\n\n{soal_baru['soal']}\n\n__Silahkan jawab pertanyaan diatas!\n\nKetik `nyerah` jika tidak tahu\nKetik `skip-tebakkalimat` untuk melewati soal.__"
        )
    elif text == soal["jawaban"].lower():
        user_id = message.from_user.id
        point = 5 + (await dB.get_var(user_id, "POINT_KALIMAT") or 0)
        msg = await update_point_user(client, chat_tebak_kalimat, chat_id, user_id, "POINT_KALIMAT", point, "tebakkalimat")
        return await message.reply_text(msg)
    else:
        await message.reply_text(">**❌ Jawaban kamu salah, coba mikir lagi yang bener.**")

@app.on_message(filters.incoming & filters.group & ~BANNED_USERS, group=ttekateki_group)
async def jawab_tekateki(client, message):
    chat_id = message.chat.id
    if chat_id not in chat_teka_teki or not message.text:
        return
    if message.sender_chat:
        return
    soal = chat_teka_teki[chat_id]
    text = message.text.lower()
    if text.startswith("/"):
        return
    if text == "nyerah":
        del chat_teka_teki[chat_id]
        return await message.reply_text(
            f">😢 **Jawaban yang benar:**\n__{soal['jawaban']}__\n\n**Pertanyaan:**\n__{soal['pertanyaan']}__"
        )
    elif text == "skip-tekateki":
        soal_baru = random.choice(TEKATEKI_SOAL)
        while soal_baru["pertanyaan"] == soal["pertanyaan"]:
            soal_baru = random.choice(TEKATEKI_SOAL)
        chat_teka_teki[chat_id] = soal_baru
        return await message.reply_text(
            f">➡️ **Soal baru:**\n\n{soal_baru['pertanyaan']}\n\n__Silahkan jawab pertanyaan diatas!\n\nKetik `nyerah` jika tidak tahu\nKetik `skip-tekateki` untuk melewati soal.__"
        )
    elif text == soal["jawaban"].lower():
        user_id = message.from_user.id
        point = 5 + (await dB.get_var(user_id, "POINT_TEKATEKI") or 0)
        msg = await update_point_user(client, chat_teka_teki, chat_id, user_id, "POINT_TEKATEKI", point, "tekateki")
        return await message.reply_text(msg)
    else:
        await message.reply_text(">**❌ Jawaban kamu salah, coba mikir lagi yang bener.**")


@app.on_message(filters.command("pointgame") & ~BANNED_USERS)
async def leaderboard_game(client, message):
    user_ids = await dB.get_list_from_var(client.me.id, "DATAGAME")
    if not user_ids:
        return await message.reply_text("❌ Belum ada data pemain game.")

    leaderboard = []
    for user_id in user_ids:
        total = 0
        for key in [
            "POINT_ASAHOTAK", "POINT_LIRIK", "POINT_BENDERA",
            "POINT_KALIMAT", "POINT_TEKATEKI"
        ]:
            total += await dB.get_var(user_id, key) or 0
        leaderboard.append((user_id, total))

    top10 = sorted(leaderboard, key=lambda x: x[1], reverse=True)[-10:]
    top10 = list(reversed(top10))

    emoji_rank = [
        "🔟", "9️⃣", "8️⃣", "7️⃣", "6️⃣",
        "5️⃣", "4️⃣", "3️⃣", "🥈", "🥇"
    ]

    text = "**🏆 Peringkat 10 Besar Game:**\n\n"
    for i, (uid, point) in enumerate(top10):
        try:
            user = await client.get_users(uid)
            name = user.mention
        except:
            name = f"`{uid}`"
        text += f"{emoji_rank[i]} {name} - **{point}** poin\n"

    return await message.reply_text(text)
