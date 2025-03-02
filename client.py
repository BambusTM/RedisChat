import socket
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

# Updated HTML page with a sleek, modern chat UI design.
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sleek Messenger</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea, #764ba2);
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            width: 90%;
            max-width: 600px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            padding: 20px;
        }
        h1 {
            text-align: center;
            margin-bottom: 20px;
            font-weight: 300;
        }
        #chat {
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 8px;
            height: 300px;
            overflow-y: scroll;
            padding: 15px;
            margin-bottom: 20px;
            background: rgba(255, 255, 255, 0.05);
        }
        .message {
            margin-bottom: 10px;
            padding: 8px;
            border-radius: 6px;
            background: rgba(0, 0, 0, 0.3);
            transition: background 0.3s ease;
        }
        .message:hover {
            background: rgba(0, 0, 0, 0.5);
        }
        .input-group {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .input-group input[type="text"] {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 6px;
            font-size: 16px;
        }
        .input-group button {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            background-color: #6c5ce7;
            color: #fff;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s ease;
        }
        .input-group button:hover {
            background-color: #a29bfe;
        }
        .username-group {
            margin-bottom: 10px;
        }
        .username-group input[type="text"] {
            width: 100%;
            padding: 10px;
            border: none;
            border-radius: 6px;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Sleek Messenger</h1>
        <div class="username-group">
            <input type="text" id="username" placeholder="Enter your username">
        </div>
        <div id="chat"></div>
        <div class="input-group">
            <input type="text" id="messageInput" placeholder="Type your message here...">
            <button id="sendBtn">Send</button>
        </div>
    </div>
    <script>
        let ws;
        // Connect to the backend server's WebSocket endpoint
        function connect() {
            ws = new WebSocket("ws://localhost:8000/ws");
            ws.onopen = function() {
                console.log("Connected to server");
            };
            ws.onmessage = function(event) {
                // Parse the JSON data received from the server
                const data = JSON.parse(event.data);
                const chat = document.getElementById("chat");
                const messageElement = document.createElement("div");
                messageElement.classList.add("message");
                messageElement.textContent = data.username + ": " + data.message;
                chat.appendChild(messageElement);
                chat.scrollTop = chat.scrollHeight;
            };
            ws.onclose = function() {
                console.log("Disconnected from server, retrying in 1 second...");
                setTimeout(connect, 1000);
            };
        }
        connect();
        document.getElementById("sendBtn").onclick = function() {
            const username = document.getElementById("username").value || "Anonymous";
            const message = document.getElementById("messageInput").value;
            if (message) {
                const data = { "username": username, "message": message };
                ws.send(JSON.stringify(data));
                document.getElementById("messageInput").value = "";
            }
        };
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return HTMLResponse(content=html_content, status_code=200)

def find_free_port(start_port=5000, max_port=5100):
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free port found in the specified range.")

if __name__ == "__main__":
    port = find_free_port()
    print(f"Starting client server on port {port}")
    uvicorn.run("client:app", host="127.0.0.1", port=port)
