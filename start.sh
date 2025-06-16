#!/bin/bash

# Start the backend server
cd backend
python3 kongchat_server.py &

# Start the frontend server
cd ../frontend
python3 -m http.server 8000 &

echo "KongChat is running!"
echo "Web client: http://localhost:8000"
echo "CLI client: python3 cli/kongchat_cli.py"
