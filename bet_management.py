class BetManagement:  
    def __init__(self, table, table_name, table_manager):
        self.table = table
        self.table_name = table_name
        self.table_manager = table_manager
        self.all_players = self.table['seats']

    def betting_round(self, street):

            # Find the big blind and dealer position from all seats (not just active players)
            big_blind_index = None
            dealer_index = None
            for i, player in enumerate(self.all_players):
                if player is not None:
                    if player.is_big_blind:
                        big_blind_index = i
                    if player.is_dealer:
                        dealer_index = i


            if street == 'preflop':
                # The player to the left of the big blind starts on preflop
                starting_player_index = (big_blind_index + 1) % len(self.all_players)
                bet_to_match = self.big_blind
            else:
                # The player to the left of the dealer starts on all other streets
                starting_player_index = (dealer_index + 1) % len(self.all_players)
                bet_to_match = 0

            # Ensure the starting player is not None
            while self.all_players[starting_player_index] is None:
                starting_player_index = (starting_player_index + 1) % len(self.all_players)

            while True:
                for i in range(starting_player_index, starting_player_index + len(self.all_players)):
                    active_players = self.table_manager.get_active_players(self.table_name)
                    eligible_players = self.table_manager.update_player_eligibility(active_players, self.table_name)

                    player_index = i % len(self.all_players)
                    player = self.all_players[player_index]

                    # Skip if the seat is empty or player is sitting out
                    if player is None or player.is_sitting_out:
                        continue

                    # Add a check here for game end conditions. If the conditions are met, return.
                    if self.check_end_conditions(bet_to_match):
                        return bet_to_match

                    if player.is_all_in or (player.has_acted and player.total_bet >= bet_to_match) or player.is_folded:
                        continue

                    action = player.make_decision(bet_to_match, street, self.community_cards, self.community_pot['pot_value'], self.side_pots, active_players, eligible_players)

                    if action.type == "FOLD":
                        player.fold(self.table)

                    elif action.type == "CHECK":
                        player.check(bet_to_match)

                    elif action.type == "CALL":
                        player.call(bet_to_match)

                    elif action.type == "BET":
                        if bet_to_match != 0:
                            print("Must Call or Raise previous Bets, please enter a valid command")
                            return player.make_decision(bet_to_match, street, self.community_cards, self.community_pot['pot_value'], self.side_pots)
                        else:
                            amount = int(input("Please enter an amount to bet: "))
                            player.bet(amount)
                            if player.last_bet > bet_to_match:
                                bet_to_match = player.last_bet

                    elif action.type == "RAISE":
                        min_raise = 2 * bet_to_match
                        raise_amount = int(input("Please enter an amount to raise: ")) 

                        if raise_amount < min_raise:
                            print("Raise amount is too small. The minimum raise is: ", min_raise)
                            return player.make_decision(bet_to_match, street, self.community_cards, self.community_pot['pot_value'], self.side_pots)

                        elif raise_amount > player.stack_size:
                            print(f"{player.name} does not have enough chips to raise. Going all-in.")
                            player.last_bet = player.all_in()  # Player goes all-in if they don't have enough chips

                        else:
                            player.last_bet = player.raise_bet(raise_amount)

                        if player.last_bet > bet_to_match:
                            bet_to_match = player.last_bet

                    elif action.type == "ALL_IN":
                        player.last_bet = player.all_in()
                        if player.last_bet > bet_to_match:
                            bet_to_match = player.last_bet

                    player.has_acted = True  # Mark player as having acted this round
                    
                    if player.last_bet >= bet_to_match and player.is_eligible_for_pot:
                        if player.name not in [p.name for p in self.community_pot['eligible_players']]:
                            self.table_manager.update_player_eligibility(player, self.community_pot)

                    self.community_pot['pot_value'] += player.last_bet  # Update the main pot with the current bet

                # If a player raises or goes all in, the bet to match changes and all players should get another chance to act
                if player is not None and player.total_bet > bet_to_match:
                    bet_to_match = player.total_bet
                    for player in active_players:
                        if not player.is_all_in and player.is_eligible_for_pot:
                            player.has_acted = False  # Reset has_acted for all players who can still act

                # If all players have either matched the current bet, gone all in, or folded, end the round
                if all((player.total_bet >= bet_to_match or player.is_all_in or player.is_folded) for player in active_players):
                    break

                # Handle side pots
                while any(player.is_all_in for player in self.community_pot['eligible_players']) and len(self.community_pot['eligible_players']) >= 3:
                    self.pot_manager.handle_bets(self.community_pot['eligible_players'], active_players)