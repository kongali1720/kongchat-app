# backend/server/main.py
import asyncio
from quart import Quart, websocket
from auth import two_factor_auth
from e2ee import encrypt_message, decrypt_message

app = Quart(__name__)

# Database pengguna terenkripsi
users = EncryptedDB('encrypted.db')

@app.route('/register', methods=['POST'])
async def register():
    data = await request.get_json()
    # Verifikasi 2FA sebelum registrasi
    if two_factor_auth(data['phone']):
        user_id = users.create(data)
        return {'status': 'success', 'user_id': user_id}
    return {'status': '2FA failed'}, 401

@app.websocket('/chat')
async def chat():
    async with websocket() as ws:
        while True:
            encrypted = await ws.receive()
            # Dekripsi pesan
            message = decrypt_message(encrypted)
            
            # Proses pesan
            if message['type'] == 'text':
                # ... [pemrosesan pesan]
            
            # Enkripsi ulang sebelum broadcast
            encrypted_resp = encrypt_message(response)
            await ws.send(encrypted_resp)
