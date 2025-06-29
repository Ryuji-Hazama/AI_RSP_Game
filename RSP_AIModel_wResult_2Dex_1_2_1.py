import random

##########################
# Static variables

N = 5
win = 0
draw = 1
lose = 2
hisCount = N * 3
wCount = hisCount + 3
weightUpperLimit = 8 ** 2 * wCount
weightLowerLimit = wCount
Hands = ("R", "S", "P")

#
##########################
# Find middle value index

def findMidIndex(minIndex, maxIndex) -> int:

    if minIndex == 0 or maxIndex == 0:
        if minIndex == 1 or maxIndex == 1:

            midIndex = 2

        else:

            midIndex = 1

    else:

        midIndex = 0

    return midIndex

#
#################################
# Regulate over weight

def regWeight(weight):

    for i in range(wCount):

        weight[i] /= 2

#
#################################
# Amplify too small weight

def ampWeight(weight):

    for i in range(wCount):

        weight[i] *= 2.5

#
#################################
# Sort predictions

def sortPredictions(pred, history) -> list:

    retPred = [0 for _ in range(3)]

    retPred[win] = pred.index(max(pred))
    retPred[lose] = pred.index(min(pred))

    # If the pred values are all same!?
    # Find safer hand based on history

    if retPred[win] == retPred[lose]:

        prevHand = history[3:6].index(max(history[3:6])) - 3
        retPred[win] = (prevHand + 1) % 3
        retPred[lose] = (retPred[win] + 2) % 3

    # Find middle index

    retPred[draw] = findMidIndex(retPred[lose], retPred[win])

    # Return result

    return retPred

#
#################################
# Tag predictions based on weight

def tagPredictions(patWeight, history, bias) -> list:

    pred = [0.0 for _ in range(3)]
    softValue = [0.0 for _ in range(3)]
    retPred = [-1 for _ in range(3)]
    i = 0

    # Sum each weights

    while i < 3:

        sumSquare = 0

        for j in range (wCount):

            pred[i] += patWeight[i][j] * history[j]
            sumSquare += patWeight[i][j] ** 2

        # If the weight is too big

        if sumSquare > weightUpperLimit:

            # Regulate weight and re-calculate

            regWeight(patWeight[i])

        elif sumSquare < weightLowerLimit:

            # Amplify too small waight

            ampWeight(patWeight[i])

        else:

            # To next weight

            i += 1

    # Tag sum results

    retPred = sortPredictions(pred, history)

    # Get soft value

    totalBias = sum(bias)

    # If it is not the beggining

    if totalBias > 7:

        for i in range(3):

            softValue[i] = bias[i] / totalBias
        
        # Correct prediction based on bias

        pred[retPred[win]] *= softValue[win]
        pred[retPred[draw]] *= softValue[draw]
        pred[retPred[lose]] *= softValue[lose]

        # Re-tag result

        retPred = sortPredictions(pred, history)

    # Return result

    return retPred

#
##########################
# Update weight

def updateWeight(weight, nomValue) -> None:

    for i in range(wCount):

        weight[i] *= nomValue

#
##########################
# Normalize weight

def normWeight(weight, history, bias) -> None:

    totalBias = sum(bias)

    # Do nothing at the beginning

    if totalBias < 9:

        return
    
    # Find middle value index

    midB = findMidIndex(bias.index(min(bias)), bias.index(max(bias)))

    # Calculate normalizing weight

    nom = [0.0 for _ in range(3)]
    
    for i in range(3):

        nom[i] = 2 * bias[i] / totalBias

    # Normalize

    for i in range(3):

        pred = tagPredictions(weight[i], history, bias)

        updateWeight(weight[i][pred[win]], nom[win])
        updateWeight(weight[i][pred[draw]], nom[draw])
        updateWeight(weight[i][pred[lose]], nom[lose])

#
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
    
    hasHistory = his[0][0] != 0

    if hasHistory:

        # Get previous state

        prevState = his[0][0:3].index(max(his[0][0:3]))

        # Was prediction wrong?
            
        for i in range(3):
            
            if prev[i] * cur[i] <= 0:

                # Update state waights

                for j in range(3):

                    weight[prevState][i][j] += float(res[j] * his[0][j])

                # Update pattern weights

                for j in range(hisCount):

                    weight[prevState][i][j + 3] += float(prev[i] * his[0][j + 3])

    # - - - - - - - -*
    # Update history *
    # - - - - - - - -*

    # Shift pattern history 3 bits toward right

    for i in range(hisCount - 1, 2, -1):

        his[0][i + 3] = his[0][i]

    # Shift state history 3 bits toward right

    for i in range(hisCount * 2 -1, 2, -1):

        his[1][i] = his[1][i - 3]

    # Refresh previous state

    for i in range(3):

        his[0][i] = res[i]
        his[1][i] = 0

    # Save player hand in first 3 bits (prefix 3 bits)

    for i in range(3):

        his[0][3 + i] = prev[i]

    # Save state

    his[1][state] = 1

    # - - - - - - - - - - -*
    # Calculate prediction *
    # - - - - - - - - - - -*

    # Get bias

    bias = [0 for _ in range(3)]

    for i in range(hisCount * 2):

        bias[i % 3] += his[1][i]
        
    for i in range(3):

        if bias[i] < 2:

            # If ther is 0 in bias value,
            # it will reset the weight

            bias[i] = 2

        elif bias[i] > 8:

            # Limit bias to not too large

            bias[i] = 8

    # If there is no history, predict manually

    if not hasHistory:

        return (m + 2) % 3
    
    # Normalize the weights based on the bias

    normWeight(weight, his[0], bias)
    
    # Prediction

    handPred = tagPredictions(weight[state], his[0], bias)

    # Return result

    return handPred[win]

