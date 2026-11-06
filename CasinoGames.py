import random
from copy import copy

import DnDUtil

def main():

    print("Welcome to Casino Mode!")
    print("These are the available games: roulette, highlow, slots, 21, gyp, Dragon's Hoard (dh), Hand of Fate (hof), Faerune Keep 'Em (fke)")
    print("Type help along with the name of the game to get a description of how the game works along with optional parameters that can change the game")
    
    while True:

        rawInput = input('What game would you like to play? ')
        if (rawInput == '' or rawInput == 'done' or rawInput == 'leave'):
            return
        command = rawInput.split()
        initCommand = command[0]
        numArgs = len(command)

        if (initCommand == 'help' and numArgs == 2):
            help(command[1])

        elif (initCommand == 'roulette'):
            playRoulette()

        elif (initCommand == 'highlow'):
            playHighLow()

        elif (initCommand == 'slots'):
            playSlots()

        elif (initCommand == '21'):
            playTwentyOne()

        elif (initCommand == 'gyp'):
            playGyp()

        elif (initCommand == 'dh'):
            playDragonsHoard()

        elif (initCommand == 'hof'):
            playHandOfFate()

        elif (initCommand == 'fke'):
            playFaeruneKeepEm()

        else:
            print("Invalid command")

def playRoulette():

    while True:

        bets = []
        # generate the roulette spin ahead of time to optimize code
        result = random.randint(-1,36)
        rawInput = 'input'
        while (rawInput != '' and rawInput != 'done'):

            rawInput = input('Place your bets: ')
            if (rawInput != '' and rawInput != 'done'):

                betInput = rawInput.split()
                if (betInput == ['help']):
                    print("Valid bet types are: a single number, high, low, red, black, green, even, odd, or dozen1/2/3")
                elif (len(betInput) != 2):
                    print("Input should be a bet type followed by the bet amount")
                else:

                    betType = betInput[0]
                    betAmount = DnDUtil.getInt(betInput[1])
                    payOut = 0
                    # single number bet
                    if (betType.isdigit()):
                        if (betType == '00' and result == -1 or betType != '00' and int(betType) == result):
                            payOut = 36*betAmount
                    elif (betType == 'high'):
                        if (result >= 19):
                            payOut = 2*betAmount
                    elif (betType == 'low'):
                        if (result >= 1 and result <= 18):
                            payOut = 2*betAmount
                    elif (betType == 'red'):
                        if (result in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]):
                            payOut = 2*betAmount
                    elif (betType == 'black'):
                        if (result in [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]):
                            payOut = 2*betAmount
                    elif (betType == 'green'):
                        if (result == -1 or result == 0):
                            payOut = 18*betAmount
                    elif (betType == 'even'):
                        if (result > 0 and result % 2 == 0):
                            payOut = 2*betAmount
                    elif (betType == 'odd'):
                        if (result > 0 and result % 2 == 1):
                            payOut = 2*betAmount
                    elif (betType == 'dozen1'):
                        if (result >= 1 and result <= 12):
                            payOut = 3*betAmount
                    elif (betType == 'dozen2'):
                        if (result >= 13 and result <= 24):
                            payOut = 3*betAmount
                    elif (betType == 'dozen3'):
                        if (result >= 25):
                            payOut = 3*betAmount
                    else:
                        print("Invalid bet type!")
                        payOut = -1

                    if (payOut > -1):
                        bets.append([betType,betAmount,payOut])

        if (not(bets)):
            return

        if (result == -1):
            resultString = '00'
        else:
            resultString = str(result)
        print("The ball lands on", resultString+'!')
        betNumber = 1
        for bet in bets:
            print("Bet", str(betNumber)+':', bet[0], bet[1])
            if (bet[2] > 0):
                print("Result: You win", DnDUtil.getPassText(bet[2]), "gold!", '(+'+str(bet[2]-bet[1])+')')
            else:
                print("Result:", DnDUtil.getFailText("You lose"))
            betNumber += 1

def playHighLow():

    answer = DnDUtil.getAnswer('Play high/low')
    while (answer == 'y'):
        firstRoll = random.randint(1,20)
        print("First roll is a", firstRoll)
        rawInput = input('Will the next roll be high or low? ')
        while (rawInput != 'high' and rawInput != 'low'):
            print("Invalid input! Valid inputs are high and low.")
            rawInput = input('Will the next roll be high or low? ')
        secondRoll = random.randint(1,20)
        if (secondRoll > firstRoll):
            compareText = 'high'
        elif (secondRoll < firstRoll):
            compareText = 'low'
        else:
            compareText = 'even'
        print("Second roll is a", secondRoll, '('+compareText+')')
        if (rawInput == compareText):
            print(DnDUtil.getPassText("You win!"))
        else:
            print(DnDUtil.getFailText("You lose."))
        answer = DnDUtil.getAnswer('Play again')

