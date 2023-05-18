import cupy as cp, os

class HandRangeMatrix:
    def __init__(self):
        self.range_matrices = {
            "9-max": {
                "UTG": None,
                "UTG+1": None,
                "MP": None,
                "LJ": None,
                "HJ": None,
                "CO": None,
                "BTN": None,
                "SB": None,
                "BB": None,
            },
            "6-max": {
                "UTG": None,
                "MP": None,
                "CO": None,
                "BTN": None,
                "SB": None,
                "BB": None,
            },
            "3-max": {
                "BTN": None,
                "SB": None,
                "BB": None,
            },
            "heads-up": {
                "SB": None,
                "BB": None,
            },
        }

    def create_range_matrix(self, table_size, seating_position):
        num_ranks = 13

        range_matrix = cp.empty((num_ranks+1, num_ranks+1), dtype=object)

        ranks = ['-', 'A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2']

        for i in range(num_ranks+1):
            for j in range(num_ranks+1):
                if i == 0 or j == 0:
                    range_matrix[i, j] = ranks[max(i, j)]
                elif i == j:
                    hand = ((i-1, ""), (j-1, ""))
                    range_matrix[i, j] = {'hand': hand, 'hand_type': 'pair', 'probability': None}
                elif i > j:
                    hand = ((i-1, ""), (j-1, ""))
                    range_matrix[i, j] = {'hand': hand, 'hand_type': 'suited', 'probability': None}
                else:
                    hand = ((j-1, ""), (i-1, ""))
                    range_matrix[i, j] = {'hand': hand, 'hand_type': 'offsuit', 'probability': None}

        self.range_matrices[table_size][seating_position] = range_matrix


    def load_range_matrix(self, table_size, seating_position, file_path):
        self.range_matrices[table_size][seating_position] = cp.load(file_path)

    def save_range_matrix(self, table_size, seating_position, file_path):
        folder_name = f"{table_size}_ranges"
        os.makedirs(folder_name, exist_ok=True)
        cp.save(os.path.join(folder_name, f"{table_size}_{seating_position}.npy"), self.range_matrices[table_size][seating_position])

    def get_range_probability(self, table_size, seating_position, hand):
        range_matrix = self.range_matrices[table_size].get(seating_position)
        if range_matrix is not None:
            rank1, suit1 = hand[0]
            rank2, suit2 = hand[1]
            suited = suit1 == suit2
            if rank1 >= rank2:
                return range_matrix[rank1, rank2]['probability'] if range_matrix[rank1, rank2]['suited'] == suited else None
            else:
                return range_matrix[rank2, rank1]['probability'] if range_matrix[rank2, rank1]['suited'] == suited else None
        return None
