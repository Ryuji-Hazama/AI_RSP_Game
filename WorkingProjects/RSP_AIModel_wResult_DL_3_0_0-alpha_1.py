import math
import random

##############################
# DL_RSP class

class DL_RSP():

    ##########################
    # Class variables

    N = 5
    WIN = 0
    DRAW = 1
    LOSE = 2
    HIS_COUNT = N * 3
    W_COUNT = HIS_COUNT + 3
    NODES_COUNT = 9
    HANDS = ("R", "S", "P")

    #
    ##########################
    # Initialize the class

    def __init__(self):

        self.weightUpperLimit = 8 ** 2 * DL_RSP.W_COUNT
        self.weightLowerLimit = DL_RSP.W_COUNT

        self.result = -1
        self.plHandInd = -1
        self.preHandInd = -1

        self.history = [[[] for _ in range(DL_RSP.W_COUNT)], [[] for _ in range(DL_RSP.HIS_COUNT * 2)]]
        self.weight = [[[[] for _ in range(DL_RSP.W_COUNT)] for _ in range(DL_RSP.NODES_COUNT)], \
                [[[] for _ in range(DL_RSP.NODES_COUNT)] for _ in range(DL_RSP.NODES_COUNT)], \
                    [[[] for _ in range(DL_RSP.NODES_COUNT)] for _ in range(3)]]
        self.nodes = [[[] for _ in range(DL_RSP.NODES_COUNT)] for _ in range(2)] + [[[] for _ in range(3)]]
        self.nodeBiases = [[] for _ in range(DL_RSP.NODES_COUNT)]

        self.initialize()

    #
    ###################################
    # Initialize valiables

    def initialize(self) -> None:

        self.result = -1
        self.plHandInd = -1
        self.preHandInd = -1

        # History

        for i in range(len(self.history)):
            for j in range(len(self.history[i])):

                self.history[i][j] = 0

        # Weights

        for i in range(len(self.weight)):
            for j in range(len(self.weight[i])):
                for k in range(len(self.weight[i][j])):

                    self.weight[i][j][k] = random.uniform(-1, 1)

        # To avoid zeroed

        self.updateNodeBiases()

    #
    ##########################
    # Update node biases

    def updateNodeBiases(self):

        """
        Get bias values based on weight values
        """

        for i in range(len(self.nodeBiases)):

            rootOf = 0
            negative = [1, -1][int(sum(self.weight[0][i]) < 0)]

            for j in range(len(self.weight[0][i])):

                rootOf += self.weight[0][i][j] ** 2

            self.nodeBiases[i] = \
                math.sqrt(rootOf) / len(self.weight[0][i]) * negative

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
    # Get bias

    def getBias(self, L) -> list:

        sHistory = self.history[1]

        # Get bias

        bias = [0 for _ in range(3)]    # win / draw / lose

        for i in range(L * 3):  # Length * 3 states

            bias[i % 3] += sHistory[i]

        # Set limits

        biasLowerLimit = L / 5
        biasUpperLimit = L * 0.8
            
        for i in range(3):

            if bias[i] < biasLowerLimit:

                # If there is 0 in bias value,
                # it will reset the weight

                bias[i] = biasLowerLimit

            elif bias[i] > biasUpperLimit:

                # Limit bias to not too large

                bias[i] = biasUpperLimit

        # Return bias list

        return bias

    #
    #################################
    # Regulate over weight

    def regWeight(self):

        for i in range(DL_RSP.W_COUNT):

            self.weight[i] /= 2

    #
    #################################
    # Calculate softmax values

    def convNodeSoftmax(self, layerIndex):

        """
        This function convert the node values into
        softmax values of the layer.
        """

        sBase = sum(math.exp(n) for n in self.nodes[layerIndex])

        for i in range(len(self.nodes[layerIndex])):

            self.nodes[layerIndex][i] = math.exp(self.nodes[layerIndex][i]) / sBase

    #
    #################################
    # Normalize nodes value

    def normNodes(self, layerIndex):

        """
        This function normalize the node values
        between -1 to 1
        """

        x1Value = max([abs(max(self.nodes[layerIndex])), abs(min(self.nodes[layerIndex]))])

        for i in range(len(self.nodes[layerIndex])):

            self.nodes[layerIndex][i] /= x1Value

    #
    #################################
    # Sort predictions

    def sortPredictions(self, pred) -> list:

        retPred = [0 for _ in range(3)]

        retPred[DL_RSP.WIN] = pred.index(max(pred))
        retPred[DL_RSP.LOSE] = pred.index(min(pred))

        # If the pred values are all same!?
        # Find safer hand based on history

        if retPred[DL_RSP.WIN] == retPred[DL_RSP.LOSE]:

            prevHand = self.history[0][3:6].index(max(self.history[0][3:6])) - 3
            retPred[DL_RSP.WIN] = (prevHand + 1) % 3
            retPred[DL_RSP.LOSE] = (retPred[DL_RSP.WIN] + 2) % 3

        # Find middle index

        retPred[DL_RSP.DRAW] = self.findMidIndex(retPred[DL_RSP.LOSE], retPred[DL_RSP.WIN])

        # Return result

        return retPred

    #
    #################################
    # Tag predictions based on weight

    def tagPredictions(self) -> list:

        # softValue = [0.0 for _ in range(3)] not now
        retPred = [-1 for _ in range(3)]
        i = 0

        # - - - - - - - - - - - *
        # Calculate node values *
        # - - - - - - - - - - - *

        # First layer

        for i in range(DL_RSP.NODES_COUNT):

            nodeValue = 0

            for j in range(DL_RSP.W_COUNT):

                weight = self.weight[0][i][j]
                activation = self.history[0][j]

                nodeValue += weight * activation

            self.nodes[0][i] = nodeValue + self.nodeBiases[i]

        # Get softmax for the first layer

        self.convNodeSoftmax(0)

        # Hidden layer

        layerDepth = len(self.nodes) - 1

        for i in range(1, layerDepth):
            for j in range(DL_RSP.NODES_COUNT):

                nodeValue = 0

                for k in range(DL_RSP.NODES_COUNT):

                    weight = self.weight[i][j][k]
                    activation = self.nodes[i - 1][k]

                    nodeValue += weight * activation

                self.nodes[i][j] = nodeValue

            # Get softmax

            self.convNodeSoftmax(i)

        # Last output layer

        for i in range(len(self.nodes[layerDepth])):

            outputValue = 0

            for j in range(DL_RSP.NODES_COUNT):

                activation = self.nodes[layerDepth - 1][j]
                weight = self.weight[layerDepth][i][j]

                outputBase = activation * weight
                outputValue += outputBase # Add emotion or something in the future

            self.nodes[layerDepth][i] = outputValue

        # Get softmax

        self.convNodeSoftmax(layerDepth)
        print(self.nodes[layerDepth])   # Debug

        # Tag sum results

        # retPred = self.sortPredictions(self.nodes[layerDepth])

        """
        # NOT NOW
        # Get soft value

        bias = self.getBias(DL_RSP.N)
        totalBias = sum(bias)

        # If it is not the beggining
        
        if sum(self.history[1]) > DL_RSP.N:

            for i in range(3):

                softValue[i] = bias[i] / totalBias
            
            # Correct prediction based on bias

            pred[retPred[DL_RSP.WIN]] *= softValue[DL_RSP.WIN]
            pred[retPred[DL_RSP.DRAW]] *= softValue[DL_RSP.DRAW]
            pred[retPred[DL_RSP.LOSE]] *= softValue[DL_RSP.LOSE]

            # Re-tag result

            retPred = self.sortPredictions(pred)
        """

        # Return result

        return self.nodes[layerDepth].index(max(self.nodes[layerDepth]))

    #
    ##########################
    # Update weight

    def updateWeight(weight, nomValue) -> None:

        for i in range(DL_RSP.W_COUNT):

            weight[i] *= nomValue

    #
    ##########################
    # Normalize weight

    def normWeight(self) -> None:

        # Get bias

        bias = self.getBias(DL_RSP.N * 2)
        totalBias = sum(bias)

        # Do nothing at the beginning

        if sum(self.history[1]) < DL_RSP.N:

            return
        
        # Find middle value index

        midB = self.findMidIndex(bias.index(min(bias)), bias.index(max(bias)))

        # Calculate normalizing weight

        nom = [0.0 for _ in range(3)]
        
        for i in range(3):

            nom[i] = 2 * bias[i] / totalBias

        # Normalize

        for i in range(3):

            pred = self.tagPredictions(self.weight[i], self.history)

            self.updateWeight(self.weight[i][pred[DL_RSP.WIN]], nom[DL_RSP.WIN])
            self.updateWeight(self.weight[i][pred[DL_RSP.DRAW]], nom[DL_RSP.DRAW])
            self.updateWeight(self.weight[i][pred[DL_RSP.LOSE]], nom[DL_RSP.LOSE])

    #
    ##########################
    # Make a prediction

    def predict(self) -> int:

        # If this is the first time
        # (cannot predict) return random

        if self.plHandInd != -1:
            # return random.randint(0, 2)
            
            # - - - - - - - - - *
            # Learn and predict *
            # - - - - - - - - - *

            layerDepth = len(self.nodes) - 1

            # Previous player hand

            prev = [-1] * 3
            prev[self.plHandInd] = 1

            # Previous result

            res = [-1] * 3
            res[self.result] = 1

            # Get output target (the true hand)

            outTarget = [0] * 3
            outTarget[self.plHandInd] = 1
            
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

            # - - - - - - - -*
            # Update weights *
            # with MSE costs *
            # - - - - - - - -*

            # Get cost per output node

            cost = 0

            for i in range(3):

                cost += (self.nodes[layerDepth][i] - outTarget[i]) ** 2

            for predInd in range(3):

                # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
                # Last layer

                for node1Ind in range(DL_RSP.NODES_COUNT):

                    # Get values for update calculation

                    negaPosiInfluence = prev[predInd]
                    activation = self.nodes[layerDepth - 1][node1Ind]
                    baseGrade = negaPosiInfluence * activation

                    # Calculate update value

                    updateValue = baseGrade * cost

                    # Update weight and previous node value

                    self.weight[layerDepth][predInd][node1Ind] += updateValue

            # Update and normalize node values

            self.nodes[layerDepth - 1] = self.weight[layerDepth][self.plHandInd][:]
            self.normNodes(layerDepth - 1)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Between hidden layer(s)

            for nodeLayersIndex in range(layerDepth - 1, 0, -1):

                # Update weights value

                for node1Ind in range(DL_RSP.NODES_COUNT):
                    for node0Ind in range(DL_RSP.NODES_COUNT):

                        # Get values for update

                        influence = self.nodes[nodeLayersIndex][node1Ind]
                        activation = self.nodes[nodeLayersIndex - 1][node0Ind]
                        baseGrade = influence * activation

                        # Get update value

                        updateValue = baseGrade * cost # Add confidence, emotion etc in the future

                        self.weight[nodeLayersIndex][node1Ind][node0Ind] += updateValue

                # Change nodes value

                for node0Ind in range(DL_RSP.NODES_COUNT):

                    self.nodes[nodeLayersIndex - 1][node0Ind] = 0

                    for node1Ind in range(DL_RSP.NODES_COUNT):

                        # Get values for update

                        activation = self.nodes[nodeLayersIndex][node1Ind]
                        weight = self.weight[nodeLayersIndex][node1Ind][node0Ind]

                        # Update

                        self.nodes[nodeLayersIndex - 1][node0Ind] += activation * weight
                        
                # Normalize node values

                self.normNodes(nodeLayersIndex - 1)

            # Update bias values

            for i in range(DL_RSP.NODES_COUNT):

                    self.nodeBiases[i] += \
                        sum(self.weight[0][i][j] * cost \
                        for j in range(DL_RSP.NODES_COUNT))

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # First layer

            for nodeIndex in range(DL_RSP.NODES_COUNT):
                for hisIndex in range(DL_RSP.W_COUNT):

                    # Get values for update

                    inputValue = self.history[0][hisIndex]
                    activation = self.nodes[0][nodeIndex]

                    # Get update value

                    updateValue = inputValue * activation

                    self.weight[0][nodeIndex][hisIndex] += updateValue
                            
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

            # - - - - - - - -*
            # Update history *
            # - - - - - - - -*

            # Shift pattern history 3 bits toward right

            self.history[0][6:] = self.history[0][3:-3]

            # Shift state history 3 bits toward right

            self.history[1][3:] = self.history[1][0:-3]

            # Refresh previous state and save

            for i in range(3):

                self.history[0][i] = res[i]
                self.history[1][i] = 0

            self.history[1][self.result] = 1

            # Save player hand in first 3 bits (prefix)

            for i in range(3):

                self.history[0][3 + i] = prev[i]

        # - - - - - - - - - - -*
        # Calculate prediction *
        # - - - - - - - - - - -*

        # Normalize the weights based on the bias

        #normWeight(weight, his) # disabled for now
        
        # Prediction

        handPred = self.tagPredictions()

        # Return result

        return handPred

    #
    ###############################

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

        print("Aww... You lose.")
        return 0

