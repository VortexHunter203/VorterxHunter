import asyncio
import logging
import time
import html

from pyrogram import enums, filters
from pyrogram.enums import ChatMemberStatus, ButtonStyle
from pyrogram.errors import FloodWait
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

# ==============================
# VC LOGGER SETTINGS
# ==============================

VC_EVENT_CACHE = {}
VC_CHAT_LOCKS = {}
VC_REGISTERED = set()
VC_PYRO_CLIENTS = {}

VC_FLOOD_UNTIL = 0

VC_DUPLICATE_DELAY = 15
VC_SEND_DELAY = 2
VC_DELETE_DELAY = 5

VC_SEND_LOCK = asyncio.Lock()


# ==============================
# JOIN VC BUTTON
# ==============================

keyboard = await _vc_join_keyboard(chat_id, app)
    client = client or app

    chat_id_str = str(chat_id)

    try:
        chat = await client.get_chat(chat_id)
        username = getattr(chat, "username", None)

        if username:
            vc_url = f"https://t.me/{username}?voicechat"

        elif chat_id_str.startswith("-100"):
            vc_url = f"https://t.me/c/{chat_id_str[4:]}?voicechat"

        else:
            LOG.warning(
                "[VC Logger] Cannot create VC button: chat=%s",
                chat_id,
            )
            return None

    except Exception:
        LOG.exception(
            "[VC Logger] Chat lookup failed: chat=%s",
            chat_id,
        )

        if chat_id_str.startswith("-100"):
            vc_url = f"https://t.me/c/{chat_id_str[4:]}?voicechat"
        else:
            return None

    try:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="🎧 Join To VC",
                        url=vc_url,
                    )
                ]
            ]
        )

        LOG.info(
            "[VC Logger] Join VC button created: %s",
            vc_url,
        )

        return keyboard

    except Exception:
        LOG.exception(
            "[VC Logger] Keyboard creation failed: chat=%s",
            chat_id,
        )
        return None


# ==============================
# AUTO DELETE NOTIFICATION
# ==============================

async def _vc_delete_later(message):

    try:
        await asyncio.sleep(VC_DELETE_DELAY)

        while True:

            try:
                await message.delete()

                LOG.info(
                    "[VC Logger] Notification deleted after %s seconds",
                    VC_DELETE_DELAY,
                )

                break

            except FloodWait as error:

                seconds = max(1, int(error.value))

                LOG.warning(
                    "[VC Logger] Delete FloodWait: waiting %s seconds",
                    seconds,
                )

                await asyncio.sleep(seconds + 1)

            except asyncio.CancelledError:
                raise

            except Exception:
                LOG.exception(
                    "[VC Logger] Notification auto-delete failed"
                )
                break

    except asyncio.CancelledError:
        raise

    except Exception:
        LOG.exception("[VC Logger] Auto-delete task failed")


# ==============================
# FLOODWAIT HANDLER
# ==============================

async def _vc_wait_for_flood():

    global VC_FLOOD_UNTIL

    while True:

        remaining = VC_FLOOD_UNTIL - time.monotonic()

        if remaining <= 0:
            return

        LOG.warning(
            "[VC Logger] Telegram cooldown: %.1f seconds",
            remaining,
        )

        await asyncio.sleep(remaining + 1)


# ==============================
# VC LOGGER ON / OFF COMMAND
# ==============================

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
                "Voice Chat Logging Is Now Stopped."
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


# ==============================
# USER MENTION
# ==============================

async def vclogger_mention(user_id: int, client=None):
    """Return a clickable mention using the user's actual first name."""
    client = client or app

    try:
        user = await client.get_users(user_id)
        name = user.first_name or "User"
    except Exception:
        name = "User"

    return (
        f"<a href='tg://user?id={user_id}'>"
        f"{html.escape(name)}</a>"
    )


# ==============================
# USER ROLE
# ==============================

async def _vc_get_role(client, chat_id, user_id):

    try:

        member = await client.get_chat_member(
            chat_id,
            user_id,
        )

        if member.status == ChatMemberStatus.OWNER:
            return "OWNER"

        if member.status == ChatMemberStatus.ADMINISTRATOR:
            return "ADMIN"

        return "MEMBER"

    except FloodWait as error:

        global VC_FLOOD_UNTIL

        VC_FLOOD_UNTIL = max(
            VC_FLOOD_UNTIL,
            time.monotonic() + int(error.value) + 2,
        )

        LOG.warning(
            "[VC Logger] Role lookup FloodWait: %s seconds",
            error.value,
        )

        return "MEMBER"

    except Exception:
        return "MEMBER"


# ==============================
# SEND VC NOTIFICATION
# ==============================

