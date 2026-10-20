import os
from PIL import Image, ImageDraw, ImageFont
from pyrogram import *
from pyrogram.types import *
from pyrogram.enums import ChatMemberStatus, ParseMode
from logging import getLogger
from html import escape

from BrandrdXMusic import app

LOGGER = getLogger(__name__)

BACKGROUND = "BrandrdXMusic/assets/Brandedwel2.png"
DEFAULT_PIC = "BrandrdXMusic/assets/upic.png"
FONT_PATH = "BrandrdXMusic/assets/font.ttf"
DOWNLOAD_DIR = "downloads"

# Background dimensions: 1536 x 1024
PHOTO_SIZE = 400
PHOTO_POSITION = (842, 326)


class WelDatabase:
    def __init__(self):
        self.data = {}

    async def find_one(self, chat_id):
        return chat_id in self.data

    async def add_wlcm(self, chat_id):
        self.data[chat_id] = {}

    async def rm_wlcm(self, chat_id):
        self.data.pop(chat_id, None)


wlcm = WelDatabase()


class temp:
    ME = None
    CURRENT = 2
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None


def circle(pfp, size=(400, 400)):
    pfp = pfp.convert("RGBA")

    width, height = pfp.size
    side = min(width, height)

    left = (width - side) // 2
    top = (height - side) // 2

    pfp = pfp.crop(
        (left, top, left + side, top + side)
    )

    pfp = pfp.resize(
        size, Image.Resampling.LANCZOS
    )

    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)

    draw.ellipse(
        (0, 0, size[0] - 1, size[1] - 1),
        fill=255
    )

    pfp.putalpha(mask)
    return pfp


def load_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except OSError:
        return ImageFont.load_default()


def fit_text(draw, text, font, max_width):
    """Shorten long text so it fits inside the details panel."""
    while text and draw.textbbox(
        (0, 0), text, font=font
    )[2] > max_width:
        text = text[:-2] + "…"

    return text


def welcomepic(pic, user, chatname, user_id, uname):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    with Image.open(BACKGROUND) as source:
        background = source.convert("RGBA")

    with Image.open(pic) as source:
        pfp = circle(source, (PHOTO_SIZE, PHOTO_SIZE))

    # PROFILE PHOTO
    background.paste(
        pfp,
        PHOTO_POSITION,
        pfp
    )

    # DRAW USER DETAILS
    draw = ImageDraw.Draw(background)

    title_font = load_font(38)
    info_font = load_font(27)

    white = (255, 255, 255, 255)
    pink = (255, 100, 220, 255)
    blue = (80, 190, 255, 255)

    name_text = f"NAME: {user or 'User'}"
    id_text = f"ID: {user_id}"

    username_text = (
        f"USERNAME: @{uname}"
        if uname
        else "USERNAME: No username"
    )

    # Left-side information panel.
    # Adjust these coordinates if your background differs.
    panel_x = 190
    max_text_width = 550

    draw.text(
        (panel_x, 475),
        "USER DETAILS",
        font=title_font,
        fill=pink,
        stroke_width=1,
        stroke_fill=white,
    )

    details = [
        (name_text, white, 535),
        (id_text, blue, 590),
        (username_text, pink, 645),
    ]

    for text, color, y in details:
        text = fit_text(
            draw, text, info_font, max_text_width
        )

        draw.text(
            (panel_x, y),
            text,
            font=info_font,
            fill=color,
        )

    output = os.path.join(
        DOWNLOAD_DIR,
        f"welcome_{user_id}.png"
    )

    background.save(output, "PNG")
    return output