def playSlots():

    answer = DnDUtil.getAnswer('Play slots (7gp to play)')
    netResult = 0
    while (answer == 'y'):
        roll1 = random.randint(1,6)
        roll2 = random.randint(1,6)
        roll3 = random.randint(1,6)
        rolls = [roll1, roll2, roll3]
        print("---------")
        print(roll1, roll2, roll3)
        print("---------")
        roll1Count = rolls.count(roll1)
        roll2Count = rolls.count(roll2)
        if (roll1Count == 3):
            if (roll1 == 6):
                print(DnDUtil.getPassText("666 Jackpot!!!"))
                payOut = 100
            else:
                print(DnDUtil.getPassText("3-Way Match!"))
                payOut = 2*3*roll1
        elif (roll1Count == 2 or roll2Count == 2):
            print("Single Match!")
            if (roll1Count == 2):
                payOut = 2*roll1
            else:
                payOut = 2*roll2
        else:
            print(DnDUtil.getFailText("No Match"))
            payOut = max(rolls)
        netPayOut = payOut - 7
        print("You win", payOut, "gold.", '('+str(netPayOut)+')')
        netResult += netPayOut
        answer = DnDUtil.getAnswer('Play again')
    print("Net Payout:", netResult)

def playTwentyOne():

    answer = DnDUtil.getAnswer('Play 21')
    while (answer == 'y'):
        roll1 = getTwentyOneFaceValue(random.randint(1,12))
        roll2 = getTwentyOneFaceValue(random.randint(1,12))
        rolls = [roll1, roll2]
        print("The dealer is showing a", roll1)
        input('Press Enter after player have finished hitting. ')
        print("The dealer reveals a", roll2)
        total = sum(rolls)
        while (total <= 16 and (not(1 in rolls) or 1 in rolls and (total+10 <= 17 or total+10 > 21))):
            print("The dealer hits at", total)
            roll = getTwentyOneFaceValue(random.randint(1,12))
            print("The dealer draws a", roll)
            rolls.append(roll)
            total += roll

        if (total > 21):
            print("The dealer", DnDUtil.getPassText('busts!'), rolls, "=", total)
        else:
            if (1 in rolls and total+10 <= 21):
                total += 10
            print("The dealer stays at", total, rolls)
        answer = DnDUtil.getAnswer('Play again')

def getTwentyOneFaceValue(roll):

    if (roll >= 10):
        return 10
    else:
        return roll

def playGyp():

    print("This is a simple dice-rolling game.")
    print("The player places a bet then rolls 2d6.")
    print("If the result is 7 or 12, the player wins.")
    print("Otherwise, the player loses unless he doubles the bet to roll another d6 to try and reach 7 or 12")
    print("The payout for winning is 2:1")