async def _vc_send_notification(
    client,
    chat_id,
    user_id,
    event_type,
):

    global VC_FLOOD_UNTIL

    if event_type == "joined":
        tag = "#JᴏɪɴᴇᴅVᴄ"

    else:
        tag = "#LᴇғᴛVᴄ"

    role = await _vc_get_role(
        client,
        chat_id,
        user_id,
    )

    mention = await vclogger_mention(user_id, client)

    text = (
        f"<b><blockquote>{tag}\n\n"
        f"➤ Usᴇʀ - {mention}\n"
        f"➤ Usᴇʀɪᴅ - <code>{user_id}</code>\n"
        f"➤ Rᴏʟᴇ - {role}"
        "</blockquote></b>"
    )

    # Create Join VC button

    keyboard = await _vc_join_keyboard(chat_id, client)

    if keyboard is None:
        LOG.error(
            "[VC Logger] Join button is None: chat=%s",
            chat_id,
        )
    else:
        LOG.info(
            "[VC Logger] Join button created: chat=%s",
             chat_id,
        )
        
    async with VC_SEND_LOCK:

        if not await is_vclogger_on(chat_id):
            return None

        await _vc_wait_for_flood()

        try:

            sent = await client.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True,
            )

            LOG.info(
                "[VC Logger] Notification sent: chat=%s user=%s event=%s",
                chat_id,
                user_id,
                event_type,
            )

            # Delete notification after 10 seconds

            asyncio.create_task(
                _vc_delete_later(sent)
            )

            await asyncio.sleep(VC_SEND_DELAY)

            return sent

        except FloodWait as error:

            seconds = max(1, int(error.value))

            VC_FLOOD_UNTIL = max(
                VC_FLOOD_UNTIL,
                time.monotonic() + seconds + 2,
            )

            LOG.warning(
                "[VC Logger] FloodWait: %s seconds. Waiting before one retry.",
                seconds,
            )

            await _vc_wait_for_flood()

            if not await is_vclogger_on(chat_id):
                return None

            try:

                sent = await app.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML,
                    disable_web_page_preview=True,
                )

                LOG.info(
                    "[VC Logger] Notification sent after FloodWait: chat=%s user=%s",
                    chat_id,
                    user_id,
                )

                # Delete retry notification after 10 seconds

                asyncio.create_task(
                    _vc_delete_later(sent)
                )

                await asyncio.sleep(VC_SEND_DELAY)

                return sent

            except FloodWait as retry_error:

                VC_FLOOD_UNTIL = max(
                    VC_FLOOD_UNTIL,
                    time.monotonic() + int(retry_error.value) + 2,
                )

                LOG.error(
                    "[VC Logger] Second FloodWait. Event skipped: %s seconds",
                    retry_error.value,
                )

                return None

            except Exception:

                LOG.exception(
                    "[VC Logger] Retry message failed: chat=%s user=%s",
                    chat_id,
                    user_id,
                )

                return None

        except asyncio.CancelledError:
            raise

        except Exception:

            LOG.exception(
                "[VC Logger] Message sending failed: chat=%s user=%s",
                chat_id,
                user_id,
            )

            return None


# ==============================
# VC PARTICIPANT HANDLER
# ==============================

async def participants_change_handler(
    client,
    update: UpdatedGroupCallParticipant,
):

    try:

        pyro_client = VC_PYRO_CLIENTS.get(
            id(client),
            app,
        )

        chat_id = getattr(update, "chat_id", None)
        participant = getattr(update, "participant", None)
        action = getattr(update, "action", None)

        if chat_id is None or participant is None:
            return

        if action == GroupCallParticipant.Action.JOINED:
            event_type = "joined"

        elif action == GroupCallParticipant.Action.LEFT:
            event_type = "left"

        else:
            return

        user_id = getattr(
            participant,
            "user_id",
            None,
        )

        if not user_id:
            return

        if not await is_vclogger_on(chat_id):
            return

        event_key = (
            chat_id,
            user_id,
            event_type,
        )

        now = time.monotonic()

        # Clean expired events

        for key, timestamp in list(VC_EVENT_CACHE.items()):

            if now - timestamp >= VC_DUPLICATE_DELAY:
                VC_EVENT_CACHE.pop(key, None)

        # Chat-wise event lock

        lock = VC_CHAT_LOCKS.setdefault(
            chat_id,
            asyncio.Lock(),
        )

        async with lock:

            now = time.monotonic()

            # Block duplicate events from all 5 assistants

            last_event = VC_EVENT_CACHE.get(
                event_key,
                0,
            )

            if now - last_event < VC_DUPLICATE_DELAY:
                return

            if not await is_vclogger_on(chat_id):
                return

            # Reserve event before sending

            VC_EVENT_CACHE[event_key] = now

            LOG.info(
                "[VC Logger] %s: chat=%s user=%s",
                event_type,
                chat_id,
                user_id,
            )

            await _vc_send_notification(
                pyro_client,
                chat_id,
                user_id,
                event_type,
            )

    except asyncio.CancelledError:
        raise

    except Exception:

        LOG.exception(
            "[VC Logger] Participant handler failed"
        )


# ==============================
# REGISTER ALL 5 ASSISTANTS
# ==============================

def register_vclogger(call):

    assistants = [
        (call.one, call.userbot1),
        (call.two, call.userbot2),
        (call.three, call.userbot3),
        (call.four, call.userbot4),
        (call.five, call.userbot5),
    ]

    participant_filter = call_filters.call_participant(
        GroupCallParticipant.Action.JOINED
        | GroupCallParticipant.Action.LEFT
    )

    registered_count = 0

    for assistant, pyro_client in assistants:

        if assistant is None or pyro_client is None:
            continue

        assistant_id = id(assistant)

        VC_PYRO_CLIENTS[assistant_id] = pyro_client

        if assistant_id in VC_REGISTERED:
            continue

        assistant.add_handler(
            participants_change_handler,
            participant_filter,
        )

        VC_REGISTERED.add(assistant_id)
        registered_count += 1

    LOG.warning(
        "[VC Logger] Registered %s new assistant handlers.",
        registered_count,
    )
