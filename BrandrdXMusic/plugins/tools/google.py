import asyncio
import html
import logging
import urllib.parse

import aiohttp
from bs4 import BeautifulSoup
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from BrandrdXMusic import app

LOGGER = logging.getLogger(__name__)


# =========================================================
# SEARCH ENGINE
# =========================================================

async def search_web(query: str, limit: int = 8):
    encoded_query = urllib.parse.quote_plus(query)

    urls = [
        f"https://html.duckduckgo.com/html/?q={encoded_query}",
        f"https://lite.duckduckgo.com/lite/?q={encoded_query}",
    ]

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,"
                  "application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
    }

    timeout = aiohttp.ClientTimeout(total=20)

    try:
        async with aiohttp.ClientSession(
            headers=headers,
            timeout=timeout
        ) as session:

            for url in urls:

                try:
                    async with session.get(
                        url,
                        allow_redirects=True
                    ) as response:

                        page = await response.text(
                            errors="ignore"
                        )

                        LOGGER.info(
                            "Search response: HTTP %s, %s bytes",
                            response.status,
                            len(page)
                        )

                        # 200 OR 202 can contain usable HTML
                        if response.status not in (200, 202):
                            continue

                        soup = BeautifulSoup(
                            page,
                            "html.parser"
                        )

                        results = []
                        seen = set()

                        # -----------------------------
                        # DuckDuckGo normal HTML
                        # -----------------------------

                        for result in soup.select(
                            ".result"
                        ):

                            link_tag = result.select_one(
                                ".result__a"
                            )

                            if not link_tag:
                                continue

                            result_url = link_tag.get(
                                "href",
                                ""
                            )

                            title = link_tag.get_text(
                                " ",
                                strip=True
                            )

                            description_tag = (
                                result.select_one(
                                    ".result__snippet"
                                )
                            )

                            description = ""

                            if description_tag:
                                description = (
                                    description_tag.get_text(
                                        " ",
                                        strip=True
                                    )
                                )

                            if result_url.startswith("//"):
                                result_url = (
                                    "https:" + result_url
                                )

                            if not result_url.startswith(
                                ("http://", "https://")
                            ):
                                continue

                            if result_url in seen:
                                continue

                            seen.add(result_url)

                            results.append(
                                {
                                    "title": title
                                    or "Search Result",
                                    "url": result_url,
                                    "description":
                                        description,
                                }
                            )

                            if len(results) >= limit:
                                return results

                        # -----------------------------
                        # Lite DuckDuckGo fallback
                        # -----------------------------

                        if not results:

                            for link_tag in soup.select(
                                "a.result-link"
                            ):

                                result_url = (
                                    link_tag.get(
                                        "href",
                                        ""
                                    )
                                )

                                title = (
                                    link_tag.get_text(
                                        " ",
                                        strip=True
                                    )
                                )

                                if not result_url:
                                    continue

                                if result_url.startswith("//"):
                                    result_url = (
                                        "https:" + result_url
                                    )

                                if not result_url.startswith(
                                    (
                                        "http://",
                                        "https://"
                                    )
                                ):
                                    continue

                                if result_url in seen:
                                    continue

                                seen.add(result_url)

                                results.append(
                                    {
                                        "title": title
                                        or "Search Result",
                                        "url": result_url,
                                        "description": "",
                                    }
                                )

                                if len(results) >= limit:
                                    return results

                        if results:
                            return results

                except Exception as e:
                    LOGGER.warning(
                        "Search endpoint failed: %s",
                        e
                    )
                    continue

        return []

    except Exception as e:
        LOGGER.exception(
            "Search failed: %s",
            e
        )
        return []


# =========================================================
# GOOGLE / SEARCH COMMAND
# =========================================================

