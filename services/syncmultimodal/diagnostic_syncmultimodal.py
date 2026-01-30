import sys
import os
import traceback
import platform
import socket
import subprocess

print("=== SyncMulti-Modal FastAPI Diagnostic ===")
print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Current working directory: {os.getcwd()}")
print(f"Environment PATH: {os.environ.get('PATH')}")

# Check port availability
def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(("127.0.0.1", port))
        if result == 0:
            print(f"Port {port} is already in use.")
        else:
            print(f"Port {port} is available.")

check_port(8009)

# Check required packages
try:
    import fastapi
    import uvicorn
    import cv2
    import pydantic
    print("All required packages are installed.")
except Exception as e:
    print(f"[Import Error] {e}")
    traceback.print_exc()

# Try to start FastAPI app and capture output
try:
    print("Attempting to start FastAPI app with uvicorn.run(app, ...)")
    from app import app
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8009)
except Exception as e:
    print(f"[Startup Error] {e}")
    traceback.print_exc()

print("=== End Diagnostic ===")
