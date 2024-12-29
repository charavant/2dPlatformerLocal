import asyncio
import json
import uuid
import websockets
from game_logic import GameState

# Global GameState instance
game_state = GameState()

# Keep track of connected players: {player_id: websocket}
connected_players = {}

async def handler(websocket, path):
    # 1) Register new player
    player_id = str(uuid.uuid4())
    connected_players[player_id] = websocket
    game_state.add_player(player_id)
    # Send initial state to all players
    await broadcast_state()

    try:
        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "MOVE":
                # {type: "MOVE", direction: "left"/"right"/"jump"}
                game_state.handle_move(player_id, data["direction"])

            elif data["type"] == "ATTACK":
                # {type: "ATTACK"}
                game_state.handle_attack(player_id)

            elif data["type"] == "START_GAME":
                # Only allow the first player to start the game (or any logic you decide)
                if game_state.can_start_game():
                    game_state.start_game()

            # After handling, broadcast updated game state
            await broadcast_state()

    except websockets.ConnectionClosed:
        print(f"Player {player_id} disconnected.")
    finally:
        # Remove player from the game state and the connected list
        del connected_players[player_id]
        game_state.remove_player(player_id)
        await broadcast_state()

async def broadcast_state():
    state_json = json.dumps(game_state.to_dict())
    # Send state to all connected players
    if connected_players:
        await asyncio.wait([
            ws.send(state_json)
            for ws in connected_players.values()
        ])

async def main():
    async with websockets.serve(handler, "0.0.0.0", 6789):
        print("Server started on ws://0.0.0.0:6789")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
