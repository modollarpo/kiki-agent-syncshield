import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def encrypt_aes256(plaintext: str, key: bytes) -> str:
    cipher = AES.new(key, AES.MODE_CFB)
    ct_bytes = cipher.encrypt(plaintext.encode())
    return base64.b64encode(cipher.iv + ct_bytes).decode()
