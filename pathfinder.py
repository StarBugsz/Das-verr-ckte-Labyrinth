from collections import deque

class Pathfinder:
    def __init__(self, board):
        self.board = board  # Referenz auf das Spielfeld

    def find_reachable_tiles(self, start, board=None):  # findet alle erreichbaren Kacheln von einer Startposition aus
        if isinstance(start, list):
            start = tuple(start)  # Umwandlung von Liste in Tupel
        board = board or self.board
        queue = deque([(start, [start])])  # Startposition und der initiale Pfad
        visited = set() # Menge der bereits besuchten Positionen (Dopplungen werden autom. geloescht)
        visited.add(start)  # Startpunkt als besucht markieren
        
        reachable_tiles = []  # Liste der erreichbaren Kacheln
        paths = {} # dictonary, das Pfade zu jeder rreichbaren Kachel enthält
        while queue:
            current, path = queue.popleft()  # Nächste Position + Pfad aus der Warteschlange holen 
            current = tuple(current)
            reachable_tiles.append(current)  # Füge die aktuelle Position zur Liste der erreichbaren Kacheln hinzu
            paths[current] = path   # Speichert Pfad, zu dieser Position
            
            neighbors = self.get_valid_neighbors(current, board)  # findet benachbarte und erreichbare Kacheln 
            for neighbor in neighbors:
                neighbor = tuple(neighbor)
                if neighbor not in visited:
                    visited.add(neighbor)  # Nachbarn als besucht markieren
                    queue.append((neighbor, path + [neighbor]))  # Nachbarn mit aktualisierten Pfad zur Warteschlange hinzufügen

        return reachable_tiles, paths  # Gibt alle erreichbaren Kacheln zurück

    def get_valid_neighbors(self, position, board=None): # findet alle gültigen Nachbarn einer Kachel
        board = board or self.board 
        if not isinstance(position, tuple):
            position = tuple(position)
        x, y = position
        neighbors = []
        directions = {
            'top': (-1, 0),
            'bottom': (1, 0),
            'left': (0, -1),
            'right': (0, 1)
        }
        for direction, (dx, dy) in directions.items():
            nx, ny = x + dx, y + dy # Nachbarposition berechnen
            if 0 <= nx < len(board) and 0 <= ny < len(board): # Stellt sicher, dass die Nachbar-Position im Spielfeld liegt
                current_tile = board[x][y] # aktuelle Kachel
                neighbor_tile = board[nx][ny] # Nachbar-Kachel
                if current_tile and neighbor_tile:  
                    if current_tile.is_connected(direction) and neighbor_tile.is_connected(self.opposite_direction(direction)): # Prüfen, ob beide Kacheln in der Richtung verbunden sind
                        neighbors.append((nx, ny))  # Fügt die Nachbar-Position zur Liste hinzu
        return neighbors
    
    def find_reachable_tilesforAI(self, start, board=None, callback=None):
        if isinstance(start, list):
            start = tuple(start)  # Umwandlung von Liste in Tupel
        board = board or self.board
        queue = deque([(start, [start])])  # Startposition und der initiale Pfad
        visited = set()
        visited.add(start)

        reachable_tiles = []
        paths = {}  # Speichert Pfade zu jeder erreichbaren Kachel

        while queue:
            current, path = queue.popleft()
            current = tuple(current)
            reachable_tiles.append(current)
            paths[current] = path  # Pfad speichern

            neighbors = self.get_valid_neighbors(current, board)
            for neighbor in neighbors:
                neighbor = tuple(neighbor)
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        # Falls ein Callback übergeben wurde, rufen wir ihn mit den Pfaden auf
        if callback:
            callback(paths)

        return reachable_tiles

    def get_valid_neighborsforAI(self, position, board=None):
        board = board or self.board

        # Sicherstellen, dass `position` ein einzelnes (x, y)-Tupel ist
        if isinstance(position, tuple) and len(position) == 2 and all(isinstance(coord, int) for coord in position):
            x, y = position
        else:
            raise ValueError(f"Invalid position format: {position}. Expected a tuple (x, y) of integers.")

        neighbors = []
        directions = {
            'top': (-1, 0),
            'bottom': (1, 0),
            'left': (0, -1),
            'right': (0, 1)
        }

        for direction, (dx, dy) in directions.items():
            nx, ny = x + dx, y + dy  # Nachbarposition berechnen
            if 0 <= nx < len(board) and 0 <= ny < len(board):  # Sicherstellen, dass die Nachbar-Position im Spielfeld liegt
                current_tile = board[x][y]  # Aktuelle Kachel
                neighbor_tile = board[nx][ny]  # Nachbar-Kachel

                if current_tile and neighbor_tile:
                    if current_tile.is_connected(direction) and neighbor_tile.is_connected(self.opposite_direction(direction)):
                        neighbors.append((nx, ny))  # Füge die Nachbar-Position zur Liste hinzu

        return neighbors


    @staticmethod
    def opposite_direction(direction):
        opposites = {
            'top': 'bottom',
            'bottom': 'top',
            'left': 'right',
            'right': 'left'
        }
        return opposites[direction]

    def reconstruct_path(self, parent_map, start, goal):
        path = []
        current = goal
        while current != start:
            path.append(current)
            current = parent_map[current]
        path.append(start)
        path.reverse()
        return path
    
    def find_path(self, start, goal):
        queue = deque([start])  # Warteschlange für die BFS
        visited = set()  # Menge der bereits besuchten Positionen
        parent_map = {}  # Speichert, von wo aus eine Position erreicht wurde

        visited.add(start)  # Startposition als besucht markieren

        while queue:
            current = queue.popleft()  # Nächste Position aus der Warteschlange holen

            if current == goal:
                # Ziel erreicht, Pfad rekonstruieren
                return self.reconstruct_path(parent_map, start, goal)

            neighbors = self.get_valid_neighbors(current)  # Gültige Nachbarn finden
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)  # Nachbarn als besucht markieren
                    parent_map[neighbor] = current  # Eltern-Position speichern
                    queue.append(neighbor)  # Nachbar zur Warteschlange hinzufügen

        return []  # Gibt einen leeren Pfad zurück, wenn kein Pfad gefunden wurde
