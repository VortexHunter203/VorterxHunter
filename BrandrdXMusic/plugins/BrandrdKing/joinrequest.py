import asyncio
import logging
from typing import Dict, Tuple

import aiohttp

from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatJoinRequest,
)

from BrandrdXMusic import app
from config import BOT_TOKEN, OWNER_ID


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.WARNING)

PENDING_REQUESTS: Dict[Tuple[int, int], dict] = {}
PROCESSING_REQUESTS = set()


# =========================================================
# HELPERS
# =========================================================

def user_mention(user) -> str:
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
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing.")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    timeout = aiohttp.ClientTimeout(total=20)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, json=data) as response:
            result = await response.json()

            if not result.get("ok"):
                raise RuntimeError(
                    result.get(
                        "description",
                        "Telegram Bot API error",
                    )
                )

            return result


# =========================================================
# OWNER NOTIFICATION
# =========================================================

async def notify_owner(client, request: ChatJoinRequest):
    try:
        user = request.from_user
        chat = request.chat

        text = (
            "🔔 <b>New Join Request</b>\n\n"
            f"👤 <b>User:</b> {user_mention(user)}\n"
            f"🆔 <b>User ID:</b> <code>{user.id}</code>\n\n"
            f"💬 <b>Chat:</b> <b>{safe_text(chat.title)}</b>\n"
            f"🆔 <b>Chat ID:</b> <code>{chat.id}</code>\n\n"
            "📥 <b>Status:</b> Pending\n"
            "⏳ Waiting for manual approval."
        )

        await client.send_message(OWNER_ID, text)

    except Exception:
        LOGGER.exception("Owner notification failed")


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

        if not user or not chat:
            return

        user_id = int(user.id)
        chat_id = int(chat.id)

        chat_title = chat.title or "this group"
        request_key = (user_id, chat_id)

        # Save pending request
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

        # Notify owner
        asyncio.create_task(
            notify_owner(client, request)
        )

        # Get bot information
        bot = await client.get_me()

        if not bot.username:
            LOGGER.error("Bot username is missing.")
            return

        # Deep link to original bot start
        start_link = (
            f"https://t.me/{bot.username}"
            f"?start=join_{user_id}_{chat_id}"
        )

        text = (
            "<blockquote>"
            f"👋 Hello {user_mention(user)}!\n\n"
            f"The admin of <b>{safe_text(chat_title)}</b> "
            "is trying to contact you about your join request.\n\n"
            "Please click the button below to open the bot "
            "and view its original welcome message."
            "</blockquote>"
        )

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔓 Unblock Bot",
                        url=start_link,
                    )
                ]
            ]
        )

        dm_chat_id = getattr(
            request,
            "user_chat_id",
            None,
        ) or user_id

        await client.send_message(
            chat_id=dm_chat_id,
            text=text,
            reply_markup=keyboard,
        )

    except Exception:
        LOGGER.exception("Join request handler failed")


# =========================================================
# CLEANUP
# =========================================================

async def cleanup_pending_requests():
    while True:
        try:
            await asyncio.sleep(1800)

            if len(PENDING_REQUESTS) > 5000:
                LOGGER.warning(
                    "Pending request cache exceeded 5000 entries."
                )
                PENDING_REQUESTS.clear()

        except asyncio.CancelledError:
            break

        except Exception:
            LOGGER.exception("Pending request cleanup failed")
