import requests

# Example batch request for SyncMulti-Modal adaptation
url = "http://127.0.0.1:8009/adapt"
payload = {
    "asset_paths": [
        "test.jpg",           # Image
        "sample_video.mp4",  # Video
        "test2.png"          # Another image
    ],
    "target_format": "story",  # Try 'vertical', 'widescreen', 'square', 'story', 'reel', 'tiktok', etc.
    "platform": "tiktok",      # Try 'youtube', 'instagram', 'facebook', 'linkedin', 'snapchat', 'twitter', 'story', 'reel', etc.
    "core_hook": "Amazing Product",
    "caption": "Check this out!"
}

resp = requests.post(url, json=payload)
print("Batch Adapt Response:")
print(resp.json())
