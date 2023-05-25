import copy


        self.preflop_stats = PreflopStats()
        self.flop_stats = FlopStats()
        self.turn_stats = TurnStats()
        self.river_stats = RiverStats()
        self.showdown_stats = ShowdownStats()
        self.hand_rank = PokerHand()


        self.vpip = 0.0
        self.pfr = 0.0
        self.three_bet = 0.0
        self.fold_to_three_bet = 0.0
        self.fold_to_c_bet = 0.0
        self.fold_to_steal = 0.0
        self.steal_attempt = 0.0
        self.call_open = 0.0
        self.wtsd = 0.0
        self.wsd = 0.0
        self.afq = 0.0
        self.afq_flop = 0.0
        self.afq_turn = 0.0
        self.afq_river = 0.0
        self.check_raise = 0.0
        self.donk_bet = 0.0
        self.squeeze = 0.0
        self.cbet = 0.0
        self.fold_to_cbet = 0.0
        self.check_raise_flop = 0.0
        self.check_raise_turn = 0.0
        self.check_raise_river = 0.0
        self.wtsd_call_pf_raise = 0.0
        self.double_barrel = 0.0
        self.triple_barrel = 0.0
        self.fold_flop_bet = 0.0
        self.fold_turn_bet = 0.0
        self.fold_river_bet = 0.0
        self.four_bet = 0.0
        self.call_three_bet = 0.0
        self.cold_call = 0.0
        self.check_fold_flop = 0.0
        self.check_fold_turn = 0.0
        self.check_fold_river = 0.0
        self.fold_big_blind_to_steal = 0.0
        self.fold_small_blind_to_steal = 0.0
        self.fold_probe_bet = 0.0
        self.fold_turn_river_probe_bet = 0.0
        self.donk_bet_flop = 0.0
        self.donk_bet_turn = 0.0
        self.donk_bet_river = 0.0
        self.call_two_bet = 0.0
        self.fold_to_four_bet = 0.0
        self.five_bet = 0.0
        self.check_raise_flop_c_bet = 0.0
        self.check_raise_turn_c_bet = 0.0
        self.fold_to_flop_c_bet_in_3bet_pot = 0.0
        self.fold_to_turn_c_bet_in_3bet_pot = 0.0
        self.fold_to_river_c_bet_in_3bet_pot = 0.0
        self.fold_to_4bet_in_3bet_pot = 0.0
        self.fold_to_flop_donk_bet = 0.0
        self.fold_to_turn_donk_bet = 0.0
        self.fold_to_river_donk_bet = 0.0
        self.fold_to_probe_bet_flop_turn_river_in_3bet_pot = 0.0
        self.fold_to_flop_probe_bet_in_4bet_pot = 0.0




class StatTracker:
    def __init__(self):
        self.players_stats = {}  # Overall statistics
        self.session_stats = {}  # Session-specific statistics
        self.current_hand_stats = {}  # Hand-specific statistics
        self.players = []
        self.previous_action = None


    def start_hand(self, players):
        self.players = players
        self.current_hand_stats = {player_name: PlayerStats() for player_name in self.players}

        # Initialize session stats for new players
        for player_name in self.players:
            if player_name not in self.session_stats:
                self.session_stats[player_name] = PlayerStats()

        self.previous_action = None


    def update_stats(self, action):
        player_name = action.player
        player_stats = self.current_hand_stats[player_name]

        if action.street == 'preflop':
            player_stats.preflop.update(action, self.previous_action)
        elif action.street == 'flop':
            player_stats.flop.update(action, self.previous_action)
        elif action.street == 'turn':
            player_stats.turn.update(action, self.previous_action)
        elif action.street == 'river':
            player_stats.river.update(action, self.previous_action)
        elif action.street == 'showdown':
            player_stats.showdown.update(action, self.previous_action)

        self.previous_action = action

    def end_hand(self):
        for player_name, player_stats in self.current_hand_stats.items():
            player_stats.end_hand()
            self.update_player_stats(player_name, player_stats, self.players_stats)  # Update overall stats
            self.update_player_stats(player_name, player_stats, self.session_stats)  # Update session stats


    def update_player_stats(self, player_name, current_stats, target_stats):
        if player_name not in target_stats:
            target_stats[player_name] = copy.deepcopy(current_stats)
        else:
            for key, value in current_stats.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        target_stats[player_name][key][sub_key] += sub_value
                else:
                    target_stats[player_name][key] += value


    def get_player_stats(self, player_name):
        return self.players_stats[player_name] if player_name in self.players_stats else None

    def get_session_stats(self, player_name):
        return self.session_stats[player_name] if player_name in self.session_stats else None

    def save_player_stats(self):
        pass

    def start_new_session(self):
        self.session_stats = {}






