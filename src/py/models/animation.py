from typing import List, Optional, Union
from pydantic.dataclasses import dataclass

@dataclass(frozen=True)
class TransformSettings:
    rotation: float = 0
    transform_x: float = 0 
    transform_y: float = 0
    offset_x: float = 0
    offset_y: float = 0

@dataclass(frozen=True)
class Layer:
    path: str
    transform: Optional[TransformSettings] = None

@dataclass(frozen=True)
class Frame:
    layers: List[Union[str, Layer]]
    frame_duration: float = 1
    transform: Optional[TransformSettings] = None

@dataclass(frozen=True)
class AnimationState:
    frames: List[Frame]
    transform: Optional[TransformSettings] = None

def parse(config: dict) -> List[AnimationState]:
    """Generates an AnimationState from a dict

        Returns:
            A list of AnimationStates corresponding with config information
    """
    results = {}
    for k, v in config.items():
        results[k] = AnimationState(**v)