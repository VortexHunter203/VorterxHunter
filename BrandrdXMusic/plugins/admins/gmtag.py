import asyncio
import logging
import random
from html import escape

from pyrogram import filters, enums
from pyrogram.errors import FloodWait, UserNotParticipant

from BrandrdXMusic import app


LOG = logging.getLogger(__name__)

TAG_TASKS = {}
TAG_STOPS = {}

TAG_DELAY = 7
MAX_FLOOD_WAIT = 120


EMOJI = [
    "🦋🦋🦋🦋🦋",
    "🧚🌸🧋🍬🫖",
    "🥀🌷🌹🌺💐",
    "🌸🌿💮🌱🌵",
    "❤️💚💙💜🖤",
    "💓💕💞💗💖",
    "🌸💐🌺🌹🦋",
    "🍔🦪🍛🍲🥗",
    "🍎🍓🍒🍑🌶️",
    "🧋🥤🧋🥛🍷",
    "🍬🍭🧁🎂🍡",
    "🍨🧉🍺☕🍻",
    "🥪🥧🍦🍥🍚",
    "🫖☕🍹🍷🥛",
    "☕🧃🍩🍦🍙",
    "🍁🌾💮🍂🌿",
    "🌨️🌥️⛈️🌩️🌧️",
    "🌷🏵️🌸🌺💐",
    "💮🌼🌻🍀🍁",
    "🧟🦸🦹🧙👸",
    "🧅🍠🥕🌽🥦",
    "🐷🐹🐭🐨🐻‍❄️",
    "🦋🐇🐀🐈🐈‍⬛",
    "🌼🌳🌲🌴🌵",
    "🥩🍋🍐🍈🍇",
    "🍴🍽️🔪🍶🥃",
    "🕌🏰🏩⛩️🏩",
    "🎉🎊🎈🎂🎀",
    "🪴🌵🌴🌳🌲",
    "🎄🎋🎍🎑🎎",
    "🦅🦜🕊️🦤🦢",
    "🦤🦩🦚🦃🦆",
    "🐬🦭🦈🐋🐳",
    "🐔🐟🐠🐡🦐",
    "🦩🦀🦑🐙🦪",
    "🐦🦂🕷️🕸️🐚",
    "🥪🍰🥧🍨🍨",
    "🥬🍉🧁🧇",
]


