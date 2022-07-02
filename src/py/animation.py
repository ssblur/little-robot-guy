"""
    A module for handling animation state management and messaging for the web view.
    Author: Patrick Emery
    Contact: info@pemery.co
"""
from datetime import datetime
from glob import glob
from queue import Empty
from time import time
from multiprocessing import Queue, Value
from os import getcwd, pathsep
from socketserver import TCPServer, BaseServer
from json import dumps
from . import config
from http.server import SimpleHTTPRequestHandler
from pydantic.json import pydantic_encoder
import asyncio

_animation_state: Queue = None
_time_queue: Queue = None
_time_data = [(time(), config.main.streamathon_settings.start_time)]

_animation_keys = list(config.animations.keys())
_animations = dumps(config.animations, default=pydantic_encoder).encode("utf-8")

class AnimationStateNotFound(Exception):
    """An error raised when attempting to set an animation state that does not exist."""
    def __init__(self, statename, *args: object) -> None:
        super().__init__(f"State {statename} was not found.\nValid states (based on config/animations) are:\n\n" + "\n\t".join(config.animations.keys()), *args)

def set_state(key: str, animation_state: Value):
    """A helper for setting the animation state

        Params:
            key: The name of the animation state being set
            animation_state: The value of animation_state
    """
    if animation_state is not None:
        try:
            animation_state.value = _animation_keys.index(key)
        except ValueError:
            raise AnimationStateNotFound(key)

def get_state() -> str:
    if _animation_state is not None:
        return _animation_keys[_animation_state.value]

class StatusHandler(SimpleHTTPRequestHandler):
    _not_found = "Not Found".encode("utf-8")

    def __init__(self, request: bytes, client_address: tuple[str, int], server: BaseServer) -> None:
        super().__init__(request, client_address, server, directory = "src/js/public")

    def do_POST(self):
        if self.path == "/animations":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(_animations)
        elif self.path == "/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(dumps(get_state()).encode("utf-8"))
        elif self.path == "/time":
            if not config.main.streamathon_settings.enabled:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(dumps([]).encode("utf-8"))
                return
            global _time_data
            while True:
                try:
                    datum = _time_queue.get(False)
                    if datum is None: 
                        break
                except Empty:
                    break
                _time_data.append((time(), datum))
            _time_data = list(filter(lambda x: x[0] > (time() - 300), _time_data))
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(dumps(_time_data).encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(self._not_found)
        self.last_path = self.path
    
    def log_message(self, *args, **kwargs):
        if hasattr(self, 'path') and (self.path in ["/status", "/time"]):
            return
        return super().log_message(*args, **kwargs)
        

def run(state, queue):
    global _animation_state, _time_queue
    _animation_state = state
    _time_queue = queue
    with TCPServer(("", config.main.web_port), StatusHandler) as server:
        server.serve_forever()