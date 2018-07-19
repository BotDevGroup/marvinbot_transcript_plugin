# -*- coding: utf-8 -*-

import logging
import urllib3
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
        self.http = urllib3.PoolManager()

    def get_default_config(self):
        return {
            'short_name': self.name,
            'enabled': True
        }

    def configure(self, config):
        self.config = config

    def setup_handlers(self, adapter):
        self.add_handler(CommandHandler('transcript', self.on_transcript_command,
                                        command_description='Transcribes voice notes to their textual representation using Google Speech Recognition.'))

    def setup_schedules(self, adapter):
        pass

    def transcribe(self, url, message):
        sent_message = message.reply_text(
            text='*Transcribing...*',
            parse_mode='Markdown'
        )

        try:
            client = speech.SpeechClient()

            request = self.http.request('GET', url, preload_content=False)
            stream = request.stream(24000)

            requests = (types.StreamingRecognizeRequest(
                audio_content=chunk) for chunk in stream)

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
                log.info('transcripts: {}'.format('\n\n'.join(transcripts)))
                sent_message.edit_text(
                    text='\n\n'.join(transcripts),
                    parse_mode='Markdown'
                )
        except Exception as err:
            message.reply_text(
                text='❌ Unable to transcribe the voice note: {}'.format(err))

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

        url = message.reply_to_message.voice.get_file().file_path

        self.transcribe(url, message)
