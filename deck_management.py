import itertools
import secrets

class DeckManager:
    def __init__(self, active_players, shuffled_deck):
        self.active_players = active_players
        self.shuffled_deck = shuffled_deck

    
    RANK_STRINGS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    SUIT_STRINGS = ['Spades', 'Clubs', 'Hearts', 'Diamonds']
    
    @staticmethod
    def get_rank_index(rank_string):
        return DeckManager.RANK_STRINGS.index(rank_string)

    @staticmethod
    def create_deck():
        deck = [(rank, suit) for rank, suit in itertools.product(range(13), range(4))]
        return deck

    @staticmethod
    def shuffle_deck(deck):
        for i in range(len(deck) - 1, -1, -1):  # Start from the last card
            j = secrets.randbelow(i + 1)  # Generate a secure random index
            deck[i], deck[j] = deck[j], deck[i]  # Swap the current card with the card at the random index
        return deck


    @staticmethod
    def draw_card(deck):
        card = deck.pop(0)
        return card, deck

    @staticmethod
    def deal_cards(deck, n):
        cards = deck[:n]
        deck = deck[n:]
        return cards, deck

    def get_card_string(self, card):
        rank, suit = card
        return self.RANK_STRINGS[rank], self.SUIT_STRINGS[suit]


    def deal_hole_cards(self):
        # Use the DeckManager to draw cards and convert them to strings
        cards, self.shuffled_deck = self.deal_cards(self.shuffled_deck, 1)
        hole_cards = [self.get_card_string(card) for card in cards]

        return hole_cards
    

    def deal_community_cards(self, num_cards):
        cards, self.shuffled_deck = self.deal_cards(self.shuffled_deck, num_cards)
        self.community_cards.extend([self.deck_manager.get_card_string(card) for card in cards])