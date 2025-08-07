from enum import IntEnum
import datetime
import inspect
import math
import os
from os import path, mkdir, getpid
import random
import Tools
import traceback

class Logger:

    def __init__(self, func = ""):

        self.CWD = os.getcwd()
        self.logfile = path.join(self.CWD, "logs", f"log_{datetime.datetime.now():%Y%m%d}.log")
        self.configFile = path.join(self.CWD, "config.mpl")
        self.intMaxValue = 4294967295
        self.consoleLogLevel = -1
        self.fileLogLevel = -1
        self.func = func

        #
        ############################
        # Check log directory

        if not path.isdir(path.join(self.CWD, "logs")):
            mkdir(path.join(self.CWD, "logs"))

        #
        ############################
        # Set output log levels

        if path.isfile(self.configFile):
            self.consoleLogLevel = self.isLogLevel(Tools.readMapleTag(self.configFile, "CMD", "Log settings"))
            self.fileLogLevel = self.isLogLevel(Tools.readMapleTag(self.configFile, "FLE", "Log settings"))

    #
    #####################
    # Set log level enum

    class LogLevel(IntEnum):

        TRACE = 0
        DEBUG = 1
        INFO = 2
        WARN = 3
        ERROR = 4
        FATAL = 5

    #
    ################
    # Check log level

    def isLogLevel(self, lLStr):

        for lLevel in self.LogLevel:
            if lLStr == lLevel.name:
                return lLevel

        return -1

    #
    #################################
    # Logger

    def logWriter(self, loglevel, message):

        ''' - - - - - - -*
        *                *
        * Logging Object *
        *                *
        * - - - - - - -'''

        f = open(self.logfile, "a")

        # Get caller informations

        callerFunc = inspect.stack()[1].function
        callerLine = inspect.stack()[1].lineno

        try:

            # Export to console and log file

            if loglevel >= self.consoleLogLevel:
                print(f"[{loglevel.name:5}][{self.func}] {callerFunc}({callerLine}) {message}")
        
            if loglevel >= self.fileLogLevel:
                print(f"({getpid()}) {datetime.datetime.now():%Y-%m-%d %H:%M:%S} [{loglevel.name:5}][{self.func}] {callerFunc}({callerLine}) {message}", file=f)

        except Exception as ex:

            # If faled to export, print error info to console

            print(f"[ERROR] {ex}")

        finally:
            f.close()

        # Check file size

        try:

            if path.getsize(self.logfile) > 3000000:

                i = 0
                logCopyFile = f"{self.logfile}{i}.log"

                while path.isfile(logCopyFile):

                    i += 1
                    logCopyFile = f"{self.logfile}{i}.log"

                os.rename(self.logfile, logCopyFile)

        except Exception as ex:
            print(f"[ERROR] {ex}")

    #
    ################################
    # Error messages

    def ShowError(self, ex):

        ''' - - - - - - - - -*
        *                    *
        * Show and log error *
        *                    *
        * - - - - - - - - -'''

        self.logWriter(self.LogLevel.ERROR, ex)
        self.logWriter(self.LogLevel.ERROR, traceback.format_exc())

##############################
# DL_RSP class

