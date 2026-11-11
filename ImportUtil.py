import csv
from copy import copy

import DnDUtil

ABILITY_FILE = 'Ability Data.csv'
WEAPON_FILE = 'Weapon Data.csv'
ARMOR_FILE = 'Armor Data.csv'

def parseMoveData(moveData):

    moveDict = {'Ground': 0, 'Fly': 0, 'Climb': 0, 'Swim': 0, 'Burrow': 0}
    moveDataLength = len(moveData)
    if (moveDataLength == 0):
        DnDUtil.printError("No move speeds given for this creature")
    else:
        moveDict['Ground'] = int(moveData[0])
        if (moveDataLength > 1):
            moveDict['Fly'] = int(moveData[1])
        if (moveDataLength > 2):
            moveDict['Climb'] = int(moveData[2])
        if (moveDataLength > 3):
            moveDict['Swim'] = int(moveData[3])
        if (moveDataLength > 4):
            moveDict['Burrow'] = int(moveData[4])

    return moveDict

def formatAtkDamageData(data,name):

    for i in range(0,len(data['Atk'])):
        data['Atk'][i] = data['Atk'][i].split(';')
        for j in range(0,len(data['Atk'][i])):
            data['Atk'][i][j] = data['Atk'][i][j].split(',')
            for k in range(0,len(data['Atk'][i][j])):
                data['Atk'][i][j][k] = int(data['Atk'][i][j][k])

    for i in range(0,len(data['Damage'])):
        data['Damage'][i] = data['Damage'][i].split(';')
        for j in range(0,len(data['Damage'][i])):
            data['Damage'][i][j] = data['Damage'][i][j].split(',')

    numRangeAtkSets = len(data['Atk'])
    numRangeDamageSets = len(data['Damage'])
    
    if (numRangeAtkSets != numRangeDamageSets):
        DnDUtil.printError("Ranged data was given for either atk bonus or damage, but not the other for "+name)
        print("Atk Range Sets:", numRangeAtkSets, "Damage:", numRangeDamageSets)
        if (numRangeAtkSets > numRangeDamageSets):
            for i in range(0,numRangeAtkSets-numRangeDamageSets):
                data['Damage'].append([['0']])
        else:
            for i in range(0,numRangeDamageSets-numRangeAtkSets):
                data['Damage'].pop()

    for i in range(0,len(data['Atk'])):
        numAtkSets = len(data['Atk'][i])
        numDamageSets = len(data['Damage'][i])

        if (numAtkSets != numDamageSets):
            DnDUtil.printError("The number of damage sets for "+name+" does not match up with the number of attack sets")
            print("Attack Sets:", numAtkSets, "Damage Sets:", numDamageSets)
            if (numAtkSets > numDamageSets):
                for j in range(0,numAtkSets-numDamageSets):
                    data['Damage'][i].append(['0'])
            else:
                for j in range(0,numDamageSets-numAtkSets):
                    data['Damage'][i].pop()

    dmgBonusData = []
    for i in range(0,len(data['Atk'])):
        dmgBonusData.append([])
        for j in range(0,len(data['Atk'][i])):
            dmgBonusData[i].append([])
            numAtks = len(data['Atk'][i][j])
            numDamages = len(data['Damage'][i][j])
            if (numDamages == 1):
                parsedDamage = DnDUtil.parseDamageCalculation(data['Damage'][i][j][0])
                damage = parsedDamage[0]
                dmgBonus = parsedDamage[1]
                data['Damage'][i][j][0] = damage
                dmgBonusData[i][j].append(dmgBonus)
                difference = numAtks - 1
                for k in range(0,difference):
                    data['Damage'][i][j].append(damage)
                    dmgBonusData[i][j].append(dmgBonus)
            elif (numAtks != numDamages):
                DnDUtil.printError("Damage data does not match up with Atk data for "+name)
                print("Atk:", numAtks, "Damage:", numDamages)
                for k in range(0,numAtks):
                    if (k < numDamages):
                        parsedDamage = DnDUtil.parseDamageCalculation(data['Damage'][i][j][k])
                        data['Damage'][i][j][k] = parsedDamage[0]
                        dmgBonusData[i][j].append(parsedDamage[1])
                    else:
                        data['Damage'][i][j].append('0')
                        dmgBonusData[i][j].append(0)
                if (numDamages > numAtks):
                    for k in range(0,numDamages-numAtks):
                        data['Damage'][i][j].pop()
            else:
                for k in range(0,numDamages):
                    parsedDamage = DnDUtil.parseDamageCalculation(data['Damage'][i][j][k])
                    data['Damage'][i][j][k] = parsedDamage[0]
                    dmgBonusData[i][j].append(parsedDamage[1])

    data['DmgBonus'] = dmgBonusData

