"""
    A terrible advertiser helper.
    Built as fast as possible to run on as many modern systems as possible with no pipfile, manual setup, or hard dependencies.
    Author: Patrick Emery
    Contact: info@pemery.co
"""
from dotenv import load_dotenv; 
load_dotenv(override = True)
from asyncio.windows_utils import Popen
from multiprocessing import Process, Queue, Value
from src.py import animation, messages, viewer, config, twitch_client

animation_state = Value("i", 0)
speak_queue = Queue()
def main():
    processes = []
    messages_process = Process(target=messages.run, args=(animation_state, speak_queue))
    messages_process.start()
    processes.append(messages_process)

    animation_process = Process(target=animation.run, args=(animation_state,))
    animation_process.start()
    processes.append(animation_process)

    twitch_process = Process(target=twitch_client.run, args=(speak_queue,))
    twitch_process.start()
    processes.append(twitch_process)

    if config.main.viewer_enabled:
        viewer_process = Process(target=viewer.run)
        viewer_process.start()
        processes.append(viewer_process)

    print("All components have been started")
    for process in processes:
        process.join()

if __name__ == "__main__":
    main()