class DL_RSP:

    ##########################
    # Initialize the class

    def __init__(self, inputCount, nodesCount, outputCount, layers, learningRate):

        """
        inputCount: Input nodes count.\n
        nodesCount: Nodes count in a layer of hidden layers.\n
        outputCount Output nodes count.\n
        layers: Hidden layers count.\n
        learningRate: Learning Rate. (0.01 - 0.1 recomended)
        """

        self.INPUT_COUNT = inputCount
        self.NODES_COUNT = nodesCount
        self.OUTPUT_COUNT = outputCount
        self.LAYER_DEPTH = layers

        # For weight normalization

        self.weightUpperLimit = 5 ** 2 * nodesCount
        #self.weightLowerLimit = nodesCount

        self.learningRate = learningRate

        self.weight = [[[[] for _ in range(inputCount)] for _ in range(nodesCount)]] + \
                [[[[] for _ in range(nodesCount)] for _ in range(nodesCount)] for _ in range(layers - 1)] + \
                    [[[[] for _ in range(nodesCount)] for _ in range(outputCount)]]
        self.nodes = [[[] for _ in range(nodesCount)] for _ in range(layers)] + [[[] for _ in range(outputCount)]]
        self.nodeBiases = [[] for _ in range(nodesCount)]

        self.initialize()

    #
    ###################################
    # Initialize valiables

    def initialize(self) -> None:

        # Weights

        for i in range(len(self.weight)):
            for j in range(len(self.weight[i])):
                for k in range(len(self.weight[i][j])):

                    self.weight[i][j][k] = random.uniform(-2, 2)

        # To avoid zeroed

        for i in range(len(self.nodeBiases)):

            rootOf = 0
            negative = [1, -1][int(sum(self.weight[0][i]) < 0)]

            for j in range(len(self.weight[0][i])):

                rootOf += self.weight[0][i][j] ** 2

            self.nodeBiases[i] = \
                math.sqrt(rootOf) / len(self.weight[0][i]) * negative
            
        logger(logLevel.DEBUG, self.nodeBiases)

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
    # Calculate softmax values

    def convNodeSoftmax(self, layerIndex):

        """
        This function converts the node values into
        softmax values of the layer (0-1 value and sum(softmax) = 1)
        """

        sBase = sum(math.exp(n) for n in self.nodes[layerIndex])

        for i in range(len(self.nodes[layerIndex])):

            self.nodes[layerIndex][i] = math.exp(self.nodes[layerIndex][i]) / sBase

    #
    #################################
    # Calculate sigmoid values

    def convNodeSigmoid(self, nodesList) -> list:

        """
        This function converts the node values into
        sigmoid value (0-1)
        """

        return [1 / (1 + math.exp(node * -1)) for node in nodesList]

    #
    #################################
    # Calcurate Tanh value

    def convNodeTanh(self, nodesList) -> list:

        """
        This function normalize the list values
        between -1 to 1
        """

        #print(nodesList)
        return [((math.exp(node) - math.exp(node * -1)) \
                                   / (math.exp(node) + math.exp(node * -1))) \
                                      for node in nodesList]
        
    #
    ##########################
    # Update weight

    def updateWeight(weight, nomValue) -> None:

        for i in range(DL_RSP.W_COUNT):

            weight[i] *= nomValue

    #
    ##########################
    # Normalize weight

    def normWeight(self, layerInd) -> None:

        MAX_VALUE = 2.0

        for i, weightLayer in enumerate(self.weight[layerInd]):

            self.weight[layerInd][i] = [max(min(w, MAX_VALUE), -MAX_VALUE) for w in weightLayer]
            
    #
    #################################
    # Learning process (MSE)

    def learnPatternMSE(self, pattern, target) -> None:

        # Tempolary Nodes

        tempNodes = [[] for _ in range(2)]

        # Get output target (the true hand)

        outTarget = [0] * self.OUTPUT_COUNT
        outTarget[target] = 1

        print(outTarget)
        logger(logLevel.DEBUG, outTarget)

        # - - - - - - - -*
        # Update weights *
        # with MSE costs *
        # - - - - - - - -*

        # Get cost per output node (for MSE values)

        cost = [(self.nodes[self.LAYER_DEPTH][i] - outTarget[i]) ** 2 for i in range(self.OUTPUT_COUNT)]
        mseValue = sum(cost) / self.OUTPUT_COUNT
        print(cost)

        for predInd in range(self.OUTPUT_COUNT):

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
            # Last layer

            for node1Ind in range(self.NODES_COUNT):

                # Get values for update calculation

                outputNode = self.nodes[self.LAYER_DEPTH][predInd]
                activation = self.nodes[self.LAYER_DEPTH - 1][node1Ind]
                baseGrade = (outputNode - outTarget[predInd]) * activation

                # Calculate update value

                updateValue = baseGrade * cost[predInd] * self.learningRate

                # Update weight and previous node value

                self.weight[self.LAYER_DEPTH][predInd][node1Ind] -= updateValue

        # Normalize weight values

        self.normWeight(self.LAYER_DEPTH)

        # Update temp node values
        
        tempNodes[0] = self.weight[self.LAYER_DEPTH][target][:]

        # Convert node values

        tempNodes[0] = self.convNodeSigmoid(tempNodes[0])

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Between hidden layer(s)

        for nodeLayersIndex in range(self.LAYER_DEPTH - 1, 0, -1):

            # Update weights value

            for node1Ind in range(self.NODES_COUNT):
                for node0Ind in range(self.NODES_COUNT):

                    # Get values for update

                    influence = self.nodes[nodeLayersIndex][node1Ind]
                    activation = self.nodes[nodeLayersIndex - 1][node0Ind]
                    baseGrade = (influence - tempNodes[0][node1Ind]) * activation

                    # Get update value

                    updateValue = baseGrade * mseValue * self.learningRate

                    # Add confidence, emotion etc in the future

                    self.weight[nodeLayersIndex][node1Ind][node0Ind] -= updateValue

            # Normalize the weight values

            self.normWeight(nodeLayersIndex)

            # Move temp nodes value

            tempNodes[1] = tempNodes[0][:]

            # Change nodes value

            for node0Ind in range(self.NODES_COUNT):

                tempNodes[0][node0Ind] = 0

                for node1Ind in range(self.NODES_COUNT):

                    # Get values for update

                    activation = tempNodes[1][node1Ind]
                    weight = self.weight[nodeLayersIndex][node1Ind][node0Ind]

                    # Update

                    tempNodes[0][node0Ind] -= activation * weight
                    
            # Normalize weight and node values

            tempNodes[0] = self.convNodeSigmoid(tempNodes[0])

        # Update bias values
        """
        for i in range(self.NODES_COUNT):

                self.nodeBiases[i] += \
                    sum([self.weight[0][i][j] * cost[target] \
                    for j in range(self.NODES_COUNT)])
        """
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # First layer

        for nodeIndex in range(self.NODES_COUNT):
            for inputIndex in range(self.INPUT_COUNT):

                # Get values for update

                inputValue = pattern[inputIndex]
                activation = self.nodes[0][nodeIndex] - tempNodes[0][nodeIndex]
                baseGrade = inputValue * activation

                # Get update value

                updateValue = baseGrade * cost[target] * self.learningRate

                self.weight[0][nodeIndex][inputIndex] -= updateValue

        # Normalize the weights

        self.normWeight(0)

    #
    #################################
    # Make a prediction

    def makePredictions(self, pattern) -> list:

        # - - - - - - - - - - - *
        # Calculate node values *
        # - - - - - - - - - - - *

        # First layer

        for i in range(self.NODES_COUNT):

            nodeValue = 0

            for j in range(self.INPUT_COUNT):

                activation = pattern[j]
                weight = self.weight[0][i][j]

                nodeValue += weight * activation

            self.nodes[0][i] = nodeValue + self.nodeBiases[i]

        # Get sigmoid for the first layer

        self.nodes[0] = self.convNodeSigmoid(self.nodes[0])

        # Hidden layer

        for i in range(1, self.LAYER_DEPTH):
            for j in range(self.NODES_COUNT):

                nodeValue = 0

                for k in range(self.NODES_COUNT):

                    activation = self.nodes[i - 1][k]
                    weight = self.weight[i][j][k]

                    nodeValue += weight * activation

                self.nodes[i][j] = nodeValue

            # Get sigmoid

            self.nodes[i] = self.convNodeSigmoid(self.nodes[i])

        # Last output layer

        for i in range(self.OUTPUT_COUNT):

            outputValue = 0

            for j in range(self.NODES_COUNT):

                activation = self.nodes[self.LAYER_DEPTH - 1][j]
                weight = self.weight[self.LAYER_DEPTH][i][j]

                outputBase = activation * weight
                outputValue += outputBase # Add emotion or something in the future

            self.nodes[self.LAYER_DEPTH][i] = outputValue

        # Get softmax

        self.convNodeSoftmax(self.LAYER_DEPTH)

        ## For Debug ##

        print(self.nodes[self.LAYER_DEPTH])

        logger(logLevel.DEBUG, "Weights:")

        for weightLayer in self.weight:
            for nodeWeight in weightLayer:
                logger(logLevel.DEBUG, nodeWeight)

        logger(logLevel.DEBUG, "Nodes:")

        for nodeLayer in self.nodes:
            logger(logLevel.DEBUG, nodeLayer)

        ## ^^ Debug ^^ ##

        # Return result

        return self.nodes[self.LAYER_DEPTH]