def formatOnHitAbilitiesData(onHitAbilitiesData):

    for i in range(0,len(onHitAbilitiesData)):
        onHitAbilitiesData[i] = onHitAbilitiesData[i].split('/')
        for j in range(0,len(onHitAbilitiesData[i])):
            onHitAbilitiesData[i][j] = onHitAbilitiesData[i][j].split('|')
            for k in range(0,len(onHitAbilitiesData[i][j])):
                if (onHitAbilitiesData[i][j][k]):
                    onHitAbilitiesData[i][j][k] = loadAbilityData('',onHitAbilitiesData[i][j][k].split(':'),False)

def parseUseAbilitiesData(useAbilitiesData):

    useDict = {}
    for i in range(0,len(useAbilitiesData)):
        ability = useAbilitiesData[i].split('-')
        if (len(ability) == 1):
            ability.append('')
        abilityData = loadAbilityData(ability[0],ability[1].split(':'),True)
        if (abilityData):
            useDict[ability[0]] = abilityData
    del useAbilitiesData[:]
    return useDict

def formatWeaponTypesData(weaponTypesData,atkData,name):

    numRangeAtkSets = len(atkData)
    numRangeWeaponTypeSets = len(weaponTypesData)

    if (not(weaponTypesData)):
        for i in range(0,numRangeAtkSets):
            weaponTypesData.append([])
            for j in range(0,len(atkData[i])):
                weaponTypesData[i].append([])
                for k in range(0,len(atkData[i][j])):
                    weaponTypesData[i][j].append([])
    else:
        for i in range(0,numRangeWeaponTypeSets):
            weaponTypesData[i] = weaponTypesData[i].split('|')
            for j in range(0,len(weaponTypesData[i])):
                weaponTypesData[i][j] = weaponTypesData[i][j].split(';')
                for k in range(0,len(weaponTypesData[i][j])):
                    weaponTypesData[i][j][k] = DnDUtil.mySplit(weaponTypesData[i][j][k],',')

        if (numRangeAtkSets != numRangeWeaponTypeSets):
            DnDUtil.printError("Ranged data was given for either atk bonus or weapon types, but not the other for "+name)
            print("Atk Range Sets:", numRangeAtkSets, "Weapon Type Range Sets:", numRangeWeaponTypeSets)
            if (numRangeAtkSets > numRangeWeaponTypeSets):
                for i in range(0,numRangeAtkSets-numRangeWeaponTypeSets):
                    weaponTypesData.append([[[]]])
            else:
                for i in range(0,numRangeWeaponTypeSets-numRangeAtkSets):
                    weaponTypesData.pop()

        for i in range(0,numRangeAtkSets):
            numAtkSets = len(atkData[i])
            numWeaponTypeAtkSets = len(weaponTypesData[i])

            if (numAtkSets != numWeaponTypeAtkSets):
                DnDUtil.printError("The number of weapon type attack sets for "+name+" does not match up with the number of attack sets")
                print("Attack Sets:", numAtkSets, "Weapon Type Attack Sets:", numWeaponTypeAtkSets)
                if (numAtkSets > numWeaponTypeAtkSets):
                    for j in range(0,numAtkSets-numWeaponTypeAtkSets):
                        weaponTypesData[i].append([[]])
                else:
                    for j in range(0,numWeaponTypeAtkSets-numAtkSets):
                        weaponTypesData[i].pop()

        for i in range(0,numRangeAtkSets):
            for j in range(0,len(atkData[i])):
                numAtks = len(atkData[i][j])
                numWeaponTypeSets = len(weaponTypesData[i][j])

                if (numAtks != numWeaponTypeSets):
                    if (numWeaponTypeSets != 1):
                        DnDUtil.printError("The number of weapon type sets for "+name+" does not match up with the number of attacks")
                        print("Attacks:", numAtks, "Weapon Type Sets:", numWeaponTypeSets)
                    if (numAtks < numWeaponTypeSets):
                        for k in range(0,numWeaponTypeSets-numAtks):
                            weaponTypesData[i][j].pop()
                    elif (numWeaponTypeSets == 1):
                        initWeaponTypes = weaponTypesData[i][j][0]
                        for k in range(0,numAtks-numWeaponTypeSets):
                            weaponTypesData[i][j].append(initWeaponTypes[:])
                    else:
                        for k in range(0,numAtks-numWeaponTypeSets):
                            weaponTypesData[i][j].append([])

        for i in range(0,len(weaponTypesData)):
            for j in range(0,len(weaponTypesData[i])):
                for k in range(0,len(weaponTypesData[i][j])):
                    if (weaponTypesData[i][j][k] and not('magic' in weaponTypesData[i][j][k]) and DnDUtil.haveCommonItem(['slashing','piercing','bludgeoning'],weaponTypesData[i][j][k])):
                        weaponTypesData[i][j][k].append('nonmagic')