@app.on_chat_member_updated(filters.group, group=-3)
async def greet_group(_, member: ChatMemberUpdated):
    chat_id = member.chat.id

    if not member.new_chat_member:
        return

    if member.old_chat_member:
        return

    if member.new_chat_member.status in {
        ChatMemberStatus.BANNED,
        ChatMemberStatus.LEFT,
        ChatMemberStatus.RESTRICTED,
    }:
        return

    user = member.new_chat_member.user

    if user.is_bot:
        return

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    pic = None
    welcomeimg = None

    downloaded_pic = os.path.join(
        DOWNLOAD_DIR,
        f"pp{user.id}.png"
    )

    try:
        # DOWNLOAD USER PROFILE PHOTO
        try:
            if user.photo:
                pic = await app.download_media(
                    user.photo.big_file_id,
                    file_name=downloaded_pic
                )
        except Exception as e:
            LOGGER.warning(
                "Profile photo download failed: %s", e
            )

        if not pic or not os.path.isfile(pic):
            pic = DEFAULT_PIC

        # REMOVE PREVIOUS WELCOME MESSAGE
        previous = temp.MELCOW.get(
            f"welcome-{chat_id}"
        )

        if previous:
            try:
                await previous.delete()
            except Exception as e:
                LOGGER.warning(
                    "Previous welcome deletion failed: %s",
                    e
                )

        # CREATE WELCOME IMAGE
        welcomeimg = welcomepic(
            pic,
            user.first_name or "User",
            member.chat.title or "Group",
            user.id,
            user.username
        )

        # ESCAPE HTML VALUES
        username = (
            f"@{escape(user.username)}"
            if user.username
            else "ɴᴏ ᴜsᴇʀɴᴀᴍᴇ"
        )

        group_title = escape(
            member.chat.title or "Group"
        )

        first_name = escape(
            user.first_name or "User"
        )

        caption = (
            f"<b><blockquote>"
            f"💖 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 {group_title} 💖\n"
            f"➖➖➖➖➖➖➖➖\n"
            f"๏ 𝗡𝗔𝗠𝗘 ➠ {first_name}\n"
            f"๏ 𝗜'𝗗 ➠ <code>{user.id}</code>\n"
            f"๏ 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘 ➠ {username}\n"
            f"๏ 𝗠𝗔𝗗𝗘 𝗕𝗬 ➠ "
            f"<a href=\"https://t.me/BRANDEDKING8\">"
            f"Bʀᴀɴᴅᴇᴅ Kɪɴɢ 📿</a>\n"
            f"➖➖➖➖➖➖➖➖"
            f"</blockquote></b>"
        )

        sent = await app.send_photo(
            chat_id,
            photo=welcomeimg,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⦿ ᴀᴅᴅ ᴍᴇ ⦿",
                            url=(
                                "https://t.me/"
                                "Systumm_music_bot"
                                "?startgroup=true"
                            )
                        )
                    ]
                ]
            )
        )

        temp.MELCOW[
            f"welcome-{chat_id}"
        ] = sent

    except Exception as e:
        LOGGER.exception(
            "Welcome image error for user %s: %s",
            user.id,
            e
        )

    finally:
        # CLEAN TEMPORARY FILES
        for path in (welcomeimg, downloaded_pic):
            try:
                if path and os.path.isfile(path):
                    os.remove(path)
            except Exception:
                pass


@app.on_message(
    filters.new_chat_members & filters.group,
    group=-1
)
async def bot_wel(_, message):
    me = await app.get_me()

    for user in message.new_chat_members:
        if user.id != me.id:
            continue

        username = (
            f"@{message.chat.username}"
            if message.chat.username
            else "ᴘʀɪᴠᴀᴛᴇ ɢʀᴏᴜᴘ"
        )

        log_text = (
            f"<b><blockquote>"
            f"📝 𝗡𝗘𝗪 𝗚𝗥𝗢𝗨𝗣\n"
            f"➖➖➖➖➖➖➖➖\n"
            f"𝗡𝗔𝗠𝗘: {escape(message.chat.title or 'Group')}\n"
            f"𝗜'𝗗: <code>{message.chat.id}</code>\n"
            f"𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘: {escape(username)}\n"
            f"➖➖➖➖➖➖➖➖"
            f"</blockquote></b>"
        )

        try:
            await app.send_message(
                LOG_CHANNEL_ID,
                log_text,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            LOGGER.error(
                "Could not send group log: %s", e
            )
