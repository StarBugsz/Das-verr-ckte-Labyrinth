import random
import copy
from pathfinder import Pathfinder
from player import Player
import json
from AIPlayer import AIPlayer

class Game:

    # Konstruktor initialisiert neues Spielfeld, Schatzkarten und Spieler der Klasse
    def __init__(self, players: list[Player], board_size=7):
        self.board_size = board_size
        if board_size not in {5, 7, 9}:
            raise ValueError(f"Unsupported board size: {board_size}")
        self.board = [[None for _ in range(board_size)] for _ in range(board_size)]  # Board-Initialisierung 7x7 Matrix (leeres Feld) 
        self.players = self.initialize_players(players)    # initialisiert Spieler
        self.current_tile = None    # speichert eine Gaengekarte, die spaeter zum Einschieben im Feld genutzt wird
        self.setup_fixed_tiles()    # feste Kacheln auf Spielfeld initialisieren
        self.setup_loose_tiles()    # lose Kacheln auf Spielfeld initialisieren
        self.treasure_cards = self.create_treasure_deck()   # erstellt Schatzkarten und mischt diese
        self.distribute_treasure_cards(self.players, self.treasure_cards) # verteilt Karten an die Spieler
        self.pathfinder = Pathfinder(self.board)  # PathFinder initialisieren
        self.current_player = 0 # aktueller Spieler
        self.tiled = False  # gibt an, ob eine Kachel eingeschoben wurde

    def initialize_players(self, players):
        start_positions = {
            5: [(0, 0), (0, 4), (4, 0), (4, 4)],
            7: [(0, 0), (0, 6), (6, 0), (6, 6)],
            9: [(0, 0), (0, 8), (8, 0), (8, 8)]
        }
        positions = start_positions[self.board_size]
        for i, player in enumerate(players):
            player.position = positions[i]
            player.start_position = positions[i]
            if player.ai:
                player.game = self
        return players
    
    def setup_fixed_tiles(self):
        fixed_tiles_by_size = {
            5: {
                (0, 0): Tile(['bottom', 'right']),  # Obere linke Ecke
                (0, 4): Tile(['bottom', 'left']),   # Obere rechte Ecke
                (4, 0): Tile(['top', 'right']),     # Untere linke Ecke
                (4, 4): Tile(['top', 'left']),      # Untere rechte Ecke
                (2, 0): Tile(['top', 'bottom', 'right'], 'map'),  # T-Kachel links
                (2, 2): Tile(['bottom', 'right', 'left']),  # T-Kachel rechts
                (2, 4): Tile(['top', 'bottom', 'left'], 'crown'),  # T-Kachel rechts
                (0, 2): Tile(['bottom', 'right', 'left'], 'book'),  # T-Kachel oben
                (4, 2): Tile(['top', 'right', 'left'], 'treasure_chest'),  # T-Kachel unten
            },
            7: {
                (0, 0): Tile(['bottom', 'right']),   # Obere linke Ecke
                (0, 6): Tile(['bottom', 'left']),    # Obere rechte Ecke
                (6, 0): Tile(['top', 'right']),      # Untere linke Ecke
                (6, 6): Tile(['top', 'left']),       # Untere rechte Ecke
                (0, 2): Tile(['bottom', 'right', 'left'], 'book'),  # T-Kachel oben
                (0, 4): Tile(['bottom', 'right', 'left'], 'money_bag'),  # T-Kachel oben
                (2, 0): Tile(['top', 'bottom', 'right'], 'map'),   # T-Kachel links
                (2, 2): Tile(['top', 'bottom', 'right'], 'crown'),   # T-Kachel rechts
                (2, 4): Tile(['bottom', 'right', 'left'], 'keys'),  # T-Kachel unten
                (2, 6): Tile(['top', 'bottom', 'left'], 'skull'),    # T-Kachel links
                (4, 0): Tile(['top', 'bottom', 'right'], 'ring'),   # T-Kachel rechts
                (4, 2): Tile(['top', 'right', 'left'], 'treasure_chest'),     # T-Kachel oben
                (4, 4): Tile(['top', 'bottom', 'left'], 'mosaic'),    # T-Kachel links
                (4, 6): Tile(['top', 'bottom', 'left'], 'sword'),    # T-Kachel links
                (6, 2): Tile(['top', 'right', 'left'], 'candlestick'),     # T-Kachel oben
                (6, 4): Tile(['top', 'right', 'left'], 'helmet'),     # T-Kachel oben
            },
            9: {
                (0, 0): Tile(['bottom', 'right']),   # Obere linke Ecke
                (0, 8): Tile(['bottom', 'left']),    # Obere rechte Ecke
                (8, 0): Tile(['top', 'right']),      # Untere linke Ecke
                (8, 8): Tile(['top', 'left']),       # Untere rechte Ecke
                (0, 2): Tile(['bottom', 'right', 'left'], 'book'),
                (0, 4): Tile(['bottom', 'right', 'left'], None),  # Keine Schatzkachel
                (0, 6): Tile(['bottom', 'right', 'left'], 'money_bag'),
                (2, 0): Tile(['top', 'bottom', 'right'], 'map'),
                (4, 0): Tile(['top', 'bottom', 'right'], None),  # Keine Schatzkachel
                (6, 0): Tile(['top', 'bottom', 'right'], 'crown'),
                (8, 2): Tile(['top', 'right', 'left'], None),  # Keine Schatzkachel
                (8, 4): Tile(['top', 'right', 'left'], 'keys'),
                (8, 6): Tile(['top', 'right', 'left'], 'skull'),
                (2, 8): Tile(['top', 'bottom', 'left'], 'ring'),
                (4, 8): Tile(['top', 'bottom', 'left'], None),  # Keine Schatzkachel
                (6, 8): Tile(['top', 'bottom', 'left'], 'treasure_chest'),
                (2, 2): Tile(['top', 'bottom', 'right'], None),  # Keine Schatzkachel
                (2, 4): Tile(['top', 'bottom', 'left'], None),
                (2, 6): Tile(['top', 'right', 'left'], None),  # Keine Schatzkachel
                (4, 2): Tile(['top', 'bottom', 'right'], 'mosaic'),
                (4, 4): Tile(['top', 'right', 'left'], None),  # Keine Schatzkachel
                (4, 6): Tile(['top', 'bottom', 'left'], 'sword'),
                (6, 2): Tile(['top', 'right', 'left'], None),  # Keine Schatzkachel
                (6, 4): Tile(['top', 'bottom', 'left'], 'candelestick'),
                (6, 6): Tile(['top', 'bottom', 'right'], 'helmet'),
            }
        }

        fixed_tiles = fixed_tiles_by_size[self.board_size]
        # Platziert die fest eingebauten Kacheln auf dem Spielfeld
        for position, tile in fixed_tiles.items():
            x, y = position
            self.board[x][y] = tile

    def setup_loose_tiles(self):
        # Schatzlisten für verschiedene Spielfeldgrößen
        treasures_7x7_9x9 = ['lizard', 'butterfly', 'bug', 'mouse', 'owl', 'spider', 
                            'ghost', 'dragon', 'bat', 'genie', 'devil', 'magician']
        treasures_5x5 = treasures_7x7_9x9[:6]  # Nur die ersten 6 Schätze für 5x5
        # Wähle die Schätze basierend auf der Spielfeldgröße
        if self.board_size == 7 or self.board_size == 9:
            treasures = treasures_7x7_9x9
        elif self.board_size == 5:
            treasures = treasures_5x5
        else:
            raise ValueError("Unsupported board size!")

        # Berechnung der benötigten losen Kacheln
        if self.board_size == 5:
            num_corner_tiles = 9  # Beispiel: 9 Eckkacheln
            num_t_tiles = 5        # Beispiel: 5 T-Kacheln
            num_straight_tiles = 3
        elif self.board_size == 7:
            num_corner_tiles = 16  # Beispiel: 16 Eckkacheln
            num_t_tiles = 6       # Beispiel: 6 T-Kacheln
            num_straight_tiles = 12
        elif self.board_size == 9:
            num_corner_tiles = 26  # Beispiel: 26 Eckkacheln
            num_t_tiles = 11       # Beispiel: 11 T-Kacheln
            num_straight_tiles = 20

        # Verteilung der Schätze bei 5x5-Feld
        if self.board_size == 5:
            corner_treasures = treasures[:len(treasures) // 2]  # Erste Hälfte der Schätze für Eckkacheln
            t_treasures = treasures[len(treasures) // 2:]  # Zweite Hälfte der Schätze für T-Kacheln
        else:
            corner_treasures = treasures[:6]  # Erste 6 Schätze für Eckkacheln
            t_treasures = treasures[6:]  # Restliche Schätze für T-Kacheln

        # Erstellen der losen Kacheln
        loose_tiles = (
            [Tile(['top', 'right'], treasure) for treasure in corner_treasures] +  # Eckkacheln mit Schatz
            [Tile(['top', 'right']) for _ in range(num_corner_tiles - len(corner_treasures))] +  # Eckkacheln ohne Schatz
            [Tile(['top', 'right', 'left'], treasure) for treasure in t_treasures] +  # T-Kacheln mit Schatz
            [Tile(['top', 'right', 'left']) for _ in range(num_t_tiles - len(t_treasures))] +  # T-Kacheln ohne Schatz
            [Tile(['top', 'bottom']) for _ in range(num_straight_tiles)]  # Gerade Kacheln (immer ohne Schatz)
        )

        # Zufällige Reihenfolge und Auswahl der aktuellen Kachel
        random.shuffle(loose_tiles)
        self.current_tile = loose_tiles.pop()  # Entfernt eine Kachel für das Einschieben

        # Drehe jede Kachel in loose_tiles zufällig
        for tile in loose_tiles:
            tile.rotate_random()

        # Platzieren der losen Kacheln auf freien Feldern
        free_positions = [(i, j) for i in range(self.board_size) for j in range(self.board_size) if self.board[i][j] is None]
        for i, (x, y) in enumerate(free_positions):
            if i < len(loose_tiles):
                self.board[x][y] = loose_tiles[i]

    # Erstellen und Mischen der Schatzkarten
    def create_treasure_deck(self):
        treasure_names_7x7_9x9 = [
            "sword", "map", "lizard", "mouse", "candlestick", "book", "money_bag",
            "devil", "mosaic", "magician", "helmet", "owl", "bat", "spider", "bug", 
            "crown", "skull", "dragon", "keys", "treasure_chest", "genie", "butterfly", 
            "ring", "ghost"
        ]
        treasure_names_5x5 = [
        'lizard', 'butterfly', 'bug', 'mouse', 'owl', 'spider', 'map', 'book', 'crown', 'treasure_chest'
        ]
        # Wähle das richtige Array basierend auf der Spielfeldgröße
        if self.board_size == 5:
            treasure_names = treasure_names_5x5
        elif self.board_size == 7 or self.board_size == 9:
            treasure_names = treasure_names_7x7_9x9
        deck = [TreasureCard(name) for name in treasure_names]
        random.shuffle(deck)
        return deck
        
    # Testfunktion zum anzeigen des Spielfeldes 
    def display_board(self):
        board_str = "["
        for row in self.board:
            row_str = str([[tile.connections, tile.treasure] if tile else None for tile in row])
            board_str += row_str + ","
            board_str = board_str[:-1]
            board_str += "]"
        return board_str
        
    # Funktion zum Verteilen der Schatzkarten an Spieler
    def distribute_treasure_cards(self, players, deck):
        num_cards_per_player = len(deck) // len(players)    # Anzahl der Schatzkarten pro Spieler ohne Rest
        for player in players:
            player.cards = [deck.pop() for _ in range(num_cards_per_player)]    # entfernt letzte Karte aus Deck und uebergibt es Spieler 
    
    def find_reachable_tiles(self, player): # findet alle erreichbaren Kacheln von Spielerposition 
        reachable_tiles, paths = self.pathfinder.find_reachable_tiles(player.position)
        return [{"row": tile[0], "col": tile[1]} for tile in reachable_tiles]
    
    def move_player(self, player, new_position): # bewegt Spieler auf neues Feld
        print(player.position)
        if not player == self.players[self.current_player]: # Spieler muss an der Reihe sein
            return {"status": "failed", "message": "Nicht der aktuelle Spieler"}
        if not player:
            return {"action": "move", "player": player, "status": "failed", "message": "Spieler nicht gefunden"}  # Fehlermeldung, falls kein Spieler
        
        # alle erreichbaren Kacheln + zugehörige Pfade
        reachable_tiles, paths = self.pathfinder.find_reachable_tiles(player.position) # alle erreichbaren Kacheln von aktueller Position
        
        # Spieler bewegen
        if new_position not in reachable_tiles:
            print("Position nicht erreichbar " + str(reachable_tiles)) 
            return {"status": "failed", "message": "Position nicht erreichbar"}

        self.tiled = False  # Kachel wurde nicht eingeschoben
        player.position = new_position
        x, y = new_position
        path_to_new_position = paths[new_position]  # Pfad zur neuen Position
        self.current_player = (self.current_player + 1) % len(self.players) # naechster Spieler ist an der Reihe
        total_players = len(self.players)
        next_player_index = (self.current_player + 1) % total_players 
        if self.players[next_player_index].cards and len(self.players[next_player_index].cards) > 0:
            next_treasure = self.players[next_player_index].cards[0].name
        else:
            next_treasure = None
        # Schatz auf aktueller Kachel überprüfen
        current_tile = self.board[player.position[0]][player.position[1]]
        if current_tile and current_tile.treasure:
            treasure = current_tile.treasure
            if player.cards and treasure == player.cards[0].name:
                treasure_found = player.cards.pop(0)  # Erste Schatzkarte von Stapel entfernen
                player.score += 1   # Spielerpunktzahl erhöhen (Schatz gefunden)
                if not player.cards:
                    player.has_collected_all_treasurecards = True  # Spieler hat alle Schätze gesammelt
                    return {"status": "success", 
                            "x": x, 
                            "y": y, 
                            "path": path_to_new_position, 
                            "treasure": treasure_found.name, 
                            "score": player.score, 
                            "next_player": self.players[self.current_player].number, 
                            "current_player": (self.players[self.current_player].number+3)%4,
                            "next_treasure": next_treasure
                        }
                return {"status": "success", 
                        "x": x, "y": y, 
                        "path": path_to_new_position, 
                        "treasure": treasure_found.name, 
                        "score": player.score, 
                        "next_player": self.players[self.current_player].number,
                        "current_player": (self.players[self.current_player].number+3)%4,
                        "next_treasure": next_treasure
                        }
        
        # Prüfen, ob der Spieler gewonnen hat (alle Schätze gesammelt und zurück am Startpunkt)
        if player.has_collected_all_treasurecards and player.position == player.start_position:
            other_players_info = [{"name": p.name, "score": p.score} for p in self.players if p != player]
            print(f"{player.name} hat alle Schätze gesammelt und gewonnen mit score {player.score}!")
            return {"status": "won",
                    "winner": player.name,
                    "score": player.score,
                    "other_players": other_players_info,
                    "next_player": self.players[self.current_player].number,
                    "current_player": (self.players[self.current_player].number+3)%4,
                    "next_treasure": next_treasure
                    }
        
        return {"status": "success", 
                "x": x,
                "y": y,
                "path": path_to_new_position,
                "treasure": None, "score": player.score, 
                "next_player": self.players[self.current_player].number,
                "current_player": (self.players[self.current_player].number+3)%4,
                "next_treasure": next_treasure
                }
    
    def move_AIplayer(self, player, new_position, callback=None):  # Bewegt den Spieler auf ein neues Feld
        if not player == self.players[self.current_player]:  # Spieler muss an der Reihe sein
            return {"status": "failed", "message": "Nicht der aktuelle Spieler"}
        if not player:
            return {"action": "move", "player": player, "status": "failed", "message": "Spieler nicht gefunden"}  # Fehlermeldung

        paths={}  # Speichert Pfade für KI-Spieler
        # Erreichbare Kacheln und zugehörige Pfade abrufen
        
        def store_paths(received_paths):
            nonlocal paths 
            paths = received_paths    
        
        reachable_tiles = self.pathfinder.find_reachable_tilesforAI(player.position, callback=store_paths)
        print("Erreichbare Kacheln: " + str(reachable_tiles))
        # Spieler bewegen
        if new_position not in reachable_tiles:
            print("Position nicht erreichbar du huso" + str(reachable_tiles))
            return {"status": "failed", "message": "Position nicht erreichbar"}

        self.tiled = False  # Kachel wurde nicht eingeschoben
        player.position = new_position
        x, y = new_position
        path_to_new_position = paths.get(new_position, [])  # Falls der Pfad nicht existiert, gib eine leere Liste zurück
        print(f"Pfad zum neuen Feld {new_position}: {path_to_new_position}")
        # Nächster Spieler an der Reihe
        print("updating current player", self.current_player)
        self.current_player = (self.current_player + 1) % len(self.players)
        # Schatz auf aktueller Kachel überprüfen
        current_tile = self.board[player.position[0]][player.position[1]]
        if current_tile and current_tile.treasure:
            treasure = current_tile.treasure
            if player.cards and treasure == player.cards[0].name:
                player.cards.pop(0)  # Erste Schatzkarte entfernen
                player.score += 1  # Punktzahl erhöhen

                if not player.cards:
                    player.has_collected_all_treasurecards = True  # Spieler hat alle Schätze gesammelt
                    return {
                        "status": "success",
                        "x": x, "y": y,
                        "path": path_to_new_position,
                        "treasure": None if not player.cards else player.cards[0].name,
                        "score": player.score,
                        "next_player": self.players[self.current_player].number
                    }

                return {
                    "status": "success",
                    "x": x, "y": y,
                    "path": path_to_new_position,
                    "treasure": player.cards[0].name,
                    "score": player.score,
                    "next_player": self.players[self.current_player].number
                }

        # Prüfen, ob der Spieler gewonnen hat
        if player.has_collected_all_treasurecards and player.position == player.start_position:
            other_players_info = [{"name": p.name, "score": p.score} for p in self.players if p != player]
            return {
                "status": "won",
                "winner": player.name,
                "score": player.score,
                "other_players": other_players_info
            }

        return {
            "status": "success",
            "x": x, "y": y,
            "path": path_to_new_position,
            "treasure": None,
            "score": player.score,
            "next_player": self.players[self.current_player].number
        }
           
    def insert_tile(self, position):    # Schiebt Kachel in jeweiligen Gang ein
        x, y = position
        affected_players = []
        
        if not (x in [0, 6] or y in [0, 6]):    # Einschiebeposition muss am Rand liegen
            return {"status": "failed", "message": "Kachel muss am Rand liegen."}

        if isinstance(self.board[x][y], Tile) and self.is_fixed_tile((x, y)):   # Einschiebegang darf keine feste Kachel haben
            return {"status": "failed", "message": "Kachel kann nicht an Gaengen mit festen Kacheln eingeschoben werden."}
        self.tiled = True   # Kachel wurde eingeschoben
        # Richtung ermitteln (Einschieben von oben/unten oder links/rechts)
        if x == 0:  # Einschieben von oben
            result = self._shift_column(y, "down", affected_players)
        elif x == 6:  # Einschieben von unten
            result = self._shift_column(y, "up", affected_players)
        elif y == 0:  # Einschieben von links
            result = self._shift_row(x, "right", affected_players)
        elif y == 6:  # Einschieben von rechts
            result = self._shift_row(x, "left", affected_players)
        else:
            return {"status": "failed", "message": "Ungültige Einschiebeposition."}
        print("test " + str(affected_players))
        # Aktualisiere erreichbare Kacheln für alle Spieler
        for player in self.players:
            reachable_tiles=self.find_reachable_tiles(player)
            #print(reachable_tiles)
        return result

    def _shift_column(self, col, direction, affected_players):
        processed_positions = set()  # Speichert Positionen der bereits verarbeiteten Spieler
        
        if direction == "down":
            new_current_tile = self.board[6][col]  # Herausgeschobene Kachel speichern
            
            for player in self.players:
                if player.position == (6, col):  # Spieler, der herausgeschoben wird
                    player.position = (0, col)
                    affected_players.append(player)
                    processed_positions.add((0, col))  # Neue Position speichern
            
            for i in range(6, 0, -1):
                self.board[i][col] = self.board[i - 1][col]  # Nach unten verschieben
                for player in self.players:
                    if player.position == (i - 1, col) and (i - 1, col) not in processed_positions:
                        player.position = (i, col)
                        processed_positions.add((i, col))  # Speichert neue Position
            
            self.board[0][col] = self.current_tile  # Neue Kachel oben einschieben

        elif direction == "up":
            new_current_tile = self.board[0][col]  # Herausgeschobene Kachel speichern
            
            for player in self.players:
                if player.position == (0, col):  # Spieler, der herausgeschoben wird
                    player.position = (6, col)
                    affected_players.append(player)
                    processed_positions.add((6, col))  # Neue Position speichern
            
            for i in range(0, 6):
                self.board[i][col] = self.board[i + 1][col]  # Nach oben verschieben
                for player in self.players:
                    if player.position == (i + 1, col) and (i + 1, col) not in processed_positions:
                        player.position = (i, col)
                        processed_positions.add((i, col))  # Speichert neue Position
            
            self.board[6][col] = self.current_tile  # Neue Kachel unten einschieben

        self.current_tile = new_current_tile  # Herausgeschobene Kachel wird neue current_tile
        return {"status": "success", "new_current_tile": self.current_tile.to_dict(), "direction": direction, "index": col}

    def _shift_row(self, row, direction, affected_players):
        processed_positions = set()  # Speichert Positionen der bereits verarbeiteten Spieler

        if direction == "right":
            new_current_tile = self.board[row][6]  # Herausgeschobene Kachel speichern

            # Spieler, die herausgeschoben werden, zuerst behandeln
            for player in self.players:
                if player.position == (row, 6):  # Spieler, der herausgeschoben wird
                    player.position = (row, 0)
                    affected_players.append(player)
                    processed_positions.add((row, 0))  # Neue Position speichern

            # Verschiebung nach rechts
            for i in range(6, 0, -1):
                self.board[row][i] = self.board[row][i - 1]  # Nach rechts verschieben
                for player in self.players:
                    if player.position == (row, i - 1) and (row, i - 1) not in processed_positions:
                        player.position = (row, i)
                        processed_positions.add((row, i))  # Speichert neue Position

            self.board[row][0] = self.current_tile  # Neue Kachel links einschieben

        elif direction == "left":
            new_current_tile = self.board[row][0]  # Herausgeschobene Kachel speichern

            # Spieler, die herausgeschoben werden, zuerst behandeln
            for player in self.players:
                if player.position == (row, 0):  # Spieler, der herausgeschoben wird
                    player.position = (row, 6)
                    affected_players.append(player)
                    processed_positions.add((row, 6))  # Neue Position speichern

            # Verschiebung nach links
            for i in range(0, 6):
                self.board[row][i] = self.board[row][i + 1]  # Nach links verschieben
                for player in self.players:
                    if player.position == (row, i + 1) and (row, i + 1) not in processed_positions:
                        player.position = (row, i)
                        processed_positions.add((row, i))  # Speichert neue Position

            self.board[row][6] = self.current_tile  # Neue Kachel rechts einschieben

        self.current_tile = new_current_tile  # Herausgeschobene Kachel wird neue current_tile
        return {"status": "success", "new_current_tile": self.current_tile.to_dict(), "direction": direction, "index": row}

    def is_fixed_tile(self, position):
        # Gibt True zurück, wenn die Kachel an dieser Position fest eingebaut ist
        fixed_positions = [
            (0, 0), (0, 2), (0, 4), (0, 6),
            (2, 0), (2, 2), (2, 4), (2, 6),
            (4, 0), (4, 2), (4, 4), (4, 6),
            (6, 0), (6, 2), (6, 4), (6, 6)
        ]
        return position in fixed_positions
        
    def check_for_treasure(self, player): # ueberprueft, ob Spieler Schatzkarte gefunden hat
        current_tile = self.board[player.position[0]][player.position[1]]
        if current_tile and current_tile.treasure:
            treasure = current_tile.treasure
            if player.cards and treasure == player.cards[0].name:
                player.cards.pop(0)  # erste Schatzkarte von Stapel entfernen
                if not player.cards:
                    player.has_collected_all_treasurecards = True   # Spieler hat alles Schatzkarten gefunden
                    print(f"{player.name} hat alle Schätze gesammelt und gewonnen!")
                    return {"status": "won", "winner": player.name}
                return {"status": "success", "treasure": treasure}
        return {"status": "no_treasure"}

         
    def get_game_state(self): # gibt aktuellen Spielstand zurueck
        state = {
            "board": [[tile.to_dict() if tile else None for tile in row] for row in self.board],
            "players": [
                {
                    "name": player.name,
                    "number": player.number,
                    "position": player.position,
                    "cards": [card.name for card in player.cards]
                } for player in self.players
            ],
            "current_tile": self.current_tile.to_dict() if self.current_tile else None,
            "current_player": self.current_player
        }
        return state
    
    def find_treasure_position(self, treasure_name, board=None):
        board = board or self.board  # Verwende ein übergebenes Spielfeld oder das aktuelle Board
        for row in range(len(board)):  # Iteration über die Zeilen des Boards
            for col in range(len(board[row])):  # Iteration über die Spalten der Zeile
                tile = board[row][col]
                if tile and tile.treasure == treasure_name:  # Prüft, ob bestimmter Schatz auf der Kachel liegt
                    return (row, col)
        return None
  
    def simulate_tile_insertion(self, position, inserted_tile=None): # simuliert das Einschieben einer Kachel
        row, col = position
        simulated_board = copy.deepcopy(self.board)  # Tiefenkopie des Boards
        inserted_tile if inserted_tile else self.current_tile  # Benutze die angegebene Kachel oder die Standardkachel
        simulated_current_tile = None  # Lokale Kopie für die Simulation

        if row == 0:  # Oben
            removed_tile = simulated_board[-1][col]
            for r in range(len(simulated_board) - 1, 0, -1):
                simulated_board[r][col] = simulated_board[r - 1][col]
            simulated_board[0][col] = inserted_tile
        elif row == len(simulated_board) - 1:  # Unten
            removed_tile = simulated_board[0][col]
            for r in range(0, len(simulated_board) - 1):
                simulated_board[r][col] = simulated_board[r + 1][col]
            simulated_board[-1][col] = inserted_tile
        elif col == 0:  # Links
            removed_tile = simulated_board[row][-1]
            for c in range(len(simulated_board[row]) - 1, 0, -1):
                simulated_board[row][c] = simulated_board[row][c - 1]
            simulated_board[row][0] = inserted_tile
        elif col == len(simulated_board[0]) - 1:  # Rechts
            removed_tile = simulated_board[row][0]
            for c in range(0, len(simulated_board[row]) - 1):
                simulated_board[row][c] = simulated_board[row][c + 1]
            simulated_board[row][-1] = inserted_tile
        else:
            raise ValueError(f"Ungültige Einschiebe-Position: {position}")

        # Aktualisiere die Einschiebekachel für die Simulation
        simulated_current_tile = removed_tile

        return simulated_board, simulated_current_tile
    
    def save_paths(self,  paths):
        print("Speichere Pfade:")
        for tile, path in paths.items():
            print(f"{tile}: {path}")

# Klasse fuer alle Gaengekarten
class Tile:
    def __init__(self, connections, treasure = None):    
        self.connections = list(connections) # speichert die Verbindungen der Kachel als Liste 
        self.treasure = treasure    # Schatzname falls vorhanden
    
    def is_connected(self, direction):
        return direction in self.connections    # Prueft, ob gewaehlte Richtung offen ist
    
    def rotate_90_clockwise(self):  # Rotationsfunktion fuer Gangkarte zum Einschieben
        rotation_map = {
            'top': 'right',
            'right': 'bottom',
            'bottom': 'left',
            'left': 'top'
        }
        self.connections = [rotation_map[direction] for direction in self.connections]  # Aktualisiert die Verbindungen basierend auf der Drehung

    def rotate_random(self):
        rotations = random.randint(0, 3)  # 0 bis 3 Drehungen (0 = keine Drehung, 1 = 90 Grad, ...)
        for _ in range(rotations):
            self.rotate_90_clockwise()

    def to_dict(self):
        return {
            "connections": self.connections,
            "treasure": self.treasure
        }

class TreasureCard:
    def __init__(self, name):
        self.name = name  # Der Name des Schatzes

if(__name__ == "__main__"):
    players = [
        AIPlayer("KI-Spieler", game=None),
        Player("Spieler 1"),
    ]
    game = Game(players)
    # Spielreferenz für KI-Spieler setzen
    for player in players:
        if isinstance(player, AIPlayer):
            player.game = game
    player = players[0]  # KI
    #player1 = players[0]  # Spieler
    #player.play_turn()
    #state = game.get_game_state()
    #reachable_tiles_json = game.pathfinder.find_reachable_tiles(player.position)
    #print(reachable_tiles_json)
    #print("ttttt")
    reachable = game.pathfinder.find_reachable_tilesforAI((1, 1), callback=game.save_paths)
    print(reachable)
    #resul= game.move_AIplayer(player, (0, 1))
    #print(resul)
    #result = game.move_AIplayer(player, (0, 1))
    #print(result)
    