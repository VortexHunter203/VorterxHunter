import base64
from html import escape
from io import BytesIO

from httpx import AsyncClient, Timeout
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from BrandrdXMusic import app


# ============================================================
# QUOTLY API CONFIG
# ============================================================

QUOTLY_API = "https://quote.yuri.ly/quote/generate"
QUOTLY_PNG_API = "https://quote.yuri.ly/quote/generate.png"

# Fallback API
FALLBACK_API = "https://quote-generator-green-three.vercel.app/"


# ============================================================
# HTTP CLIENT
# ============================================================

fetch = AsyncClient(
    http2=True,
    verify=True,
    headers={
        "Accept": "application/json,image/png,image/webp,*/*",
        "Content-Type": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        ),
    },
    timeout=Timeout(30.0),
)


# ============================================================
# EXCEPTION
# ============================================================

class QuotlyException(Exception):
    pass


# ============================================================
# SAFE TELEGRAM REPLY
# ============================================================

async def safe_reply_text(message: Message, text: str):
    try:
        return await message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
        )

    except Exception:
        try:
            clean_text = (
                text.replace("<blockquote>", "")
                .replace("</blockquote>", "")
                .replace("<code>", "")
                .replace("</code>", "")
                .replace("<b>", "")
                .replace("</b>", "")
                .replace("<br>", "\n")
            )

            return await message.reply_text(
                clean_text,
                parse_mode=None,
            )

        except Exception:
            return None


# ============================================================
# SENDER ID
# ============================================================

async def get_message_sender_id(ctx: Message):

    if ctx.forward_date:

        if ctx.forward_sender_name:
            return 1

        if ctx.forward_from:
            return ctx.forward_from.id

        if ctx.forward_from_chat:
            return ctx.forward_from_chat.id

        return 1

    if ctx.from_user:
        return ctx.from_user.id

    if ctx.sender_chat:
        return ctx.sender_chat.id

    return 1


# ============================================================
# SENDER NAME
# ============================================================

async def get_message_sender_name(ctx: Message):

    if ctx.forward_date:

        if ctx.forward_sender_name:
            return ctx.forward_sender_name

        if ctx.forward_from:

            first_name = (
                ctx.forward_from.first_name
                or ""
            )

            last_name = (
                ctx.forward_from.last_name
                or ""
            )

            return (
                f"{first_name} {last_name}".strip()
            )

        if ctx.forward_from_chat:
            return (
                ctx.forward_from_chat.title
                or ""
            )

        return ""

    if ctx.from_user:

        first_name = (
            ctx.from_user.first_name
            or ""
        )

        last_name = (
            ctx.from_user.last_name
            or ""
        )

        return (
            f"{first_name} {last_name}".strip()
        )

    if ctx.sender_chat:
        return ctx.sender_chat.title or ""

    return ""


# ============================================================
# CUSTOM EMOJI
# ============================================================

async def get_custom_emoji(ctx: Message):

    try:

        if ctx.forward_date:

            if ctx.forward_sender_name:
                return ""

            if not ctx.forward_from:
                return ""

            if ctx.forward_from.emoji_status:
                return (
                    ctx.forward_from
                    .emoji_status
                    .custom_emoji_id
                )

            return ""

        if ctx.from_user:
            if ctx.from_user.emoji_status:
                return (
                    ctx.from_user
                    .emoji_status
                    .custom_emoji_id
                )

    except Exception:
        pass

    return ""


# ============================================================
# USERNAME
# ============================================================

async def get_message_sender_username(
    ctx: Message,
):

    if ctx.forward_date:

        if (
            not ctx.forward_sender_name
            and not ctx.forward_from
            and ctx.forward_from_chat
        ):
            return (
                ctx.forward_from_chat.username
                or ""
            )

        if ctx.forward_sender_name:
            return ""

        if not ctx.forward_from:
            return ""

        return (
            ctx.forward_from.username
            or ""
        )

    if ctx.from_user:
        return (
            ctx.from_user.username
            or ""
        )

    if ctx.sender_chat:
        return (
            ctx.sender_chat.username
            or ""
        )

    return ""


# ============================================================
# PROFILE PHOTO
# ============================================================

