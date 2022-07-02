"""
    A terrible general-purpose stream assistant.
    Built as fast as possible to run decently between other projects.
    Author: Patrick Emery
    Contact: info@pemery.co
"""
from dotenv import load_dotenv; 
load_dotenv(override = True)
from asyncio.windows_utils import Popen
from multiprocessing import Process, Queue, Value
from src.py import animation, messages, viewer, config, twitch_client


def main():
    animation_state = Value("i", 0)
    speak_queue = Queue()
    time_queue = Queue()

    processes = []
    messages_process = Process(target=messages.run, args=(animation_state, speak_queue))
    messages_process.start()
    processes.append(messages_process)

    animation_process = Process(target=animation.run, args=(animation_state, time_queue))
    animation_process.start()
    processes.append(animation_process)

    twitch_process = Process(target=twitch_client.run, args=(speak_queue, time_queue))
    twitch_process.start()
    processes.append(twitch_process)

    if config.main.viewer_enabled:
        viewer_process = Process(target=viewer.run)
        viewer_process.start()
        processes.append(viewer_process)

    print("All components have been started")
    print("Press enter to terminate.")
    input()
    print('Terminating...')
    for process in processes:
        process.terminate()

if __name__ == "__main__":
    main()
