class Player:
    def __init__(self, name, stack_size, model):
        self.name = name
        self.stack_size = stack_size
        self.model = model
        self.hole_cards = []
        
        self.is_folded = False
        self.is_all_in = False
        self.current_bet = 0
     
         # PT4 Stats
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


    def fold(self):
        self.hole_cards = []  # discard hand
        self.is_folded = True

    def check(self):
        if self.current_bet != 0:
            raise ValueError(f"{self.name} cannot check because the current bet is {self.current_bet}")
        # else: do nothing

    def call(self, bet):
        if bet > self.stack_size:
            print(f"{self.name} does not have enough chips to call. Going all-in.")
            return self.all_in()
        else:
            self.stack_size -= bet
            self.current_bet = bet

    def bet(self, amount):
        if amount > self.stack_size:
            raise ValueError(f"{self.name} does not have enough chips to bet. Available chips: {self.stack_size}")
        else:
            self.stack_size -= amount
            self.current_bet = amount

    def raise_bet(self, current_bet, raise_amount):
        total_bet = current_bet + raise_amount
        if total_bet > self.stack_size:
            print(f"{self.name} does not have enough chips to raise. Going all-in.")
            return self.all_in()
        else:
            self.stack_size -= total_bet
            self.current_bet = total_bet

    def all_in(self):
        all_in_value = self.stack_size
        self.stack_size = 0
        self.current_bet = all_in_value
        self.is_all_in = True
        return all_in_value

    def reset_for_new_hand(self):
        self.hole_cards = []
        self.is_folded = False
        self.is_all_in = False
        self.current_bet = 0
       