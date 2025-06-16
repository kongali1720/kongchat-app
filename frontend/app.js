document.addEventListener('DOMContentLoaded', () => {
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const messageContainer = document.getElementById('messageContainer');
    const themeToggle = document.getElementById('themeToggle');
    const emojiBtn = document.getElementById('emojiBtn');
    const emojiPicker = document.getElementById('emojiPicker');
    const voiceBtn = document.getElementById('voiceBtn');
    const roomList = document.getElementById('roomList');
    const userList = document.getElementById('userList');

    // WebSocket connection
    const socket = new WebSocket('ws://localhost:8765');

    // Sample emojis
    const emojis = ['😀', '😂', '😍', '😎', '👍', '👋', '🎉', '❤️', '🔥', '💯'];
    emojis.forEach(emoji => {
        const span = document.createElement('span');
        span.className = 'emoji';
        span.textContent = emoji;
        span.addEventListener('click', () => {
            messageInput.value += emoji;
        });
        emojiPicker.appendChild(span);
    });

    // Theme toggle
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('light-mode');
        const icon = themeToggle.querySelector('i');
        if (document.body.classList.contains('light-mode')) {
            icon.className = 'fas fa-sun';
            themeToggle.innerHTML = '<i class="fas fa-sun"></i> Mode Terang';
        } else {
            icon.className = 'fas fa-moon';
            themeToggle.innerHTML = '<i class="fas fa-moon"></i> Mode Gelap';
        }
    });

    // Emoji picker toggle
    emojiBtn.addEventListener('click', () => {
        emojiPicker.style.display = emojiPicker.style.display === 'grid' ? 'none' : 'grid';
    });

    // Voice message (simplified: just a button)
    voiceBtn.addEventListener('click', () => {
        alert('Fitur rekaman suara akan datang!');
    });

    // Room switching
    roomList.querySelectorAll('li').forEach(room => {
        room.addEventListener('click', () => {
            roomList.querySelectorAll('li').forEach(r => r.classList.remove('active'));
            room.classList.add('active');
            // In a real app, we would switch the WebSocket room
            messageContainer.innerHTML = '';
            addSystemMessage(`Anda memasuki ruang: ${room.textContent}`);
        });
    });

    // Send message
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', e => {
        if (e.key === 'Enter') sendMessage();
    });

    function sendMessage() {
        const message = messageInput.value.trim();
        if (message) {
            // Construct message object
            const messageObj = {
                type: 'message',
                content: message,
                sender: 'Anda', // This would be the actual username
                room: roomList.querySelector('.active').textContent,
                timestamp: new Date().toISOString()
            };

            // Display message immediately
            addMessage(messageObj, 'self');

            // Send to server
            socket.send(JSON.stringify(messageObj));

            messageInput.value = '';
            emojiPicker.style.display = 'none';
        }
    }

    // Receive messages
    socket.addEventListener('message', event => {
        const msg = JSON.parse(event.data);
        if (msg.type === 'message') {
            addMessage(msg, 'other');
        } else if (msg.type === 'user_list') {
            updateUserList(msg.users);
        }
    });

    function addMessage(msg, who) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${who}`;
        messageElement.innerHTML = `
            <span class="sender">${msg.sender}</span>
            <div class="content">${msg.content}</div>
            <span class="time">${formatTime(msg.timestamp)}</span>
        `;
        messageContainer.appendChild(messageElement);
        messageContainer.scrollTop = messageContainer.scrollHeight;
        
        // Play sound for other's messages
        if (who === 'other') {
            new Audio('assets/sounds/notification.mp3').play();
        }
    }

    function addSystemMessage(text) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message system';
        messageElement.innerHTML = `<div class="content">${text}</div>`;
        messageContainer.appendChild(messageElement);
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }

    function updateUserList(users) {
        userList.innerHTML = '';
        users.forEach(user => {
            const li = document.createElement('li');
            li.textContent = user;
            userList.appendChild(li);
        });
    }

    function formatTime(isoString) {
        const date = new Date(isoString);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    // Simulate initial system message
    addSystemMessage('Selamat datang di KongChat!');
});
