import os
import random
import html
from datetime import datetime, timedelta

from telegraph import upload_file
from PIL import Image, ImageDraw
from pyrogram import *
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatType, ParseMode

# BOT FILE NAME
from BrandrdXMusic import app as app
from BrandrdXMusic.mongo.couples_db import _get_image, get_couple


POLICE = [
    [
        InlineKeyboardButton(
            text="🥀 ᴍʏ ᴄᴜᴛᴇ ᴅᴇᴠᴇʟᴏᴘᴇʀ 🥀",
            url="https://t.me/BRANDED_PAID_CC",
        ),
    ],
]


def dt():
    now = datetime.now()
    return [
        now.strftime("%d/%m/%Y %H:%M"),
        now.strftime("%d/%m/%Y"),
    ]


def dt_tom():
    return (
        datetime.now() + timedelta(days=1)
    ).strftime("%d/%m/%Y")


@app.on_message(filters.command("couples"))
async def ctest(_, message):
    cid = message.chat.id

    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(
            "💖 ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs."
        )

    msg = None
    output_file = f"test_{cid}.png"
    p1 = None
    p2 = None

    try:
        # GENERATING MESSAGE
        msg = await message.reply_text(
            "<b>💞 ɢᴇɴᴇʀᴀᴛɪɴɢ ᴄᴏᴜᴘʟᴇs ɪᴍᴀɢᴇ... ✨</b>",
            parse_mode=ParseMode.HTML,
        )

        # GET LIST OF USERS
        list_of_users = []

        async for member in app.get_chat_members(
            cid, limit=50
        ):
            if not member.user.is_bot:
                list_of_users.append(member.user.id)

        if len(list_of_users) < 2:
            await msg.edit_text(
                "❌ ɴᴏᴛ ᴇɴᴏᴜɢʜ ᴜsᴇʀs ᴛᴏ sᴇʟᴇᴄᴛ ᴀ ᴄᴏᴜᴘʟᴇ."
            )
            return

        # SELECT TWO DIFFERENT USERS
        c1_id, c2_id = random.sample(list_of_users, 2)

        # GET USER INFORMATION
        user1 = await app.get_users(c1_id)
        user2 = await app.get_users(c2_id)

        c1_name = html.escape(user1.first_name or "User")
        c2_name = html.escape(user2.first_name or "User")

        # GET PROFILE PHOTOS
        photo1 = (await app.get_chat(c1_id)).photo
        photo2 = (await app.get_chat(c2_id)).photo

        try:
            if not photo1:
                raise ValueError("First user has no profile photo")

            p1 = await app.download_media(
                photo1.big_file_id,
                file_name="pfp.png",
            )
        except Exception:
            p1 = "BrandrdXMusic/assets/upic.png"

        try:
            if not photo2:
                raise ValueError("Second user has no profile photo")

            p2 = await app.download_media(
                photo2.big_file_id,
                file_name="pfp1.png",
            )
        except Exception:
            p2 = "BrandrdXMusic/assets/upic.png"

        # OPEN IMAGES
        with Image.open(p1) as source:
            img1 = source.convert("RGBA")

        with Image.open(p2) as source:
            img2 = source.convert("RGBA")

        with Image.open(
            "BrandrdXMusic/assets/cppicbranded.jpg"
        ) as source:
            img = source.convert("RGBA")

        # PROFILE PHOTO SIZE AND POSITIONS
        # Coordinates are for the supplied 1536 x 1024 background.
        photo_size = 340

        img1 = img1.resize(
            (photo_size, photo_size),
            Image.Resampling.LANCZOS,
        )
        img2 = img2.resize(
            (photo_size, photo_size),
            Image.Resampling.LANCZOS,
        )

        # CIRCULAR MASK
        mask = Image.new("L", (photo_size, photo_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse(
            (0, 0, photo_size - 1, photo_size - 1),
            fill=255,
        )

        img1.putalpha(mask)
        img2.putalpha(mask.copy())

        # PASTE PROFILE PHOTOS
        # Adjust these coordinates if the source background differs.
        img.paste(img1, (235, 316), img1)
        img.paste(img2, (955, 316), img2)

        # SAVE IMAGE
        img.save(output_file, format="PNG")

        # CALCULATE TOMORROW'S DATE AT COMMAND TIME
        tomorrow = dt_tom()
        today = datetime.now().strftime("%d/%m/%Y")

        # COLOURFUL CAPTION
        TXT = f"""<b><blockquote>
💖 ᴛᴏᴅᴀʏ's sᴇʟᴇᴄᴛᴇᴅ ᴄᴏᴜᴘʟᴇs ✨
━━━━━━━━━━━━━━━━━━
👑 <a href="tg://openmessage?user_id={c1_id}">{c1_name}</a>
          💞 ➕ 💞
👑 <a href="tg://openmessage?user_id={c2_id}">{c2_name}</a>
━━━━━━━━━━━━━━━━━━
💘 ɴᴇxᴛ ᴄᴏᴜᴘʟᴇs ᴡɪʟʟ ʙᴇ
🌟 sᴇʟᴇᴄᴛᴇᴅ ᴏɴ: {tomorrow} 🌟
━━━━━━━━━━━━━━━━━━
</blockquote></b>"""

        # SEND COUPLES IMAGE
        await message.reply_photo(
            output_file,
            caption=TXT,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(POLICE),
        )

        # DELETE GENERATING MESSAGE
        try:
            await msg.delete()
        except Exception:
            pass
        msg = None

        # UPLOAD TO TELEGRAPH
        # upload_file is synchronous, so run it in a worker thread.
        import asyncio
        uploaded_files = await asyncio.to_thread(
            upload_file, output_file
        )

        for x in uploaded_files:
            img_url = "https://graph.org/" + x

            couple = {
                "c1_id": c1_id,
                "c2_id": c2_id,
            }

            # Database saving remains disabled, as in your original code.
            # await save_couple(cid, today, couple, img_url)

    except Exception as e:
        print(f"Couples Error: {e}")

        if msg:
            try:
                await msg.edit_text(
                    "❌ ᴄᴏᴜᴘʟᴇs ɪᴍᴀɢᴇ ɢᴇɴᴇʀᴀᴛɪᴏɴ ғᴀɪʟᴇᴅ."
                )
            except Exception:
                pass

    finally:
        # CLEAN UP TEMPORARY FILES
        for path in (
            p1,
            p2,
            output_file,
            "./downloads/pfp.png",
            "./downloads/pfp1.png",
        ):
            try:
                if path and os.path.isfile(path):
                    os.remove(path)
            except Exception:
                pass
