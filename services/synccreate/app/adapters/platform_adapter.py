"""
SyncMulti-Modal – Platform-Specific Adapter
"""
from .multi_modal_adapter import get_aspect_ratio, get_prompt_vibe

class PlatformAdapter:
    def __init__(self, platform: str):
        self.platform = platform
        self.aspect_ratio = get_aspect_ratio(platform)
        self.vibe = get_prompt_vibe(platform)

    def adapt_prompt(self, base_prompt: str) -> str:
        return f"{base_prompt}, {self.vibe}, aspect ratio: {self.aspect_ratio}"

    def get_render_settings(self):
        if self.aspect_ratio == "9:16":
            return {"resolution": "1080x1920", "orientation": "vertical"}
        elif self.aspect_ratio == "16:9":
            return {"resolution": "1920x1080", "orientation": "horizontal"}
        elif self.aspect_ratio == "4k":
            return {"resolution": "3840x2160", "orientation": "horizontal"}
        else:
            return {"resolution": "1080x1080", "orientation": "square"}
