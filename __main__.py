"""
    A terrible advertiser helper.
    Built as fast as possible to run on as many modern systems as possible with no pipfile, manual setup, or hard dependencies.
    Author: Patrick Emery
    Contact: info@pemery.co
"""
import asyncio
from src.py.messages import MessageBot
from src.py import config

async def run():
    tasks = []
    messages = MessageBot(config.main.tts)
    tasks.append(messages.run())

    print("All valid components have been started")

    await asyncio.gather(*tasks)

def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()