#
###############################
# Judge the result

def judgement(winHand, drawHand, judgeHand) -> int:

    if judgeHand == winHand:

        print("You win!")
        return 2

    elif judgeHand == drawHand:

        print("Oh, it's a draw.")
        return 1

    else:

        print("Aw... You lose.")
        return 0

#
####################################
# Valiables

nextPredict = True
result = -1
plHandInd = -1
preHandInd = -1
history = [[[] for _ in range(wCount)], [[] for _ in range(hisCount * 2)]]
weight = [[[[] for _ in range(wCount)] for _ in range(3)] for _ in range(3)]

#
###################################
# Initialize

def initial(result, plHandInd, preHandInd, history, weight):

    result = -1
    plHandInd = -1
    preHandInd = -1

    for i in range(len(history)):

        for j in range(len(history[i])):

            history[i][j] = 0

    for i in range(len(weight)):

        for j in range(len(weight[i])):

            for k in range(len(weight[i][j])):

                weight[i][j][k] = 1.0
                
#
###################################
# Main method

# Greeting

print("\n\n"
      "        * * * * * * * * * * *\n"
      "        * RSP AI Model 2Dex *\n"
      "        *     V 1.2.1       *\n"
      "        * * * * * * * * * * *\n"
      "\n"
      "\n"
      "* This is a classic Rock-Scissors-Paper game.\n"
      "* Choose your hand from\n"
      "  Rock (R) / Scissors (S) / Paper (P)\n"
      "  (Press Enter key to throw)\n"
      "* The computer predicts your hand\n"
      "  BEFORE you choose your hand.\n"
      "* The computer will learn from your pattern\n"
      "  and the prediction will be more accurate.\n"
      "* Even if you change your strategy\n"
      "  in the middle of the game,\n"
      "  the AI will sense that and\n"
      "  try to adapt to it.\n"
      "\n"
      "\n"
      "          *                *\n"
      "           CAN YOU BEAT IT?\n"
      "          *                *\n")

# Initialize the variables

initial(result, plHandInd, preHandInd, history, weight)

while True:

    stateBias = [0 for _ in range(3)] # [win, draw, lose]
    print("\n* * * * * * * * * * * * * * * * * * * * *"
          "\n* Are you ready?")

    while stateBias[win] < 30 and stateBias[lose] < 30:

        # Predict

        if nextPredict:

            preHandInd = predict(plHandInd, history, weight, preHandInd, result)
            comHand = Hands[(preHandInd + 2) % 3]

        # Get user input

        plHand = input("\n(R)ock, (S)cissors, (P)aper. 1, 2, 3!! > ").upper()

        try:

            plHandInd = Hands.index(plHand)

        except:

            nextPredict = False

            if plHand == "EXIT" or plHand == "QUIT":

                # Exit the game main loop
                break

            print("What is that lol?")
            continue;

        nextPredict = True

        # Figure out counter hand against computer

        winHand = Hands[(plHandInd + 1) % 3]

        # Print computer hand

        print(f"Computer: {comHand}\n")

        # Judge

        result = judgement(winHand, plHand, comHand)

        if result == 2:

            stateBias[win] += 1

        elif result == 1:

            stateBias[draw] += 1

        else:

            stateBias[lose] += 1
            result = 0

        # Show current summary

        print(f"Win: {stateBias[win]} / Draw: {stateBias[draw]} / Lose: {stateBias[lose]}")

    # Show final result

    if stateBias[win] > stateBias[lose]:

        print("\nYOU WIN!!")

    else:

        print("\nYOU LOSE...")

    # What do you do next?

    while True:

        rep = input("Will you --\n"
                    "\n"
                    "1 > Retry with current memory\n" \
                    "2 > Clear memory and retry\n" \
                    "3 > Quit\n\n" \
                    "> ")
        
        if rep == "1" or rep == "2" or rep == "3" or rep.upper() == "EXIT" or rep.upper() == "QUIT":

            break

        else:

            print(f"\n\"{rep}\" is not on the menu. :)")
        
    if rep == "1":

        continue

    elif rep == "2":

        # Reset memories

        nextPredict = True
        initial(result, plHandInd, preHandInd, history, weight)
        print("\n* Memories initialized. *\n")

    else:

        # Quit and exit
        break