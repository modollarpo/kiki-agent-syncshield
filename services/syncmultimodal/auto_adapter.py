import requests

def auto_adapt(asset_path, platforms, core_hook, caption):
    results = []
    for platform in platforms:
        if platform == "instagram":
            target_format = "vertical"
        elif platform == "linkedin":
            target_format = "widescreen"
        elif platform == "youtube":
            target_format = "widescreen"
        else:
            target_format = "square"
        payload = {
            "asset_path": asset_path,
            "target_format": target_format,
            "platform": platform,
            "core_hook": core_hook,
            "caption": caption
        }
        resp = requests.post("http://localhost:8009/adapt", json=payload)
        results.append(resp.json())
    return results

if __name__ == "__main__":
    # Example usage
    print(auto_adapt("test.jpg", ["instagram", "linkedin", "youtube"], "Amazing Product", "Check this out!"))
