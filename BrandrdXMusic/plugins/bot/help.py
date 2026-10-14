from html import escape
from typing import Union

from pyrogram import enums, filters, types
from pyrogram.errors import MessageNotModified
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from BrandrdXMusic import app
from BrandrdXMusic.utils import help_pannel
from BrandrdXMusic.utils.database import get_lang
from BrandrdXMusic.utils.decorators.language import (
    LanguageStart,
    languageCB,
)
from BrandrdXMusic.utils.inline.help import (
    help_back_markup,
    private_help_panel,
)
from BrandrdXMusic.utils.stuffs.buttons import BUTTONS
from BrandrdXMusic.utils.stuffs.helper import Helper

from config import BANNED_USERS, SUPPORT_CHAT
from strings import get_string, helpers

PRIVATE_HELP_VIDEO = (
    "https://graph.org/file/84d30d4fd04570c0e0256.mp4"
)

GROUP_HELP_VIDEO = (
    "https://te.legra.ph/file/51293513e6af319726fe7.mp4"
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HTML BLOCKQUOTE HELPER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def help_blockquote(text):
    """
    Safely format plain help text inside HTML blockquote.

    Existing Markdown markers are displayed as plain text.
    Telegram HTML entities are escaped.
    """

    content = escape(str(text or ""))

    return (
        "<b><blockquote>"
        f"{content}"
        "</blockquote></b>"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SAFE MESSAGE EDIT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def edit_help_message(
    callback: types.CallbackQuery,
    text: str,
    reply_markup=None,
):
    """
    Video/photo messages need edit_message_caption().
    Normal text messages need edit_message_text().
    """

    message = callback.message

    formatted_text = help_blockquote(text)

    try:

        if message.video or message.photo or message.animation:

            await callback.edit_message_caption(
                caption=formatted_text,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML,
            )

        else:

            await callback.edit_message_text(
                text=formatted_text,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True,
            )

    except MessageNotModified:
        pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PRIVATE HELP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(
    filters.command(["help"])
    & filters.private
    & ~BANNED_USERS
)
@app.on_callback_query(
    filters.regex(r"^settings_back_helper$")
    & ~BANNED_USERS
)
async def helper_private(
    client,
    update: Union[types.Message, types.CallbackQuery],
):

    is_callback = isinstance(
        update,
        types.CallbackQuery,
    )

    if is_callback:

        try:
            await update.answer()
        except Exception:
            pass

        chat_id = update.message.chat.id

        language = await get_lang(chat_id)

        _ = get_string(language)

        keyboard = help_pannel(_, True)

        help_text = _["help_1"].format(SUPPORT_CHAT)

        await edit_help_message(
            callback=update,
            text=help_text,
            reply_markup=keyboard,
        )

        return

    # Private /help command.

    chat_id = update.chat.id

    language = await get_lang(chat_id)

    _ = get_string(language)

    keyboard = help_pannel(_)

    help_text = _["help_1"].format(SUPPORT_CHAT)

    await update.reply_video(
        video=PRIVATE_HELP_VIDEO,
        caption=help_blockquote(help_text),
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GROUP HELP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(
    filters.command(["help"])
    & filters.group
    & ~BANNED_USERS
)
@LanguageStart
async def help_com_group(
    client,
    message: Message,
    _,
):

    keyboard = private_help_panel(_)

    await message.reply_video(
        video=GROUP_HELP_VIDEO,
        caption=help_blockquote(_["help_2"]),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=enums.ParseMode.HTML,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELP PAGE CALLBACKS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HELP_PAGES = {
    "hb1": helpers.HELP_1,
    "hb2": helpers.HELP_2,
    "hb3": helpers.HELP_3,
    "hb4": helpers.HELP_4,
    "hb5": helpers.HELP_5,
    "hb6": helpers.HELP_6,
    "hb7": helpers.HELP_7,
    "hb8": helpers.HELP_8,
    "hb9": helpers.HELP_9,
    "hb10": helpers.HELP_10,
    "hb11": helpers.HELP_11,
    "hb12": helpers.HELP_12,
    "hb13": helpers.HELP_13,
    "hb14": helpers.HELP_14,
    "hb15": helpers.HELP_15,
}


@app.on_callback_query(
    filters.regex(r"^help_callback(?:\s|$)")
    & ~BANNED_USERS
)
@languageCB
async def helper_cb(
    client,
    callback: types.CallbackQuery,
    _,
):

    try:
        await callback.answer()
    except Exception:
        pass

    callback_data = (callback.data or "").strip()

    parts = callback_data.split(maxsplit=1)

    if len(parts) < 2:
        return

    page = parts[1].strip()

    help_text = HELP_PAGES.get(page)

    if help_text is None:
        return

    keyboard = help_back_markup(_)

    await edit_help_message(
        callback=callback,
        text=help_text,
        reply_markup=keyboard,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MANAGEMENT BOT HELP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_callback_query(
    filters.regex(r"^mbot_cb$")
    & ~BANNED_USERS
)
async def management_bot_help(
    client,
    callback: types.CallbackQuery,
):

    try:
        await callback.answer()
    except Exception:
        pass

    keyboard = InlineKeyboardMarkup(
        BUTTONS.MBUTTON
    )

    await edit_help_message(
        callback=callback,
        text=Helper.HELP_M,
        reply_markup=keyboard,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MANAGEMENT BOT BACK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_callback_query(
    filters.regex(r"^managebot123(?:\s|$)")
    & ~BANNED_USERS
)
async def on_back_button(
    client,
    callback: types.CallbackQuery,
):

    try:
        await callback.answer()
    except Exception:
        pass

    chat_id = callback.message.chat.id

    language = await get_lang(chat_id)

    _ = get_string(language)

    keyboard = help_pannel(_, True)

    help_text = _["help_1"].format(SUPPORT_CHAT)

    await edit_help_message(
        callback=callback,
        text=help_text,
        reply_markup=keyboard,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MANAGEMENT BOT EXTRA PAGES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_callback_query(
    filters.regex(r"^mplus(?:\s|$)")
    & ~BANNED_USERS
)
async def mb_plugin_button(
    client,
    callback: types.CallbackQuery,
):

    try:
        await callback.answer()
    except Exception:
        pass

    callback_data = (callback.data or "").strip()

    parts = callback_data.split(maxsplit=1)

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "ʙᴀᴄᴋ",
                    callback_data="mbot_cb",
                )
            ]
        ]
    )

    if len(parts) < 2:

        return await edit_help_message(
            callback=callback,
            text="Invalid help page.",
            reply_markup=keyboard,
        )

    page = parts[1].strip()

    if page == "Okieeeeee":

        return await edit_help_message(
            callback=callback,
            text="Something went wrong.",
            reply_markup=keyboard,
        )

    # Only allow public helper constants.
    # Avoid accepting arbitrary/private attribute names.

    if (
        not page.isidentifier()
        or page.startswith("_")
        or not page.isupper()
    ):

        return await edit_help_message(
            callback=callback,
            text="Invalid help page.",
            reply_markup=keyboard,
        )

    help_text = getattr(
        Helper,
        page,
        None,
    )

    if not isinstance(help_text, str):

        return await edit_help_message(
            callback=callback,
            text="This help page is unavailable.",
            reply_markup=keyboard,
        )

    await edit_help_message(
        callback=callback,
        text=help_text,
        reply_markup=keyboard,
    )