class PlayerStats:
    def __init__(self):
        self.preflop = PreflopStats()
        self.flop = FlopStats()
        self.turn = TurnStats()
        self.river = RiverStats()
        self.showdown = ShowdownStats()

    def add(self, other):
        self.preflop.add(other.preflop)
        self.flop.add(other.flop)
        self.turn.add(other.turn)
        self.river.add(other.river)
        self.showdown.add(other.showdown)

    def end_hand(self):
        self.preflop.end_hand()
        self.flop.end_hand()
        self.turn.end_hand()
        self.river.end_hand()
        self.showdown.end_hand()



class PreflopStats:
    def __init__(self):
        self.stats = {
            'VPIP': 0,
            'PFR': 0,
            'steal_attempt': 0,
            'call_open': 0,
            'four_bet': 0,
            'call_three_bet': 0,
            'cold_call': 0,
            'fold_to_four_bet': 0,
            'five_bet': 0,
            'fold_to_4bet_in_3bet_pot': 0,
            'opportunities': {
                'VPIP': 0,
                'PFR': 0,
                'steal_attempt': 0,
                'call_open': 0,
                'four_bet': 0,
                'call_three_bet': 0,
                'cold_call': 0,
                'fold_to_four_bet': 0,
                'five_bet': 0,
                'fold_to_4bet_in_3bet_pot': 0,
            }
        }
        self.previous_action = None
        self.num_raises = 0
        self.steal_attempts = 0

    def update(self, action):
        self.stats['preflop']['opportunities']['VPIP'] += 1
        self.stats['preflop']['opportunities']['PFR'] += 1
        self.stats['preflop']['opportunities']['steal_attempt'] += 1 if action.type == 'raise' and self.is_steal_position(action.position) else 0
        self.stats['preflop']['steal_attempt'] += 1 if action.type == 'raise' and self.is_steal_position(action.position) else 0
        self.stats['preflop']['opportunities']['call_open'] += 1 if action.type == 'call' else 0
        self.stats['preflop']['call_open'] += 1 if action.type == 'call' else 0
        self.stats['preflop']['opportunities']['four_bet'] += 1 if self.is_four_bet_opportunity() else 0
        self.stats['preflop']['four_bet'] += 1 if action.type == 'raise' and self.is_four_bet_opportunity() else 0
        self.stats['preflop']['opportunities']['call_three_bet'] += 1 if self.is_three_bet_opportunity() else 0
        self.stats['preflop']['call_three_bet'] += 1 if action.type == 'call' and self.is_three_bet_opportunity() else 0
        self.stats['preflop']['opportunities']['cold_call'] += 1 if action.type == 'call' and self.is_cold_call_opportunity() else 0
        self.stats['preflop']['cold_call'] += 1 if action.type == 'call' and self.is_cold_call_opportunity() else 0
        self.stats['preflop']['opportunities']['fold_to_four_bet'] += 1 if self.is_four_bet_opportunity() else 0
        self.stats['preflop']['fold_to_four_bet'] += 1 if action.type == 'fold' and self.is_four_bet_opportunity() else 0
        self.stats['preflop']['opportunities']['five_bet'] += 1 if self.is_five_bet_opportunity() else 0
        self.stats['preflop']['five_bet'] += 1 if action.type == 'raise' and self.is_five_bet_opportunity() else 0
        self.stats['preflop']['opportunities']['fold_to_4bet_in_3bet_pot'] += 1 if self.is_four_bet_opportunity() and self.is_three_bet_pot() else 0
        self.stats['preflop']['fold_to_4bet_in_3bet_pot'] += 1 if action.type == 'fold' and self.is_four_bet_opportunity() and self.is_three_bet_pot() else 0
            

        if action.type == 'CALL':
            self.stats['VPIP'] += 1
            self.stats['call_open'] += 1
            self.stats['cold_call'] += 1 if self.is_cold_call_opportunity() else 0
            self.stats['call_three_bet'] += 1 if self.is_three_bet_opportunity() else 0
        elif action.type == 'RAISE':
            self.stats['VPIP'] += 1
            self.stats['PFR'] += 1
            self.num_raises += 1  # increment the raise counter
            self.stats['steal_attempt'] += 1 if self.is_steal_position(action.position) else 0
            self.stats['four_bet'] += 1 if self.is_four_bet_opportunity() else 0
            self.stats['five_bet'] += 1 if self.is_five_bet_opportunity() else 0
        elif action.type == 'FOLD':
            self.stats['fold_to_four_bet'] += 1 if self.is_four_bet_opportunity() else 0
            self.stats['fold_to_4bet_in_3bet_pot'] += 1 if self.is_four_bet_opportunity() and self.is_three_bet_pot() else 0

        self.previous_action = action


    def is_steal_position(self, position):
        # In general, late positions like the Cut-off (CO) and the Button (BU) are considered steal positions in No Limit Hold'em
        return position in ['CO', 'BU', 'SB']

    def is_cold_call_opportunity(self):
        # A cold call opportunity arises when there was a raise and there's a chance to call without having put any money in the pot yet
        # Assuming that the 'previous_action' attribute is an object with a 'type' attribute that can be 'RAISE'
        return self.previous_action.type == 'RAISE'

    def is_three_bet_pot(self):
        # A three-bet pot is one where there has been a raise and a re-raise (three bet sizes: the blinds, the raise, the re-raise)
        # Assuming that 'num_raises' tracks the number of raises in the hand
        return self.num_raises == 2

    def is_three_bet_opportunity(self):
        # A three-bet opportunity arises when there was a raise and there's a chance to re-raise
        # Assuming that the 'previous_action' attribute is an object with a 'type' attribute that can be 'RAISE'
        return self.previous_action.type == 'RAISE'

    def is_four_bet_opportunity(self):
        # A four-bet opportunity arises when there was a raise, a re-raise, and there's a chance to re-raise again
        return self.num_raises == 2

    def is_five_bet_opportunity(self):
        # A five-bet opportunity arises when there was a raise, a re-raise, another re-raise, and there's a chance to re-raise again
        return self.num_raises == 3

    def end_hand(self):
        # calculate the final preflop stats after the hand
        # for instance, percentage stats could be calculated here based on counts and opportunities
        self.previous_action = None
        self.num_raises = 0
        self.steal_attempts = 0


