from collections import Counter
from deck_management import DeckManager

class PokerHand:
    HAND_RANKS = {
        'ROYAL_FLUSH': 9,
        'STRAIGHT_FLUSH': 8,
        'FOUR_OF_A_KIND': 7,
        'FULL_HOUSE': 6,
        'FLUSH': 5,
        'STRAIGHT': 4,
        'THREE_OF_A_KIND': 3,
        'TWO_PAIR': 2,
        'ONE_PAIR': 1,
        'HIGH_CARD': 0
    }

    @staticmethod
    def evaluate_hand(hole_cards, community_cards):
        all_cards = hole_cards + community_cards
        all_cards.sort(key=lambda card: (DeckManager.get_rank_index(card[0]), card[1]), reverse=True)

        rank_counts = Counter(card[0] for card in all_cards)
        suit_counts = Counter(card[1] for card in all_cards)

        largest_same_kind = max(rank_counts.values())
        is_flush = max(suit_counts.values()) >= 5

        flush_suit = None
        if is_flush:
            flush_suit = max(suit_counts, key=suit_counts.get)
            flush_cards = [card for card in all_cards if card[1] == flush_suit]
            straight_flush_cards = PokerHand.is_straight(flush_cards)
            if straight_flush_cards:
                if DeckManager.get_rank_index(straight_flush_cards[0][0]) == 12:
                    return (PokerHand.HAND_RANKS['ROYAL_FLUSH'], straight_flush_cards)
                else:
                    return (PokerHand.HAND_RANKS['STRAIGHT_FLUSH'], straight_flush_cards)

        straight_cards = PokerHand.is_straight(all_cards)

        best_hand = None

        if largest_same_kind == 4:
            best_hand = PokerHand.prepare_result('FOUR_OF_A_KIND', all_cards, rank_counts, 4)
        elif largest_same_kind == 3 and len([count for count in rank_counts.values() if count >= 2]) > 1:
            best_hand = PokerHand.prepare_result('FULL_HOUSE', all_cards, rank_counts, 3, pair_needed=True)
        elif is_flush:
            best_hand = (PokerHand.HAND_RANKS['FLUSH'], flush_cards[:5])
        elif straight_cards:
            best_hand = (PokerHand.HAND_RANKS['STRAIGHT'], straight_cards)
        elif largest_same_kind == 3:
            best_hand = PokerHand.prepare_result('THREE_OF_A_KIND', all_cards, rank_counts, 3)
        elif largest_same_kind == 2:
            pair_ranks = [rank for rank, count in rank_counts.items() if count == 2]
            if len(pair_ranks) >= 2:
                best_hand = PokerHand.prepare_result('TWO_PAIR', all_cards, rank_counts, 2)
            else:
                best_hand = PokerHand.prepare_result('ONE_PAIR', all_cards, rank_counts, 2)
        else:
            best_hand = (PokerHand.HAND_RANKS['HIGH_CARD'], all_cards[:5])

        return best_hand

    @staticmethod
    def prepare_result(hand_type, all_cards, rank_counts, rank_count_needed, pair_needed=False):
        important_cards = [card for card in all_cards if rank_counts[card[0]] == rank_count_needed]
        other_cards = [card for card in all_cards if rank_counts[card[0]] < rank_count_needed]

        cards = important_cards + other_cards[:5 - len(important_cards)]

        if pair_needed:
            pair_cards = [card for card in all_cards if rank_counts[card[0]] == 2][:2]
            cards = important_cards + pair_cards

        return (PokerHand.HAND_RANKS[hand_type], cards[:5])

    
    
    @staticmethod
    def is_straight(cards):
        # Create a set of unique cards (no duplicates in rank)
        unique_cards = []
        seen_ranks = set()
        for card in cards:
            rank = DeckManager.get_rank_index(card[0])
            if rank not in seen_ranks:
                unique_cards.append(card)
                seen_ranks.add(rank)

        # Sort unique cards in descending order by rank
        unique_cards.sort(key=lambda card: DeckManager.get_rank_index(card[0]), reverse=True)

        for i in range(len(unique_cards) - 4):
            sorted_ranks = sorted(DeckManager.get_rank_index(card[0]) for card in unique_cards[i:i+5])
            if sorted_ranks[4] - sorted_ranks[0] == 4:
                return sorted(unique_cards[i:i+5], key=lambda card: DeckManager.get_rank_index(card[0]), reverse=True)
            elif sorted_ranks == [0, 1, 2, 3, 12]:  # Special case: 5,4,3,2,A
                # Move Ace to the end
                sorted_cards = sorted(unique_cards[i:i+5], key=lambda card: DeckManager.get_rank_index(card[0]), reverse=True)
                sorted_cards.append(sorted_cards.pop(0))
                return sorted_cards
        return False



    @staticmethod
    def sort_players_by_hand_rank(players):
        # Sort the list in descending order by hand rank and all five cards considering the kicker
        players.sort(key=lambda player: (
            player.current_hand_rank[0],  # hand rank
            [DeckManager.get_rank_index(card[0]) for card in sorted(player.current_hand_rank[1], reverse=True)]  # all five cards
        ), reverse=True)

        # Initialize the list that will store the sorted players
        sorted_players = []

        # Loop over the sorted list of players
        for player in players:
            hand_rank, hand_cards = player.current_hand_rank
            hand_card_ranks = [DeckManager.get_rank_index(card[0]) for card in sorted(hand_cards, reverse=True)]

            # If the sorted_players list is empty, or the last group has a different hand rank or all five cards,
            # add a new group
            if not sorted_players or \
                sorted_players[-1][0].current_hand_rank[0] != hand_rank or \
                [DeckManager.get_rank_index(card[0]) for card in sorted(sorted_players[-1][0].current_hand_rank[1], reverse=True)] != hand_card_ranks:
                sorted_players.append([player])  # Only append the player object
            else:
                # Otherwise, add the player to the last group
                sorted_players[-1].append(player)  # Only append the player object

        return sorted_players