def playTableGame(maxBettingRounds,initFunc,perRoundFunc,getBestHandFunc):

    tableData = generateTableData()
    numActors = len(tableData['TurnOrder'])
    buyIn = tableData['BuyIn']
    while (True):

        rawInput = input('Press Enter to play (type help to see commands): ')
        tableCommand = rawInput.split()
        numArgs = len(tableCommand)
        if (numArgs == 0):
            pot = numActors * buyIn
            currentHandTurnOrder = copy(tableData['TurnOrder'])
            firstBetIndex = tableData['FirstBetIndex']
            # initialize NPC hands based on the game being played
            initFunc(tableData)
            bettingRound = 1
            while (len(currentHandTurnOrder) > 1 and bettingRound < maxBettingRounds+1):
                # reset bets for all actors in play
                for dataDictKey in ['NPCData', 'PlayerData']:
                    for actor in tableData[dataDictKey]:
                        tableData[dataDictKey][actor]['HasBet'] = False
                        tableData[dataDictKey][actor]['Bet'] = 0
                # do anything that should be done at the start of this round of betting based on the game being played
                perRoundFunc(bettingRound,tableData)

                turnIndex = firstBetIndex
                highestBet = 0
                doneBetting = False
                while (not(doneBetting)):
                    takenTurn = False
                    actor = currentHandTurnOrder[turnIndex]
                    playerTurn = actor in tableData['PlayerData']
                    if (playerTurn):
                        actorData = tableData['PlayerData'][actor]
                    else:
                        actorData = tableData['NPCData'][actor]
                    hasBet = actorData['HasBet']
                    currentBet = actorData['Bet']

                    if (hasBet and currentBet == highestBet or len(currentHandTurnOrder) == 1):
                        doneBetting = True
                    else:
                        promptString = actor
                        if (not(playerTurn)):
                            promptString += ' (hand: '+getHandString(actorData['Hand'])+')'
                        if (tableData['PublicHand']):
                            promptString += ' (public: '+getHandString(tableData['PublicHand'])+')'
                        promptString += ' ('+str(highestBet-currentBet)+' to call)'
                        promptString += ': '
                        while (not(takenTurn)):
                            rawInput = input(promptString)
                            command = rawInput.split()
                            numArgs = len(command)
                            if (numArgs >= 1):
                                initCommand = command[0]
                            else:
                                initCommand = ''

                            if ((initCommand == 'b' or initCommand == 'bet') and numArgs == 2):
                                bet = DnDUtil.getInt(command[1]) - currentBet
                                if (bet < highestBet):
                                    print("Bet must meet the highest bet ("+str(highestBet)+")!")
                                else:
                                    takenTurn = True
                                    actorData['Bet'] += bet
                                    pot += bet
                                    if (actorData['Bet'] > highestBet):
                                        highestBet = actorData['Bet']
                                
                            elif ((initCommand == '' or initCommand == 'c' or initCommand == 'call') and (numArgs == 0 or numArgs == 1)):
                                takenTurn = True
                                actorData['Bet'] = highestBet
                                pot += highestBet - currentBet

                            elif ((initCommand == 'r' or initCommand == 'raise') and numArgs == 2):
                                takenTurn = True
                                raiseAmount = DnDUtil.getInt(command[1])
                                actorData['Bet'] = highestBet + raiseAmount
                                highestBet = actorData['Bet']
                                pot += highestBet - currentBet

                            elif ((initCommand == 'f' or initCommand == 'fold') and numArgs == 1):
                                takenTurn = True
                                if (firstBetIndex > turnIndex):
                                    firstBetIndex -= 1
                                currentHandTurnOrder.remove(actor)
                                if (firstBetIndex == len(currentHandTurnOrder)):
                                    firstBetIndex = 0
                                turnIndex -= 1

                            elif ((initCommand == 'ins' or initCommand == 'insight') and numArgs == 2):
                                targetActor = command[1]

                                if (targetActor in tableData['PlayerData']):
                                    playerTarget = True
                                elif (targetActor in tableData['NPCData']):
                                    playerTarget = False
                                elif (targetActor.isdigit() and 'NPC'+targetActor in tableData['NPCData']):
                                    targetActor = 'NPC'+targetActor
                                    playerTarget = False
                                else:
                                    print("Actor", targetActor, "not found!")

                                if (targetActor in currentHandTurnOrder):
                                    if (playerTurn):
                                        insight = DnDUtil.getInt(input('Make an insight check: '))
                                    else:
                                        insight = random.randint(1,20)+actorData['Insight']
                                    if (playerTarget):
                                        deception = DnDUtil.getInt(input('Make a deception check: '))
                                    else:
                                        deception = random.randint(1,20)+tableData['NPCData'][targetActor]['Deception']
                                    print("Insight:", insight, "Deception:", deception)
                                    delta = insight-deception
                                    if (delta >= 20):
                                        resultString = DnDUtil.getPassText("a true")
                                    elif (delta >= 15):
                                        resultString = DnDUtil.getPassText("an excellent")
                                    elif (delta >= 10):
                                        resultString = DnDUtil.getPassText("a great")
                                    elif (delta >= 5):
                                        resultString = 'a decent'
                                    elif (delta >= 0):
                                        resultString = 'a minor'
                                    else:
                                        resultString = DnDUtil.getFailText('no')

                                    if (delta >= 0 and not(playerTarget)):
                                        print(actor, "gets", resultString, "read on", targetActor+"'s hand" , '('+getHandString(tableData['NPCData'][targetActor]['Hand'])+')')
                                    else:
                                       print(actor, "gets", resultString, "read on", targetActor+"'s hand")

                            elif (initCommand == 'pot' and numArgs == 1):
                                print("There is", pot, "gold in the pot.")

                            elif ((initCommand == 'd' or initCommand == 'display') and (numArgs == 1 or numArgs == 2)):
                                if (numArgs == 2):
                                    NPCName = command[1]
                                else:
                                    NPCName = actor

                                if (NPCName.isdigit()):
                                    NPCName = 'NPC'+NPCName

                                if (NPCName in tableData['NPCData']):
                                    displayNPCData(NPCName,tableData['NPCData'][NPCName])
                                else:
                                    print("No data for", NPCName, "found!")

                            elif (initCommand == 'table' and numArgs == 1):
                                displayTableData(tableData)

                            elif (initCommand == 'help' and (numArgs == 1 or numArgs == 2)):
                                if (numArgs == 1):
                                    print("Valid commands are as follows: bet, call, raise, fold, insight, pot, display, table, and help")
                                    print("Type help plus a command name to learn more about it.")
                                elif (command[1] == 'b' or command[1] == 'bet'):
                                    print("Place a bet with the given amount. Keep in mind the bet must meet or exceed the highest bet for that round.")
                                    print("Usage: b/bet [amount]")
                                elif (command[1] == 'c' or command[1] == 'call'):
                                    print("Match the current bet")
                                    print("Usage: c/call")
                                    print("Note: Inputting no command also calls")
                                elif (command[1] == 'r' or command[1] == 'raise'):
                                    print("Call the current highest bet and raise it by a given amount")
                                    print("Usage: r/raise [amount]")
                                elif (command[1] == 'f' or command[1] == 'fold'):
                                    print("Forfeit the hand")
                                    print("Usage: f/fold")
                                elif (command[1] == 'ins' or command[1] == 'insight'):
                                    print("Make an insight check against a particular actor")
                                    print("Usage: ins/insight [actor]")
                                    print("Note: NPC names may be given with a number")
                                elif (command[1] == 'pot'):
                                    print("Check how much gold is in the pot")
                                    print("Usage: pot")
                                elif (command[1] == 'd' or command[1] == 'display'):
                                    print("Displays data for the given NPC or the current NPC")
                                    print("Usage: d/display ([NPCName])")
                                    print("Note: The NPC's number may be given as well")
                                elif (command[1] == 'table'):
                                    print("Displays the data for the current table")
                                    print("Usage: table")
                                else:
                                    print("Command", command[1], "not found! Valid commands are bet, call, raise, fold, insight, pot, display, table, and help")
                            else:
                                print("Invalid Command: Valid commands are bet, call, raise, fold, insight, pot, display, table, and help")

                        actorData['HasBet'] = True
                    if (turnIndex == len(currentHandTurnOrder)-1):
                        turnIndex = 0
                    else:
                        turnIndex += 1
                bettingRound += 1

            # if more than one actor made it to the end, reveal hands and eliminate the losers
            if (len(currentHandTurnOrder) > 1):
                # this function must reveal all npc hand values, get player hand values, store hand values into tableData, and return the best hand value
                bestHand = getBestHandFunc(currentHandTurnOrder,tableData)
                i = 0
                while (i < len(currentHandTurnOrder)):
                    actor = currentHandTurnOrder[i]
                    if (actor in tableData['PlayerData']):
                        dataKey = 'PlayerData'
                    else:
                        dataKey = 'NPCData'
                    # this assumes the hand has already been formatted by getBestHandFunc to easily compare with bestHand
                    if (bestHand != tableData[dataKey][actor]['Hand']):
                        currentHandTurnOrder.remove(actor)
                    else:
                        i += 1
            else:
                bestHand = []
            
            # take casino's 10% cut and split the pot among all winning players
            print("----------------------------------------")
            if (bestHand):
                print("The winning hand value is", bestHand)
            pot = int(0.9*pot)
            print("Final pot is", pot)
            for actor in currentHandTurnOrder:
                if (actor in tableData['PlayerData']):
                    print(actor, "wins", DnDUtil.getPassText(DnDUtil.divide((pot), (len(currentHandTurnOrder)))), "gold!")
                else:
                    print(actor, "wins", DnDUtil.divide((pot), (len(currentHandTurnOrder))), "gold!")
            print("----------------------------------------")

            # increment first bet index for the next game so a new player starts the betting
            if (tableData['FirstBetIndex'] == numActors-1):
                tableData['FirstBetIndex'] = 0
            else:
                tableData['FirstBetIndex'] += 1

        elif (tableCommand[0] == 'leave' and numArgs == 1):
            return

        elif (tableCommand[0] == 'add' and numArgs == 2 and (tableCommand[1] == 'p' or tableCommand[1] == 'player' or tableCommand[1] == 'n' or tableCommand[1] == 'npc')):
            if (tableCommand[1][0] == 'p'):
                actorName = input('What is the player''\'s name? ')
                tableData['PlayerData'][actorName] = {'HasBet': False, 'Bet': 0}
            else:
                actorName = 'NPC'+str(len(tableData['NPCData'])+1)
                tableData['NPCData'][actorName] = getRandomNPCData()
                displayNPCData(actorName,tableData['NPCData'][actorName])
            
            tableData['TurnOrder'].append(actorName)
            numActors += 1
            print(actorName, "has joined the table!")

        elif (tableCommand[0] == 'remove' and (numArgs == 1 or numArgs == 2)):
            if (numArgs == 1):
                options = list(tableData['PlayerData'].keys()) + list(tableData['NPCData'].keys())
                choice = DnDUtil.chooseOption('Choose a player to remove',options)
                actorName = options[choice-1]
            else:
                actorName = tableCommand[1]

            if (actorName in tableData['PlayerData']):
                dataKey = 'PlayerData'
            elif (actorName in tableData['NPCData']):
                dataKey = 'NPCData'
            else:
                dataKey = ''

            if (dataKey):
                del tableData[dataKey][actorName]
                removeIndex = tableData['TurnOrder'].index(actorName)
                if (tableData['FirstBetIndex'] > removeIndex):
                    tableData['FirstBetIndex'] -= 1
                tableData['TurnOrder'].remove(actorName)
                if (tableData['FirstBetIndex'] == len(tableData['TurnOrder'])):
                    tableData['FirstBetIndex'] = 0
                numActors -= 1
                print(actorName, "has left the table!")
            else:
                print("No actor named", actorName, "is at the table!")
                print("The players at the table are:", list(tableData['PlayerData'].keys()) + list(tableData['NPCData'].keys()))

        elif (tableCommand[0] == 'help' and (numArgs == 1 or numArgs == 2)):
            if (numArgs == 1):
                print("The valid commands are: leave, add, remove, and help")
            elif (tableCommand[1] == 'leave'):
                print("leave - Exits the current game and returns to the main casino menu")
                print("Usage: leave")
            elif (tableCommand[1] == 'add'):
                print("add - Adds an npc or player to the table")
                print("Usage: add p/player/n/npc")
            elif (tableCommand[1] == 'remove'):
                print("remove - Removes an actor from the table")
                print("Usage: remove ([actor])")
                print("Note: If no name is given, you will be presented with a list of options")
            else:
                print("Command", tableCommand[1], "not found! Valid commands are leave, add, remove, and help")

        else:
            print("Invalid Command! Valid commands are leave, add, remove, and help")

