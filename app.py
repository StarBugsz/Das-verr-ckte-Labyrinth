from flask import Flask, jsonify, send_from_directory, request, session
import os
import asyncio
from websockets import serve
import mimetypes
import json
import threading

from player import Player
from lobby import Lobby
from game import Game
import server
from AIPlayer import AIPlayer
import time

player_ids = set()
players = dict()
lobbys = dict()
connections = dict()

def generate_id():
    id = os.urandom(6).hex()
    while id in player_ids:
        id = os.urandom(6).hex()
    player_ids.add(id)
    return id

def lobbys_json(): 
    temp = dict()
    for lobby in lobbys:
        if not lobbys[lobby].private and not lobbys[lobby].started:
            temp[lobby] = lobbys[lobby].get_json()
    return temp

async def handle_websocket(websocket):
    lobby = None
    path = websocket.request.path
    parts = path.strip('/').split('/')
    if parts[0] not in ['uid', 'name']:
        await websocket.close()
        return

    key = parts[0]
    if len(parts) > 1:
        value = parts[1]
    else:  
        value = None
    try:
        if key == 'uid':
            print(value)
            uid = value
            if uid not in players:
                print("websocket closed because uid not found in players")
                await websocket.close()
                return
            if not players[uid].lobby:
                print("websocket closed because lobby not found")
                await websocket.close()
                return
            if not lobbys[players[uid].lobby].started:
                await websocket.close()
                return
            lobby = lobbys[players[uid].lobby]
            str = json.dumps({"action": "connection", "type": "response", "status": "success", "message": {"name": players[uid].name, "number": players[uid].number, "color": players[uid].color}, "board":  lobbys[players[uid].lobby].game.get_game_state(), "treasure": players[uid].cards[0].name})
            await websocket.send(str)
            print(str)
            if lobby.game.current_player == players[uid].number:
                await websocket.send(json.dumps({"action": "turn", "type": "response", "status": "success", "message": lobby.game.find_reachable_tiles(players[uid])}))
        elif key == 'name':
            uid = generate_id()
            players[uid] = Player(uid)
            await websocket.send(json.dumps(uid))

        connections[uid] = websocket

        async for message in websocket:
            print(f"message received from {uid}: {message}")

            player = players[uid]
            if "set_username" in message:
                players[uid].name = message.split(":")[1]
                await websocket.send(json.dumps({"action": "set_playername", "type": "response", "status": "success", "message": {"uid": uid}}))

            elif message == "lobbys":
                await websocket.send(json.dumps({"action": "lobbys", "type": "response", "status": "success", "message": lobbys_json()}))

            elif "join_lobby" in message:
                link = message.split(":")[1]
                if link in lobbys:
                    if lobbys[link].add_player(players[uid]):
                        players[uid].lobby = link
                        lobby = lobbys[link]
                        await broadcast(json.dumps({"action": "join_lobby", "type": "response", "status": "success", "message": {"players": lobbys[link].get_players(), "host": lobbys[link].get_host()}}), lobby)
                    else:
                        await websocket.send(json.dumps({"action": "join_lobby", "type": "response", "status": "error", "message": "Lobby is full."}))
                else:
                    await websocket.send(json.dumps({"action": "join_lobby", "type": "response", "status": "error", "message": "Lobby not found."}))

            elif message == "get_lobby":
                await websocket.send(json.dumps({"action": "get_lobby", "type": "response", "status": "success", "message": {"players": lobbys[players[uid].lobby].get_players(), "host": lobbys[players[uid].lobby].get_host()}}))
                
            elif message == "create_lobby":
                lobby = Lobby(players[uid])
                while lobby.link in lobbys:
                    lobby = Lobby(players[uid])
                lobbys[lobby.link] = lobby
                players[uid].lobby = lobby.link
                await websocket.send(json.dumps({"action": "create_lobby", "type": "response", "status": "success", "message": {"link": lobby.link}}))
                for pl in players:
                    if players[pl].lobby == None:
                        try:
                            await connections[players[pl].id].send(json.dumps({"action": "lobbys", "type": "response", "status": "success", "message": lobbys_json()}))
                        except Exception as e:
                            print(f"Error: {e}")

            elif message == "get_player_moves":
                await websocket.send(json.dumps({"action": "get_player_moves", "type": "response", "status": "success", "message": lobby.game.pathfinder.find_reachable_tiles(player.position)}))

            elif message.startswith("move:"):
                if(players[uid].number == lobby.game.current_player):
                    if(lobby.game.tiled):
                        position_str = message.split(":")[1]
                        x, y = map(int, position_str.split(","))
                        position = (x, y)
                        result = lobby.game.move_player(player, position)
                        if(result["status"] == "success" or result["status"] == "won"):
                            await broadcast(json.dumps({"action": "move", "type": "response", "status": result["status"], "player": player.number, "message": result}), lobby)
                        else:
                            await websocket.send(json.dumps({"action": "move", "type": "response", "status": result["status"], "message": result}))
                        print(result)
                        player = lobby.game.players[lobby.game.current_player]
                        while(player.ai):
                            await asyncio.sleep(len(result["path"])*1.34)
                            print("AI move")
                            """
                            (first_insert_position, first_move_position,
                            second_insert_position, second_move_position) = player.decide_move()
                            result = lobby.game.insert_tile(first_insert_position)
                            (x, y) = first_insert_position
                            """
                            insertposition= player.decide_tile_insertion()
                            (x, y) = insertposition
                            
                            result= lobby.game.insert_tile(insertposition)
                            moveposition = player.decide_movetest()
                            await broadcast(json.dumps({"action": "set_tile", "type": "response", "status": "success", "message": {"x":x, "y":y}}), lobby)
                            await broadcast(json.dumps({"action": "insert_tile", "type": "response", "status": result["status"], "message": result}), lobby)
                            #result = lobby.game.move_AIplayer(player, first_move_position)
                            result = lobby.game.move_AIplayer(player, moveposition)
                            await asyncio.sleep(1)
                            await broadcast(json.dumps({"action": "move", "type": "response", "status": result["status"], "player": player.number, "message": result}), lobby)
                            player = lobby.game.players[lobby.game.current_player]
                            print("currentplayer: ", lobby.game.current_player)

                    else:
                        await websocket.send(json.dumps({"action": "move", "type": "response", "status": "error", "message": "Tile not inserted."}))
                    
                else: 
                    await websocket.send(json.dumps({"action": "move", "type": "response", "status": "error", "message": "It is not your turn."}))
                
                

            elif message.startswith("set_tile:"):
                if(players[uid].number != lobby.game.current_player):
                    await websocket.send(json.dumps({"action": "set_tile", "type": "response", "status": "error", "message": "It is not your turn."}))
                else:    
                    position_str = message.split(":")[1]
                    x, y = map(int, position_str.split(","))
                    position = (x, y)
                    if not (x in [0, 6] or y in [0, 6]):    # Einschiebeposition muss am Rand liegen
                        await websocket.send(json.dumps({"action": "set_tile", "type": "response", "status": "error", "message": "Invalid position."}))
                    else:
                        await broadcast(json.dumps({"action": "set_tile", "type": "response", "status": "success", "message": {"x":x, "y":y}}), lobby)
            elif message.startswith("insert_tile:"):
                if(not players[uid].number != lobby.game.current_player):
                    if(not lobby.game.tiled):
                        position_str = message.split(":")[1]
                        x, y = map(int, position_str.split(","))
                        position = (x, y)
                        result = lobby.game.insert_tile(position)
                        await broadcast(json.dumps({"action": "insert_tile", "type": "response", "status": result["status"], "message": result}), lobby)
                    else:
                        await websocket.send(json.dumps({"action": "insert_tile", "type": "response", "status": "error", "message": "Tile already inserted."}))
                else:
                    await websocket.send(json.dumps({"action": "insert_tile", "type": "response", "status": "error", "message": "It is not your turn."}))
                    
                

            elif message == "rotate90":
                lobby.game.current_tile.rotate_90_clockwise()
                await broadcast(json.dumps({"action": "rotate90", "type": "response", "status": "success", "message": {"rotation": "rotate"}}), lobby)

            elif message == "board":
                await websocket.send(json.dumps({"action": "board", "type": "response", "status": "success", "message": lobbys[players[uid].link].game.game_state()}))
            
            elif message == "start_game":
                if players[uid] != lobbys[players[uid].lobby].host:
                    await websocket.send(json.dumps({"action": "start_game", "type": "response", "status": "error", "message": "You are not the host of this lobby."}))
                else:
                    lobbys[players[uid].lobby].start()
                    for player in lobby.players:
                        if player.ai:
                            player.game = lobby.game
                    current_player = lobbys[players[uid].lobby].game.players[0]
                    game_started = True
                    await broadcast(json.dumps({"action": "start_game", "type": "response", "status": "success"}), lobby)

            elif message.startswith("settings"):
                type = message.split(":")[1]
                value = message.split(":")[2]
                if(lobbys[players[uid].lobby].host == players[uid]):
                    if(type == "size"):
                        lobbys[players[uid].lobby].fieldsize = int(value.split("x")[0])
                        await broadcast(json.dumps({"action": "settings", "type": "response", "status": "success", "message": {"size": value}}), lobby)
                    elif(type == "privateLobby"):
                        lobbys[players[uid].lobby].private = value
                        await broadcast(json.dumps({"action": "settings", "type": "response", "status": "success", "message": {"privateLobby": value}}), lobby)
                    elif(type == "lobbysize"):
                        lobbys[players[uid].lobby].size = int(value)
                        await broadcast(json.dumps({"action": "settings", "type": "response", "status": "success", "message": {"lobbysize": value}}), lobby)
            elif message == "add_ai_player":
                if(lobbys[players[uid].lobby].host == players[uid]):
                    id = generate_id()
                    aiplayer = AIPlayer(id)
                    lobbys[players[uid].lobby].add_player(aiplayer)
                    players[id] = aiplayer
                    aiplayer.lobby = players[uid].lobby
                    aiplayer.name = "KI"
                    #await broadcast(json.dumps({"action": "add_ai_player", "type": "response", "status": "success", "number": aiplayer.number, "name": aiplayer.name}), lobby)
                    await broadcast(json.dumps({"action": "get_lobby", "type": "response", "status": "success", "message": {"players": lobbys[players[uid].lobby].get_players(), "host": lobbys[players[uid].lobby].get_host()}}), lobby)
            elif message.startswith("kick_player:"):
                player_number = int(message.split(":")[1])
                if players[uid] == lobby.host:
                    if(lobby.remove_player(player_number)):
                            #await broadcast(json.dumps({"action": "kick_player", "type": "response", "status": "success", "message": {"kicked_player": player_number}}), lobby)
                            await broadcast(json.dumps({"action": "get_lobby", "type": "response", "status": "success", "message": {"players": lobbys[players[uid].lobby].get_players(), "host": lobbys[players[uid].lobby].get_host()}}), lobby)
                    else:
                        await websocket.send(json.dumps({"action": "kick_player", "type": "response", "status": "error", "message": "Player not found or not in lobby."}))
                else:
                    await websocket.send(json.dumps({"action": "kick_player", "type": "response", "status": "error", "message": "You are not the host of this lobby."}))
    finally:
        if(uid in connections):
            print("closing websocket "+ uid)
            del connections[uid]


async def broadcast(message, lobby):
    for player in lobby.players:
        try:
            await connections[player.id].send(message)
        except Exception as e:
            print(f"Error: {e}")
    

async def main():
    print("websocket server started")
    async with serve(handle_websocket, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever

def dummy(pla=1):
    # Define a fixed UID for the player
    player1 = Player("test0")
    players['test0'] = player1
    player1.name="Test0"
    # Create a lobby with a fixed link and add the player to the lobby
    fixed_link = "test"
    lobby = Lobby(player1)
    lobbys[lobby.link] = lobby
    lobby.size = pla
    for i in range(1, pla):
        fixed_uid = "test" + str(i)
    
        # Create a player with the fixed UID
        player = AIPlayer(fixed_uid)
        player.game = lobby.game
        players[fixed_uid] = player
        player.name = "Test"+str(i)
        lobby.add_player(player)
        player.lobby = lobby.link
    
    lobby.start()
    #player1.position = (3, 4)
    print(f"Dummy lobby created with {len(lobby.players)} players")
def run_server():
    server.run()
# Run the app
if __name__ == '__main__':
    dummy(2)
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    asyncio.run(main())
    exit()