TAGMES = [
    "➠ ɢᴏᴏᴅ ɴɪɢʜᴛ 🌚",
    "➠ ᴄʜᴜᴘ ᴄʜᴀᴘ sᴏ ᴊᴀ 🙊",
    "➠ ᴘʜᴏɴᴇ ʀᴀᴋʜ ᴋᴀʀ sᴏ ᴊᴀ, ɴᴀʜɪ ᴛᴏ ʙʜᴏᴏᴛ ᴀᴀ ᴊᴀʏᴇɢᴀ..👻",
    "➠ ᴀᴡᴇᴇ ʙᴀʙᴜ sᴏɴᴀ ᴅɪɴ ᴍᴇɪɴ ᴋᴀʀ ʟᴇɴᴀ ᴀʙʜɪ sᴏ ᴊᴀᴏ..?? 🥲",
    "➠ ᴍᴜᴍᴍʏ ᴅᴇᴋʜᴏ ʏᴇ ᴀᴘɴᴇ ɢғ sᴇ ʙᴀᴀᴛ ᴋʀ ʀʜᴀ ʜ ʀᴀᴊᴀɪ ᴍᴇ ɢʜᴜs ᴋᴀʀ, sᴏ ɴᴀʜɪ ʀᴀʜᴀ 😜",
    "➠ ᴘᴀᴘᴀ ʏᴇ ᴅᴇᴋʜᴏ ᴀᴘɴᴇ ʙᴇᴛᴇ ᴋᴏ ʀᴀᴀᴛ ʙʜᴀʀ ᴘʜᴏɴᴇ ᴄʜᴀʟᴀ ʀʜᴀ ʜᴀɪ 🤭",
    "➠ ᴊᴀɴᴜ ᴀᴀᴊ ʀᴀᴀᴛ ᴋᴀ sᴄᴇɴᴇ ʙɴᴀ ʟᴇ..?? 🌠",
    "➠ ɢɴ sᴅ ᴛᴄ.. 🙂",
    "➠ ɢᴏᴏᴅ ɴɪɢʜᴛ sᴡᴇᴇᴛ ᴅʀᴇᴀᴍ ᴛᴀᴋᴇ ᴄᴀʀᴇ..?? ✨",
    "➠ ʀᴀᴀᴛ ʙʜᴜᴛ ʜᴏ ɢʏɪ ʜᴀɪ sᴏ ᴊᴀᴏ, ɢɴ..?? 🌌",
    "➠ ᴍᴜᴍᴍʏ ᴅᴇᴋʜᴏ 11 ʙᴀᴊɴᴇ ᴡᴀʟᴇ ʜᴀɪ ʏᴇ ᴀʙʜɪ ᴛᴀᴋ ᴘʜᴏɴᴇ ᴄʜᴀʟᴀ ʀʜᴀ ɴᴀʜɪ sᴏ ɴᴀʜɪ ʀʜᴀ 🕦",
    "➠ ᴋᴀʟ sᴜʙʜᴀ sᴄʜᴏᴏʟ ɴᴀʜɪ ᴊᴀɴᴀ ᴋʏᴀ, ᴊᴏ ᴀʙʜɪ ᴛᴀᴋ ᴊᴀɢ ʀʜᴇ ʜᴏ 🏫",
    "➠ ʙᴀʙᴜ, ɢᴏᴏᴅ ɴɪɢʜᴛ sᴅ ᴛᴄ..?? 😊",
    "➠ ᴀᴀᴊ ʙʜᴜᴛ ᴛʜᴀɴᴅ ʜᴀɪ, ᴀᴀʀᴀᴍ sᴇ ᴊᴀʟᴅɪ sᴏ ᴊᴀᴛɪ ʜᴏᴏɴ 🌼",
    "➠ ᴊᴀɴᴇᴍᴀɴ, ɢᴏᴏᴅ ɴɪɢʜᴛ 🌷",
    "➠ ᴍᴇ ᴊᴀ ʀᴀʜɪ sᴏɴᴇ, ɢɴ sᴅ ᴛᴄ 🏵️",
    "➠ ʜᴇʟʟᴏ ᴊɪ ɴᴀᴍᴀsᴛᴇ, ɢᴏᴏᴅ ɴɪɢʜᴛ 🍃",
    "➠ ʜᴇʏ, ʙᴀʙʏ ᴋᴋʀʜ..? sᴏɴᴀ ɴᴀʜɪ ʜᴀɪ ᴋʏᴀ ☃️",
    "➠ ɢᴏᴏᴅ ɴɪɢʜᴛ ᴊɪ, ʙʜᴜᴛ ʀᴀᴀᴛ ʜᴏ ɢʏɪ..? ⛄",
    "➠ ᴍᴇ ᴊᴀ ʀᴀʜɪ ʀᴏɴᴇ, ɪ ᴍᴇᴀɴ sᴏɴᴇ ɢᴏᴏᴅ ɴɪɢʜᴛ ᴊɪ 😁",
    "➠ ᴍᴀᴄʜʜᴀʟɪ ᴋᴏ ᴋᴇʜᴛᴇ ʜᴀɪ ғɪsʜ, ɢᴏᴏᴅ ɴɪɢʜᴛ ᴅᴇᴀʀ ᴍᴀᴛ ᴋʀɴᴀ ᴍɪss, ᴊᴀ ʀʜɪ sᴏɴᴇ 🌄",
    "➠ ɢᴏᴏᴅ ɴɪɢʜᴛ ʙʀɪɢʜᴛғᴜʟʟ ɴɪɢʜᴛ 🤭",
    "➠ ᴛʜᴇ ɴɪɢʜᴛ ʜᴀs ғᴀʟʟᴇɴ, ᴛʜᴇ ᴅᴀʏ ɪs ᴅᴏɴᴇ,, ᴛʜᴇ ᴍᴏᴏɴ ʜᴀs ᴛᴀᴋᴇɴ ᴛʜᴇ ᴘʟᴀᴄᴇ ᴏғ ᴛʜᴇ sᴜɴ... 😊",
    "➠ ᴍᴀʏ ᴀʟʟ ʏᴏᴜʀ ᴅʀᴇᴀᴍs ᴄᴏᴍᴇ ᴛʀᴜᴇ ❤️",
    "➠ ɢᴏᴏᴅ ɴɪɢʜᴛ sᴘʀɪɴᴋʟᴇs sᴡᴇᴇᴛ ᴅʀᴇᴀᴍ 💚",
    "➠ ɢᴏᴏᴅ ɴɪɢʜᴛ, ɴɪɴᴅ ᴀᴀ ʀʜɪ ʜᴀɪ 🥱",
    "➠ ᴅᴇᴀʀ ғʀɪᴇɴᴅ ɢᴏᴏᴅ ɴɪɢʜᴛ 💤",
    "➠ ʙᴀʙʏ ᴀᴀᴊ ʀᴀᴀᴛ ᴋᴀ sᴄᴇɴᴇ ʙɴᴀ ʟᴇ 🥰",
    "➠ ɪᴛɴɪ ʀᴀᴀᴛ ᴍᴇ ᴊᴀɢ ᴋᴀʀ ᴋʏᴀ ᴋᴀʀ ʀʜᴇ ʜᴏ sᴏɴᴀ ɴᴀʜɪ ʜᴀɪ ᴋʏᴀ 😜",
    "➠ ᴄʟᴏsᴇ ʏᴏᴜʀ ᴇʏᴇs sɴᴜɢɢʟᴇ ᴜᴘ ᴛɪɢʜᴛ,, ᴀɴᴅ ʀᴇᴍᴇᴍʙᴇʀ ᴛʜᴀᴛ ᴀɴɢᴇʟs, ᴡɪʟʟ ᴡᴀᴛᴄʜ ᴏᴠᴇʀ ʏᴏᴜ ᴛᴏɴɪɢʜᴛ... 💫",
]


