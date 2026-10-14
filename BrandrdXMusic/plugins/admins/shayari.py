import asyncio
import random
from html import escape

from pyrogram import enums, filters
from pyrogram.errors import FloodWait, UserNotParticipant

from BrandrdXMusic import app

SHAYARI_TASKS = {}
SHAYARI_STOPS = {}

TAG_DELAY = 7
MAX_FLOOD_WAIT = 120


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


SHAYRI = [
    (
        "🌺 बहुत अच्छा लगता है तुझे सताना और फिर प्यार से तुझे मनाना। 🌺\n\n"
        "🥀 Bahut aacha lagta hai tujhe satana Aur fir pyar se tujhe manana. 🥀"
    ),
    (
        "🌺 मेरी जिंदगी मेरी जान हो तुम मेरे सुकून का दुसरा नाम हो तुम। 🌺\n\n"
        "🥀 Meri zindagi Meri jaan ho tum Mere sukoon ka Dusra naam ho tum. 🥀"
    ),
    (
        "🌺 तुम मेरी वो खुशी हो जिसके बिना, मेरी सारी खुशी अधूरी लगती है। 🌺\n\n"
        "🥀 Tum Meri Wo Khushi Ho Jiske Bina, Meri Saari Khushi Adhuri Lagti Hai. 🥀"
    ),
    (
        "🌺 काश वो दिन जल्दी आए, जब तू मेरे साथ सात फेरो में बन्ध जाए। 🌺\n\n"
        "🥀 Kash woh din jldi aaye Jb tu mere sath 7 feron me bndh jaye. 🥀"
    ),
    (
        "🌺 अपना हाथ मेरे दिल पर रख दो और अपना दिल मेरे नाम कर दो। 🌺\n\n"
        "🥀 Apna hath mere dil pr rakh do aur apna dil mere naam kar do. 🥀"
    ),
    (
        "🌺 महादेव ना कोई गाड़ी ना कोई बंगला चाहिए सलामत रहे मेरा प्यार बस यही दुआ चाहिए। 🌺\n\n"
        "🥀 Mahadev na koi gadi na koi bangla chahiye salamat rhe mera pyar bas yahi dua chahiye. 🥀"
    ),
    (
        "🌺 फिक्र तो होगी ना तुम्हारी इकलौती मोहब्बत हो तुम मेरी। 🌺\n\n"
        "🥀 Fikr to hogi na tumhari ikloti mohabbat ho tum meri. 🥀"
    ),
    (
        "🌺 सुनो जानू आप सिर्फ किचन संभाल लेना आप को संभालने के लिए मैं हूं ना। 🌺\n\n"
        "🥀 Suno jaanu aap sirf kitchen sambhal lena ap ko sambhalne ke liye me hun naa. 🥀"
    ),
    (
        "🌺 सौ बात की एक बात मुझे चाहिए बस तेरा साथ। 🌺\n\n"
        "🥀 So bat ki ek bat mujhe chahiye bas tera sath. 🥀"
    ),
    (
        "🌺 बहुत मुश्किलों से पाया हैं तुम्हें, अब खोना नहीं चाहते, कि तुम्हारे थे तुम्हारे हैं अब किसी और के होना नहीं चाहते। 🌺\n\n"
        "🥀 Bahut mushkilon se paya hai tumhe Ab khona nahi chahte. 🥀"
    ),
    (
        "🌺 बेबी बातें तो रोज करते है चलो आज रोमांस करते है। 🌺\n\n"
        "🥀 Baby baten to roj karte hai chalo aaj romance karte hai. 🥀"
    ),
    (
        "🌺 सुबह शाम तुझे याद करते है हम और क्या बताएं की तुमसे कितना प्यार करते है हम। 🌺\n\n"
        "🥀 Subha sham tujhe yad karte hai hum aur kya batayen ki tumse kitna pyar karte hai hum. 🥀"
    ),
    (
        "🌺 किसी से दिल लग जाने को मोहब्बत नहीं कहते जिसके बिना दिल न लगे उसे मोहब्बत कहते हैं। 🌺\n\n"
        "🥀 Kisi se dil lag jane ko mohabbat nahi kehte jiske bina dil na lage use mohabbat kehte hai. 🥀"
    ),
    (
        "🌺 मेरे दिल के लॉक की चाबी हो तुम क्या बताएं जान मेरे जीने की एकलौती वजह हो तुम। 🌺\n\n"
        "🥀 Mere dil ke lock ki chabi ho tum kya batayen jaan mere jeene ki eklauti wajah ho tum. 🥀"
    ),
    (
        "🌺 हम आपकी हर चीज़ से प्यार कर लेंगे, आपकी हर बात पर ऐतबार कर लेंगे, बस एक बार कह दो कि तुम सिर्फ मेरे हो, हम ज़िन्दगी भर आपका इंतज़ार कर लेंगे। 🌺\n\n"
        "🥀 Hum apki har cheez se pyar kar lenge, zindagi bhar apka intzaar kar lenge. 🥀"
    ),
    (
        "🌺 मोहब्बत कभी स्पेशल लोगो से नहीं होती जिससे होती है वही स्पेशल बन जाता है। 🌺\n\n"
        "🥀 Mohabbat kabhi special logo se nahi hoti jisse hoti hai wahi special ban jata hai. 🥀"
    ),
    (
        "🌺 तू मेरी जान है इसमें कोई शक नहीं तेरे अलावा मुझ पर किसी और का हक़ नहीं। 🌺\n\n"
        "🥀 Tu meri jaan hai isme koi shak nahi tere alawa mujh par kisi aur ka hak nahi. 🥀"
    ),
    (
        "🌺 पहली मोहब्बत मेरी हम जान न सके, प्यार क्या होता है हम पहचान न सके, हमने उन्हें दिल में बसा लिया इस कदर कि, जब चाहा उन्हें दिल से निकाल न सके। 🌺\n\n"
        "🥀 Pehli mohabbat meri hum jaan na sake, jab chaha unhe dil se nikal na sake. 🥀"
    ),
    (
        "🌺 खुद नहीं जानती वो कितनी प्यारी हैं, जान है हमारी पर जान से प्यारी हैं, दूरियों के होने से कोई फर्क नहीं पड़ता वो कल भी हमारी थी और आज भी हमारी है। 🌺\n\n"
        "🥀 Khud nahi janti vo kitni pyari hai, duriyon se koi fark nahi padta. 🥀"
    ),
    (
        "🌺 चुपके से आकर इस दिल में उतर जाते हो, सांसों में मेरी खुशबु बनके बिखर जाते हो, कुछ यूँ चला है तेरे इश्क का जादू, सोते-जागते तुम ही तुम नज़र आते हो। 🌺\n\n"
        "🥀 Chupke se aakar iss dil mein utar jate ho, sote-jagte tum hi tum nazar aate ho. 🥀"
    ),
    (
        "🌺 प्यार करना सिखा है नफरतो का कोई ठौर नही, बस तु ही तु है इस दिल मे दूसरा कोई और नही। 🌺\n\n"
        "🥀 Pyar karna sikha hai nafraton ka koi thor nahi, bas tu hi tu hai is dil me. 🥀"
    ),
    (
        "🌺 रब से आपकी खुशीयां मांगते है, दुआओं में आपकी हंसी मांगते है, सोचते है आपसे क्या मांगे, चलो आपसे उम्र भर की मोहब्बत मांगते है। 🌺\n\n"
        "🥀 Rab se apki khushiyan mangte hai, apse umar bhar ki mohabbat mangte hai. 🥀"
    ),
    (
        "🌺 काश मेरे होंठ तेरे होंठों को छू जाए देखूं जहा बस तेरा ही चेहरा नज़र आए हो जाए हमारा रिश्ता कुछ ऐसा होंठों के साथ हमारे दिल भी जुड़ जाए। 🌺\n\n"
        "🥀 Kash mere hoth tere honthon ko chu jayen, hamare dil bhi jud jayen. 🥀"
    ),
    (
        "🌺 आज मुझे ये बताने की इजाज़त दे दो, आज मुझे ये शाम सजाने की इजाज़त दे दो, अपने इश्क़ मे मुझे क़ैद कर लो, आज जान तुम पर लूटाने की इजाज़त दे दो। 🌺\n\n"
        "🥀 Aaj mujhe ye batane ki izazat de do, apne ishq me mujhe kaid kar lo. 🥀"
    ),
    (
        "🌺 जाने लोग मोहब्बत को क्या क्या नाम देते है, हम तो तेरे नाम को ही मोहब्बत कहते है। 🌺\n\n"
        "🥀 Jane log mohabbat ko kya kya naam dete hai, hum to tere naam ko hi mohabbat kehte hai. 🥀"
    ),
    (
        "🌺 देख के हमें वो सिर झुकाते हैं। बुला के महफिल में नजर चुराते हैं। नफरत हैं हमसे तो भी कोई बात नहीं। पर गैरो से मिल के दिल क्यों जलाते हो। 🌺\n\n"
        "🥀 Dekh ke hame wo sir jhukate hai, gairon se mil ke dil kyon jalate ho. 🥀"
    ),
    (
        "🌺 तेरे बिना टूट कर बिखर जायेंगे, तुम मिल गए तो गुलशन की तरह खिल जायेंगे, तुम ना मिले तो जीते जी ही मर जायेंगे, तुम्हें जो पा लिया तो मर कर भी जी जायेंगे। 🌺\n\n"
        "🥀 Tere bina tut kar bikhar jayenge, tum mil gaye to gulshan ki tarah khil jayenge. 🥀"
    ),
    (
        "🌺 सनम तेरी कसम जेसे मै जरूरी हूँ तेरी ख़ुशी के लिये, तू जरूरी है मेरी जिंदगी के लिये। 🌺\n\n"
        "🥀 Sanam teri kasam, tu zaruri hai meri zindagi ke liye. 🥀"
    ),
    (
        "🌺 तुम्हारे गुस्से पर मुझे बड़ा प्यार आया हैं इस बेदर्द दुनिया में कोई तो हैं जिसने मुझे पुरे हक्क से धमकाया हैं। 🌺\n\n"
        "🥀 Tumhare gusse par mujhe bada pyar aaya hai. 🥀"
    ),
    (
        "🌺 पलको से आँखो की हिफाजत होती है धडकन दिल की अमानत होती है ये रिश्ता भी बडा प्यारा होता है कभी चाहत तो कभी शिकायत होती है। 🌺\n\n"
        "🥀 Palkon se aankhon ki hifazat hoti hai, kabhi chahat to kabhi shikayat hoti hai. 🥀"
    ),
    (
        "🌺 मुहब्बत को जब लोग खुदा मानते हैं प्यार करने वाले को क्यों बुरा मानते हैं। जब जमाना ही पत्थर दिल हैं। फिर पत्थर से लोग क्यों दुआ मांगते है। 🌺\n\n"
        "🥀 Mohabbat ko jab log khuda mante hain, pyar karne walon ko kyon bura mante hain. 🥀"
    ),
    (
        "🌺 हुआ जब इश्क़ का एहसास उन्हें आकर वो पास हमारे सारा दिन रोते रहे हम भी निकले खुदगर्ज़ इतने यारो कि ओढ़ कर कफ़न, आँखें बंद करके सोते रहे। 🌺\n\n"
        "🥀 Hua jab ishq ka ehsaas unhe, aankhen band karke sote rahe. 🥀"
    ),
    (
        "🌺 दिल के कोने से एक आवाज़ आती हैं। हमें हर पल उनकी याद आती हैं। दिल पुछता हैं बार-बार हमसे के जितना हम याद करते हैं उन्हें क्या उन्हें भी हमारी याद आती हैं। 🌺\n\n"
        "🥀 Dil ke kone se ek aawaz aati hai, hame har pal unki yaad aati hai. 🥀"
    ),
    (
        "🌺 कभी लफ्ज़ भूल जाऊं कभी बात भूल जाऊं, तूझे इस कदर चाहूँ कि अपनी जात भूल जाऊं, कभी उठ के तेरे पास से जो मैं चल दूँ, जाते हुए खुद को तेरे पास भूल जाऊं। 🌺\n\n"
        "🥀 Kabhi lafz bhool jaaun, kabhi baat bhool jaaun, tujhe is kadar chahun. 🥀"
    ),
    (
        "🌺 आईना देखोगे तो मेरी याद आएगी साथ गुज़री वो मुलाकात याद आएगी पल भर के लिये वक़्त ठहर जाएगा, जब आपको मेरी कोई बात याद आएगी। 🌺\n\n"
        "🥀 Aaina dekhoge to meri yaad aayegi, saath guzri wo mulaqat yaad aayegi. 🥀"
    ),
    (
        "🌺 प्यार किया तो उनकी मोहब्बत नज़र आई दर्द हुआ तो पलके उनकी भर आई दो दिलों की धड़कन में एक बात नज़र आई दिल तो उनका धड़का पर आवाज़ इस दिल की आई। 🌺\n\n"
        "🥀 Pyar kiya to unki mohabbat nazar aayi, dil to unka dhadka par awaaz is dil ki aayi. 🥀"
    ),
    (
        "🌺 कई चेहरे लेकर लोग यहाँ जिया करते हैं हम तो बस एक ही चेहरे से प्यार करते हैं ना छुपाया करो तुम इस चेहरे को, क्योंकि हम इसे देख के ही जिया करते हैं। 🌺\n\n"
        "🥀 Kai chehre lekar log yahan jiya karte hain, hum to bas ek hi chehre se pyar karte hain. 🥀"
    ),
    (
        "🌺 सबके bf को अपनी gf से बात करके नींद आजाती है और मेरे वाले को मुझसे लड़े बिना नींद नहीं आती। 🌺\n\n"
        "🥀 Sabke bf ko apni gf se baat karke neend aa jati hai aur mere wale ko mujhse lade bina neend nahi aati. 🥀"
    ),
    (
        "🌺 सच्चा प्यार कहा किसी के नसीब में होता है। एसा प्यार कहा इस दुनिया में किसी को नसीब होता है। 🌺\n\n"
        "🥀 Sacha pyar kahan kisi ke naseeb mein hota hai. 🥀"
    ),
]


