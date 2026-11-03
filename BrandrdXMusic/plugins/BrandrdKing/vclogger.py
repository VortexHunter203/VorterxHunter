import asyncio
import logging
import time
import html

from pyrogram import enums, filters
from pyrogram.errors import FloodWait
from pyrogram.enums import ParseMode, ButtonStyle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from pytgcalls import filters as call_filters
from pytgcalls.types import (
    GroupCallParticipant,
    UpdatedGroupCallParticipant,
)

from BrandrdXMusic import app
from BrandrdXMusic.utils.database import (
    is_vclogger_on,
    vclogger_on,
    vclogger_off,
)


LOG = logging.getLogger(__name__)
LOG.setLevel(logging.WARNING)

VC_EVENT_CACHE = {}
VC_CHAT_LOCKS = {}
VC_REGISTERED = set()

VC_QUEUE = asyncio.Queue()
VC_WORKER = None

VC_FLOOD_UNTIL = 0

VC_DUPLICATE_DELAY = 15
VC_SEND_DELAY = 2
VC_DELETE_DELAY = 5


# VC LOGGER ENABLE / DISABLE COMMAND

@app.on_message(filters.command("vclogger") & filters.group)
async def vclogger_command(client, message):
    chat_id = message.chat.id

    try:
        if not message.from_user:
            return

        member = await client.get_chat_member(
            chat_id,
            message.from_user.id,
        )

        if member.status not in (
            ChatMemberStatus.OWNER,
            ChatMemberStatus.ADMINISTRATOR,
        ):
            return await message.reply_text(
                "<b>❌ Only Admins Can Manage VC Logger.</b>",
                parse_mode=enums.ParseMode.HTML,
            )

        if len(message.command) < 2:
            status = await is_vclogger_on(chat_id)

            return await message.reply_text(
                "<b><blockquote>"
                "🎧 VC LOGGER SETTINGS\n\n"
                f"Status : {'ENABLED ✅' if status else 'DISABLED ❌'}\n\n"
                "➤ /vclogger on\n"
                "➤ /vclogger off"
                "</blockquote></b>",
                parse_mode=enums.ParseMode.HTML,
            )

        action = message.command[1].lower()

        if action in ("on", "enable"):
            await vclogger_on(chat_id)

            return await message.reply_text(
                "<b><blockquote>"
                "✅ VC LOGGER ENABLED\n\n"
                "Voice Chat Join/Leave Logging Is Now Active."
                "</blockquote></b>",
                parse_mode=enums.ParseMode.HTML,
            )

        elif action in ("off", "disable"):
            await vclogger_off(chat_id)

            return await message.reply_text(
                "<b><blockquote>"
                "❌ VC LOGGER DISABLED\n\n"
                "Voice Chat Join/Leave Logging Is Now Stopped."
                "</blockquote></b>",
                parse_mode=enums.ParseMode.HTML,
            )

        return await message.reply_text(
            "<b>Usage: /vclogger on | off</b>",
            parse_mode=enums.ParseMode.HTML,
        )

    except asyncio.CancelledError:
        raise

    except Exception:
        LOG.exception("[VC Logger] Command failed")


# USER MENTION

async def vclogger_mention(user_id: int):
    try:
        user = await app.get_users(user_id)
        name = user.first_name or "User"

    except Exception:
        name = "User"

    return (
        f"<a href='tg://user?id={user_id}'>"
        f"{html.escape(name)}</a>"
    )


# AUTO DELETE AFTER 5 SECONDS

async def _vc_delete_later(message):
    try:
        await asyncio.sleep(VC_DELETE_DELAY)

        while True:
            try:
                await message.delete()
                return

            except FloodWait as error:
                seconds = max(1, int(error.value))
                LOG.warning(
                    "[VC Logger] Delete FloodWait: %s seconds",
                    seconds,
                )
                await asyncio.sleep(seconds + 1)

            except Exception:
                return

    except asyncio.CancelledError:
        raise

    except Exception:
        LOG.exception("[VC Logger] Auto delete failed")


# JOIN VC BUTTON

async def _vc_join_keyboard(chat_id):
    try:
        chat = await app.get_chat(chat_id)
        username = getattr(chat, "username", None)

        if username:
            vc_url = f"https://t.me/{username}?voicechat"

        elif str(chat_id).startswith("-100"):
            vc_url = (
                f"https://t.me/c/{str(chat_id)[4:]}?voicechat"
            )

        else:
            return None

        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🎧 Join To VC",
                        url=vc_url,
                        style=ButtonStyle.SUCCESS,
                    )
                ]
            ]
        )

    except Exception:
        return None


# CLEAN EXPIRED DUPLICATE EVENTS

def _vc_clean_cache():
    now = time.monotonic()

    for key, timestamp in list(VC_EVENT_CACHE.items()):
        if now - timestamp >= VC_DUPLICATE_DELAY:
            VC_EVENT_CACHE.pop(key, None)


# SEND VC MESSAGE

