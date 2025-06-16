# Troubleshooting


### File: `INSTALL.sh`

```bash
#!/bin/bash

echo "Installing KongChat v1.0..."

# Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip npm
pip3 install websockets pycryptodome

# Install Node.js for optional future features (like voice processing)
curl -fsSL https://deb.nodesource.com/setup_14.x | sudo -E bash -
sudo apt install -y nodejs

# Set up the database
cd backend
python3 -c "import sqlite3; conn = sqlite3.connect('users.db'); conn.close()"
cd ..

echo "Installation completed! Run ./start.sh to begin."
```

### File: start.sh

```bash
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
```