@app.on_message(
    filters.command(
        ["google", "gle", "app", "apps"]
    )
)
async def google_search_handler(
    client,
    message
):

    # -----------------------------------------------------
    # GET QUERY FROM REPLY
    # -----------------------------------------------------

    if (
        message.reply_to_message
        and message.reply_to_message.text
    ):
        user_input = (
            message.reply_to_message.text.strip()
        )

    # -----------------------------------------------------
    # GET QUERY FROM COMMAND
    # -----------------------------------------------------

    elif len(message.command) > 1:
        user_input = " ".join(
            message.command[1:]
        ).strip()

    # -----------------------------------------------------
    # NO QUERY
    # -----------------------------------------------------

    else:
        await message.reply_text(
            "<b>❌ Pʟᴇᴀsᴇ Gɪᴠᴇ A Sᴇᴀʀᴄʜ Qᴜᴇʀʏ.</b>\n\n"
            "<blockquote>"
            "<b>Eᴜɪᴍᴘʟᴇ:</b>\n"
            "<code>/google branded king</code>\n"
            "<code>/google phone pe</code>\n"
            "<code>/app Telegram</code>"
            "</blockquote>",
            parse_mode="html"
        )
        return

    # -----------------------------------------------------
    # SEARCHING MESSAGE
    # -----------------------------------------------------

    status = await message.reply_text(
        "<b>🔎 Sᴇᴀʀᴄʜɪɴɢ...</b>\n\n"
        "<blockquote>"
        "<b>Qᴜᴇʀʏ:</b> "
        f"<code>{html.escape(user_input)}</code>"
        "</blockquote>",
    )

    try:

        results = await search_web(
            user_input,
            limit=8
        )

        # -------------------------------------------------
        # NO RESULTS
        # -------------------------------------------------

        if not results:

            await status.edit_text(
                "<b>❌ Nᴏ Rᴇsᴜʟᴛs Fᴏᴜɴᴅ.</b>\n\n"
                "<blockquote>"
                "<b>Qᴜᴇʀʏ:</b> "
                f"<code>{html.escape(user_input)}</code>"
                "</blockquote>\n\n"
                "<i>Tʀʏ A Dɪғғᴇʀᴇɴᴛ Qᴜᴇʀʏ.</i>",
            )

            return

        # -------------------------------------------------
        # BUILD RESPONSE
        # -------------------------------------------------

        text = (
            "<b>🔎 Sᴇᴀʀᴄʜ Rᴇsᴜʟᴛs</b>\n\n"
            "<blockquote>"
            "<b>Qᴜᴇʀʏ:</b> "
            f"<code>{html.escape(user_input)}</code>"
            "</blockquote>\n"
        )

        buttons = []

        for number, result in enumerate(
            results,
            start=1
        ):

            title = html.escape(
                str(result["title"])
            )

            description = html.escape(
                str(result["description"])
            )

            result_url = str(
                result["url"]
            )

            if len(title) > 100:
                title = title[:97] + "..."

            if len(description) > 300:
                description = (
                    description[:297] + "..."
                )

            text += (
                f"\n<b>❍ {number}. {title}</b>\n"
            )

            if description:
                text += (
                    "<blockquote>"
                    f"{description}"
                    "</blockquote>"
                )

            buttons.append(
                [
                    InlineKeyboardButton(
                        f"🔗 Rᴇsᴜʟᴛ {number}",
                        url=result_url
                    )
                ]
            )

        # -------------------------------------------------
        # SEND RESULTS
        # -------------------------------------------------

        await status.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                buttons
            ),
            disable_web_page_preview=True,
        )

    except Exception as e:

        LOGGER.exception(
            "Search command error: %s",
            e
        )

        await status.edit_text(
            "<b>⚠️ Sᴇᴀʀᴄʜ Eʀʀᴏʀ</b>\n\n"
            "<blockquote>"
            f"<b>Eʀʀᴏʀ:</b> "
            f"<code>{html.escape(str(e))}</code>"
            "</blockquote>",
        )


# =========================================================
# HELP
# =========================================================

__MODULE__ = "Gᴏᴏɢʟᴇ"

__HELP__ = """
<b>🔎 Wᴇʙ Sᴇᴀʀᴄʜ</b>

<blockquote>
<b>/google [query]</b> - Sᴇᴀʀᴄʜ Wᴇʙ
<b>/gle [query]</b> - Sᴀᴍᴇ Sᴇᴀʀᴄʜ
<b>/app [query]</b> - Sᴀᴍᴇ Sᴇᴀʀᴄʜ
<b>/apps [query]</b> - Sᴀᴍᴇ Sᴇᴀʀᴄʜ

<b>Eᴜɪᴍᴘʟᴇ:</b>
<code>/google branded king</code>
<code>/google phone pe</code>
<code>/app Telegram</code>
</blockquote>
"""