async def get_message_sender_photo(
    ctx: Message,
):

    try:

        if ctx.forward_date:

            if (
                not ctx.forward_sender_name
                and not ctx.forward_from
                and ctx.forward_from_chat
                and ctx.forward_from_chat.photo
            ):

                photo = (
                    ctx.forward_from_chat.photo
                )

                return {
                    "small_file_id": (
                        photo.small_file_id
                    ),
                    "small_photo_unique_id": (
                        photo.small_photo_unique_id
                    ),
                    "big_file_id": (
                        photo.big_file_id
                    ),
                    "big_photo_unique_id": (
                        photo.big_photo_unique_id
                    ),
                }

            if ctx.forward_sender_name:
                return ""

            if not ctx.forward_from:
                return ""

            if ctx.forward_from.photo:

                photo = (
                    ctx.forward_from.photo
                )

                return {
                    "small_file_id": (
                        photo.small_file_id
                    ),
                    "small_photo_unique_id": (
                        photo.small_photo_unique_id
                    ),
                    "big_file_id": (
                        photo.big_file_id
                    ),
                    "big_photo_unique_id": (
                        photo.big_photo_unique_id
                    ),
                }

            return ""

        if (
            ctx.from_user
            and ctx.from_user.photo
        ):

            photo = ctx.from_user.photo

            return {
                "small_file_id": (
                    photo.small_file_id
                ),
                "small_photo_unique_id": (
                    photo.small_photo_unique_id
                ),
                "big_file_id": (
                    photo.big_file_id
                ),
                "big_photo_unique_id": (
                    photo.big_photo_unique_id
                ),
            }

        if (
            ctx.sender_chat
            and ctx.sender_chat.photo
        ):

            photo = ctx.sender_chat.photo

            return {
                "small_file_id": (
                    photo.small_file_id
                ),
                "small_photo_unique_id": (
                    photo.small_photo_unique_id
                ),
                "big_file_id": (
                    photo.big_file_id
                ),
                "big_photo_unique_id": (
                    photo.big_photo_unique_id
                ),
            }

    except Exception:
        pass

    return ""


# ============================================================
# TEXT / CAPTION
# ============================================================

async def get_text_or_caption(
    ctx: Message,
):

    if ctx.text:
        return ctx.text

    if ctx.caption:
        return ctx.caption

    return ""


# ============================================================
# ENTITY CONVERTER
# ============================================================

def convert_entities(
    entities,
):

    result = []

    if not entities:
        return result

    for entity in entities:

        try:

            entity_type = entity.type

            if hasattr(entity_type, "name"):
                entity_type = (
                    entity_type.name.lower()
                )
            else:
                entity_type = str(
                    entity_type
                ).lower()

            item = {
                "type": entity_type,
                "offset": entity.offset,
                "length": entity.length,
            }

            # Custom emoji
            if entity_type == "custom_emoji":

                custom_emoji_id = getattr(
                    entity,
                    "custom_emoji_id",
                    None,
                )

                if custom_emoji_id:
                    item[
                        "custom_emoji_id"
                    ] = custom_emoji_id

            # Text link
            if entity_type == "text_link":

                url = getattr(
                    entity,
                    "url",
                    None,
                )

                if url:
                    item["url"] = url

            result.append(item)

        except Exception:
            continue

    return result


# ============================================================
# BUILD QUOTLY MESSAGE
# ============================================================

async def build_quotly_message(
    message: Message,
    is_reply: bool = False,
):

    sender_id = (
        await get_message_sender_id(
            message
        )
    )

    sender_name = (
        await get_message_sender_name(
            message
        )
    )

    sender_username = (
        await get_message_sender_username(
            message
        )
    )

    sender_photo = (
        await get_message_sender_photo(
            message
        )
    )

    text = await get_text_or_caption(
        message
    )

    # --------------------------------------------------------
    # CHAT TYPE
    # --------------------------------------------------------

    chat_type = "private"

    try:

        if message.chat:
            if message.chat.type:
                chat_type = (
                    message.chat.type
                    .name.lower()
                )

    except Exception:
        pass

    # --------------------------------------------------------
    # ENTITIES
    # --------------------------------------------------------

    entities = None

    if message.entities:
        entities = convert_entities(
            message.entities
        )

    elif message.caption_entities:
        entities = convert_entities(
            message.caption_entities
        )

    else:
        entities = []

    # --------------------------------------------------------
    # FROM
    # --------------------------------------------------------

    from_data = {
        "id": sender_id,
        "name": sender_name or "Unknown",
        "username": (
            sender_username or ""
        ),
        "type": chat_type,
        "photo": sender_photo,
    }

    # --------------------------------------------------------
    # FINAL MESSAGE
    # --------------------------------------------------------

    result = {
        "entities": entities,
        "avatar": True,
        "from": from_data,
        "text": text,
        "chatId": sender_id,
        "replyMessage": {},
    }

    # --------------------------------------------------------
    # REPLY
    # --------------------------------------------------------

    if (
        message.reply_to_message
        and is_reply
    ):

        reply = (
            message.reply_to_message
        )

        result["replyMessage"] = {
            "name": (
                await get_message_sender_name(
                    reply
                )
            ),
            "text": (
                await get_text_or_caption(
                    reply
                )
            ),
            "chatId": (
                await get_message_sender_id(
                    reply
                )
            ),
            "entities": convert_entities(
                reply.entities
                or reply.caption_entities
            ),
        }

    return result