async def _vc_send_event(chat_id, user_id, event_type, tag):

    if not await is_vclogger_on(chat_id):
        return False

    role = "MEMBER"

    try:
        member = await app.get_chat_member(
            chat_id,
            user_id,
        )

        if member.status == ChatMemberStatus.OWNER:
            role = "OWNER"

        elif member.status == ChatMemberStatus.ADMINISTRATOR:
            role = "ADMIN"

    except Exception:
        pass

    mention = await vclogger_mention(user_id)

    text = (
        f"<b><blockquote>{tag}\n\n"
        f"➤ Usᴇʀ - {mention}\n"
        f"➤ Usᴇʀɪᴅ - <code>{user_id}</code>\n"
        f"➤ Rᴏʟᴇ - {role}"
        "</blockquote></b>"
    )

    keyboard = await _vc_join_keyboard(chat_id)

    global VC_FLOOD_UNTIL

    while True:

        if not await is_vclogger_on(chat_id):
            return False

        # Respect global Telegram FloodWait.
        now = time.monotonic()

        if now < VC_FLOOD_UNTIL:
            await asyncio.sleep(VC_FLOOD_UNTIL - now)

        try:
            sent_message = await app.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True,
            )

            asyncio.create_task(
                _vc_delete_later(sent_message)
            )

            LOG.warning(
                "[VC Logger] %s notification sent: chat=%s user=%s",
                event_type,
                chat_id,
                user_id,
            )

            return True

        except FloodWait as error:
            seconds = max(1, int(error.value))

            VC_FLOOD_UNTIL = (
                time.monotonic() + seconds + 2
            )

            LOG.warning(
                "[VC Logger] Telegram FloodWait: waiting %s seconds",
                seconds,
            )

            await asyncio.sleep(seconds + 2)

        except asyncio.CancelledError:
            raise

        except Exception:
            LOG.exception(
                "[VC Logger] Message sending failed: chat=%s user=%s",
                chat_id,
                user_id,
            )
            return False


# CENTRAL VC MESSAGE QUEUE

async def _vc_message_worker():

    LOG.warning("[VC Logger] Message queue worker started.")

    while True:
        event = await VC_QUEUE.get()

        chat_id, user_id, event_type, tag, event_key = event

        try:
            success = await _vc_send_event(
                chat_id,
                user_id,
                event_type,
                tag,
            )

            if not success:
                VC_EVENT_CACHE.pop(event_key, None)

            else:
                VC_EVENT_CACHE[event_key] = time.monotonic()

            await asyncio.sleep(VC_SEND_DELAY)

        except asyncio.CancelledError:
            VC_EVENT_CACHE.pop(event_key, None)
            raise

        except Exception:
            VC_EVENT_CACHE.pop(event_key, None)

            LOG.exception(
                "[VC Logger] Queue processing failed"
            )

        finally:
            VC_QUEUE.task_done()


# START QUEUE WORKER

def _start_vc_worker():
    global VC_WORKER

    if VC_WORKER is None or VC_WORKER.done():
        VC_WORKER = asyncio.create_task(
            _vc_message_worker()
        )


# VC JOIN / LEFT LOGGER - PyTgCalls v3

async def participants_change_handler(_, update: UpdatedGroupCallParticipant):

    try:
        chat_id = getattr(update, "chat_id", None)
        participant = getattr(update, "participant", None)
        action = getattr(update, "action", None)

        if chat_id is None or participant is None:
            return

        if action == GroupCallParticipant.Action.JOINED:
            tag = "#JᴏɪɴᴇᴅVᴄ"
            event_type = "joined"

        elif action == GroupCallParticipant.Action.LEFT:
            tag = "#LᴇғᴛVᴄ"
            event_type = "left"

        else:
            return

        user_id = getattr(participant, "user_id", None)

        if user_id is None:
            return

        if not await is_vclogger_on(chat_id):
            return

        event_key = (chat_id, user_id, event_type)

        lock = VC_CHAT_LOCKS.setdefault(
            chat_id,
            asyncio.Lock(),
        )

        async with lock:

            _vc_clean_cache()

            # Prevent duplicate events from all assistants.
            if event_key in VC_EVENT_CACHE:
                return

            # Reserve event before queueing.
            VC_EVENT_CACHE[event_key] = time.monotonic()

            _start_vc_worker()

            await VC_QUEUE.put(
                (
                    chat_id,
                    user_id,
                    event_type,
                    tag,
                    event_key,
                )
            )

            LOG.warning(
                "[VC Logger] Event queued: %s chat=%s user=%s",
                event_type,
                chat_id,
                user_id,
            )

    except asyncio.CancelledError:
        raise

    except Exception:
        LOG.exception(
            "[VC Logger] Participant handler failed"
        )


# REGISTER LOGGER WITH ALL 5 ASSISTANTS

def register_vclogger(call):

    assistants = [
        call.one,
        call.two,
        call.three,
        call.four,
        call.five,
    ]

    participant_filter = call_filters.call_participant(
        GroupCallParticipant.Action.JOINED
        | GroupCallParticipant.Action.LEFT
    )

    registered = 0

    for assistant in assistants:

        if assistant is None:
            continue

        assistant_id = id(assistant)

        if assistant_id in VC_REGISTERED:
            continue

        assistant.add_handler(
            participants_change_handler,
            participant_filter,
        )

        VC_REGISTERED.add(assistant_id)
        registered += 1

    LOG.warning(
        "[VC Logger] Participant handlers registered: %s",
        registered,
    )
