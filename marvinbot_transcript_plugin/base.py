# -*- coding: utf-8 -*-

from marvinbot.utils import localized_date, get_message
from marvinbot.handlers import CommandHandler, CallbackQueryHandler
from marvinbot.plugins import Plugin
from marvinbot.models import User

import logging
import ctypes
import time
import re
import traceback
import base64
import json

from io import BytesIO

from apiclient.discovery import build
import httplib2

log = logging.getLogger(__name__)


class MarvinBotTranscriptPlugin(Plugin):
    def __init__(self):
        super(MarvinBotTranscriptPlugin, self).__init__('marvinbot_transcript_plugin')
        self.bot = None

    def get_default_config(self):
        return {
            'short_name': self.name,
            'enabled': True
        }

    def configure(self, config):
        self.config = config
        pass

    def setup_handlers(self, adapter):
        self.bot = adapter.bot
        self.add_handler(CommandHandler('transcript', self.on_transcript_command, command_description='Converter voice note to text'))
 
    def setup_schedules(self, adapter):
        pass

    def transcribe(self, content):
        service = build('speech', 'v1', developerKey=self.config.get('key'))
        service_request = service.speech().recognize(
            body={
                'config': {
                    'encoding': 'OGG_OPUS',
                    'sampleRateHertz': 16000,
                    'languageCode': 'es-DO'
                },
                'audio': {
                    'content': base64.b64encode(content.getvalue()).decode('UTF-8')
                    }
                })
        response = service_request.execute()

        for result in response['results']:
            return u'{}\n\nConfidence: {:.2f}%'.format(
                result['alternatives'][0]['transcript'],
                (float(result['alternatives'][0]['confidence']) * 100)
                )

    def on_transcript_command(self, update, *args, **kwargs):
        message = get_message(update)

        if message.reply_to_message and message.reply_to_message.voice:
            voice = message.reply_to_message.voice
            msg = ""
            out = None

            try:
                file = self.adapter.bot.getFile(file_id=voice['file_id'])
        
                # Download Voice
                out = BytesIO()
                out.seek(0)
                file.download(out=out)
                out.seek(0)

                if out is not None:
                    msg = self.transcribe(out)
                    self.adapter.bot.sendMessage(chat_id=message.chat_id, reply_to_message_id=message.reply_to_message.message_id, text=msg, parse_mode='Markdown')
            except Exception as err:
                msg = "Nope. Y'all can't use this shit. 🖕🏿"
                self.adapter.bot.sendMessage(chat_id=message.chat_id, text=msg)
                log.error("Transcript - get voice error: {}".format(err))
        else:
            msg = "Use /transcript when replying only to a VN only."
            self.adapter.bot.sendMessage(chat_id=message.chat_id, text=msg)