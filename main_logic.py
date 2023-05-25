from game_management import Tournament, CashGame, SpinAndGo, HeadsUp
from pot_management import BlindStructure
from table_config import TableConfig
from table_management import TableManagement



# Global Settings
GAME_TYPE = "cash"  # change this to control the game type
STARTING_STACK = 10000
NUM_PLAYERS = 9
LEVEL_DURATION = 12 # set to hands for training, minutes for actual use
TOURNAMENT_BLINDS = None
TABLE_NAME = 'low'
BUY_IN = 'min_buy_in'


if GAME_TYPE == "tournament":
    # Create a tournament with the set number of seats, starting stack, and max players
    tournament = Tournament(NUM_PLAYERS, STARTING_STACK, TOURNAMENT_BLINDS, LEVEL_DURATION)

elif GAME_TYPE == "cash":
    # Create CashGame instance
    cash_game = CashGame(TABLE_NAME, NUM_PLAYERS, BUY_IN)
    cash_game.run_game()

elif GAME_TYPE == "heads_up":
    heads_up = HeadsUp(STARTING_STACK)

elif GAME_TYPE == "spin_and_go":
    spin_and_go = SpinAndGo(STARTING_STACK)