class FlopStats:
    def __init__(self):
        self.stats = {
            'opportunities': {
                'fold_to_c_bet': 0,
                'check_raise': 0,
                'donk_bet': 0,
                'cbet': 0,
                'fold_to_cbet': 0,
                'check_raise_flop': 0,
                'fold_flop_bet': 0,
                'check_fold_flop': 0,
                'donk_bet_flop': 0,
            },
            'fold_to_c_bet': 0,
            'check_raise': 0,
            'donk_bet': 0,
            'cbet': 0,
            'fold_to_cbet': 0,
            'check_raise_flop': 0,
            'fold_flop_bet': 0,
            'check_fold_flop': 0,
            'donk_bet_flop': 0,
        }
        self.previous_action = None

    def update(self, action):
        if action.type == 'FOLD':
            self.stats['fold_to_c_bet'] += 1 if self.is_c_bet_opportunity() else 0
            self.stats['fold_flop_bet'] += 1 if self.previous_action and self.previous_action.type == 'BET' else 0
            self.stats['check_fold_flop'] += 1 if self.previous_action and self.previous_action.type == 'CHECK' else 0

        elif action.type == 'CHECK':
            self.stats['opportunities']['check_raise'] += 1
            self.stats['opportunities']['check_raise_flop'] += 1
            self.stats['opportunities']['check_fold_flop'] += 1

        elif action.type == 'RAISE':
            self.stats['check_raise'] += 1 if self.previous_action and self.previous_action.type == 'CHECK' else 0
            self.stats['check_raise_flop'] += 1 if self.previous_action and self.previous_action.type == 'CHECK' else 0

        elif action.type == 'BET':
            self.stats['donk_bet'] += 1 if self.is_donk_bet_opportunity() else 0
            self.stats['donk_bet_flop'] += 1 if self.is_donk_bet_opportunity() else 0
            self.stats['cbet'] += 1 if self.is_c_bet_opportunity() else 0
            self.stats['opportunities']['fold_flop_bet'] += 1
            self.stats['opportunities']['donk_bet_flop'] += 1 if self.is_donk_bet_opportunity() else 0
            self.stats['opportunities']['cbet'] += 1 if self.is_c_bet_opportunity() else 0

        if self.is_c_bet_opportunity():
            self.stats['opportunities']['fold_to_c_bet'] += 1
            self.stats['opportunities']['fold_to_cbet'] += 1

        self.previous_action = action

    def is_c_bet_opportunity(self):
        # You're the last preflop aggressor if you made the last raise or call before the flop
        # This logic might need to be updated to reflect the exact rules of your game
        return self.previous_action and self.previous_action.type in ['RAISE', 'CALL'] and self.previous_action.street == 'preflop'

    def is_donk_bet_opportunity(self):
        # You make a donk bet if you're out of position and betting into the last preflop aggressor
        # This logic might need to be updated to reflect the exact rules of your game
        return self.previous_action and self.previous_action.type == 'BET' and self.previous_action.street == 'flop'

    def end_hand(self):
        self.previous_action = None