# ============================================================
# CREATE PAYLOAD
# ============================================================

async def create_quotly_payload(
    messages,
    is_reply=False,
):

    if not isinstance(
        messages,
        list,
    ):
        messages = [messages]

    quotly_messages = []

    for message in messages:

        if not message:
            continue

        if message.empty:
            continue

        # Skip unsupported media-only messages
        text = await get_text_or_caption(
            message
        )

        if not text:
            continue

        try:

            quotly_message = (
                await build_quotly_message(
                    message,
                    is_reply=is_reply,
                )
            )

            quotly_messages.append(
                quotly_message
            )

        except Exception:
            continue

    if not quotly_messages:
        raise QuotlyException(
            "No valid text messages found."
        )

    return {
        "type": "quote",
        "format": "png",
        "backgroundColor": "#1b1429",
        "width": 512,
        "scale": 2,
        "emojiBrand": "apple",
        "messages": quotly_messages,
    }


# ============================================================
# DECODE QUOTLY RESPONSE
# ============================================================

def decode_image_response(
    response,
):

    # --------------------------------------------------------
    # Direct PNG
    # --------------------------------------------------------

    content_type = (
        response.headers
        .get("content-type", "")
        .lower()
    )

    content = response.content

    if (
        "image/png" in content_type
        or content.startswith(b"\x89PNG")
    ):
        return content

    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    try:
        data = response.json()

    except Exception as e:

        raise QuotlyException(
            "Quotly returned an invalid response."
        ) from e

    if not isinstance(data, dict):

        raise QuotlyException(
            "Invalid Quotly response."
        )

    # --------------------------------------------------------
    # ERROR
    # --------------------------------------------------------

    if data.get("error"):

        error_data = data.get(
            "error"
        )

        if isinstance(
            error_data,
            dict,
        ):

            message = (
                error_data.get(
                    "message"
                )
                or str(error_data)
            )

        else:
            message = str(
                error_data
            )

        raise QuotlyException(
            message
        )

    # --------------------------------------------------------
    # IMAGE
    # --------------------------------------------------------

    image = data.get("image")

    # Some API versions return:
    # result -> image

    if not image:

        result = data.get(
            "result"
        )

        if isinstance(
            result,
            dict,
        ):
            image = result.get(
                "image"
            )

    if not image:

        raise QuotlyException(
            "Quotly response contains no image."
        )

    # --------------------------------------------------------
    # BASE64 IMAGE
    # --------------------------------------------------------

    if isinstance(
        image,
        str,
    ):

        try:

            # Remove data URL prefix
            if "," in image:
                image = image.split(
                    ",",
                    1,
                )[1]

            return base64.b64decode(
                image
            )

        except Exception as e:

            raise QuotlyException(
                "Failed to decode quote image."
            ) from e

    # --------------------------------------------------------
    # BYTES
    # --------------------------------------------------------

    if isinstance(
        image,
        (bytes, bytearray),
    ):
        return bytes(image)

    raise QuotlyException(
        "Unsupported image format."
    )


# ============================================================
# GENERATE QUOTE
# ============================================================