def getBestHandSum(actors,tableData):

    bestHand = 0
    for actor in actors:
        if (actor in tableData['PlayerData']):
            hand = DnDUtil.getInt(input('What is '+actor+'\'s hand total? '))
            tableData['PlayerData'][actor]['Hand'] = hand
        else:
            hand = sum(tableData['NPCData'][actor]['Hand'])
            print(actor, "reveals a", hand, '('+getHandString(tableData['NPCData'][actor]['Hand'])+')')
            tableData['NPCData'][actor]['Hand'] = hand
        if (hand > bestHand):
            bestHand = hand

    return bestHand

def getBestHandPoker(actors,tableData):

    # this list represents the overall value of the hand so we can easily compare hands
    # the first number indicates the hand type (like 2 Pair)
    # the second number indicates the primary tie-breaker (like the number on a pair or the higher pair)
    # the third number indicates the secondary tie-breaker (like the number on a lower pair or the highest single number in a 3-of-a-kind)
    # the fourth number indicates the final tie-breaker (only used for the un-paired number on a 2 pair hand)
    bestHandValueList = [0, 0, 0, 0]
    publicHand = tableData['PublicHand']
    for actor in actors:
        if (actor in tableData['PlayerData']):
            dataKey = 'PlayerData'
            privateHand = input('What is '+actor+'\'s private hand? ').split(',')
            while (len(privateHand) != 2 or not(privateHand[0].isdigit()) or not(privateHand[1].isdigit())):
                print("Hand must be 2 digits separated by a comma!")
                privateHand = input('What is '+actor+'\'s private hand? ').split(',')
            privateHand[0] = int(privateHand[0])
            privateHand[1] = int(privateHand[1])
        else:
            dataKey = 'NPCData'
            privateHand = tableData['NPCData'][actor]['Hand']

        hand = privateHand + publicHand
        handCounts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for number in hand:
            handCounts[number-1] += 1
        
        handValueList = [0, 0, 0, 0]
        tableData[dataKey][actor]['Hand'] = handValueList
        if (all(count > 0 for count in handCounts[7:])):
            handType = 'Royal Straight!'
            handValueList[0] = 8
        elif (any(handCount >= 5 for handCount in handCounts)):
            handType = '5 of a Kind!'
            handValueList[0] = 7
        elif (4 in handCounts):
            handType = '4 of a Kind!'
            handValueList[0] = 6
            handValueList[1] = handCounts.index(4)+1
            if (2 in handCounts):
                handValueList[2] = max(handCounts.index(2),handCounts.index(1)) + 1
            else:
                handValueList[2] = getHighestNumberWithFrequency(handCounts,1)
        elif (isStraight(hand)):
            handType = 'Straight!'
            handValueList[0] = 5
            highStraightNumber = 0
            i = 11
            while (highStraightNumber == 0):
                if (handCounts[i] >= 1 and handCounts[i-1] >= 1 and handCounts[i-2] >= 1):
                    highStraightNumber = i+1
                i -= 1
            handValueList[1] = highStraightNumber
        elif (handCounts.count(3) == 2 or 3 in handCounts and 2 in handCounts):
            handType = 'Full House!'
            handValueList[0] = 4
            handValueList[1] = getHighestNumberWithFrequency(handCounts,3)
            if (handCounts.count(3) == 2):
                handValueList[2] = handCounts.index(3)+1
            else:
                handValueList[2] = getHighestNumberWithFrequency(handCounts,2)
        elif (3 in handCounts):
            handType = '3 of a Kind!'
            handValueList[0] = 3
            handValueList[1] = handCounts.index(3)+1
            handValueList[2] = getHighestNumberWithFrequency(handCounts,1)
        elif (handCounts.count(2) >= 2):
            handType = '2 Pair'
            handValueList[0] = 2
            handValueList[1] = getHighestNumberWithFrequency(handCounts,2)
            if (handCounts.count(2) == 3):
                midPairNumber = 0
                i = handValueList[1]-2
                while (midPairNumber == 0):
                    if (handCounts[i] == 2):
                        midPairNumber = i+1
                    i -= 1
                handValueList[2] = midPairNumber
                handValueList[3] = max(handCounts.index(2),handCounts.index(1)) + 1
            else:
                handValueList[2] = handCounts.index(2)+1
                handValueList[3] = getHighestNumberWithFrequency(handCounts,1)
        elif (2 in handCounts):
            handType = 'Single Pair'
            handValueList[0] = 1
            handValueList[1] = handCounts.index(2)+1
            handValueList[2] = getHighestNumberWithFrequency(handCounts,1)
        else:
            handType = 'None'
            handValueList[0] = 0
            handValueList[1] = getHighestNumberWithFrequency(handCounts,1)

        print(actor, "reveals a", handType, '('+getHandString(privateHand)+')', '('+getHandString(publicHand)+')')

        if (handValueList > bestHandValueList):
            bestHandValueList = handValueList

    return bestHandValueList

