import json
import sys
from typing import Dict, List
from .models import config, animation

class ConfigException(Exception):
    def __init__(self, name,  *args: object) -> None:
        super().__init__(f"Please set up {name}. Example is provided in ./example_config/{name}", *args)

main: config.Config
try:
    with open("config/main.json", "r") as f:
        main = config.parse(json.load(f))
except FileNotFoundError:
    raise ConfigException("main.json")

animations: Dict[str, animation.AnimationState]
try:
    with open("config/animations.json", "r") as f:
        data = json.load(f)
        animations = animation.parse(data)
except FileNotFoundError:
    raise ConfigException("animations.json")

