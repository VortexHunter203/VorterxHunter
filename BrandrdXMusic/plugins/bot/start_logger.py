
import logging
from html import escape

from pyrogram import enums
from pyrogram.types import Message

import config


LOGGER = logging.getLogger(__name__)


async def send_start_log(client, message: Message):
    """Send private /start notification without interrupting welcome."""

    user = message.from_user

    if not user:
        return

    logger_id = getattr(config, "LOGGER_ID", None)

    if not logger_id:
        LOGGER.error("START LOGGER: LOGGER_ID is missing or zero")
        return

    try:
        logger_id = int(logger_id)

        name = escape(
            " ".join(
                filter(
                    None,
                    [user.first_name, user.last_name]
                )
            ) or "Unknown"
        )

        username = (
            f"@{escape(user.username)}"
            if user.username
            else "No username"
        )

        link = f"tg://user?id={user.id}"

        text = (
            "<b>🎫 ɴᴇᴡ ᴜsᴇʀ ʙᴏᴛ sᴛᴀʀᴛ</b>\n\n"

            "<blockquote>"
            f'👤 <a href="{link}">{name}</a> '
            "ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n"

            f"🆔 <b>ᴜsᴇʀ ɪᴅ :</b> "
            f"<code>{user.id}</code>\n"

            f"🔗 <b>ᴜsᴇʀɴᴀᴍᴇ :</b> "
            f"{username}\n"

            f'👤 <b>ᴘʀᴏғɪʟᴇ :</b> '
            f'<a href="{link}">ᴠɪᴇᴡ ᴜsᴇʀ</a>'
            "</blockquote>"
        )

        await client.send_message(
            chat_id=logger_id,
            text=text,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True,
        )

    except Exception:
        LOGGER.exception(
            "START LOGGER: failed to send notification for user %s",
            user.id,
        )
