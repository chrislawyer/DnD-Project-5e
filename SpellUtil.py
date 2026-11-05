import csv

import DnDUtil

ABILITY_FILE = 'Ability Data.csv'
SPELL_LIST_FILE = 'Spell List Data.csv'

def inputSpellLevel(spellName,baseLevel):

    while True:
        input = raw_input("Input spell level for "+spellName+" (skip to cast at base level of "+str(baseLevel)+"): ")
        if (len(input) == 0):
            return baseLevel
        else:
            spellLevel = DnDUtil.getInt(input)
            if (spellLevel < 1):
                print "Spells cannot be cast at a level lower than 1! Try again."
            elif (spellLevel > 9):
                print "Spells cannot be cast at a level higher than 9! Try again."
            elif (spellLevel < baseLevel):
                print "Spells cannot be cast at a level lower than their base level! Try again."
            else:
                return spellLevel

def autoCompleteAbility(name,abilityDict):

    if (name in abilityDict):
        return name

    matches = []

    for ability in abilityDict:
        if (ability.startswith(name)):
            matches.append(ability)

    if (len(matches) == 0):
        return ''
    elif (len(matches) == 1):
        return matches[0]
    else:
        choice = DnDUtil.chooseOption('Choose an ability',matches,True)
        if (choice == len(matches)+1):
            return ''
        else:
            return matches[choice-1]

def replaceSpellMod(actions,actorData):

    returnActions = []
    for action in actions:
        returnAction = []
        for actionParameter in action:
            spModIndex = actionParameter.find('spmod')
            if (spModIndex != -1):
                if (spModIndex + 5 == len(actionParameter)):
                    spModString = 'spmod'
                # if spmod was not found at the end of the action string and the next character is a digit, we will search for that corresponding spmod and replace it
                elif (actionParameter[spModIndex+5].isdigit()):
                    spModString = 'spmod'+actionParameter[spModIndex+5]
                if (spModString in actorData['Misc']):
                    spellMod = actorData['Misc'][spModString]
                else:
                    promptString = 'What is this actor\'s spellcasting ability modifier? '
                    if (spModString != 'spmod'):
                        promptString += '('+spModString+') '
                    spellMod = DnDUtil.getInt(raw_input(promptString))
                returnAction.append(actionParameter.replace(spModString,str(spellMod)))
            else:
                returnAction.append(actionParameter)
        returnActions.append(returnAction)

    return returnActions

def getCantripModifierForActor(actor,actorData):

    if ('splvl' in actorData['Misc']):
        spellLevel = actorData['Misc']['splvl']
    else:
        spellLevel = actorData['CR']

    if (spellLevel < 5):
        return 1
    elif (spellLevel < 11):
        return 2
    elif (spellLevel < 17):
        return 3
    else:
        return 4

def replaceLvl(actions,lvl):

    returnActions = []
    for action in actions:
        returnAction = []
        for actionParameter in action:
            replaced = False
            for searchString in ['lvl*','lvl/','lvl']:
                findIndex = actionParameter.find(searchString)
                if (findIndex != -1):
                    replaced = True
                    if (searchString == 'lvl'):
                        replacement = str(lvl)
                    elif (searchString == 'lvl*'):
                        searchString += actionParameter[findIndex+4]
                        replacement = str(lvl*int(actionParameter[findIndex+4]))
                    else:
                        searchString += actionParameter[findIndex+4]
                        replacement = str(lvl/int(actionParameter[findIndex+4]))
                    actionParameter = actionParameter.replace(searchString,replacement)
            if (replaced):
                actionParameter = DnDUtil.simplifyCalculation(actionParameter)
            returnAction.append(actionParameter)
        returnActions.append(returnAction)
            
    return returnActions

