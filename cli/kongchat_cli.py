import curses
import json
import websockets
import asyncio
from ascii_art import print_login_art
import sys

async def chat_client(stdscr):
    # Initialize colors
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)  # System message
    curses.init_pair(2, curses.COLOR_BLUE, -1)   # Self message
    curses.init_pair(3, curses.COLOR_YELLOW, -1) # Other message
    curses.init_pair(4, curses.COLOR_CYAN, -1)   # Input

    stdscr.clear()
    curses.curs_set(1)
    stdscr.refresh()

    # Login screen
    win = curses.newwin(20, 60, 0, 0)
    win.box()
    win.addstr(0, 2, "KongChat Login")
    win.addstr(2, 2, "Username: ")
    win.addstr(3, 2, "Password: ")
    win.refresh()

    # Get username and password
    username = ""
    password = ""
    win.move(2, 12)
    while True:
        ch = win.getch()
        if ch == 10:  # Enter
            break
        elif ch == curses.KEY_BACKSPACE:
            if username:
                username = username[:-1]
                win.addch(2, 12 + len(username), ' ')
                win.move(2, 12 + len(username))
        else:
            username += chr(ch)
            win.addch(2, 12 + len(username)-1, chr(ch))
    win.addstr(3, 12, "*" * len(password))
    win.move(3, 12)
    while True:
        ch = win.getch()
        if ch == 10:
            break
        elif ch == curses.KEY_BACKSPACE:
            if password:
                password = password[:-1]
                win.addch(3, 12 + len(password), ' ')
                win.move(3, 12 + len(password))
        else:
            password += chr(ch)
            win.addstr(3, 12, "*" * len(password))
            win.move(3, 12 + len(password))

    # Connect to server
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as websocket:
            # Send login
            await websocket.send(json.dumps({
                'type': 'login',
                'username': username,
                'password': password
            }))

            # Wait for login response
            response = await websocket.recv()
            data = json.loads(response)
            if data['type'] == 'system' and 'berhasil' in data['content']:
                stdscr.clear()
                stdscr.addstr(0, 0, f"Logged in as {username}. Press Ctrl+C to exit.", curses.color_pair(1))
                stdscr.refresh()
            else:
                stdscr.addstr(5, 0, "Login failed. Exiting...")
                stdscr.refresh()
                await asyncio.sleep(2)
                return

            # Input and output areas
            output_win = curses.newwin(curses.LINES-3, curses.COLS, 1, 0)
            input_win = curses.newwin(3, curses.COLS, curses.LINES-3, 0)
            input_win.box()
            input_win.addstr(0, 2, "Input")
            input_win.refresh()

            # Input and output tasks
            async def handle_input():
                input_buffer = ""
                while True:
                    input_win.addstr(1, 1, "> " + input_buffer + "_")
                    input_win.refresh()
                    ch = input_win.getch()
                    if ch == 10:  # Enter
                        if input_buffer.strip():
                            await websocket.send(json.dumps({
                                'type': 'message',
                                'content': input_buffer
                            }))
                            input_buffer = ""
                    elif ch == curses.KEY_BACKSPACE:
                        input_buffer = input_buffer[:-1]
                    else:
                        input_buffer += chr(ch)

            async def handle_output():
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    if data['type'] == 'message':
                        output_win.addstr(f"{data['sender']}: {data['content']}\n", 
                                          curses.color_pair(3) if data['sender'] != username else curses.color_pair(2))
                    else:
                        output_win.addstr(f"System: {data['content']}\n", curses.color_pair(1))
                    output_win.refresh()

            await asyncio.gather(handle_input(), handle_output())
    except Exception as e:
        stdscr.addstr(5, 0, f"Error: {str(e)}")
        stdscr.refresh()
        await asyncio.sleep(5)

def main():
    try:
        print_login_art()
        asyncio.run(curses.wrapper(chat_client))
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
