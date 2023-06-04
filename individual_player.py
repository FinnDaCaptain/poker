class Player:
    def __init__(self, name, stack_size, model):
        self.name = name
        self.stack_size = stack_size
        self.model = model

        self.hole_cards = []
        self.current_hand_rank = None
        
        self.is_waiting = False
        self.is_sitting_out = False
        self.is_eligible_for_pot = True
        
        self.is_folded = False
        self.is_all_in = False
        self.has_acted = False
        self.is_tied = False
        
        self.is_dealer = False
        self.is_small_blind = False
        self.is_big_blind = False

        self.last_bet = 0
        self.round_bet = 0
        self.total_bet = 0
     
    def pay_ante(self, ante_amount):
        if ante_amount >= self.stack_size:
            print(f"{self.name} does not have enough chips. Going all-in.")
            self.is_all_in = True
            all_in_value = self.stack_size
            self.stack_size = 0
            self.total_bet += all_in_value
            return all_in_value # All_in will return the amount to be added to the pot
        else:
            self.stack_size -= ante_amount
            self.total_bet += ante_amount
            return ante_amount

    def fold(self, eligible_players):
        self.hole_cards = []  # discard hand
        self.is_folded = True
        self.is_eligible_for_pot = False
        self.last_bet = 0
        
        # if player's name is in the community pot eligible players list
        if self in eligible_players:
            eligible_players.remove(self)

    def check(self, bet_to_match):
        self.last_bet = bet_to_match - self.round_bet
        self.round_bet += self.last_bet
        self.total_bet += self.last_bet
        return self.last_bet

    def bet(self, bet_amount):
        if bet_amount >= self.stack_size:
            print(f"{self.name} does not have enough chips. Going all-in.")
            return self.all_in()  # All_in will return the amount to be added to the pot
        else:
            self.stack_size -= bet_amount
            self.last_bet = bet_amount
            self.round_bet += self.last_bet
            self.total_bet += self.last_bet
            return self.last_bet  # Return amount to be added to the pot


    def raise_bet(self, raise_amount):
        self.last_bet = raise_amount
        self.stack_size -= self.last_bet
        self.round_bet += self.last_bet
        self.total_bet += self.last_bet
        return raise_amount


    def call(self, bet_to_match):
        if bet_to_match >= self.stack_size:
            print(f"Call put {self.name} all in")
            return self.all_in()
        call_amount = bet_to_match - self.round_bet
        self.stack_size -= call_amount
        self.last_bet = call_amount
        self.round_bet += self.last_bet
        self.total_bet += self.last_bet
        return call_amount  # Return bet to be added to the pot


    def all_in(self):
        self.is_all_in = True
        all_in_value = self.stack_size
        self.stack_size = 0
        
        self.last_bet = all_in_value
        self.round_bet += self.last_bet
        self.total_bet += self.last_bet
        return all_in_value  # Return all_in_value to be added to the pot


    def reset_for_betting_round(self):
        self.last_bet = 0
        self.round_bet = 0
        self.has_acted = False

    def reset_for_new_hand(self):
        self.hole_cards = []
        self.current_hand_rank = None
        self.is_eligible_for_pot = True
        self.has_acted = False
        self.is_folded = False
        self.is_all_in = False
        self.last_bet = 0
        self.round_bet = 0
        self.total_bet = 0


    def make_decision_test(self, big_blind, bet_to_match, last_raise):
        
        bet_amount = bet_to_match
        action = "CALL"
        return Action(action, bet_amount)


    def make_decision(self, big_blind, bet_to_match, last_raise):
        
        while True:
            bet_amount = 0
            try:
                if self.round_bet == bet_to_match:
                    action = input("Please enter an action (CHECK/BET/ALL_IN): ").upper()
                    if action == 'CHECK':
                        bet_amount = bet_to_match
                        break
                    elif action == 'BET':
                        bet_amount = int(input("Enter your bet amount: "))
                        if bet_amount >= big_blind:
                            if bet_amount <= self.stack_size:
                                break
                            else:
                                print("You don't have enough chips to bet this amount.")
                        else:
                            print(f"Invalid bet amount. Minimum bet is {big_blind}. Please try again.")
                    elif action == 'ALL_IN':
                        if self.stack_size >= bet_to_match:
                            break
                        else:
                            print("You don't have enough chips to go all in.")
                    else:
                        print("Invalid action. Please try again.")
                else:            
                    action = input("Please enter an action (FOLD/CALL/RAISE/ALL_IN): ").upper()
                    if action == 'FOLD':
                        break
                    elif action == 'CALL':
                        if self.stack_size >= bet_to_match:
                            bet_amount = bet_to_match
                            break
                        else:
                            print("You don't have enough chips to call.")
                    elif action == 'RAISE':
                        min_raise = max(big_blind, last_raise)
                        bet_amount = int(input(f"Enter your raise amount, {bet_to_match + min_raise} is the minimum: "))
                        if bet_amount >= bet_to_match + min_raise:
                            if bet_amount <= self.stack_size:
                                break
                            else:
                                print("You don't have enough chips to raise this amount.")
                        else:
                            print(f"Invalid raise amount. Minimum raise is {bet_to_match + min_raise}. Please try again.")
                    elif action == 'ALL_IN':
                        break
                    else:
                        print("Invalid action. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a numeric value for bet/raise amount.")
        
        
        return Action(action, bet_amount)
    
    

class Action:
    def __init__(self, type, amount=0):
        self.type = type.upper()
        self.amount = amount
