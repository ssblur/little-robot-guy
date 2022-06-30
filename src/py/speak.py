import pyttsx3

engine = pyttsx3.init()

def speak(message):
    engine.say(message)
    engine.runAndWait()