import asyncio
import logging
from typing import Dict, Tuple

import aiohttp
from pyrogram.enums import ChatMemberStatus, ButtonStyle
from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatJoinRequest,
    Message,
)

from BrandrdXMusic import app
from config import BOT_TOKEN, OWNER_ID


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.WARNING)


# =========================================================
# CONFIG
# =========================================================

PENDING_REQUESTS: Dict[Tuple[int, int], dict] = {}

# Prevent duplicate processing
PROCESSING_REQUESTS = set()


# =========================================================
# HELPERS
# =========================================================

def user_mention(user) -> str:
    """Create safe Telegram HTML mention."""
    name = user.first_name or "User"

    name = (
        str(name)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )

    return f'<a href="tg://user?id={user.id}">{name}</a>'


def safe_text(value, default="Unknown") -> str:
    """Make text safe for Telegram HTML."""
    if not value:
        return default

    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# =========================================================
# TELEGRAM BOT API
# =========================================================

async def bot_api(method: str, data: dict):
    """Call Telegram Bot API directly."""

    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN is missing in environment variables."
        )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    timeout = aiohttp.ClientTimeout(total=20)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, json=data) as response:
            try:
                result = await response.json()
            except Exception:
                result = {
                    "ok": False,
                    "description": await response.text(),
                }

            if not result.get("ok"):
                description = result.get(
                    "description",
                    "Unknown Telegram Bot API error",
                )
                error_code = result.get("error_code")

                raise RuntimeError(
                    f"Telegram Bot API error "
                    f"{error_code}: {description}"
                )

            return result


async def approve_join_request(chat_id: int, user_id: int) -> bool:
    """Approve a pending join request through Telegram Bot API."""

    result = await bot_api(
        "approveChatJoinRequest",
        {
            "chat_id": int(chat_id),
            "user_id": int(user_id),
        },
    )

    return bool(result.get("ok"))


# =========================================================
# OWNER NOTIFICATION
# =========================================================

async def notify_owner(client, request: ChatJoinRequest):
    """Send join request notification to OWNER_ID."""

    try:
        user = request.from_user
        chat = request.chat

        text = (
            "🔔 <b>New Join Request</b>\n\n"
            f"👤 <b>User:</b> {user_mention(user)}\n"
            f"🆔 <b>User ID:</b> <code>{user.id}</code>\n\n"
            f"💬 <b>Chat:</b> "
            f"<b>{safe_text(chat.title)}</b>\n"
            f"🆔 <b>Chat ID:</b> <code>{chat.id}</code>\n\n"
            "📥 <b>Status:</b> Pending\n"
            "⏳ Waiting for user verification."
        )

        await client.send_message(OWNER_ID, text)

        LOGGER.info(
            "Owner notification sent | user=%s chat=%s",
            user.id,
            chat.id,
        )

    except Exception as e:
        LOGGER.error(
            "Owner notification failed | error=%s",
            e,
            exc_info=True,
        )


# =========================================================
# JOIN REQUEST HANDLER
# =========================================================

@app.on_chat_join_request()
async def handle_join_request(
    client,
    request: ChatJoinRequest,
):
    try:
        user = request.from_user
        chat = request.chat

        if not user:
            LOGGER.warning("Join request received without user.")
            return

        if not chat:
            LOGGER.warning("Join request received without chat.")
            return

        user_id = int(user.id)
        chat_id = int(chat.id)
        chat_title = chat.title or "this group"
        request_key = (user_id, chat_id)

        # INFO logs are disabled for this module.
        # Request processing and notifications remain enabled.

        # -------------------------------------------------
        # SAVE REQUEST
        # -------------------------------------------------

        PENDING_REQUESTS[request_key] = {
            "chat_id": chat_id,
            "user_id": user_id,
            "user_chat_id": getattr(
                request,
                "user_chat_id",
                user_id,
            ),
            "user_name": user.first_name or "User",
            "chat_title": chat_title,
        }

        # -------------------------------------------------
        # OWNER NOTIFICATION
        # -------------------------------------------------

        asyncio.create_task(
            notify_owner(client, request)
        )

        # -------------------------------------------------
        # BOT INFORMATION
        # -------------------------------------------------

        try:
            bot = await client.get_me()
        except Exception as e:
            LOGGER.error(
                "get_me() failed: %s",
                e,
                exc_info=True,
            )
            return

        if not bot.username:
            LOGGER.error(
                "Bot has no username. Cannot create start link."
            )
            return

        bot_name = bot.first_name or "Angel Music Bot"

        # -------------------------------------------------
        # START LINK
        # -------------------------------------------------

        start_link = (
            f"https://t.me/{bot.username}"
            f"?start=join_{user_id}_{chat_id}"
        )

        # -------------------------------------------------
        # MESSAGE
        # -------------------------------------------------

        text = (
            f"<blockquote>"
            f"👋 Hello {user_mention(user)}!\n\n"
            f"The admin of <b>{safe_text(chat_title)}</b> "
            f"is trying to contact you about your recent "
            f"join request.\n\n"
            f"If you would like to get approved, "
            f"please remove <b>{safe_text(bot_name)}</b> "
            f"from your list of blocked users or simply "
            f"press the button below this message."
            f"</blockquote>"
        )

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔓 Unblock Bot",
                        url=start_link,
                        style=ButtonStyle.SUCCESS
                    )
                ]
            ]
        )

        # -------------------------------------------------
        # SEND DM
        # -------------------------------------------------

        user_chat_id = getattr(
            request,
            "user_chat_id",
            None,
        )
        dm_chat_id = user_chat_id or user_id

        try:
            await client.send_message(
                chat_id=dm_chat_id,
                text=text,
                reply_markup=keyboard,
            )

            LOGGER.info(
                "Join request DM sent | "
                "user=%s dm_chat=%s group=%s",
                user_id,
                dm_chat_id,
                chat_id,
            )

        except Exception as e:
            LOGGER.error(
                "Could not DM join requester | "
                "user=%s dm_chat=%s group=%s error=%s",
                user_id,
                dm_chat_id,
                chat_id,
                e,
                exc_info=True,
            )
            return

    except Exception as e:
        LOGGER.error(
            "Join request handler failed: %s",
            e,
            exc_info=True,
        )


