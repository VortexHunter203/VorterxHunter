import asyncio
import logging
from html import escape

from pyrogram import enums, filters
from pyrogram.errors import FloodWait

from BrandrdXMusic import app

LOG = logging.getLogger(__name__)

TAG_TASKS = {}
TAG_STOPS = {}

BATCH_SIZE = 1
TAG_DELAY = 7
MAX_FLOOD_WAIT = 120


def get_mention(user):
    """
    Use @username when available.
    Otherwise use clickable first name.
    """

    username = getattr(user, "username", None)

    if username:
        name = f"@{escape(username)}"
    else:
        name = escape(user.first_name or "User")

    return (
        f'<a href="tg://user?id={user.id}">'
        f"{name}</a>"
    )


async def wait_or_stop(stop_event, seconds):
    """
    Interruptible delay.
    Returns True if stop was requested.
    """

    try:
        await asyncio.wait_for(
            stop_event.wait(),
            timeout=seconds,
        )
        return True

    except asyncio.TimeoutError:
        return False


async def send_batch(
    chat_id,
    text,
    mentions,
    replied,
    stop_event,
):
    if not mentions:
        return False

    usertxt = "\n".join(
        f"⊚ {mention}"
        for mention in mentions
    )

    if replied:
        content = (
            "<b><blockquote>"
            f"{usertxt}"
            "</blockquote></b>"
        )

        reply_id = replied.id

    else:
        content = (
            "<b><blockquote>"
            f"✨ {escape(text)}\n\n"
            f"{usertxt}"
            "</blockquote></b>"
        )

        reply_id = None

    while not stop_event.is_set():

        try:
            await app.send_message(
                chat_id=chat_id,
                text=content,
                disable_web_page_preview=True,
                reply_to_message_id=reply_id,
            )

            return True

        except FloodWait as error:
            seconds = max(1, int(error.value))

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
            return False

    return False


async def run_tagging(
    message,
    text,
    replied,
    stop_event,
):
    chat_id = message.chat.id

    seen_users = set()
    mentions = []

    total_retrieved = 0
    total_tagged = 0
    completed = False

    try:
        async for member in app.get_chat_members(chat_id):

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

            mentions.append(
                get_mention(user)
            )

            if len(mentions) >= BATCH_SIZE:

                sent = await send_batch(
                    chat_id=chat_id,
                    text=text,
                    mentions=mentions,
                    replied=replied,
                    stop_event=stop_event,
                )

                if not sent:
                    break

                total_tagged += len(mentions)
                mentions = []

                if await wait_or_stop(
                    stop_event,
                    TAG_DELAY,
                ):
                    break

        else:
            completed = True

        # Send remaining users.
        if (
            completed
            and mentions
            and not stop_event.is_set()
        ):
            sent = await send_batch(
                chat_id=chat_id,
                text=text,
                mentions=mentions,
                replied=replied,
                stop_event=stop_event,
            )

            if sent:
                total_tagged += len(mentions)

    except asyncio.CancelledError:
        raise

    except FloodWait:
        pass

    except Exception:
        pass

    finally:
        current_task = asyncio.current_task()

        if TAG_TASKS.get(chat_id) is current_task:
            TAG_TASKS.pop(chat_id, None)
            TAG_STOPS.pop(chat_id, None)

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
            pass


@app.on_message(
    filters.command(
        ["all", "mention", "mentionall"],
        prefixes=["/", "@", ".", "#"],
    )
    & admin_filter
)
async def tag_all_users(_, message):
    chat_id = message.chat.id

    if message.chat.type == enums.ChatType.PRIVATE:
        return await message.reply_text(
            "<b><blockquote>"
            "🚫 ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ғᴏʀ ɢʀᴏᴜᴘs."
            "</blockquote></b>",
        )

    replied = message.reply_to_message

    parts = (message.text or "").split(None, 1)

    text = (
        parts[1].strip()
        if len(parts) > 1
        else ""
    )

    if not text and not replied:
        return await message.reply_text(
            "<b><blockquote>"
            "💬 ɢɪᴠᴇ sᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ ᴛᴀɢ ᴀʟʟ.\n\n"
            "ᴇxᴀᴍᴘʟᴇ » <code>@all Hi Friends</code>\n"
            "ᴏʀ ʀᴇᴘʟʏ ᴡɪᴛʜ <code>/all</code>"
            "</blockquote></b>",
        )

    existing = TAG_TASKS.get(chat_id)

    if existing and not existing.done():
        return await message.reply_text(
            "<b><blockquote>"
            "⚠️ ᴛᴀɢɢɪɴɢ ɪs ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ!\n\n"
            "🛑 <code>/cancel</code>"
            "</blockquote></b>",
        )

    stop_event = asyncio.Event()

    TAG_STOPS[chat_id] = stop_event

    task = asyncio.create_task(
        run_tagging(
            message=message,
            text=text,
            replied=replied,
            stop_event=stop_event,
        )
    )

    TAG_TASKS[chat_id] = task

    try:
        await message.reply_text(
            "<b><blockquote>"
            "🚀 ᴛᴀɢɢɪɴɢ sᴛᴀʀᴛᴇᴅ!\n\n"
            "👤 1 ᴍᴇᴍʙᴇʀ ᴘᴇʀ ᴍᴇssᴀɢᴇ.\n"
            "⏳ ᴅᴇʟᴀʏ: 7 sᴇᴄᴏɴᴅs\n\n"
            "🛑 ᴏғғ ᴛᴀɢɢɪɴɢ » <code>/cancel</code>"
            "</blockquote></b>",
        )

    except Exception:
        pass


@app.on_message(
    filters.command(
        [
            "stopmention",
            "offall",
            "cancel",
            "allstop",
            "stopall",
            "cancelmention",
            "offmention",
            "mentionoff",
            "alloff",
            "cancelall",
            "allcancel",
        ],
        prefixes=["/", "@", "#"],
    )
    & admin_filter
)
async def cancelcmd(_, message):
    chat_id = message.chat.id

    task = TAG_TASKS.get(chat_id)
    stop_event = TAG_STOPS.get(chat_id)

    if not task or task.done() or not stop_event:
        return await message.reply_text(
            "<b><blockquote>"
            "⚠️ ɴᴏ ᴘʀᴏᴄᴇss ᴏɴɢᴏɪɴɢ!"
            "</blockquote></b>",
        )

    stop_event.set()

    return await message.reply_text(
        "<b><blockquote>"
        "🛑 ᴛᴀɢɢɪɴɢ sᴛᴏᴘ ʀᴇǫᴜᴇsᴛᴇᴅ!\n\n"
        "⏳ ᴘʀᴏᴄᴇss ɪs sᴛᴏᴘᴘɪɴɢ..."
        "</blockquote></b>",
    )
