class PokerGame:
    def __init__(self, table_manager, ranked_players, community_cards, community_pot, side_pots, active_players, eligible_players):
        self.table_manager = table_manager
        self.ranked_players = ranked_players
        self.community_cards = community_cards
        self.community_pot = community_pot
        self.side_pots = side_pots
        self.active_players = active_players
        self.eligible_players = eligible_players

    def betting_round(self, player, action, bet_to_match, street):

        if action.type == "FOLD":
            player.fold(self.eligible_players)

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

        return bet_to_match
        


    def evaluate_showdown(self, poker_hand, pot_manager):
        # Determine the winners and distribute the pot(s)
        best_hands = []
        self.ranked_players = []
        for player in self.active_players:
            if not player.is_folded:  # Only consider players who haven't folded
                hole_cards = player.hole_cards
                best_hand = poker_hand.evaluate_hand(hole_cards, self.community_cards)
                best_hands.append((player, best_hand))

        # Sort the best hands in descending order based on hand rank and relevant card ranks
        best_hands.sort(key=lambda x: x[1], reverse=True)

        self.ranked_players = [player_hand[0] for player_hand in best_hands]  # Store only player objects in ranked_players

        # Determine the winners
        highest_hand_rank = best_hands[0][1]
        winners = [player_hand for player_hand in best_hands if player_hand[1] == highest_hand_rank]

        # Handle ties
        if len(winners) > 1:
            highest_hand_cards = winners[0][1][1]  # The card ranks associated with the highest hand
            winners = [player_hand for player_hand in winners if player_hand[1][1] == highest_hand_cards]

        winners = [winner[0] for winner in winners]  # We only want the player objects in the winners list
        print("Congratulations, the winners are: " + ', '.join(str(winner.name) for winner in winners))

        # Distribute the pot(s) accordingly
        pot_manager.distribute_pots(self.ranked_players)



    def check_end_conditions(self):
        active_players = self.table_manager.get_active_players()
        active_not_folded_players = [player for player in active_players if not player.is_folded]
        active_not_all_in_players = [player for player in active_players if not player.is_all_in]
        highest_bet = max(player.total_bet for player in active_players)
        bet_to_match = highest_bet
        if len(active_not_folded_players) == 1:
            remaining_player = active_not_folded_players[0]
            print(f"Congratulations, the winner is: {remaining_player.name}")
            self.hidden_end()  # Call hidden_end when all other players have folded
            return True
    
        elif len(active_not_all_in_players) == 1:
            remaining_player = active_not_all_in_players[0]
            if remaining_player not in self.eligible_players:
                self.table_manager.update_player_eligibility()
            return True

        elif all(player.total_bet >= highest_bet for player in active_players):
            return bet_to_match

        else: 
            return False



    def finish_game(self, deck_manager, poker_hand, pot_manager, shuffled_deck):
        # Finish the game by dealing remaining community cards
        while len(self.community_cards) < 5:
            card, shuffled_deck = deck_manager.draw_card(shuffled_deck)
            self.community_cards.append(deck_manager.get_card_string(card))

        print("All players ready to end")
        # Showdown
        self.evaluate_showdown(poker_hand, pot_manager)


    def hidden_end(self):
        # Identify the player who hasn't folded
        remaining_player = next(player for player in self.table_manager.get_active_players() if not player.is_folded)

        # Add the pot to the remaining player's stack
        remaining_player.stack_size += self.community_pot['pot_value']

        print(f"All other players have folded. {remaining_player.name} wins the pot of {self.community_pot['pot_value']}.")

        # Reset the community pot
        self.community_pot['pot_value'] = 0

        # Reset all players' status for the new hand
        for player in self.active_players:
            player.reset_for_new_hand()

