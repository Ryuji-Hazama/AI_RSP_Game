import random

###############################
# Main Method

_HANDS = ("R", "S", "P")

# Get hands

hand = input("(R)ock, (S)cissors, (P)aper. 1, 2, 3!! > ").upper()
comHand = random.choice(_HANDS)

print(f"Computer: {comHand}")

# Evaluate the input

if hand in _HANDS:

    winHand = _HANDS[(_HANDS.index(hand) + 1) % 3]

else:

    print("What is that lol?")
    exit()

# Judge the result

if comHand == winHand:

    print("You win!")

elif comHand == hand:

    print("Oh, it's a draw.")

else:

    print("Aw... You lose.")
