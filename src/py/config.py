import json
import sys
from .models import config, animation

class ConfigException(Exception):
    def __init__(self, name,  *args: object) -> None:
        super().__init__(f"Please set up {name}. Example is provided in ./example_config/{name}", *args)

try:
    with open("config/main.json", "r") as f:
        main = config.parse(json.load(f))
except FileNotFoundError:
    raise ConfigException("main.json")

try:
    with open("config/animations.json", "r") as f:
        animations = animation.parse(json.load(f))
except FileNotFoundError:
    raise ConfigException("animations.json")
