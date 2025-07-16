from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import BANNED_USERS
from core import app
from utils.fonts import Fonts

__MODULE__ = "Fonts"

__HELP__ = """
<blockquote expandable>

🔤 <b>Stylish Fonts</b>

• <b>/font</b> or <b>/fonts</b> [reply text] – Convert your text or caption into cool fonts.

</blockquote>
"""


FONT_MAP = {
    "typewriter": Fonts.typewriter,
    "outline": Fonts.outline,
    "serif": Fonts.serief,
    "bold_cool": Fonts.bold_cool,
    "cool": Fonts.cool,
    "small_cap": Fonts.smallcap,
    "script": Fonts.script,
    "script_bolt": Fonts.bold_script,
    "tiny": Fonts.tiny,
    "comic": Fonts.comic,
    "sans": Fonts.san,
    "slant_sans": Fonts.slant_san,
    "slant": Fonts.slant,
    "sim": Fonts.sim,
    "circles": Fonts.circles,
    "circle_dark": Fonts.dark_circle,
    "gothic": Fonts.gothic,
    "gothic_bolt": Fonts.bold_gothic,
    "cloud": Fonts.cloud,
    "happy": Fonts.happy,
    "sad": Fonts.sad,
    "special": Fonts.special,
    "squares": Fonts.square,
    "squares_bold": Fonts.dark_square,
    "andalucia": Fonts.andalucia,
    "manga": Fonts.manga,
    "stinky": Fonts.stinky,
    "bubbles": Fonts.bubbles,
    "underline": Fonts.underline,
    "ladybug": Fonts.ladybug,
    "rays": Fonts.rays,
    "birds": Fonts.birds,
    "slash": Fonts.slash,
    "stop": Fonts.stop,
    "skyline": Fonts.skyline,
    "arrows": Fonts.arrows,
    "qvnes": Fonts.rvnes,
    "strike": Fonts.strike,
    "frozen": Fonts.frozen,
}

PAGE_1 = [
    [InlineKeyboardButton("𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛", callback_data="fontclick+typewriter"),
     InlineKeyboardButton("𝕆𝕦𝕥𝕝𝕚𝕟𝕖", callback_data="fontclick+outline"),
     InlineKeyboardButton("𝐒𝐞𝐫𝐢𝐟", callback_data="fontclick+serif")],
    [InlineKeyboardButton("𝑺𝒆𝒓𝒊𝒇", callback_data="fontclick+bold_cool"),
     InlineKeyboardButton("𝑆𝑒𝑟𝑖𝑓", callback_data="fontclick+cool"),
     InlineKeyboardButton("Sᴍᴀʟʟ Cᴀᴘs", callback_data="fontclick+small_cap")],
    [InlineKeyboardButton("𝓈𝒸𝓇𝒾𝓅𝓉", callback_data="fontclick+script"),
     InlineKeyboardButton("𝓼𝓬𝓻𝓲𝓹𝓽", callback_data="fontclick+script_bolt"),
     InlineKeyboardButton("ᵗⁱⁿʸ", callback_data="fontclick+tiny")],
    [InlineKeyboardButton("ᑕOᗰIᑕ", callback_data="fontclick+comic"),
     InlineKeyboardButton("𝗦𝗮𝗻𝘀", callback_data="fontclick+sans"),
     InlineKeyboardButton("𝙎𝙖𝙣𝙨", callback_data="fontclick+slant_sans")],
    [InlineKeyboardButton("𝘚𝘢𝘯𝘴", callback_data="fontclick+slant"),
     InlineKeyboardButton("𝖲𝖺𝗇𝗌", callback_data="fontclick+sim"),
     InlineKeyboardButton("Ⓒ︎Ⓘ︎Ⓡ︎Ⓒ︎Ⓛ︎Ⓔ︎Ⓢ︎", callback_data="fontclick+circles")],
    [InlineKeyboardButton("🅒︎🅘︎🅡︎🅒︎🅛︎🅔︎🅢︎", callback_data="fontclick+circle_dark"),
     InlineKeyboardButton("𝔊𝔬𝔱𝔥𝔦𝔠", callback_data="fontclick+gothic"),
     InlineKeyboardButton("𝕲𝖔𝖙𝖍𝖎𝖈", callback_data="fontclick+gothic_bolt")],
    [InlineKeyboardButton("C͜͡l͜͡o͜͡u͜͡d͜͡s͜͡", callback_data="fontclick+cloud"),
     InlineKeyboardButton("H̆̈ă̈p̆̈p̆̈y̆̈", callback_data="fontclick+happy"),
     InlineKeyboardButton("S̑̈ȃ̈d̑̈", callback_data="fontclick+sad")],
    [InlineKeyboardButton("Next", callback_data="pagefont")]
]