def getHighestNumberWithFrequency(handCounts,frequency):

    return max(i for i, val in enumerate(handCounts) if val == frequency) + 1

def isStraight(hand):

    # to check for a straight, eliminate the duplicates, then check for 5 number sequence 
    uniqueHand = list(set(hand))
    for i in range(0,len(uniqueHand)-4):
        baseNumber = uniqueHand[i]
        if (uniqueHand[i+1] == baseNumber+1 and uniqueHand[i+2] == baseNumber+2 and uniqueHand[i+3] == baseNumber+3 and uniqueHand[i+4] == baseNumber+4):
            return True
        
    return False

def playDragonsHoard():

    playTableGame(3,dragonsHoardInit,dragonsHoardPerRound,getBestHandSum)

def dragonsHoardInit(tableData):

    tableData['PublicHand'] = []
    # roll NPC's starting hands
    for NPC in tableData['NPCData']:
        tableData['NPCData'][NPC]['Hand'] = [random.randint(1,6), random.randint(1,6), random.randint(1,6), random.randint(1,6)]
    input('Press Enter after players have rolled their dice. (4d6) ')

def dragonsHoardPerRound(bettingRound,tableData):

    # if it's not the first round, roll the public die and remove it from all npc hands
    if (bettingRound > 1):
        publicDie = random.randint(1,6)
        tableData['PublicHand'].append(publicDie)
        print("--------------------------------------------")
        print("The dealer rolls a", publicDie, "for the public die!")
        print("--------------------------------------------")
        for NPC in tableData['NPCData']:
            hand = tableData['NPCData'][NPC]['Hand']
            tableData['NPCData'][NPC]['Hand'] = [value for value in hand if value != publicDie]

