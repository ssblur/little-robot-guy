from glob import glob
from multiprocessing import Value
from os import getcwd, pathsep
from socketserver import TCPServer, BaseServer
from json import dumps
from . import config
from http.server import SimpleHTTPRequestHandler
from pydantic.json import pydantic_encoder
import asyncio

_animation_state = None
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
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(self._not_found)
        self.last_path = self.path
    
    def log_message(self, *args, **kwargs):
        if hasattr(self, 'path') and self.path == "/status":
            return
        return super().log_message(*args, **kwargs)
        

def run(state):
    global _animation_state
    _animation_state = state
    with TCPServer(("", config.main.web_port), StatusHandler) as server:
        server.serve_forever()