# =========================================================
# /START HANDLER
# =========================================================

@app.on_message(
    filters.private & filters.command("start"),
    group=-1,
)
async def join_start_handler(
    client,
    message: Message,
):
    try:
        if not message.from_user:
            return

        actual_user_id = int(message.from_user.id)

        # =====================================================
        # CASE 1: DEEP-LINK /start join_USER_ID_CHAT_ID
        # =====================================================

        payload = None

        if len(message.command) >= 2:
            payload = message.command[1]

        if payload and payload.startswith("join_"):
            parts = payload.split("_")

            if len(parts) != 3:
                await message.reply_text(
                    "<blockquote>❌ Invalid join request link.</blockquote>"
                )
                return

            try:
                requested_user_id = int(parts[1])
                requested_chat_id = int(parts[2])
            except (ValueError, IndexError):
                await message.reply_text(
                    "<blockquote>❌ Invalid join request data.</blockquote>"
                )
                return

            if actual_user_id != requested_user_id:
                await message.reply_text(
                    "<blockquote>❌ This join request link is not for you.</blockquote>"
                )
                return

            request_key = (
                requested_user_id,
                requested_chat_id,
            )

            if request_key in PROCESSING_REQUESTS:
                await message.reply_text(
                    "⏳ Your join request is already being processed."
                )
                return

            PROCESSING_REQUESTS.add(request_key)

            try:
                pending = PENDING_REQUESTS.get(request_key)

                if not pending:
                    await message.reply_text(
                        "<blockquote>"
                        "⚠️ This join request has expired "
                        "or was already processed."
                        "</blockquote>"
                    )
                    return

                chat_id = int(pending["chat_id"])
                user_id = int(pending["user_id"])
                chat_title = pending.get("chat_title", "the group")

                LOGGER.info(
                    "Processing deep-link join request | "
                    "user=%s chat=%s title=%s",
                    user_id,
                    chat_id,
                    chat_title,
                )

                try:
                    approved = await approve_join_request(
                        chat_id=chat_id,
                        user_id=user_id,
                    )

                except Exception as e:
                    LOGGER.error(
                        "Telegram approval failed | "
                        "user=%s chat=%s error=%s",
                        user_id,
                        chat_id,
                        e,
                        exc_info=True,
                    )

                    error_text = str(e)

                    if "CHANNEL_INVALID" in error_text:
                        reply = (
                            "❌ <b>Telegram rejected this group.</b>\n\n"
                            "The group/channel ID is invalid or "
                            "the bot no longer has access to it.\n\n"
                            f"<code>{chat_id}</code>"
                        )

                    elif (
                        "CHAT_ADMIN_REQUIRED" in error_text
                        or "administrator" in error_text.lower()
                        or "RIGHT_FORBIDDEN" in error_text
                    ):
                        reply = (
                            "❌ <b>Bot permission problem.</b>\n\n"
                            "Please make sure I am an administrator "
                            "of the group with permission to "
                            "<b>Invite Users / Add Members</b>."
                        )

                    elif "USER_NOT_FOUND" in error_text:
                        reply = (
                            "❌ Telegram could not find the "
                            "pending join request."
                        )

                    else:
                        reply = (
                            "⚠️ <b>Approval failed.</b>\n\n"
                            "Please try again after a few seconds."
                        )

                    await message.reply_text(reply)
                    return

                if approved:
                    PENDING_REQUESTS.pop(request_key, None)

                    await message.reply_text(
                        "<blockquote>"
                        "✅ <b>Unblocked & Approved!</b>\n\n"
                        f"Your join request for "
                        f"<b>{safe_text(chat_title)}</b> "
                        f"has been approved successfully. 🎉"
                        "</blockquote>"
                    )

                    LOGGER.info(
                        "JOIN REQUEST APPROVED VIA DEEP LINK | "
                        "user=%s chat=%s",
                        user_id,
                        chat_id,
                    )

                else:
                    await message.reply_text(
                        "⚠️ Telegram did not confirm the approval."
                    )

            finally:
                PROCESSING_REQUESTS.discard(request_key)

            return

        # =====================================================
        # CASE 2: NORMAL /start
        # =====================================================

        pending_matches = []

        for request_key, pending in list(PENDING_REQUESTS.items()):
            try:
                pending_user_id = int(
                    pending.get("user_id", request_key[0])
                )

                if pending_user_id == actual_user_id:
                    pending_matches.append((request_key, pending))

            except Exception:
                continue

        if not pending_matches:
            return

        request_key, pending = pending_matches[-1]

        chat_id = int(pending["chat_id"])
        user_id = int(pending["user_id"])
        chat_title = pending.get("chat_title", "the group")

        if request_key in PROCESSING_REQUESTS:
            await message.reply_text(
                "⏳ Your join request is already being processed."
            )
            return

        PROCESSING_REQUESTS.add(request_key)

        try:
            LOGGER.info(
                "NORMAL /start DETECTED FOR PENDING REQUEST | "
                "user=%s chat=%s title=%s",
                user_id,
                chat_id,
                chat_title,
            )

            try:
                approved = await approve_join_request(
                    chat_id=chat_id,
                    user_id=user_id,
                )

            except Exception as e:
                LOGGER.error(
                    "Normal /start approval failed | "
                    "user=%s chat=%s error=%s",
                    user_id,
                    chat_id,
                    e,
                    exc_info=True,
                )

                error_text = str(e)

                if "CHANNEL_INVALID" in error_text:
                    reply = (
                        "❌ <b>Telegram rejected this group.</b>\n\n"
                        "The group/channel ID is invalid or "
                        "the bot no longer has access to it.\n\n"
                        f"<code>{chat_id}</code>"
                    )

                elif (
                    "CHAT_ADMIN_REQUIRED" in error_text
                    or "administrator" in error_text.lower()
                    or "RIGHT_FORBIDDEN" in error_text
                ):
                    reply = (
                        "❌ <b>Bot permission problem.</b>\n\n"
                        "Please make sure I am an administrator "
                        "of the group with permission to "
                        "<b>Invite Users / Add Members</b>."
                    )

                elif "USER_NOT_FOUND" in error_text:
                    reply = (
                        "⚠️ Your join request is no longer pending "
                        "or has already been processed."
                    )

                else:
                    reply = (
                        "⚠️ <b>Verification failed.</b>\n\n"
                        "Please try pressing Start again."
                    )

                await message.reply_text(reply)
                return

            if approved:
                PENDING_REQUESTS.pop(request_key, None)

                await message.reply_text(
                    "<blockquote>"
                    "✅ <b>Verification Successful!</b>\n\n"
                    f"Your join request for "
                    f"<b>{safe_text(chat_title)}</b> "
                    "has been approved successfully. 🎉\n\n"
                    "Welcome to the group! ❤️"
                    "</blockquote>"
                )

                LOGGER.info(
                    "JOIN REQUEST APPROVED AFTER NORMAL /start | "
                    "user=%s chat=%s",
                    user_id,
                    chat_id,
                )

                # Notify owner that verification is completed.
                try:
                    await client.send_message(
                        OWNER_ID,
                        (
                            "✅ <b>Join Request Approved</b>\n\n"
                            f"👤 <b>User:</b> "
                            f"{user_mention(message.from_user)}\n"
                            f"🆔 <b>User ID:</b> "
                            f"<code>{user_id}</code>\n"
                            f"💬 <b>Chat:</b> "
                            f"<b>{safe_text(chat_title)}</b>\n"
                            f"🆔 <b>Chat ID:</b> "
                            f"<code>{chat_id}</code>\n\n"
                            "🔓 User unblocked the bot and "
                            "pressed Start."
                        ),
                    )

                except Exception as e:
                    LOGGER.error(
                        "Owner approval notification failed: %s",
                        e,
                        exc_info=True,
                    )

            else:
                await message.reply_text(
                    "<blockquote>"
                    "⚠️ Telegram did not confirm the approval."
                    "</blockquote>"
                )

        finally:
            PROCESSING_REQUESTS.discard(request_key)

    except Exception as e:
        LOGGER.error(
            "Join /start handler failed: %s",
            e,
            exc_info=True,
        )


# =========================================================
# CLEANUP
# =========================================================

async def cleanup_pending_requests():
    """Remove excess in-memory pending requests."""

    while True:
        try:
            await asyncio.sleep(1800)

            if len(PENDING_REQUESTS) > 5000:
                LOGGER.warning(
                    "Pending request cache exceeded 5000 entries. "
                    "Clearing cache."
                )
                PENDING_REQUESTS.clear()

        except asyncio.CancelledError:
            break

        except Exception:
            LOGGER.exception("Pending request cleanup failed")