#
###################################
# Main method

# Greeting

print("\n\n"
      "        * * * * * * * * * * *\n"
      "        * RSP AI Model 2Dex *\n"
      "        *     V 3.0.0       *\n"
      "        * * * * * * * * * * *\n"
      "\n"
      "\n"
      "* This is a classic Rock-Scissors-Paper game.\n"
      "* Choose your hand:\n"
      "  Rock (R), Scissors (S), or Paper (P)\n"
      "  (Press Enter key to throw)\n"
      "* The computer predicts your hand\n"
      "  BEFORE you choose your hand.\n"
      "* The computer will learn your pattern\n"
      "  and the prediction will be more accurate.\n"
      "* Even if you change your strategy\n"
      "  in the middle of the game,\n"
      "  the AI will sense that and\n"
      "  try to adapt to it.\n"
      "* The winner will be the one who\n"
      "  wins 30 times first."
      "\n"
      "\n"
      "          *                *\n"
      "           CAN YOU BEAT IT?\n"
      "              GOOD LUCK!\n"
      "          *                *\n")

# Class instance and variables

Prediction = DL_RSP()
nextPredict = True

while True:

    resultState = [0 for _ in range(3)] # [win, draw, lose]
    print("\n* * * * * * * * * * * * * * * * * * * * *"
          "\n* Are you ready?")

    while resultState[DL_RSP.WIN] < 30 and resultState[DL_RSP.LOSE] < 30:

        # Predict

        if nextPredict:

            Prediction.preHandInd = Prediction.predict()
            comHand = DL_RSP.HANDS[(Prediction.preHandInd + 2) % 3]

        # Get user input

        plHand = input("\n(R)ock, (S)cissors, (P)aper. 1, 2, 3!! > ").upper()

        if plHand in DL_RSP.HANDS:

            # Figure out winnable hand for the player

            Prediction.plHandInd = DL_RSP.HANDS.index(plHand)
            winHand = DL_RSP.HANDS[(Prediction.plHandInd + 1) % 3]

        elif plHand == "EXIT" or plHand == "QUIT":

            # Exit the game main loop
            break

        else:

            nextPredict = False
            print(random.choice(["What is that? lol", "Huh? That's not a move!"]))

            continue;

        nextPredict = True

        # Print computer hand

        print(f"Computer: {comHand}\n")

        # Judge
        
        Prediction.result = judgement(winHand, plHand, comHand)

        if Prediction.result == 2:

            resultState[DL_RSP.WIN] += 1

        elif Prediction.result == 1:

            resultState[DL_RSP.DRAW] += 1

        else:

            resultState[DL_RSP.LOSE] += 1
            Prediction.result = 0

        # Show current summary

        print(f"Win: {resultState[DL_RSP.WIN]} / Draw: {resultState[DL_RSP.DRAW]} / Lose: {resultState[DL_RSP.LOSE]}")

    print("\n* - - - - - - - - - - - - - - -")

    # Show final result

    if resultState[DL_RSP.WIN] > resultState[DL_RSP.LOSE]:

        print("\n"
              "*         *\n"
              " YOU WIN!!\n"
              "*         *\n")

    else:

        print("\n"
              "*           *\n"
              " YOU LOSE...\n"
              "*           *\n")

    # What do you do next?

    while True:

        rep = input("Will you --\n"
                    "\n"
                    "1 > Retry with current memory\n" \
                    "2 > Clear memory and retry\n" \
                    "3 > Quit\n\n" \
                    "> ")
        
        if rep == "1" or rep == "2" or rep == "3" \
            or rep.upper() == "EXIT" or rep.upper() == "QUIT":

            break

        else:

            print(f"\n\"{rep}\" is not on the menu. :)")
        
    if rep == "1":

        continue

    elif rep == "2":

        # Reset memories

        nextPredict = True
        Prediction.initial()
        print("\n* AI memory cleared. *\n")

    else:

        # Quit and exit
        break