VC_TAG = [
    "➠ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ, ᴋᴇsᴇ ʜᴏ 🐱",
    "➠ ɢᴍ, sᴜʙʜᴀ ʜᴏ ɢʏɪ ᴜᴛʜɴᴀ ɴᴀʜɪ ʜᴀɪ ᴋʏᴀ 🌤️",
    "➠ ɢᴍ ʙᴀʙʏ, ᴄʜᴀɪ ᴘɪ ʟᴏ ☕",
    "➠ ᴊᴀʟᴅɪ ᴜᴛʜᴏ, sᴄʜᴏᴏʟ ɴᴀʜɪ ᴊᴀɴᴀ ᴋʏᴀ 🏫",
    "➠ ɢᴍ, ᴄʜᴜᴘ ᴄʜᴀᴘ ʙɪsᴛᴇʀ sᴇ ᴜᴛʜᴏ ᴠʀɴᴀ ᴘᴀɴɪ ᴅᴀʟ ᴅᴜɴɢɪ 🧊",
    "➠ ʙᴀʙʏ ᴜᴛʜᴏ ᴀᴜʀ ᴊᴀʟᴅɪ ғʀᴇsʜ ʜᴏ ᴊᴀᴏ, ɴᴀsᴛᴀ ʀᴇᴀᴅʏ ʜᴀɪ 🫕",
    "➠ ᴏғғɪᴄᴇ ɴᴀʜɪ ᴊᴀɴᴀ ᴋʏᴀ ᴊɪ ᴀᴀᴊ, ᴀʙʜɪ ᴛᴀᴋ ᴜᴛʜᴇ ɴᴀʜɪ 🏣",
    "➠ ɢᴍ ᴅᴏsᴛ, ᴄᴏғғᴇᴇ/ᴛᴇᴀ ᴋʏᴀ ʟᴏɢᴇ ☕🍵",
    "➠ ʙᴀʙʏ 8 ʙᴀᴊɴᴇ ᴡᴀʟᴇ ʜᴀɪ, ᴀᴜʀ ᴛᴜᴍ ᴀʙʜɪ ᴛᴋ ᴜᴛʜᴇ ɴᴀʜɪ 🕖",
    "➠ ᴋʜᴜᴍʙʜᴋᴀʀᴀɴ ᴋɪ ᴀᴜʟᴀᴅ ᴜᴛʜ ᴊᴀᴀ... ☃️",
    "➠ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ ʜᴀᴠᴇ ᴀ ɴɪᴄᴇ ᴅᴀʏ... 🌄",
    "➠ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ, ʜᴀᴠᴇ ᴀ ɢᴏᴏᴅ ᴅᴀʏ... 🪴",
    "➠ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ, ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ ʙᴀʙʏ 😇",
    "➠ ᴍᴜᴍᴍʏ ᴅᴇᴋʜᴏ ʏᴇ ɴᴀʟᴀʏᴋ ᴀʙʜɪ ᴛᴀᴋ sᴏ ʀʜᴀ ʜᴀɪ... 😵‍💫",
    "➠ ʀᴀᴀᴛ ʙʜᴀʀ ʙᴀʙᴜ sᴏɴᴀ ᴋʀ ʀʜᴇ ᴛʜᴇ ᴋʏᴀ, ᴊᴏ ᴀʙʜɪ ᴛᴋ sᴏ ʀʜᴇ ʜᴏ ᴜᴛʜɴᴀ ɴᴀʜɪ ʜᴀɪ ᴋʏᴀ... 😏",
    "➠ ʙᴀʙᴜ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ ᴜᴛʜ ᴊᴀᴏ ᴀᴜʀ ɢʀᴏᴜᴘ ᴍᴇ sᴀʙ ғʀɪᴇɴᴅs ᴋᴏ ɢᴍ ᴡɪsʜ ᴋʀᴏ... 🌟",
    "➠ ᴘᴀᴘᴀ ʏᴇ ᴀʙʜɪ ᴛᴀᴋ ᴜᴛʜ ɴᴀʜɪ, sᴄʜᴏᴏʟ ᴋᴀ ᴛɪᴍᴇ ɴɪᴋᴀʟᴛᴀ ᴊᴀ ʀʜᴀ ʜᴀɪ... 🥲",
    "➠ ᴊᴀɴᴇᴍᴀɴ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ, ᴋʏᴀ ᴋʀ ʀʜᴇ ʜᴏ ... 😅",
    "➠ ɢᴍ ʙᴇᴀsᴛɪᴇ, ʙʀᴇᴀᴋғᴀsᴛ ʜᴜᴀ ᴋʏᴀ... 🍳",
]


