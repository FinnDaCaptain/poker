import itertools
import secrets

class DeckManager:
    RANK_STRINGS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    SUIT_STRINGS = ['Spades', 'Hearts', 'Diamonds', 'Clubs']

    deck = None

    @staticmethod
    def create_deck(deck):
        deck = [(rank, suit) for rank, suit in itertools.product(range(13), range(4))]
        return deck

    @staticmethod
    def shuffle_deck(deck):
        for i in range(len(deck)-1, 0, -1):  # Start from the last card
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