class TurnStats:
    def __init__(self):
        self.stats = {
            'opportunities': {
                'fold_to_c_bet': 0,
                'check_raise': 0,
                'donk_bet': 0,
                'double_barrel': 0,
                'fold_to_double_barrel': 0,
                'check_fold_turn': 0,
                'donk_bet_turn': 0,
            },
            'fold_to_c_bet': 0,
            'check_raise': 0,
            'donk_bet': 0,
            'double_barrel': 0,
            'fold_to_double_barrel': 0,
            'check_fold_turn': 0,
            'donk_bet_turn': 0,
        }
        self.previous_action = None

    def update(self, action):
        if action.type == 'FOLD':
            self.stats['fold_to_c_bet'] += 1 if self.is_c_bet_opportunity() else 0
            self.stats['fold_to_double_barrel'] += 1 if self.is_double_barrel_opportunity() else 0
            self.stats['check_fold_turn'] += 1 if self.previous_action and self.previous_action.type == 'CHECK' else 0

        elif action.type == 'CHECK':
            self.stats['opportunities']['check_raise'] += 1
            self.stats['opportunities']['check_fold_turn'] += 1

        elif action.type == 'RAISE':
            self.stats['check_raise'] += 1 if self.previous_action and self.previous_action.type == 'CHECK' else 0

        elif action.type == 'BET':
            self.stats['donk_bet'] += 1 if self.is_donk_bet_opportunity() else 0
            self.stats['donk_bet_turn'] += 1 if self.is_donk_bet_opportunity() else 0
            self.stats['double_barrel'] += 1 if self.is_double_barrel_opportunity() else 0
            self.stats['opportunities']['donk_bet_turn'] += 1 if self.is_donk_bet_opportunity() else 0

        if self.is_c_bet_opportunity():
            self.stats['opportunities']['fold_to_c_bet'] += 1

        if self.is_double_barrel_opportunity():
            self.stats['opportunities']['fold_to_double_barrel'] += 1

        self.previous_action = action

    def is_c_bet_opportunity(self):
        return self.previous_action and self.previous_action.type in ['RAISE', 'CALL'] and self.previous_action.street == 'flop'

    def is_donk_bet_opportunity(self):
        return self.previous_action and self.previous_action.type == 'BET' and self.previous_action.street == 'turn'

    def is_double_barrel_opportunity(self):
        # Assuming this method should return True if the player bet on the flop and now has a chance to bet on the turn
        return self.previous_action and self.previous_action.type == 'BET' and self.previous_action.street == 'flop'

    def end_hand(self):
        for key, value in self.stats.items():
            if key == 'opportunities':
                continue
            opportunities = self.stats['opportunities'].get(key, 0)
            if opportunities != 0:
                self.stats[key] = value / opportunities
        
        self.previous_action = None




