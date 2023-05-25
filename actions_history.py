import numpy as np

class HandHistory:
    def __init__(self, max_seats):
        self.hand_history = []

        # Initialize the history for each player
        for seat in range(max_seats):
            self.hand_history.append({
                'player_name': None,
                'initial_stack_size': None,
                'hole_cards': None,
                'actions': None,  # This should be a numpy array
                'final_stack_size': None,
                'position': None
            })

    def add_player_to_hand(self, player_name, initial_stack_size, position, seat):
        self.hand_history[seat]['player_name'] = player_name
        self.hand_history[seat]['initial_stack_size'] = initial_stack_size
        self.hand_history[seat]['position'] = position
        self.hand_history[seat]['actions'] = np.empty((0, 4))  # Initialize actions as an empty numpy array

    def add_hole_cards(self, hole_cards, seat):
        self.hand_history[seat]['hole_cards'] = hole_cards

    def add_action(self, street, action, amount, seat):
        # Appending action to the respective player's action array
        self.hand_history[seat]['actions'] = np.append(self.hand_history[seat]['actions'], np.array([[street, action, amount]]), axis=0)

    def finalize_hand(self, final_stack_size, seat):
        self.hand_history[seat]['final_stack_size'] = final_stack_size
