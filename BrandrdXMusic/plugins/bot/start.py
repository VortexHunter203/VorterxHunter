import asyncio
import logging
import time

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from BrandrdXMusic import app
from BrandrdXMusic.misc import _boot_
from pyrogram import StopPropagation
from BrandrdXMusic.plugins.sudo.sudoers import sudoers_list
from BrandrdXMusic.plugins.bot.start_logger import send_start_log
from BrandrdXMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
)
from BrandrdXMusic.utils.decorators.language import LanguageStart
from BrandrdXMusic.utils.formatters import get_readable_time
from BrandrdXMusic.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string

LOGGER = logging.getLogger(__name__)


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    if not message.from_user:
        return

    await send_start_log(client, message)
    await add_served_user(message.from_user.id)

    try:
        await message.react("❤")
    except Exception:
        pass

    parts = (message.text or "").split(None, 1)
    if len(parts) > 1:
        name = parts[1]

        if name.startswith("help"):
            keyboard = help_pannel(_)
            await message.reply_sticker(
                "CAACAgUAAxkBAAEQI1RlTLnRAy4h9lOS6jgS5FYsQoruOAAC1gMAAg6ryVcldUr_lhPexzME"
            )
            return await message.reply_photo(
                photo=config.START_IMG_URL,
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )

        if name.startswith("sud"):
            return await sudoers_list(client=client, message=message, _=_)

        if name.startswith("inf"):
            progress = await message.reply_text("🔎")
            try:
                video_id = name.replace("info_", "", 1)
                query = f"https://www.youtube.com/watch?v={video_id}"
                data = await VideosSearch(query, limit=1).next()
                results = data.get("result", [])
                if not results:
                    return await progress.edit_text("❌ ɴᴏ ᴛʀᴀᴄᴋ ғᴏᴜɴᴅ.")

                result = results[0]
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
                searched_text = _["start_6"].format(
                    title, duration, views, published, channellink, channel, app.mention
                )
                keyboard = InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(text=_["S_B_8"], url=link),
                        InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT),
                    ]]
                )
                await progress.delete()
                return await client.send_photo(
                    chat_id=message.chat.id,
                    photo=thumbnail,
                    caption=searched_text,
                    reply_markup=keyboard,
                )
            except Exception:
                LOGGER.exception("START: track information failed")
                try:
                    await progress.edit_text("❌ ғᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ ᴛʀᴀᴄᴋ ɪɴғᴏ.")
                except Exception:
                    pass
                return

    out = private_panel(_)
    welcome = None
    progress = None
    sticker = None
    chat_photo = config.START_IMG_URL

    try:
        welcome = await message.reply_text(
            "𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁𝐚𝐛𝐲 ꨄ︎ {}.. ❣️".format(message.from_user.mention)
        )
        for value in ("🥳", "💥", "🤩", "💌", "💞"):
            try:
                await welcome.edit_text(
                    "𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁𝐚𝐛𝐲 ꨄ {}.. {}".format(message.from_user.mention, value)
                )
            except Exception:
                pass
        await welcome.delete()
        welcome = None

        progress = await message.reply_text("**⚡️ѕ**")
        for frame in (
            "⚡ѕт", "**⚡ѕтα**", "**⚡ѕтαя**", "**⚡ѕтαят**",
            "**⚡ѕтαятι**", "**⚡ѕтαятιи**", "**⚡ѕтαятιиg**",
            "**⚡ѕтαятιиg.**", "**⚡ѕтαятιиg....**",
        ):
            await asyncio.sleep(0.1)
            try:
                await progress.edit_text(frame)
            except Exception:
                pass

        sticker = await message.reply_sticker(
            "CAACAgUAAxkBAAEQI1BlTLmx7PtOO3aPNshEU2gCy7iAFgACNQUAApqMuVeA6eJ50VbvmDME"
        )
        if message.chat.photo:
            try:
                downloaded = await client.download_media(message.chat.photo.big_file_id)
                if downloaded:
                    chat_photo = downloaded
            except Exception:
                LOGGER.exception("START: failed to download user photo")
                chat_photo = "assets/nodp.png"
        else:
            chat_photo = "assets/nodp.png"
    except Exception:
        LOGGER.exception("START: welcome animation failed")
    finally:
        for temporary in (welcome, progress, sticker):
            if temporary is not None:
                try:
                    await temporary.delete()
                except Exception:
                    pass

    try:
        await message.reply_photo(
            photo=chat_photo,
            caption=_["start_2"].format(message.from_user.mention, app.mention),
            reply_markup=InlineKeyboardMarkup(out),
        )
    except Exception:
        LOGGER.exception("START: welcome photo failed; trying default image")
        if chat_photo != config.START_IMG_URL:
            await message.reply_photo(
                photo=config.START_IMG_URL,
                caption=_["start_2"].format(message.from_user.mention, app.mention),
                reply_markup=InlineKeyboardMarkup(out),
            )
        else:
            raise


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
    )
    return await add_served_chat(message.chat.id)


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except Exception:
                    pass
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                await message.reply_photo(
                    photo=config.START_IMG_URL,
                    caption=_["start_3"].format(
                        message.from_user.first_name if message.from_user else "User",
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except Exception:
            LOGGER.exception("START: group welcome failed")