def playHandOfFate():

    playTableGame(3,clearHands,handOfFatePerRound,getBestHandSum)

def handOfFatePerRound(bettingRound,tableData):

    # if it's the first round, roll a d8
    if (bettingRound == 1):
        die = 8
    # if it's the second round, roll a d6
    elif (bettingRound == 2):
        die = 6
    # if it's the third round, roll a d4
    else:
        die = 4
    for NPC in tableData['NPCData']:
        tableData['NPCData'][NPC]['Hand'].append(random.randint(1,die))
    input('Press Enter after players have rolled their dice. (1d'+str(die)+') ')

def playFaeruneKeepEm():

    playTableGame(4,faeruneKeepEmInit,faeruneKeepEmPerRound,getBestHandPoker)

def faeruneKeepEmInit(tableData):

    tableData['PublicHand'] = []
    # roll NPC's starting hands
    for NPC in tableData['NPCData']:
        tableData['NPCData'][NPC]['Hand'] = [random.randint(1,12), random.randint(1,12)]
    input('Press Enter after players have rolled their dice. (2d12) ')

def faeruneKeepEmPerRound(bettingRound,tableData):

    if (bettingRound == 1):
        numPublicDice = 0
    elif (bettingRound == 2):
        numPublicDice = 3
    else:
        numPublicDice = 1

    if (numPublicDice > 0):
        print("--------------------------------------------")
    for i in range(0,numPublicDice):
        publicDie = random.randint(1,12)
        print("The dealer rolls a", publicDie, "for the public die!")
        tableData['PublicHand'].append(publicDie)
    if (numPublicDice > 0):
        print("--------------------------------------------")