def get_mention(user):
    """
    Clickable username or first name.
    """

    username = getattr(user, "username", None)

    if username:
        display = f"@{escape(username)}"
    else:
        display = escape(user.first_name or "User")

    return (
        f'<a href="tg://user?id={user.id}">'
        f"{display}</a>"
    )


async def check_admin(client, message):
    """
    Only group owner/admin can run or stop tagging.
    """

    if not message.from_user:
        return False

    try:
        participant = await client.get_chat_member(
            message.chat.id,
            message.from_user.id,
        )

        return participant.status in (
            enums.ChatMemberStatus.OWNER,
            enums.ChatMemberStatus.ADMINISTRATOR,
        )

    except UserNotParticipant:
        return False

    except Exception:
        LOG.exception("[GN/GM TAG] Admin check failed")
        return False


async def wait_or_stop(stop_event, seconds):
    """
    Sleep without delaying /gmstop unnecessarily.
    """

    try:
        await asyncio.wait_for(
            stop_event.wait(),
            timeout=seconds,
        )
        return True

    except asyncio.TimeoutError:
        return False


async def send_tag(
    client,
    chat_id,
    content,
    stop_event,
    reply_to_message_id=None,
):
    """
    Send message with FloodWait handling.
    """

    while not stop_event.is_set():

        try:
            await client.send_message(
                chat_id=chat_id,
                text=content,
                disable_web_page_preview=True,
                reply_to_message_id=reply_to_message_id,
            )

            return True

        except FloodWait as error:
            seconds = max(1, int(error.value))

            LOG.warning(
                "[GN/GM TAG] FloodWait chat=%s wait=%ss",
                chat_id,
                seconds,
            )

            if seconds > MAX_FLOOD_WAIT:
                return False

            if await wait_or_stop(
                stop_event,
                seconds + 1,
            ):
                return False

        except asyncio.CancelledError:
            raise

        except Exception:
            LOG.exception(
                "[GN/GM TAG] Message send failed chat=%s",
                chat_id,
            )
            return False

    return False


