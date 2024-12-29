function renderGame(state) {
    const canvas = document.getElementById("gameCanvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
  
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  
    // Draw all players
    if (state.players) {
      for (let pid in state.players) {
        const player = state.players[pid];
        if (player.isAlive) {
          // Example: draw a rectangle for each player
          ctx.fillStyle = "blue";
          ctx.fillRect(player.x, player.y, 30, 30);
  
          // Display lives above the player
          ctx.fillStyle = "white";
          ctx.font = "14px Arial";
          ctx.fillText(`Lives: ${player.lives}`, player.x, player.y - 10);
        }
      }
    }
  
    // Show time remaining
    if (state.gameStarted) {
      ctx.fillStyle = "black";
      ctx.font = "20px Arial";
      ctx.fillText(`Time: ${state.timeRemaining}s`, 700, 30);
    } else {
      ctx.fillStyle = "red";
      ctx.font = "20px Arial";
      ctx.fillText("Game not started or round ended", 280, 300);
    }
  }
  