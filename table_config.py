class TableConfig:
    cash_configs = {
        'low': {
            'min_buy_in': 20,  # how many times the big blind
            'max_buy_in': 100, 
            'time_to_act': None,
            'max_time_bank': None,
            'time_bank_added_per_level': None,
            'max_seats': 9,
            'blinds': (1, 2, 1),
            'players': [None] * 9,
            'player_activity': {'active_players': [], 'waiting_players': []},
            'community_pot': {'pot_value': 0, 'eligible_players': []},
            'side_pots': []  # A list of dictionaries, where each dict is {'pot_value': 0, 'eligible_players': []}
        },
        # Add more predefined tables here
        'heads_up': {
            'min_buy_in': 20,  # how many times the big blind
            'max_buy_in': 100, 
            'max_seats': 2,
            'blinds': (10, 20, 1),
            'players': [None] * 2,
            'player_activity': {'active_players': [], 'waiting_players': [],},
            'community_pot': {'pot_value': 0, 'eligible_players': []},
            'side_pots': []  # A list of dictionaries, where each dict is {'pot_value': 0, 'eligible_players': []}
        },
    }

    tourney_configs = {
        'small': {
            'min_buy_in': 20,  # how many times the big blind
            'max_buy_in': 100, 
            'max_seats': 9,
            'blinds': (10, 20, 1),
            'players': [None] * 9,
            'player_activity': {'active_players': [], 'folded_players': []},
            'community_pot': {'pot_value': 0, 'eligible_players': []},
            'side_pots': []  # A list of dictionaries, where each dict is {'pot_value': 0, 'eligible_players': []}
        },
        # Add more predefined tables here
    }