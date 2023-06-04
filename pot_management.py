
class PotManagement:
    def __init__(self, table_manager, community_pot, side_pots, ranked_players, eligible_players, active_players, ante, small_blind, big_blind):
        self.table_manager = table_manager
        self.community_pot = community_pot
        self.side_pots = side_pots

        self.ranked_players = ranked_players
        self.eligible_players =  eligible_players
        self.active_players = active_players

        self.ante = ante
        self.small_blind = small_blind
        self.big_blind = big_blind


    def collect_blinds(self):
        
        for player in self.active_players:
            if player is None or player.is_sitting_out:  # Skip the empty seats
                continue

            if player.is_small_blind:
                # Collect small blind
                small_blind_amount = min(player.stack_size, self.small_blind)

                # Check if a player has gone all-in for less
                if small_blind_amount < self.small_blind:
                    player.all_in()
                else:
                    player.bet(small_blind_amount)

                # Add blinds to the main pot
                self.community_pot['pot_value'] += small_blind_amount

            if player.is_big_blind:
                # Collect big blind
                big_blind_amount = min(player.stack_size, self.big_blind)

                if big_blind_amount < self.big_blind:
                    player.all_in()
                else:
                    player.bet(big_blind_amount)

                # Add blinds to the main pot
                self.community_pot['pot_value'] += big_blind_amount
        
        return self.community_pot['pot_value']    



    def collect_antes(self):
        for player in self.active_players:
            if player.stack_size == 0:
                continue  # Skip players with no chips
            ante_amount = min(player.stack_size, self.ante)
            player.pay_ante(ante_amount)
            self.community_pot['pot_value'] += ante_amount
        return self.community_pot['pot_value']


    def create_side_pot(self):
        all_in_players = sorted([player for player in self.active_players if player.is_all_in and player.is_eligible_for_pot], key=lambda player: player.total_bet)

        while len(all_in_players) > 0:
            side_pot_players = []  # List to store players with the same all-in amount
            player = all_in_players.pop(0)  # Get the first player who went all-in
            side_pot_players.append(player)  # Add the player to the list

            # Find other players with the same all-in amount
            while len(all_in_players) > 0 and all_in_players[0].total_bet == player.total_bet:
                side_pot_players.append(all_in_players.pop(0))

            player_pot_value = player.total_bet  

            # Calculate the side pot value and subtract it from each eligible player's total bet
            side_pot_value = 0
            for pot_player in self.community_pot['eligible_players']:
                pot_player.total_bet -= player_pot_value
                side_pot_value += player_pot_value

            self.community_pot['pot_value'] -= side_pot_value

            side_pot_eligible_players = self.community_pot['eligible_players']

            self.side_pots.append({'pot_value': side_pot_value, 'eligible_players': side_pot_eligible_players})

        # The all-in players are no longer eligible for further pots
        for player in side_pot_players:
            player.is_eligible_for_pot = False

        self.eligible_players = self.table_manager.update_player_eligibility()

        return self.side_pots


    def distribute_pots(self, ranked_player_groups):
        # ranked_player_groups is a list of lists, process each group in the list
        for group in ranked_player_groups:
            if not isinstance(group, list):
                group = [group]
            # Check if any player in the group is eligible for a side pot
            for index in reversed(range(len(self.side_pots))):
                pot = self.side_pots[index]
                if all(player.name in [player.name for player in pot['eligible_players']] for player in group):
                    print(f"{', '.join(player.name for player in group)} distributed side pot of {pot['pot_value']}.")
                    self.distribute_pot(pot, group)  # Distribute the pot amongst the group
                    self.side_pots.pop(index)

            # Check if any player in the group is eligible for the community pot
            if self.community_pot['pot_value'] > 0 and all(player.name in [p.name for p in self.community_pot['eligible_players']] for player in group):
                print(f"{', '.join(player.name for player in group)} distributed community pot of {self.community_pot['pot_value']}.")
                self.distribute_pot(self.community_pot, group)  # Distribute the pot amongst the group
                self.community_pot['pot_value'] = 0
                self.community_pot['eligible_players'] = []

            # If all pots are distributed, break the loop
            if self.side_pots == [] and self.community_pot['pot_value'] == 0:
                break


    def distribute_pot(self, pot, player_group):
        pot_size = pot['pot_value']

        # Find the eligible winners from the ranked players
        winners = [player for player in player_group if player.name in [p.name for p in pot['eligible_players']]]

        if len(winners) == 1:
            winner = winners[0]
            winner.stack_size += pot_size

        else:
            # Split the pot among the winners
            winnings_per_player = pot_size // len(winners)
            remainder = pot_size % len(winners)

            for winner in winners:
                winner.stack_size += winnings_per_player

            # Distribute any remaining chips
            for i in range(remainder):
                winners[i].stack_size += 1






