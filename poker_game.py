from collections import Counter
from deck_management import DeckManager
from pot_management import PotManagement, BlindStructure

class PokerGame:
    def __init__(self, players, shuffled_deck, blind_structure):
        self.current_player_index = 0
        self.community_cards = []
        self.players = players  # Assign players passed from the main logic
        self.shuffled_deck = shuffled_deck
        self.small_blind, self.big_blind, self.ante = blind_structure
        self.deck_manager = DeckManager()  # Initialize an instance of DeckManager
        self.pot_manager = PotManagement(blind_structure)  # Initialize PotManagement
        
    # Winning hand tier list for hand evaluation
    WINNING_HANDS = [
        "High Card",
        "One Pair",
        "Two Pair",
        "Three of a Kind",
        "Straight",
        "Flush",
        "Full House",
        "Four of a Kind",
        "Straight Flush",
        "Royal Flush"
    ]


    def start_game(self):
        # Initialize the game
        for player in self.players:
            # Use the DeckManager to draw cards and convert them to strings
            cards, self.shuffled_deck = self.deck_manager.deal_cards(self.shuffled_deck, 2)
            player.hole_cards = [self.deck_manager.get_card_string(card) for card in cards]
        
        # Collect blinds and antes at the start of the game
        self.pot_manager.collect_antes(self.players)
        self.pot_manager.collect_blinds(self.players)

        # Betting round: Preflop
        self.betting_round('preflop')
        if not self.remaining_players():  # if all players are all in
            self.finish_game()
            return

        # Betting round: Flop
        self.community_cards.extend([self.deck_manager.get_card_string(card) for card in self.deck_manager.deal_cards(3)])
        self.betting_round('flop')
        if not self.remaining_players():  # if all players are all in
            self.finish_game()
            return

        # Betting round: Turn
        self.community_cards.extend([self.deck_manager.get_card_string(card) for card in self.deck_manager.deal_cards(1)])
        self.betting_round('turn')
        if not self.remaining_players():  # if all players are all in
            self.finish_game()
            return

        # Betting round: River
        self.community_cards.extend([self.deck_manager.get_card_string(card) for card in self.deck_manager.deal_cards(1)])
        self.betting_round('river')

        # Showdown
        self.evaluate_showdown()

    def finish_game(self):
        # Finish the game by dealing remaining community cards
        while len(self.community_cards) < 5:
            card, self.shuffled_deck = self.deck_manager.draw_card(self.shuffled_deck)
            self.community_cards.append(self.deck_manager.get_card_string(card))

        # Showdown
        self.evaluate_showdown()


    def betting_round(self, stage):
        # Determine the active players who are still in the hand
        active_players = [player for player in self.players if not player.is_folded]

        # Initialize the betting variables
        bet_to_match = self.big_blind
        last_raised_amount = 0
        current_bet = 0
        round_complete = False


        while not round_complete:
            for player in active_players:
                if player.is_all_in:
                    continue

                if current_bet > player.current_bet:
                    action = player.make_decision(current_bet)
                else:
                    action = player.make_decision(bet_to_match)

                if action == "fold":
                    player.is_folded = True
                    active_players.remove(player)
                    if len(active_players) == 1:
                        round_complete = True
                    continue

                if action == "check":
                    pass

                if action == "bet":
                    min_bet = self.big_blind
                    max_bet = player.stack_size
                    bet_amount = player.determine_bet_amount(min_bet, max_bet)
                    if bet_amount < min_bet:
                        bet_amount = min_bet
                    elif bet_amount > max_bet:
                        bet_amount = max_bet
                    self.pot_manager.handle_bets([player])
                    player.update_stack(-bet_amount)
                    player.current_bet = bet_amount
                    current_bet = bet_amount

                if action == "call":
                    amount = current_bet - player.current_bet
                    if amount >= player.stack_size:
                        amount = player.stack_size
                        player.is_all_in = True
                    self.pot_manager.handle_bets([player])
                    player.update_stack(-amount)
                    player.current_bet = current_bet

                    # Refund excess bet to the initial player
                    for p in active_players:
                        if p.current_bet > current_bet and p.current_bet < player.current_bet:
                            excess_amount = p.current_bet - current_bet
                            p.update_stack(excess_amount)
                            self.pot_manager.update_pots(-excess_amount)

                if action == "raise":
                    min_raise = last_raised_amount + (2 * self.big_blind)
                    max_raise = player.stack_size
                    raise_amount = player.determine_raise_amount(min_raise, max_raise)
                    if raise_amount < min_raise:
                        raise_amount = min_raise
                    elif raise_amount > max_raise:
                        raise_amount = max_raise
                    amount = raise_amount - player.current_bet
                    if amount >= player.stack_size:
                        amount = player.stack_size
                        player.is_all_in = True
                    self.pot_manager.handle_bets([player])
                    player.update_stack(-amount)
                    player.current_bet = raise_amount
                    current_bet = raise_amount
                    last_raised_amount = raise_amount

            # Check if the betting round is complete
            if all(player.current_bet == current_bet for player in active_players) or len(active_players) == 1:
                round_complete = True

        # Update the pots after the betting round
        self.pot_manager.handle_bets(active_players)


    def evaluate_hand(self, all_cards):
        # all_cards is a list of tuples representing cards
        # The first element of each tuple is the rank, and the second element is the suit

        # Get a list of all the ranks and suits of the cards
        all_card_ranks = sorted([card[0] for card in all_cards], reverse=True)
        all_card_suits = [card[1] for card in all_cards]

        # Count the occurrences of each rank and suit
        rank_counter = Counter(all_card_ranks)
        suit_counter = Counter(all_card_suits)

        # Check for royal flush
        if all(rank in all_card_ranks for rank in range(8, 13)) and max(suit_counter.values()) >= 5:
            return (9, [])

        # Check for straight flush
        for rank in range(7, -1, -1):
            if all(r in all_card_ranks for r in range(rank, rank + 5)) and max(suit_counter.values()) >= 5:
                return (8, [rank + 4])

        # Check for four of a kind
        if 4 in rank_counter.values():
            four_rank = [rank for rank, count in rank_counter.items() if count == 4][0]
            other_rank = [rank for rank in all_card_ranks if rank != four_rank][0]
            return (7, [four_rank, other_rank])

        # Check for full house
        if 3 in rank_counter.values() and 2 in rank_counter.values():
            three_rank = [rank for rank, count in rank_counter.items() if count == 3][0]
            pair_rank = [rank for rank, count in rank_counter.items() if count == 2][0]
            return (6, [three_rank, pair_rank])

        # Check for flush
        if max(suit_counter.values()) >= 5:
            flush_ranks = sorted([rank for rank, suit in all_cards if suit == max(suit_counter, key=suit_counter.get)], reverse=True)[:5]
            return (5, flush_ranks)

        # Check for straight
        for rank in range(8, -1, -1):
            if all(r in all_card_ranks for r in range(rank, rank + 5)):
                return (4, [rank + 4])

        # Check for three of a kind
        if 3 in rank_counter.values():
            three_rank = [rank for rank, count in rank_counter.items() if count == 3][0]
            other_ranks = [rank for rank in all_card_ranks if rank != three_rank][:2]
            return (3, [three_rank] + other_ranks)

        # Check for two pair
        if list(rank_counter.values()).count(2) >= 2:
            pair_ranks = sorted([rank for rank, count in rank_counter.items() if count == 2], reverse=True)[:2]
            other_rank = [rank for rank in all_card_ranks if rank not in pair_ranks][0]
            return (2, pair_ranks + [other_rank])

        # Check for one pair
        if 2 in rank_counter.values():
            pair_rank = [rank for rank, count in rank_counter.items() if count == 2][0]
            other_ranks = [rank for rank in all_card_ranks if rank != pair_rank][:3]
            return (1, [pair_rank] + other_ranks)

        # Check for high card
        high_card_ranks = sorted(all_card_ranks, reverse=True)[:5]
        return (0, high_card_ranks)


    def evaluate_showdown(self):
        # Determine the winners and distribute the pot(s)
        best_hands = []
        for player in self.players:
            if not player.is_folded:  # Only consider players who haven't folded
                hole_cards = player.hole_cards
                all_cards = hole_cards + self.community_cards
                best_hand = self.evaluate_hand(all_cards)
                best_hands.append((player, best_hand))

        # Sort the best hands in descending order based on hand rank and relevant card ranks
        best_hands.sort(key=lambda x: x[1], reverse=True)

        # Determine the winners
        highest_hand_rank = best_hands[0][1]
        winners = [player_hand[0] for player_hand in best_hands if player_hand[1] == highest_hand_rank]

        # Distribute the pot(s) accordingly
        self.pot_manager.distribute_pots(winners)


    def update_current_player(self):
        # Move to the next player
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        
        # Skip players who have folded or are all in
        while self.players[self.current_player_index].is_folded or self.players[self.current_player_index].is_all_in:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
        
        # Set the current player
        self.current_player = self.players[self.current_player_index]

    #def switch_to_gpu(self):
        # Switch relevant data structures to cupy arrays for GPU computations
        # Convert necessary computations to use cupy functions

    #def switch_to_cpu(self):
        # Switch relevant data structures back to numpy arrays or Python lists for CPU computations

    # Other helper methods and functionalities as needed


       
