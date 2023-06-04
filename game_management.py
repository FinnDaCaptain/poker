from poker_game import PokerGame
from deck_management import DeckManager
from individual_player import Player
from player_model import Model, PlayerModel, PlayerModelManager
from table_management import TableManagement
from pot_management import PotManagement, BlindStructure
from table_config import TableConfig
from poker_hand import PokerHand


class StateMachine:
    def __init__(self, table_name, num_players, buy_in):
        self.num_players = num_players
        self.winning_players = None

        self.all_players = []
        self.active_players = []
        self.eligible_players = []
        self.ranked_players = []
        self.community_cards = []
        self.shuffled_deck = []

        self.table_name = table_name
        self.table_manager = TableManagement(self.table_name)
        self.table_config = TableConfig().cash_configs[self.table_name]

        self.table_manager.add_table(self.table_name, self.table_config)
        self.table = self.table_manager.tables[self.table_name]
        self.starting_stack = self.table_config[buy_in] * self.table_config['blinds'][1]

        # Add players to the table
        for i in range(self.num_players):
            model = Model(f"Model{i+1}")  # Create a new model for each player
            player = Player(f"Player {i+1}", self.starting_stack, model)
            self.table_manager.add_player(player, self.table)
   
        self.community_pot = self.table['community_pot']
        self.side_pots = self.table['side_pots']
        self.active_players = self.table['player_activity']['active_players']
        self.all_players = self.table['seats']
        self.eligible_players = self.table['community_pot']['eligible_players']
        self.blinds = self.table_config['blinds']
        self.small_blind, self.big_blind, self.ante = self.blinds

        self.deck_manager = DeckManager(self.active_players, self.shuffled_deck)  # Initialize an instance of DeckManager
        self.pot_manager = PotManagement(self.table_manager, self.community_pot, self.side_pots, self.ranked_players, self.eligible_players, self.active_players, self.ante, self.small_blind, self.big_blind)  # Initialize PotManagement
        self.poker_hand = PokerHand()
        
        self.streets = {
            'preflop': {
                'name': 'preflop',
                'num_cards': 0,
            },
            'flop': {
                'name': 'flop',
                'num_cards': 3,
            },
            'turn': {
                'name': 'turn',
                'num_cards': 1,
            },
            'river': {
                'name': 'river',
                'num_cards': 1,
            }
        }
        
        self.state_actions = {
            'setup': self.setup,
            'deal_hole_cards': self.deal_hole_cards,
            'preflop': self.preflop,
            'flop': self.flop,
            'turn': self.turn,
            'river': self.river,
            'early_finish': self.early_finish,
            'showdown': self.showdown,
            'hidden_end': self.hidden_end,
            'payout': self.payout,
            'reset': self.reset,
            'wait': self.wait,
        }

        # Initialize the game
        self.game = PokerGame(self.table_manager, self.table, self.poker_hand, self.blinds, self.community_cards, self.community_pot, self.side_pots)
        
        # Setting the initial state
        self.state = 'setup'


    def street_rotation(self, street_name):

        new_cards, self.shuffled_deck = self.deck_manager.deal_cards(self.shuffled_deck, self.streets[street_name]['num_cards'])
        self.community_cards.extend([self.deck_manager.get_card_string(card) for card in new_cards])

        for player in self.active_players:    
            player.current_hand_rank = self.poker_hand.evaluate_hand(player.hole_cards, self.community_cards)

        self.active_players, self.eligible_players = self.game.betting_round(self.streets[street_name],self.community_cards, self.active_players, self.eligible_players)

        while any(player.is_all_in and player.is_eligible_for_pot for player in self.active_players) and len(self.active_players) >= 3:
            self.side_pots = self.pot_manager.create_side_pot()
        
        # Calculate the number of players who are not all in
        not_all_in_count = len([player for player in self.active_players if not player.is_all_in])

        # Check if only one active player remains, if so, they are the winner
        if len(self.active_players) == 1:                        
            self.state = 'hidden_end'
            return 

        # Check if all players are all in or if there is only one player who is not all in
        elif not_all_in_count == 1 or all(player.is_all_in for player in self.active_players):
            self.state = 'early_finish'
            return


        # Reset last bet for all players after each betting round
        for player in self.active_players:
            player.last_bet = 0
            player.round_bet = 0
            player.has_acted = False        


    def setup(self):
        self.active_players = self.table_manager.get_active_players()
        self.eligible_players = self.table_manager.update_player_eligibility()

        # set blinds and button
        self.table_manager.advance_button(self.table_manager, self.table_name)
        
        # Collect blinds and antes at the start of the game
        self.pot_manager.collect_antes()
        self.pot_manager.collect_blinds()

        self.state = 'deal_hole_cards'
        

    def deal_hole_cards(self):
        # Create deck
        self.deck = self.deck_manager.create_deck()
        self.shuffled_deck = self.deck_manager.shuffle_deck(self.deck)

        for player in self.active_players:
            while len(player.hole_cards) < 2:
                # Use the DeckManager to draw one card and convert it to a string
                card, self.shuffled_deck = self.deck_manager.deal_cards(self.shuffled_deck, 1)
                player.hole_cards.append(self.deck_manager.get_card_string(card[0]))  # Append the dealt card to the player's hole cards

        self.state = 'preflop'
        

    def preflop(self):
        self.street_rotation(self.streets['preflop']['name'])
        if self.state in ['hidden_end', 'early_finish']:  # Check if the state has changed within the street_rotation call
            return  # If it has, return immediately to avoid proceeding to the next state
        self.state = 'flop'


    def flop(self):
        self.street_rotation(self.streets['flop']['name'])
        if self.state in ['hidden_end', 'early_finish']:
            return
        self.state = 'turn'

    def turn(self):
        self.street_rotation(self.streets['turn']['name'])
        if self.state in ['hidden_end', 'early_finish']:
            return
        self.state = 'river'

    def river(self):
        self.street_rotation(self.streets['river']['name'])
        if self.state in ['hidden_end', 'early_finish']:
            return
        self.state = 'showdown'

    
    def early_finish(self):
        print("All players ready to end")

        while len(self.community_cards) < 5:
            card, self.shuffled_deck = self.deck_manager.draw_card(self.shuffled_deck)
            self.community_cards.append(self.deck_manager.get_card_string(card))

        self.state = 'showdown'


    def showdown(self):
        self.ranked_players = self.game.evaluate_showdown(self.active_players)
        self.state = 'payout'
    

    def hidden_end(self):
        print(f"All players have folded, {self.active_players[0].name} is the winner")

        self.ranked_players = self.active_players
        self.state = 'payout'
    

    def payout(self):
        self.pot_manager.distribute_pots(self.ranked_players)
        self.state = 'reset'
    
    
    def reset(self):
        for player in self.all_players:
            if player is None or player.is_sitting_out:
                continue
            if player.stack_size == 0:
                self.table_manager.remove_player(player, self.table_name)
            player.reset_for_new_hand()
        self.ranked_players = []
        self.community_cards = []
       
        self.state = 'setup'  # back to deal state for the next hand


    def wait(self):
        # code for enough players to join table
        self.state = 'setup'
    

    def run_game(self):
        while True:
            try:
                state_action = self.state_actions[self.state]
                state_action()
            except KeyError:
                raise ValueError(f"Invalid state: {self.state}")













class SpinAndGo():
    def __init__(self, blind_structure, initial_stack):
        pass


class HeadsUp():
    def __init__(self, blind_structure):
        pass

class Tournament():
    def __init__(self, max_seats, initial_stack, starting_players, level_durations=None):
        pass