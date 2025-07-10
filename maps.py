

from geopy.geocoders import Nominatim
import config
from core import app
from pyrogram import filters

__MODULE__ = "Maps"
__HELP__ = """
<blockquote expandable>
<b>🗺️ Location Lookup</b>

<b>★ /maps</b> (location name or address) – Get the geolocation on the map.
</blockquote>
"""



@app.on_message(filters.command(["maps"]) & ~config.BANNED_USERS)
async def maps_cmd(client, message):
    prompt = client.get_text(message)
    if not prompt:
        return await message.reply(f"><b>Please specify location!!\nExample: `{message.text.split()[0]} Ceger, Pondok Aren Tangerang Selatan`</b>")
    try:
        geolocator = Nominatim(user_agent="User")
        geoloc = geolocator.geocode(prompt)
        if geoloc:
            lon = geoloc.longitude
            lat = geoloc.latitude
            share = await message.reply_location(latitude=lat, longitude=lon)
            return await message.reply(f">**Location for: `{prompt}`.**", reply_to_message_id=share.id,
            )
        else:
            return await message.reply(
                f">**Addres not found!! Please input a valid address.**"
            )
    except Exception as er:
        return await message.reply(f">**ERROR:** {str(er)}")
