from table_management import TableManagement
from individual_player import Player
from pot_management import PotManagement, BlindStructure


class GameManagement:
    def __init__(self, game_type, max_seats, blind_structure, max_players):
        self.game_type = game_type
        self.max_seats = max_seats  
        self.blind_structure = blind_structure
        self.table = TableManagement(max_seats)
        self.pot = PotManagement(blind_structure)

    def add_player(self, player):
        self.table.add_player(player)

    def remove_player(self, player):
        self.table.remove_player(player)

    def start_hand(self):
        if self.table.can_start_hand():
            self.pot.collect_blinds(self.table.get_blind_players())
            if self.pot.ante > 0:
                self.pot.collect_antes(self.table.get_active_players())
            # Add more actions here for a complete hand
        else:
            print("Not enough players for a hand.")




class Tournament(GameManagement):
    def __init__(self, max_seats, initial_stack, starting_players, level_durations=None):
        self.current_blind_level = 0
        self.initial_stack = initial_stack
        self.blind_structure = BlindStructure()
        self.starting_players = starting_players
        self.active_players = starting_players
        super().__init__(max_seats, self.initial_stack, self.blind_structure, starting_players)  # Pass max_players to GameManagement's __init__
        for i in range(starting_players):
            player_name = f"Player {i + 1}"
            self.table.add_player(Player(player_name, self.initial_stack))



class CashGame(GameManagement):
    def __init__(self, max_seats, blinds_and_ante, max_players):
        super().__init__("cash_game", max_seats, blinds_and_ante, max_players)


class SpinAndGo(GameManagement):
    def __init__(self, blind_structure, initial_stack):
        super().__init__(3, blind_structure)  # Spin and Go is always 3 players
        self.initial_stack = initial_stack
        for player in self.table.players:
            player.stack = self.initial_stack


class HeadsUp(GameManagement):
    def __init__(self, blind_structure):
        super().__init__(2, blind_structure)  # Heads up is always 2 players
