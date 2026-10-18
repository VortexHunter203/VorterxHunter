import asyncio

from pyrogram import filters
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import InlineKeyboardMarkup, Message

from BrandrdXMusic import app
from BrandrdXMusic.utils.database import (
    autoplay_off,
    autoplay_on,
    is_active_chat,
    is_autoplay,
)
from BrandrdXMusic.utils.decorators.admins import (
    ActualAdminCB,
    AdminRightsCheckAnyTime,
)
from BrandrdXMusic.utils.formatters import with_autoplay_status
from BrandrdXMusic.utils.inline.play import autoplay_markup
from config import BANNED_USERS


def _autoplay_command_text(mode: bool) -> str:
    status = "ON ✅" if mode else "OFF ❌"

    return (
        "🔁 Autoplay\n\n"
        f"Current status: {status}\n\n"
        "When Autoplay is ON, the bot automatically queues and plays a related "
        "track once the current queue runs out, instead of leaving the voice chat."
    )


async def _reply_with_floodwait(message, text, reply_markup=None):
    """Send a reply and retry once if Telegram requests a cooldown."""
    try:
        return await message.reply_text(
            text,
            reply_markup=reply_markup,
        )
    except FloodWait as e:
        await asyncio.sleep(e.value)

    try:
        return await message.reply_text(
            text,
            reply_markup=reply_markup,
        )
    except FloodWait:
        return None


async def _edit_with_floodwait(edit_func, *args, **kwargs):
    """Edit a message and handle Telegram FloodWait safely."""
    try:
        return await edit_func(*args, **kwargs)
    except MessageNotModified:
        return None
    except FloodWait as e:
        await asyncio.sleep(e.value)

    try:
        return await edit_func(*args, **kwargs)
    except (FloodWait, MessageNotModified):
        return None


@app.on_message(filters.command(["autoplay"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheckAnyTime
async def autoplay_command(client, message: Message, _, chat_id):
    mode = await is_autoplay(chat_id)
    markup = InlineKeyboardMarkup([autoplay_markup(chat_id, mode)])

    await _reply_with_floodwait(
        message,
        _autoplay_command_text(mode),
        reply_markup=markup,
    )


@app.on_callback_query(
    filters.regex(r"^autoplay ") & ~BANNED_USERS
)
@ActualAdminCB
async def autoplay_toggle(client, CallbackQuery, _):
    try:
        chat_id = int(CallbackQuery.data.split(None, 1)[1])
    except (ValueError, IndexError):
        await CallbackQuery.answer(
            "Invalid autoplay request.",
            show_alert=True,
        )
        return

    # Read current status and toggle it.
    mode = await is_autoplay(chat_id)

    if mode:
        await autoplay_off(chat_id)
        new_mode = False
        toast = "Autoplay turned OFF"
    else:
        if not await is_active_chat(chat_id):
            await CallbackQuery.answer(
                "No song is currently playing. Play something first, then enable Autoplay.",
                show_alert=True,
            )
            return
        await autoplay_on(chat_id)
        new_mode = True
        toast = "Autoplay turned ON"

    # Answer callback promptly so Telegram stops showing the spinner.
    try:
        await CallbackQuery.answer(toast, show_alert=False)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        try:
            await CallbackQuery.answer(toast, show_alert=False)
        except Exception:
            pass

    message = CallbackQuery.message

    # Update only the autoplay button; preserve other buttons.
    markup = message.reply_markup

    if markup:
        rows = []

        for row in markup.inline_keyboard:
            new_row = []

            for button in row:
                if (
                    button.callback_data
                    and button.callback_data.startswith("autoplay ")
                ):
                    new_row.extend(autoplay_markup(chat_id, new_mode))
                else:
                    new_row.append(button)

            rows.append(new_row)

        markup = InlineKeyboardMarkup(rows)

    # Update caption for photo messages.
    if message.photo:
        base_caption = (
            message.caption.html if message.caption else ""
        )

        new_caption = await with_autoplay_status(
            base_caption,
            chat_id,
        )

        await _edit_with_floodwait(
            message.edit_caption,
            caption=new_caption,
            reply_markup=markup,
        )

    # Update text for normal messages.
    else:
        await _edit_with_floodwait(
            message.edit_text,
            text=_autoplay_command_text(new_mode),
            reply_markup=markup,
        )
