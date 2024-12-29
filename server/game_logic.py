import time

class Player:
    def __init__(self, player_id):
        self.id = player_id
        self.x = 100
        self.y = 100
        self.lives = 3
        self.is_alive = True

class GameState:
    def __init__(self):
        self.players = {}
        self.game_started = False
        self.start_time = 0
        self.round_duration = 5 * 60  # 5 minutes in seconds
        self.first_player = None

    def add_player(self, player_id):
        player = Player(player_id)
        self.players[player_id] = player
        # If first_player not set, assign this one
        if not self.first_player:
            self.first_player = player_id

    def remove_player(self, player_id):
        if player_id in self.players:
            del self.players[player_id]

    def can_start_game(self):
        # For now, let the first connected player start the game
        return True

    def start_game(self):
        self.game_started = True
        self.start_time = time.time()

    def handle_move(self, player_id, direction):
        player = self.players.get(player_id)
        if not player or not self.game_started:
            return

        if direction == "left":
            player.x -= 5
        elif direction == "right":
            player.x += 5
        elif direction == "jump":
            # simplistic jump
            player.y -= 20

        # Very simple boundary checks (for an 800x600 "game world")
        if player.x < 0:
            player.x = 0
        if player.x > 800:
            player.x = 800
        if player.y < 0:
            player.y = 0
        if player.y > 600:
            player.y = 600

    def handle_attack(self, player_id):
        if not self.game_started:
            return
        attacker = self.players.get(player_id)
        if not attacker:
            return

        # Check if any player is near the attacker to reduce their life
        for pid, other in self.players.items():
            if pid != player_id and self._check_collision(attacker, other):
                other.lives -= 1
                if other.lives <= 0:
                    other.is_alive = False
                    self._respawn(other)

    def _respawn(self, player):
        # Simple respawn logic
        player.x = 50
        player.y = 50
        player.lives = 3
        player.is_alive = True

    def _check_collision(self, p1, p2):
        # Very simplistic collision check
        return (abs(p1.x - p2.x) < 30) and (abs(p1.y - p2.y) < 30)

    def to_dict(self):
        # End the game if the round duration has passed
        if self.game_started and (time.time() - self.start_time >= self.round_duration):
            self.game_started = False

        return {
            "gameStarted": self.game_started,
            "timeRemaining": max(
                0, 
                self.round_duration - int(time.time() - self.start_time)
            ) if self.game_started else 0,
            "players": {
                pid: {
                    "x": p.x,
                    "y": p.y,
                    "lives": p.lives,
                    "isAlive": p.is_alive
                } for pid, p in self.players.items()
            }
        }