async def run_tagging(
    client,
    message,
    mode,
    reply_message,
    stop_event,
):
    """
    Tag each unique user returned by Telegram only once.
    """

    chat_id = message.chat.id

    seen_users = set()

    total_retrieved = 0
    total_tagged = 0

    completed = False

    try:
        async for member in client.get_chat_members(chat_id):

            if stop_event.is_set():
                break

            user = getattr(member, "user", None)

            if not user:
                continue

            if user.id in seen_users:
                continue

            seen_users.add(user.id)

            total_retrieved += 1

            if user.is_bot or user.is_deleted:
                continue

            mention = get_mention(user)

            if mode == "gn_reply":

                emoji = random.choice(EMOJI)

                content = (
                    "<b><blockquote>"
                    f"{mention}\n"
                    f"{escape(emoji)}"
                    "</blockquote></b>"
                )

                reply_id = reply_message.id

            elif mode == "gm":

                phrase = random.choice(VC_TAG)

                content = (
                    "<b><blockquote>"
                    f"🌅 {mention}\n\n"
                    f"{escape(phrase)}"
                    "</blockquote></b>"
                )

                reply_id = None

            else:

                phrase = random.choice(TAGMES)

                content = (
                    "<b><blockquote>"
                    f"🌙 {mention}\n\n"
                    f"{escape(phrase)}"
                    "</blockquote></b>"
                )

                reply_id = None

            sent = await send_tag(
                client=client,
                chat_id=chat_id,
                content=content,
                stop_event=stop_event,
                reply_to_message_id=reply_id,
            )

            if not sent:
                break

            total_tagged += 1

            LOG.info(
                "[GN/GM TAG] chat=%s mode=%s "
                "user=%s tagged=%s",
                chat_id,
                mode,
                user.id,
                total_tagged,
            )

            if await wait_or_stop(
                stop_event,
                TAG_DELAY,
            ):
                break

        else:
            completed = True

    except asyncio.CancelledError:
        raise

    except FloodWait as error:
        LOG.warning(
            "[GN/GM TAG] Member retrieval FloodWait "
            "chat=%s wait=%ss",
            chat_id,
            error.value,
        )

    except Exception:
        LOG.exception(
            "[GN/GM TAG] Member retrieval failed chat=%s",
            chat_id,
        )

    finally:

        current_task = asyncio.current_task()

        if TAG_TASKS.get(chat_id) is current_task:
            TAG_TASKS.pop(chat_id, None)
            TAG_STOPS.pop(chat_id, None)

        LOG.warning(
            "[GN/GM TAG] Finished chat=%s mode=%s "
            "retrieved=%s tagged=%s completed=%s",
            chat_id,
            mode,
            total_retrieved,
            total_tagged,
            completed,
        )

        status = (
            "✅ ᴛᴀɢɢɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!"
            if completed
            else "🛑 ᴛᴀɢɢɪɴɢ sᴛᴏᴘᴘᴇᴅ!"
        )

        try:
            await message.reply_text(
                "<b><blockquote>"
                f"{status}\n\n"
                f"👥 ᴍᴇᴍʙᴇʀs ʀᴇᴛʀɪᴇᴠᴇᴅ: "
                f"<code>{total_retrieved}</code>\n"
                f"✨ ᴍᴇᴍʙᴇʀs ᴛᴀɢɢᴇᴅ: "
                f"<code>{total_tagged}</code>\n"
                "🔁 ᴅᴜᴘʟɪᴄᴀᴛᴇ ᴛᴀɢs: <code>0</code>"
                "</blockquote></b>",
            )

        except Exception:
            LOG.exception(
                "[GN/GM TAG] Completion message failed"
            )


