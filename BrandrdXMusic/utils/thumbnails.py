import os
import asyncio
from io import BytesIO

import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from config import YOUTUBE_IMG_URL

# ==============================
# BRANDRDXMUSIC PLAYER SETTINGS
# ==============================

CACHE_DIR = "cache"

PLAYER_WIDTH = 1648
PLAYER_HEIGHT = 900

GREEN = "#1ED760"
WHITE = "#FFFFFF"
CYAN = "#55DDFF"

SOURCES = (
    "maxresdefault",
    "sddefault",
    "hqdefault",
    "mqdefault",
)


# ==============================
# YOUTUBE THUMBNAIL DOWNLOAD
# ==============================

async def get_thumb(videoid):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = f"{CACHE_DIR}/{videoid}.jpg"

    if os.path.exists(path):
        return path

    async with aiohttp.ClientSession() as session:
        for source in SOURCES:
            url = f"https://i.ytimg.com/vi/{videoid}/{source}.jpg"

            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.read()

                        image = Image.open(BytesIO(data))
                        if image.width > 300:
                            with open(path, "wb") as file:
                                file.write(data)
                            return path
            except Exception:
                pass

    return YOUTUBE_IMG_URL


# ==============================
# FONT
# ==============================

def font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
    ]

    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass

    return ImageFont.load_default()


# ==============================
# ROUNDED IMAGE HELPERS
# ==============================

def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)

    draw.rounded_rectangle(
        (0, 0, size[0], size[1]),
        radius=radius,
        fill=255,
    )

    return mask


def rounded_paste(base, image, position, radius=40):
    image = image.convert("RGBA")

    base.paste(
        image,
        position,
        rounded_mask(image.size, radius),
    )


# ==============================
# COVER FIT / CROP
# ==============================

def fit_cover(image, size):
    image = image.convert("RGB")

    target_w, target_h = size
    src_w, src_h = image.size

    scale = max(
        target_w / src_w,
        target_h / src_h,
    )

    new_w = int(src_w * scale)
    new_h = int(src_h * scale)

    image = image.resize(
        (new_w, new_h),
        Image.Resampling.LANCZOS,
    )

    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2

    return image.crop(
        (
            left,
            top,
            left + target_w,
            top + target_h,
        )
    )


# ==============================
# TITLE FIT HELPER
# ==============================

def fit_title(draw, title, max_width, max_size=60, min_size=28):
    title = str(title or "Unknown Track").strip()

    current_size = max_size

    while current_size >= min_size:
        title_font = font(current_size, True)

        bbox = draw.textbbox(
            (0, 0),
            title,
            font=title_font,
        )

        if bbox[2] - bbox[0] <= max_width:
            return title, title_font

        current_size -= 1

    title_font = font(min_size, True)

    shortened = title

    while shortened:
        test_title = shortened.rstrip() + "..."

        bbox = draw.textbbox(
            (0, 0),
            test_title,
            font=title_font,
        )

        if bbox[2] - bbox[0] <= max_width:
            return test_title, title_font

        shortened = shortened[:-1]

    return "...", title_font


# ==============================
# PLAYER THUMBNAIL GENERATOR
# ==============================

