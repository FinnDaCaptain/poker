from poker_hand import PokerHand

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
        
        self.is_dealer = False
        self.is_small_blind = False
        self.is_big_blind = False

        self.last_bet = 0
        self.round_bet = 0
        self.total_bet = 0
     
    def pay_ante(self, ante_amount):
        if ante_amount > self.stack_size:
            print(f"{self.name} does not have enough chips to pay the ante. Going all-in.")
            return self.all_in()  # All_in will return the amount to be added to the pot
        else:
            self.stack_size -= ante_amount
            self.total_bet += ante_amount
            return ante_amount


    def fold(self, eligible_players):
        self.hole_cards = []  # discard hand
        self.is_folded = True
        self.is_eligible_for_pot = False
        
        # if player's name is in the community pot eligible players list
        if self in eligible_players:
            eligible_players.remove(self)


    def check(self, bet_to_match):
        if self.total_bet != bet_to_match:
            raise ValueError(f"{self.name} cannot check because the current bet is {bet_to_match}")
        else:
            self.last_bet = bet_to_match
            self.round_bet += self.last_bet
            self.total_bet += self.last_bet
            return self.last_bet


    def bet(self, amount):
        if amount > self.stack_size:
            raise ValueError(f"{self.name} does not have enough chips to bet. Available chips: {self.stack_size}")
        else:
            self.stack_size -= amount
            self.last_bet = amount
            self.round_bet += self.last_bet
            self.total_bet += self.last_bet
            return amount  # Return amount to be added to the pot


    def raise_bet(self, raise_amount):
        if raise_amount >= self.stack_size + self.total_bet:
            print(f"{self.name} does not have enough chips to raise. Going all-in.")
            return self.all_in()  # All_in will return the amount to be added to the pot
        else:
            self.stack_size -= raise_amount
            self.last_bet = raise_amount - self.total_bet
            self.round_bet += self.last_bet
            self.total_bet += self.last_bet
            return raise_amount


    def call(self, bet_to_match):
        if bet_to_match > self.stack_size + self.last_bet:
            print(f"{self.name} does not have enough chips to call. Going all-in.")
            return self.all_in()  # All_in will return the amount to be added to the pot
        elif self.stack_size + self.total_bet == bet_to_match:
            return self.all_in()
        else:
            call_amount = bet_to_match - self.round_bet
            self.stack_size -= call_amount
            self.last_bet = call_amount
            self.round_bet = self.last_bet
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


    def make_decision(self, bet_to_match, street, community_cards, community_pot, side_pots, active_players, eligibile_players):
        self.current_hand_rank = PokerHand.evaluate_hand(self.hole_cards, community_cards)
        
        print(active_players)
        print(eligibile_players)

        print("\nIt's your turn, {}.".format(self.name))
        print("Your hole cards are: ", [str(card) for card in self.hole_cards])
        print("Your current Hand Rank is: ", self.current_hand_rank )
        print("Your current stack is: ", self.stack_size)
        print("Current bet to match is: ", bet_to_match)
        print("Your current bet is: ", self.round_bet)
        print("Current street is: ", street)
        print("Community cards are: ", [str(card) for card in community_cards])
        print("Community pot size is: ", community_pot['pot_value'])
        print("Side pots are: ", side_pots)

        
       
        action = input("Please enter an action (FOLD/CHECK/CALL/BET/RAISE/ALL_IN): ").upper()

        #action = "CALL"

        return Action(action, self.last_bet)
    
    

class Action:
    def __init__(self, type, amount=0):
        self.type = type.upper()
        self.amount = amount