async def start_tagging(
    client,
    message,
    mode,
    reply_message=None,
):
    chat_id = message.chat.id

    existing = TAG_TASKS.get(chat_id)

    if existing and not existing.done():
        return await message.reply_text(
            "<b><blockquote>"
            "⚠️ ᴛᴀɢɢɪɴɢ ɪs ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ!\n\n"
            "🛑 <code>/gmstop</code>"
            "</blockquote></b>",
        )

    stop_event = asyncio.Event()

    TAG_STOPS[chat_id] = stop_event

    task = asyncio.create_task(
        run_tagging(
            client=client,
            message=message,
            mode=mode,
            reply_message=reply_message,
            stop_event=stop_event,
        )
    )

    TAG_TASKS[chat_id] = task

    mode_name = {
        "gn": "🌙 ɢᴏᴏᴅ ɴɪɢʜᴛ",
        "gn_reply": "🌙 ᴇᴍᴏᴊɪ ʀᴇᴘʟʏ",
        "gm": "🌅 ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ",
    }.get(mode, "ᴛᴀɢɢɪɴɢ")

    try:
        await message.reply_text(
            "<b><blockquote>"
            "🚀 𝐁𝐑𝐀𝐍𝐃𝐄𝐃 𝐓𝐀𝐆𝐆𝐈𝐍𝐆\n\n"
            f"💬 ᴍᴏᴅᴇ: {mode_name}\n"
            "👥 ᴇᴀᴄʜ ᴜɴɪǫᴜᴇ ᴍᴇᴍʙᴇʀ ᴏɴᴄᴇ\n"
            "⏳ ᴅᴇʟᴀʏ: 7 sᴇᴄᴏɴᴅs\n\n"
            "🛑 <code>/gmstop</code>"
            "</blockquote></b>",
        )

    except Exception:
        LOG.exception(
            "[GN/GM TAG] Start message failed"
        )


@app.on_message(
    filters.command(
        ["gntag", "tagmember"],
        prefixes=["/", "@", "#"],
    )
)
async def mentionall(client, message):

    if message.chat.type == enums.ChatType.PRIVATE:
        return await message.reply_text(
            "<b><blockquote>"
            "🚫 ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ғᴏʀ ɢʀᴏᴜᴘs."
            "</blockquote></b>",
        )

    if not await check_admin(client, message):
        return await message.reply_text(
            "<b><blockquote>"
            "🚫 ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ʙᴀʙʏ.\n\n"
            "👑 ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴛᴀɢ ᴍᴇᴍʙᴇʀs."
            "</blockquote></b>",
        )

    parts = (message.text or "").split(None, 1)

    if len(parts) > 1:
        return await message.reply_text(
            "<b><blockquote>"
            "⚠️ ᴜsᴇ:\n\n"
            "➻ <code>/gntag</code>\n"
            "➻ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ "
            "ᴡɪᴛʜ <code>/gntag</code>"
            "</blockquote></b>",
        )

    reply_message = message.reply_to_message

    mode = (
        "gn_reply"
        if reply_message
        else "gn"
    )

    await start_tagging(
        client=client,
        message=message,
        mode=mode,
        reply_message=reply_message,
    )


@app.on_message(
    filters.command(
        ["gmtag"],
        prefixes=["/", "@", "#"],
    )
)
async def mention_allvc(client, message):

    if message.chat.type == enums.ChatType.PRIVATE:
        return await message.reply_text(
            "<b><blockquote>"
            "🚫 ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ғᴏʀ ɢʀᴏᴜᴘs."
            "</blockquote></b>",
        )

    if not await check_admin(client, message):
        return await message.reply_text(
            "<b><blockquote>"
            "🚫 ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ʙᴀʙʏ.\n\n"
            "👑 ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴛᴀɢ ᴍᴇᴍʙᴇʀs."
            "</blockquote></b>",
        )

    await start_tagging(
        client=client,
        message=message,
        mode="gm",
    )


