import random
import DnDUtil

def hasStatus(data,statusTypes):

    for statusEffect in data['Status']:
        if (statusEffect[0] in statusTypes):
            return True

    return False

def applyBlessBane(actor,actorData,curResult,targetResult):

    targetDiff = curResult - targetResult
    hasBless = hasStatus(actorData,['bless'])
    hasBane = hasStatus(actorData,['bane'])
    if (hasBless and hasBane):
        print("The effects of bless and bane on", actor, "cancel out!")
        return curResult
    if (hasBless and targetDiff >= -4 and targetDiff < 0):
        if (targetDiff == -1):
            roll = 1
            print(actor, "takes a +1 from bless bonus to succeed!")
        elif ('HP' in actorData):
            roll = random.randint(1,4)
            print(actor, "rolls a", roll, "for bless bonus")
        else:
            roll = DnDUtil.getInt(input('Roll for bless bonus (1d4): '))
        return curResult + roll
    if (hasBane and targetDiff < 4 and targetDiff >= 0):
        if (targetDiff == 0):
            roll = 1
            print(actor, "takes a -1 from bane penalty to fail!")
        elif ('HP' in actorData):
            roll = random.randint(1,4)
            print(actor, "rolls a", roll, "for bane penalty")
        else:
            roll = DnDUtil.getInt(input('Roll for bane penalty (1d4): '))
        return curResult - roll
    return curResult

def makeCheck(actor,actorData,playerActor,checkType,checkAdvantage=False,checkDisadvantage=False):

    checkTypes = checkType.split('/')
    checkAdvantage = checkAdvantage or 'checks' in actorData['Advantages']
    checkDisadvantage = checkDisadvantage or 'checks' in actorData['Disadvantages'] or hasStatus(actorData,['poison']) or hasStatus(actorData,['fear']) and DnDUtil.getAnswer('Is '+actor+'\'s source of fear in line of sight') == 'y'
    statList = ['str','dex','con','int','wis','cha']
    hasNextStatAdv = any('next'+stat in actorData['Advantages'] for stat in statList)
    hasStatAdv = any(stat in actorData['Advantages'] for stat in statList)
    hasNextStatDis = any('next'+stat in actorData['Disadvantages'] for stat in statList)
    hasStatDis = any(stat in actorData['Disadvantages'] for stat in statList)
    checkArgs = []
    for checkType in checkTypes:
        nextAdvantages = []
        nextDisadvantages = []
        checkArgs.append([checkType,nextAdvantages,nextDisadvantages])

        # ensure that all advantages and disadvantages that affect the next check are consumed
        for nextAdvantage in ['nextcheck','next'+checkType]:
            if (nextAdvantage in actorData['Advantages']):
                nextAdvantages.append(nextAdvantage)
        for nextDisadvantage in ['nextcheck','next'+checkType]:
            if (nextDisadvantage in actorData['Disadvantages']):
                nextDisadvantages.append(nextDisadvantage)

        advantage = checkAdvantage or len(nextAdvantages) > 0 or checkType in actorData['Advantages']
        disadvantage = checkDisadvantage or len(nextDisadvantages) > 0 or checkType in actorData['Disadvantages']

        # try to determine which stat is used for this check based on its name
        if (checkType in statList):
            checkStat = checkType
        elif (checkType == 'athletics'):
            checkStat = 'str'
        elif (checkType in ['acrobatics','sleight of hand','stealth']):
            checkStat = 'dex'
        elif (checkType in ['arcana','history','investigation','nature','religion']):
            checkStat = 'int'
        elif (checkType in ['animal handling','insight','medicine','perception','survival']):
            checkStat = 'wis'
        elif (checkType in ['deception','intimidation','performance','persuasion']):
            checkStat = 'cha'
        else:
            checkStat = ''
        # if this actor has advantage or disadvantage on the next check involving a specific stat OR
        # advantage or disadvantage on ANY check involving a specific stat AND doesn't already have advantage or disadvantage, we will need to determine which stat this check is using
        if (hasNextStatAdv or hasNextStatDis or not(advantage) and hasStatAdv or not(disadvantage) and hasStatDis):
            # if we still don't know which stat to use, such as with spellcasting ability checks, ask the user
            if (checkStat == ''):
                choice = DnDUtil.chooseOption('Choose which stat is being used for the '+checkType+' check',statList)
                checkStat = statList[choice-1]
            # ensure that all advantages and disadvantages that affect the next check using this stat are consumed
            if ('next'+checkStat in actorData['Advantages']):
                nextAdvantages.append('next'+checkStat)
            if ('next'+checkStat in actorData['Disadvantages']):
                nextDisadvantages.append('next'+checkStat)

            advantage = advantage or len(nextAdvantages) > 0 or checkStat in actorData['Advantages']
            disadvantage = disadvantage or len(nextDisadvantages) > 0 or checkStat in actorData['Disadvantages']

        checkArgs[-1].append(advantage)
        checkArgs[-1].append(disadvantage)

        if (playerActor):
            checkBonus = -100
        else:
            if (checkStat):
                bonusString = ' (+'+str(actorData[checkStat.capitalize()+'Save'])+' '+checkStat+' save)'
            else:
                bonusString = ''
            checkBonus = DnDUtil.getInt(input('What is '+actor+'\'s '+checkType+' bonus'+bonusString+'? '))
        checkArgs[-1].append(checkBonus)

    # for players, decide if it matters which check is chosen, and if it does, ask the user which check is being made
    if (playerActor):
        if (len(checkArgs) > 1):
            # it only matters which check we choose if any of the checks would grant adv/dis and the others don't
            equal = True
            for i in range(0,len(checkArgs)-1):
                checkData = checkArgs[i]
                for itCheckData in checkArgs[i+1:]:
                    if (checkData[1:] != itCheckData[1:]):
                        equal = False
                        break
                if (not(equal)):
                    break
            if (equal):
                checkData = checkArgs[0]
                for checkArg in checkArgs[1:]:
                    checkData[0] += ' OR ' + checkArg[0]
            else:
                options = []
                for checkData in checkArgs:
                    checkStr = checkData[0]
                    if (checkData[3] and not(checkData[4])):
                        checkStr += ' (advantage)'
                    elif (checkData[4] and not(checkData[3])):
                        checkStr += ' (disadvantage)'
                    if (checkData[1] or checkData[2]):
                        checkStr += ' (this check only)'
                    options.append(checkStr)
                choice = DnDUtil.chooseOption('Choose which check to make',options)
                checkData = checkArgs[choice-1]
        else:
            checkData = checkArgs[0]
    # for creatures, make the check that will give the highest result
    else:
        maxCheckValueIndex = 0
        maxCheckValue = -100
        for i in range(0,len(checkArgs)):
            checkData = checkArgs[i]
            value = checkData[5]
            if (checkData[3]):
                value += 3.5
            if (checkData[4]):
                value -= 3.5
            if (value > maxCheckValue):
                maxCheckValue = value
                maxCheckIndex = i
        checkData = checkArgs[maxCheckIndex]

    for nextAdv in checkData[1]:
        actorData['Advantages'].remove(nextAdv)
    for nextDis in checkData[2]:
        actorData['Disadvantages'].remove(nextDis)

    if (checkData[0][0] in ['a','e','i','o','u']):
        checkArticle = 'an'
    else:
        checkArticle = 'a'
    result = makeRoll(actor,playerActor,checkData[3],checkData[4],checkData[5],True,'Make '+checkArticle+' '+checkData[0]+' check')
    return result

