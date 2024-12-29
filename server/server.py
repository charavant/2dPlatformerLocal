import asyncio
import json
import uuid
import websockets
import time
from game_logic import GameState

TICK_RATE = 60     # physics updates per second
BROADCAST_RATE = 15  # how many times per second we broadcast state

game_state = GameState()
connected_players = {}

async def handler(websocket, path):
    player_id = str(uuid.uuid4())
    connected_players[player_id] = websocket
    game_state.add_player(player_id)

    # We won't broadcast immediately here. The broadcast loop handles it.

    try:
        async for message in websocket:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "MOVE":
                direction = data.get("direction")
                game_state.handle_move(player_id, direction)

            elif msg_type == "STOP_MOVE":
                axis = data.get("axis")
                game_state.stop_move(player_id, axis)

            elif msg_type == "ATTACK":
                angle = data.get("angle", None)
                game_state.handle_attack(player_id, angle)

            elif msg_type == "START_GAME":
                if game_state.can_start_game():
                    game_state.start_game()

    except websockets.exceptions.ConnectionClosed:
        print(f"Player {player_id} disconnected.")
    finally:
        if player_id in connected_players:
            del connected_players[player_id]
        game_state.remove_player(player_id)

async def game_loop():
    """ Physics update loop at TICK_RATE. """
    interval = 1 / TICK_RATE
    while True:
        start_time = time.perf_counter()
        # Update the game physics
        game_state.update_physics()
        elapsed = time.perf_counter() - start_time
        await asyncio.sleep(max(0, interval - elapsed))

async def broadcast_loop():
    """ Broadcast state to all players at BROADCAST_RATE. """
    interval = 1 / BROADCAST_RATE
    while True:
        state_json = json.dumps(game_state.to_dict())
        send_tasks = []
        for ws in connected_players.values():
            if not ws.closed:
                send_tasks.append(asyncio.create_task(ws.send(state_json)))
        if send_tasks:
            await asyncio.gather(*send_tasks)
        await asyncio.sleep(interval)

async def main():
    server = websockets.serve(handler, "0.0.0.0", 6789)
    print("Server starting on ws://0.0.0.0:6789")

    async with server:
        # Run both loops concurrently
        await asyncio.gather(
            game_loop(),
            broadcast_loop()
        )

if __name__ == "__main__":
    asyncio.run(main())
