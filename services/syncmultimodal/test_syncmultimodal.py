import requests
import os

def test_adapt_image():
    # Prepare a test image (ensure test.jpg exists in the service directory)
    test_path = "test.jpg"
    if not os.path.exists(test_path):
        # Create a dummy image
        import cv2
        import numpy as np
        img = np.ones((1080, 1920, 3), dtype=np.uint8) * 255
        cv2.putText(img, "Test", (100, 500), cv2.FONT_HERSHEY_SIMPLEX, 10, (0,0,255), 20)
        cv2.imwrite(test_path, img)
    # Call the API
    payload = {
        "asset_path": test_path,
        "target_format": "vertical",
        "platform": "instagram",
        "core_hook": "Amazing Product",
        "caption": "Check this out!"
    }
    resp = requests.post("http://127.0.0.1:8009/adapt", json=payload)
    print("Adapt response:", resp.json())

if __name__ == "__main__":
    test_adapt_image()
