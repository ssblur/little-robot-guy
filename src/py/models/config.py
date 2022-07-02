from types import NoneType
from typing import Dict, List, Optional, Union
from pydantic import Field
from pydantic.dataclasses import dataclass

@dataclass(frozen=True)
class TTSConfig:
    speech: List[str]
    animation: str
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
class StreamathonTimeSettings:
    follow: List[int]
    bits: List[int]
    subscription: List[int]
    rewards: Dict[str, List[int]]

@dataclass(frozen=True)
class StreamathonSettings:
    enabled: bool
    start_time: int
    time: StreamathonTimeSettings
    message_animation: str

@dataclass(frozen=True)
class Config:
    tts: List[TTSConfig]
    web_port: int
    twitch_username: str
    tts_rewards: List[TTSReward]
    viewer_enabled: bool = False
    streamathon_settings: StreamathonSettings = None

def parse(config: dict) -> Config:
    """Generates a Config from a dict

        Returns:
            A Config object corresponding to the dict passed in
    """
    return Config(**config)