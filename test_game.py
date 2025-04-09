import unittest
from game import Game, Tile
from player import Player
from pathfinder import Pathfinder

class TestGameInitialization(unittest.TestCase):
    def test_board_initialization_7x7(self):
        players = [
        Player("Spieler 0"),
        Player("Spieler 1"),
        Player("Spieler 3"),
        Player("Spieler 4")
        ]
        # Initialisiere ein 5x5 Spiel
        game = Game(players, board_size=7)

        # Überprüfen, ob das Spielfeld die korrekte Größe hat
        self.assertEqual(len(game.board), 7)
        for row in game.board:
            self.assertEqual(len(row), 7)

        # Überprüfen, ob alle Kacheln korrekt platziert wurden
        filled_positions = sum(1 for row in game.board for tile in row if tile is not None)
        self.assertEqual(filled_positions, 49, "Das Spielfeld hat nicht die erwartete Anzahl an Kacheln!")

        # Überprüfen, ob `current_tile` gesetzt ist
        self.assertIsNotNone(game.current_tile, "Die aktuelle lose Kachel wurde nicht gesetzt!")

    def test_board_initialization_invalid_size(self):
        with self.assertRaises(ValueError):
            players = [
                Player("Spieler 0"),
                Player("Spieler 1"),
                Player("Spieler 2"),
                Player("Spieler 3")
                ]
            Game(players, board_size=4)  # Ungültige Spielfeldgröße

    def test_board_initialization_5x5(self):
        players = [
            Player("Spieler 0"),
            Player("Spieler 1"),
            Player("Spieler 2"),
            Player("Spieler 3")
        ]
        # Initialisiere ein 5x5 Spiel
        game = Game(players, board_size=5)

        # Rufe die Initialisierungslogik des Spielfelds auf
        game.get_game_state()

        # Überprüfen, ob das Spielfeld die korrekte Größe hat
        self.assertEqual(len(game.board), 5)
        for row in game.board:
            self.assertEqual(len(row), 5)

        # Überprüfen, ob alle Kacheln korrekt platziert wurden
        filled_positions = sum(1 for row in game.board for tile in row if tile is not None)
        self.assertEqual(filled_positions, 25, "Das Spielfeld hat nicht die erwartete Anzahl an Kacheln!")  # 5x5 - 1 lose Kachel

        # Überprüfen, ob `current_tile` gesetzt ist
        self.assertIsNotNone(game.current_tile, "Die aktuelle lose Kachel wurde nicht gesetzt!")
        
    def test_reachable_tiles_before_and_after_insert(self):
        players = [
            Player("Spieler 0"),
            Player("Spieler 1"),
        ]
        
        game = Game(players, board_size=7)
        game.initialize_players(players)
        
        player = players[0]
        initial_position = player.position

        # Ermittelbare Kacheln vor dem Einschieben
        pathfinder = Pathfinder(game.board)
        initial_reachable_tiles = pathfinder.find_reachable_tiles(initial_position)[0]

        # Kachel einschieben
        game.insert_tile((0, 1))  # Einschieben in die Spalte bei (0, 3)

        # Ermittelbare Kacheln nach dem Einschieben
        updated_reachable_tiles = pathfinder.find_reachable_tiles(player.position)[0]

        print("EinschbiebeKachel", game.current_tile.connections)
        print("Vor Einschieben erreichbar:", initial_reachable_tiles)
        print("Nach Einschieben erreichbar:", updated_reachable_tiles)
        
        self.assertNotEqual(initial_reachable_tiles, updated_reachable_tiles, "Die erreichbaren Kacheln sollten sich geändert haben.")
        self.assertIn(player.position, updated_reachable_tiles, "Die aktuelle Position des Spielers sollte weiterhin erreichbar sein.")

class TestTileInsertion(unittest.TestCase):
    def test_insert_tile_valid(self):
        players = [
            Player("Spieler 0"),
            Player("Spieler 1"),
        ]
        
        game = Game(players, board_size=7)
        game.initialize_players(players)
        initial_board = game.board
        for player in players:
            player.game = game
        player = players[0]
        """Testet das Einschieben einer Kachel an einer gültigen Position."""
        previous_free_tile = game.current_tile  # Die aktuelle freie Kachel speichern
        insert_position = (1, 0)  # Beispiel: Kachel in die zweite Spalte schieben
        
        tile_afterinsert=game.insert_tile(insert_position)  # Kachel einschieben
        
        # 🔹 1️⃣ Prüfen, ob sich das Spielfeld verändert hat
        self.assertNotEqual(previous_free_tile, game.current_tile, "Das Spielfeld sollte sich ändern.")

if __name__ == '__main__':
    unittest.main()
