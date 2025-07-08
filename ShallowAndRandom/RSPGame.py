import random

###############################
# Judge the result

def judgement(win, draw, judgeHand) -> None:

    if judgeHand == win:

        print("You win!")

    elif judgeHand == draw:

        print("Oh, it's a draw.")

    else:

        print("Aw... You lose.")

#
###############################
# Main Method

_HANDS = ("R", "S", "P")
hand = input("(R)ock, (S)cissors, (P)aper. 1, 2, 3!! > ").upper()
comHands = random.choice(_HANDS)

print(f"Computer: {comHands}")

if hand in _HANDS:

    winHand = _HANDS[(_HANDS.index(hand) + 1) % 3]

else:

    print("What is that lol?")
    exit()

judgement(winHand, hand, comHands)
