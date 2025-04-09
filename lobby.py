import os
from game import Game
import json

class Lobby:
    def __init__(self, host):
        self.size = 4
        self.link = os.urandom(3).hex()
        self.host = host
        host.number = 0
        host.lobby = self.link
        self.players = [host]
        self.active = True # False when game ends
        self.started = False # True when game starts
        self.powerups = False
        self.game = None
        self.private = False
        self.fieldsize = 7

    def _find_free_number(self):
        number = 0
        for i in range(0, len(self.players)):
            for player in self.players:
                if player.number == i:
                    number += 1
                    break
        return number
            
    def add_player(self, player):
        if len(self.players) < self.size:
            player.number = self._find_free_number()
            self.players.append(player)
            return True
        return False
    
    def start(self):
        self.started = True
        self.game = Game(self.players)

    def get_players(self):
        temp = dict()
        for player in self.players:
            temp[player.number] = {"name": player.name, "color": player.color, "nummer": player.number, "position": player.position, "cards": player.get_treasure_cards(), "has_collected_all_treasurecards": player.has_collected_all_treasurecards, "start_position": player.start_position}
        return temp
    
    def remove_player(self, player_number):
        for player in self.players:
            if player.number == player_number:      
                self.players.remove(player)
                return True
        return False
          

    def get_host(self):
        return {"nummer": self.host.number, "name": self.host.name, "color": self.host.color}
    
    def get_json(self):
        return json.dumps({
            "size": self.size,
            "link": self.link,
            "host": self.get_host(),
            "players": self.get_players(),
            "active": self.active,
            "started": self.started
        })