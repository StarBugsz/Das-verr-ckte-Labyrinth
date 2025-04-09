class Player:
    def __init__(self, id):
        self.name = None
        self.id = id
        self.position = None
        self.cards = []
        self.has_collected_all_treasurecards = False
        self.start_position = None
        self.lobby = None
        self.color = "Black"
        self.number = None
        self.score = 0
        self.ai = False

    def set_color(self, color):
        self.color = color

    def get_treasure_cards(self):
        return [card.name for card in self.cards]

    def __str__(self):
        return self.name
    
    def __eq__(self, other):
        return self.id == other.id