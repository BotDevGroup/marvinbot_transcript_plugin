# -*- coding: utf-8 -*-

import io
import logging
import os
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from marvinbot.handlers import CommandHandler
from marvinbot.models import User
from marvinbot.net import fetch_from_telegram
from marvinbot.plugins import Plugin
from marvinbot.utils import trim_markdown

log = logging.getLogger(__name__)


class TranscriptPlugin(Plugin):
    def __init__(self):
        super(TranscriptPlugin, self).__init__('transcript_plugin')

    def get_default_config(self):
        return {
            'short_name': self.name,
            'key': None,
            'enabled': True
        }

    def configure(self, config):
        self.config = config
        if self.config.get('key') is None:
            log.error(
                'Google API key for speech recognition missing. /transcribe will not work')

    def setup_handlers(self, adapter):
        self.add_handler(CommandHandler('transcript', self.on_transcript_command,
                                        command_description='Transcribes voice notes to their textual representation using Google Speech Recognition.'))

    def setup_schedules(self, adapter):
        pass

    def transcribe(self, file_name, message):
        sent_message = message.reply_text(
            text='*Transcribing...*',
            parse_mode='Markdown'
        )

        try:
            client = speech.SpeechClient()

            with io.open(file_name, 'rb') as audio_file:
                content = audio_file.read()

            stream = [content]
            requests = (types.StreamingRecognizeRequest(audio_content=chunk) for chunk in stream)

            config = types.RecognitionConfig(
                encoding=enums.RecognitionConfig.AudioEncoding.OGG_OPUS,
                sample_rate_hertz=48000,
                language_code='es-DO'
            )
            streaming_config = types.StreamingRecognitionConfig(config=config)

            responses = client.streaming_recognize(streaming_config, requests)

            transcripts = []
            for response in responses:
                for result in response.results:
                    for alternative in result.alternatives:
                        transcripts.append('*Transcript:* {transcript}\n*Confidence:* {confidence:.2f}%'.format(
                            transcript=trim_markdown(alternative.transcript),
                            confidence=alternative.confidence,
                        ))

                sent_message.edit_text(
                    text='\n\n'.join(transcripts),
                    parse_mode='Markdown'
                )
        except Exception as err:
            message.reply_text(text='❌ Unable to transcribe the voice note: {}'.format(err))

        os.unlink(file_name)

    def on_transcript_command(self, update):
        message = update.effective_message

        if not User.is_user_admin(message.from_user):
            message.reply_text(text="❌ You are not allowed to do that.")
            return

        if not message.reply_to_message or not message.reply_to_message.voice:
            message.reply_text(
                text='❌ Use /transcript when replying to a voice note.')
            return

        duration = message.reply_to_message.voice.duration

        if duration > 60:
            message.reply_text(
                text='❌ Voice notes longer than one minute are not allowed.')
            return

        file_id = message.reply_to_message.voice.file_id

        fetch_from_telegram(
            self.adapter,
            file_id,
            on_done=lambda file_name: self.transcribe(file_name, message))
