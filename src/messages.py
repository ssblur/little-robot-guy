"""
    A basic module for selecting and playing messages out loud using speak.
    Author: Patrick Emery
    Contact: info@pemery.co
"""
from random import choice, randint
from .speak.speak import speak
import asyncio


def _has_valid_speech(message: dict):
    if "can_repeat" in message and message["can_repeat"] == False:
        if "visited" in message:
            return len(message["visited"]) < len(message["speech"])
    return True

def _get_speech(message: dict):
    if "can_repeat" in message and message["can_repeat"] == False:
        message["visited"] = message.get("visited") or []
        index, speech = choice([(k, v) for k, v in enumerate(message["speech"])]) # Picks a random list entry and its index.
        while index in message["visited"]: # Keep picking until we find something which hasn't been picked before.
            index, speech = choice([(k, v) for k, v in enumerate(message["speech"])])
        message["visited"].append(index)
        return speech
    return choice(message["speech"])

class MessageBot:
    def __init__(self, config: dict):
        config = list(config)
        for message in config:
            if "speech" in message and type(message["speech"]) is str:
                message["speech"] = [message["speech"]]
        self.config = config

    async def run(self):
        config = self.config

        minutes = 0
        while True:
            valid_messages = []
            for message in config:
                if (
                    ("after" not in message or message["after"] <= minutes) and
                    ("before" not in message or message["before"] >= minutes) and
                    (
                        "minimum_gap" not in message or 
                        "last" not in message or
                        (minutes - message["last"]) > message["minimum_gap"]
                    ) and
                    _has_valid_speech(message)
                ):
                    valid_messages.append(message)

            if valid_messages and randint(0, 2) == 0: # There is a 2/3 chance that nothing will be said each time.
                message = choice(valid_messages)
                message["last"] = minutes
                speak(_get_speech(message))

            await asyncio.sleep(60)
            minutes += 1