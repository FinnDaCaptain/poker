import copy

class PotManagement:
    def __init__(self, table_manager, community_pot, side_pots, ranked_players, eligible_players, active_players):
        self.table_manager = table_manager
        self.community_pot = community_pot
        self.side_pots = side_pots

        self.ranked_players = ranked_players
        self.eligible_players =  eligible_players
        self.active_players = active_players

    def collect_blinds(self, small_blind, big_blind):
        
        for player in self.active_players:
            if player is None:  # Skip the empty seats
                continue

            if player.is_small_blind:
                # Collect small blind
                small_blind_amount = min(player.stack_size, small_blind)

                # Check if a player has gone all-in for less
                if small_blind_amount < small_blind:
                    player.all_in()
                else:
                    player.bet(small_blind_amount)

                # Add blinds to the main pot
                self.community_pot['pot_value'] += small_blind_amount

            if player.is_big_blind:
                # Collect big blind
                big_blind_amount = min(player.stack_size, big_blind)

                if big_blind_amount < big_blind:
                    player.all_in()
                else:
                    player.bet(big_blind_amount)

                # Add blinds to the main pot
                self.community_pot['pot_value'] += big_blind_amount
        
        return self.community_pot['pot_value']    



    def collect_antes(self, ante):
        for player in self.active_players:
            if player.stack_size == 0:
                continue  # Skip players with no chips
            ante_amount = min(player.stack_size, ante)
            player.pay_ante(ante_amount)
            self.community_pot['pot_value'] += ante_amount
        return self.community_pot['pot_value']



    def handle_bets(self):
        all_in_players = sorted([player for player in self.active_players if player.is_all_in], key=lambda player: player.all_in_amount)
        covered_all_in_amount = 0  # All-in amount that was already covered by the previous side pots

        while len(all_in_players) > 0:
            player = all_in_players.pop(0)  # Remove and get the first player who went all-in

            # Create a side pot if there are at least 2 players who can contribute to it
            if len(self.eligible_players) >= 3:
                side_pot_multiplier = len(self.eligible_players)
                player_pot_value = player.total_bet - covered_all_in_amount  # Excess of the player's total bet over the covered all_in amount
                side_pot_value = player_pot_value * side_pot_multiplier
                
                # Check that the side pot value doesn't exceed the community pot value
                side_pot_value = min(side_pot_value, self.community_pot['pot_value'])
                
                self.community_pot['pot_value'] -= side_pot_value

                # Add a copy of each eligible player to the new side pot
                self.side_pots.append({'pot_value': side_pot_value, 'eligible_players': [copy.copy(player) for player in self.eligible_players]})

                covered_all_in_amount = player.total_bet  # Update the covered all-in amount

            # The all-in player is no longer eligible for further pots
            self.community_pot['eligible_players'].remove(player)

        # This might not be necessary anymore, but keeping it in case there are other reasons to update eligible players
        self.community_pot['eligible_players'] = [player for player in self.community_pot['eligible_players'] if player.is_eligible_for_pot]



    def distribute_pots(self, ranked_players):
        for player in ranked_players:

            # Distribute all pots this player is eligible for
            for pot in self.side_pots + [self.community_pot]:
                if player.name in [p.name for p in pot['eligible_players']]:
                    self.distribute_pot(pot, player)

            # Stop distribution if all pots have been distributed
            if all(pot['pot_value'] == 0 for pot in self.side_pots) and self.community_pot['pot_value'] == 0:
                break

        # Clear the list of eligible players for the next hand
        self.eligible_players = []
        self.side_pots = []


    def distribute_pot(self, pot, player):
        pot_size = pot['pot_value']

        # Check if player is eligible for this pot
        if player.name not in [p.name for p in pot['eligible_players']]:
            return

        # Find the eligible winners from the ranked players
        winners = [p for p in pot['eligible_players'] if p.name == player.name]

        if len(winners) == 1:
            winner = winners[0]
            winner.stack_size += pot_size
            print(f"Player {winner.name} wins the pot of {pot_size}.")
        else:
            # Split the pot among the winners
            winnings_per_player = pot_size // len(winners)
            remainder = pot_size % len(winners)

            for winner in winners:
                winner.stack_size += winnings_per_player

            # Distribute any remaining chips
            for i in range(remainder):
                winners[i].stack_size += 1

            print("The pot was split among multiple winners.")

        # Update pot values
        pot['pot_value'] = 0
        # Remove this player from the eligible players for this pot
        pot['eligible_players'].remove(player)




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