def draw_player(videoid, title, duration, artist):

    original = f"{CACHE_DIR}/{videoid}.jpg"
    output = f"{CACHE_DIR}/{videoid}_player.jpg"

    if not os.path.exists(original):
        return YOUTUBE_IMG_URL

    try:
        cover = Image.open(original).convert("RGB")

        W = PLAYER_WIDTH
        H = PLAYER_HEIGHT

        # ==============================
        # BACKGROUND - LIGHT SOFT BLUR
        # ==============================

        bg = fit_cover(cover, (W, H))

        # Reduced blur for a softer natural background
        bg = bg.filter(
            ImageFilter.GaussianBlur(14)
        )

        bg = bg.convert("RGBA")

        # Light transparent blue overlay
        overlay = Image.new(
            "RGBA",
            (W, H),
            (15, 75, 120, 22),
        )

        bg = Image.alpha_composite(
            bg,
            overlay,
        )

        draw = ImageDraw.Draw(bg, "RGBA")

        # ==============================
        # LEFT SIDEBAR
        # ==============================

        draw.rectangle(
            (0, 0, 155, H),
            fill=(10, 65, 100, 175),
        )

        # SPOTIFY LOGO
        draw.ellipse(
            (50, 59, 108, 117),
            fill=(29, 215, 96, 255),
        )

        draw.arc(
            (61, 72, 99, 91),
            195, 345,
            fill=(0, 40, 25, 255),
            width=5,
        )

        draw.arc(
            (64, 82, 96, 99),
            195, 345,
            fill=(0, 40, 25, 255),
            width=4,
        )

        draw.arc(
            (67, 91, 93, 105),
            195, 345,
            fill=(0, 40, 25, 255),
            width=3,
        )

        # HOME
        draw.rounded_rectangle(
            (29, 179, 128, 289),
            28,
            fill=(20, 150, 130, 95),
            outline=(100, 245, 220, 130),
            width=2,
        )

        draw.text(
            (50, 202),
            "◆",
            font=font(38, True),
            fill=GREEN,
        )

        draw.text(
            (49, 250),
            "Home",
            font=font(22),
            fill=GREEN,
        )

        # SEARCH
        draw.ellipse(
            (61, 321, 91, 351),
            outline=WHITE,
            width=3,
        )

        draw.line(
            (85, 346, 100, 362),
            fill=WHITE,
            width=4,
        )

        draw.text(
            (44, 369),
            "Search",
            font=font(21),
            fill=WHITE,
        )

        # LIBRARY
        draw.text(
            (60, 427),
            "Ⅱ",
            font=font(40),
            fill=WHITE,
        )

        draw.text(
            (27, 486),
            "Your Library",
            font=font(19),
            fill=WHITE,
        )

        # LIKED SONGS
        draw.text(
            (54, 552),
            "♡",
            font=font(45),
            fill=WHITE,
        )

        draw.text(
            (31, 610),
            "Liked Songs",
            font=font(18),
            fill=WHITE,
        )

        # USER
        draw.line(
            (48, 709, 109, 709),
            fill=(200, 240, 255, 110),
            width=2,
        )

        draw.ellipse(
            (46, 746, 112, 812),
            fill=(150, 205, 235, 180),
        )

        draw.ellipse(
            (68, 758, 90, 780),
            fill=WHITE,
        )

        draw.rounded_rectangle(
            (58, 783, 100, 803),
            15,
            fill=WHITE,
        )

        draw.text(
            (57, 826),
            "User",
            font=font(20),
            fill=WHITE,
        )

        # ==============================
        # TOP UPGRADE BUTTON
        # ==============================

        draw.rounded_rectangle(
            (1298, 48, 1447, 98),
            26,
            fill=(50, 120, 175, 85),
            outline=(200, 245, 255, 170),
            width=2,
        )

        draw.text(
            (1328, 63),
            "UPGRADE",
            font=font(18, True),
            fill=WHITE,
        )

        # BELL
        draw.arc(
            (1483, 58, 1515, 91),
            180, 360,
            fill=WHITE,
            width=3,
        )

        draw.line(
            (1483, 75, 1483, 85),
            fill=WHITE,
            width=3,
        )

        draw.line(
            (1515, 75, 1515, 85),
            fill=WHITE,
            width=3,
        )

        draw.arc(
            (1483, 67, 1515, 98),
            0, 180,
            fill=WHITE,
            width=3,
        )

        draw.ellipse(
            (1496, 92, 1502, 98),
            fill=WHITE,
        )

        draw.text(
            (1545, 48),
            "•••",
            font=font(30, True),
            fill=WHITE,
        )

        # ==============================
        # MAIN PLAYER PANEL
        # FULLY TRANSPARENT
        # ==============================

        draw.rounded_rectangle(
            (184, 145, 1607, 814),
            48,
            outline=(85, 225, 255, 235),
            width=3,
        )

        # Inner border
        draw.rounded_rectangle(
            (188, 149, 1603, 810),
            45,
            outline=(210, 250, 255, 120),
            width=1,
        )

        # ==============================
        # ALBUM COVER
        # ==============================

        album = fit_cover(
            cover,
            (570, 656),
        ).convert("RGBA")

        rounded_paste(
            bg,
            album,
            (190, 150),
            48,
        )

        draw = ImageDraw.Draw(bg, "RGBA")

        # Album border
        draw.rounded_rectangle(
            (190, 150, 760, 806),
            48,
            outline=(150, 240, 255, 210),
            width=2,
        )

        # ==============================
        # PLAYING FROM YOUTUBE
        # ==============================

        for i, height in enumerate((18, 30, 24, 12)):
            x = 817 + i * 10

            draw.rounded_rectangle(
                (x, 250-height, x+6, 250),
                3,
                fill=(29, 215, 96, 255),
            )

        draw.text(
            (877, 224),
            "PLAYING FROM YOUTUBE",
            font=font(40, True),
            fill=(95, 225, 210, 255),
        )

        # ==============================
        # SONG TITLE
        # SPOTIFY STYLE - LARGE BOLD
        # ==============================

        title = str(title or "Unknown Track")

        title_x = 814
        title_y = 288

        # Heart aur more button se pehle tak
        title_max_width = 620

        title, title_font = fit_title(
            draw,
            title,
            title_max_width,
            max_size=85,
            min_size=45,
        )

        # SONG TITLE WITH LIGHT BLACK STROKE
        draw.text(
            (title_x, title_y),
            title,
            font=title_font,
            fill=(255, 255, 255, 255),
            stroke_width=1,
            stroke_fill=(20, 20, 20, 180),
        )

        # ==============================
        # ARTIST
        # ==============================

        draw.text(
            (814, 366),
            str(artist or "BRANDED MUSIC"),
            font=font(30),
            fill=(205, 230, 250, 255),
        )

        # ==============================
        # HEART BUTTON
        # ==============================

        draw.ellipse(
            (1452, 284, 1517, 350),
            fill=(45, 130, 185, 105),
            outline=(150, 240, 255, 180),
            width=2,
        )

        draw.text(
            (1464, 289),
            "♥",
            font=font(42),
            fill=GREEN,
        )

        # ==============================
        # MORE BUTTON
        # ==============================

        draw.ellipse(
            (1530, 284, 1595, 350),
            fill=(45, 130, 185, 105),
            outline=(150, 240, 255, 180),
            width=2,
        )

        draw.text(
            (1540, 298),
            "•••",
            font=font(24, True),
            fill=WHITE,
        )

        # ==============================
        # PROGRESS BAR
        # ==============================

        draw.rounded_rectangle(
            (815, 445, 1547, 458),
            7,
            fill=(120, 180, 220, 190),
        )

        draw.rounded_rectangle(
            (815, 445, 1084, 458),
            7,
            fill=GREEN,
        )

        draw.ellipse(
            (1067, 433, 1103, 470),
            fill=GREEN,
        )

        draw.text(
            (815, 479),
            "0:00",
            font=font(28),
            fill=WHITE,
        )

        try:
            duration = int(float(duration))
            time_text = f"{duration//60}:{duration%60:02d}"
        except Exception:
            time_text = str(duration)

        draw.text(
            (1482, 479),
            time_text,
            font=font(28),
            fill=WHITE,
        )

        # ==============================
        # SHUFFLE
        # ==============================

        draw.text(
            (832, 578),
            "⤨",
            font=font(45),
            fill=GREEN,
        )

        draw.ellipse(
            (853, 641, 863, 651),
            fill=GREEN,
        )

        # ==============================
        # PREVIOUS
        # ==============================

        draw.text(
            (986, 574),
            "◀",
            font=font(48),
            fill=WHITE,
        )

        # ==============================
        # PLAY / PAUSE
        # ==============================

        draw.ellipse(
            (1117, 537, 1255, 675),
            fill=WHITE,
        )

        draw.text(
            (1157, 564),
            "Ⅱ",
            font=font(65, True),
            fill=(8, 25, 40, 255),
        )

        # ==============================
        # NEXT
        # ==============================

        draw.text(
            (1340, 574),
            "▶",
            font=font(48),
            fill=WHITE,
        )

        # ==============================
        # REPEAT
        # ==============================

        draw.text(
            (1484, 578),
            "↻",
            font=font(45),
            fill=GREEN,
        )

        draw.ellipse(
            (1510, 641, 1520, 651),
            fill=GREEN,
        )

        # ==============================
        # BOTTOM VOLUME PANEL
        # FULLY TRANSPARENT
        # ==============================

        draw.rounded_rectangle(
            (800, 718, 1575, 805),
            44,
            outline=(120, 225, 255, 145),
            width=2,
        )

        # VOLUME ICON
        draw.text(
            (837, 735),
            "◀",
            font=font(35),
            fill=WHITE,
        )

        # VOLUME BAR
        draw.rounded_rectangle(
            (911, 755, 1232, 764),
            5,
            fill=(120, 180, 220, 190),
        )

        draw.rounded_rectangle(
            (911, 755, 1070, 764),
            5,
            fill=GREEN,
        )

        draw.ellipse(
            (1060, 743, 1092, 776),
            fill=WHITE,
        )

        # ==============================
        # EQUALIZER
        # ==============================

        for y in (748, 761, 774):
            draw.line(
                (1307, y, 1338, y),
                fill=WHITE,
                width=3,
            )

        for x, y in (
            (1310, 748),
            (1322, 761),
            (1314, 774),
        ):
            draw.ellipse(
                (x-4, y-4, x+4, y+4),
                fill=WHITE,
            )

        # ==============================
        # MINI PLAYER
        # ==============================

        draw.rounded_rectangle(
            (1398, 744, 1432, 778),
            4,
            outline=WHITE,
            width=3,
        )

        draw.line(
            (1405, 769, 1425, 769),
            fill=WHITE,
            width=2,
        )

        # ==============================
        # FULLSCREEN
        # ==============================

        draw.text(
            (1498, 738),
            "⛶",
            font=font(42),
            fill=WHITE,
        )

        # ==============================
        # SAVE PLAYER IMAGE
        # ==============================

        bg.convert("RGB").save(
            output,
            "JPEG",
            quality=95,
        )

        return output

    except Exception:
        return original


# ==============================
# ASYNC PLAYER THUMB FUNCTION
# ==============================

async def get_player_thumb(
    videoid,
    title,
    duration,
    artist="BRANDED MUSIC",
):
    await get_thumb(videoid)

    return await asyncio.to_thread(
        draw_player,
        videoid,
        title,
        duration,
        artist,
)
