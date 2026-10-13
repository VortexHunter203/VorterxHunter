
import logging
from html import escape

from pyrogram import filters, enums
from pyrogram.types import Message

from BrandrdXMusic import app
from config import LOGGER_ID

LOGGER = logging.getLogger(__name__)


@app.on_message(
    filters.command("start") & filters.private,
    group=1,
)
async def start_user_logger(client, message: Message):
    user = message.from_user

    if not user:
        return

    user_id = user.id

    name = escape(
        user.first_name or "Unknown User"
    )

    if user.last_name:
        name += " " + escape(user.last_name)

    username = (
        f"@{escape(user.username)}"
        if user.username
        else "No Username"
    )

    profile_link = f"tg://user?id={user_id}"

    text = (
        "<b>🎫 ɴᴇᴡ ʙᴏᴛ sᴛᴀʀᴛ</b>\n\n"
        "<blockquote>"
        f"👤 <b>{name}</b> ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n"
        f"🆔 <b>ᴜsᴇʀ ɪᴅ :</b> <code>{user_id}</code>\n"
        f"🔗 <b>ᴜsᴇʀɴᴀᴍᴇ :</b> {username}\n"
        f"👤 <b>ᴘʀᴏғɪʟᴇ :</b> "
        f'<a href="{profile_link}">ᴠɪᴇᴡ ᴜsᴇʀ</a>'
        "</blockquote>"
    )

    try:
        await client.send_message(
            chat_id=LOGGER_ID,
            text=text,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True,
        )

    except Exception as e:
        LOGGER.warning(
            "Failed to send start notification for user %s: %s",
            user_id,
            e,
        )