def user_mention(user):
    """
    Username available: @username
    Otherwise: clickable first name.
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


async def is_admin(client, message):
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
        LOG.exception(
            "[SHAYARI] Admin verification failed"
        )
        return False


async def wait_or_stop(stop_event, seconds):
    """
    Wait for delay, but allow /shayarioff to interrupt.
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


async def send_shayari(
    client,
    chat_id,
    content,
    stop_event,
    reply_to_message_id=None,
):
    """
    Send HTML message with Telegram FloodWait handling.
    """

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

            LOG.warning(
                "[SHAYARI] FloodWait chat=%s wait=%ss",
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
            LOG.exception(
                "[SHAYARI] Send failed chat=%s",
                chat_id,
            )
            return False

    return False


async def run_shayari(
    client,
    message,
    reply_message,
    stop_event,
):
    chat_id = message.chat.id

    seen_users = set()
    total_tagged = 0
    total_retrieved = 0
    completed = False

    try:
        async for member in client.get_chat_members(chat_id):

            if stop_event.is_set():
                break

            user = getattr(member, "user", None)

            if user is None:
                continue

            if user.id in seen_users:
                continue

            seen_users.add(user.id)
            total_retrieved += 1

            if user.is_bot or user.is_deleted:
                continue

            mention = user_mention(user)

            if reply_message:
                emoji = random.choice(EMOJI)

                content = (
                    "<b><blockquote>"
                    f"{mention}\n"
                    f"{escape(emoji)}"
                    "</blockquote></b>"
                )

                reply_id = reply_message.id

            else:
                shayari = random.choice(SHAYRI)

                content = (
                    "<b><blockquote>"
                    f"💗 {mention}\n\n"
                    f"{escape(shayari)}"
                    "</blockquote></b>"
                )

                reply_id = None

            sent = await send_shayari(
                client=client,
                chat_id=chat_id,
                content=content,
                stop_event=stop_event,
                reply_to_message_id=reply_id,
            )

            if not sent:
                break

            total_tagged += 1

            LOG.info(
                "[SHAYARI] chat=%s user=%s tagged=%s",
                chat_id,
                user.id,
                total_tagged,
            )

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
        LOG.warning(
            "[SHAYARI] Member retrieval FloodWait "
            "chat=%s wait=%ss",
            chat_id,
            error.value,
        )

    except Exception:
        LOG.exception(
            "[SHAYARI] Member retrieval error chat=%s",
            chat_id,
        )

    finally:
        current_task = asyncio.current_task()

        if SHAYARI_TASKS.get(chat_id) is current_task:
            SHAYARI_TASKS.pop(chat_id, None)
            SHAYARI_STOPS.pop(chat_id, None)

        LOG.warning(
            "[SHAYARI] Finished chat=%s retrieved=%s "
            "tagged=%s completed=%s",
            chat_id,
            total_retrieved,
            total_tagged,
            completed,
        )

        status = (
            "✅ 𝐒𝐇𝐀𝐘𝐀𝐑𝐈 𝐓𝐀𝐆𝐆𝐈𝐍𝐆 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄𝐃"
            if completed
            else "🛑 𝐒𝐇𝐀𝐘𝐀𝐑𝐈 𝐓𝐀𝐆𝐆𝐈𝐍𝐆 𝐒𝐓𝐎𝐏𝐏𝐄𝐃"
        )

        try:
            await message.reply_text(
                "<b><blockquote>"
                f"{status}\n\n"
                f"👥 ᴜɴɪǫᴜᴇ ᴍᴇᴍʙᴇʀs ʀᴇᴛʀɪᴇᴠᴇᴅ: "
                f"<code>{total_retrieved}</code>\n"
                f"💗 ᴍᴇᴍʙᴇʀs ᴛᴀɢɢᴇᴅ: "
                f"<code>{total_tagged}</code>\n"
                "🔁 ᴅᴜᴘʟɪᴄᴀᴛᴇ ᴛᴀɢs: <code>0</code>"
                "</blockquote></b>",
            )

        except Exception:
            LOG.exception(
                "[SHAYARI] Completion message failed"
            )


@app.on_message(
    filters.command(
        ["shayari"],
        prefixes=["/", "@", "#"],
    )
)
async def mentionall(client, message):
    chat_id = message.chat.id

    if message.chat.type == enums.ChatType.PRIVATE:
        return await message.reply_text(
            "<b><blockquote>"
            "🚫 𝐓𝐡𝐢𝐬 𝐂𝐨𝐦𝐦𝐚𝐧𝐝 𝐎𝐧𝐥𝐲 𝐅𝐨𝐫 𝐆𝐫𝐨𝐮𝐩𝐬."
            "</blockquote></b>",
        )

    if not await is_admin(client, message):
        return await message.reply_text(
            "<b><blockquote>"
            "🚫 𝐘𝐨𝐮 𝐀𝐫𝐞 𝐍𝐨𝐭 𝐀𝐧 𝐀𝐝𝐦𝐢𝐧 𝐁𝐚𝐛𝐲 😏\n\n"
            "👑 𝐎𝐧𝐥𝐲 𝐀𝐝𝐦𝐢𝐧𝐬 𝐂𝐚𝐧 𝐔𝐬𝐞 𝐓𝐡𝐢𝐬."
            "</blockquote></b>",
        )

    existing_task = SHAYARI_TASKS.get(chat_id)

    if existing_task and not existing_task.done():
        return await message.reply_text(
            "<b><blockquote>"
            "⏳ 𝐒𝐡𝐚𝐲𝐚𝐫𝐢 𝐓𝐚𝐠𝐠𝐢𝐧𝐠 𝐈𝐬 "
            "𝐀𝐥𝐫𝐞𝐚𝐝𝐲 𝐑𝐮𝐧𝐧𝐢𝐧𝐠.\n\n"
            "🛑 <code>/shayarioff</code>"
            "</blockquote></b>",
        )

    reply_message = message.reply_to_message

    parts = (message.text or "").split(None, 1)

    if len(parts) > 1:
        return await message.reply_text(
            "<b><blockquote>"
            "⚠️ 𝐔𝐬𝐞 𝐓𝐡𝐞 𝐂𝐨𝐦𝐦𝐚𝐧𝐝 𝐋𝐢𝐤𝐞 𝐓𝐡𝐢𝐬:\n\n"
            "➻ <code>/shayari</code>\n"
            "➻ 𝐎𝐫 𝐑𝐞𝐩𝐥𝐲 𝐓𝐨 𝐀𝐧𝐲 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 "
            "𝐖𝐢𝐭𝐡 <code>/shayari</code>"
            "</blockquote></b>",
        )

    stop_event = asyncio.Event()

    SHAYARI_STOPS[chat_id] = stop_event

    task = asyncio.create_task(
        run_shayari(
            client=client,
            message=message,
            reply_message=reply_message,
            stop_event=stop_event,
        )
    )

    SHAYARI_TASKS[chat_id] = task

    mode = (
        "🌸 ᴇᴍᴏᴊɪ ʀᴇᴘʟʏ ᴍᴏᴅᴇ"
        if reply_message
        else "💗 ʀᴀɴᴅᴏᴍ sʜᴀʏᴀʀɪ ᴍᴏᴅᴇ"
    )

    try:
        await message.reply_text(
            "<b><blockquote>"
            "🌷 𝐁𝐑𝐀𝐍𝐃𝐄𝐃 𝐒𝐇𝐀𝐘𝐀𝐑𝐈\n\n"
            "🚀 ᴘʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ!\n"
            f"{mode}\n"
            "👥 ᴇᴀᴄʜ ᴜɴɪǫᴜᴇ ᴍᴇᴍʙᴇʀ ᴏɴᴄᴇ\n"
            "⏳ ᴅᴇʟᴀʏ: 7 sᴇᴄᴏɴᴅs\n\n"
            "🛑 <code>/shayarioff</code>"
            "</blockquote></b>",
        )

    except Exception:
        LOG.exception(
            "[SHAYARI] Start message failed"
        )


@app.on_message(
    filters.command(
        ["cancelshayari", "shayarioff"],
        prefixes=["/", "@", "#"],
    )
)
async def cancel_spam(client, message):
    chat_id = message.chat.id

    if message.chat.type == enums.ChatType.PRIVATE:
        return

    if not await is_admin(client, message):
        return await message.reply_text(
            "<b><blockquote>"
            "🚫 𝐘𝐨𝐮 𝐀𝐫𝐞 𝐍𝐨𝐭 𝐀𝐧 𝐀𝐝𝐦𝐢𝐧 𝐁𝐚𝐛𝐲 😏\n\n"
            "👑 𝐎𝐧𝐥𝐲 𝐀𝐝𝐦𝐢𝐧𝐬 𝐂𝐚𝐧 "
            "𝐒𝐭𝐨𝐩 𝐓𝐡𝐢𝐬 𝐏𝐫𝐨𝐜𝐞𝐬𝐬."
            "</blockquote></b>",
        )

    task = SHAYARI_TASKS.get(chat_id)
    stop_event = SHAYARI_STOPS.get(chat_id)

    if not task or task.done() or not stop_event:
        return await message.reply_text(
            "<b><blockquote>"
            "⚠️ 𝐂𝐮𝐫𝐫𝐞𝐧𝐭𝐥𝐲 𝐈'𝐦 𝐍𝐨𝐭 "
            "𝐑𝐮𝐧𝐧𝐢𝐧𝐠 𝐀𝐧𝐲 𝐒𝐡𝐚𝐲𝐚𝐫𝐢 𝐏𝐫𝐨𝐜𝐞𝐬𝐬."
            "</blockquote></b>",
        )

    stop_event.set()

    return await message.reply_text(
        "<b><blockquote>"
        "🛑 𝐁𝐑𝐀𝐍𝐃𝐄𝐃 𝐒𝐇𝐀𝐘𝐀𝐑𝐈\n\n"
        "💗 𝐒𝐓𝐎𝐏 𝐑𝐄𝐐𝐔𝐄𝐒𝐓𝐄𝐃\n"
        "⏳ ᴘʀᴏᴄᴇss ɪs sᴛᴏᴘᴘɪɴɢ..."
        "</blockquote></b>",
    )