PAGE_2 = [
    [InlineKeyboardButton("🇸 🇵 🇪 🇨 🇮 🇦 🇱 ", callback_data="fontclick+special"),
     InlineKeyboardButton("🅂🅀🅄🄰🅁🄴🅂", callback_data="fontclick+squares"),
     InlineKeyboardButton("🆂︎🆀︎🆄︎🅰︎🆁︎🅴︎🆂︎", callback_data="fontclick+squares_bold")],
    [InlineKeyboardButton("ꪖꪀᦔꪖꪶꪊᥴ𝓲ꪖ", callback_data="fontclick+andalucia"),
     InlineKeyboardButton("爪卂几ᘜ卂", callback_data="fontclick+manga"),
     InlineKeyboardButton("S̾t̾i̾n̾k̾y̾", callback_data="fontclick+stinky")],
    [InlineKeyboardButton("B̥ͦu̥ͦb̥ͦb̥ͦl̥ͦe̥ͦs̥ͦ", callback_data="fontclick+bubbles"),
     InlineKeyboardButton("U͟n͟d͟e͟r͟l͟i͟n͟e͟", callback_data="fontclick+underline"),
     InlineKeyboardButton("꒒ꍏꀷꌩꌃꀎꁅ", callback_data="fontclick+ladybug")],
    [InlineKeyboardButton("R҉a҉y҉s҉", callback_data="fontclick+rays"),
     InlineKeyboardButton("B҈i҈r҈d҈s҈", callback_data="fontclick+birds"),
     InlineKeyboardButton("S̸l̸a̸s̸h̸", callback_data="fontclick+slash")],
    [InlineKeyboardButton("s⃠t⃠o⃠p⃠", callback_data="fontclick+stop"),
     InlineKeyboardButton("S̺͆k̺͆y̺͆l̺͆i̺͆n̺͆e̺͆", callback_data="fontclick+skyline"),
     InlineKeyboardButton("A͎r͎r͎o͎w͎s͎", callback_data="fontclick+arrows")],
    [InlineKeyboardButton("ዪሀክቿነ", callback_data="fontclick+qvnes"),
     InlineKeyboardButton("S̶t̶r̶i̶k̶e̶", callback_data="fontclick+strike"),
     InlineKeyboardButton("F༙r༙o༙z༙e༙n༙", callback_data="fontclick+frozen")],
    [InlineKeyboardButton("Prev", callback_data="pagefont+0")]
]

@app.on_message(filters.command(["font", "fonts"]) & ~BANNED_USERS)
async def show_fonts(_, message):
    text = message.reply_to_message.text or message.reply_to_message.caption
    if not message.reply_to_message:
        return await message.reply(">**Reply to a message containing text to apply font style.**")
    return await message.reply(
        text,
        reply_markup=InlineKeyboardMarkup(PAGE_1)
    )

@app.on_callback_query(filters.regex("^pagefont"))
async def handle_pagination(_, callback_query):
    data = callback_query.data
    await callback_query.answer()
    if data == "pagefont":
        return await callback_query.message.edit_reply_markup(InlineKeyboardMarkup(PAGE_2))
    elif data == "pagefont+0":
        return await callback_query.message.edit_reply_markup(InlineKeyboardMarkup(PAGE_1))


@app.on_callback_query(filters.regex(r"^fontclick\+"))
async def apply_font(_, callback_query):
    await callback_query.answer()
    _, font_key = callback_query.data.split("+", 1)
    formatter = FONT_MAP.get(font_key)

    if not formatter:
        return await callback_query.message.reply("Font not found.")

    if not callback_query.message.text:
        return await callback_query.message.reply("Text not found to apply font.")

    styled_text = formatter(callback_query.message.text)
    await callback_query.message.edit_text(styled_text)
