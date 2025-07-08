import random

##########################
# Static variables

N = 5
Hands = ["R", "S", "P"]

##########################
# Make a prediction

def predict(m, his, weight, preHand, state) -> int:

    # If this is the first time
    # (cannto predict) return random

    if m == -1:
        return random.randint(0, 2)
    
    # - - - - - - - - - *
    # Learn and predict *
    # - - - - - - - - - *

    # Previous player hand

    prev = [-1] * 3
    prev[m] = 1

    # Previous prediction (current hand)

    cur = [-1] * 3
    cur[preHand] = 1

    # Previous result

    res = [-1] * 3
    res[state] = 1

    # If the prediction was wrong
    # learn and correct

    # Check history data
    
    hasHistory = his[0] != 0

    if hasHistory:

        # Get previous state

        prevState = his[0:3].index(max(his[0:3]))

        # Prediction was wrong?
            
        for i in range(3):
            
            if prev[i] * cur[i] <= 0:

                # Update state waights

                for j in range(0, 3):

                    weight[prevState][(3 * N + 3) * i + j] += res[j] * his[j]

                # Update pattern weights

                for j in range(0, N * 3):

                    weight[prevState][(3 * N + 3) * i + 3 + j] += prev[i] * his[3 + j]

    # - - - - - - - -*
    # Update history *
    # - - - - - - - -*

    # Refresh previous state

    for i in range(3):

        his[i] = res[i]

    # Shift 3 bits toward right

    for i in range(17, 5, -1):

        his[i] = his[i - 3]

    # Save player's hand in first 3 bits (prefix 3 bits)

    for i in range(3):

        his[3 + i] = prev[i]

    # - - - - - - - - - - -*
    # Calculate prediction *
    # - - - - - - - - - - -*

    # If there is no history, predict manually

    if not hasHistory:

        return (m + 2) % 3
    
    # Prediction

    pr = [0] * 3

    for i in range(3):

        for j in range(0, N * 3 + 3):

            pr[i] += weight[state][(N * 3 + 3) * i + j] * his[j]

    # Find most heavy prediction

    maxPre = 0

    for i in range(3):

        if pr[i] > pr[maxPre]:

            maxPre = i

    # Return result

    return maxPre

#
###############################
# Judge the result

def judgement(win, draw, judgeHand) -> int:

    if judgeHand == win:

        print("You win!")
        return 0

    elif judgeHand == draw:

        print("Oh, it's a draw.")
        return 1

    else:

        print("Aw... You lose.")
        return 2

#
####################################
# Main method

# Initialize

win = 0
drw = 0
los = 0
result = -1
plHandInd = -1
preHandInd = -1
history = [0] * ((N * 3) + 3)
weight = [[0] * ((N * 3 + 3) * 3)] * 3
predictedHand = [0] * 3

#-----------------------------------

while win < 30 or los < 30:

    # Predict

    preHandInd = predict(plHandInd, history, weight, preHandInd, result)
    comHand = Hands[(preHandInd + 2) % 3]

    # Get user input

    plHand = input("(R)ock, (S)cissors, (P)aper. 1, 2, 3!! > ").upper()

    try:
        plHandInd = Hands.index(plHand)

    except:

        print("What is that lol?")
        plHandInd = preHandInd

        continue;

    # Figure out counter hand against computer

    winHand = Hands[(plHandInd + 1) % 3]

    # Print computer hand

    print(f"Computer: {comHand}")

    # Judge

    result = judgement(winHand, plHand, comHand)

    if result == 0:

        win += 1

    elif result == 1:

        drw += 1

    else:

        los += 1
        result = 2

    # Show current summary

    print(f"Win: {win} / Draw: {drw} / Lose: {los}")

# Show final result

if win > los:

    print("YOU WIN!!")

else:

    print("YOU LOSE...")
