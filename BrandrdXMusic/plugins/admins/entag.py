import asyncio
import logging
import random
from html import escape

from pyrogram import filters, enums
from pyrogram.errors import FloodWait, UserNotParticipant

from BrandrdXMusic import app


LOGGER = logging.getLogger(__name__)

TAG_TASKS = {}
TAG_STOPS = {}

TAG_DELAY = 7
MAX_FLOOD_WAIT = 120


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EMOJI COLLECTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENGLISH TAG MESSAGES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TAGMES = [
    "※ ɪ ʟᴏᴠᴇ ʏᴏᴜ...ᰔᩚ",
    "※ ғᴏʀɢᴇᴛ ᴍᴇ..ᰔᩚ",
    "※ ɪ ᴅᴏɴ'ᴛ ʟᴏᴠᴇ ʏᴏᴜ...ᰔᩚ",
    "※ ᴍᴀᴋᴇ ɪᴛ ʏᴏᴜʀs ᴘɪʏᴀ, ᴍᴀᴋᴇ ɪᴛ ʏᴏᴜʀs...ᰔᩚ",
    "※ ᴊᴏɪɴ ᴍʏ ɢʀᴏᴜᴘ ᴀʟsᴏ...ᰔᩚ",
    "※ ɪ ᴋᴇᴘᴛ ʏᴏᴜʀ ɴᴀᴍᴇ ɪɴ ᴍʏ ʜᴇᴀʀᴛ...ᰔᩚ",
    "※ ᴡʜᴇʀᴇ ᴀʀᴇ ᴀʟʟ ʏᴏᴜʀ ғʀɪᴇɴᴅs...ᰔᩚ",
    "※ ɪɴ ᴡʜᴏsᴇ ᴍᴇᴍᴏʀʏ ᴀʀᴇ ʏᴏᴜ ʟᴏsᴛ ᴍʏ ʟᴏᴠᴇ...ᰔᩚ",
    "※ ᴡʜᴀᴛs ʏᴏᴜʀ ᴘʀᴏғᴇssɪᴏɴ...ᰔᩚ",
    "※ ᴡʜᴇʀᴇ ᴅɪᴅ ʏᴏᴜ ʟɪᴠᴇ...ᰔᩚ",
    "※ ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ, ʙᴀʙʏ...ᰔᩚ",
    "※ ɢᴏᴏᴅ ɴɪɢʜᴛ, ɪᴛ's ᴠᴇʀʏ ʟᴀᴛᴇ...ᰔᩚ",
    "※ ɪ ғᴇᴇʟ ᴠᴇʀʏ sᴀᴅ ᴛᴏᴅᴀʏ...ᰔᩚ",
    "※ ᴛᴀʟᴋ ᴛᴏ ᴍᴇ ᴛᴏᴏ...ᰔᩚ",
    "※ ᴡʜᴀᴛ's ғᴏʀ ᴅɪɴɴᴇʀ ᴛᴏᴅᴀʏ...ᰔᩚ",
    "※ ᴡʜᴀᴛ's ɢᴏɪɴɢ ᴏɴ...ᰔᩚ",
    "※ ᴡʜʏ ᴅᴏɴ'ᴛ ʏᴏᴜ ᴍᴇssᴀɢᴇ...ᰔᩚ",
    "※ ɪ ᴀᴍ ɪɴɴᴏᴄᴇɴᴛ...ᰔᩚ",
    "※ ɪᴛ ᴡᴀs ғᴜɴ ʏᴇsᴛᴇʀᴅᴀʏ, ᴡᴀsɴ'ᴛ ɪᴛ...ᰔᩚ",
    "※ ᴡʜᴇʀᴇ ᴡᴇʀᴇ ʏᴏᴜ ʙᴜsʏ ʏᴇsᴛᴇʀᴅᴀʏ...ᰔᩚ",
    "※ ʏᴏᴜ ʀᴇᴍᴀɪɴ sᴏ ᴄᴀʟᴍ ғʀɪᴇɴᴅ...ᰔᩚ",
    "※ ᴅᴏ ʏᴏᴜ ᴋɴᴏᴡ ʜᴏᴡ ᴛᴏ sɪɴɢ, sɪɴɢ...ᰔᩚ",
    "※ ᴡɪʟʟ ʏᴏᴜ ᴄᴏᴍᴇ ғᴏʀ ᴀ ᴡᴀʟᴋ ᴡɪᴛʜ ᴍᴇ...ᰔᩚ",
    "※ ᴀʟᴡᴀʏs ʙᴇ ʜᴀᴘᴘʏ ғʀɪᴇɴᴅ...ᰔᩚ",
    "※ ᴄᴀɴ ᴡᴇ ʙᴇ ғʀɪᴇɴᴅs...ᰔᩚ",
    "※ ᴀʀᴇ ʏᴏᴜ ᴍᴀʀʀɪᴇᴅ...ᰔᩚ",
    "※ ᴡʜᴇʀᴇ ʜᴀᴠᴇ ʏᴏᴜ ʙᴇᴇɴ ʙᴜsʏ ғᴏʀ sᴏ ᴍᴀɴʏ ᴅᴀʏs...ᰔᩚ",
    "※ ʟɪɴᴋ ɪs ɪɴ ʙɪᴏ, ᴛᴏ ᴊᴏɪɴ ɴᴏᴡ...ᰔᩚ",
    "※ ʜᴀᴅ ғᴜɴ...ᰔᩚ",
    "※ ᴅᴏ ʏᴏᴜ ᴋɴᴏᴡ ᴛʜᴇ ᴏᴡɴᴇʀ ᴏғ ᴛʜɪs ɢʀᴏᴜᴘ...ᰔᩚ",
    "※ ᴅᴏ ʏᴏᴜ ᴇᴠᴇʀ ʀᴇᴍᴇᴍʙᴇʀ ᴍᴇ...ᰔᩚ",
    "※ ʟᴇᴛ's ᴘᴀʀᴛʏ...ᰔᩚ",
    "※ ʜᴏᴡ ᴄᴏᴍᴇ ᴛᴏᴅᴀʏ...ᰔᩚ",
    "※ ʟɪsᴛᴇɴ ᴍᴇ...ᰔᩚ",
    "※ ʜᴏᴡ ᴡᴀs ʏᴏᴜʀ ᴅᴀʏ...ᰔᩚ",
    "※ ᴅɪᴅ ʏᴏᴜ sᴇᴇ...ᰔᩚ",
    "※ ᴀʀᴇ ʏᴏᴜ ᴛʜᴇ ᴀᴅᴍɪɴ ʜᴇʀᴇ...ᰔᩚ",
    "※ ᴀʀᴇ ʏᴏᴜ ɪɴ ʀᴇʟᴀᴛɪᴏɴsʜɪᴘ...ᰔᩚ",
    "※ ᴀɴᴅ ʜᴏᴡ ɪs ᴛʜᴇ ᴘʀɪsᴏɴᴇʀ...ᰔᩚ",
    "※ sᴀᴡ ʏᴏᴜ ʏᴇsᴛᴇʀᴅᴀʏ...ᰔᩚ",
    "※ ᴡʜᴇʀᴇ ᴀʀᴇ ʏᴏᴜ ғʀᴏᴍ...ᰔᩚ",
    "※ ᴀʀᴇ ʏᴏᴜ ᴏɴʟɪɴᴇ...ᰔᩚ",
    "※ ᴡʜᴀᴛ ᴅᴏ ʏᴏᴜ ʟɪᴋᴇ ᴛᴏ ᴇᴀᴛ...ᰔᩚ",
    "※ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ, ɪ ᴡɪʟʟ ᴘʟᴀʏ ᴍᴜsɪᴄ ᴀɴᴅ ᴛᴀɢ ᴇᴠᴇʀʏᴏɴᴇ...ᰔᩚ",
    "※ ᴡɪʟʟ ʏᴏᴜ ᴘʟᴀʏ ᴛʀᴜᴛʜ ᴀɴᴅ ᴅᴀʀᴇ...ᰔᩚ",
    "※ ᴡʜᴀᴛs ʜᴀᴘᴘᴇɴᴇᴅ ᴛᴏ ʏᴏᴜ...ᰔᩚ",
    "※ ᴅᴏ ʏᴏᴜ ᴡᴀɴɴᴀ ᴇᴀᴛ ᴄʜᴏᴄᴏʟᴀᴛᴇ...ᰔᩚ",
    "※ ʜᴇʟʟᴏ ʙᴀʙʏ...ᰔᩚ",
    "※ ᴅᴏ ᴄʜᴀᴛᴛɪɴɢ ᴡɪᴛʜ ᴍᴇ...ᰔᩚ",
    "※ ᴡʜᴀᴛ ᴅᴏ ʏᴏᴜ sᴀʏ...ᰔᩚ",
    "※ ɢɪᴠᴇ ᴍᴇ ʏᴏᴜʀ ᴡʜᴀᴛsᴀᴘᴘ ɴᴜᴍʙᴇʀ ᴘʟᴇᴀsᴇ...ᰔᩚ",
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BENGALI TAG MESSAGES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VC_TAG = [
    "⚘ আমাকে ভুলে যাও...💥",
    "⚘ আমি তোমাকে ভালোবাসি না...💥",
    "⚘ এটাকে তোমার করো পিয়া, তোমার করো...💥",
    "⚘ আমার গ্রুপেও যোগ দিন...💥",
    "⚘ আমি হৃদয়ে তোমার নাম রেখেছি...💥",
    "⚘ তোমার সব বন্ধু কোথায়...💥",
    "⚘ কার স্মৃতিতে তুমি হারিয়ে গেছো আমার ভালোবাসা...💥",
    "⚘ তোমার পেশা কি...💥",
    "⚘ তুমি কোথায় থাকো...💥",
    "⚘ শুভ সকাল, বাবু...💥",
    "⚘ শুভ রাত্রি, অনেক দেরি হয়ে গেছে...💥",
    "⚘ আমার আজ খুব খারাপ লাগছে...💥",
    "⚘ আমার সাথেও কথা বল...💥",
    "⚘ আজ রাতের খাবারের জন্য কি...💥",
    "⚘ কি হচ্ছে...💥",
    "⚘ তুমি মেসেজ দাও না কেন...💥",
    "⚘ আমি নির্দোষ...💥",
    "⚘ এটা গতকাল মজা ছিল, তাই না...💥",
    "⚘ তুমি গতকাল কোথায় ব্যস্ত ছিলে...💥",
    "⚘ তুমি কি সম্পর্কে আছো...💥",
    "⚘ তুমি খুব শান্ত থাকো বন্ধু...💥",
    "⚘ তুমি কি গাইতে জানো, গাইতে...💥",
    "⚘ তুমি কি আমার সাথে বেড়াতে আসবে...💥",
    "⚘ সবসময় হাসিখুশি থেকো বন্ধু...💥",
    "⚘ আমরা কি বন্ধু হতে পারি...💥",
    "⚘ তুমি কি বিবাহিত...💥",
    "⚘ এত দিন কোথায় ব্যস্ত ছিলে...💥",
    "⚘ লিঙ্ক বায়োতে আছে, এখন যোগ দিতে...💥",
    "⚘ মজা করলাম...💥",
    "⚘ আপনি কি এই গ্রুপের মালিককে চেনেন...💥",
    "⚘ তোমার কি কখনো মনে পড়ে আমায়...💥",
    "⚘ চলো পার্টি করি...💥",
    "⚘ আজ কেমন এলো...💥",
    "⚘ কেমন কাটলো তোমার দিন...💥",
    "⚘ তুমি কি দেখেছো...💥",
    "⚘ আপনি কি এখানকার প্রশাসক...💥",
    "⚘ আমরা বন্ধু হতে পারি...💥",
    "⚘ তুমি কি সম্পর্কে আছো...💥",
    "⚘ আর বন্দী কেমন আছে...💥",
    "⚘ তোমাকে গতকাল দেখেছি...💥",
    "⚘ তুমি কোথা থেকে...💥",
    "⚘ আপনি কি অনলাইনে আছেন...💥",
    "⚘ তুমি কি আমার বন্ধু....💥",
    "⚘ তুমি কি খেতে পছন্দ কর...💥",
    "⚘ আমাকে আপনার গ্রুপে অ্যাড করুন, আমি গান বাজিয়ে সবাইকে ট্যাগ করব....💥",
    "⚘ আজ আমি দুঃখিত...💥",
    "⚘ তুমি কি সত্য খেলবে এবং সাহস করবে...💥",
    "⚘ তোমার মত বন্ধু থাকলে চিন্তার কি আছে...💥",
    "⚘ কি হয়েছে তোমার...💥",
    "⚘ তুমি কি চকলেট খেতে চাও....💥",
    "⚘ হ্যালো বাবু...💥",
    "⚘ আমার সাথে চ্যাট করো...💥",
    "⚘ তুমি কি বলো...💥",
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_user_mention(user):
    """
    Username available:
        @username (clickable)

    Username unavailable:
        First name (clickable)
    """

    username = getattr(user, "username", None)

    if username:
        display_name = f"@{escape(username)}"
    else:
        display_name = escape(user.first_name or "User")

    return (
        f'<a href="tg://user?id={user.id}">'
        f"{display_name}</a>"
    )


async def is_group_admin(client, message):

    if not message.from_user:
        return False

    try:
        member = await client.get_chat_member(
            message.chat.id,
            message.from_user.id,
        )

        return member.status in (
            enums.ChatMemberStatus.OWNER,
            enums.ChatMemberStatus.ADMINISTRATOR,
        )

    except UserNotParticipant:
        return False

    except Exception:
        LOGGER.exception(
            "[EN/BN TAG] Admin verification failed"
        )
        return False


async def wait_or_stop(stop_event, seconds):

    try:
        await asyncio.wait_for(
            stop_event.wait(),
            timeout=seconds,
        )

        return True

    except asyncio.TimeoutError:
        return False


async def send_tag_message(
    client,
    chat_id,
    content,
    stop_event,
    reply_to_message_id=None,
):

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

            LOGGER.warning(
                "[EN/BN TAG] FloodWait chat=%s wait=%ss",
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

            LOGGER.exception(
                "[EN/BN TAG] Failed sending message chat=%s",
                chat_id,
            )

            return False

    return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN UNIQUE TAGGING PROCESS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def run_tagging(
    client,
    message,
    mode,
    replied,
    stop_event,
):

    chat_id = message.chat.id

    seen_users = set()

    total_retrieved = 0
    total_tagged = 0

    completed = False

    try:

        # IMPORTANT:
        # Iterate the member list only once.
        # Do not restart this loop repeatedly.

        async for member in client.get_chat_members(chat_id):

            if stop_event.is_set():
                break

            user = getattr(member, "user", None)

            if not user:
                continue

            # Prevent duplicate tagging.
            if user.id in seen_users:
                continue

            seen_users.add(user.id)

            total_retrieved += 1

            # Skip bots and deleted accounts.
            if user.is_bot or user.is_deleted:
                continue

            mention = get_user_mention(user)

            # ━━━━━━━━━━━━━━━━━━━━━━━
            # ENGLISH REPLY MODE
            # ━━━━━━━━━━━━━━━━━━━━━━━

            if mode == "english_reply":

                emoji = random.choice(EMOJI)

                content = (
                    "<b><blockquote>"
                    f"{mention}\n\n"
                    f"{escape(emoji)}"
                    "</blockquote></b>"
                )

                reply_id = replied.id

            # ━━━━━━━━━━━━━━━━━━━━━━━
            # BENGALI MODE
            # ━━━━━━━━━━━━━━━━━━━━━━━

            elif mode == "bengali":

                phrase = random.choice(VC_TAG)

                content = (
                    "<b><blockquote>"
                    f"🌸 {mention}\n\n"
                    f"{escape(phrase)}"
                    "</blockquote></b>"
                )

                reply_id = None

            # ━━━━━━━━━━━━━━━━━━━━━━━
            # ENGLISH MODE
            # ━━━━━━━━━━━━━━━━━━━━━━━

            else:

                phrase = random.choice(TAGMES)

                content = (
                    "<b><blockquote>"
                    f"💗 {mention}\n\n"
                    f"{escape(phrase)}"
                    "</blockquote></b>"
                )

                reply_id = None

            sent = await send_tag_message(
                client=client,
                chat_id=chat_id,
                content=content,
                stop_event=stop_event,
                reply_to_message_id=reply_id,
            )

            if not sent:
                break

            total_tagged += 1

            LOGGER.info(
                "[EN/BN TAG] chat=%s mode=%s "
                "user_id=%s tagged=%s",
                chat_id,
                mode,
                user.id,
                total_tagged,
            )

            # Interruptible delay.
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

        LOGGER.warning(
            "[EN/BN TAG] Member retrieval FloodWait "
            "chat=%s wait=%ss",
            chat_id,
            error.value,
        )

    except Exception:

        LOGGER.exception(
            "[EN/BN TAG] Member retrieval failed chat=%s",
            chat_id,
        )

    finally:

        current_task = asyncio.current_task()

        # Only clean up our own task.
        if TAG_TASKS.get(chat_id) is current_task:
            TAG_TASKS.pop(chat_id, None)
            TAG_STOPS.pop(chat_id, None)

        LOGGER.warning(
            "[EN/BN TAG] Finished chat=%s mode=%s "
            "retrieved=%s tagged=%s completed=%s",
            chat_id,
            mode,
            total_retrieved,
            total_tagged,
            completed,
        )

        if completed:
            status = "✅ ᴛᴀɢɢɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!"
        else:
            status = "🛑 ᴛᴀɢɢɪɴɢ sᴛᴏᴘᴘᴇᴅ!"

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

            LOGGER.exception(
                "[EN/BN TAG] Completion notification failed"
            )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# START PROCESS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def start_tagging(
    client,
    message,
    mode,
    replied=None,
):

    chat_id = message.chat.id

    existing_task = TAG_TASKS.get(chat_id)

    if existing_task and not existing_task.done():

        return await message.reply_text(
            "<b><blockquote>"
            "⚠️ ᴀ ᴛᴀɢɢɪɴɢ ᴘʀᴏᴄᴇss "
            "ɪs ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ!\n\n"
            "🛑 <code>/enstop</code> "
            "ᴏʀ <code>/bnstop</code>"
            "</blockquote></b>",
        )

    stop_event = asyncio.Event()

    TAG_STOPS[chat_id] = stop_event

    task = asyncio.create_task(
        run_tagging(
            client=client,
            message=message,
            mode=mode,
            replied=replied,
            stop_event=stop_event,
        )
    )

    TAG_TASKS[chat_id] = task

    mode_name = {
        "english": "🇬🇧 ᴇɴɢʟɪsʜ",
        "english_reply": "💗 ᴇᴍᴏᴊɪ ʀᴇᴘʟʏ",
        "bengali": "🇧🇩 ʙᴇɴɢᴀʟɪ",
    }.get(mode, "ᴛᴀɢɢɪɴɢ")

    try:

        await message.reply_text(
            "<b><blockquote>"
            "🚀 𝐁𝐑𝐀𝐍𝐃𝐄𝐃 𝐓𝐀𝐆𝐆𝐈𝐍𝐆\n\n"
            f"💬 ᴍᴏᴅᴇ: {mode_name}\n"
            "👥 ᴇᴀᴄʜ ᴜɴɪǫᴜᴇ ᴍᴇᴍʙᴇʀ ᴏɴᴄᴇ\n"
            f"⏳ ᴅᴇʟᴀʏ: {TAG_DELAY} sᴇᴄᴏɴᴅs\n\n"
            "🛑 <code>/enstop</code> "
            "ᴏʀ <code>/bnstop</code>"
            "</blockquote></b>",
        )

    except Exception:

        LOGGER.exception(
            "[EN/BN TAG] Start notification failed"
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENGLISH TAG COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(
    filters.command(
        ["entag", "englishtag"],
        prefixes=["/", "@", "#"],
    )
)
async def english_tag(client, message):

    if message.chat.type == enums.ChatType.PRIVATE:

        return await message.reply_text(
            "<b><blockquote>"
            "🚫 ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ғᴏʀ ɢʀᴏᴜᴘs."
            "</blockquote></b>",
        )

    if not await is_group_admin(client, message):

        return await message.reply_text(
            "<b><blockquote>"
            "🚫 ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ʙᴀʙʏ.\n\n"
            "👑 ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴛᴀɢ ᴍᴇᴍʙᴇʀs."
            "</blockquote></b>",
        )

    parts = (message.text or "").split(None, 1)

    # Commands do not require additional text.
    # They use random English messages from TAGMES.

    if len(parts) > 1:

        return await message.reply_text(
            "<b><blockquote>"
            "⚠️ ᴄᴏʀʀᴇᴄᴛ ᴜsᴀɢᴇ:\n\n"
            "➻ <code>/entag</code>\n"
            "➻ <code>/englishtag</code>\n\n"
            "💬 ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴍᴇssᴀɢᴇ "
            "ᴡɪᴛʜ <code>/entag</code>"
            "</blockquote></b>",
        )

    replied = message.reply_to_message

    if replied:
        mode = "english_reply"
    else:
        mode = "english"

    await start_tagging(
        client=client,
        message=message,
        mode=mode,
        replied=replied,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BENGALI TAG COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(
    filters.command(
        ["bntag"],
        prefixes=["/", "@", "#"],
    )
)
async def bengali_tag(client, message):

    if message.chat.type == enums.ChatType.PRIVATE:

        return await message.reply_text(
            "<b><blockquote>"
            "🚫 ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ғᴏʀ ɢʀᴏᴜᴘs."
            "</blockquote></b>",
        )

    if not await is_group_admin(client, message):

        return await message.reply_text(
            "<b><blockquote>"
            "🚫 ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ʙᴀʙʏ.\n\n"
            "👑 ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴛᴀɢ ᴍᴇᴍʙᴇʀs."
            "</blockquote></b>",
        )

    await start_tagging(
        client=client,
        message=message,
        mode="bengali",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STOP TAGGING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(
    filters.command(
        ["cancel", "enstop", "bnstop"],
        prefixes=["/", "@", "#"],
    )
)
async def cancel_spam(client, message):

    if message.chat.type == enums.ChatType.PRIVATE:
        return

    chat_id = message.chat.id

    if not await is_group_admin(client, message):

        return await message.reply_text(
            "<b><blockquote>"
            "🚫 ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ "
            "sᴛᴏᴘ ᴛʜᴇ ᴛᴀɢɢɪɴɢ ᴘʀᴏᴄᴇss."
            "</blockquote></b>",
        )

    task = TAG_TASKS.get(chat_id)

    stop_event = TAG_STOPS.get(chat_id)

    if not task or task.done() or not stop_event:

        return await message.reply_text(
            "<b><blockquote>"
            "ℹ️ ᴄᴜʀʀᴇɴᴛʟʏ ɪ'ᴍ "
            "ɴᴏᴛ ᴛᴀɢɢɪɴɢ ʙᴀʙʏ."
            "</blockquote></b>",
        )

    # Request a graceful stop.
    stop_event.set()

    return await message.reply_text(
        "<b><blockquote>"
        "🛑 𝐁𝐑𝐀𝐍𝐃𝐄𝐃 𝐓𝐀𝐆𝐆𝐈𝐍𝐆\n\n"
        "✨ ᴍᴇɴᴛɪᴏɴ ᴘʀᴏᴄᴇss "
        "sᴛᴏᴘ ʀᴇǫᴜᴇsᴛᴇᴅ.\n\n"
        "⏳ ᴘʀᴏᴄᴇss ɪs sᴛᴏᴘᴘɪɴɢ..."
        "</blockquote></b>",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MEMBER RETRIEVAL DIAGNOSTIC
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(
    filters.command(
        ["entagcheck"],
        prefixes=["/", "@", "#"],
    )
)
async def english_tag_check(client, message):

    if message.chat.type == enums.ChatType.PRIVATE:
        return

    if not await is_group_admin(client, message):
        return

    chat_id = message.chat.id

    status = await message.reply_text(
        "<b><blockquote>"
        "🔍 ᴄʜᴇᴄᴋɪɴɢ ᴍᴇᴍʙᴇʀ ʀᴇᴛʀɪᴇᴠᴀʟ..."
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

        LOGGER.exception(
            "[EN/BN TAG CHECK] Failed chat=%s",
            chat_id,
        )

    try:
        reported = await client.get_chat_members_count(chat_id)

    except Exception:
        reported = "Unavailable"

    LOGGER.warning(
        "[EN/BN TAG CHECK] chat=%s "
        "group_count=%s retrieved=%s",
        chat_id,
        reported,
        total,
    )

    result = (
        "<b><blockquote>"
        "🔍 𝐁𝐑𝐀𝐍𝐃𝐄𝐃 𝐓𝐀𝐆 𝐂𝐇𝐄𝐂𝐊\n\n"
        f"👥 ɢʀᴏᴜᴘ ᴍᴇᴍʙᴇʀs: "
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
            "⚠️ ᴛᴇʟᴇɢʀᴀᴍ ᴅɪᴅ ɴᴏᴛ "
            "ʀᴇᴛᴜʀɴ ᴛʜᴇ ғᴜʟʟ ᴍᴇᴍʙᴇʀ ʟɪsᴛ."
        )

    else:

        result += (
            "✅ ᴍᴇᴍʙᴇʀ ʀᴇᴛʀɪᴇᴠᴀʟ "
            "ᴄʜᴇᴄᴋ ғɪɴɪsʜᴇᴅ."
        )

    result += "</blockquote></b>"

    await status.edit_text(
        result,
    )
