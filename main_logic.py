from poker_game import PokerGame
from deck_management import DeckManager
from individual_player import Player
from player_model import Model, PlayerModel, PlayerModelManager
from table_management import TableManagement
from pot_management import PotManagement, BlindStructure
from game_management import Tournament, CashGame, SpinAndGo, HeadsUp

import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")



# Global Settings
GAME_TYPE = "cash"  # change this to control the game type
STARTING_STACK = 10000
TABLE_SEATS = 9
MAX_PLAYERS = 9
LEVEL_DURATION = 12 #set to hands for training, minutes for actual use
CASH_BLINDS = (10, 20, 1)  # small blind, big blind, ante

DECK = None

if GAME_TYPE == "tournament":
    # Create a tournament with the set number of seats, starting stack, and max players
    tournament = Tournament(TABLE_SEATS, STARTING_STACK, MAX_PLAYERS, LEVEL_DURATION)

    # Add players to the tournament
    for i in range(MAX_PLAYERS):
        player = Player(f"Player{i+1}", STARTING_STACK)
        tournament.add_player(player)

    # Game loop
    while tournament.active_players > 1:
        tournament.start_hand()
        tournament.advance_blind_level()  # if your structure advances each hand
        print(f"Hand completed. Active players: {tournament.active_players}, Current blinds: {tournament.get_current_blinds()}")

    print("Tournament completed!")



elif GAME_TYPE == "cash":
    # Create CashGame instance
    cash_game = CashGame(TABLE_SEATS, CASH_BLINDS, MAX_PLAYERS)

    # Create table
    table_manager = TableManagement(TABLE_SEATS)
    
    # Add players to the table
    for i in range(MAX_PLAYERS):
        model = Model(f"Model{i+1}")  # Create a new model for each player
        player = Player(f"Player{i+1}", STARTING_STACK, model)
        table_manager.add_player(player)

    # Game loop
    while len(table_manager.players) >= 2:  # end game if not enough players for a hand
        # Create deck
        deck_manager = DeckManager()
        deck = deck_manager.create_deck(DECK)
        shuffled_deck = deck_manager.shuffle_deck(deck)

        # Initialize the game
        game = PokerGame(table_manager.players, shuffled_deck, CASH_BLINDS)

        # Start a new hand
        game.start_game()

        print(f"Hand completed. Small blind: {CASH_BLINDS[0]}, Big blind: {CASH_BLINDS[1]}, Ante: {CASH_BLINDS[2]}")

    print("Cash game completed!")



elif GAME_TYPE == "heads_up":
    heads_up = HeadsUp(STARTING_STACK)

    # Add players to the heads-up game
    for i in range(2):
        player = Player(f"Player{i+1}", STARTING_STACK)
        heads_up.add_player(player)

    # Game loop
    while True:  # adjust the condition based on your desired stop condition
        heads_up.start_hand()
        print("Hand completed.")



elif GAME_TYPE == "spin_and_go":
    spin_and_go = SpinAndGo(STARTING_STACK)

    # Add players to the spin and go
    for i in range(3):
        player = Player(f"Player{i+1}", STARTING_STACK)
        spin_and_go.add_player(player)

    # Game loop
    while True:  # adjust the condition based on your desired stop condition
        spin_and_go.start_hand()
        print("Hand completed.")