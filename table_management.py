class TableManagement:
    def __init__(self, table_name):
        self.tables = {}
        self.table_name = table_name
        self.dealer_position = 0


    def get_active_players(self):
        players_list = self.tables[self.table_name]['player_activity']['active_players']
        # Filter the players who have not folded
        active_players = [player for player in players_list if not player.is_folded and not player.is_sitting_out]
        
        return active_players


    def update_player_eligibility(self):
        
        eligible_players = [player for player in self.tables[self.table_name]['player_activity']['active_players'] if player.is_eligible_for_pot and not player.is_folded and not player.is_sitting_out]
        self.tables[self.table_name]['community_pot']['eligible_players'] = eligible_players
        
        return eligible_players


    def add_table(self, table_name, table_config):
        self.tables[table_name] = {
            'max_seats': table_config['max_seats'],
            'min_buy_in': table_config['min_buy_in'],
            'max_buy_in': table_config['max_buy_in'],
            'blinds': table_config['blinds'],
            'player_activity': {
                'active_players': [None]*table_config['max_seats'],
                'waiting_player': [None]*table_config['max_seats'] * 2,
            },
            'community_pot': table_config['community_pot'].copy(),
            'side_pots': table_config['side_pots'].copy(),
            'seats': [None]*table_config['max_seats'],  
        }
        return table_name


    def remove_table(self):
        table = self.tables[self.table_name]
        # Prevent the removal of the table if there are players at the table
        if len(table['players']) > 0:
            print("Table is not empty. Cannot remove table.")
            return
        self.tables.pop(self.table_name)


    def add_player(self, player, table):
    
        # Check if there is an open seat
        if None in table['seats']:
            # Find the first empty seat
            position = table['seats'].index(None)

            # Place the player in the seat
            table['seats'][position] = player
            table['player_activity']['active_players'][position] = player  # Add player to 'players' list at the same position
        else:
            print("Table is full. Cannot add more players.")



    def remove_player(self, player, table_name):
        table = self.tables[table_name]

        if player in table['seats']:
            print(f"{player.name} has been removed from the table.")
            index = table['seats'].index(player)
            table['seats'][index] = None
            table['player_activity']['active_players'].remove(player)
            

    def manage_table(self, table_name):
        table = self.tables[table_name]

        for player in table['seats']:
            if player and player.chips <= 0:
                self.remove_player(player, table_name)
                print(f"Player {player.name} has been removed from the table.")


    def combine_tables(self, first_table_id, second_table_id):
        first_table = self.tables[first_table_id]
        second_table = self.tables[second_table_id]

        empty_seats = first_table['seats'].count(None)
        active_players_other_table = len(second_table['player_activity']['active_players']) - second_table['seats'].count(None)

        if empty_seats >= active_players_other_table:
            # Get non-empty seats from first table and non-empty players from second table
            combined_players = [player for seat, player in zip(first_table['seats'], first_table['player_activity']['active_players']) if seat is not None] + \
                            [player for seat, player in zip(second_table['seats'], second_table['player_activity']['active_players']) if seat is not None]
            
            # Update the first table with the combined players
            first_table['player_activity']['active_players'] = combined_players
            first_table['seats'] = [player if player is not None else None for player in first_table['player_activity']['active_players']]

            # Clear the second table
            second_table['player_activity']['active_players'] = [None] * len(second_table['seats'])
            second_table['seats'] = [None] * len(second_table['seats'])
        else:
            print("Not enough empty seats to combine tables.")


    def set_start_index(self, street, table, big_blind):
        all_players = table['seats']
        
        big_blind_index = None
        dealer_index = None
        for i, player in enumerate(all_players):
            if player is not None:
                if player.is_big_blind:
                    big_blind_index = i
                if player.is_dealer:
                    dealer_index = i


        if street == 'preflop':
            # The player to the left of the big blind starts on preflop
            starting_player_index = (big_blind_index + 1) % len(all_players)
            bet_to_match = big_blind
        else:
            # The player to the left of the dealer starts on all other streets
            starting_player_index = (dealer_index + 1) % len(all_players)
            bet_to_match = 0

        # Ensure the starting player is not None
        while all_players[starting_player_index] is None:
            starting_player_index = (starting_player_index + 1) % len(all_players)
    
        return all_players, starting_player_index, bet_to_match



    def advance_button(self, table_manager, table_name):
        table = table_manager.tables[table_name]
        seats = table['seats']

        # Reset dealer, small blind and big blind status for all players
        for player in seats:
            if player is not None:
                player.is_dealer = False
                player.is_small_blind = False
                player.is_big_blind = False

        # Find the next non-empty seat for dealer
        self.dealer_position = (self.dealer_position + 1) % len(seats)
        while seats[self.dealer_position] is None:
            self.dealer_position = (self.dealer_position + 1) % len(seats)
        seats[self.dealer_position].is_dealer = True

        # Find the next non-empty seat for small blind
        self.small_blind_position = (self.dealer_position + 1) % len(seats)
        while seats[self.small_blind_position] is None:
            self.small_blind_position = (self.small_blind_position + 1) % len(seats)

        # Find the next non-empty seat for big blind
        self.big_blind_position = (self.small_blind_position + 1) % len(seats)
        while seats[self.big_blind_position] is None:
            self.big_blind_position = (self.big_blind_position + 1) % len(seats)

        # In heads-up situations, the dealer also posts the small blind
        if len([seat for seat in seats if seat is not None]) == 2:
            seats[self.dealer_position].is_small_blind = True
            seats[self.small_blind_position].is_big_blind = True
        else:
            seats[self.small_blind_position].is_small_blind = True
            seats[self.big_blind_position].is_big_blind = True
