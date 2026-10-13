import asyncio
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ntgcalls import TelegramServerError
from pytgcalls import PyTgCalls
from pytgcalls.exceptions import AlreadyJoinedError, NoActiveGroupCall, NotInGroupCallError
from pytgcalls.types import (
    JoinedGroupCallParticipant, LeftGroupCallParticipant, MediaStream,
    AudioQuality, VideoQuality, Update,
)
from pytgcalls.types.stream import StreamAudioEnded
import config
from BrandrdXMusic import LOGGER, YouTube, app
from BrandrdXMusic.misc import db
from BrandrdXMusic.utils.database import (
    add_active_chat, add_active_video_chat, get_lang, get_loop,
    group_assistant, is_autoend, is_vclogger_on, music_on,
    remove_active_chat, remove_active_video_chat, set_loop,
)
from BrandrdXMusic.utils.exceptions import AssistantErr
from BrandrdXMusic.utils.formatters import (
    check_duration, seconds_to_min, speed_converter,
)
from BrandrdXMusic.utils.inline.play import stream_markup, stream_markup2
from BrandrdXMusic.utils.stream.autoclear import auto_clean
from BrandrdXMusic.utils.thumbnails import get_thumb
from strings import get_string

LOG = LOGGER(__name__)
LOG.setLevel(logging.WARNING)
autoend = {}
counter = {}
DOWNLOAD_TIMEOUT = 270
JOIN_TIMEOUT = 60
CHANGE_TIMEOUT = 60
loop = asyncio.get_event_loop_policy().get_event_loop()

# Keep the current track start time to reject clearly premature end events.
stream_started = {}
EARLY_END_GRACE = 30



def _file_valid(path):
    if not path or not isinstance(path, (str, os.PathLike)):
        return False
    try:
        return os.path.isfile(path) and os.path.getsize(path) > 1024
    except OSError:
        return False


def _make_stream(link, video=False, ffmpeg_parameters=None):
    if not link:
        raise AssistantErr('Invalid or empty stream path.')
    kwargs = {'audio_parameters': AudioQuality.HIGH}
    if video:
        kwargs['video_parameters'] = VideoQuality.SD_480p
    else:
        kwargs['video_flags'] = MediaStream.IGNORE
    if ffmpeg_parameters:
        kwargs['ffmpeg_parameters'] = ffmpeg_parameters
    return MediaStream(link, **kwargs)


async def _clear_(chat_id):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)
    stream_started.pop(chat_id, None)
    autoend.pop(chat_id, None)
    counter.pop(chat_id, None)
    LOG.info('[VC] Cleared chat: %s', chat_id)


async def vclogger_mention(user_id: int):
    try:
        user = await app.get_users(user_id)
        return user.mention
    except Exception:
        return f"<a href='tg://user?id={user_id}'>ᴜsᴇʀ</a>"


async def _safe_delete(message):
    if message:
        try:
            await message.delete()
        except Exception:
            pass


async def _safe_error(message, text):
    if not message:
        return
    try:
        await message.edit_text(text, disable_web_page_preview=True)
    except Exception:
        try:
            await message.reply_text(text)
        except Exception:
            pass


def _already_left(error):
    if isinstance(error, NotInGroupCallError):
        return True
    if type(error).__name__ == "ConnectionNotFound":
        return True
    msg = str(error).lower()
    return (
        "isn't in a group call" in msg
        or 'is not in a group call' in msg
        or 'not in a group call' in msg
        or 'connection with chat id' in msg and 'not found' in msg
    )