@app.on_message(
    filters.command(
        ["gmstop", "gnstop", "cancle"],
        prefixes=["/", "@", "#"],
    )
)
async def cancel_spam(client, message):

    chat_id = message.chat.id

    if message.chat.type == enums.ChatType.PRIVATE:
        return

    if not await check_admin(client, message):
        return await message.reply_text(
            "<b><blockquote>"
            "🚫 ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ sᴛᴏᴘ ᴛᴀɢɢɪɴɢ."
            "</blockquote></b>",
        )

    task = TAG_TASKS.get(chat_id)
    stop_event = TAG_STOPS.get(chat_id)

    if not task or task.done() or not stop_event:
        return await message.reply_text(
            "<b><blockquote>"
            "ℹ️ ᴄᴜʀʀᴇɴᴛʟʏ ɴᴏ ᴛᴀɢɢɪɴɢ "
            "ᴘʀᴏᴄᴇss ɪs ʀᴜɴɴɪɴɢ."
            "</blockquote></b>",
        )

    stop_event.set()

    return await message.reply_text(
        "<b><blockquote>"
        "🛑 𝐁𝐑𝐀𝐍𝐃𝐄𝐃 𝐓𝐀𝐆𝐆𝐈𝐍𝐆\n\n"
        "⏳ sᴛᴏᴘ ʀᴇǫᴜᴇsᴛᴇᴅ.\n"
        "✨ ᴘʀᴏᴄᴇss ɪs sᴛᴏᴘᴘɪɴɢ..."
        "</blockquote></b>",
    )


@app.on_message(
    filters.command(
        ["tagdiagnose"],
        prefixes=["/", "@", "#"],
    )
)
async def tag_diagnose(client, message):
    """
    Diagnostic command:
    Check how many members Telegram actually returns
    to this Pyrogram client.
    """

    if message.chat.type == enums.ChatType.PRIVATE:
        return

    if not await check_admin(client, message):
        return

    chat_id = message.chat.id

    status = await message.reply_text(
        "<b><blockquote>"
        "🔍 ᴄʜᴇᴄᴋɪɴɢ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴇᴍʙᴇʀ ʟɪsᴛ..."
        "</blockquote></b>",
    )

    seen = set()
    total = 0
    error_text = None

    try:
        async for member in client.get_chat_members(chat_id):

            user = getattr(member, "user", None)

            if not user:
                continue

            if user.id in seen:
                continue

            seen.add(user.id)
            total += 1

    except Exception as error:
        error_text = str(error)

        LOG.exception(
            "[TAG DIAGNOSE] Failed chat=%s",
            chat_id,
        )

    try:
        reported = await client.get_chat_members_count(chat_id)
    except Exception:
        reported = "Unavailable"

    LOG.warning(
        "[TAG DIAGNOSE] chat=%s reported=%s retrieved=%s",
        chat_id,
        reported,
        total,
    )

    result = (
        "<b><blockquote>"
        "🔍 𝐓𝐀𝐆 𝐃𝐈𝐀𝐆𝐍𝐎𝐒𝐓𝐈𝐂\n\n"
        f"👥 ɢʀᴏᴜᴘ ᴍᴇᴍʙᴇʀ ᴄᴏᴜɴᴛ: "
        f"<code>{reported}</code>\n"
        f"📥 ᴜɴɪǫᴜᴇ ᴍᴇᴍʙᴇʀs ʀᴇᴛʀɪᴇᴠᴇᴅ: "
        f"<code>{total}</code>\n\n"
    )

    if error_text:
        result += (
            "⚠️ ᴇʀʀᴏʀ:\n"
            f"<code>{escape(error_text[:300])}</code>"
        )

    elif isinstance(reported, int) and total < reported:
        result += (
            "⚠️ ᴛᴇʟᴇɢʀᴀᴍ ᴅɪᴅ ɴᴏᴛ ʀᴇᴛᴜʀɴ "
            "ᴛʜᴇ ғᴜʟʟ ᴍᴇᴍʙᴇʀ ʟɪsᴛ."
        )

    else:
        result += "✅ ᴍᴇᴍʙᴇʀ ʀᴇᴛʀɪᴇᴠᴀʟ ᴄʜᴇᴄᴋ ғɪɴɪsʜᴇᴅ."

    result += "</blockquote></b>"

    await status.edit_text(
        result,
    )
