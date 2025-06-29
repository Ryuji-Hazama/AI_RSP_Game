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

hands = input("(R)ock, (S)cissors, (P)aper. 1, 2, 3!! > ").upper()

if hands == "R":

    comHand = random.choice(["R", "P"])
    winHand = "S"

elif hands == "S":

    comHand = random.choice(["R", "S"])
    winHand = "P"

elif hands == "P":

    comHand = random.choice(["S", "P"])
    winHand = "R"

else:

    print("What is that lol?")
    exit()

print(f"Computer: {comHand}")
judgement(winHand, hands, comHand)