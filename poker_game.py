class PokerGame:
    def __init__(self, table_manager, table, poker_hand, blinds, community_cards, community_pot, side_pots):
        self.table_manager = table_manager
        self.table = table
        self.poker_hand = poker_hand
        self.community_cards = community_cards
        self.community_pot = community_pot
        self.side_pots = side_pots

        self.bet_to_match = 0
        self.last_raise = 0
        self.bet_counter = 0

        self.small_blind, self.big_blind, self.ante = blinds


    def player_info_print(self, player, street, bet_to_match, community_cards, community_pot, side_pots):
        print("\nIt's your turn, {}.".format(player.name))
        print("Your hole cards are: ", [str(card) for card in player.hole_cards])
        print("Your current Hand Rank is: ", player.current_hand_rank )
        print("Your current stack is: ", player.stack_size)
        print("Current bet to match is: ", bet_to_match)
        print("Your current bet is: ", player.round_bet)
        print("Current street is: ", street)
        print("Community cards are: ", [str(card) for card in community_cards])
        print("Community pot size is: ", community_pot['pot_value'])
        print("Side pots are: ", side_pots)


    def betting_action(self, player, action, eligible_players):
        if action.type == "FOLD":
            player.fold(eligible_players)

        elif action.type == "CHECK":
            player.check(action.amount)

        elif action.type == "CALL":
            player.call(action.amount)

        elif action.type == "BET":
            player.bet(action.amount)            
            self.bet_counter += 1

        elif action.type == "RAISE":
            player.raise_bet(action.amount)
            self.last_raise = player.last_bet - self.bet_to_match
            self.bet_counter += 1

        elif action.type == "ALL_IN":
            player.all_in()
        
        if player.last_bet > self.bet_to_match:
            self.bet_to_match = player.last_bet

        player.has_acted = True  # Mark player as having acted this round

        
    def betting_round(self, street, community_cards, active_players, eligible_players):
        # Find the big blind and dealer position from all seats (not just active players)
        all_players , starting_player_index, self.bet_to_match = self.table_manager.set_start_index(street['name'], self.table, self.big_blind)
        
        while any([player for player in active_players if not player.is_all_in and not player.has_acted]) and len(active_players) > 1:
            for i in range(starting_player_index, starting_player_index + len(all_players)):
                
                player_index = i % len(all_players)
                player = all_players[player_index]

                # Skip if the seat is empty, player is sitting out or folded
                if player is None or player.is_sitting_out or player.is_folded:
                    continue

                if player.is_all_in or (player.has_acted and player.round_bet == self.bet_to_match) :
                    continue

                if len(active_players) == 1:
                    break

                self.player_info_print(player, street['name'], self.bet_to_match, community_cards, self.community_pot, self.side_pots)
                
                action = player.make_decision(self.big_blind, self.bet_to_match, self.last_raise)

                # Calculate betting action
                self.betting_action(player, action, eligible_players)

                self.community_pot['pot_value'] += player.last_bet  # Update the main pot with the last bet

                for player in active_players:
                    if not player.is_all_in and player.has_acted and player.round_bet < self.bet_to_match:
                        player.has_acted = False  # Reset has_acted for all players who can still act

                active_players = self.table_manager.get_active_players()
                eligible_players = self.table_manager.update_player_eligibility()

        self.bet_to_match = 0
        self.last_raise = 0
        self.raise_counter = 0

        return active_players, eligible_players


    def evaluate_showdown(self, active_players):
        # Determine the winners and distribute the pot(s)
        best_hands = []
        for player in active_players:
            best_hands.append((player))

        # Sort the best hands in descending order based on hand rank and relevant card ranks
        ranked_players = self.poker_hand.sort_players_by_hand_rank(best_hands)

        winners = ranked_players[0]  # We only want the player objects in the first group

        # Check if there is a tie
        if len(winners) > 1:
            print("It's a tie between: " + ', '.join(str(winner.name) for winner in winners))
        else:
            print("Congratulations, the winner is: " + winners[0].name)

        return ranked_players
