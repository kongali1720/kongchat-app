import asyncio
import websockets
import json
import sqlite3
from datetime import datetime
import hashlib
import secrets

DB_FILE = "users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, created_at TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY, room TEXT, sender TEXT, content TEXT, timestamp TIMESTAMP)''')
    conn.commit()
    conn.close()

def register_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    salt = secrets.token_hex(16)
    hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
    try:
        c.execute("INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)",
                  (username, f"{hashed_password}:{salt}", datetime.now().isoformat()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        stored_password, salt = row.split(':')
        hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
        return hashed_password == stored_password
    return False

clients = {}
rooms = {
    "Umum": set(),
    "Teknologi": set(),
    "Game": set()
}

async def broadcast_user_list(room):
    if room in rooms:
        users = [client_id for client_id in rooms[room]]
        message = json.dumps({
            "type": "user_list",
            "users": users
        })
        for websocket in rooms[room]:
            await websocket.send(message)

async def chat_server(websocket, path):
    client_id = None
    current_room = None
    try:
        async for message in websocket:
            data = json.loads(message)
            if data['type'] == 'login':
                if authenticate_user(data['username'], data['password']):
                    client_id = data['username']
                    clients[websocket] = client_id
                    # Join the default room
                    current_room = "Umum"
                    rooms[current_room].add(websocket)
                    await websocket.send(json.dumps({
                        "type": "system",
                        "content": "Login berhasil!"
                    }))
                    await broadcast_user_list(current_room)
                else:
                    await websocket.send(json.dumps({
                        "type": "system",
                        "content": "Login gagal. Username atau password salah."
                    }))
            elif data['type'] == 'register':
                if register_user(data['username'], data['password']):
                    await websocket.send(json.dumps({
                        "type": "system",
                        "content": "Registrasi berhasil! Silakan login."
                    }))
                else:
                    await websocket.send(json.dumps({
                        "type": "system",
                        "content": "Registrasi gagal. Username sudah digunakan."
                    }))
            elif data['type'] == 'join_room':
                if current_room:
                    rooms[current_room].remove(websocket)
                current_room = data['room']
                rooms[current_room].add(websocket)
                await broadcast_user_list(current_room)
                await websocket.send(json.dumps({
                    "type": "system",
                    "content": f"Anda memasuki ruang: {current_room}"
                }))
            elif data['type'] == 'message' and client_id and current_room:
                # Save message to database
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("INSERT INTO messages (room, sender, content, timestamp) VALUES (?, ?, ?, ?)",
                          (current_room, client_id, data['content'], datetime.now().isoformat()))
                conn.commit()
                conn.close()
                # Broadcast to all in the room
                broadcast_data = {
                    "type": "message",
                    "sender": client_id,
                    "content": data['content'],
                    "timestamp": datetime.now().isoformat()
                }
                for client in rooms[current_room]:
                    await client.send(json.dumps(broadcast_data))
    finally:
        if websocket in clients:
            del clients[websocket]
        if current_room and websocket in rooms[current_room]:
            rooms[current_room].remove(websocket)
            if current_room:
                await broadcast_user_list(current_room)

async def main():
    init_db()
    async with websockets.serve(chat_server, "localhost", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
