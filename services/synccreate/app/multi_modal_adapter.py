"""
SyncMulti-Modal – Format-Aware Adapter
"""
from typing import Literal

def get_aspect_ratio(platform: str) -> str:
    if platform.lower() == "instagram":
        return "9:16"
    elif platform.lower() == "linkedin":
        return "16:9"
    elif platform.lower() == "youtube":
        return "4k"
    else:
        return "1:1"

def get_prompt_vibe(platform: str) -> str:
    if platform.lower() == "instagram":
        return "lifestyle, fast-paced, vertical"
    elif platform.lower() == "linkedin":
        return "professional, authoritative, horizontal"
    elif platform.lower() == "youtube":
        return "cinematic, high-impact, hook transitions"
    else:
        return "default"
