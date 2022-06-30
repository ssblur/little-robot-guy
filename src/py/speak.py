from enum import Enum
from threading import Lock
from . import animation
import asyncio
import pyttsx3
import tempfile

engine = pyttsx3.init()

def speak(message: str):
    """Says a message out loud
    
        Params: 
            message: The message to speak
    """
    engine.say(message)
    engine.runAndWait()
