class TableManagement:
    def __init__(self, max_seats):
        self.max_seats = max_seats
        self.players = [None] * max_seats  # Initializes an array with 'None' to represent empty seats

    def add_player(self, player, position=None):
        if self.players.count(None) == 0:
            print("Table is full. Cannot add more players.")
            return
        if position is None:
            position = self.players.index(None)  # Adds player to first empty seat
        self.players[position] = player

    def remove_player(self, player):
        if player in self.players:
            self.players[self.players.index(player)] = None  # Removes player and leaves seat empty

    def manage_table(self):
        for player in self.players:
            if player and player.chips <= 0:
                self.remove_player(player)
                print(f"Player {player.name} has been removed from the table.")

    def combine_tables(self, other_table):
        empty_seats = self.players.count(None)
        active_players_other_table = len(other_table.players) - other_table.players.count(None)

        # Only combine tables if there are enough empty seats for all active players in the other table
        if empty_seats >= active_players_other_table:
            for _ in range(active_players_other_table):
                transferring_player = next((player for player in other_table.players if player is not None), None)
                self.add_player(transferring_player)
                other_table.remove_player(transferring_player)
        else:
            print("Not enough empty seats to combine tables.")
