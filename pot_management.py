class PotManagement:
    def __init__(self, blinds_and_ante):
        self.small_blind, self.big_blind, self.ante = blinds_and_ante
        self.pots = [{'amount': 0, 'players': []}]

    def increase_blinds(self):
        self.current_blind *= self.blind_increase_rate

    def collect_blinds(self, players):
        small_blind_player = players[0]
        big_blind_player = players[1]

        # Collect blinds
        small_blind_amount = min(small_blind_player.stack_size, self.small_blind)
        big_blind_amount = min(big_blind_player.stack_size, self.big_blind)
        
        small_blind_player.bet(small_blind_amount)
        big_blind_player.bet(big_blind_amount)

        # Add blinds to the main pot
        self.pots[0]['amount'] += small_blind_amount + big_blind_amount

    def collect_antes(self, players):
        for player in players:
            ante_amount = min(player.stack_size, self.ante)
            player.bet(ante_amount)
            self.pots[0]['amount'] += ante_amount

    def handle_bets(self, players):
        # This function should be called after each round of betting
        # It assumes that the 'current_bet' of each player is the total amount they have bet in this round
        highest_bet = max(player.current_bet for player in players)

        for player in players:
            bet = player.current_bet
            if bet < highest_bet and player.stack_size > 0:
                # This player needs to be isolated into a side pot
                self.pots.append({'amount': bet * len(self.pots[0]['players']), 'players': self.pots[0]['players']})
                self.pots[0]['players'].remove(player)
                self.pots[0]['amount'] -= bet * (len(self.pots[0]['players']) + 1)
            elif bet > 0:
                self.pots[0]['amount'] += bet

            player.current_bet = 0  # Reset the player's current bet

    def distribute_pots(self, ranked_players):
        # This function should be called at the end of a hand
        # It assumes 'ranked_players' is a list of players in order from winner to loser
        for pot in self.pots[::-1]:  # Start distributing from the last side pot
            for player in ranked_players:
                if player in pot['players']:
                    # This player has won the pot
                    winnings = pot['amount'] // len(pot['players'])
                    player.stack_size += winnings
                    pot['amount'] -= winnings

        self.pots = [{'amount': 0, 'players': []}]  # Reset the pots



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
