"""
    A terrible advertiser helper.
    Built as fast as possible to run on as many modern systems as possible with no pipfile, manual setup, or hard dependencies.
    Author: Patrick Emery
    Contact: info@pemery.co
"""
import json
import sys
import asyncio
from src.py.messages import MessageBot

async def run():
    try:
        with open("config/main.json", "r") as f:
            config = json.load(f)
    except:
        print("Please set up config.json. Example is provided in config.example.json")
        sys.exit(1)

    tasks = []
    if "tts" in config:
        messages = MessageBot(config["tts"])
        tasks.append(messages.run())

    print("All valid components have been started")

    await asyncio.gather(*tasks)

def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()