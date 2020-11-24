# Dennis Zalitach

"""
A module containing the card class (to represent, well, cards), 
which also has some binary operations defined on it.
Also has several functions pertaining directly to cribbage so as to
ease calculations, as well as constants SPADE, HEART, DIAMOND, and CLUB
which point to the unicode characters for the suit symbols.
"""

SPADE = "\N{BLACK SPADE SUIT}"
HEART = "\N{BLACK HEART SUIT}"
DIAMOND = "\N{BLACK DIAMOND SUIT}"
CLUB = "\N{BLACK CLUB SUIT}"

class Card:
    """
    A simple card class, whose attributes and methods are minimum for what cribbage requires.
    Card(value, suit) : value and suit are strings (corresponding to the value and suit, of course)
    """
    values = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    suits = [SPADE, HEART, DIAMOND, CLUB]
    
    def __init__(self, value, suit):
        assert value in Card.values, "Invalid card value"
        assert suit in Card.suits, "Invalid card suit"
        self._value = value
        self._suit = suit

    @property
    def value(self):
        return self._value 

    @property
    def suit(self):
        return self._suit

    def __str__(self):
        return "[{}|{}]".format(self._value, self._suit)

    def __eq__(self, other):
        return self.value == other.value and self.suit == other.suit

    def same_value(self, other):
        """Returns true when card values are the same."""
        if type(other) != Card:
            raise TypeError
        return self.value == other.value

    def same_suit(self, other):
        """Returns true when card suits are the same."""
        if type(other) != Card:
            raise TypeError
        return self.suit == other.suit

    def val_to_int(self):
        if self._value in Card.values[1:10]:
            return int(self._value)
        elif self._value == "A":
            return 1
        else:
            return 10

    def val_to_index(self):
        return Card.values.index(self._value)

    @classmethod
    def make_deck(cls):
        """Returns a list: a standard 52 card deck."""
        deck = []
        for suit in cls.suits:
            for val in cls.values:
                deck.append(Card(val, suit))

        return deck 

def get_combos(hand):
    """Returns a list of all combinations of cards (list of lists)"""
    combos = []
    size = len(hand)
    
    for i in range(size):
        for j in range(i+1, size):
            # add all pairs...
            combos.append([i, j])
            for k in range(j+1, size):
                # and triples..
                combos.append([i, j, k])
                for l in range(k+1, size):
                    # and quadruples...
                    combos.append([i, j, k, l])
    # and finally the whole hand, if including cut card
    if size == 5:
        combos.append([i for i in range(size)])

    return combos

def fifteens(hand, combos):
    """Returns the combinations summing to 15 (list of lists) in hand (list of size 4 or 5) given all combinations"""
    valid = []

    for combo in combos:
        total = 0
        for i in combo:
            total += hand[i].val_to_int()
        if total == 15:
            valid.append(combo)

    return valid

def runs(hand, combos):
    """Returns the largest run in hand (there is only one, since run is minimum 3 cards), along with how many duplicates there are."""
    current_best = [] # will store the largest run given by values in index form (given by Card.values)
    val_indices = [] # stores the sequence of indices for current combo being processed
    multiplicity = 1 # stores the number of "duplicate" runs

    for combo in combos:
        if len(combo) >= 3:
            val_indices = sorted([hand[i].val_to_index() for i in combo])
            consecutive = True
            for i in val_indices[0:len(val_indices) - 1]:
                if i+1 not in val_indices or val_indices.count(i) > 1:
                    consecutive = False
            if consecutive == True:
                if len(val_indices) > len(current_best):
                    multiplicity = 1
                    current_best = val_indices
                elif len(val_indices) == len(current_best):
                    multiplicity += 1

    return current_best, multiplicity

def pairs(hand, combos):
    """Returns all pairs in hand as combinations of hand indices."""
    pairs = []
    for combo in combos:
        if len(combo) == 2:
            if hand[combo[0]].value == hand[combo[1]].value:
                pairs.append(combo)
    
    return pairs

def suit_flush(hand):
    """Returns 1 if all cards in hand are of the same suit, 0 otherwise."""
    suit = hand[0].suit
    for card in hand[1:]:
        if card.suit != suit:
            return 0
    return 1