class BlindStructure:
    def __init__(self):
        self.blind_levels = self.blinds_list()

    def blinds_list(self):
        # Manually define blinds and antes for the first 100 levels
        blinds = [
            # 1-20
            (10, 20, 2), (15, 30, 4), (20, 40, 5), (25, 50, 6), (30, 60, 8), 
            (40, 80, 10), (50, 100, 12), (75, 150, 18), (100, 200, 25), (125, 250, 30),
            (150, 300, 38), (200, 400, 50), (250, 500, 62), (300, 600, 75), (400, 800, 100),
            (500, 1000, 125), (600, 1200, 150), (800, 1600, 200), (1000, 2000, 250), (1200, 2400, 300),
            # 21-40
            (10, 20, 0), (15, 30, 0), (20, 40, 0), (25, 50, 0), (30, 60, 0), 
            (40, 80, 0), (50, 100, 0), (75, 150, 0), (100, 200, 0), (100, 200, 20),
            (150, 300, 30), (200, 400, 40), (250, 500, 50), (300, 600, 60), (400, 800, 80),
            (500, 1000, 100), (600, 1200, 120), (800, 1600, 160), (1000, 2000, 200), (1200, 2400, 240),
            # 41-60
            (10, 20, 0), (15, 30, 0), (20, 40, 0), (25, 50, 0), (30, 60, 0), 
            (40, 80, 0), (50, 100, 0), (75, 150, 0), (100, 200, 0), (100, 200, 20),
            (150, 300, 30), (200, 400, 40), (250, 500, 50), (300, 600, 60), (400, 800, 80),
            (500, 1000, 100), (600, 1200, 120), (800, 1600, 160), (1000, 2000, 200), (1200, 2400, 240),
            # 61-80                     
            (10, 20, 0), (15, 30, 0), (20, 40, 0), (25, 50, 0), (30, 60, 0), 
            (40, 80, 0), (50, 100, 0), (75, 150, 0), (100, 200, 0), (100, 200, 20),
            (150, 300, 30), (200, 400, 40), (250, 500, 50), (300, 600, 60), (400, 800, 80),
            (500, 1000, 100), (600, 1200, 120), (800, 1600, 160), (1000, 2000, 200), (1200, 2400, 240),
            # 81-100          
            (10, 20, 0), (15, 30, 0), (20, 40, 0), (25, 50, 0), (30, 60, 0), 
            (40, 80, 0), (50, 100, 0), (75, 150, 0), (100, 200, 0), (100, 200, 20),
            (150, 300, 30), (200, 400, 40), (250, 500, 50), (300, 600, 60), (400, 800, 80),
            (500, 1000, 100), (600, 1200, 120), (800, 1600, 160), (1000, 2000, 200), (1200, 2400, 240),             
        ]
        last_blind = blinds[-1]
        for _ in range(len(blinds), 100):  # Continue until we reach 100 levels
            last_blind = (last_blind[0] * 1.5, last_blind[1] * 1.5, last_blind[2] * 1.5)
            # Round to nearest integer
            last_blind = tuple(round(x) for x in last_blind)
            blinds.append(last_blind)
        return blinds


    def get_blinds(self, level):
        return self.blind_levels[level]


    def get_level_duration(self, level):
        # If there's a specific duration for this level, return it
        if level < len(self.level_durations):
            return self.level_durations[level]
        # Otherwise, return a default duration
        else:
            return 20  # minutes, for example
