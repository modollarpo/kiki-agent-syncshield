"""
SyncMulti-Modal™ – Asset Adaptation Service
Bridges creative and market with smart cropping, contextual rewrites, and codec optimization.
"""
# Diagnostic: catch and print import/startup errors
import sys
try:
    import cv2
    import os
    import subprocess
    from fastapi import FastAPI
    from pydantic import BaseModel
    from typing import List
except Exception as e:
    print(f"[Startup Error] {e}", file=sys.stderr)
    raise
import cv2
import os
import subprocess
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="SyncMulti-Modal Asset Adapter")


class AdaptRequest(BaseModel):
    asset_paths: list[str]  # Support batch processing
    target_format: str  # 'vertical', 'widescreen', 'square', 'story', 'reel', 'tiktok', etc.
    platform: str
    core_hook: str
    caption: str

import asyncio
from concurrent.futures import ThreadPoolExecutor

def platform_codec_and_ext(platform: str):
    platform = platform.lower()
    # Add more platforms as needed
    if platform == "youtube":
        return "libx265", ".mp4"
    elif platform in ["instagram", "tiktok", "facebook", "linkedin", "snapchat", "twitter", "story", "reel", "pinterest", "reddit", "whatsapp", "telegram", "wechat", "line", "viber", "tumblr", "vimeo", "medium", "quora", "discord", "mastodon", "threads", "substack", "bereal", "lemon8"]:
        return "libx264", ".mp4"
    else:
        return "libx264", ".mp4"

