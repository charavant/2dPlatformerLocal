# Local Multiplayer Prototype

This repository contains a simple local multiplayer prototype using a Python WebSocket server and an HTML/JS client.

## Prerequisites
- Python 3.7+ (tested with 3.8, 3.9, etc.)
- Node is **not** required, but you do need a modern web browser to open the client.
- All players/clients need to be on the same network if you want them to join your local server.

## 1. Install Dependencies

```bash
pip install -r server/requirements.txt
```

## 2. Run the Server

```bash
python server/server.py
```
You should see a message indicating the server started on `ws://0.0.0.0:6789`.

## 3. Run the Client

Open `client/index.html` in your web browser. For convenience:

- On the same machine running the server, set `serverUrl = "ws://localhost:6789"` in `main.js`.
- If you want other computers on the network to connect, replace `localhost` in `serverUrl` with the local IP of the machine running the server. For example:

```js
const serverUrl = "ws://192.168.1.10:6789";
```

Then each client opens the `index.html` file in a web browser, pointing to that server IP.

## 4. Controls
- **Left Arrow**: move left  
- **Right Arrow**: move right  
- **Up Arrow**: jump  
- **Space**: melee attack  

## 5. Start the Game
The first connected player can click "Start Game" to begin the 5-minute round.

## 6. Stopping the Server
To stop the server, press `Ctrl + C` in the terminal where it is running.

