// For demonstration, let's assume each sprite sheet has 4 frames
// wide, 1 frame tall. Frame size is 50x50 (just an example).
// We'll show how to pick the frame based on an animation counter.

const spriteSheets = {
  idle: {
    img: null,
    frames: 4,
    frameWidth: 50,
    frameHeight: 50
  },
  running: {
    img: null,
    frames: 6,
    frameWidth: 50,
    frameHeight: 50
  },
  jumping: {
    img: null,
    frames: 2,
    frameWidth: 50,
    frameHeight: 50
  },
  attacking: {
    img: null,
    frames: 3,
    frameWidth: 50,
    frameHeight: 50
  }
};

// We'll track an animation counter to cycle frames
let animCounter = 0;

function loadSprites() {
  // Example: load from client/assets/player/
  spriteSheets.idle.img = new Image();
  spriteSheets.idle.img.src = "assets/player/idle.png";

  spriteSheets.running.img = new Image();
  spriteSheets.running.img.src = "assets/player/run.png";

  spriteSheets.jumping.img = new Image();
  spriteSheets.jumping.img.src = "assets/player/jump.png";

  spriteSheets.attacking.img = new Image();
  spriteSheets.attacking.img.src = "assets/player/attack.png";
}

// Returns the current frame index for a given animation
function getAnimationFrame(state) {
  // For a stable animation speed, slow down by a factor (e.g., 10)
  const slowFactor = 10;
  const sheet = spriteSheets[state] || spriteSheets.idle;
  const frameCount = sheet.frames;
  const frame = Math.floor(animCounter / slowFactor) % frameCount;
  return frame;
}

function renderGame(state) {
  const canvas = document.getElementById("gameCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Optional: draw a background
  // let bg = new Image();
  // bg.src = "assets/background.png";
  // ctx.drawImage(bg, 0, 0, canvas.width, canvas.height);

  // Draw platforms
  if (state.platforms) {
    state.platforms.forEach((plat) => {
      // For a more polished look, draw a tile or repeated tiles
      // For simplicity, fillRect. 
      ctx.fillStyle = "darkgreen";
      ctx.fillRect(plat.x, plat.y, plat.w, plat.h);
    });
  }

  // Draw players
  if (state.players) {
    for (let pid in state.players) {
      const player = state.players[pid];
      if (!player.isAlive) continue;

      // Determine sprite based on state
      const sState = player.state || "idle";
      const sheet = spriteSheets[sState] || spriteSheets.idle;

      const frameIndex = getAnimationFrame(sState);
      const sx = frameIndex * sheet.frameWidth;
      const sy = 0;

      // Adjust for facing angle if we want to flip horizontally
      let flip = false;
      // If facing > 90 and < 270, assume facing left, or we can check player.vx < 0
      // or something simpler. We'll just do a naive check:
      if ((player.facing > 90 && player.facing < 270) || player.facing === 180) {
        flip = true;
      }

      ctx.save();
      if (flip) {
        ctx.translate(player.x + sheet.frameWidth, player.y);
        ctx.scale(-1, 1);
        ctx.drawImage(
          sheet.img,
          sx, sy, sheet.frameWidth, sheet.frameHeight,
          0, 0, sheet.frameWidth, sheet.frameHeight
        );
      } else {
        ctx.drawImage(
          sheet.img,
          sx, sy, sheet.frameWidth, sheet.frameHeight,
          player.x, player.y,
          sheet.frameWidth, sheet.frameHeight
        );
      }
      ctx.restore();

      // Display lives
      ctx.fillStyle = "white";
      ctx.font = "14px Arial";
      ctx.fillText(`Lives: ${player.lives}`, player.x, player.y - 10);
    }
  }

  // Show time remaining
  if (state.gameStarted) {
    ctx.fillStyle = "black";
    ctx.font = "20px Arial";
    ctx.fillText(`Time: ${state.timeRemaining}s`, 650, 30);
  } else {
    ctx.fillStyle = "red";
    ctx.font = "20px Arial";
    ctx.fillText("Game not started or round ended", 280, 300);
  }

  // Update animation counter
  animCounter++;
}
