import asyncio
import random
from html import escape

from pyrogram import enums, filters
from pyrogram.errors import (
    ChannelInvalid,
    ChannelPrivate,
    PeerIdInvalid,
    UserNotParticipant,
)

from pyrogram.types import Message

from config import LOGGER_ID

from BrandrdXMusic import LOGGER, app
from BrandrdXMusic.utils.database import (
    delete_served_chat,
    get_assistant,
)

logger = LOGGER("BrandrdXMusic.BrandrdKing.botleft")

PHOTO = [
    "https://imgdb.io/i/qi_QJx0.jpg",
    "https://imgdb.io/i/jgqv2mQ.jpg",
    "https://imgdb.io/i/jjJShXQ.jpg",
    "https://imgdb.io/i/HTo_3F0.jpg",
    "https://imgdb.io/i/UX0rVaE.jpg",
]

# Prevent duplicate cleanup for the same group.
PROCESSING_CHATS = set()

BOT_ID = None


async def get_bot_id():
    global BOT_ID

    if BOT_ID is None:
        me = await app.get_me()
        BOT_ID = me.id

    return BOT_ID


def get_remover_mention(message: Message) -> str:
    user = message.from_user

    if user:
        name = escape(
            user.first_name or user.username or "Unknown User"
        )

        return (
            f'<a href="tg://user?id={user.id}">'
            f"{name}</a>"
        )

    if message.sender_chat:
        return escape(
            message.sender_chat.title or "Anonymous Admin"
        )

    return "Unknown User"


async def send_left_log(message: Message, bot_username: str):
    if not LOGGER_ID:
        return

    chat = message.chat

    chat_id = chat.id
    chat_title = escape(chat.title or "Unknown Group")

    chat_username = (
        f"@{escape(chat.username)}"
        if chat.username
        else "Private Group"
    )

    removed_by = get_remover_mention(message)

    bot_name = (
        f"@{escape(bot_username)}"
        if bot_username
        else "Music Bot"
    )

    caption = (
        "<b><blockquote>"
        "✫ <u>#𝗟𝗘𝗙𝗧_𝗚𝗥𝗢𝗨𝗣</u> ✫\n\n"
        f"𝐂ʜᴀᴛ 𝐓ɪᴛʟᴇ : {chat_title}\n\n"
        f"𝗖𝗛𝗔𝗧 𝗜𝗗 : <code>{chat_id}</code>\n\n"
        f"𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘 : {chat_username}\n\n"
        f"𝗥𝗘𝗠𝗢𝗩𝗘𝗗 𝗕𝗬 : {removed_by}\n\n"
        f"𝗕𝗢𝗧 : {bot_name}"
        "</blockquote></b>"
    )

    try:
        await app.send_photo(
            chat_id=LOGGER_ID,
            photo=random.choice(PHOTO),
            caption=caption,
            parse_mode=enums.ParseMode.HTML,
        )

    except Exception:
        logger.exception(
            "[LEFT GROUP] Failed to send log for chat=%s",
            chat_id,
        )

        # If the photo cannot be sent, try a text log.
        try:
            await app.send_message(
                chat_id=LOGGER_ID,
                text=caption,
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True,
            )

        except Exception:
            logger.exception(
                "[LEFT GROUP] Text log also failed for chat=%s",
                chat_id,
            )


@app.on_message(filters.left_chat_member)
async def on_left_chat_member(client, message: Message):
    chat_id = message.chat.id

    # Only handle groups and supergroups.
    if message.chat.type not in (
        enums.ChatType.GROUP,
        enums.ChatType.SUPERGROUP,
    ):
        return

    left_member = message.left_chat_member

    if not left_member:
        return

    try:
        bot_id = await get_bot_id()

    except Exception:
        logger.exception(
            "[LEFT GROUP] Unable to identify bot"
        )
        return

    # Ignore normal members leaving the group.
    if left_member.id != bot_id:
        return

    if chat_id in PROCESSING_CHATS:
        return

    PROCESSING_CHATS.add(chat_id)

    try:
        me = await client.get_me()

        # Get assistant before deleting the served-chat record.
        assistant = None

        try:
            assistant = await get_assistant(chat_id)

        except Exception:
            logger.exception(
                "[LEFT GROUP] Assistant lookup failed chat=%s",
                chat_id,
            )

        # Send removal log.
        await send_left_log(
            message=message,
            bot_username=me.username or "",
        )

        # Delete group from served-chat database.
        try:
            await delete_served_chat(chat_id)

        except Exception:
            logger.exception(
                "[LEFT GROUP] Database cleanup failed chat=%s",
                chat_id,
            )

        # Remove assistant account from the group.
        if assistant is not None:
            try:
                await assistant.leave_chat(chat_id)

            except (
                ChannelInvalid,
                ChannelPrivate,
                PeerIdInvalid,
                UserNotParticipant,
            ):
                pass

            except Exception:
                logger.exception(
                    "[LEFT GROUP] Assistant leave failed chat=%s",
                    chat_id,
                )

    except asyncio.CancelledError:
        raise

    except Exception:
        logger.exception(
            "[LEFT GROUP] Unexpected error chat=%s",
            chat_id,
        )

    finally:
        PROCESSING_CHATS.discard(chat_id)