class GameState:
    def __init__(self, num_players):
        self.num_players = num_players
        self.player_positions = [0] * num_players  # Current positions of the players (0 to num_players-1)
        self.player_stacks = [1000] * num_players  # Current chip stacks of the players
        self.current_pot = 0  # Current size of the pot
        self.community_cards = []  # List of community cards
        self.betting_round = 0  # Current betting round (0 for pre-flop, 1 for flop, 2 for turn, 3 for river)
        self.bets = [0] * num_players  # Current bets of each player
        self.is_folded = [False] * num_players  # Flags indicating whether each player has folded
        self.is_all_in = [False] * num_players  # Flags indicating whether each player is all-in
        self.previous_actions = []  # List of previous actions in the current betting round

    def get_active_players(self):
        """Returns a list of active players who have not folded or are not all-in."""
        active_players = []
        for i in range(self.num_players):
            if not self.is_folded[i] and not self.is_all_in[i]:
                active_players.append(i)
        return active_players

    def get_player_position(self, player_index):
        """Returns the position of the specified player."""
        return self.player_positions[player_index]

    def get_player_stack(self, player_index):
        """Returns the chip stack of the specified player."""
        return self.player_stacks[player_index]

    def get_current_pot(self):
        """Returns the size of the current pot."""
        return self.current_pot

    def get_community_cards(self):
        """Returns the list of community cards."""
        return self.community_cards

    def get_betting_round(self):
        """Returns the current betting round."""
        return self.betting_round

    def get_current_bets(self):
        """Returns the current bets of each player."""
        return self.bets

    def get_previous_actions(self):
        """Returns the list of previous actions in the current betting round."""
        return self.previous_actions

    def update_state(self, player_index, action, amount):
        """Updates the game state based on a player's action."""
        self.previous_actions.append((player_index, action, amount))

        if action == "fold":
            self.is_folded[player_index] = True
        elif action == "all-in":
            self.is_all_in[player_index] = True
            self.bets[player_index] += amount
            self.current_pot += amount
        else:
            self.bets[player_index] += amount
            self.player_stacks[player_index] -= amount
            self.current_pot += amount

    def reset_betting_round(self):
        """Resets the state for a new betting round."""
        self.betting_round += 1
        self.bets = [0] * self.num_players
        self.is_folded = [False] * self.num_players
        self.is_all_in = [False] * self.num_players
        self.previous_actions = []

    def reset_game(self):
        """Resets the game state for a new game."""
        self.player_positions = [0] * self.num_players
        self.player_stacks = [1000] * self.num_players
        self.current_pot = 0
        self.community_cards = []
        self.betting_round = 0
        self.bets = [0] * self.num_players
        self.is_folded = [False] * self.num_players
        self.is_all_in = [False] * self.num_players
        self.previous_actions = []

    def clone(self):
        """Creates a deep copy of the game state."""
        cloned_state = GameState(self.num_players)
        cloned_state.player_positions = self.player_positions.copy()
        cloned_state.player_stacks = self.player_stacks.copy()
        cloned_state.current_pot = self.current_pot
        cloned_state.community_cards = self.community_cards.copy()
        cloned_state.betting_round = self.betting_round
        cloned_state.bets = self.bets.copy()
        cloned_state.is_folded = self.is_folded.copy()
        cloned_state.is_all_in = self.is_all_in.copy()
        cloned_state.previous_actions = self.previous_actions.copy()
        return cloned_state

