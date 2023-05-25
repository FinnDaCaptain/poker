from poker_game import PokerGame
from deck_management import DeckManager
from individual_player import Player
from player_model import Model, PlayerModel, PlayerModelManager
from table_management import TableManagement
from pot_management import PotManagement, BlindStructure
from table_config import TableConfig
from poker_hand import PokerHand


class CashGame:
    def __init__(self, table_name, num_players, buy_in):
        self.num_players = num_players
        self.community_cards = []
        self.shuffled_deck = []
        self.table_manager = TableManagement(table_name)
        self.table_name = table_name
        self.table_config = TableConfig().cash_configs[self.table_name]
        self.table_manager.add_table(self.table_name, self.table_config)
        self.table = self.table_manager.tables[table_name]
        self.starting_stack = self.table_config[buy_in] * self.table_config['blinds'][1]

        # Add players to the table
        for i in range(self.num_players):
            model = Model(f"Model{i+1}")  # Create a new model for each player
            player = Player(f"Player{i+1}", self.starting_stack, model)
            self.table_manager.add_player(player, self.table)
   
        self.community_pot = self.table['community_pot']
        self.side_pots = self.table['side_pots']
        self.ranked_players = []
        self.active_players = self.table_manager.tables[table_name]['player_activity']['active_players']
        self.all_players = self.table['seats']
        self.eligible_players = self.table['community_pot']['eligible_players']
        self.blinds = self.table_config['blinds']
        self.small_blind, self.big_blind, self.ante = self.blinds

        self.deck_manager = DeckManager()  # Initialize an instance of DeckManager
        self.pot_manager = PotManagement(self.table, self.community_pot, self.side_pots, self.ranked_players, self.eligible_players, self.active_players)  # Initialize PotManagement
        self.poker_hand = PokerHand()

        # Initialize the game
        self.game = PokerGame(self.table_manager, self.ranked_players, self.community_cards, self.community_pot, self.side_pots, self.active_players, self.eligible_players)

    def run_game(self):
        self.active_players = self.table_manager.get_active_players()
        self.eligible_players = self.table_manager.update_player_eligibility()
       
        # Game loop
        while len(self.active_players) >= 2:  # end game if not enough players for a hand
            # set blinds and button
            self.table_manager.advance_button(self.table_manager, self.table_name)
            
            self.community_cards = []
            bet_to_match = 0
            
            # Create deck
            self.deck = self.deck_manager.create_deck()
            self.shuffled_deck = self.deck_manager.shuffle_deck(self.deck)
            
            # Deal Cards
            for player in self.active_players:
                # Use the DeckManager to draw cards and convert them to strings
                cards, self.shuffled_deck = self.deck_manager.deal_cards(self.shuffled_deck, 2)
                player.hole_cards = [self.deck_manager.get_card_string(card) for card in cards]

            # Collect blinds and antes at the start of the game
            self.pot_manager.collect_antes(self.ante)
            self.pot_manager.collect_blinds(self.small_blind, self.big_blind)

            # Define the streets and the number of community cards to deal for each one
            streets = [('preflop', 0), ('flop', 3), ('turn', 1), ('river', 1)]

            for street, num_cards in streets:
                if num_cards > 0:  # If there are community cards to be dealt for this street
                    new_cards, self.shuffled_deck = self.deck_manager.deal_cards(self.shuffled_deck, num_cards)
                    self.community_cards.extend([self.deck_manager.get_card_string(card) for card in new_cards])

                # Find the big blind and dealer position from all seats (not just active players)
                all_players , starting_player_index, bet_to_match = self.table_manager.set_start_index(street, self.table, self.big_blind)

                while True:
                    for i in range(starting_player_index, starting_player_index + len(all_players)):
                        
                        self.active_players = self.table_manager.get_active_players()
                        self.eligible_players = self.table_manager.update_player_eligibility()
                    
                        player_index = i % len(all_players)
                        player = all_players[player_index]

                        # Skip if the seat is empty or player is sitting out
                        if player is None or player.is_sitting_out:
                            continue

                        # Add a check here for game end conditions. If the conditions are met, return.
                        if self.game.check_end_conditions():
                            return bet_to_match

                        if player.is_all_in or (player.has_acted and player.total_bet == bet_to_match) or player.is_folded:
                            continue

                        action = player.make_decision(bet_to_match, street, self.community_cards, self.community_pot, self.side_pots, self.active_players, self.eligible_players)

                        # Run betting round for this street
                        bet_to_match = self.game.betting_round(player, action, bet_to_match, street)

                        if player.last_bet >= bet_to_match and player.is_eligible_for_pot:
                            if player.name not in [p.name for p in self.eligible_players]:
                                self.table_manager.update_player_eligibility(player, self.community_pot)

                        self.community_pot['pot_value'] += player.last_bet  # Update the main pot with the current bet

                    # If a player raises or goes all in, the bet to match changes and all players should get another chance to act
                    if player is not None and player.total_bet > bet_to_match:
                        bet_to_match = player.total_bet
                        for player in self.active_players:
                            if not player.is_all_in and player.is_eligible_for_pot:
                                player.has_acted = False  # Reset has_acted for all players who can still act

                    # If all players have either matched the current bet, gone all in, or folded, end the round
                    if all((player.round_bet >= bet_to_match or player.is_all_in or player.is_folded) for player in self.active_players):
                        break

                    # Handle side pots
                    while any(player.is_all_in for player in self.eligible_players) and len(self.eligible_players) >= 3:
                        self.pot_manager.handle_bets()


                # If game end conditions are met, finish the game and return
                if self.game.check_end_conditions():
                    self.game.finish_game(self.deck_manager, self.poker_hand, self.pot_manager, self.shuffled_deck)
                    return

                # Reset last bet for all players after each betting round
                for player in self.active_players:
                    player.last_bet = 0
                    player.round_bet = 0
                    player.has_acted = False

            # If game reaches this point, we've gone through all betting rounds. Time for showdown.
            self.game.finish_game(self.deck_manager, self.poker_hand, self.pot_manager, self.shuffled_deck)

            #reset all players after game                        
            for player in self.active_players:
                if player.stack_size == 0:
                    self.table_manager.remove_player(player, self.table_name)
                player.reset_for_new_hand()
                self.table_manager.get_active_players()
            
            print(f"Hand completed.")

        print("Cash game completed!")








class SpinAndGo():
    def __init__(self, blind_structure, initial_stack):
        super().__init__(3, blind_structure)  # Spin and Go is always 3 players
        self.initial_stack = initial_stack
        for player in self.table.players:
            player.stack = self.initial_stack


class HeadsUp():
    def __init__(self, blind_structure):
        super().__init__(2, blind_structure)  # Heads up is always 2 players


class Tournament():
    def __init__(self, max_seats, initial_stack, starting_players, level_durations=None):
        self.current_blind_level = 0
        self.initial_stack = initial_stack
        self.blind_structure = BlindStructure()
        self.starting_players = starting_players
        self.active_players = starting_players
        for i in range(starting_players):
            player_name = f"Player {i + 1}"
            self.table.add_player(Player(player_name, self.initial_stack))
