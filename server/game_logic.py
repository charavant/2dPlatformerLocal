import time
import random
import json
import os

GRAVITY = 0.6
JUMP_POWER = 12
MOVE_SPEED = 4
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 40

class Player:
    def __init__(self, player_id):
        self.id = player_id
        self.x = 100
        self.y = 100
        self.vx = 0
        self.vy = 0
        self.lives = 3
        self.is_alive = True
        self.facing = 0  # direction for attack
        self.state = "idle"  # can be "idle", "running", "jumping", "attacking"

class GameState:
    def __init__(self):
        self.players = {}
        self.game_started = False
        self.start_time = 0
        self.round_duration = 5 * 60  # 5 minutes
        self.first_player = None

        # Platforms from persistent file or generated
        self.platforms = []

    def add_player(self, player_id):
        player = Player(player_id)
        self.players[player_id] = player
        if not self.first_player:
            self.first_player = player_id

    def remove_player(self, player_id):
        if player_id in self.players:
            del self.players[player_id]

    def can_start_game(self):
        return True

    def start_game(self):
        self.game_started = True
        self.start_time = time.time()

        # Try loading an existing map first
        if os.path.exists("server/map.json"):
            with open("server/map.json", "r") as f:
                self.platforms = json.load(f)
            print("Loaded existing map from map.json")
        else:
            # Generate a random map, then save it
            self.platforms = self._generate_random_map(num_platforms=5)
            # Add a floor
            self.platforms.append({"x": 0, "y": 550, "w": 800, "h": 50})
            with open("server/map.json", "w") as f:
                json.dump(self.platforms, f)
            print("Generated new map and saved to map.json")

        # Reset players
        for p in self.players.values():
            p.x = 100
            p.y = 100
            p.vx = 0
            p.vy = 0
            p.lives = 3
            p.is_alive = True
            p.state = "idle"

    def handle_move(self, player_id, direction):
        player = self.players.get(player_id)
        if not player or not self.game_started:
            return

        if direction == "left":
            player.vx = -MOVE_SPEED
            player.state = "running"
            player.facing = 180  # face left
        elif direction == "right":
            player.vx = MOVE_SPEED
            player.state = "running"
            player.facing = 0  # face right
        elif direction == "jump":
            if self._is_on_ground(player):
                player.vy = -JUMP_POWER
                player.state = "jumping"

    def stop_move(self, player_id, axis):
        player = self.players.get(player_id)
        if not player or not self.game_started:
            return
        if axis == "x":
            player.vx = 0
            # if on ground -> idle, else -> jumping
            if self._is_on_ground(player):
                player.state = "idle"

    def handle_attack(self, player_id, angle=None):
        if not self.game_started:
            return
        attacker = self.players.get(player_id)
        if not attacker:
            return

        if angle is not None:
            attacker.facing = angle

        attacker.state = "attacking"

        # Check collisions with others
        for pid, other in self.players.items():
            if pid == player_id:
                continue
            if self._check_collision(attacker, other):
                other.lives -= 1
                if other.lives <= 0:
                    other.is_alive = False
                    self._respawn(other)

    def update_physics(self):
        """ Called at a fixed interval from the server game loop. """
        if not self.game_started:
            return

        for player in self.players.values():
            if not player.is_alive:
                continue

            # Apply gravity
            player.vy += GRAVITY

            # 1) Move horizontally
            old_x = player.x
            player.x += player.vx
            # Check horizontal collisions
            self._check_platform_collisions(player, horizontal=True)

            # 2) Move vertically
            old_y = player.y
            player.y += player.vy
            # Check vertical collisions
            self._check_platform_collisions(player, horizontal=False)

            # Boundaries
            if player.x < 0:
                player.x = 0
            elif player.x > 800 - PLAYER_WIDTH:
                player.x = 800 - PLAYER_WIDTH

            if player.y < 0:
                player.y = 0
            elif player.y > 600 - PLAYER_HEIGHT:
                player.y = 600 - PLAYER_HEIGHT

            # If velocity is near 0 horizontally, set to idle if on ground
            if abs(player.vx) < 0.001 and self._is_on_ground(player) and player.state != "attacking":
                player.state = "idle"

    def _check_platform_collisions(self, player, horizontal):
        """ 
        Adjust player's position if colliding with a platform.
        horizontal=True means we only check/fix horizontal overlap;
        horizontal=False means we only check/fix vertical overlap.
        """
        for plat in self.platforms:
            if self._rect_overlap(
                player.x, player.y, PLAYER_WIDTH, PLAYER_HEIGHT,
                plat["x"], plat["y"], plat["w"], plat["h"]
            ):
                # Overlapping
                if horizontal:
                    # Undo horizontal movement
                    if player.vx > 0:
                        # Moved right, so place at left edge of platform
                        player.x = plat["x"] - PLAYER_WIDTH
                    else:
                        # Moved left
                        player.x = plat["x"] + plat["w"]
                    player.vx = 0
                else:
                    # Undo vertical movement
                    if player.vy > 0:
                        # Moved down
                        player.y = plat["y"] - PLAYER_HEIGHT
                    else:
                        # Moved up
                        player.y = plat["y"] + plat["h"]
                    player.vy = 0

    def _is_on_ground(self, player):
        """ Check if the bottom of the player is on top of a platform or floor """
        # If at bottom boundary
        if player.y >= 600 - PLAYER_HEIGHT:
            return True

        player_bottom = player.y + PLAYER_HEIGHT
        for plat in self.platforms:
            # check if horizontally overlapping
            if not (player.x + PLAYER_WIDTH < plat["x"] or player.x > plat["x"] + plat["w"]):
                # check if player's bottom is exactly on top of platform
                # within some small threshold
                if abs(player_bottom - plat["y"]) < 2 and player_bottom <= plat["y"]:
                    return True
        return False

    def _check_collision(self, p1, p2):
        # simple bounding box
        return self._rect_overlap(p1.x, p1.y, PLAYER_WIDTH, PLAYER_HEIGHT,
                                  p2.x, p2.y, PLAYER_WIDTH, PLAYER_HEIGHT)

    def _rect_overlap(self, x1, y1, w1, h1, x2, y2, w2, h2):
        return not (x1 + w1 < x2 or x1 > x2 + w2 or
                    y1 + h1 < y2 or y1 > y2 + h2)

    def _respawn(self, player):
        player.x = 50
        player.y = 50
        player.vx = 0
        player.vy = 0
        player.lives = 3
        player.is_alive = True
        player.state = "idle"

    def _generate_random_map(self, num_platforms):
        """ Generate a random set of platforms. """
        platforms = []
        for _ in range(num_platforms):
            w = random.randint(100, 200)
            h = 20
            x = random.randint(0, 800 - w)
            y = random.randint(100, 400)
            platforms.append({"x": x, "y": y, "w": w, "h": h})
        return platforms

    def to_dict(self):
        # End the round if time is up
        if self.game_started and (time.time() - self.start_time >= self.round_duration):
            self.game_started = False

        return {
            "gameStarted": self.game_started,
            "timeRemaining": max(0, self.round_duration - int(time.time() - self.start_time))
            if self.game_started else 0,
            "players": {
                pid: {
                    "x": p.x,
                    "y": p.y,
                    "lives": p.lives,
                    "isAlive": p.is_alive,
                    "facing": p.facing,
                    "state": p.state
                }
                for pid, p in self.players.items()
            },
            "platforms": self.platforms
        }
