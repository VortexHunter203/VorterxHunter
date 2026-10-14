import logging
from html import escape

from pyrogram import enums
from config import LOGGER_ID

LOGGER = logging.getLogger(__name__)


async def send_start_log(client, message):
    """Call from the existing private /start handler; does not register a second handler."""
    user = message.from_user
    if user is None or message.chat.type != enums.ChatType.PRIVATE:
        return

    if not LOGGER_ID:
        LOGGER.error('START LOGGER: LOGGER_ID is empty')
        return

    try:
        target = int(str(LOGGER_ID).strip()) if str(LOGGER_ID).strip().lstrip('-').isdigit() else str(LOGGER_ID).strip()
        uid = user.id
        name = escape(' '.join(filter(None, (user.first_name, user.last_name))) or 'Unknown User')
        username = f'@{escape(user.username)}' if user.username else 'No Username'
        url = f'tg://user?id={uid}'
        text = (
            '<b>🎫 ɴᴇᴡ ʙᴏᴛ sᴛᴀʀᴛ</b>\n\n'
            '<blockquote>'
            f'👤 <a href="{url}"><b>{name}</b></a> ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n'
            f'🆔 <b>ᴜsᴇʀ ɪᴅ :</b> <code>{uid}</code>\n'
            f'🔗 <b>ᴜsᴇʀɴᴀᴍᴇ :</b> {username}\n'
            f'👤 <b>ᴘʀᴏғɪʟᴇ :</b> <a href="{url}">ᴠɪᴇᴡ ᴜsᴇʀ</a>'
            '</blockquote>'
        )
        await client.send_message(
            chat_id=target,
            text=text,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True,
        )
        LOGGER.warning('START LOGGER: sent for user_id=%s to %s', uid, target)
    except Exception:
        LOGGER.exception('START LOGGER: send failed; LOGGER_ID=%r', LOGGER_ID)
