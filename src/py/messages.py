"""
    A basic module for selecting and playing messages out loud using speak.
    Author: Patrick Emery
    Contact: info@pemery.co
"""
from multiprocessing import Queue
from queue import Empty
import pyttsx3

from random import choice, random
from time import sleep
from typing import Dict, List

from .models.config import TTSConfig
from . import config, animation

_animation_state = None
_engine = pyttsx3.init()
_speak_queue: Queue = None

def _speak(message: str):
    sleep(0.5)
    _engine.say(message)
    _engine.runAndWait()

class MessageBot:
    _last: Dict[int, float] = {}
    _visit: Dict[int, List[int]] = {}

    def __init__(self, config: List[TTSConfig]):
        self.config = config

    def _has_valid_speech(self, index: int, message: TTSConfig):
        self._visit[index] = self._visit.get(index) or []
        if message.can_repeat == False:
            if self._visit[index]:
                return len(self._visit[index]) < len(message.speech)
        return True

    def _get_speech(self, message_index: int, message: TTSConfig):
        if message.can_repeat == False:
            self._visit[message_index] = self._visit.get(message_index) or []
            index, speech = choice([(k, v) for k, v in enumerate(message.speech)]) # Picks a random list entry and its index.
            while index in self._visit[message_index]: # Keep picking until we find something which hasn't been picked before.
                index, speech = choice([(k, v) for k, v in enumerate(message.speech)])
            self._visit[message_index].append(index)
            return speech
        return choice(message.speech)

    def run(self):
        seconds = 0
        while True:
            while True:
                try:
                    datum = _speak_queue.get(False)
                    if datum is None: 
                        break
                    (message, animation_state) = datum
                    animation.set_state(animation_state, _animation_state)
                    _speak(message)
                    animation.set_state("default", _animation_state)
                except Empty:
                    break
                
            valid_messages = []
            for index, message in enumerate(self.config):
                if (
                    ((not message.after) or message.after <= seconds) and
                    ((not message.before) or message.before >= seconds) and
                    (
                        (not message.minimum_gap) or 
                        (index not in self._last) or
                        (seconds - self._last[index]) > message.minimum_gap
                    ) and
                    self._has_valid_speech(index, message)
                ):
                    valid_messages.append((index, message))

            if valid_messages and message.chance > random():
                index, message = choice(valid_messages)
                self._last[index] = seconds
                animation.set_state(message.animation, _animation_state)
                _speak(self._get_speech(index, message))
                animation.set_state("default", _animation_state)
            sleep(1)
            seconds += 1

def run(state, speak_queue):
    global _animation_state, _speak_queue
    _speak_queue = speak_queue
    _animation_state = state
    messages = MessageBot(config.main.tts)
    messages.run()