"""
    A terrible advertiser helper.
    Built as fast as possible to run on as many modern systems as possible with no pipfile, manual setup, or hard dependencies.
    Author: Patrick Emery
    Contact: info@pemery.co
"""
from asyncio.windows_utils import Popen
from multiprocessing import Process, Value
from src.py import animation, messages, viewer, config

animation_state = Value("i", 0)
def main():
    processes = []
    messages_process = Process(target=messages.run, args=(animation_state,))
    messages_process.start()
    processes.append(messages_process)

    animation_process = Process(target=animation.run, args=(animation_state,))
    animation_process.start()
    processes.append(animation_process)

    if config.main.viewer_enabled:
        viewer_process = Process(target=viewer.run)
        viewer_process.start()
        processes.append(viewer_process)

    print("All components have been started")
    for process in processes:
        process.join()

if __name__ == "__main__":
    main()
