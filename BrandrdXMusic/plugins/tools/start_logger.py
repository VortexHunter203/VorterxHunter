import logging
from html import escape

from pyrogram import filters, enums
from pyrogram.types import Message

from BrandrdXMusic import app
from config import LOGGER_ID

LOGGER = logging.getLogger(__name__)


@app.on_message(filters.command('start') & filters.private, group=-1)
async def start_user_logger(client, message: Message):
    user = message.from_user
    if user is None:
        return

    if not LOGGER_ID:
        LOGGER.error('START LOGGER: LOGGER_ID is not configured')
        return

    user_id = user.id
    full_name = escape(' '.join(filter(None, [user.first_name, user.last_name])) or 'Unknown User')
    username = f'@{escape(user.username)}' if user.username else 'No Username'
    profile_link = f'tg://user?id={user_id}'

    text = (
        '<b>🎫 ɴᴇᴡ ʙᴏᴛ sᴛᴀʀᴛ</b>\n\n'
        '<blockquote>'
        f'👤 <a href="{profile_link}"><b>{full_name}</b></a> ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n'
        f'🆔 <b>ᴜsᴇʀ ɪᴅ :</b> <code>{user_id}</code>\n'
        f'🔗 <b>ᴜsᴇʀɴᴀᴍᴇ :</b> {username}\n'
        f'👤 <b>ᴘʀᴏғɪʟᴇ :</b> <a href="{profile_link}">ᴠɪᴇᴡ ᴜsᴇʀ</a>'
        '</blockquote>'
    )

    try:
        await client.send_message(
            chat_id=int(LOGGER_ID),
            text=text,
            disable_web_page_preview=True,
        )
        LOGGER.warning('START LOGGER: notification sent for user %s', user_id)
    except Exception:
        LOGGER.exception('START LOGGER: failed to notify LOGGER_ID=%s for user=%s', LOGGER_ID, user_id)