def generateTableData():

    tableData = {}
    tableData['PublicHand'] = []
    tableData['BuyIn'] = DnDUtil.getInt(input('What is the buy-in? '))
    numNPCs = DnDUtil.getInt(input('How many NPCs are playing? '))
    tableData['NPCData'] = {}
    tableData['TurnOrder'] = []
    for i in range(0,numNPCs):
        NPCName = 'NPC'+str(i+1)
        tableData['NPCData'][NPCName] = getRandomNPCData()
        tableData['TurnOrder'].append(NPCName)
    displayTableData(tableData)

    numPlayers = DnDUtil.getInt(input('How many players are playing? '))
    tableData['PlayerData'] = {}
    for i in range(0,numPlayers):
        playerName = input('What is player'+str(i+1)+'\'s name? ')
        tableData['PlayerData'][playerName] = {'HasBet': False, 'Bet': 0}
        tableData['TurnOrder'].append(playerName)
    tableData['FirstBetIndex'] = random.randint(0,len(tableData['TurnOrder'])-1)

    return tableData

def getRandomNPCData():

    NPCData = {}
    genderRoll = random.randint(1,3)
    if (genderRoll == 3):
        NPCData['Gender'] = 'female'
    else:
        NPCData['Gender'] = 'male'
    raceRoll = random.randint(1,10)
    if (raceRoll <= 3):
        NPCData['Race'] = 'human'
    elif (raceRoll <= 5):
        NPCData['Race'] = 'dwarf'
    elif (raceRoll == 6):
        NPCData['Race'] = 'half-elf'
    elif (raceRoll == 7):
        NPCData['Race'] = 'half-orc'
    elif (raceRoll == 8):
        NPCData['Race'] = 'gnome'
    elif (raceRoll == 9):
        NPCData['Race'] = 'halfling'
    else:
        raceRoll2 = random.randint(1,4)
        if (raceRoll == 1):
            NPCData['Race'] = 'elf'
        elif (raceRoll == 2):
            NPCData['Race'] = 'dragonborn'
        elif (raceRoll == 3):
            NPCData['Race'] = 'tiefling'
        else:
            NPCData['Race'] = 'goliath'

    NPCData['Insight'] = random.randint(1,4) + random.randint(1,4)
    NPCData['Deception'] = random.randint(1,4) + random.randint(1,4)
    NPCData['HasBet'] = False
    NPCData['Bet'] = 0
    NPCData['Hand'] = []

    return NPCData

def clearHands(tableData):

    tableData['PublicHand'] = []
    for NPC in tableData['NPCData']:
        tableData['NPCData'][NPC]['Hand'] = []

def getHandString(hand):

    numDice = len(hand)

    if (numDice == 0):
        return "EMPTY"

    handString = ""
    for i in range(0,numDice-1):
        handString += str(hand[i])+'|'
    handString += str(hand[-1])
    return handString

def displayNPCData(name,data):

    print(name+':', data['Gender'], data['Race'])
    print("Insight:", data['Insight'], "Deception:", data['Deception'])
    print("Hand:", data['Hand'], "Bet:", data['Bet'])

