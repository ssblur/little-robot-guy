from types import NoneType
from typing import List, Optional, Union
from pydantic import Field
from pydantic.dataclasses import dataclass

@dataclass(frozen=True)
class TTSConfig:
    speech: List[str]
    after: Optional[float] = None
    before: Optional[float] = None
    minimum_gap: Union[float, NoneType] = None
    chance: float = 1
    can_repeat: bool = True

@dataclass(frozen=True)
class TTSReward:
    name: str
    animation: str

@dataclass(frozen=True)
class Config:
    tts: List[TTSConfig]
    web_port: int
    twitch_username: str
    tts_rewards: List[TTSReward]
    viewer_enabled: bool = False

def parse(config: dict) -> Config:
    """Generates a Config from a dict

        Returns:
            A Config object corresponding to the dict passed in
    """
    return Config(**config)