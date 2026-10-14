import asyncio
import random
from html import escape

from pyrogram import filters, enums
from pyrogram.errors import FloodWait, UserNotParticipant

from BrandrdXMusic import app

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
# HINDI TAG MESSAGES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TAGMES = [
    "❅ बेबी कहा हो। 🤗",
    "❅ ओए सो गए क्या, ऑनलाइन आओ ।😊",
    "❅ ओए वीसी आओ बात करते हैं । 😃",
    "❅ खाना खाया कि नही। 🥲",
    "❅ घर में सब कैसे हैं। 🥺",
    "❅ पता है बहुत याद आ रही आपकी। 🤭",
    "❅ और बताओ कैसे हो।..?? 🤨",
    "❅ मेरी भी सैटिंग करवा दो प्लीज..?? 🙂",
    "❅ आपका नाम क्या है।..?? 🥲",
    "❅ नाश्ता हो गया..?? 😋",
    "❅ मुझे अपने ग्रूप में ऐड कर लो। 😍",
    "❅ आपका दोस्त आपको बुला रहा है। 😅",
    "❅ मुझसे शादी करोगे ..?? 🤔",
    "❅ सोने चले गए क्या 🙄",
    "❅ अरे यार कोई AC चला दो 😕",
    "❅ आप कहा से हो..?? 🙃",
    "❅ हेलो जी नमस्ते 😛",
    "❅ BABY क्या कर रही हो..? 🤔",
    "❅ क्या आप मुझे जानते हो .? ☺️",
    "❅ आओ baby Ludo खेलते है .🤗",
    "❅ चलती है क्या 9 से 12... 😇",
    "❅ आपके पापा क्या करते है 🤭",
    "❅ आओ baby बाजार चलते है गोलगप्पे खाने। 🥺",
    "❅ अकेली ना बाजार जाया करो, नज़र लग जायेगी। 😶",
    "❅ और बताओ BF कैसा है ..?? 🤔",
    "❅ गुड मॉर्निंग 😜",
    "❅ मेरा एक काम करोगे। 🙂",
    "❅ DJ वाले बाबू मेरा गाना चला दो। 😪",
    "❅ आप से मिलकर अच्छा लगा।☺",
    "❅ मेरे बाबू ने थाना थाया।..? 🙊",
    "❅ पढ़ाई कैसी चल रही हैं ? 😺",
    "❅ हम को प्यार हुआ। 🥲",
    "❅ Nykaa कौन है...? 😅",
    "❅ तू खींच मेरी फ़ोटो ..? 😅",
    "❅ Phone काट मम्मी आ गई क्या। 😆",
    "❅ और भाबी से कब मिल वा रहे हो । 😉",
    "❅ क्या आप मुझसे प्यार करते हो 💚",
    "❅ मैं तुम से बहुत प्यार करती हूं..? 👀",
    "❅ बेबी एक kiss दो ना..?? 🙉",
    "❅ एक जॉक सुनाऊं..? 😹",
    "❅ vc पर आओ कुछ दिखाती हूं 😻",
    "❅ क्या तुम instagram चलते हो..?? 🙃",
    "❅ whatsapp नंबर दो ना अपना..? 😕",
    "❅ आप की दोस्त से मेरी सेटिंग करा दो ..? 🙃",
    "❅ सारा काम हो गया हो तो ऑनलाइन आ जाओ।..? 🙃",
    "❅ कहा से हो आप 😊",
    "❅ जा तुझे आज़ाद कर दिया मैंने मेरे दिल से। 🥺",
    "❅ मेरा एक काम करोगे, ग्रूप मे कुछ मेंबर ऐड कर दो ..? ♥️",
    "❅ मैं तुमसे नाराज़ हूं 😠",
    "❅ आपकी फैमिली कैसी है..? ❤",
    "❅ क्या हुआ..? 🤔",
    "❅ बहुत याद आ रही है आपकी 😒",
    "❅ भूल गए मुझे 😏",
    "❅ झूठ क्यों बोला आपने मुझसे 🤐",
    "❅ इतना भाव मत खाया करो, रोटी खाया करो कम से कम मोटी तो हो जाओगी 😒",
    "❅ ये attitude किसे @BRANDED_PAID_CC दिखा रहे हो 😮",
    "❅ हेमलो कहा busy ho 👀",
    "❅ आपके जैसा दोस्त पाकर मे बहुत खुश हूं। 🙈",
    "❅ आज मन बहुत उदास है ☹️",
    "❅ मुझसे भी बात कर लो ना 🥺",
    "❅ आज खाने में क्या बनाया है 👀",
    "❅ क्या चल रहा है 🙂",
    "❅ message क्यों नहीं करती हो..🥺",
    "❅ मैं मासूम हूं ना 🥺",
    "❅ कल मज़ा आया था ना 😅",
    "❅ कल कहा busy थे 😕",
    "❅ आप relationship में हो क्या..? 👀",
    "❅ कितने शांत रहते हो यार आप 😼",
    "❅ आपको गाना, गाना आता है..? 😸",
    "❅ घूमने चलोगे मेरे साथ..?? 🙈",
    "❅ हमेशा हैप्पी रहा करो यार 🤞",
    "❅ क्या हम दोस्त बन सकते है...? 🥰",
    "❅ आप का विवाह हो गया क्या.. 🥺",
    "❅ कहा busy the इतने दिनों से 🥲",
    "❅ single हो या mingle 😉",
    "❅ आओ पार्टी करते है 🥳",
    "❅ Bio में link हैं join कर लो 🧐",
    "❅ मैं तुमसे प्यार नहीं करती, 🥺",
    "❅ यहां आ जाओ ना @BRANDED_WORLD मस्ती करेंगे 🤭",
    "❅ भूल जाओ मुझे,..? 😊",
    "❅ अपना बना ले पिया, अपना बना ले 🥺",
    "❅ मेरा ग्रुप भी join कर लो ना 🤗",
    "❅ मैने तेरा नाम Dil rakh diya 😗",
    "❅ तुमारे सारे दोस्त कहा गए 🥺",
    "❅ my cute owner @BRANDRD_BOT 🥰",
    "❅ किसकी याद मे खोए हो जान 😜",
    "❅ गुड नाईट जी बहुत रात हो गई 🥰",
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LIFE QUOTES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VC_TAG = [
    "❅ ɪғ ʏᴏᴜ ᴅᴏ ɴᴏᴛ sᴛᴇᴘ ғᴏʀᴡᴀʀᴅ ʏᴏᴜ ᴡɪʟʟ ʀᴇᴍᴀɪɴ ɪɴ ᴛʜᴇ sᴀᴍᴇ ᴘʟᴀᴄᴇ.",
    "❅ ʟɪғᴇ ɪs ʜᴀʀᴅ ʙᴜᴛ ɴᴏᴛ ɪᴍᴘᴏssɪʙʟᴇ.",
    "❅ ʟɪғᴇ’s ᴛᴏᴏ sʜᴏʀᴛ ᴛᴏ ᴀʀɢᴜᴇ ᴀɴᴅ ғɪɢʜᴛ.",
    "❅ ᴅᴏɴ’ᴛ ᴡᴀɪᴛ ғᴏʀ ᴛʜᴇ ᴘᴇʀғᴇᴄᴛ ᴍᴏᴍᴇɴᴛ ᴛᴀᴋᴇ ᴍᴏᴍᴇɴᴛ ᴀɴᴅ ᴍᴀᴋᴇ ɪᴛ ᴘᴇʀғᴇᴄᴛ.",
    "❅ sɪʟᴇɴᴄᴇ ɪs ᴛʜᴇ ʙᴇsᴛ ᴀɴsᴡᴇʀ ᴛᴏ sᴏᴍᴇᴏɴᴇ ᴡʜᴏ ᴅᴏᴇsɴ’ᴛ ᴠᴀʟᴜᴇ ʏᴏᴜʀ ᴡᴏʀᴅs.",
    "❅ ᴇᴠᴇʀʏ ɴᴇᴡ ᴅᴀʏ ɪs ᴀ ᴄʜᴀɴᴄᴇ ᴛᴏ ᴄʜᴀɴɢᴇ ʏᴏᴜʀ ʟɪғᴇ.",
    "❅ ᴛᴏ ᴄʜᴀɴɢᴇ ʏᴏᴜʀ ʟɪғᴇ, ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴄʜᴀɴɢᴇ ʏᴏᴜʀ ᴘʀɪᴏʀɪᴛɪᴇs.",
    "❅ ʟɪғᴇ ɪs ᴀ ᴊᴏᴜʀɴᴇʏ, ɴᴏᴛ ᴀ ʀᴀᴄᴇ..",
    "❅ sᴍɪʟᴇ ᴀɴᴅ ᴅᴏɴ’ᴛ ᴡᴏʀʀʏ, ʟɪғᴇ ɪs ᴀᴡᴇsᴏᴍᴇ.",
    "❅ ᴅᴏ ɴᴏᴛ ᴄᴏᴍᴘᴀʀᴇ ʏᴏᴜʀsᴇʟғ ᴛᴏ ᴏᴛʜᴇʀs ɪғ ʏᴏᴜ ᴅᴏ sᴏ ʏᴏᴜ ᴀʀᴇ ɪɴsᴜʟᴛɪɴɢ ʏᴏᴜʀsᴇʟғ.",
    "❅ ɪ ᴀᴍ ɪɴ ᴛʜᴇ ᴘʀᴏᴄᴇss ᴏғ ʙᴇᴄᴏᴍɪɴɢ ᴛʜᴇ ʙᴇsᴛ ᴠᴇʀsɪᴏɴ ᴏғ ᴍʏsᴇʟғ.",
    "❅ ʟɪғᴇ ɪs ʟɪᴋᴇ ɪᴄᴇ ᴇɴᴊᴏʏ ɪᴛ ʙᴇғᴏʀᴇ ɪᴛ ᴍᴇʟᴛs.",
    "❅ ʙᴇ ғʀᴇᴇ ʟɪᴋᴇ ᴀ ʙɪʀᴅ.",
    "❅ ɴᴏ ᴏɴᴇ ɪs ᴄᴏᴍɪɴɢ ᴛᴏ sᴀᴠᴇ ʏᴏᴜ. ᴛʜɪs ʟɪғᴇ ᴏғ ʏᴏᴜʀ ɪs 100% ʏᴏᴜʀ ʀᴇsᴘᴏɴsɪʙɪʟɪᴛʏ..",
    "❅ ʟɪғᴇ ᴀʟᴡᴀʏs ᴏғғᴇʀs ʏᴏᴜ ᴀ sᴇᴄᴏɴᴅ ᴄʜᴀɴᴄᴇ. ɪᴛ’s ᴄᴀʟʟᴇᴅ ᴛᴏᴍᴏʀʀᴏᴡ.",
    "❅ ʟɪғᴇ ʙᴇɢɪɴs ᴀᴛ ᴛʜᴇ ᴇɴᴅ ᴏғ ʏᴏᴜʀ ᴄᴏᴍғᴏʀᴛ ᴢᴏɴᴇ.",
    "❅ ᴀʟʟ ᴛʜᴇ ᴛʜɪɴɢs ᴛʜᴀᴛ ʜᴜʀᴛ ʏᴏᴜ, ᴀᴄᴛᴜᴀʟʟʏ ᴛᴇᴀᴄʜ ʏᴏᴜ.",
    "❅ ʟɪғᴇ ɪs ʟɪᴋᴇ ᴀ ᴄᴀᴍᴇʀᴀ. sᴏ ғᴀᴄᴇ ɪᴛ ᴡɪᴛʜ ᴀ sᴍɪʟᴇ.",
    "❅ ʟɪғᴇ ɪs 10% ᴏғ ᴡʜᴀᴛ ʜᴀᴘᴘᴇɴs ᴛᴏ ʏᴏᴜ ᴀɴᴅ 90% ᴏғ ʜᴏᴡ ʏᴏᴜ ʀᴇsᴘᴏɴᴅ ᴛᴏ ɪᴛ.",
    "❅ ʟɪғᴇ ᴀʟᴡᴀʏs ᴏғғᴇʀs ʏᴏᴜ ᴀ sᴇᴄᴏɴᴅ ᴄʜᴀɴᴄᴇ. ɪᴛ’s ᴄᴀʟʟᴇᴅ ᴛᴏᴍᴏʀʀᴏᴡ.",
    "❅ ɴᴏ ᴏɴᴇ ɪs ᴄᴏᴍɪɴɢ ᴛᴏ sᴀᴠᴇ ʏᴏᴜ. ᴛʜɪs ʟɪғᴇ ᴏғ ʏᴏᴜʀ ɪs 100% ʏᴏᴜʀ ʀᴇsᴘᴏɴsɪʙɪʟɪᴛʏ..",
    "❅ ʟɪғᴇ ɪs ɴᴏᴛ ᴀɴ ᴇᴀsʏ ᴛᴀsᴋ.",
    "❅ ʟɪғᴇ ɪs ᴀ ᴡᴏɴᴅᴇʀғᴜʟ ᴀᴅᴠᴇɴᴛᴜʀᴇ.",
    "❅ ʟɪғᴇ ʙᴇɢɪɴs ᴏɴ ᴛʜᴇ ᴏᴛʜᴇʀ sɪᴅᴇ ᴏғ ᴅᴇsᴘᴀɪʀ.",
    "❅ ʟɪғᴇ ɪs ɴᴏᴛ ᴀ ᴘʀᴏʙʟᴇᴍ ᴛᴏ ʙᴇ sᴏʟᴠᴇᴅ ʙᴜᴛ ᴀ ʀᴇᴀʟɪᴛʏ ᴛᴏ ʙᴇ ᴇxᴘᴇʀɪᴇɴᴄᴇᴅ.",
    "❅ ʟɪғᴇ ᴅᴏᴇs ɴᴏᴛ ʜᴀᴠᴇ ᴀ ʀᴇᴍᴏᴛᴇ; ɢᴇᴛ ᴜᴘ ᴀɴᴅ ᴄʜᴀɴɢᴇ ɪᴛ ʏᴏᴜʀsᴇʟғ.",
    "❅ sᴛᴀʀᴛ ᴛʀᴜsᴛɪɴɢ ʏᴏᴜʀsᴇʟғ, ᴀɴᴅ ʏᴏᴜ’ʟʟ ᴋɴᴏᴡ ʜᴏᴡ ᴛᴏ ʟɪᴠᴇ.",
    "❅ ʜᴇᴀʟᴛʜ ɪs ᴛʜᴇ ᴍᴏsᴛ ɪᴍᴘᴏʀᴛᴀɴᴛ ɢᴏᴏᴅ ᴏғ ʟɪғᴇ.",
    "❅ ᴛɪᴍᴇ ᴄʜᴀɴɢᴇ ᴘʀɪᴏʀɪᴛʏ ᴄʜᴀɴɢᴇs.",
    "❅ ᴛᴏ sᴇᴇ ᴀɴᴅ ᴛᴏ ғᴇᴇʟ ᴍᴇᴀɴs ᴛᴏ ʙᴇ, ᴛʜɪɴᴋ ᴀɴᴅ ʟɪᴠᴇ.",
    "❅ ʙᴇ ᴡɪᴛʜ sᴏᴍᴇᴏɴᴇ ᴡʜᴏ ʙʀɪɴɢs ᴏᴜᴛ ᴛʜᴇ ʙᴇsᴛ ᴏғ ʏᴏᴜ.",
    "❅ ʏᴏᴜʀ ᴛʜᴏᴜɢʜᴛs ᴀʀᴇ ʏᴏᴜʀ ʟɪғᴇ.",
    "❅ ᴘᴇᴏᴘʟᴇ ᴄʜᴀɴɢᴇ, ᴍᴇᴍᴏʀɪᴇs ᴅᴏɴ’ᴛ.",
    "❅ ᴏᴜʀ ʟɪғᴇ ɪs ᴡʜᴀᴛ ᴡᴇ ᴛʜɪɴᴋ ɪᴛ ɪs.",
    "❅ ʟɪɢʜᴛ ʜᴇᴀʀᴛ ʟɪᴠᴇs ʟᴏɴɢᴇʀ.",
    "❅ ᴅᴇᴘʀᴇssɪᴏɴ ᴇᴠᴇɴᴛᴜᴀʟʟʏ ʙᴇᴄᴏᴍᴇs ᴀ ʜᴀʙɪᴛ.",
    "❅ ʟɪғᴇ ɪs ᴀ ɢɪғᴛ. ᴛʀᴇᴀᴛ ɪᴛ ᴡᴇʟʟ.",
    "❅ ʟɪғᴇ ɪs ᴡʜᴀᴛ ᴏᴜʀ ғᴇᴇʟɪɴɢs ᴅᴏ ᴡɪᴛʜ ᴜs.",
    "❅ ᴡʀɪɴᴋʟᴇs ᴀʀᴇ ᴛʜᴇ ʟɪɴᴇs ᴏғ ʟɪғᴇ ᴏɴ ᴛʜᴇ ғᴀᴄᴇ.",
    "❅ ʟɪғᴇ ɪs ᴍᴀᴅᴇ ᴜᴘ ᴏғ sᴏʙs, sɴɪғғʟᴇs, ᴀɴᴅ sᴍɪʟᴇs.",
    "❅ ɴᴏᴛ ʟɪғᴇ, ʙᴜᴛ ɢᴏᴏᴅ ʟɪғᴇ, ɪs ᴛᴏ ʙᴇ ᴄʜɪᴇғʟʏ ᴠᴀʟᴜᴇᴅ.",
    "❅ ʏᴏᴜ ᴄʜᴀɴɢᴇ ʏᴏᴜʀ ʟɪғᴇ ʙʏ ᴄʜᴀɴɢɪɴɢ ʏᴏᴜʀ ʜᴇᴀʀᴛ.",
    "❅ ʟɪғᴇ ɪs ɴᴏᴛʜɪɴɢ ᴡɪᴛʜᴏᴜᴛ ᴛʀᴜᴇ ғʀɪᴇɴᴅsʜɪᴘ.",
    "❅ ɪғ ʏᴏᴜ ᴀʀᴇ ʙʀᴀᴠᴇ ᴛᴏ sᴀʏ ɢᴏᴏᴅ ʙʏᴇ, ʟɪғᴇ ᴡɪʟʟ ʀᴇᴡᴀʀᴅ ʏᴏᴜ ᴡɪᴛʜ ᴀ ɴᴇᴡ ʜᴇʟʟᴏ.",
    "❅ ᴛʜᴇʀᴇ ɪs ɴᴏᴛʜɪɴɢ ᴍᴏʀᴇ ᴇxᴄɪᴛɪɴɢ ɪɴ ᴛʜᴇ ᴡᴏʀʟᴅ, ʙᴜᴛ ᴘᴇᴏᴘʟᴇ.",
    "❅ ʏᴏᴜ ᴄᴀɴ ᴅᴏ ᴀɴʏᴛʜɪɴɢ, ʙᴜᴛ ɴᴏᴛ ᴇᴠᴇʀʏᴛʜɪɴɢ.",
    "❅ ʟɪғᴇ ʙᴇᴄᴏᴍᴇ ᴇᴀsʏ ᴡʜᴇɴ ʏᴏᴜ ʙᴇᴄᴏᴍᴇ sᴛʀᴏɴɢ.",
    "❅ ᴍʏ ʟɪғᴇ ɪsɴ’ᴛ ᴘᴇʀғᴇᴄᴛ ʙᴜᴛ ɪᴛ ᴅᴏᴇs ʜᴀᴠᴇ ᴘᴇʀғᴇᴄᴛ ᴍᴏᴍᴇɴᴛs.",
    "❅ ʟɪғᴇ ɪs ɢᴏᴅ’s ɴᴏᴠᴇʟ. ʟᴇᴛ ʜɪᴍ ᴡʀɪᴛᴇ ɪᴛ.",
    "❅ ᴏᴜʀ ʟɪғᴇ ɪs ᴀ ʀᴇsᴜʟᴛ ᴏғ ᴏᴜʀ ᴅᴏᴍɪɴᴀɴᴛ ᴛʜᴏᴜɢʜᴛs.",
    "❅ ʟɪғᴇ ɪs ᴀ ᴍᴏᴛɪᴏɴ ғʀᴏᴍ ᴀ ᴅᴇsɪʀᴇ ᴛᴏ ᴀɴᴏᴛʜᴇʀ ᴅᴇsɪʀᴇ.",
    "❅ ᴛᴏ ʟɪᴠᴇ ᴍᴇᴀɴs ᴛᴏ ғɪɢʜᴛ.",
    "❅ ʟɪғᴇ ɪs ʟɪᴋᴇ ᴀ ᴍᴏᴜɴᴛᴀɪɴ, ɴᴏᴛ ᴀ ʙᴇᴀᴄʜ.",
    "❅ ᴛʜᴇ ᴡᴏʀsᴛ ᴛʜɪɴɢ ɪɴ ʟɪғᴇ ɪs ᴛʜᴀᴛ ɪᴛ ᴘᴀssᴇs.",
    "❅ ʟɪғᴇ ɪs sɪᴍᴘʟᴇ ɪғ ᴡᴇ ᴀʀᴇ sɪᴍᴘʟᴇ.",
    "❅ ᴀʟᴡᴀʏs ᴛʜɪɴᴋ ᴛᴡɪᴄᴇ, sᴘᴇᴀᴋ ᴏɴᴄᴇ.",
    "❅ ʟɪғᴇ ɪs sɪᴍᴘʟᴇ, ᴡᴇ ᴍᴀᴋᴇ ɪᴛ ᴄᴏᴍᴘʟɪᴄᴀᴛᴇᴅ.",
    "❅ ʟɪғᴇ ɪs ɴᴏᴛ ᴍᴜᴄʜ ᴏʟᴅᴇʀ ᴛʜᴀɴ ᴛʜᴇ ᴅᴇᴀᴛʜ.",
    "❅ ᴛʜᴇ sᴇᴄʀᴇᴛ ᴏғ ʟɪғᴇ ɪs ʟᴏᴡ ᴇxᴘᴇᴄᴛᴀᴛɪᴏɴs!",
    "❅ ʟɪғᴇ ɪs ᴀ ᴛᴇᴀᴄʜᴇʀ..,ᴛʜᴇ ᴍᴏʀᴇ ᴡᴇ ʟɪᴠᴇ, ᴛʜᴇ ᴍᴏʀᴇ ᴡᴇ ʟᴇᴀʀɴ.",
    "❅ ʜᴜᴍᴀɴ ʟɪғᴇ ɪs ɴᴏᴛʜɪɴɢ ʙᴜᴛ ᴀɴ ᴇᴛᴇʀɴᴀʟ ɪʟʟᴜsɪᴏɴ.",
    "❅ ᴛʜᴇ ʜᴀᴘᴘɪᴇʀ ᴛʜᴇ ᴛɪᴍᴇ, ᴛʜᴇ sʜᴏʀᴛᴇʀ ɪᴛ ɪs.",
    "❅ ʟɪғᴇ ɪs ʙᴇᴀᴜᴛɪғᴜʟ ɪғ ʏᴏᴜ ᴋɴᴏᴡ ᴡʜᴇʀᴇ ᴛᴏ ʟᴏᴏᴋ.",
    "❅ ʟɪғᴇ ɪs ᴀᴡᴇsᴏᴍᴇ ᴡɪᴛʜ ʏᴏᴜ ʙʏ ᴍʏ sɪᴅᴇ.",
    "❅ ʟɪғᴇ – ʟᴏᴠᴇ = ᴢᴇʀᴏ",
    "❅ ʟɪғᴇ ɪs ғᴜʟʟ ᴏғ sᴛʀᴜɢɢʟᴇs.",
    "❅ ɪ ɢᴏᴛ ʟᴇss ʙᴜᴛ ɪ ɢᴏᴛ ʙᴇsᴛ",
    "❅ ʟɪғᴇ ɪs 10% ᴡʜᴀᴛ ʏᴏᴜ ᴍᴀᴋᴇ ɪᴛ, ᴀɴᴅ 90% ʜᴏᴡ ʏᴏᴜ ᴛᴀᴋᴇ ɪᴛ.",
    "❅ ᴛʜᴇʀᴇ ɪs sᴛɪʟʟ sᴏ ᴍᴜᴄʜ ᴛᴏ sᴇᴇ",
    "❅ ʟɪғᴇ ᴅᴏᴇsɴ’ᴛ ɢᴇᴛ ᴇᴀsɪᴇʀ ʏᴏᴜ ɢᴇᴛ sᴛʀᴏɴɢᴇʀ.",
    "❅ ʟɪғᴇ ɪs ᴀʙᴏᴜᴛ ʟᴀᴜɢʜɪɴɢ & ʟɪᴠɪɴɢ.",
    "❅ ᴇᴀᴄʜ ᴘᴇʀsᴏɴ ᴅɪᴇs ᴡʜᴇɴ ʜɪs ᴛɪᴍᴇ ᴄᴏᴍᴇs.",
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_user_mention(user):

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
            "[HI/LIFE TAG] Admin verification failed"
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
                "[HI/LIFE TAG] FloodWait chat=%s wait=%ss",
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
                "[HI/LIFE TAG] Failed sending message chat=%s",
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

        async for member in client.get_chat_members(chat_id):

            if stop_event.is_set():
                break

            user = getattr(member, "user", None)

            if not user:
                continue

            if user.id in seen_users:
                continue

            seen_users.add(user.id)

            total_retrieved += 1

            if user.is_bot or user.is_deleted:
                continue

            mention = get_user_mention(user)

            # ━━━━━━━━━━━━━━━━━━━━━━━
            # HINDI REPLY MODE
            # ━━━━━━━━━━━━━━━━━━━━━━━

            if mode == "hindi_reply":

                emoji = random.choice(EMOJI)

                content = (
                    "<b><blockquote>"
                    f"{mention}\n\n"
                    f"{escape(emoji)}"
                    "</blockquote></b>"
                )

                reply_id = replied.id

            # ━━━━━━━━━━━━━━━━━━━━━━━
            # LIFE QUOTES MODE
            # ━━━━━━━━━━━━━━━━━━━━━━━

            elif mode == "life":

                phrase = random.choice(VC_TAG)

                content = (
                    "<b><blockquote>"
                    f"🌸 {mention}\n\n"
                    f"{escape(phrase)}"
                    "</blockquote></b>"
                )

                reply_id = None

            # ━━━━━━━━━━━━━━━━━━━━━━━
            # HINDI MODE
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
                "[HI/LIFE TAG] chat=%s mode=%s "
                "user_id=%s tagged=%s",
                chat_id,
                mode,
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

        LOGGER.warning(
            "[HI/LIFE TAG] Member retrieval FloodWait "
            "chat=%s wait=%ss",
            chat_id,
            error.value,
        )

    except Exception:

        LOGGER.exception(
            "[HI/LIFE TAG] Member retrieval failed chat=%s",
            chat_id,
        )

    finally:

        current_task = asyncio.current_task()

        if TAG_TASKS.get(chat_id) is current_task:
            TAG_TASKS.pop(chat_id, None)
            TAG_STOPS.pop(chat_id, None)

        LOGGER.warning(
            "[HI/LIFE TAG] Finished chat=%s mode=%s "
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
                "[HI/LIFE TAG] Completion notification failed"
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
            "🛑 <code>/histop</code> "
            "ᴏʀ <code>/lifestop</code>"
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
        "hindi": "🇮🇳 ʜɪɴᴅɪ",
        "hindi_reply": "💗 ᴇᴍᴏᴊɪ ʀᴇᴘʟʏ",
        "life": "🌸 ʟɪғᴇ ǫᴜᴏᴛᴇs",
    }.get(mode, "ᴛᴀɢɢɪɴɢ")

    try:

        await message.reply_text(
            "<b><blockquote>"
            "🚀 𝐁𝐑𝐀𝐍𝐃𝐄𝐃 𝐓𝐀𝐆𝐆𝐈𝐍𝐆\n\n"
            f"💬 ᴍᴏᴅᴇ: {mode_name}\n"
            "👥 ᴇᴀᴄʜ ᴜɴɪǫᴜᴇ ᴍᴇᴍʙᴇʀ ᴏɴᴄᴇ\n"
            f"⏳ ᴅᴇʟᴀʏ: {TAG_DELAY} sᴇᴄᴏɴᴅs\n\n"
            "🛑 <code>/histop</code> "
            "ᴏʀ <code>/lifestop</code>"
            "</blockquote></b>",
        )

    except Exception:

        LOGGER.exception(
            "[HI/LIFE TAG] Start notification failed"
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HINDI TAG COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(
    filters.command(
        ["hitag"],
        prefixes=["/", "@", "#"],
    )
)
async def hindi_tag(client, message):

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

    if len(parts) > 1:

        return await message.reply_text(
            "<b><blockquote>"
            "⚠️ ᴄᴏʀʀᴇᴄᴛ ᴜsᴀɢᴇ:\n\n"
            "➻ <code>/hitag</code>\n\n"
            "💬 ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴍᴇssᴀɢᴇ "
            "ᴡɪᴛʜ <code>/hitag</code>"
            "</blockquote></b>",
        )

    replied = message.reply_to_message

    if replied:
        mode = "hindi_reply"
    else:
        mode = "hindi"

    await start_tagging(
        client=client,
        message=message,
        mode=mode,
        replied=replied,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LIFE TAG COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(
    filters.command(
        ["lifetag"],
        prefixes=["/", "@", "#"],
    )
)
async def life_tag(client, message):

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
        mode="life",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STOP TAGGING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(
    filters.command(
        ["histop", "lifestop"],
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
        ["hitagcheck"],
        prefixes=["/", "@", "#"],
    )
)
async def hindi_tag_check(client, message):

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
            "[HI/LIFE TAG CHECK] Failed chat=%s",
            chat_id,
        )

    try:
        reported = await client.get_chat_members_count(chat_id)

    except Exception:
        reported = "Unavailable"

    LOGGER.warning(
        "[HI/LIFE TAG CHECK] chat=%s "
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
