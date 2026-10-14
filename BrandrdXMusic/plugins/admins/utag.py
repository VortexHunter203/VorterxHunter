import asyncio
from html import escape

from pyrogram import filters, enums
from pyrogram.errors import FloodWait

from BrandrdXMusic import app
from BrandrdXMusic.utils.branded_ban import admin_filter

SPAM_CHATS = {}
TAG_TASKS = {}

BATCH_SIZE = 5
TAG_DELAY = 7


def get_user_mention(user):
    """
    Display @username when available.
    Otherwise display a clickable first name.
    """

    username = getattr(user, "username", None)

    if username:
        display = f"@{escape(username)}"
    else:
        display = escape(
            getattr(user, "first_name", None) or "User"
        )

    return (
        f'<a href="tg://user?id={user.id}">'
        f"{display}"
        "</a>"
    )


async def send_tag_message(chat_id, text, mentions):
    """
    Send one batch and respect Telegram FloodWait.
    """

    if not SPAM_CHATS.get(chat_id):
        return False

    usertxt = "\n".join(
        f"⊚ {mention}"
        for mention in mentions
    )

    content = (
        "<b><blockquote>"
        f"{escape(text)}\n\n"
        f"{usertxt}\n\n"
        "|| ➥ ᴏғғ ᴛᴀɢɢɪɴɢ ʙʏ » "
        "<code>/stoputag</code> ||"
        "</blockquote></b>"
    )

    while SPAM_CHATS.get(chat_id):

        try:
            await app.send_message(
                chat_id=chat_id,
                text=content,
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True,
            )

            return True

        except FloodWait as error:
            seconds = max(1, int(error.value))

            LOGGER.warning(
                "[UTAG] FloodWait chat=%s wait=%ss",
                chat_id,
                seconds,
            )

            await asyncio.sleep(seconds + 1)

        except asyncio.CancelledError:
            raise

        except Exception:
            LOGGER.exception(
                "[UTAG] Failed to send batch in %s",
                chat_id,
            )

            return False

    return False


async def run_tagging(message, text):
    """
    Tag every unique member returned by Telegram once.
    No infinite restart of the member iterator.
    """

    chat_id = message.chat.id

    seen_users = set()
    mentions = []

    total_tagged = 0
    completed = False

    try:
        async for member in app.get_chat_members(chat_id):

            if not SPAM_CHATS.get(chat_id):
                break

            user = getattr(member, "user", None)

            if not user:
                continue

            if getattr(user, "is_bot", False):
                continue

            user_id = user.id

            # Never repeat the same member in this run.
            if user_id in seen_users:
                continue

            seen_users.add(user_id)

            mentions.append(
                get_user_mention(user)
            )

            if len(mentions) >= BATCH_SIZE:

                sent = await send_tag_message(
                    chat_id,
                    text,
                    mentions,
                )

                if not sent:
                    break

                total_tagged += len(mentions)

                mentions = []

                LOGGER.info(
                    "[UTAG] chat=%s tagged=%s",
                    chat_id,
                    total_tagged,
                )

                await asyncio.sleep(TAG_DELAY)

        else:
            completed = True

        # Send the final batch of 1–4 remaining members.
        if completed and mentions and SPAM_CHATS.get(chat_id):

            sent = await send_tag_message(
                chat_id,
                text,
                mentions,
            )

            if sent:
                total_tagged += len(mentions)

    except asyncio.CancelledError:
        raise

    except FloodWait as error:
        LOGGER.warning(
            "[UTAG] Member fetching FloodWait: %ss",
            error.value,
        )

        try:
            await message.reply_text(
                "<b><blockquote>"
                "⚠️ ᴛᴇʟᴇɢʀᴀᴍ ʀᴀᴛᴇ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ.\n"
                "ᴛᴀɢɢɪɴɢ ʜᴀs ʙᴇᴇɴ sᴛᴏᴘᴘᴇᴅ."
                "</blockquote></b>",
                parse_mode=enums.ParseMode.HTML,
            )
        except Exception:
            pass

    except Exception:
        LOGGER.exception(
            "[UTAG] Member iteration failed: chat=%s",
            chat_id,
        )

    finally:

        SPAM_CHATS[chat_id] = False

        current_task = asyncio.current_task()

        if TAG_TASKS.get(chat_id) is current_task:
            TAG_TASKS.pop(chat_id, None)

        status = (
            "✅ ᴛᴀɢɢɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!"
            if completed
            else "🛑 ᴛᴀɢɢɪɴɢ sᴛᴏᴘᴘᴇᴅ!"
        )

        try:
            await message.reply_text(
                "<b><blockquote>"
                f"{status}\n\n"
                f"👥 ᴛᴏᴛᴀʟ ᴍᴇᴍʙᴇʀs ᴛᴀɢɢᴇᴅ: "
                f"<code>{total_tagged}</code>\n"
                "🔁 ᴅᴜᴘʟɪᴄᴀᴛᴇ ᴛᴀɢs: <code>0</code>"
                "</blockquote></b>",
                parse_mode=enums.ParseMode.HTML,
            )

        except Exception:
            LOGGER.exception(
                "[UTAG] Failed to send completion message"
            )