def displayTableData(tableData):

    print("Buy-In:", tableData['BuyIn'])
    print("Public Hand:", tableData['PublicHand'])
    print("NPCS:", len(tableData['NPCData']))
    for i in range(1,len(tableData['NPCData'])+1):
        NPCData = tableData['NPCData']['NPC'+str(i)]
        print('NPC'+str(i)+':', NPCData['Gender'], NPCData['Race'])
        print("Insight:", NPCData['Insight'], "Deception:", NPCData['Deception'])

def help(gameName):

    if (gameName == 'roulette'):
        print("This game follows the rules and payouts of a traditional double-zero roulette")
        print("Any number of bets may be made before the roulette is spun, but their amounts must be declared in advance")
        print("You may bet for a single number or other options such as high/low/red/black/green/even/odd or which dozen the result belongs to (dozen1/dozen2/dozen3)")
        print("The payouts are as follows:")
        print("Single Number - 35:1")
        print("Green - 17:1")
        print("Dozen - 2:1")
        print("High/Low/Red/Black/Even/Odd - 1:1")
    elif (gameName == 'highlow'):
        print("This is a simple game in which the player places a bet in advance")
        print("The dealer then rolls a d20 and the player must guess whether the next roll will be higher or lower than the first roll")
        print("The player wins if he/she guesses correctly. The player loses if it is the same roll.")
        print("The payout for winning is 1:3")
    elif (gameName == 'slots'):
        print("This game simulates slots using dice. The player must pay 7 gold to play.")
        print("3d6 is rolled to simulate the slots, and payouts are given based on the result")
        print("If none match, the player wins gold equal to the highest number rolled")
        print("If two match, the player wins gold equal to the total of the matching dice")
        print("If all three match, the player wins gold equal to double the total of the dice")
        print("If 666 is rolled, the player wins 100 gold!")
    elif (gameName == '21'):
        print("This game is a dice simulation of blackjack")
        print("Each player places a bet before cards are dealt")
        print("The dealer rolls 2d12 and reveals one result.")
        print("The players then roll 2d12 and may roll any number of additional d12s")
        print("Going over 21 is a bust and is a loss for the player.")
        print("11s and 12s count as 10, and 1s may count as a 1 or 11.")
        print("Getting a 21 on the opening hand results in a 1.5:1 payout unless the dealer also gets 21")
        print("The player doubles the bet if the player does not bust and has a hand higher than the dealer's or the dealer busts.")
        print("If it is a tie, the bet is not lost")
    elif (gameName == 'gyp'):
        print("This is a simple dice-rolling game.")
        print("The player places a bet then rolls 2d6.")
        print("If the result is 7 or 12, the player wins.")
        print("Otherwise, the player loses unless he doubles the bet to roll another d6 to try and reach 7 or 12.")
        print("The payout for winning is 2:1")
    elif (gameName == 'dh'):
        print("This is a dice-rolling table game involving 3 rounds of betting.")
        print("Each player rolls 4d6 in secret followed by a round of betting.")
        print("After each round of betting (except the final round), a d6 is rolled and any dice rolled that match this number do not count toward the total.")
        print("Then all dice are revealed. The player (that hasn't folded) with the highest total wins!")
        print("Along the way, players can use deception to bluff and insight to read other players and even try to cheat with sleight of hand.")
        print("Note that the casino takes 10% of every pot")
    elif (gameName == 'hof'):
        print("This is a dice-rolling table game involving 3 rounds of betting")
        print("Initially, each player rolls a d8 in secret followed by a d6, then a d4")
        print("After each roll, there is a round of betting.")
        print("The player with the highest total wins!")
        print("Along the way, players can use deception to bluff and insight to read other players and even try to cheat with sleight of hand.")
        print("Note that the casino takes 10% of every pot")
    elif (gameName == 'fke'):
        print("This is a Texas Hold 'Em rip-off that uses dice instead of cards")
        print("The dice rolled are d12s")
        print("Flop = Flip, Turn = Twist, River = Stream")
        print("Best to worst hands are as follows (note that straight beats full house):")
        print("Royal Straight")
        print("Five-of-a-Kind")
        print("Four-of-a-Kind")
        print("Straight")
        print("Full House")
        print("Three-of-a-Kind")
        print("Two Pairs")
        print("One Pair")
    else:
        print("Game", gameName, "not found!")
        print("Valid games are: roulette, highlow, slots, 21, gyp, Dragon's Hoard (dh), Hand of Fate (hof), Faerune Keep 'Em (fke)")