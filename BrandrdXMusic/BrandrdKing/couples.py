import os
import random
import html
from datetime import datetime, timedelta
from telegraph import upload_file
from PIL import Image, ImageDraw
from pyrogram import *
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import *
from pyrogram.enums import ParseMode

# BOT FILE NAME
from BrandrdXMusic import app as app
from BrandrdXMusic.mongo.couples_db import _get_image, get_couple

POLICE = [
    [
        InlineKeyboardButton(
            text="💖 ᴍʏ ᴄᴜᴛᴇ ᴅᴇᴠᴇʟᴏᴘᴇʀ 🥀",
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
            message.chat.id, limit=50
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
        img1 = Image.open(p1).convert("RGBA")
        img2 = Image.open(p2).convert("RGBA")

        img = Image.open(
            "BrandrdXMusic/assets/cppicbranded.jpg"
        ).convert("RGBA")

        # PROFILE PHOTO SIZE
        # Background size: 1536 x 1024
        # Circle positions estimated for the supplied background
        photo_size = 340

        img1 = img1.resize(
            (photo_size, photo_size),
            Image.Resampling.LANCZOS,
        )
        img2 = img2.resize(
            (photo_size, photo_size),
            Image.Resampling.LANCZOS,
        )

        # CIRCULAR MASK FOR FIRST PHOTO
        mask = Image.new("L", (photo_size, photo_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse(
            (0, 0, photo_size - 1, photo_size - 1),
            fill=255,
        )

        # CIRCULAR MASK FOR SECOND PHOTO
        mask1 = Image.new("L", (photo_size, photo_size), 0)
        draw = ImageDraw.Draw(mask1)
        draw.ellipse(
            (0, 0, photo_size - 1, photo_size - 1),
            fill=255,
        )

        img1.putalpha(mask)
        img2.putalpha(mask1)

        # FIXED PHOTO POSITIONS FOR THE SUPPLIED BACKGROUND
        img.paste(img1, (235, 316), img1)
        img.paste(img2, (955, 316), img2)

        # SAVE FINAL IMAGE
        img.save(output_file)

        # UPDATE DATE ON EVERY COMMAND
        tomorrow = dt_tom()
        today = datetime.now().strftime("%d/%m/%Y")

        # COLOURFUL CAPTION
        TXT = f"""<b><blockquote>
💖✨ ᴛᴏᴅᴀʏ's sᴇʟᴇᴄᴛᴇᴅ ᴄᴏᴜᴘʟᴇs ✨💖
━━━━━━━━━━━━━━━━━━
👑 <a href="tg://openmessage?user_id={c1_id}">{c1_name}</a>
          💞 ➕ 💞
👑 <a href="tg://openmessage?user_id={c2_id}">{c2_name}</a>
━━━━━━━━━━━━━━━━━━
💘 ᴍᴀᴅᴇ ғᴏʀ ᴇᴀᴄʜ ᴏᴛʜᴇʀ 💘
💕 ɴᴇxᴛ ᴄᴏᴜᴘʟᴇs ᴡɪʟʟ ʙᴇ
🌟 sᴇʟᴇᴄᴛᴇᴅ ᴏɴ: {tomorrow} 🌟
━━━━━━━━━━━━━━━━━━

🥀 ᴍʏ ᴄᴜᴛᴇ ᴅᴇᴠᴇʟᴏᴘᴇʀ 🥀
</blockquote></b>"""

        # SEND COUPLES IMAGE
        await message.reply_photo(
            output_file,
            caption=TXT,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(POLICE),
        )

        await msg.delete()
        msg = None

        # UPLOAD TO TELEGRAPH
        a = upload_file(output_file)

        for x in a:
            img_url = "https://graph.org/" + x

            couple = {
                "c1_id": c1_id,
                "c2_id": c2_id,
            }

            # Original database saving remains disabled
            # await save_couple(cid, today, couple, img_url)

    except Exception as e:
        print(f"Couples Error