def makeRoll(actor,playerActor,advantage,disadvantage,rollBonus=-100,returnTotal=True,rollPrompt=''):

    # 0: standard roll, 1: roll with advantage, -1: roll with disadvantage
    rollType = 0
    advantageDisadvantageText = ''

    if (advantage and not(disadvantage)):
        rollType = 1
        advantageDisadvantageText += ' (with advantage)'
    elif (disadvantage and not(advantage)):
        rollType = -1
        advantageDisadvantageText += ' (with disadvantage)'

    if (playerActor):
        roll = DnDUtil.getInt(input(rollPrompt+advantageDisadvantageText+': '))
        if (rollBonus == -100 or not(returnTotal)):
            return roll
        else:
            return roll+rollBonus
    else:
        roll1 = random.randint(1,20)
        roll = roll1
        if (rollType != 0):
            roll2 = random.randint(1,20)
            if (rollType == 1):
                roll = max(roll1,roll2)
            else:
                roll = min(roll1,roll2)
            advantageDisadvantageText += ' (' + str(roll1) + ',' + str(roll2) + ')'

        if (rollBonus == -100):
            rollTotal = roll
            rollTotalText = ''
        else:
            rollTotal = roll+rollBonus
            rollTotalText = '('+str(rollTotal)+')'

        print(actor, "rolls a", roll, rollTotalText+advantageDisadvantageText)
        if (returnTotal):
            return rollTotal
        else:
            return roll

def isImmuneToType(data,types):

    return 'all' in data['Immunities'] or hasStatus(data,['petrification']) and DnDUtil.haveCommonItem(types,['poison','disease']) or DnDUtil.haveCommonItem(data['Immunities'],types)

def isVulnerableToType(data,types):

    return 'all' in data['Vulnerabilities'] or DnDUtil.haveCommonItem(data['Vulnerabilities'],types)

def hasResistFromType(data,types):
    
    return 'all' in data['Resistances'] or hasStatus(data,['petrification']) or DnDUtil.haveCommonItem(data['Resistances'],types)

def canAct(data):

    return not(hasStatus(data,['paralysis','petrification','stun','sleep','unconscious','incapacitate']))

def canReact(data):

    return data['Reaction'] and data['CanReact'] and canAct(data)