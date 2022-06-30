"""
    A basic module for selecting and playing messages out loud using speak.
    Author: Patrick Emery
    Contact: info@pemery.co
"""
from random import choice, randint, random
from typing import Dict, List, Tuple

from .models.config import TTSConfig
from .speak import speak
import asyncio


class MessageBot:
    _last: Dict[int, float] = {}
    _visit: Dict[int, List[int]] = {}

    def __init__(self, config: List[TTSConfig]):
        self.config = config

    def _has_valid_speech(self, index: int, message: TTSConfig):
        if message.can_repeat == False:
            if self._visit[message]:
                return len(self._visit[message]) < len(message.speech)
        return True

    def _get_speech(self, message_index: int, message: TTSConfig):
        if message.can_repeat == False:
            self._visit[message_index] = self._visit.get(index) or []
            index, speech = choice([(k, v) for k, v in enumerate(message.speech)]) # Picks a random list entry and its index.
            while index in self._visit[message_index]: # Keep picking until we find something which hasn't been picked before.
                index, speech = choice([(k, v) for k, v in enumerate(message.speech)])
            self._visit[message_index].append(index)
            return speech
        return choice(message.speech)

    async def run(self):
        minutes = 0
        while True:
            valid_messages = []
            for index, message in enumerate(self.config):
                if (
                    ((not message.after) or message.after <= minutes) and
                    ((not message.before) or message.before >= minutes) and
                    (
                        (not message.minimum_gap) or 
                        (index not in self._last) or
                        (minutes - self._last[index]) > message.minimum_gap
                    ) and
                    self._has_valid_speech(index, message)
                ):
                    valid_messages.append((index, message))

            if valid_messages and message.chance > random():
                index, message = choice(valid_messages)
                self._last[index] = minutes
                speak(self._get_speech(index, message))

            await asyncio.sleep(1)
            minutes += 1