def spellInfo(spellName):
    
    abilityFile = open(ABILITY_FILE,'rb')
    csvAbilityReader = csv.reader(abilityFile)
    header = csvAbilityReader.next()
    
    for row in csvAbilityReader:
        if (row[0] == spellName):
            abilityFile.close()
            abilityData = {}
            for key in header:
                abilityData[key] = row[header.index(key)]
            try:
                print "Base Level:", abilityData['Base Level']
                print "Targets:", abilityData['Targets']
                print "Range:", abilityData['Range']
                print "Duration:", abilityData['Duration']
                if (abilityData['Attack']):
                    print "Attack:", abilityData['Attack']
                print "Concentration:", abilityData['Concentration?']
                print "Use Turn:", abilityData['Use Turn?']
                print "Static Damage:", abilityData['Static Damage?']
                if (abilityData['Save']):
                    print "Save:", abilityData['Save'], abilityData['Save Result']
                if (abilityData['Target Type Mods']):
                    print "Target Type Mods:", abilityData['Target Type Mods']
                if (abilityData['Type']):
                    print "Types:", abilityData['Type']
                print "Actions:", abilityData['Actions']
                if (abilityData['Scaled Actions']):
                    print "Scaled Actions:", abilityData['Scaled Actions']
                if (int(abilityData['Trigger Duration'])):
                    print "Trigger Duration:", abilityData['Trigger Duration']
                    print "Target On Cast:", abilityData['Target On Cast?']
                    print "When To Trigger:", abilityData['When To Trigger']
                classes = getClassesWithSpell(spellName,int(abilityData['Base Level']))
                if (classes):
                    print "Able To Cast:", classes
            except KeyError:
                DnDUtil.printError("Missing data in "+ABILITY_FILE+" for ability "+spellName)
            except ValueError:
                DnDUtil.printError("Expected int for Trigger Duration data for ability "+spellName+" in "+ABILITY_FILE)
            return

    abilityFile.close()
    classes = getClassesWithSpell(spellName,-999)
    if (classes):
        print "Able To Cast:", classes
    else:
        print "Spell", spellName, "not found."

def getClassesWithSpell(spellName,spellLevel):

    classesString = ''
    if (spellLevel >= 0 and spellLevel <= 9 or spellLevel == -999):
        spellListFile = open(SPELL_LIST_FILE,'rb')
        csvSpellListReader = csv.reader(spellListFile)
        csvSpellListReader.next()
        baseClasses = []
        for row in csvSpellListReader:
            if (not('(' in row[0])):
                baseClass = row[0]
            else:
                baseClass = row[0][:row[0].find('(')-1]
            # if we don't know the spell's level, search all of the columns for the spell as long as this is a base class 
            if (spellLevel == -999):
                if (baseClass == row[0]):
                    spells = []
                    for spellList in row[1:]:
                        spells.extend(DnDUtil.mySplit(spellList,','))
                # if this isn't a base class, stop searching since no subclass would know a spell that a base class doesn't
                else:
                    spellListFile.close()
                    return classesString
            else:
                spells = DnDUtil.mySplit(row[spellLevel+1],',')
            # only display this class if it is a base class or it is a subclass whose base class does not have this spell
            if (spellName in spells and not(baseClass in baseClasses)):
                classesString += row[0]+'/'
                if (baseClass == row[0]):
                    baseClasses.append(baseClass)
                # if we didn't know the spell level, set it now based on which column the spell was found in
                if (spellLevel == -999):
                    i = 1
                    while (spellLevel == -999):
                        if (spellName in DnDUtil.mySplit(row[i],',')):
                            spellLevel = i-1
                            print "Spell Level:", spellLevel
                        i += 1
        spellListFile.close()
        if (classesString):
            classesString = classesString[:-1]
        
    return classesString

def printSpellList(classList,spellLevel):

    if (spellLevel >= -1 and spellLevel <= 9):
        spellListFile = open(SPELL_LIST_FILE,'rb')
        csvSpellListReader = csv.reader(spellListFile)
        csvSpellListReader.next()
        if (len(classList) == 1):
            for row in csvSpellListReader:
                classString = row[0].replace(' ','')
                if (classString == classList[0]):
                    printSpellListForRow(row,spellLevel)
                    spellListFile.close()
                    return
            print "Class", classList[0], "not found!"
        elif (len(classList) == 2):
            matchingClasses = []
            for row in csvSpellListReader:
                fullClassString = row[0].replace(' ','')
                subclassIndex = fullClassString.find('(')
                if (subclassIndex != -1):
                    baseClass = fullClassString[:subclassIndex]
                    subClass = fullClassString[subclassIndex+1:-1]
                    if (baseClass == classList[0]):
                        if (subClass == classList[1]):
                            printSpellListForRow(row,spellLevel)
                            spellListFile.close()
                            return
                        elif (classList[1] in subClass):
                            matchingClasses.append(row)
            if (matchingClasses):
                choice = DnDUtil.chooseOption('Choose which spell list to display',[matchingClass[0] for matchingClass in matchingClasses],True)
                if (choice <= len(matchingClasses)):
                    printSpellListForRow(matchingClasses[choice-1],spellLevel)
            else:
                print "Class", classList[0], "with subclass", classList[1], "not found!"
        else:
            print "A class can't have more than 1 subclass!"
        spellListFile.close()
    else:
        print spellLevel, "is not a valid spell level!"

def printSpellListForRow(row,spellLevel):

    if (spellLevel == -1):
        i = 1
        while (i < 11):
            if (row[i]):
                print row[0].capitalize(), str(i-1)+':', row[i]
            i += 1
    else:
        print row[0].capitalize(), str(spellLevel)+':', row[spellLevel+1]