class RiverStats:
    def __init__(self):
        self.stats = {
            'opportunities': {
                'fold_to_c_bet': 0,
                'check_raise': 0,
                'donk_bet': 0,
                'cbet': 0,
                'fold_to_cbet': 0,
                'check_raise_river': 0,
                'fold_river_bet': 0,
                'check_fold_river': 0,
                'donk_bet_river': 0,
            },
            'fold_to_c_bet': 0,
            'check_raise': 0,
            'donk_bet': 0,
            'cbet': 0,
            'fold_to_cbet': 0,
            'check_raise_river': 0,
            'fold_river_bet': 0,
            'check_fold_river': 0,
            'donk_bet_river': 0,
        }
        self.previous_action = None

    def update(self, action):
        if action.type == 'FOLD':
            self.stats['fold_to_c_bet'] += 1 if self.is_c_bet_opportunity() else 0
            self.stats['fold_river_bet'] += 1 if self.previous_action and self.previous_action.type == 'BET' else 0
            self.stats['check_fold_river'] += 1 if self.previous_action and self.previous_action.type == 'CHECK' else 0

        elif action.type == 'CHECK':
            self.stats['opportunities']['check_raise'] += 1
            self.stats['opportunities']['check_raise_river'] += 1
            self.stats['opportunities']['check_fold_river'] += 1

        elif action.type == 'RAISE':
            self.stats['check_raise'] += 1 if self.previous_action and self.previous_action.type == 'CHECK' else 0
            self.stats['check_raise_river'] += 1 if self.previous_action and self.previous_action.type == 'CHECK' else 0

        elif action.type == 'BET':
            self.stats['donk_bet'] += 1 if self.is_donk_bet_opportunity() else 0
            self.stats['donk_bet_river'] += 1 if self.is_donk_bet_opportunity() else 0
            self.stats['cbet'] += 1 if self.is_c_bet_opportunity() else 0
            self.stats['opportunities']['fold_river_bet'] += 1
            self.stats['opportunities']['donk_bet_river'] += 1 if self.is_donk_bet_opportunity() else 0
            self.stats['opportunities']['cbet'] += 1 if self.is_c_bet_opportunity() else 0

        if self.is_c_bet_opportunity():
            self.stats['opportunities']['fold_to_c_bet'] += 1
            self.stats['opportunities']['fold_to_cbet'] += 1

        self.previous_action = action

    def is_c_bet_opportunity(self):
        return self.previous_action and self.previous_action.type in ['RAISE', 'CALL'] and self.previous_action.street == 'turn'

    def is_donk_bet_opportunity(self):
        return self.previous_action and self.previous_action.type == 'BET' and self.previous_action.street == 'river'

    def end_hand(self):
        for key, value in self.stats['opportunities'].items():
            if value > 0:
                self.stats[key] /= value
                self.stats[key] *= 100
        
        self.previous_action = None



class ShowdownStats:
    def __init__(self):
        self.stats = {
            'opportunities': {
                'wtsd': 0,  # Went to Showdown
                'wsd': 0,  # Won at Showdown
                'afq': 0,  # Aggression Frequency
                'call_open': 0,  # Call Open
            },
            'wtsd': 0,
            'wsd': 0,
            'afq': 0,
            'call_open': 0,
        }
        self.previous_action = None
        self.player_won_hand = False

    def update(self, action):
        if action.type == 'SHOWDOWN':
            self.stats['opportunities']['wtsd'] += 1
            self.stats['wtsd'] += 1
            if self.player_won_hand:
                self.stats['opportunities']['wsd'] += 1
                self.stats['wsd'] += 1

        if action.type == 'CALL':
            self.stats['call_open'] += 1

        if action.type in ['BET', 'RAISE']:
            self.stats['afq'] += 1

        self.stats['opportunities']['afq'] += 1
        self.stats['opportunities']['call_open'] += 1
        self.previous_action = action

    def end_hand(self, player_won_hand):
        self.player_won_hand = player_won_hand

        # Calculate the percentages at the end of each hand
        for key, value in self.stats['opportunities'].items():
            if value > 0:
                self.stats[key] /= value
                self.stats[key] *= 100
        
        self.previous_action = None

