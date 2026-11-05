import sys
import random
try:
    import colorama
    colorama.init(convert=True,autoreset=True)
except ImportError:
    pass

def getInt(input):

    while (True):
        try:
            return int(input)
        except ValueError:
            print "Illegal input", '\''+input+'\'', "- input must be an integer!"
            input = raw_input("Try Again: ")

def mySplit(string,parseChar):

    if (string == ''):
        return []
    else:
        return string.split(parseChar)

def maxCalculate(command,printOutput=True):

    operands = command.split('+')

    total = 0
    for item in operands:
        if (item.find('d') == -1):
            constantValue = getInt(item)
            total += constantValue
        else:
            arguments = item.split('d')
            total += getInt(arguments[0])*getInt(arguments[1])

    if (printOutput):
        print 'MAX('+command+') =', total

    return total

def calculate(command,printOutput=True):

    operands = command.split('+')

    total = 0
    output = ['('+command+'): ']

    for item in operands:
        if (item.find('d') == -1):
            constantValue = getInt(item)
            output[0] += str(constantValue) + ' '
            total += constantValue
        else:
            arguments = item.split('d')
            total += diceRolls(getInt(arguments[0]),getInt(arguments[1]),output)
            
    if (printOutput):
        print output[0] + '=', total

    return total

def diceRolls(numDice,diceValue,output):

    total = 0
    output[0] += '['

    for i in range(0,numDice):
        result = random.randint(1,diceValue)
        output[0] += str(result)
        if (i < numDice - 1):
            output[0] += '+'
        total += result

    output[0] += '] '

    return total

def getAnswer(question):

    answer = raw_input(question+" (y/n)? ")
    while (answer != 'y' and answer != 'n'):
        answer = raw_input(question+" (y/n)? ")

    return answer

def chooseOption(choosePrompt,options,allowNone=False):

    numOptions = len(options)
    if (numOptions == 0):
        return 0
    elif (numOptions == 1 and not(allowNone)):
        return 1

    print "--------------------------"
    for i in range(0,numOptions):
        print "Option", str(i+1)+':', options[i]
    if (allowNone):
        numOptions += 1
        print "Option", str(numOptions)+':', "None"
        
    print "--------------------------"
    choice = 0
    while (choice < 1 or choice > numOptions):
        choice = raw_input(choosePrompt+': ')
        # giving no input while "None" is an option will automatically select the "None" option
        if (allowNone and choice == ''):
            choice = numOptions
        else:
            choice = getInt(choice)

    return choice

def simplifyCalculation(calculation):

    parsedCalculation = mySplit(calculation,'+')
    if (len(parsedCalculation) <= 1):
        return calculation

    orderedTerms = []
    for term in parsedCalculation:
        findIndex = term.find('d')
        if (findIndex == -1):
            numerator = int(term)
            denominator = 0
        else:
            numerator = int(term[:findIndex])
            denominator = int(term[findIndex+1:])
        if (orderedTerms):
            i = 0
            curDenominator = sys.maxint
            while (i < len(orderedTerms) and denominator < curDenominator):
                curDenominator = orderedTerms[i][1]
                i += 1
            if (curDenominator == denominator):
                orderedTerms[i-1][0] += numerator
            else:
                orderedTerms.insert(i,[numerator,denominator])
        else:
            orderedTerms.append([numerator,denominator])

    returnCalculation = ''
    for term in orderedTerms:
        if (term[0] > 0):
            if (term[1] > 0):
                returnCalculation += str(term[0])+'d'+str(term[1])+'+'
            else:
                returnCalculation += str(term[0])+'+'

    if (returnCalculation == ''):
        return '0'
    return returnCalculation[:-1]

def haveCommonItem(list1,list2):

    for item in list1:
        if (item in list2):
            return True
    return False

def parseDamageCalculation(damageCalculation):

    splitIndex = damageCalculation.rfind('+')
    # check if the last argument is an integer and if so, get the bonus, otherwise, assume all arguments are dice rolls
    if (splitIndex != -1 and damageCalculation[splitIndex+1:].isdigit() or damageCalculation[splitIndex+1] == '-' and damageCalculation[splitIndex+2:].isdigit()):
        dmgBonus = int(damageCalculation[splitIndex+1:])
        return [damageCalculation[:splitIndex], dmgBonus]

    return [damageCalculation, 0]

def printError(errorString):

    try:
        print colorama.Fore.LIGHTRED_EX + "Error: " + errorString + '!'
    except NameError:
        print "Error:", errorString+'!'

def printWarning(warningString):

    try:
        print colorama.Fore.LIGHTYELLOW_EX + "Warning: " + warningString + '!'
    except NameError:
        print "Warning:", warningString+'!'

def getHealText(healAmount):

    try:
        return colorama.Fore.LIGHTGREEN_EX + str(healAmount)
    except NameError:
        return str(healAmount)

def getStatusText(status):

    try:
        return colorama.Fore.LIGHTMAGENTA_EX + status
    except NameError:
        return status

def getPassText(passString):

    try:
        return colorama.Fore.LIGHTGREEN_EX + str(passString)
    except NameError:
        return passString

def getFailText(failString):

    try:
        return colorama.Fore.LIGHTRED_EX + str(failString)
    except NameError:
        return failString

def getDamageText(damage):

    try:
        return colorama.Fore.LIGHTYELLOW_EX + str(damage) + colorama.Style.RESET_ALL
    except NameError:
        return damage

def getDeathText(deathString):

    try:
        return colorama.Fore.LIGHTRED_EX + deathString
    except NameError:
        return deathString