#
#####################################
# Global variables

N = 5
WIN = 0
DRAW = 1
LOSE = 2
HANDS = ("R", "S", "P")

result = -1
playerHandIndex = -1
predictedHnadIndex = -1

history = [[0 for _ in range(N * 3 + 3)], [[] for _ in range(N * 2 * 3)]]

cLogger = Logger("RSP")
logger = cLogger.logWriter
logLevel = cLogger.LogLevel
Prediction = DL_RSP(18, 9, 3, 2, 0.05)

#
#####################################
# Initialize

def initialize():

    for i in range(len(history)):
        for j in range(len(history[i])):

            history[i][j] = 0

    Prediction.initialize()

#
#####################################
# Make a prediction with an AI model

def predict(plHandInd, result, history) -> int:

    # If this is not the first time,
    # train the machine

    if plHandInd != -1:
        
        # - - - - - - - - - *
        # Learn and predict *
        # - - - - - - - - - *

        # Learning process

        Prediction.learnPatternMSE(history[0], plHandInd)

        # Previous player hand

        prev = [-1] * 3
        prev[plHandInd] = 1

        # Previous result

        res = [-1] * 3
        res[result] = 1

        # - - - - - - - -*
        # Update history *
        # - - - - - - - -*

        # Shift pattern history 3 bits toward right

        history[0][6:] = history[0][3:-3]

        # Shift state history 3 bits toward right

        history[1][3:] = history[1][0:-3]

        # Refresh previous state and save

        for i in range(3):

            history[0][i] = res[i]
            history[1][i] = 0

        history[1][result] = 1

        # Save player hand in first 3 bits (prefix)

        for i in range(3):

            history[0][3 + i] = prev[i]

    # - - - - - - - - - - -*
    # Calculate prediction *
    # - - - - - - - - - - -*

    # Prediction

    preList = Prediction.makePredictions(history[0])

    # Return result

    return preList.index(max(preList))

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

