import os 
import random
from datetime import datetime 
from telegraph import upload_file
from PIL import Image , ImageDraw
from pyrogram import *
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import *

#BOT FILE NAME
from BrandrdXMusic import app as app
from BrandrdXMusic.mongo.couples_db import _get_image, get_couple

POLICE = [
    [
        InlineKeyboardButton(
            text="ᴍʏ ᴄᴜᴛᴇ ᴅᴇᴠᴇʟᴏᴘᴇʀ  🥀",
            url=f"https://t.me/BRANDED_PAID_CC",
        ),
    ],
]


def dt():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M")
    dt_list = dt_string.split(" ")
    return dt_list
    
def dt():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M")
    dt_list = dt_string.split(" ")
    return dt_list


def dt_tom():
    a = (
        str(int(dt()[0].split("/")[0]) + 1)
        + "/"
        + dt()[0].split("/")[1]
        + "/"
        + dt()[0].split("/")[2]
    )
    return a


tomorrow = str(dt_tom())
today = str(dt()[0])


@app.on_message(filters.command("couples"))
async def ctest(_, message):
    cid = message.chat.id

    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(
            "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs."
        )

    try:
        # is_selected = await get_couple(cid, today)
        # if not is_selected:

        msg = await message.reply_text(
            "ɢᴇɴᴇʀᴀᴛɪɴɢ ᴄᴏᴜᴘʟᴇs ɪᴍᴀɢᴇ..."
        )

        # GET LIST OF USERS
        list_of_users = []

        async for i in app.get_chat_members(message.chat.id, limit=50):
            if not i.user.is_bot:
                list_of_users.append(i.user.id)

        if len(list_of_users) < 2:
            await msg.edit_text(
                "❌ ɴᴏᴛ ᴇɴᴏᴜɢʜ ᴜsᴇʀs ᴛᴏ sᴇʟᴇᴄᴛ ᴀ ᴄᴏᴜᴘʟᴇ."
            )
            return

        c1_id = random.choice(list_of_users)
        c2_id = random.choice(list_of_users)

        while c1_id == c2_id:
            c2_id = random.choice(list_of_users)

        # Get user information
        user1 = await app.get_users(c1_id)
        user2 = await app.get_users(c2_id)

        c1_name = user1.first_name or "User"
        c2_name = user2.first_name or "User"

        N1 = user1.mention
        N2 = user2.mention

        # Get profile photos
        photo1 = (await app.get_chat(c1_id)).photo
        photo2 = (await app.get_chat(c2_id)).photo

        try:
            p1 = await app.download_media(
                photo1.big_file_id,
                file_name="pfp.png"
            )
        except Exception:
            p1 = "BrandrdXMusic/assets/upic.png"

        try:
            p2 = await app.download_media(
                photo2.big_file_id,
                file_name="pfp1.png"
            )
        except Exception:
            p2 = "BrandrdXMusic/assets/upic.png"

        img1 = Image.open(p1).convert("RGBA")
        img2 = Image.open(p2).convert("RGBA")

        img = Image.open(
            "BrandrdXMusic/assets/cppicbranded.jpg"
        ).convert("RGBA")

        img1 = img1.resize((437, 437))
        img2 = img2.resize((437, 437))

        mask = Image.new("L", img1.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse(
            (0, 0) + img1.size,
            fill=255
        )

        mask1 = Image.new("L", img2.size, 0)
        draw = ImageDraw.Draw(mask1)
        draw.ellipse(
            (0, 0) + img2.size,
            fill=255
        )

        img1.putalpha(mask)
        img2.putalpha(mask1)

        img.paste(img1, (116, 160), img1)
        img.paste(img2, (789, 160), img2)

        img.save(f"test_{cid}.png")

        # HTML formatted caption
        TXT = f"""<b><blockquote>
ᴛᴏᴅᴀʏ's sᴇʟᴇᴄᴛᴇᴅ ᴄᴏᴜᴘʟᴇs " 🎉 :
➖➖➖➖➖➖➖➖➖➖
<a href="tg://openmessage?user_id={c1_id}">{c1_name}</a> + <a href="tg://openmessage?user_id={c2_id}">{c2_name}</a> = ❣️
➖➖➖➖➖➖➖➖➖➖
ɴᴇxᴛ ᴄᴏᴜᴘʟᴇꜱ ᴡɪʟʟ ʙᴇ sᴇʟᴇᴄᴛᴇᴅ ᴏɴ {tomorrow} "!!
</blockquote></b>"""

        await message.reply_photo(
            f"test_{cid}.png",
            caption=TXT,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(POLICE),
        )

        await msg.delete()

        a = upload_file(f"test_{cid}.png")

        for x in a:
            img_url = "https://graph.org/" + x
            couple = {
                "c1_id": c1_id,
                "c2_id": c2_id,
            }

            # await save_couple(cid, today, couple, img_url)

        # elif is_selected:
        #     ...

    except Exception as e:
        print(f"Couples Error: {e}")

    finally:
        try:
            os.remove("./downloads/pfp.png")
        except Exception:
            pass

        try:
            os.remove("./downloads/pfp1.png")
        except Exception:
            pass

        try:
            os.remove(f"test_{cid}.png")
        except Exception:
            pass


__mod__ = "COUPLES"

__help__ = """
**» /couples** - Get Todays Couples Of The Group In Interactive View
"""