async def pyrogram_to_quotly(
    messages,
    is_reply=False,
):

    payload = await create_quotly_payload(
        messages,
        is_reply=is_reply,
    )

    errors = []

    # ========================================================
    # API #1
    # ========================================================

    try:

        response = await fetch.post(
            QUOTLY_API,
            json=payload,
        )

        if response.status_code == 200:

            return decode_image_response(
                response
            )

        errors.append(
            "quote.yuri.ly/generate: "
            f"HTTP {response.status_code}"
        )

    except QuotlyException as e:

        errors.append(
            f"quote.yuri.ly/generate: {e}"
        )

    except Exception as e:

        errors.append(
            f"quote.yuri.ly/generate: {e}"
        )

    # ========================================================
    # API #2 PNG
    # ========================================================

    try:

        response = await fetch.post(
            QUOTLY_PNG_API,
            json=payload,
        )

        if response.status_code == 200:

            return decode_image_response(
                response
            )

        errors.append(
            "quote.yuri.ly/generate.png: "
            f"HTTP {response.status_code}"
        )

    except QuotlyException as e:

        errors.append(
            f"quote.yuri.ly/generate.png: {e}"
        )

    except Exception as e:

        errors.append(
            f"quote.yuri.ly/generate.png: {e}"
        )

    # ========================================================
    # API #3 FALLBACK VERCEL
    # ========================================================

    try:

        fallback_payload = {
            "json": payload
        }

        response = await fetch.post(
            FALLBACK_API,
            json=fallback_payload,
        )

        if response.status_code == 200:

            data = response.json()

            # ----------------------------------------------
            # Common response structures
            # ----------------------------------------------

            if isinstance(
                data,
                dict,
            ):

                # data.image
                image = data.get(
                    "image"
                )

                # data.data.image
                if not image:

                    nested = data.get(
                        "data"
                    )

                    if isinstance(
                        nested,
                        dict,
                    ):
                        image = nested.get(
                            "image"
                        )

                # data.result.image
                if not image:

                    result = data.get(
                        "result"
                    )

                    if isinstance(
                        result,
                        dict,
                    ):
                        image = result.get(
                            "image"
                        )

                # ------------------------------------------
                # Decode
                # ------------------------------------------

                if image:

                    if isinstance(
                        image,
                        str,
                    ):

                        if "," in image:
                            image = (
                                image.split(
                                    ",",
                                    1,
                                )[1]
                            )

                        return base64.b64decode(
                            image
                        )

                    if isinstance(
                        image,
                        (
                            bytes,
                            bytearray,
                        ),
                    ):
                        return bytes(image)

                # ------------------------------------------
                # API error
                # ------------------------------------------

                if data.get("msg"):
                    errors.append(
                        "fallback: "
                        + str(
                            data.get("msg")
                        )
                    )

                elif data.get("error"):
                    errors.append(
                        "fallback: "
                        + str(
                            data.get("error")
                        )
                    )

                else:
                    errors.append(
                        "fallback: image missing"
                    )

            else:

                errors.append(
                    "fallback: invalid response"
                )

        else:

            errors.append(
                "fallback: "
                f"HTTP {response.status_code}"
            )

    except Exception as e:

        errors.append(
            f"fallback: {e}"
        )

    # ========================================================
    # ALL API FAILED
    # ========================================================

    # Don't expose huge HTML / Cloudflare response
    short_errors = []

    for error in errors:

        error = str(error)

        if len(error) > 250:
            error = error[:250] + "..."

        short_errors.append(
            error
        )

    raise QuotlyException(
        "All quote APIs failed.\n\n"
        + "\n".join(
            short_errors
        )
    )


# ============================================================
# INTEGER ARGUMENT
# ============================================================

def isArgInt(txt):

    try:

        return [
            True,
            int(txt),
        ]

    except (
        ValueError,
        TypeError,
    ):

        return [
            False,
            0,
        ]


# ============================================================
# /Q /R COMMAND
# ============================================================

