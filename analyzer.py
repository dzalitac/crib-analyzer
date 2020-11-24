# Dennis Zalitach

"""
The main program, which has two routines for determining optimal play.
For the discard analyzer, it takes a 6 card hand and whether or not the crib is yours,
and gives the best discard option. The pegging analyzer takes a 4 card hand and a played card
(none if the user is playing first i.e. is not the dealer) and gives a likely range for opponent,
continuing to do so until either all 8 cards have been played or the user exits. It should
be noted that the discard analyzer is more conservative, and thus checks for obvious plays
before considering average scores across all cuts. In this sense, it's more suited for one-shot
games rather than a tournament type of setting (multiple-eliminations, best of __ games, etc.).
"""

import crib
Card = crib.Card

def str_to_card(string):
    """Returns a card from a string of the form 'value/suit'"""
    card = string.split("/")
    value = card[0]
    suit = card[1]
    if suit not in ["S", "C", "H", "D"] or value not in Card.values:
        raise ValueError 
    if suit == "S":
        suit = crib.SPADE
    elif suit == "C":
      suit = crib.CLUB
    elif suit == "H":
        suit = crib.HEART
    elif suit == "D":
        suit = crib.DIAMOND
    
    return Card(value, suit)

def score(hand):
    """Returns the score of a hand."""
    total = 0
    combos = crib.get_combos(hand)
    fifteens = crib.fifteens(hand, combos)
    run, multiplicity = crib.runs(hand, combos)
    pairs = crib.pairs(hand, combos)
    flush = crib.suit_flush(hand[0:5])

    total += len(fifteens) * 2
    total += len(pairs) * 2
    total += 4 * flush
    if len(hand) == 5:
        total += crib.suit_flush(hand) # i.e. in-hand flush worth 4, hand + cut flush worth 5
    total += len(run) * multiplicity

    return total

def crib_prune(bests, yours):
    """Helper function for discard() which prunes the bests list based on the potential of discarded cards."""
    # first check if the discarded cards of any of the bests give points and adjust their scores accordingly
    # the values ascribed to each type of combination is based on the probability that it scores higher:
    #       4 for fifteens (more likely to get another copy of one of the two values)
    #       3 for pairs (less likely to get more copies, but still guarantees two points)
    #       2 for consecutive cards (getting one higher or one lower is ~8/52 chance)
    #       1 for suited cards (getting the full flush in crib is ~(11/52)^3 chance)
    #       add .5 if one card is a jack (since nobs only worth one point, won't be considered a full rank higher)
    # multiply by -1 if crib is opponent's
    multiplier = 1
    if not yours:
        multiplier = -1
    for best in bests:
        if best[1][0].val_to_int() + best[1][1].val_to_int() == 15:
            best[2] += multiplier * 4
        elif best[1][0].value == best[1][1].value:
            best[2] += multiplier * 3
        elif best[1][0].val_to_index() + 1 == best[1][1].val_to_index():
            best[2] += multiplier * 2 
        elif best[1][0].val_to_index() - 1 == best[1][1].val_to_index():
            best[2] += multiplier * 2 
        elif best[1][0].suit == best[1][1].suit:
            best[2] += multiplier
            
        if best[1][0].value == "J" or best[1][1].value == "J":
            best[2] += multiplier * .5
    bests = sorted(bests, key=lambda x: x[2]) # sort by score
    while bests[-1][2] < bests[0][2]:
        bests.pop() # then prune to highest

    return bests

def cut_prune(bests):
    """Helper function for discard() which prunes bests list based on all possible cuts."""
    deck = Card.make_deck()
    # cards in hand (hand + discards for any bests[i]) can't be cuts
    used = bests[0][0]
    used.extend(bests[0][1])
    for card1 in deck:
        for card2 in used:
            if card1 == card2:
                deck.remove(card1)

    for best in bests:
        average = 0
        for card in deck:
            hand = best[0]
            hand.append(card)
            average += score(hand)
            hand.pop()
        average /= 46.0
        best[2] = average

    bests = sorted(bests, key=lambda x: x[2])
    while bests[-1][2] < bests[0][2]:
        bests.pop()

    return bests

def discard(deal, yours):
    """Gives the best discards given a 6 card deal. yours = True means the crib is counted for the hand; False, against the hand."""
    bests = [[[], [], 0]] # list of lists: each element is (hand, discards, score)

    for i in range(6):
        for j in range(i+1, 6):
            hand = [card for card in deal if deal.index(card) != i and deal.index(card) != j]
            points = score(hand)
            if points > bests[0][2]:
                # clear bests if score is higher and add new hand
                bests = [[hand, [deal[i], deal[j]], points]]
            elif points == bests[0][2]:
                bests.append([hand, [deal[i], deal[j]], points])

    # now prune bests list as best as possible (note that the score field of each 'best' is now skewed from pruning functions)
    if len(bests) > 1:
        bests = crib_prune(bests, yours) # first stage of pruning based on possible crib score
    if len(bests) > 1:
        bests = cut_prune(bests) # second stage of pruning based on all possible 5-card hands
    
    print("Recommended hand: ", end=" ")
    for card in bests[0][0]:
        print(card, end=" ")
    print()

def main():
    
    welcome = """
Welcome to the cribbage analyzer! 
Please note that when you are asked to input a card, it should be entered in the form 'value/suit', 
where \"value\" is 'A', 'J', 'Q', 'K', or a number from 2 to 10, and \"suit\" is 'S', 'C', 'H', or 'D' (for spades, clubs, etc.)
"""
    print(welcome)
    done = False
    while not done:
        valid = False
        while not valid:
            mode = input("(A)nalyze a hand , or (q)uit: ").upper()
            if mode in ["A","Q"]:
                valid = True
            else:
                print("Please enter 'a' or 'q' ")
        if mode == "Q":
            print("Goodbye!")
            done = True
        elif mode == "A":
            hand = input("Enter a six-card hand as a space-separated list: ").split(" ")
            try:
                hand = [str_to_card(x) for x in hand]
            except:
                print("Invalid form for card input (remember: cards are formatted as 'value/suit'")
            else:
                yours = input("Is it your crib? (y/n): ")
                if yours[0].upper() == "Y":
                    discard(hand, True)
                elif yours[0].upper() == "N":
                    discard(hand, False)

main()