class Call(PyTgCalls):
    def __init__(self):
        self.userbot1 = Client(name='BrandrdXMusic1', api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING1))
        self.one = PyTgCalls(self.userbot1, cache_duration=100)
        self.userbot2 = Client(name='BrandrdXMusic2', api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING2))
        self.two = PyTgCalls(self.userbot2, cache_duration=100)
        self.userbot3 = Client(name='BrandrdXMusic3', api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING3))
        self.three = PyTgCalls(self.userbot3, cache_duration=100)
        self.userbot4 = Client(name='BrandrdXMusic4', api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING4))
        self.four = PyTgCalls(self.userbot4, cache_duration=100)
        self.userbot5 = Client(name='BrandrdXMusic5', api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING5))
        self.five = PyTgCalls(self.userbot5, cache_duration=100)
        LOG.info('[VC] Call class initialized successfully.')

    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.pause_stream(chat_id)
        LOG.info('[VC] Paused: %s', chat_id)

    async def mute_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.mute_stream(chat_id)

    async def unmute_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.unmute_stream(chat_id)

    async def get_participant(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        return await assistant.get_participants(chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.resume_stream(chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await _clear_(chat_id)
        try:
            await assistant.leave_group_call(chat_id)
        except Exception as e:
            if not _already_left(e):
                LOG.warning('[VC] Stop stream leave error: %s', e)

    async def stop_stream_force(self, chat_id: int):
        assistants = [
            (config.STRING1, self.one), (config.STRING2, self.two),
            (config.STRING3, self.three), (config.STRING4, self.four),
            (config.STRING5, self.five),
        ]
        for session, assistant in assistants:
            if not session:
                continue
            try:
                await assistant.leave_group_call(chat_id)
            except Exception as e:
                if not _already_left(e):
                    LOG.warning('[VC] Force leave error: %s', e)
        await _clear_(chat_id)

    async def speedup_stream(self, chat_id: int, file_path, speed, playing):
        assistant = await group_assistant(self, chat_id)
        if not _file_valid(file_path):
            raise AssistantErr('Playback file is missing or invalid.')
        if str(speed) != '1.0':
            base = os.path.basename(file_path)
            chatdir = os.path.join(os.getcwd(), 'playback', str(speed))
            os.makedirs(chatdir, exist_ok=True)
            out = os.path.join(chatdir, base)
            if not _file_valid(out):
                if str(speed) == '0.5':
                    vs = 2.0
                elif str(speed) == '0.75':
                    vs = 1.35
                elif str(speed) == '1.5':
                    vs = 0.68
                elif str(speed) == '2.0':
                    vs = 0.5
                else:
                    vs = 1.0
                command = [
                    'ffmpeg', '-y', '-i', file_path,
                    '-filter:v', f'setpts={vs}*PTS',
                    '-filter:a', f'atempo={speed}', out,
                ]
                LOG.info('[FFmpeg] Speed conversion started: %s', file_path)
                proc = await asyncio.create_subprocess_exec(
                    *command, stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.PIPE,
                )
                try:
                    _, stderr = await asyncio.wait_for(proc.communicate(), timeout=180)
                except asyncio.TimeoutError:
                    proc.kill()
                    await proc.communicate()
                    raise AssistantErr('FFmpeg speed conversion timed out.')
                if proc.returncode != 0:
                    LOG.error('[FFmpeg] Conversion failed: %s', stderr.decode(errors='replace')[-1500:])
                    raise AssistantErr('FFmpeg speed conversion failed.')
        else:
            out = file_path
        if not _file_valid(out):
            raise AssistantErr('Converted playback file is invalid.')
        dur = int(await asyncio.to_thread(check_duration, out))
        played, con_seconds = speed_converter(playing[0]['played'], speed)
        duration = seconds_to_min(dur)
        video = playing[0]['streamtype'] == 'video'
        stream = _make_stream(out, video=video, ffmpeg_parameters=f'-ss {played} -to {duration}')
        if str(db[chat_id][0]['file']) != str(file_path):
            raise AssistantErr('Playback file changed during speed conversion.')
        await assistant.change_stream(chat_id, stream)
        stream_started[chat_id] = time.monotonic()
        if str(db[chat_id][0]['file']) == str(file_path):
            if not playing[0].get('old_dur'):
                db[chat_id][0]['old_dur'] = db[chat_id][0]['dur']
                db[chat_id][0]['old_second'] = db[chat_id][0]['seconds']
            db[chat_id][0]['played'] = con_seconds
            db[chat_id][0]['dur'] = duration
            db[chat_id][0]['seconds'] = dur
            db[chat_id][0]['speed_path'] = out
            db[chat_id][0]['speed'] = speed

    async def force_stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            check = db.get(chat_id)
            if check:
                check.pop(0)
        except Exception:
            pass
        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)
        try:
            await assistant.leave_group_call(chat_id)
        except Exception as e:
            if not _already_left(e):
                LOG.warning('[VC] Force stop leave error: %s', e)

    async def skip_stream(self, chat_id: int, link: str, video: Union[bool, str] = None, image: Union[bool, str] = None):
        assistant = await group_assistant(self, chat_id)
        LOG.info('[VC] Skip stream: chat=%s link=%s', chat_id, link)
        await assistant.change_stream(chat_id, _make_stream(link, video=bool(video)))
        stream_started[chat_id] = time.monotonic()

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        assistant = await group_assistant(self, chat_id)
        stream = _make_stream(file_path, video=(mode == 'video'), ffmpeg_parameters=f'-ss {to_seek} -to {duration}')
        await assistant.change_stream(chat_id, stream)
        stream_started[chat_id] = time.monotonic()

    async def stream_call(self, link):
        assistant = await group_assistant(self, config.LOGGER_ID)
        await assistant.join_group_call(config.LOGGER_ID, MediaStream(link))
        await asyncio.sleep(0.2)
        await assistant.leave_group_call(config.LOGGER_ID)

    async def join_call(self, chat_id: int, original_chat_id: int, link, video: Union[bool, str] = None, image: Union[bool, str] = None):
        started = time.monotonic()
        LOG.info('[VC] Join requested: chat=%s file=%s video=%s', chat_id, link, video)
        assistant = await group_assistant(self, chat_id)
        language = await get_lang(chat_id)
        _ = get_string(language)
        if not link:
            LOG.error('[VC] Empty stream path: %s', chat_id)
            raise AssistantErr('Song download failed. Empty stream path.')
        if isinstance(link, str) and not link.startswith(('http://', 'https://', 'rtmp://', 'rtsp://')):
            if not _file_valid(link):
                LOG.error('[VC] Invalid local file: %s', link)
                raise AssistantErr('Downloaded audio file is missing or invalid.')
        stream = _make_stream(link, video=bool(video))
        try:
            LOG.info('[VC] Joining group call: %s', chat_id)
            await asyncio.wait_for(assistant.join_group_call(chat_id, stream), timeout=JOIN_TIMEOUT)
        except NoActiveGroupCall:
            LOG.error('[VC] No active group call: %s', chat_id)
            raise AssistantErr(_['call_8'])
        except AlreadyJoinedError:
            LOG.warning('[VC] Already joined: %s', chat_id)
            raise AssistantErr(_['call_9'])
        except TelegramServerError:
            LOG.exception('[VC] Telegram server error')
            raise AssistantErr(_['call_10'])
        except asyncio.TimeoutError:
            LOG.error('[VC] Join timed out: %s', chat_id)
            raise AssistantErr('Assistant VC join timed out.')
        except Exception as e:
            if 'phone.CreateGroupCall' in str(e):
                raise AssistantErr(_['call_8'])
            LOG.exception('[VC] Unexpected join call error')
            raise
        stream_started[chat_id] = time.monotonic()
        LOG.info('[VC] JOIN SUCCESS chat=%s time=%.2fs', chat_id, time.monotonic() - started)
        await add_active_chat(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)
        if await is_autoend():
            counter[chat_id] = {}
            try:
                users = len(await assistant.get_participants(chat_id))
                if users == 1:
                    autoend[chat_id] = datetime.now() + timedelta(minutes=1)
            except Exception:
                LOG.exception('[VC] Autoend participant check failed')

    async def change_stream(self, client, chat_id):
        LOG.info('[QUEUE] Stream ended: chat=%s', chat_id)
        check = db.get(chat_id)
        if not check:
            await _clear_(chat_id)
            try:
                await client.leave_group_call(chat_id)
            except Exception as e:
                if not _already_left(e):
                    LOG.warning('[QUEUE] Leave error: %s', e)
            return
        popped = None
        loop_count = await get_loop(chat_id)
        try:
            if loop_count == 0:
                popped = check.pop(0)
            else:
                loop_count -= 1
                await set_loop(chat_id, loop_count)
            if popped:
                try:
                    await auto_clean(popped)
                except Exception:
                    LOG.exception('[QUEUE] Auto-clean failed')
            if not check:
                await _clear_(chat_id)
                try:
                    return await client.leave_group_call(chat_id)
                except Exception as e:
                    if not _already_left(e):
                        LOG.warning('[QUEUE] Leave error: %s', e)
                    return
        except Exception:
            LOG.exception('[QUEUE] Queue processing failed')
            await _clear_(chat_id)
            try:
                await client.leave_group_call(chat_id)
            except Exception as e:
                if not _already_left(e):
                    LOG.warning('[QUEUE] Leave error: %s', e)
            return
        queued = check[0]['file']
        language = await get_lang(chat_id)
        _ = get_string(language)
        title = check[0]['title'].title()
        artist = (check[0].get('artist') or check[0].get('uploader') or check[0].get('channel') or check[0].get('by') or 'Vibe Music')
        user = check[0]['by']
        original_chat_id = check[0]['chat_id']
        streamtype = check[0]['streamtype']
        videoid = check[0]['vidid']
        duration = check[0].get('dur') or '0:00'
        db[chat_id][0]['played'] = 0
        if exis := check[0].get('old_dur'):
            db[chat_id][0]['dur'] = exis
            db[chat_id][0]['seconds'] = check[0]['old_second']
            db[chat_id][0]['speed_path'] = None
            db[chat_id][0]['speed'] = 1.0
        video = str(streamtype) == 'video'
        LOG.info('[QUEUE] Next track: %s | %s | %s', title, videoid, streamtype)
        if 'live_' in queued:
            n, link = await YouTube.video(videoid, True)
            if n == 0 or not link:
                LOG.error('[QUEUE] Live download failed: %s', videoid)
                return await app.send_message(original_chat_id, text=_['call_6'])
            stream = _make_stream(link, video=video)
            try:
                await asyncio.wait_for(client.change_stream(chat_id, stream), timeout=CHANGE_TIMEOUT)
            except Exception:
                LOG.exception('[QUEUE] Live stream change failed')
                return await app.send_message(original_chat_id, text=_['call_6'])
            img = await get_thumb(videoid)
            button = stream_markup2(_, chat_id)
            run = await app.send_photo(
                has_spoiler=True,
                chat_id=original_chat_id, photo=img,
                caption=_['stream_1'].format(f'https://t.me/{app.username}?start=info_{videoid}', title[:23], duration, user),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]['mystic'] = run
            db[chat_id][0]['markup'] = 'tg'
        elif 'vid_' in queued:
            mystic = await app.send_message(original_chat_id, _['call_7'])
            LOG.info('[QUEUE] YouTube download started: %s', videoid)
            try:
                file_path, direct = await asyncio.wait_for(
                    YouTube.download(videoid, mystic, videoid=True, video=video), timeout=DOWNLOAD_TIMEOUT,
                )
            except asyncio.TimeoutError:
                LOG.error('[QUEUE] Download timeout: %s', videoid)
                return await _safe_error(mystic, _['call_6'])
            except Exception:
                LOG.exception('[QUEUE] YouTube download exception')
                return await _safe_error(mystic, _['call_6'])
            if not direct or not _file_valid(file_path):
                LOG.error('[QUEUE] Download failed or invalid: %s path=%s', videoid, file_path)
                return await _safe_error(mystic, _['call_6'])
            LOG.info('[QUEUE] DOWNLOAD SUCCESS: %s (%s bytes)', file_path, os.path.getsize(file_path))
            stream = _make_stream(file_path, video=video)
            try:
                await asyncio.wait_for(client.change_stream(chat_id, stream), timeout=CHANGE_TIMEOUT)
            except Exception:
                LOG.exception('[QUEUE] change_stream failed')
                return await _safe_error(mystic, _['call_6'])
            LOG.info('[QUEUE] PLAYBACK STARTED: %s', videoid)
            img = await get_thumb(videoid)
            button = stream_markup(_, videoid, chat_id)
            await _safe_delete(mystic)
            run = await app.send_photo(
                has_spoiler=True,
                chat_id=original_chat_id, photo=img,
                caption=_['stream_1'].format(f'https://t.me/{app.username}?start=info_{videoid}', title[:23], duration, user),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]['mystic'] = run
            db[chat_id][0]['markup'] = 'stream'
        elif 'index_' in queued:
            stream = _make_stream(videoid, video=video)
            try:
                await asyncio.wait_for(client.change_stream(chat_id, stream), timeout=CHANGE_TIMEOUT)
            except Exception:
                LOG.exception('[QUEUE] Index stream failed')
                return await app.send_message(original_chat_id, text=_['call_6'])
            button = stream_markup2(_, chat_id)
            run = await app.send_photo(
                has_spoiler=True,
                chat_id=original_chat_id, photo=config.STREAM_IMG_URL,
                caption=_['stream_2'].format(user), reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]['mystic'] = run
            db[chat_id][0]['markup'] = 'tg'
        else:
            stream = _make_stream(queued, video=video)
            try:
                await asyncio.wait_for(client.change_stream(chat_id, stream), timeout=CHANGE_TIMEOUT)
            except Exception:
                LOG.exception('[QUEUE] Direct stream change failed')
                return await app.send_message(original_chat_id, text=_['call_6'])
            if videoid == 'telegram':
                button = stream_markup2(_, chat_id)
                run = await app.send_photo(
                has_spoiler=True,
                    chat_id=original_chat_id,
                    photo=config.TELEGRAM_AUDIO_URL if str(streamtype) == 'audio' else config.TELEGRAM_VIDEO_URL,
                    caption=_['stream_1'].format(config.SUPPORT_CHAT, title[:23], duration, user),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]['mystic'] = run
                db[chat_id][0]['markup'] = 'tg'
            elif videoid == 'soundcloud':
                button = stream_markup2(_, chat_id)
                run = await app.send_photo(
                has_spoiler=True,
                    chat_id=original_chat_id, photo=config.SOUNDCLOUD_IMG_URL,
                    caption=_['stream_1'].format(config.SUPPORT_CHAT, title[:23], duration, user),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]['mystic'] = run
                db[chat_id][0]['markup'] = 'tg'
            else:
                img = await get_thumb(videoid)
                button = stream_markup(_, videoid, chat_id)
                run = await app.send_photo(
                has_spoiler=True,
                    chat_id=original_chat_id, photo=img,
                    caption=_['stream_1'].format(f'https://t.me/{app.username}?start=info_{videoid}', title[:23], duration, user),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]['mystic'] = run
                db[chat_id][0]['markup'] = 'stream'
        stream_started[chat_id] = time.monotonic()
        LOG.info('[QUEUE] Next stream processed: %s', videoid)

    async def ping(self):
        pings = []
        assistants = [
            (config.STRING1, self.one), (config.STRING2, self.two),
            (config.STRING3, self.three), (config.STRING4, self.four),
            (config.STRING5, self.five),
        ]
        for session, assistant in assistants:
            if not session:
                continue
            try:
                value = await assistant.ping
                pings.append(value)
            except Exception as e:
                LOG.warning('[VC] Assistant ping failed: %s', e)
        if not pings:
            return '0'
        return str(round(sum(pings) / len(pings), 3))

    async def start(self):
        LOG.info('Starting PyTgCalls Client...')
        assistants = [
            ('ONE', config.STRING1, self.one), ('TWO', config.STRING2, self.two),
            ('THREE', config.STRING3, self.three), ('FOUR', config.STRING4, self.four),
            ('FIVE', config.STRING5, self.five),
        ]
        started = 0
        for name, session, assistant in assistants:
            if not session:
                continue
            LOG.info('[VC] Starting Assistant %s...', name)
            try:
                await assistant.start()
                started += 1
                LOG.info('[VC] Assistant %s started successfully.', name)
            except Exception:
                LOG.exception('[VC] Assistant %s startup failed', name)
                raise
        LOG.info('[VC] PyTgCalls startup completed. Active assistants: %s', started)

    async def decorators(self):
        # Separate service callbacks identify WHY the assistant left.
        async def service_event(chat_id, reason):
            LOG.warning('[VC EVENT] %s chat=%s queue=%s elapsed=%.1fs',
                        reason, chat_id, len(db.get(chat_id) or []),
                        time.monotonic() - stream_started.get(chat_id, time.monotonic()))
            try:
                await self.stop_stream(chat_id)
            except Exception:
                LOG.exception('[VC EVENT] Service handler failed: %s', reason)

        async def kicked_handler(_, chat_id):
            await service_event(chat_id, 'KICKED')

        async def closed_handler(_, chat_id):
            await service_event(chat_id, 'VOICE_CHAT_CLOSED')

        async def left_handler(_, chat_id):
            await service_event(chat_id, 'ASSISTANT_LEFT')

        for assistant in (self.one, self.two, self.three, self.four, self.five):
            assistant.on_kicked()(kicked_handler)
            assistant.on_closed_voice_chat()(closed_handler)
            assistant.on_left()(left_handler)

        @self.one.on_stream_end()
        @self.two.on_stream_end()
        @self.three.on_stream_end()
        @self.four.on_stream_end()
        @self.five.on_stream_end()
        async def stream_end_handler(client, update: Update):
            try:
                if not isinstance(update, StreamAudioEnded):
                    return
                chat_id = update.chat_id
                tracks = db.get(chat_id) or []
                elapsed = time.monotonic() - stream_started.get(chat_id, time.monotonic())
                expected = 0
                if tracks:
                    try:
                        expected = float(tracks[0].get('seconds') or 0)
                    except (ValueError, TypeError):
                        pass
                LOG.warning('[VC EVENT] AUDIO_ENDED chat=%s elapsed=%.1fs expected=%ss queue=%s',
                            chat_id, elapsed, expected, len(tracks))
                # Do not discard a multi-minute song due to a premature end update.
                # This is a safety guard, not a fix for a truncated/corrupt audio file.
                if expected > 45 and elapsed < EARLY_END_GRACE:
                    LOG.warning('[VC EVENT] Premature stream-end ignored: chat=%s', chat_id)
                    return
                await self.change_stream(client, chat_id)
            except Exception:
                LOG.exception('[VC] Stream end handler failed')

        @self.one.on_participants_change()
        @self.two.on_participants_change()
        @self.three.on_participants_change()
        @self.four.on_participants_change()
        @self.five.on_participants_change()
        async def participants_change_handler(_, update: Update):
            try:
                if not await is_vclogger_on(update.chat_id):
                    return
                if isinstance(update, JoinedGroupCallParticipant):
                    tag = '#JᴏɪɴᴇᴅVᴄ'
                elif isinstance(update, LeftGroupCallParticipant):
                    tag = '#LᴇғᴛVᴄ'
                else:
                    return
                user_id = update.participant.user_id
                role = 'MEMBER'
                try:
                    member = await app.get_chat_member(update.chat_id, user_id)
                    if member.status == ChatMemberStatus.OWNER:
                        role = 'OWNER'
                    elif member.status == ChatMemberStatus.ADMINISTRATOR:
                        role = 'ADMIN'
                    elif member.status == ChatMemberStatus.MEMBER:
                        role = 'MEMBER'
                except Exception as e:
                    LOG.warning('[VC Logger] Role detection failed user=%s error=%s', user_id, e)
                mention = await vclogger_mention(user_id)
                text = (
                    f'<blockquote>{tag}\n'
                    f'➤ Usᴇʀ - {mention}\n'
                    f'➤ Usᴇʀɪᴅ - <code>{user_id}</code>\n'
                    f'➤ Rᴏʟᴇ - <b>{role}</b></blockquote>'
                )
                keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton('🎧 Jᴏɪɴ Tᴏ Vᴄ', url='https://t.me/c/' + str(update.chat_id)[4:])
                ]])
                sent_message = await app.send_message(
                    chat_id=update.chat_id, text=text, reply_markup=keyboard,
                )
                LOG.info('[VC Logger] %s user=%s chat=%s role=%s', tag, user_id, update.chat_id, role)

                async def delete_after_10_seconds():
                    await asyncio.sleep(10)
                    await _safe_delete(sent_message)

                asyncio.create_task(delete_after_10_seconds())
                return sent_message
            except Exception:
                LOG.exception('[VC Logger] Participant handler failed')
                return None


Hotty = Call()
