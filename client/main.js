const serverUrl = "ws://localhost:6790"; // Adjust if running on a different IP/port
let socket;
let gameState = {};

document.addEventListener("DOMContentLoaded", () => {
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

  // Listen for key presses for movement
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
        // Space to attack
        socket.send(JSON.stringify({ type: "ATTACK" }));
        break;
    }
  });

  // Start game button
  const startGameBtn = document.getElementById("startGameBtn");
  startGameBtn.addEventListener("click", () => {
    socket.send(JSON.stringify({ type: "START_GAME" }));
  });

  // Begin rendering
  gameLoop();
});

function gameLoop() {
  requestAnimationFrame(gameLoop);
  renderGame(gameState);
}
