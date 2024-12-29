const serverUrl = "ws://localhost:6789"; 
let socket;
let gameState = {};
let mouseAngle = 0;

document.addEventListener("DOMContentLoaded", () => {
  // Load sprite images
  loadSprites();

  socket = new WebSocket(serverUrl);

  socket.onopen = () => {
    console.log("Connected to server.");
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    gameState = data;
  };

  socket.onclose = () => {
    console.log("Disconnected from server.");
  };

  // Keydown
  document.addEventListener("keydown", (e) => {
    switch (e.key) {
      case "ArrowLeft":
        socket.send(JSON.stringify({ type: "MOVE", direction: "left" }));
        break;
      case "ArrowRight":
        socket.send(JSON.stringify({ type: "MOVE", direction: "right" }));
        break;
      case "ArrowUp":
        socket.send(JSON.stringify({ type: "MOVE", direction: "jump" }));
        break;
      case " ":
        // Space to attack, send the current mouse angle
        socket.send(JSON.stringify({ type: "ATTACK", angle: mouseAngle }));
        break;
    }
  });

  // Keyup
  document.addEventListener("keyup", (e) => {
    if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
      socket.send(JSON.stringify({ type: "STOP_MOVE", axis: "x" }));
    }
  });

  // Mouse move for attack facing
  const canvas = document.getElementById("gameCanvas");
  canvas.addEventListener("mousemove", (e) => {
    if (!gameState.players) return;
    // For simplicity, assume the local player's the first in the dictionary
    const localPlayerId = Object.keys(gameState.players)[0];
    if (!localPlayerId) return;

    const localPlayer = gameState.players[localPlayerId];
    if (!localPlayer) return;

    const rect = canvas.getBoundingClientRect();
    const px = rect.left + localPlayer.x + 20; // player's center X
    const py = rect.top + localPlayer.y + 20; // player's center Y

    const dx = e.clientX - px;
    const dy = e.clientY - py;
    mouseAngle = (Math.atan2(dy, dx) * 180) / Math.PI;
  });

  // Start game button
  const startGameBtn = document.getElementById("startGameBtn");
  startGameBtn.addEventListener("click", () => {
    socket.send(JSON.stringify({ type: "START_GAME" }));
  });

  // Render loop
  gameLoop();
});

function gameLoop() {
  requestAnimationFrame(gameLoop);
  renderGame(gameState);
}