def parseMiscData(miscData,name):

    miscDict = {}
    for i in range(0,len(miscData)):
        entry = miscData[i].split('-')
        if (len(entry) == 1):
            miscDict[entry[0]] = 0
        elif (len(entry) == 2):
            if (entry[1].isdigit()):
                miscDict[entry[0]] = int(entry[1])
            else:
                miscDict[entry[0]] = entry[1]
        else:
            DnDUtil.printError("Too many misc arugments for "+name)
    del miscData[:]

    return miscDict

def getInitAbilityData():

    initAbilityData = {'DC': 0, 'Attack Mod': 0}
    dataKeys = ['Base Level','Save','Save Result','Attack','Concentration?','Use Turn?','Static Damage?','Trigger Duration','Target Type Mods','Type','Actions','Scaled Actions','Duration']
    for dataKey in dataKeys:
        initAbilityData[dataKey] = None
    return initAbilityData

def loadAbilityData(name,data,useAbility):

    abilityFile = open(ABILITY_FILE, 'r', encoding='utf-8', newline='')
    csvAbilityReader = csv.reader(abilityFile)
    header = next(csvAbilityReader)

    dataLength = len(data)

    if (name):
        for row in csvAbilityReader:
            if (row[0] == name):
                abilityFile.close()
                return parseAbilityData(row,header,data)

    abilityFile.close()

    if (useAbility):
        abilityDict = {'Base Level': -2, 'Attack': '', 'Attack Mod': 0, 'Save': '', 'DC': 0, 'Save Result': 'negates', 'Concentration?': False, 'Use Turn?': True, 'Static Damage?': True, 'Trigger Duration': 0, 'Target Type Mods': {}, 'Type': [name], 'Scaled Actions': [['']], 'Duration': 0}
    else:
        abilityDict = {'Trigger Condition': '', 'Save': '', 'DC': 0, 'Save Result': 'negates', 'Concentration?': False, 'Charges': -1, 'Duration': 0}

    abilityDict['Actions'] = []
    actions = data[dataLength // 2].split(';')
    for action in actions:
        abilityDict['Actions'].append(action.split(','))
    if (dataLength == 3):
        abilityDict['Actions2'] = []
        actions = data[2].split(';')
        for action in actions:
            abilityDict['Actions2'].append(action.split(','))

    if (dataLength == 2 or dataLength == 3):
        prereqs = data[0].split(',')
        numPrereqs = len(prereqs)
        if (numPrereqs == 1):
            if (prereqs[0].isdigit()):
                if (useAbility):
                    DnDUtil.printError("Save DC was given for use ability "+name+", but this ability was not found in "+ABILITY_FILE)
                else:
                    DnDUtil.printError("Invalid prerequisite arguments "+data[0]+" in on-hit ability")
            elif (useAbility):
                abilityDict['Attack'] = prereqs[0]
            else:
                abilityDict['Trigger Condition'] = prereqs[0]
        elif (numPrereqs == 3):
            if (prereqs[1].isdigit()):
                abilityDict['Save'] = prereqs[0]
                abilityDict['DC'] = int(prereqs[1])
                abilityDict['Save Result'] = prereqs[2]
            else:
                if (useAbility):
                    if (prereqs[1] == 'atk' and prereqs[2].isdigit()):
                        abilityDict['Attack'] = prereqs[0]
                        abilityDict['Attack Mod'] = int(prereqs[2])
                    else:
                        DnDUtil.printError("Invalid prerequisite arguments "+data[0]+" in ability "+name)
                else:
                    DnDUtil.printError("Invalid prerequisite arguments "+data[0]+" in on-hit ability")
        elif (numPrereqs == 4):
            if (prereqs[2].isdigit()):
                if (useAbility):
                    abilityDict['Attack'] = prereqs[0]
                else:
                    abilityDict['Trigger Condition'] = prereqs[0]
                abilityDict['Save'] = prereqs[1]
                abilityDict['DC'] = int(prereqs[2])
                abilityDict['Save Result'] = prereqs[3]
            elif (useAbility):
                DnDUtil.printError("Invalid prerequisite arguments "+data[0]+" in ability "+name)
            else:
                DnDUtil.printError("Invalid prerequisite arguments "+data[0]+" in on-hit ability")
        elif (numPrereqs == 6):
            if (useAbility):
                if (prereqs[1] == 'atk' and prereqs[2].isdigit() and prereqs[4].isdigit()):
                    abilityDict['Attack'] = prereqs[0]
                    abilityDict['Attack Mod'] = int(prereqs[2])
                    abilityDict['Save'] = prereqs[3]
                    abilityDict['DC'] = int(prereqs[4])
                    abilityDict['Save Result'] = prereqs[5]
                else:
                    DnDUtil.printError("Invalid prerequisite arguments "+data[0]+" in ability "+name)
            else:
                DnDUtil.printError("Invalid prerequisite arguments "+data[0]+" in on-hit ability")
        elif (useAbility):
            DnDUtil.printError("Invalid number of prereqs for ability "+name)
        else:
            DnDUtil.printError("Invalid number of prereqs for on-hit ability")

    if (actions == ['']):
        if (useAbility):
            DnDUtil.printError("No actions found for use ability "+name)
        else:
            DnDUtil.printError("No actions found for on-hit ability")

    return abilityDict

def parseAbilityData(row,header,data):

    numDataColumns = len(header)
    dataLength = len(data)
    # attempt to get the name of the ability first so we can reference it in case an error occurs
    try:
        nameIndex = header.index('Name')
        abilityName = row.pop(nameIndex)
        header.remove('Name')
    except ValueError:
        DnDUtil.printError("No 'Name' column found in "+ABILITY_FILE)
        return {}
    except IndexError:
        DnDUtil.printError("Not enough data columns in "+ABILITY_FILE+"! Expected "+str(numDataColumns)+" columns, but only "+str(len(row))+" columns were given")
        return {}
    
    # remove all columns we won't be collecting data from
    for extraColumn in ['Targets','Range','Target On Cast?','When To Trigger']:
        header.remove(extraColumn)
    # initialize ability data with default values
    abilityData = getInitAbilityData()
    # for every other data key, load from the data given in the ability file
    i = 0
    while (header):
        try:
            dataKey = header.pop(0)
            # handle keys that copy the string
            if (dataKey in ['Save','Save Result','Attack']):
                abilityData[dataKey] = row[i]
            # handle keys that convert the string to int
            elif (dataKey in ['Base Level','Trigger Duration']):
                abilityData[dataKey] = int(row[i])
            # handle keys that convert yes/no to bool
            elif dataKey in ['Concentration?','Use Turn?','Static Damage?']:
                if (row[i] == 'yes'):
                    abilityData[dataKey] = True
                elif (row[i] == 'no'):
                    abilityData[dataKey] = False
                else:
                    DnDUtil.printWarning("Invalid data given for ability "+abilityName+" in column "+str(i+1)+"! Expected "+dataKey+"data! Defaulting to True")
                    abilityData[dataKey] = True
            # handle keys that parse the string by ,
            elif (dataKey == 'Type'):
                abilityData[dataKey] = DnDUtil.mySplit(row[i],',')
                abilityData[dataKey].append(abilityName)
            # handle the target type modifiers
            elif (dataKey == 'Target Type Mods'):
                targetTypeModsDict = {}
                targetTypeModData = DnDUtil.mySplit(row[i],';')
                for targetTypeMod in targetTypeModData:
                    entry = DnDUtil.mySplit(targetTypeMod,'-')
                    if (len(entry) == 0):
                        DnDUtil.printError("There is likely an extra ; in target type modifiers for ability "+abilityName)
                    elif (len(entry) == 1):
                        DnDUtil.printWarning("Target type modifier "+entry[0]+" given in ability "+abilityName+", but no types were given")
                    elif (len(entry) == 2):
                        if (entry[0] == 'imm'):
                            targetTypeModsDict['Immune'] = entry[1].split(',')
                        elif (entry[0] == 'req'):
                            targetTypeModsDict['Required'] = entry[1].split(',')
                        elif (entry[0] == 'adv'):
                            targetTypeModsDict['Advantage'] = entry[1].split(',')
                        elif (entry[0] == 'dis'):
                            targetTypeModsDict['Disadvantage'] = entry[1].split(',')
                        else:
                            DnDUtil.printError("Unrecognized target type modifier "+entry[0]+" in ability "+abilityName+"! Valid modifiers are imm, req, adv, and dis")
                    else:
                        DnDUtil.printError("Too many target type modifier arugments for mod "+entry[0]+" in ability "+abilityName)
                abilityData[dataKey] = targetTypeModsDict
            # handle duration
            elif (dataKey == 'Duration'):
                duration = row[i]
                if (duration == 'actorstart'):
                    abilityData[dataKey] = 1
                elif (duration == 'actorend'):
                    abilityData[dataKey] = 1.5
                elif (duration == 'targetstart' or duration == 'targetend'):
                    abilityData[dataKey] = duration
                else:
                    abilityData[dataKey] = int(duration)
            # handle the action data
            elif (dataKey == 'Actions'):
                abilityData['Actions'] = []
                actions = data[dataLength // 2].split(';')
                actions2 = []
                if (actions == ['']):
                    actionSet = row[i].split(':')
                    actions = actionSet[0].split(';')
                    if (len(actionSet) == 2):
                        actions2 = actionSet[1].split(';')
                for action in actions:
                    abilityData['Actions'].append(action.split(','))
                if (dataLength == 3):
                    actions2 = data[2].split(';')
                if (actions2):
                    abilityData['Actions2'] = []
                    for action in actions2:
                        abilityData['Actions2'].append(action.split(','))
            # handle the scaled action data
            elif (dataKey == 'Scaled Actions'):
                if (row[i]):
                    allScaledActions = row[i].split(':')
                    abilityData['Scaled Actions'] = []
                    scaledActions = allScaledActions[0].split(';')
                    for action in scaledActions:
                        abilityData['Scaled Actions'].append(action.split(','))

                    if (len(allScaledActions) > 1):
                        abilityData['Scaled Actions2'] = []
                        scaledActions2 = allScaledActions[1].split(';')
                        for action in scaledActions2:
                            abilityData['Scaled Actions2'].append(action.split(','))
                else:
                    del abilityData['Scaled Actions']
            else:
                DnDUtil.printError("Unknown column '"+dataKey+"' found in "+ABILITY_FILE)
                return {}
            i += 1
        except IndexError:
            DnDUtil.printError("Not enough data columns for ability "+abilityName+"! Expected "+str(numDataColumns)+" columns, but only "+str(len(row))+" columns were given")
            return {}
        except ValueError:
            DnDUtil.printError("Invalid data given for ability "+abilityName+" in column "+str(i+1)+"! Expected "+dataKey+" data")
            return {}

    # ensure that every data key was set
    missingDataKeys = []
    for dataKey in abilityData:
        if (abilityData[dataKey] is None):
            missingDataKeys.append(dataKey)
    
    if (missingDataKeys):
        DnDUtil.printError("Missing data for ability "+abilityName+"! The following data is missing from "+ABILITY_FILE+": "+str(missingDataKeys))
        return {}

    # if the base level is at least -1, assume it is magical
    if (abilityData['Base Level'] >= -1):
        abilityData['Type'].append('magic')
    # if we have given a non-negative base level for the ability, assume it is a spell
    if (abilityData['Base Level'] >= 0):
        abilityData['Type'].append('spell')
    
    # override attack/save/save result/DC based on data given for this specific ability
    if (dataLength == 2 or dataLength == 3):
        prereqs = data[0].split(',')
        numPrereqs = len(prereqs)
        if (numPrereqs == 1):
            if (prereqs[0].isdigit()):
                if (abilityData['Save']):
                    abilityData['DC'] = int(prereqs[0])
                else:
                    DnDUtil.printError("Save DC was given for ability "+abilityName+" but this ability does not require a save")
            else:
                abilityData['Attack'] = prereqs[0]
        elif (numPrereqs == 2):
            if (prereqs[1].isdigit()):
                if (prereqs[0] == 'dc'):
                    if (abilityData['Save']):
                        abilityData['DC'] = int(prereqs[1])
                    else:
                        DnDUtil.printError("Save DC was given for ability "+abilityName+" but this ability does not require a save")
                elif (prereqs[0] == 'atk'):
                    if (abilityData['Attack']):
                        abilityData['Attack Mod'] = int(prereqs[1])
                    else:
                        DnDUtil.printError("Attack mod was given for ability "+abilityName+" but this ability does not require an attack")
                else:
                    DnDUtil.printError("Invalid prerequisite arguments "+data[0]+" in ability "+abilityName)
            else:
                DnDUtil.printError("Invalid prerequisite arguments "+data[0]+" in ability "+abilityName)
        elif (numPrereqs == 3):
            if (prereqs[1].isdigit()):
                abilityData['Save'] = prereqs[0]
                abilityData['DC'] = int(prereqs[1])
                abilityData['Save Result'] = prereqs[2]
            elif (prereqs[1] == 'atk' and prereqs[2].isdigit()):
                abilityData['Attack'] = prereqs[0]
                abilityData['Attack Mod'] = int(prereqs[2])
            else:
                DnDUtil.printError("Invalid prerequisite arguments "+data[0]+" in ability "+abilityName)
        elif (numPrereqs == 4):
            if (prereqs[2].isdigit()):
                abilityData['Attack'] = prereqs[0]
                abilityData['Save'] = prereqs[1]
                abilityData['DC'] = int(prereqs[2])
                abilityData['Save Result'] = prereqs[3]
            elif (prereqs[0] == 'atk' and prereqs[1].isdigit() and prereqs[2] == 'dc' and prereqs[3].isdigit()):
                abilityData['Attack Mod'] = int(prereqs[1])
                abilityData['DC'] = int(prereqs[3])
            else:
                DnDUtil.printError("Invalid prerequisite arguments "+data[0]+" in ability "+abilityName)
        elif (numPrereqs == 6):
            if (prereqs[1] == 'atk' and prereqs[2].isdigit() and prereqs[4].isdigit()):
                abilityData['Attack'] = prereqs[0]
                abilityData['Attack Mod'] = int(prereqs[2])
                abilityData['Save'] = prereqs[3]
                abilityData['DC'] = int(prereqs[4])
                abilityData['Save Result'] = prereqs[5]
            else:
                DnDUtil.printError("Invalid prerequisite arguments "+data[0]+" in ability "+abilityName)
        else:
            DnDUtil.printError("Invalid number of prereqs for ability "+abilityName)
            abilityData['Attack'] = ''
            abilityData['Save'] = ''

    return abilityData

def getInitWeaponData():

    initWeaponData = {'CritC': 20, 'CritD': 2.0}
    dataKeys = ['Name','Class','Damage','Damage Type','Traits','Value','Min Level','Max Level']
    for dataKey in dataKeys:
        initWeaponData[dataKey] = None
    return initWeaponData

def loadWeaponData(level=0):

    weaponFile = open(WEAPON_FILE, 'r', encoding='utf-8', newline='')
    csvWeaponReader = csv.reader(weaponFile)
    header = next(csvWeaponReader)
    weaponData = {}
    for row in csvWeaponReader:
        parsedWeaponData = parseWeaponData(row,copy(header))
        if (parsedWeaponData and (level == 0 or level >= parsedWeaponData['Min Level'] and level <= parsedWeaponData['Max Level'])):
            weaponName = parsedWeaponData.pop('Name')
            weaponData[weaponName] = parsedWeaponData
    weaponFile.close()
    return weaponData

def parseWeaponData(row,header):

    numDataColumns = len(header)
    # attempt to get the name of the weapon first so we can reference it in case an error occurs
    try:
        nameIndex = header.index('Name')
        weaponName = row[nameIndex]
    except ValueError:
        DnDUtil.printError("No 'Name' column found in "+WEAPON_FILE)
        return {}
    except IndexError:
        DnDUtil.printError("Not enough data columns in "+WEAPON_FILE+"! Expected "+str(numDataColumns)+" columns, but only "+str(len(row))+" columns were given")
        return {}
        
    # initialize weapon data with default values
    weaponData = getInitWeaponData()
    # for every other data key, load from the data given in the weapon file
    i = 0
    while (header):
        try:
            dataKey = header.pop(0)
            # handle keys that copy the string
            if (dataKey in ['Name','Class','Damage','Damage Type','Traits']):
                weaponData[dataKey] = row[i]
            # handle keys that convert the string to int
            elif (dataKey in ['Min Level','Max Level']):
                weaponData[dataKey] = int(row[i])
            # handle keys that convert the string to float
            elif (dataKey == 'Value'):
                weaponData[dataKey] = float(row[i])
            else:
                DnDUtil.printError("Unknown column '"+dataKey+"' found in "+WEAPON_FILE)
                return {}
            i += 1
        except IndexError:
            DnDUtil.printError("Not enough data columns for weapon "+weaponName+"! Expected "+str(numDataColumns)+" columns, but only "+str(len(row))+" columns were given")
            return {}
        except ValueError:
            DnDUtil.printError("Invalid data given for weapon "+weaponName+" in column "+str(i+1)+"! Expected "+dataKey+" data")
            return {}

    # ensure that every data key was set
    missingDataKeys = []
    for dataKey in weaponData:
        if (weaponData[dataKey] is None):
            missingDataKeys.append(dataKey)
    
    if (missingDataKeys):
        DnDUtil.printError("Missing data for weapon "+weaponName+"! The following data is missing from "+WEAPON_FILE+": "+str(missingDataKeys))
        return {}

    return weaponData

def getInitArmorData():

    initArmorData = {}
    dataKeys = ['Name','Base AC','AC Mod','Class','Value','Str Req','Stealth','Min Level','Max Level']
    for dataKey in dataKeys:
        initArmorData[dataKey] = None
    return initArmorData

def loadArmorData(level=0):

    armorFile = open(ARMOR_FILE, 'r', encoding='utf-8', newline='')
    csvArmorReader = csv.reader(armorFile)
    header = next(csvArmorReader)
    armorData = {}
    for row in csvArmorReader:
        parsedArmorData = parseArmorData(row,copy(header))
        if (parsedArmorData and (level == 0 or level >= parsedArmorData['Min Level'] and level <= parsedArmorData['Max Level'])):
            armorName = parsedArmorData.pop('Name')
            armorData[armorName] = parsedArmorData
    armorFile.close()
    return armorData

def parseArmorData(row,header):

    numDataColumns = len(header)
    # attempt to get the name of the armor first so we can reference it in case an error occurs
    try:
        nameIndex = header.index('Name')
        armorName = row[nameIndex]
    except ValueError:
        DnDUtil.printError("No 'Name' column found in "+ARMOR_FILE)
        return {}
    except IndexError:
        DnDUtil.printError("Not enough data columns in "+ARMOR_FILE+"! Expected "+str(numDataColumns)+" columns, but only "+str(len(row))+" columns were given")
        return {}

    # initialize armor data with default values
    armorData = getInitArmorData()
    # for every other data key, load from the data given in the armor file
    i = 0
    while (header):
        try:
            dataKey = header.pop(0)
            # handle keys that copy the string
            if (dataKey in ['Name','AC Mod','Class','Stealth']):
                armorData[dataKey] = row[i]
            # handle keys that convert the string to int
            elif (dataKey in ['Base AC','Str Req','Min Level','Max Level']):
                armorData[dataKey] = int(row[i])
            # handle keys that convert the string to float
            elif (dataKey == 'Value'):
                armorData[dataKey] = float(row[i])
            else:
                DnDUtil.printError("Unknown column '"+dataKey+"' found in "+ARMOR_FILE)
                return {}
            i += 1
        except IndexError:
            DnDUtil.printError("Not enough data columns for armor "+armorName+"! Expected "+str(numDataColumns)+" columns, but only "+str(len(row))+" columns were given")
            return {}
        except ValueError:
            DnDUtil.printError("Invalid data given for armor "+armorName+" in column "+str(i+1)+"!' Expected "+dataKey+" data")
            return {}

    # ensure that every data key was set
    missingDataKeys = []
    for dataKey in armorData:
        if (armorData[dataKey] is None):
            missingDataKeys.append(dataKey)
    
    if (missingDataKeys):
        DnDUtil.printError("Missing data for armor "+armorName+"! The following data is missing from "+ARMOR_FILE+": "+str(missingDataKeys))
        return {}

    return armorData