@app.on_message(
    filters.command(
        ["utag", "uall"],
        prefixes=["/", "@", ".", "#"],
    )
    & admin_filter
)
async def tag_all_users(_, message):

    chat_id = message.chat.id

    if not message.text:
        return

    parts = message.text.split(None, 1)

    if len(parts) < 2 or not parts[1].strip():

        return await message.reply_text(
            "<b><blockquote>"
            "💬 ɢɪᴠᴇ sᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ ᴛᴀɢ ᴀʟʟ.\n\n"
            "ᴇxᴀᴍᴘʟᴇ » <code>@utag Hi Friends</code>"
            "</blockquote></b>",
            parse_mode=enums.ParseMode.HTML,
        )

    existing_task = TAG_TASKS.get(chat_id)

    if existing_task and not existing_task.done():

        return await message.reply_text(
            "<b><blockquote>"
            "⚠️ ᴜᴛᴀɢ ɪs ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ!\n\n"
            "🛑 sᴛᴏᴘ ɪᴛ ᴜsɪɴɢ "
            "<code>/stoputag</code>"
            "</blockquote></b>",
            parse_mode=enums.ParseMode.HTML,
        )

    text = parts[1].strip()

    SPAM_CHATS[chat_id] = True

    await message.reply_text(
        "<b><blockquote>"
        "🚀 ᴜᴛᴀɢ sᴛᴀʀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!\n\n"
        "👥 ᴇᴀᴄʜ ᴍᴇᴍʙᴇʀ ᴡɪʟʟ ʙᴇ ᴛᴀɢɢᴇᴅ ᴏɴᴄᴇ.\n"
        "⏳ ᴅᴇʟᴀʏ: 7 sᴇᴄᴏɴᴅs.\n\n"
        "🛑 sᴛᴏᴘ » <code>/stoputag</code>"
        "</blockquote></b>",
        parse_mode=enums.ParseMode.HTML,
    )

    task = asyncio.create_task(
        run_tagging(message, text)
    )

    TAG_TASKS[chat_id] = task


@app.on_message(
    filters.command(
        [
            "stoputag",
            "stopuall",
            "offutag",
            "offuall",
            "utagoff",
            "ualloff",
        ],
        prefixes=["/", ".", "@", "#"],
    )
    & admin_filter
)
async def stop_tagging(_, message):

    chat_id = message.chat.id

    task = TAG_TASKS.get(chat_id)

    if not task or task.done():

        SPAM_CHATS[chat_id] = False

        return await message.reply_text(
            "<b><blockquote>"
            "ℹ️ ᴜᴛᴀɢ ᴘʀᴏᴄᴇss ɪs ɴᴏᴛ ᴀᴄᴛɪᴠᴇ."
            "</blockquote></b>",
            parse_mode=enums.ParseMode.HTML,
        )

    SPAM_CHATS[chat_id] = False

    await message.reply_text(
        "<b><blockquote>"
        "⏳ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...\n\n"
        "🛑 sᴛᴏᴘᴘɪɴɢ ᴜᴛᴀɢ..."
        "</blockquote></b>",
        parse_mode=enums.ParseMode.HTML,
    )
