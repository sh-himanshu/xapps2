__all__ = ["DEVICE"]

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass
class Device:
    android: Literal[9, 10, 11, 12]
    android_str: field(init=False)
    sdk: field(init=False)
    arch: Literal["armeabi-v7a", "arm64-v8a", "x86", "x86_64"] = "arm64-v8a"
    dpi: Literal[120, 160, 240, 320, 480] = 480

    def __post_init__(self):
        self.android_str = ["P", "Q", "R", "S"][self.android - 9]
        self.sdk = self.android + 19

    @classmethod
    def load_config(cls) -> "Device":
        device_conf = Path("device_config.json")
        if device_conf.is_file():
            with device_conf.open("r") as f:
                return cls(**json.load(f))
        else:
            return cls(11)


DEVICE = Device.load_config()