@app.on_message(
    filters.command(
        ["q", "r"]
    )
    & filters.reply
)
async def msg_quotly_cmd(
    client,
    ctx: Message,
):

    # --------------------------------------------------------
    # WAIT MESSAGE
    # --------------------------------------------------------

    ww = await safe_reply_text(
        ctx,
        "<blockquote>"
        "ᴡᴀɪᴛ ᴀ sᴇᴄᴏɴᴅ......"
        "</blockquote>",
    )

    # --------------------------------------------------------
    # /r = reply mode
    # --------------------------------------------------------

    is_reply = False

    try:

        if (
            ctx.command
            and ctx.command[0]
            .lower()
            .endswith("r")
        ):
            is_reply = True

    except Exception:
        pass

    # ========================================================
    # MULTIPLE MESSAGE QUOTE
    # ========================================================

    if (
        ctx.command
        and len(ctx.command) > 1
    ):

        check_arg = isArgInt(
            ctx.command[1]
        )

        if check_arg[0]:

            count = check_arg[1]

            # ------------------------------------------------
            # RANGE
            # ------------------------------------------------

            if count < 2 or count > 10:

                if ww:
                    await ww.delete()

                return await safe_reply_text(
                    ctx,
                    "<blockquote>"
                    "❌ Invalid range.<br>"
                    "Use a number between "
                    "2 and 10."
                    "</blockquote>",
                )

            # ------------------------------------------------
            # GET MESSAGES
            # ------------------------------------------------

            try:

                start_id = (
                    ctx.reply_to_message.id
                )

                messages = (
                    await client.get_messages(
                        chat_id=ctx.chat.id,
                        message_ids=range(
                            start_id,
                            start_id
                            + count,
                        ),
                    )
                )

                valid_messages = []

                for message in messages:

                    if not message:
                        continue

                    if message.empty:
                        continue

                    if not (
                        message.text
                        or message.caption
                    ):
                        continue

                    valid_messages.append(
                        message
                    )

                messages = valid_messages

            except Exception as e:

                if ww:
                    await ww.delete()

                error = escape(
                    str(e)[:500]
                )

                return await safe_reply_text(
                    ctx,
                    "<blockquote>"
                    "❌ Failed to get messages:<br>"
                    f"<code>{error}</code>"
                    "</blockquote>",
                )

            # ------------------------------------------------
            # CHECK
            # ------------------------------------------------

            if not messages:

                if ww:
                    await ww.delete()

                return await safe_reply_text(
                    ctx,
                    "<blockquote>"
                    "❌ No valid text messages "
                    "found."
                    "</blockquote>",
                )

            # ------------------------------------------------
            # GENERATE
            # ------------------------------------------------

            try:

                quote_image = (
                    await pyrogram_to_quotly(
                        messages,
                        is_reply=is_reply,
                    )
                )

                if ww:
                    await ww.delete()

                return await ctx.reply_photo(
                    photo=quote_image,
                    caption=(
                        "<blockquote>"
                        "❖ Quotly"
                        "</blockquote>"
                    ),
                    parse_mode=ParseMode.HTML,
                )

            except Exception as e:

                if ww:
                    await ww.delete()

                error = escape(
                    str(e)[:1000]
                ).replace(
                    "\n",
                    "<br>",
                )

                return await safe_reply_text(
                    ctx,
                    "<blockquote>"
                    "❌ Quotly Error:<br>"
                    f"<code>{error}</code>"
                    "</blockquote>",
                )

    # ========================================================
    # SINGLE MESSAGE
    # ========================================================

    try:

        message = (
            await client.get_messages(
                chat_id=ctx.chat.id,
                message_ids=(
                    ctx.reply_to_message.id
                ),
            )
        )

    except Exception as e:

        if ww:
            await ww.delete()

        error = escape(
            str(e)[:500]
        )

        return await safe_reply_text(
            ctx,
            "<blockquote>"
            "❌ Failed to get message:<br>"
            f"<code>{error}</code>"
            "</blockquote>",
        )

    # --------------------------------------------------------
    # CHECK MESSAGE
    # --------------------------------------------------------

    if (
        not message
        or message.empty
    ):

        if ww:
            await ww.delete()

        return await safe_reply_text(
            ctx,
            "<blockquote>"
            "❌ Message not found."
            "</blockquote>",
        )

    if not (
        message.text
        or message.caption
    ):

        if ww:
            await ww.delete()

        return await safe_reply_text(
            ctx,
            "<blockquote>"
            "❌ This message has no "
            "text to quote."
            "</blockquote>",
        )

    # ========================================================
    # GENERATE
    # ========================================================

    try:

        quote_image = (
            await pyrogram_to_quotly(
                [message],
                is_reply=is_reply,
            )
        )

        if ww:
            await ww.delete()

        return await ctx.reply_photo(
            photo=quote_image,
            caption=(
                "<blockquote>"
                "❖ Quotly"
                "</blockquote>"
            ),
            parse_mode=ParseMode.HTML,
        )

    except Exception as e:

        if ww:
            await ww.delete()

        error = escape(
            str(e)[:1000]
        ).replace(
            "\n",
            "<br>",
        )

        return await safe_reply_text(
            ctx,
            "<blockquote>"
            "❌ Quotly Error:<br>"
            f"<code>{error}</code>"
            "</blockquote>",
        )


# ============================================================
# HELP
# ============================================================

__HELP__ = """
**ǫᴜᴏᴛᴇ ɢᴇɴᴇʀᴀᴛɪᴏɴ ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs**

๏ `/q`
➻ Reply to a text message to generate a quote.

๏ `/q 2`
➻ Generate a quote from multiple messages.

๏ `/q 5`
➻ Generate a quote from 5 messages.

๏ `/r`
➻ Generate a quote with reply context.

๏ `/r 5`
➻ Generate a quote from multiple messages
   with reply context.

**Usage:**
➻ Reply to any text message and use `/q`.
"""

__MODULE__ = "Qᴜᴏᴛᴇ"