def adapt_single_asset(asset_path, req, ffmpeg_path, aspect_map, image_exts, video_exts):
    import mimetypes
    import numpy as np
    import cv2
    import os
    mime_type, _ = mimetypes.guess_type(asset_path)
    ext = os.path.splitext(asset_path)[1].lower()
    # Smart cropping logic
    aspect = aspect_map.get(req.target_format, (1, 1))
    img = cv2.imread(asset_path)
    if img is not None:
        h, w = img.shape[:2]
        target_w = int(h * aspect[0] / aspect[1]) if aspect[0] < aspect[1] else w
        target_h = int(w * aspect[1] / aspect[0]) if aspect[0] > aspect[1] else h
        cropped = cv2.resize(img, (target_w, target_h))
        output_path = f"adapted_{req.target_format}_{os.path.basename(asset_path)}"
        cv2.imwrite(output_path, cropped)
        # Contextual rewrite (extended platforms)
        p = req.platform.lower()
        if p == "linkedin":
            caption = f"{req.core_hook} | {req.caption} (Professional, Data-Driven)"
        elif p == "instagram":
            caption = f"{req.core_hook} 🚀 {req.caption} #trending"
        elif p == "youtube":
            caption = f"{req.core_hook}: {req.caption} (Cinematic)"
        elif p == "tiktok":
            caption = f"{req.core_hook} 🎵 {req.caption} #foryou"
        elif p == "facebook":
            caption = f"{req.core_hook} | {req.caption} (Social)"
        elif p == "snapchat":
            caption = f"{req.core_hook} 👻 {req.caption} #snap"
        elif p == "twitter":
            caption = f"{req.core_hook} 🐦 {req.caption} #viral"
        elif p == "story":
            caption = f"{req.core_hook} | {req.caption} (Story)"
        elif p == "reel":
            caption = f"{req.core_hook} | {req.caption} (Reel)"
        elif p == "pinterest":
            caption = f"{req.core_hook} 📌 {req.caption} #pinterest"
        elif p == "reddit":
            caption = f"{req.core_hook} 👽 {req.caption} #reddit"
        elif p == "whatsapp":
            caption = f"{req.core_hook} 💬 {req.caption} #whatsapp"
        elif p == "telegram":
            caption = f"{req.core_hook} ✈️ {req.caption} #telegram"
        elif p == "wechat":
            caption = f"{req.core_hook} 🟩 {req.caption} #wechat"
        elif p == "line":
            caption = f"{req.core_hook} 🟩 {req.caption} #line"
        elif p == "viber":
            caption = f"{req.core_hook} 📞 {req.caption} #viber"
        elif p == "tumblr":
            caption = f"{req.core_hook} 🌀 {req.caption} #tumblr"
        elif p == "vimeo":
            caption = f"{req.core_hook} 🎬 {req.caption} #vimeo"
        elif p == "medium":
            caption = f"{req.core_hook} ✍️ {req.caption} #medium"
        elif p == "quora":
            caption = f"{req.core_hook} ❓ {req.caption} #quora"
        elif p == "discord":
            caption = f"{req.core_hook} 🎮 {req.caption} #discord"
        elif p == "mastodon":
            caption = f"{req.core_hook} 🐘 {req.caption} #mastodon"
        elif p == "threads":
            caption = f"{req.core_hook} 🧵 {req.caption} #threads"
        elif p == "substack":
            caption = f"{req.core_hook} 📧 {req.caption} #substack"
        elif p == "bereal":
            caption = f"{req.core_hook} 📸 {req.caption} #bereal"
        elif p == "lemon8":
            caption = f"{req.core_hook} 🍋 {req.caption} #lemon8"
        else:
            caption = req.caption
        # Image handling
        if (mime_type and mime_type.startswith('image')) or ext in image_exts:
            return {
                "output_path": output_path,
                "caption": caption,
                "note": "Image adaptation complete. No ffmpeg encoding.",
            }
        # Video handling (image as input, but treat as video if needed)
        # Not typical, but could be extended here
        return {
            "output_path": output_path,
            "caption": caption,
            "note": "Unknown image/video type."
        }
    # If not an image, try as video
    if (mime_type and mime_type.startswith('video')) or ext in video_exts:
        codec, out_ext = platform_codec_and_ext(req.platform)
        encoded_path = f"encoded_{os.path.splitext(os.path.basename(asset_path))[0]}{out_ext}"
        cmd = [ffmpeg_path, "-y", "-i", asset_path, "-vcodec", codec, encoded_path]
        try:
            import subprocess
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            return {
                "error": f"ffmpeg failed: {e}",
                "stderr": e.stderr,
                "stdout": e.stdout,
                "cmd": ' '.join(cmd)
            }
        except Exception as e:
            return {"error": f"ffmpeg failed: {e}"}
        # Contextual rewrite (reuse above)
        if req.platform.lower() == "linkedin":
            caption = f"{req.core_hook} | {req.caption} (Professional, Data-Driven)"
        elif req.platform.lower() == "instagram":
            caption = f"{req.core_hook} 🚀 {req.caption} #trending"
        elif req.platform.lower() == "youtube":
            caption = f"{req.core_hook}: {req.caption} (Cinematic)"
        elif req.platform.lower() == "tiktok":
            caption = f"{req.core_hook} 🎵 {req.caption} #foryou"
        elif req.platform.lower() == "facebook":
            caption = f"{req.core_hook} | {req.caption} (Social)"
        elif req.platform.lower() == "snapchat":
            caption = f"{req.core_hook} 👻 {req.caption} #snap"
        elif req.platform.lower() == "twitter":
            caption = f"{req.core_hook} 🐦 {req.caption} #viral"
        elif req.platform.lower() == "story":
            caption = f"{req.core_hook} | {req.caption} (Story)"
        elif req.platform.lower() == "reel":
            caption = f"{req.core_hook} | {req.caption} (Reel)"
        else:
            caption = req.caption
        return {
            "output_path": encoded_path,
            "caption": caption,
            "codec": codec
        }
    # Unknown file type
    return {
        "error": f"Unsupported file type: {asset_path}",
        "mime_type": mime_type,
        "extension": ext
    }

