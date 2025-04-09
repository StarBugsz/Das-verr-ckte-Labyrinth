import random
import copy
from pathfinder import Pathfinder

class AIPlayer():
    def __init__(self, id):
        self.name = None
        self.id = id
        self.position = None
        self.cards = []
        self.has_collected_all_treasurecards = False
        self.start_position = None
        self.lobby = None
        self.color = None
        self.game = None
        self.number = None
        self.score = 0
        self.ai = True

    def set_color(self, color):
        self.color = color

    def get_treasure_cards(self):
        return [card.name for card in self.cards]

    def __str__(self):
        return self.name
    
    def __eq__(self, other):
        return self.id == other.id
    
    def evaluate_position(self, position, simulated_board, simulated_current_tile=None, mode="move"):
        """
        Bewertet eine Position oder ein Einschieben basierend auf strategischen Kriterien.
        Args:
            position (tuple): Zielposition (row, col) oder Einschiebe-Position.
            simulated_board: Das simulierte Spielfeld nach einer Aktion.
            simulated_current_tile (Tile, optional): Die eingeschobene Kachel (nur relevant für "insert").
            mode (str): Bewertungsmodus, entweder "move" oder "insert".
        Rückgabewert:
            float: Bewertungswert. Höhere Werte sind besser.
        """
        score = 0
        row, col = position

        # 1. Nähe zum nächsten Schatz
        if self.cards:
            treasure_position = self.game.find_treasure_position(self.cards[0].name, simulated_board)
            if treasure_position:
                distance_to_treasure = abs(treasure_position[0] - row) + abs(treasure_position[1] - col)
                if mode == "move":
                    score += max(50 - distance_to_treasure, 0)  # Belohne Nähe zum Schatz
                elif mode == "insert" and treasure_position in self.game.pathfinder.find_reachable_tilesforAI(self.position, simulated_board):
                    score += 100  # Hoher Bonus, wenn das Einschieben den Schatz erreichbar macht

        # 2. Bewegungsfreiheit, mehr Kacheln erreichbar
        reachable_before = len(self.game.pathfinder.find_reachable_tilesforAI(self.position))
        reachable_after = len(self.game.pathfinder.find_reachable_tilesforAI(self.position, simulated_board))
        score += (reachable_after - reachable_before) * 5  # Belohne Verbesserung der Bewegungsoptionen

        # 3. Gegnerstrategien verhindern
        for opponent in self.game.players:
            if opponent != self:
                opponent_target = opponent.cards[0].name if opponent.cards else None
                if opponent_target:
                    opponent_treasure = self.game.find_treasure_position(opponent_target, simulated_board)
                    if opponent_treasure and opponent_treasure in self.game.pathfinder.find_reachable_tilesforAI(opponent.position, simulated_board):
                        score -= 30  # Bestrafe Züge, die dem Gegner helfen

        # 4. Nähe zur Startposition
        if not self.cards and mode == "move":  # Nur relevant, wenn alle Schätze eingesammelt sind
            start_row, start_col = self.start_position
            distance_to_start = abs(start_row - row) + abs(start_col - col)
            score += max(50 - distance_to_start, 0)

        # 5. Zufälligkeit bei gleichen Punktzahlen
        score += random.uniform(0, 1)  # Füge eine kleine Zufälligkeit hinzu

        return score

    def simulate_move(self, player, move_position, board):  # Simuliert die Bewegung eines Spielers auf dem Board.
        # Erstelle eine Kopie des aktuellen Boards
        simulated_board = copy.deepcopy(self.game.board)  # Tiefenkopie des Boards

        # Spielerposition aktualisieren
        simulated_player = player
        simulated_player.position = move_position

        # Falls es notwendig ist, zusätzliche Effekte wie Schatzsammeln zu simulieren:
        treasure_position = self.game.find_treasure_position(
            player.cards[0].name, simulated_board
        ) if player.cards else None

        if treasure_position == move_position:
            # Simuliere das Sammeln eines Schatzes
            simulated_player.cards.pop(0)

        return simulated_board

    def decide_move(self):
        # Simuliert zwei Züge im Voraus und wählt die beste Kombination aus Einschieben und Bewegung für beide Züge aus.
        possible_insert_positions = [  # Mögliche Einschiebe-Positionen
            (0, i) for i in range(1, 7, 2)
        ] + [
            (6, i) for i in range(1, 7, 2)
        ] + [
            (i, 0) for i in range(1, 7, 2)
        ] + [
            (i, 6) for i in range(1, 7, 2)
        ]

        best_score = float('-inf')
        best_first_insert_position = None
        best_first_move_position = None
        best_second_insert_position = None
        best_second_move_position = None

        # 1. Schleife durch alle möglichen Einschiebe-Positionen (erster Zug)
        for first_insert_position in possible_insert_positions:
            # Simuliere das Einschieben für den ersten Zug
            simulated_board_first, simulated_current_tile_first = self.game.simulate_tile_insertion(first_insert_position)

            # Bestimme erreichbare Felder nach dem ersten Einschieben
            reachable_tiles_first = self.game.pathfinder.find_reachable_tilesforAI(self.position, simulated_board_first)
            print(first_insert_position)
            print(f"Erreichbare Felder nach dem ersten Einschieben: {reachable_tiles_first}")
            for first_move_position in reachable_tiles_first:
                # Simuliere die Bewegung der KI für den ersten Zug
                simulated_board_after_first_move = self.simulate_move(self, first_move_position, simulated_board_first)
                
                # 2. Schleife durch mögliche Einschiebe-Positionen für den zweiten Zug
                for second_insert_position in possible_insert_positions:
                    if second_insert_position == first_insert_position:  # Vermeidet dieselbe Einschiebe-Position
                        continue

                    # Simuliert das Einschieben für den zweiten Zug
                    simulated_board_second, simulated_current_tile_second = self.game.simulate_tile_insertion(
                        second_insert_position,
                        inserted_tile=simulated_current_tile_first
                    )

                    # Bestimmt erreichbare Felder nach dem zweiten Einschieben
                    reachable_tiles_second = self.game.pathfinder.find_reachable_tilesforAI(
                        first_move_position, simulated_board_second
                    )

                    for second_move_position in reachable_tiles_second:
                        # Berechnet den Score für die simulierten Züge
                        score_first_move = self.evaluate_position(
                            first_move_position,
                            simulated_board_after_first_move,
                            mode="move"
                        )
                        score_second_move = self.evaluate_position(
                            second_move_position,
                            simulated_board_second,
                            mode="move"
                        )

                        # Gesamtbewertung der zwei Züge
                        total_score = score_first_move + score_second_move
                        # Aktualisiert den besten Zug basierend auf dem Score
                        if total_score > best_score:
                            best_score = total_score
                            best_first_insert_position = first_insert_position
                            best_first_move_position = first_move_position
                            best_second_insert_position = second_insert_position
                            best_second_move_position = second_move_position

        print(f"Beste erste Einschiebe-Position: {best_first_insert_position}")
        print(f"Beste erste Bewegungsposition: {best_first_move_position}")
        print(f"Beste zweite Einschiebe-Position: {best_second_insert_position}")
        print(f"Beste zweite Bewegungsposition: {best_second_move_position}")
        print(f"Höchster Score: {best_score}")

        return (best_first_insert_position, best_first_move_position,
                best_second_insert_position, best_second_move_position)

    def decide_tile_insertion(self):
        # Wählt eine Position für das Einschieben der Kachel.
        possible_positions = [
            (0, i) for i in range(1, 7, 2)
        ] + [
            (6, i) for i in range(1, 7, 2)
        ] + [
            (i, 0) for i in range(1, 7, 2)
        ] + [
            (i, 6) for i in range(1, 7, 2)
        ]

        best_position = None
        best_score = float('-inf')

        for position in possible_positions:
            # Simuliert das Einfügen und bewertet die Position
            simulated_board, simulated_current_tile = self.game.simulate_tile_insertion(position)
            score = self.evaluate_position(position, simulated_board, simulated_current_tile, mode="insert")

            if score > best_score:  # Speichert die beste Position
                best_score = score
                best_position = position

        print(f"Beste Einschiebe-Position: {best_position} mit Score {best_score}")
        return best_position

    def decide_movetest(self):  # Wählt eine Position für die Bewegung der KI
        reachable_tiles = self.game.pathfinder.find_reachable_tilesforAI(self.position)
        best_score = float('-inf')
        best_move = None
        print(f"Erreichbare Felder 1: {reachable_tiles}")
        for position in reachable_tiles:
            
            simulated_board = self.game.board  # Aktuelles Spielfeld, keine Simulation erforderlich
            score = self.evaluate_positiontest(position, simulated_board, mode="move")

            if score > best_score:
                best_score = score
                best_move = position
        print(f"Beste Bewegungsposition: {best_move} mit Score {best_score}")
        return best_move

    def evaluate_positiontest(self, position, simulated_board, simulated_current_tile=None, mode="move"):
        score = 0
        row, col = position

        # 1. Nähe zum nächsten Schatz
        if self.cards:
            treasure_position = self.game.find_treasure_position(self.cards[0].name, simulated_board)
            if treasure_position:
                distance_to_treasure = abs(treasure_position[0] - row) + abs(treasure_position[1] - col)
                reachable_tiles = self.game.pathfinder.find_reachable_tilesforAI(self.position, simulated_board)
                if mode == "move":
                    score += max(50 - distance_to_treasure, 0)  # Belohne Nähe zum Schatz
                    if treasure_position in reachable_tiles:
                        score += 1000
                elif mode == "insert" and treasure_position in self.game.pathfinder.find_reachable_tilesforAI(self.position, simulated_board):
                    reachable_tiles = self.game.pathfinder.find_reachable_tilesforAI(self.position, simulated_board)
                    score += 100  # Hoher Bonus, wenn das Einschieben den Schatz erreichbar macht
                    if treasure_position in reachable_tiles:
                        score += 1000
                
        # 2. Bewegungsfreiheit, mehr Kacheln erreichbar
        reachable_before = len(self.game.pathfinder.find_reachable_tilesforAI(self.position))
        reachable_after = len(self.game.pathfinder.find_reachable_tilesforAI(self.position, simulated_board))
        score += (reachable_after - reachable_before) * 5  # Belohne Verbesserung der Bewegungsoptionen

        # 3. Gegnerstrategien verhindern
        for opponent in self.game.players:
            if opponent != self:
                opponent_target = opponent.cards[0].name if opponent.cards else None
                if opponent_target:
                    opponent_treasure = self.game.find_treasure_position(opponent_target, simulated_board)
                    if opponent_treasure and opponent_treasure in self.game.pathfinder.find_reachable_tilesforAI(opponent.position, simulated_board):
                        score -= 30  # Bestrafe Züge, die dem Gegner helfen

        # 4. Nähe zur Startposition
        if not self.cards and mode == "move":  # Nur relevant, wenn alle Schätze eingesammelt sind
            start_row, start_col = self.start_position
            distance_to_start = abs(start_row - row) + abs(start_col - col)
            score += max(50 - distance_to_start, 0)

        # 5. Zufälligkeit bei gleichen Punktzahlen
        score += random.uniform(0, 1)  # Füge eine kleine Zufälligkeit hinzu

        return score


    # Testfunktion zum ausfuehren eines KI-Zuges
    def play_turn(self):
        # Wählt die beste Kombination aus Einschieben und Bewegungen für zwei Züge
        (first_insert_position, first_move_position,
        second_insert_position, second_move_position) = self.decide_move()

        # 1. Erster Zug
        print(f"KI wählt erste Einschiebe-Position: {first_insert_position}")
        insert_result_first = self.game.insert_tile(first_insert_position)
        if insert_result_first["status"] != "success":
            print(f"KI konnte keine Kachel einfügen: {insert_result_first['message']}")
            return

        print(f"KI wählt erste Bewegungsposition: {first_move_position}")
        move_result_first = self.game.move_player(self, first_move_position)
        print(f"KI hat sich zu {first_move_position} bewegt")
        """
        # 2. Zweiter Zug
        print(f"KI wählt zweite Einschiebe-Position: {second_insert_position}")
        insert_result_second = self.game.insert_tile(second_insert_position)
        if insert_result_second["status"] != "success":
            print(f"KI konnte keine Kachel einfügen: {insert_result_second['message']}")
            return

        print(f"KI wählt zweite Bewegungsposition: {second_move_position}")
        move_result_second = self.game.move_player(self, second_move_position)
        print(f"KI hat sich zu {second_move_position} bewegt")
        """

