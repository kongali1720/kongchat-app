from Crypto.Cipher import AES
import base64
import hashlib

def pad(s):
    return s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)

def unpad(s):
    return s[:-ord(s[len(s)-1:])]

def encrypt_message(message, key):
    key = hashlib.sha256(key.encode()).digest()
    message = pad(message)
    iv = b'kongchataesiv123'  # Should be random in production
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(message.encode())).decode()

def decrypt_message(encrypted, key):
    key = hashlib.sha256(key.encode()).digest()
    encrypted = base64.b64decode(encrypted)
    iv = encrypted[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(encrypted[16:])).decode()