async def adapt_asset(req: AdaptRequest):
    ffmpeg_path = "C:/xampp/htdocs/kiki_agent/ffmpeg/ffmpeg-8.0.1-essentials_build/bin/ffmpeg.exe"
    aspect_map = {
        "vertical": (9, 16),
        "widescreen": (16, 9),
        "square": (1, 1),
        "story": (9, 16),
        "reel": (9, 16),
        "tiktok": (9, 16),
    }
    image_exts = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
    video_exts = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
    results = []
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        tasks = [loop.run_in_executor(pool, adapt_single_asset, asset_path, req, ffmpeg_path, aspect_map, image_exts, video_exts) for asset_path in req.asset_paths]
        results = await asyncio.gather(*tasks)
    return {"results": results}
    # Find ffmpeg binary
    ffmpeg_path = "C:/xampp/htdocs/kiki_agent/ffmpeg/ffmpeg-8.0.1-essentials_build/bin/ffmpeg.exe"
    # Smart cropping logic
    input_path = req.asset_path
    output_path = f"adapted_{req.target_format}_{os.path.basename(input_path)}"
    aspect_map = {
        "vertical": (9, 16),
        "widescreen": (16, 9),
        "square": (1, 1)
    }
    aspect = aspect_map.get(req.target_format, (1, 1))
    if not os.path.isfile(input_path):
        return {"error": f"Input file does not exist: {input_path}"}
    img = cv2.imread(input_path)
    if img is None:
        return {"error": f"Invalid image/video path or unreadable file: {input_path}"}
    h, w = img.shape[:2]
    target_w = int(h * aspect[0] / aspect[1]) if aspect[0] < aspect[1] else w
    target_h = int(w * aspect[1] / aspect[0]) if aspect[0] > aspect[1] else h
    cropped = cv2.resize(img, (target_w, target_h))
    write_success = cv2.imwrite(output_path, cropped)
    log_msg = f"cv2.imwrite('{output_path}') success: {write_success}"
    print(log_msg)
    if not write_success or not os.path.isfile(output_path):
        return {"error": f"Failed to create adapted file: {output_path}", "log": log_msg}
        write_success = cv2.imwrite(output_path, cropped)
        log_msg = f"cv2.imwrite('{output_path}') success: {write_success}"
        print(log_msg)
        if not write_success or not os.path.isfile(output_path):
            return {"error": f"Failed to create output file: {output_path}", "log": log_msg}
    if req.platform.lower() == "linkedin":
        caption = f"{req.core_hook} | {req.caption} (Professional, Data-Driven)"
    elif req.platform.lower() == "instagram":
        caption = f"{req.core_hook} 🚀 {req.caption} #trending"
    elif req.platform.lower() == "youtube":
        caption = f"{req.core_hook}: {req.caption} (Cinematic)"
    else:
        caption = req.caption
    # Determine if input is image or video
    import mimetypes
    mime_type, _ = mimetypes.guess_type(output_path)
    ext = os.path.splitext(output_path)[1].lower()
    image_exts = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
    video_exts = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
    # Clean diagnostics: only log on error
    # Image handling
    if (mime_type and mime_type.startswith('image')) or ext in image_exts:
        return {
            "output_path": output_path,
            "caption": caption,
            "note": "Image adaptation complete. No ffmpeg encoding.",
        }
    # Video handling
    if (mime_type and mime_type.startswith('video')) or ext in video_exts:
        # Choose codec based on platform
        platform = req.platform.lower()
        if platform == "youtube":
            codec = "libx265"
            out_ext = ".mp4"
        elif platform == "instagram":
            codec = "libx264"
            out_ext = ".mp4"
        else:
            codec = "libx264"
            out_ext = ".mp4"
        encoded_path = f"encoded_{os.path.splitext(os.path.basename(output_path))[0]}{out_ext}"
        cmd = [ffmpeg_path, "-y", "-i", output_path, "-vcodec", codec, encoded_path]
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            return {
                "error": f"ffmpeg failed: {e}",
                "stderr": e.stderr,
                "stdout": e.stdout,
                "cmd": ' '.join(cmd)
            }
        except Exception as e:
            return {"error": f"ffmpeg failed: {e}"}
        return {
            "output_path": encoded_path,
            "caption": caption,
            "codec": codec
        }
    # Unknown file type
    return {
        "error": f"Unsupported file type: {output_path}",
        "mime_type": mime_type,
        "extension": ext
    }


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

# Allow direct execution for diagnostics
if __name__ == "__main__":
    import uvicorn
    print("Starting SyncMulti-Modal FastAPI service...")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