logger(logLevel.INFO, "Start game")

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

nextPredict = True

while True:

    resultState = [0 for _ in range(3)] # [win, draw, lose]
    print("\n* * * * * * * * * * * * * * * * * * * * *"
          "\n* Are you ready?")

    while resultState[WIN] < 30 and resultState[LOSE] < 30:

        # Predict

        if nextPredict:

            predictedHnadIndex = predict(playerHandIndex, result, history)
            comHand = HANDS[(predictedHnadIndex + 2) % 3]

        # Get user input

        plHand = input("\n(R)ock, (S)cissors, (P)aper. 1, 2, 3!! > ").upper()

        if plHand in HANDS:

            # Figure out winnable hand for the player

            playerHandIndex = HANDS.index(plHand)
            winHand = HANDS[(playerHandIndex + 1) % 3]

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
        
        result = judgement(winHand, plHand, comHand)

        if result == 2:

            resultState[WIN] += 1

        elif result == 1:

            resultState[DRAW] += 1

        else:

            resultState[LOSE] += 1
            result = 0

        # Show current summary

        print(f"Win: {resultState[WIN]} / Draw: {resultState[DRAW]} / Lose: {resultState[LOSE]}")

    print("\n* - - - - - - - - - - - - - - -")

    # Show final result

    if resultState[WIN] > resultState[LOSE]:

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
        initialize()
        print("\n* AI memory cleared. *\n")

    else:

        logger(logLevel.INFO, "Exit game")

        # Quit and exit
        break