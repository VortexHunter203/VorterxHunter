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
