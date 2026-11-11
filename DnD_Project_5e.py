import sys
import math
import random
import csv
import json
import webbrowser
from copy import copy
from copy import deepcopy
from collections import OrderedDict

import DnDUtil
import ImportUtil
import ActorUtil
import SpellUtil
import Spells
import Player
import PDFUtil
import CasinoGames
from functools import reduce

PLAYER_FILE = 'Player Data 12.csv'
CREATURE_FILE = 'Creature Data.csv'
LAIR_FILE = 'Lair Data.csv'
CLASS_FILE = 'Class Data.csv'
LOOT_FILE = 'Loot Data.csv'
ENCOUNTER_FILE = 'Encounter.json'
TEST_ENCOUNTER_FILE = 'Test Encounter.json'
BLACKSMITH_OUTPUT_FILE = 'Blacksmith.txt'
MAGIC_SHOP_OUTPUT_FILE = 'Magic Shop.txt'
# When enabled, remember to input 100 as the roll if the attack crits
PLAYERS_ADD_BONUS = True

def test():

    '''
    creatureFile = open(CREATURE_FILE, 'r', encoding='utf-8', newline='')
    csvCreatureReader = csv.reader(creatureFile)
    next(csvCreatureReader)

    errorCreatures = []
    for row in csvCreatureReader:
        creatureData = getCreatureData(row[0])
        if (not(creatureData)):
            DnDUtil.printError("There was a problem loading data from creature "+row[0])
            errorCreatures.append(row[0])
        else:
            for rangeSet in creatureData['WeaponTypes']:
                for atkSet in rangeSet:
                    for atk in atkSet:
                        if (atk and not(DnDUtil.haveCommonItem(atk,['bludgeoning','piercing','slashing'])) and not('spell' in atk)):
                            print creatureData['Base']+':', atk[0]
                            if (DnDUtil.getAnswer('Open') == 'y'):
                                PDFUtil.openBookmark(creatureData['Base']+',creature')
    '''

    classes = ['druid','sorcerer']
    maxSpellLevel = 1
    spellDictList = []
    uniqueSpellListDictList = []
    for i in range(0,maxSpellLevel+1):
        spellDictList.append({})
        uniqueSpellListDictList.append({})
    spellListFile = open('Spell List Data.csv', 'r', encoding='utf-8', newline='')
    csvSpellListReader = csv.reader(spellListFile)
    next(csvSpellListReader)
    for row in csvSpellListReader:
        currentClass = row[0]
        if (not(classes)):
            break
        if (currentClass in classes):
            for i in range(1,maxSpellLevel+2):
                spells = DnDUtil.mySplit(row[i],',')
                for spell in spells:
                    if (spell in spellDictList[i-1]):
                        spellDictList[i-1][spell] += '/'+currentClass
                    else:
                        spellDictList[i-1][spell] = currentClass
            classes.remove(currentClass)

    for i in range(0,maxSpellLevel+1):
        spellDict = spellDictList[i]
        for spell in spellDict:
            if (not('/' in spellDict[spell])):
                if (spellDict[spell] in uniqueSpellListDictList[i]):
                    uniqueSpellListDictList[i][spellDict[spell]].append(spell)
                else:
                    uniqueSpellListDictList[i][spellDict[spell]] = [spell]

    for spellLevel in range(0,maxSpellLevel+1):
        uniqueSpellList = uniqueSpellListDictList[spellLevel]
        for currentClass in uniqueSpellList:
            print(currentClass.capitalize(), str(spellLevel)+':', uniqueSpellList[currentClass])
    

    '''
    environmentFile = open('Environment Data.csv', 'r', encoding='utf-8', newline='')
    csvEnvironmentReader = csv.reader(environmentFile)

    environmentDict = {}
    for row in csvEnvironmentReader:
        environment = row[0]
        for creatures in row[1:]:
            creatureList = DnDUtil.mySplit(creatures,',')
            for creature in creatureList:
                if (creature in environmentDict):
                    environmentDict[creature] += ','+environment
                else:
                    environmentDict[creature] = environment

    environmentFile.close()

    creatureFile = open(CREATURE_FILE, 'r', encoding='utf-8', newline='')
    csvCreatureReader = csv.reader(creatureFile)
    next(csvCreatureReader)

    for row in csvCreatureReader:
        if (row[0] == 'tinyservant'):
            break

    environmentFile = open('Final Environment Data.csv', 'w', encoding='utf-8', newline='')
    csvEnvironmentWriter = csv.writer(environmentFile)
    for row in csvCreatureReader:
        creature = row[0]
        if (creature in environmentDict):
            environments = environmentDict.pop(creature])
        else:
            print "No environments found for", creature
            environments = ''
        csvEnvironmentWriter.writerow([creature,environments])
      
    creatureFile.close()

    for creature in environmentDict:
        print "Creature not found:", creature, "| Environments:", environmentDict[creature]
    '''

def testEncounter():

    createEncounter(TEST_ENCOUNTER_FILE)

def testCreatures():

    testEncounter = {}
    creatureFile = open(CREATURE_FILE, 'r', encoding='utf-8', newline='')
    csvCreatureReader = csv.reader(creatureFile)
    next(csvCreatureReader)

    errorCreatures = []
    for row in csvCreatureReader:
        creatureData = getCreatureData(row[0])
        if (not(creatureData)):
            DnDUtil.printError("There was a problem loading data from creature "+row[0])
            errorCreatures.append(row[0])
        testEncounter[row[0]] = creatureData
      
    creatureFile.close()

    if (errorCreatures):
        print("There was a problem loading data from", len(errorCreatures), "creature(s):")
        for creature in errorCreatures:
            print(creature)
    else:
        print("There were no problems loading data from all the creatures!")
    #for creature in testEncounter:
    #    usePassiveAbilities(creature,testEncounter[creature],False)

# handles all code that should be run just before the main loop of the program
def onProgramStart():

    loadPlayerData()
    loadEquipmentData()

# load the data for every weapon and armor that could drop at the current level
def loadEquipmentData():

    global weaponData
    weaponData = ImportUtil.loadWeaponData(avgLevel)
    global armorData
    armorData = ImportUtil.loadArmorData(avgLevel)

def getInitActorData():

    initActorData = {'ExtraOnHitAbilities': {}, 'Concentration': [], 'Effects': [], 'Status': [], 'Reaction': True, 'CanReact': True, 'Prone': False, 'LastAction': '', 'InitRoll': 0}
    dataKeys = ['Base','Size','Type','Move','AC','Immunities','Vulnerabilities','Resistances','Atk','Damage','OnHitAbilities','WeaponTypes','SpellAtk','SpellDC','UseAbilities','StrSave','DexSave','ConSave','IntSave','WisSave','ChaSave','Advantages','Disadvantages','Init','Misc']
    for dataKey in dataKeys:
        initActorData[dataKey] = None
    return initActorData

def getInitPlayerData():

    initPlayerData = getInitActorData()
    playerDataKeys = ['Level']
    for dataKey in playerDataKeys:
        initPlayerData[dataKey] = None
    # initialize stats we do not need to load from the player data file if the players are adding their bonuses
    if (PLAYERS_ADD_BONUS):
        for dataKey in ['SpellAtk','StrSave','DexSave','ConSave','IntSave','WisSave','ChaSave','Init']:
            initPlayerData[dataKey] = 0
    return initPlayerData

def getInitCreatureData():

    initCreatureData = getInitActorData()
    initCreatureData['TempHP'] = 0
    creatureDataKeys = ['HP','Environments','AbilitiesInfo','CR']
    for dataKey in creatureDataKeys:
        initCreatureData[dataKey] = None
    return initCreatureData

def getInitLairData():

    initLairData = {'Init': -9999, 'InitRoll': 20, 'Concentration': [], 'Effects': [], 'Status': [], 'Misc': {}}
    lairDataKeys = ['CRMod','AbilitiesInfo','UseAbilities','RegionalEffects']
    for lairDataKey in lairDataKeys:
        initLairData[lairDataKey] = None
    return initLairData

def loadPlayerData():

    global avgLevel
    global numPlayers
    global partyExpThresholds
    numPlayers = 0
    partyExpThresholds = [0,0,0,0]
    totalLevels = 0.0
    playerFile = open(PLAYER_FILE, 'r', encoding='utf-8', newline='')
    csvPlayerReader = csv.reader(playerFile)
    header = next(csvPlayerReader)

    for row in csvPlayerReader:
        parsedPlayerData = parsePlayerData(row,copy(header))
        if (parsedPlayerData):
            playerData[parsedPlayerData['Base']] = parsedPlayerData
            level = parsedPlayerData.pop('Level')
            parsedPlayerData['CR'] = level
            if (not('pet' in playerData[row[0]]['Misc'])):
                playerExpThresholds = getExpThresholdsForPlayer(level)
                for i in range(0,len(partyExpThresholds)):
                    partyExpThresholds[i] += playerExpThresholds[i]
                totalLevels += level
                numPlayers += 1

    if (numPlayers):
        avgLevel = int(totalLevels / numPlayers)
    playerFile.close()

def parsePlayerData(row,header):

    numDataColumns = len(header)
    # remove all spaces from the header
    for i in range(0,numDataColumns):
        header[i] = header[i].replace(' ','')
    # attempt to get the name of the player first so we can reference it in case an error occurs
    try:
        nameIndex = header.index('Name')
        name = row[nameIndex]
        header.insert(nameIndex,'Base')
        header.remove('Name')
    except ValueError:
        DnDUtil.printError("No 'Name' column found in "+PLAYER_FILE)
        return {}
    except IndexError:
        DnDUtil.printError("Not enough data columns in "+PLAYER_FILE+"! Expected "+str(numDataColumns)+" columns, but only "+str(len(row))+" columns were given")
        return {}
    # remove notes from the header since we don't want to load this data
    if ('Notes' in header):
        header.remove('Notes')
    # initialize player data with default values
    retPlayerData = getInitPlayerData()
    # for every other data key, load from the data given in the player file
    i = 0
    while (header):
        try:
            dataKey = header.pop(0)
            # handle keys that copy the string
            if (dataKey in ['Base','Size']):
                retPlayerData[dataKey] = row[i]
            # handle keys that convert the string to int
            elif (dataKey in ['Level','AC','StrSave','DexSave','ConSave','IntSave','WisSave','ChaSave','Init','SpellAtk','SpellDC']):
                retPlayerData[dataKey] = int(row[i])
            # handle keys that parse the string by ,
            elif (dataKey in ['Type','Move','Immunities','Vulnerabilities','Resistances','Advantages','Disadvantages']):
                retPlayerData[dataKey] = DnDUtil.mySplit(row[i],',')
            # handle keys that parse the string by ;
            elif (dataKey == 'Misc'):
                retPlayerData[dataKey] = DnDUtil.mySplit(row[i],';')
            # handle keys that parse the string by |
            elif (dataKey in ['Atk','Damage','UseAbilities']):
                retPlayerData[dataKey] = DnDUtil.mySplit(row[i],'|')
            # handle keys that parse the string by /
            elif (dataKey == 'WeaponTypes'):
                retPlayerData[dataKey] = DnDUtil.mySplit(row[i],'/')
            # handle keys that parse the string by _
            elif (dataKey == 'OnHitAbilities'):
                retPlayerData[dataKey] = DnDUtil.mySplit(row[i],'_')
            else:
                DnDUtil.printError("Unknown column '"+dataKey+"' found in "+PLAYER_FILE)
                return {}
            i += 1
        except IndexError:
            DnDUtil.printError("Not enough data columns for player "+name+"! Expected "+str(numDataColumns)+" columns, but only "+str(len(row))+" columns were given")
            return {}
        except ValueError:
            DnDUtil.printError("Invalid data given for player "+name+" in column "+str(i+1)+". Expected "+dataKey+" data")
            return {}

    # ensure that every data key was set
    missingDataKeys = []
    for dataKey in retPlayerData:
        if (retPlayerData[dataKey] is None):
            missingDataKeys.append(dataKey)
    
    if (missingDataKeys):
        DnDUtil.printError("Missing data for player "+name)
        print("The following data is missing from the player data file:")
        for dataKey in missingDataKeys:
            print(dataKey)
        return {}

    # store a size mod so we can quickly compare sizes using integers
    retPlayerData['SizeMod'] = getSizeMod(retPlayerData['Size'])
    # seperate the move data into ground, fly, climb, swim, and burrow speeds
    retPlayerData['Move'] = ImportUtil.parseMoveData(retPlayerData['Move'])
    # further split atk and damage values by attack set and individual attacks and ensure that the data lines up
    # also split damage between the dice and the constant modifier for faster crit calculations
    ImportUtil.formatAtkDamageData(retPlayerData,name)
    # parse the on hit abilities and ensure they line up with the number of attacks we have
    ImportUtil.formatOnHitAbilitiesData(retPlayerData['OnHitAbilities'])
    # parse and load data for the use abilities
    retPlayerData['UseAbilities'] = ImportUtil.parseUseAbilitiesData(retPlayerData['UseAbilities'])
    # parse the weapon types and ensure they line up with the number of attacks we have
    ImportUtil.formatWeaponTypesData(retPlayerData['WeaponTypes'],retPlayerData['Atk'],name)
    # parse the misc data
    retPlayerData['Misc'] = ImportUtil.parseMiscData(retPlayerData['Misc'],name)
    # set a baseline number of legendary actions if no amount was given
    if ('lactions' in retPlayerData['Misc']):
        if (retPlayerData['Misc']['lactions'] == 0):
            DnDUtil.printWarning("Legendary actions given for player "+name+" but no number was set! Defaulting to 3")
            retPlayerData['Misc']['lactions'] = 3
        retPlayerData['Misc']['maxlactions'] = retPlayerData['Misc']['lactions']
    # check to see if this player has a lair, and if so, ask to load the lair's data if one does not already exist
    if ('lair' in retPlayerData['Misc'] and not('lair' in encounter) and not('lair' in playerData)):
        if (autoBattle or DnDUtil.getAnswer('Is this encounter occurring in '+name+'\'s lair') == 'y'):
            if (retPlayerData['Misc']['lair'] == 0):
                lairName = name
            else:
                lairName = retPlayerData['Misc']['lair']
            lairData = getLairData(lairName,retPlayerData)
            if (lairData):
                playerData['lair'] = lairData
                # if this lair was added mid-encounter, we will need to call insertNewActor to place it into the turn order
                if (turnOrder):
                    insertNewActor('lair',lairData)

    return retPlayerData

def addPartyMember(name):

    creatureFile = open(CREATURE_FILE, 'r', encoding='utf-8', newline='')
    csvCreatureReader = csv.reader(creatureFile)
    header = next(csvCreatureReader)

    for row in csvCreatureReader:
        if (row[0] == name):
            creatureFile.close()
            # store all data for this creature as a dict, using the header as the key for each column
            rawCreatureData = {}
            for i in range(0,len(header)):
                rawCreatureData[header[i]] = row[i]
            # input level in case it is different from CR
            rawCreatureData['CR'] = DnDUtil.getInt(input('What is '+name+'\'s level (CR +'+str(rawCreatureData['CR'])+')? '))
            print(name+"'s", "HP is", DnDUtil.calculate(rawCreatureData['HP'],False), '('+rawCreatureData['HP']+')')
            # if this is not a humanoid, ask if it should be treated as a pet to avoid soaking exp and altering the party's average level
            if (not('humanoid' in rawCreatureData['Type']) and DnDUtil.getAnswer('Treat '+name+' as a pet') == 'y'):
                if (rawCreatureData['Misc']):
                    rawCreatureData['Misc'] += ';'
                rawCreatureData['Misc'] += 'pet'
            # get the header from the player data file
            playerFile = open(PLAYER_FILE, 'r', encoding='utf-8', newline='')
            csvPlayerReader = csv.reader(playerFile)
            header = next(csvPlayerReader)
            playerFile.close()
            # create the row that will be printed in the player file using the header and comparing with our data keys
            playerDataList = []
            for key in header:
                try:
                    if (key == 'Level'):
                        playerDataList.append(rawCreatureData['CR'])
                    else:
                        playerDataList.append(rawCreatureData[key])
                except KeyError:
                    DnDUtil.printError('Key "'+key+'" not present in creature data')
                    playerDataList = []
                    break
            if (playerDataList):
                playerFile = open(PLAYER_FILE, 'a', encoding='utf-8', newline='')
                csvPlayerWriter = csv.writer(playerFile)
                csvPlayerWriter.writerow(playerDataList)
                playerFile.close()
                loadPlayerData()
                print(name, "is now a party member!")
            return
    print("Could not find creature", name+'!')
    creatureFile.close()

def printEquipmentInfo(item):

    if (item in weaponData):
        itemData = weaponData[item]
        print(item+':', itemData['Class'], "weapon", '('+itemData['Damage'], itemData['Damage Type'], "damage)", "worth", itemData['Value'], "gp")
        if (itemData['Traits']):
            print("Traits:", itemData['Traits'])
    elif (item in armorData):
        itemData = armorData[item]
        print(item+':', itemData['Class'], "armor worth", itemData['Value'], "gp")
        print("AC:", str(itemData['Base AC'])+itemData['AC Mod'])
        if (itemData['Str Req'] > 0):
            print("Strength Requirement:", itemData['Str Req'])
        if (itemData['Stealth']):
            print("Stealth:", itemData['Stealth'])
    else:
        print("Item not found.")

def getEquipmentInfo(item,baseItem):

    if (baseItem in weaponData):
        itemData = weaponData[baseItem]
        parsedItem = DnDUtil.mySplit(item,' ')
        atkBonus = 0
        dmgBonus = 0
        critC = itemData['CritC']
        critD = itemData['CritD']
        value = itemData['Value']
        if (len(parsedItem) >= 2):
            for prefix in parsedItem[:2]:
                if (prefix != baseItem):
                    if (prefix[0] == '+' and len(prefix) > 1 and prefix[1:].isdigit()):
                        magicBonus = int(prefix[1:])
                        atkBonus += magicBonus
                        dmgBonus += magicBonus
                        value += getItemValue('magicbonus',magicBonus)
                    elif (prefix == 'Keen'):
                        critC -= 1
                        value += getItemValue('enhanced',0)
                    elif (prefix == 'Deadly'):
                        critD += 1
                        value += getItemValue('enhanced',0)
                    elif (prefix == 'Strong'):
                        dmgBonus += 1
                        value += getItemValue('enhanced',0)
                    elif (prefix == 'Accurate'):
                        atkBonus += 1
                        value += getItemValue('enhanced',0)
        if ('of' in parsedItem):
            enchantStartIndex = parsedItem.index('of') + 1
            if (enchantStartIndex < len(parsedItem)):
                enchantStart = parsedItem[enchantStartIndex]
                if (enchantStart == 'Greater'):
                    value += getItemValue('enchant',2)
                elif (enchantStart == 'Superior'):
                    value += getItemValue('enchant',3)
                elif (enchantStart == 'Supreme'):
                    value += getItemValue('enchant',4)
                else:
                    value += getItemValue('enchant',1)
        if (atkBonus > 0):
            atkString = '+'+str(atkBonus)+' to hit|'
        else:
            atkString = ''
        if (dmgBonus > 0):
            dmgString = '+'+str(dmgBonus)
        else:
            dmgString = ''
        if (critC < 20 or critD != 2):
            critString = '|Crit: '
            if (critC < 20):
                critString += str(critC)
            if (critD != 2):
                critString += 'x'+str(critD)
        else:
            critString = ''
        if (itemData['Traits']):
            traitsString = '|'+itemData['Traits']
        else:
            traitsString = ''

        resultString = baseItem+' ('+atkString+itemData['Damage']+dmgString+' '+itemData['Damage Type']+critString+traitsString+')'
        
    elif (baseItem in armorData):
        itemData = armorData[baseItem]
        parsedItem = DnDUtil.mySplit(item,' ')
        prefix = parsedItem[0]
        armorBonus = 0
        value = itemData['Value']
        if (prefix[0] == '+' and len(prefix) > 1 and prefix[1:].isdigit()):
            magicBonus = int(prefix[1:])
            armorBonus += magicBonus
            value += getItemValue('magicbonus',armorBonus+1)
        if ('of' in parsedItem):
            enchantStartIndex = parsedItem.index('of') + 1
            if (enchantStartIndex < len(parsedItem)):
                enchantStart = parsedItem[enchantStartIndex]
                # make enchantments 50% more expensive than their magic bonus counterparts
                if (enchantStart == 'Greater'):
                    value += getItemValue('enchant',2)
                elif (enchantStart == 'Superior'):
                    value += getItemValue('enchant',3)
                elif (enchantStart == 'Supreme'):
                    value += getItemValue('enchant',4)
                else:
                    value += getItemValue('enchant',1)
        if (itemData['Str Req']):
            strReqString = '|Str Req: '+str(itemData['Str Req'])
        else:
            strReqString = ''
        if (itemData['Stealth']):
            stealthString = '|Stealth: '+itemData['Stealth']
        else:
            stealthString = ''

        resultString = baseItem+' ('+itemData['Class'].capitalize()+'|'+str(itemData['Base AC']+armorBonus)+itemData['AC Mod']+' AC'+strReqString+stealthString+')'

    else:
        DnDUtil.printError("Could not find item "+baseItem+" in weapon data or armor data")
        return [item,0]

    resultString = item.replace(baseItem,resultString)
    if (value >= 1):
        value = int(math.ceil(value))
    return [resultString,value]

def getItemValue(itemClass,itemTier):

    if (itemClass == 'potion'):
        if (itemTier == 0):
            return 0
        elif (itemTier == 1):
            return 5
        elif (itemTier == 2):
            return 10
        elif (itemTier == 3):
            return 15
        elif (itemTier == 4):
            return 25
        elif (itemTier == 5):
            return 40
        elif (itemTier == 6):
            return 60
        elif (itemTier == 7):
            return 80
        elif (itemTier == 8):
            return 100
        elif (itemTier == 9):
            return 125
        elif (itemTier == 10):
            return 150
    elif (itemClass == 'scroll'):
        if (itemTier == 0):
            return 5
        elif (itemTier == 1):
            return 10
        elif (itemTier == 2):
            return 20
        elif (itemTier == 3):
            return 40
        elif (itemTier == 4):
            return 75
        elif (itemTier == 5):
            return 100
        elif (itemTier == 6):
            return 150
        elif (itemTier == 7):
            return 300
        elif (itemTier == 8):
            return 600
        elif (itemTier == 9):
            return 1000
    elif (itemClass == 'maxpotion'):
        return 300
    elif (itemClass == 'enhanced'):
        return 250
    elif (itemClass == 'armormod'):
        return 500
    elif (itemClass == 'magicbonus'):
        if (itemTier == 0):
            return 0
        elif (itemTier == 1):
            return 200
        elif (itemTier == 2):
            return 1000
        elif (itemTier == 3):
            return 10000
        elif (itemTier == 4):
            return 50000
    elif (itemClass == 'skill'):
        return 400
    elif (itemClass == 'enchant'):
        # make enchantments 50% more expensive than their magic bonus counterparts
        if (itemTier == 1):
            return 300
        elif (itemTier == 2):
            return 1500
        elif (itemTier == 3):
            return 15000
        elif (itemTier == 4):
            return 75000
    elif (itemClass == 'tome'):
        # skill tome
        if (itemTier == 1):
            return 2500
        # stat tome
        elif (itemTier == 2):
            return 10000
        # feat tome
        elif (itemTier == 3):
            return 50000
    elif (itemClass == 'hitbox'):
        return 100 + 10*avgLevel

    DnDUtil.printError("Could not find value for tier "+str(itemTier)+' '+itemClass)
    return 0

def getPlayerData(name):

    playerFile = open(PLAYER_FILE, 'r', encoding='utf-8', newline='')
    csvPlayerReader = csv.reader(playerFile)
    header = next(csvPlayerReader)

    for row in csvPlayerReader:
        if (row[0] == name):
            playerFile.close()
            parsedPlayerData = parsePlayerData(row,header)
            parsedPlayerData['CR'] = parsedPlayerData.pop('Level')
            return parsedPlayerData
    playerFile.close()
    return {}

def getCreatureData(name,addExp=True):

    creatureFile = open(CREATURE_FILE, 'r', encoding='utf-8', newline='')
    csvCreatureReader = csv.reader(creatureFile)
    header = next(csvCreatureReader)

    for row in csvCreatureReader:
        if (row[0] == name):
            creatureFile.close()
            return parseCreatureData(row,header,addExp)
    creatureFile.close()
    return {}

def parseCreatureData(row,header,addExp=True):

    global totalExp
    global totalGold
    numDataColumns = len(header)
    # remove all spaces from the header
    for i in range(0,numDataColumns):
        header[i] = header[i].replace(' ','')
    # attempt to get the name of the creature first so we can reference it in case an error occurs
    try:
        nameIndex = header.index('Name')
        name = row[nameIndex]
        header.insert(nameIndex,'Base')
        header.remove('Name')
    except ValueError:
        DnDUtil.printError("No 'Name' column found in "+CREATURE_FILE)
        return {}
    except IndexError:
        DnDUtil.printError("Not enough data columns in "+CREATURE_FILE+"! Expected "+str(numDataColumns)+" columns, but only "+str(len(row))+" columns were given")
        return {}
    # remove notes from the header since we don't want to load this data
    if ('Notes' in header):
        header.remove('Notes')
    # initialize creature data with default values
    retCreatureData = getInitCreatureData()
    # for every other data key, load from the data given in the creature file
    i = 0
    while (header):
        try:
            dataKey = header.pop(0)
            # handle keys that copy the string
            if (dataKey in ['Base','Size','AbilitiesInfo']):
                retCreatureData[dataKey] = row[i]
            # handle keys that convert the string to int
            elif (dataKey in ['AC','StrSave','DexSave','ConSave','IntSave','WisSave','ChaSave','Init','SpellAtk','SpellDC']):
                retCreatureData[dataKey] = int(row[i])
            # handle keys that convert the string to float
            elif (dataKey == 'CR'):
                retCreatureData[dataKey] = float(row[i])
            # handle keys that calculate a value by on the string
            elif (dataKey == 'HP'):
                retCreatureData[dataKey] = DnDUtil.calculate(row[i],False)
            # handle keys that parse the string by ,
            elif (dataKey in ['Type','Environments','Move','Immunities','Vulnerabilities','Resistances','Advantages','Disadvantages']):
                retCreatureData[dataKey] = DnDUtil.mySplit(row[i],',')
            # handle keys that parse the string by ;
            elif (dataKey == 'Misc'):
                retCreatureData[dataKey] = DnDUtil.mySplit(row[i],';')
            # handle keys that parse the string by |
            elif (dataKey in ['Atk','Damage','UseAbilities']):
                retCreatureData[dataKey] = DnDUtil.mySplit(row[i],'|')
            # handle keys that parse the string by /
            elif (dataKey == 'WeaponTypes'):
                retCreatureData[dataKey] = DnDUtil.mySplit(row[i],'/')
            # handle keys that parse the string by _
            elif (dataKey == 'OnHitAbilities'):
                retCreatureData[dataKey] = DnDUtil.mySplit(row[i],'_')
            else:
                DnDUtil.printError("Unknown column '"+dataKey+"' found in "+CREATURE_FILE)
                return {}
            i += 1
        except IndexError:
            DnDUtil.printError("Not enough data columns for creature "+name+"! Expected "+str(numDataColumns)+" columns, but only "+str(len(row))+" columns were given")
            return {}
        except ValueError:
            DnDUtil.printError("Invalid data given for creature "+name+" in column "+str(i+1)+". Expected "+dataKey+" data")
            return {}

    # ensure that every data key was set
    missingDataKeys = []
    for dataKey in retCreatureData:
        if (retCreatureData[dataKey] is None):
            missingDataKeys.append(dataKey)
    
    if (missingDataKeys):
        DnDUtil.printError("Missing data for creature "+name)
        print("The following data is missing from the creature data file:")
        for dataKey in missingDataKeys:
            print(dataKey)
        return {}

    # ensure the creature has at least 1 hp
    if (retCreatureData['HP'] <= 0):
        retCreatureData['HP'] = 1
    # set max hp
    retCreatureData['MaxHP'] = retCreatureData['HP']
    # randomize the race if it is a base humanoid
    if (retCreatureData['Type'] == ['humanoid']):
        randomHumanoid = randomItem(['race'])
        retCreatureData['Type'].append(randomHumanoid)
        # change size to small if we randomized to a small humanoid
        if (randomHumanoid in ['gnome','halfling']):
            retCreatureData['Size'] = 'small'
        else:
            retCreatureData['Size'] = 'medium'
    # store a size mod so we can quickly compare sizes using integers
    retCreatureData['SizeMod'] = getSizeMod(retCreatureData['Size'])
    # seperate the move data into ground, fly, climb, swim, and burrow speeds
    retCreatureData['Move'] = ImportUtil.parseMoveData(retCreatureData['Move'])
    # further split atk and damage values by attack set and individual attacks and ensure that the data lines up
    # also split damage between the dice and the constant modifier for faster crit calculations
    ImportUtil.formatAtkDamageData(retCreatureData,name)
    # parse the on hit abilities and ensure they line up with the number of attacks we have
    ImportUtil.formatOnHitAbilitiesData(retCreatureData['OnHitAbilities'])
    # parse and load data for the use abilities
    retCreatureData['UseAbilities'] = ImportUtil.parseUseAbilitiesData(retCreatureData['UseAbilities'])
    # parse the weapon types and ensure they line up with the number of attacks we have
    ImportUtil.formatWeaponTypesData(retCreatureData['WeaponTypes'],retCreatureData['Atk'],name)
    # parse the misc data
    retCreatureData['Misc'] = ImportUtil.parseMiscData(retCreatureData['Misc'],name)
    # set a baseline number of legendary actions if no amount was given
    if ('lactions' in retCreatureData['Misc']):
        if (retCreatureData['Misc']['lactions'] == 0):
            DnDUtil.printWarning("Legendary actions given for creature "+retCreatureData['Base']+" but no number was set! Defaulting to 3")
            retCreatureData['Misc']['lactions'] = 3
        retCreatureData['Misc']['maxlactions'] = retCreatureData['Misc']['lactions']
    # check to see if this creature has a lair, and if so, ask to load the lair's data if one does not already exist
    if ('lair' in retCreatureData['Misc'] and not('lair' in encounter) and not('lair' in playerData)):
        if (autoBattle or DnDUtil.getAnswer('Is this encounter occurring in '+name+'\'s lair') == 'y'):
            if (retCreatureData['Misc']['lair'] == 0):
                lairName = name
            else:
                lairName = retCreatureData['Misc']['lair']
            lairData = getLairData(lairName,retCreatureData)
            if (lairData):
                encounter['lair'] = lairData
                # if this lair was added mid-encounter, we will need to call insertNewActor to place it into the turn order
                if (turnOrder):
                    insertNewActor('lair',lairData)

    # add gold and experience from this creature to the encounter totals
    if (addExp):
        totalExp += getExpForCreature(retCreatureData['CR'])
        totalGold += getGoldForCreature(retCreatureData['CR'])

    return retCreatureData

def getLairData(actor,actorData):

    lairFile = open(LAIR_FILE, 'r', encoding='utf-8', newline='')
    csvLairReader = csv.reader(lairFile)
    header = next(csvLairReader)
    numDataColumns = len(header)
    # remove all spaces from the header
    for i in range(0,numDataColumns):
        header[i] = header[i].replace(' ','')
    # remove notes and owner from the header since we don't want to load this data
    if ('Notes' in header):
        header.remove('Notes')
    try:
        header.remove('Owner')
    except ValueError:
        DnDUtil.printError("Missing Owner data column in lair data file "+LAIR_FILE)

    for row in csvLairReader:
        if (row[0] == actor):
            lairFile.close()
            # initialize the lair data so we can recognize if data is not set
            retLairData = getInitLairData()
            # load from the data given in the lair file
            i = 1
            while (header):
                try:
                    dataKey = header.pop(0)
                    # handle keys that copy the string
                    if (dataKey in ['AbilitiesInfo','RegionalEffects']):
                        retLairData[dataKey] = row[i]
                    # handle keys that convert the string to int
                    elif (dataKey == 'CRMod'):
                        retLairData[dataKey] = int(row[i])
                    # handle keys that parse the string by |
                    elif (dataKey == 'UseAbilities'):
                        retLairData[dataKey] = DnDUtil.mySplit(row[i],'|')
                    else:
                        DnDUtil.printError("Unknown column '"+dataKey+"' found in "+LAIR_FILE)
                        return {}
                    i += 1
                except IndexError:
                    DnDUtil.printError("Not enough data columns for lair "+actor+"! Expected "+str(numDataColumns)+" columns, but only "+str(len(row))+" columns were given")
                    return {}
                except ValueError:
                    DnDUtil.printError("Invalid data given for lair "+actor+" in column "+str(i+1)+". Expected "+dataKey+" data")
                    return {}

            # ensure that every data key was set
            missingDataKeys = []
            for dataKey in retLairData:
                if (retLairData[dataKey] is None):
                    missingDataKeys.append(dataKey)
    
            if (missingDataKeys):
                DnDUtil.printError("Missing data for lair "+actor)
                print("The following data is missing from the lair data file:")
                for dataKey in missingDataKeys:
                    print(dataKey)
                return {}

            # apply the CR mod to the owner's CR if it is a creature then remove it from the lair data
            if ('HP' in actorData):
                actorData['CR'] += retLairData['CRMod']
            del retLairData['CRMod']

            # parse and load the lair abilities
            retLairData['UseAbilities'] = ImportUtil.parseUseAbilitiesData(retLairData['UseAbilities'])

            # print the lair's regional effects, then delete them since they are no longer necessary
            if (retLairData['RegionalEffects']):
                print("-----------------------------------------------------------------------------------------")
                print(actor+'\'s', "lair:", retLairData['RegionalEffects'])
                print("-----------------------------------------------------------------------------------------")
            del retLairData['RegionalEffects']

            # copy every entry from this lair's owner that we haven't already set to ensure this lair has valid data as an actor
            for actorKey in [key for key in actorData if not(key in retLairData)]:
                retLairData[actorKey] = actorData[actorKey]

            return retLairData
    lairFile.close()
    DnDUtil.printError("Could not find lair data for "+actor)
    return {}

def getData(target):

    if (target in playerData):
        return playerData[target]
    elif (target in encounter):
        return encounter[target]
    else:
        return None

def convertData(data):

    if ('HP' in data):
        print("HP is", data['HP'])
        # delete stats players shouldn't have
        del data['HP']
        del data['MaxHP']
        del data['TempHP']
        del data['Environments']
        del data['AbilitiesInfo']
        # if players add bonuses, set all bonuses to 0
        if (PLAYERS_ADD_BONUS):
            for atkKey in ['Atk','DmgBonus']:
                for i in range(0,len(data[atkKey])):
                    for j in range(0,len(data[atkKey][i])):
                        for k in range(0,len(data[atkKey][i][j])):
                            data[atkKey][i][j][k] = 0
            for key in ['SpellAtk','Init','StrSave','DexSave','ConSave','IntSave','WisSave','ChaSave']:
                data[key] = 0
            if ('spmod' in data['Misc']):
                data['Misc']['spmod'] = 0
    else:
        hp = DnDUtil.calculate(input("Input HP: "))
        # add stats that creatures should have
        data['HP'] = hp
        data['MaxHP'] = hp
        data['TempHP'] = 0
        data['Environments'] = ['Unknown']
        data['AbilitiesInfo'] = 'Unknown'

def getAC(targetData):
    
    return targetData['AC']

def search(arguments):

    creatureFile = open(CREATURE_FILE, 'r', encoding='utf-8', newline='')
    csvCreatureReader = csv.reader(creatureFile)
    header = next(csvCreatureReader)
    # these are the columns for which we will return matches if a substring of the data matches the search string
    stringColumnNames = ['name','type','environments','immunities','vulnerabilities','resistances','advantages','disadvantages','useabilities','misc','abilitiesinfo']
    stringColumnIndices = []
    # from each header, convert to lowercase and remove all spaces
    for i in range(0,len(header)):
        header[i] = header[i].replace(' ','').lower()
        if (header[i] in stringColumnNames):
            stringColumnNames.remove(header[i])
            stringColumnIndices.append(i)
    
    parameterIndices = []
    primaryParameterIndex = -1
    for i in range(0,len(arguments)):
        # ensure all letters are lowercase and search for an exact match
        parameter = arguments[i][0].lower()
        if (parameter in header):
            parameterIndex = header.index(parameter)
            parameterIndices.append(parameterIndex)
            if (primaryParameterIndex == -1 and parameter != 'cr'):
                primaryParameterIndex = parameterIndex
        else:
            DnDUtil.printError("Parameter "+parameter+" not found")
            creatureFile.close()
            return []

    crIndex = header.index('cr')

    creatureList = []
                    
    for row in csvCreatureReader:
        match = True
        i = 0
        while (i < len(arguments) and match):
            parameterIndex = parameterIndices[i]
            innerMatch = False
            j = 1
            while (j < len(arguments[i]) and not(innerMatch)):
                searchValue = arguments[i][j]
                creatureValue = row[parameterIndex]
                if (creatureValue != searchValue):
                    if (searchValue.find('>') == 0 and (parameterIndex == crIndex or creatureValue.isdigit()) and searchValue[1:].isdigit()):
                        if (parameterIndex == crIndex):
                            creatureValue = float(creatureValue)
                        else:
                            creatureValue = int(creatureValue)
                        searchValue = int(searchValue[1:])
                        if (creatureValue >= searchValue):
                            innerMatch = True
                    elif (searchValue.find('<') == 0 and (parameterIndex == crIndex or creatureValue.isdigit()) and searchValue[1:].isdigit()):
                        if (parameterIndex == crIndex):
                            creatureValue = float(creatureValue)
                        else:
                            creatureValue = int(creatureValue)
                        searchValue = int(searchValue[1:])
                        if (creatureValue <= searchValue):
                            innerMatch = True
                    elif (parameterIndex in stringColumnIndices and not(searchValue.isdigit()) and creatureValue.find(searchValue) != -1):
                        innerMatch = True
                else:
                    innerMatch = True
                if (parameterIndex == primaryParameterIndex):
                    primaryCreatureValue = creatureValue
                j += 1
            match &= innerMatch
            i += 1
        if (match):
            if (primaryParameterIndex != -1):
                creatureList.append([row[0],row[crIndex],primaryCreatureValue])
            else:
                creatureList.append([row[0],row[crIndex]])

    creatureFile.close()
    return creatureList

def convertClass(Class,level):

    if (Class == 'magicT'):
        breakPoints = [3,5,8,11,14,16,18,20]
        newClass = 'magicbonus'
    else:
        newClass = Class[:-1]
        if (Class == 'spellT'):
            breakPoints = [4,7,9,11,13,16,18,20]
        elif (Class == 'potionT'):
            breakPoints = [2,5,8,11,14,16,18,20]
        elif (Class == 'gemT'):
            breakPoints = [4,8,12,16,20]
        elif (Class == 'artT'):
            breakPoints = [5,10,15,20]
        elif (Class == 'magicitemT'):
            # magic item tiers need to be handled with more precision since some tiers near the middle should never be available at lower levels and, generally, more than 4 tiers need to be available at each level
            if (avgLevel <= 4):
                if (level == 1):
                    convertedTier = 1
                elif (level == 2):
                    randomTable = [2,2,2,3,3]
                    roll = random.randint(1,len(randomTable))
                    convertedTier = randomTable[roll-1]
                elif (level == 3):
                    convertedTier = 6
                else:
                    convertedTier = 7
            elif (avgLevel <= 10):
                if (level == 1):
                    convertedTier = 1
                elif (level == 2):
                    randomTable = [2,2,2,3,3,4]
                    roll = random.randint(1,len(randomTable))
                    convertedTier = randomTable[roll-1]
                elif (level == 3):
                    randomTable = [6,6,6,6,6,6,6,7,7]
                    roll = random.randint(1,len(randomTable))
                    convertedTier = randomTable[roll-1]
                else:
                    convertedTier = 8
            elif (avgLevel <= 16):
                if (level == 1):
                    randomTable = [1,2,3,3,3]
                    roll = random.randint(1,len(randomTable))
                    convertedTier = randomTable[roll-1]
                elif (level == 2):
                    randomTable = [4,4,5]
                    roll = random.randint(1,len(randomTable))
                    convertedTier = randomTable[roll-1]
                elif (level == 3):
                    randomTable = [6,6,7,7,8,8,8,8,8]
                    roll = random.randint(1,len(randomTable))
                    convertedTier = randomTable[roll-1]
                else:
                    convertedTier = 9
            else:
                if (level == 1):
                    randomTable = [3,3,3,4,4,4,4,4,4,4,4]
                    roll = random.randint(1,len(randomTable))
                    convertedTier = randomTable[roll-1]
                elif (level == 2):
                    convertedTier = 5
                elif (level == 3):
                    randomTable = [7,8,8,9,9,9]
                    roll = random.randint(1,len(randomTable))
                    convertedTier = randomTable[roll-1]
                else:
                    convertedTier = 9

            return newClass+str(convertedTier)

    i = 0
    while (i < len(breakPoints) and avgLevel > breakPoints[i]):
        i += 1

    return newClass+str(i+level)

def getItem(data,classTable):

    roll = random.randint(0,len(classTable)-1)
    itemClass = classTable[roll]
    filteredLootTable = []
    for item in data:
        if (data[item]['Class'] == itemClass):
            levelDiff = int(abs(2*((data[item]['Max Level']+data[item]['Min Level']) / 2 - avgLevel)))
            if (levelDiff == 0):
                levelDiff = 1
            filteredLootTable.append([item,levelDiff])
    finalLootTable = []
    breakPoints = []
    for element in filteredLootTable:
        item = element[0]
        levelDiff = element[1]
        i = 0
        while (i < len(breakPoints) and levelDiff > breakPoints[i]):
            i += 1
        finalLootTable.insert(i,item)
        breakPoints.insert(i,levelDiff)

    lcm = lcmm(*breakPoints)
    totalBreakPoints = 0
    for i in range(0,len(breakPoints)):
        breakPoints[i] = lcm // breakPoints[i]
        totalBreakPoints += breakPoints[i]
    roll = random.randint(1,totalBreakPoints)
    prevBreakPoint = 0
    i = 0
    while (i < len(breakPoints) and roll > breakPoints[i]+prevBreakPoint):
        prevBreakPoint += breakPoints[i]
        i += 1

    return finalLootTable[i]

def randomItem(itemRules,itemClass='',prevRules=None):

    if (prevRules is None):
        prevRules = []

    baseItem = ''
    prefix = ''
    suffix = ''

    for rule in itemRules:
        enchantLevel = 0
        convertedTier = -1
        if (rule == 'weapon'):
            classTable = ['simple','simple','simple','martial','martial']
            baseItem = getItem(weaponData,classTable)
            itemClass = 'weapon'
        elif (rule == 'armor'):
            classTable = ['robe','light','light','light','medium','medium','medium','heavy','heavy','heavy','shield','shield']
            baseItem = getItem(armorData,classTable)
            itemClass = armorData[baseItem]['Class']
        elif (rule == 'shield'):
            baseItem = getItem(armorData,['shield'])
            itemClass = 'shield'
        elif (rule.find('magicT') == 0 and len(rule) > 6 and rule[6].isdigit()):
                magicBonus = randomItem([convertClass('magicT',DnDUtil.getInt(rule[-1]))])
                if (magicBonus != '0'):
                    prefix += '+'+magicBonus+' '
        elif (rule == 'enhanced'):
            roll = random.randint(1,4)
            if (roll == 1):
                prefix += 'Deadly '
            elif (roll == 2):
                prefix += 'Keen '
            elif (roll == 3):
                prefix += 'Strong '
            else:
                prefix += 'Accurate '
        else:
            if (rule == 'enchant'):
                if (itemClass == '' or itemClass == 'jewelry'):
                    itemClass = 'basic'
                rule = itemClass+'enchant'
                # these calculations assume level 1: 1-10, level 2: 5-15, level 3: 11-20, level 4: 16-20
                if (avgLevel < 5):
                    enchantLevel = 1
                # 20% chance to get a level 2 enchant at 5th level
                elif (avgLevel == 5):
                    enchantLevel = (random.randint(1,5) // 5) + 1
                else:
                    # the chance out of 10 that we roll the lower enchantment level
                    lowEnchantChance = -2*avgLevel+(10+10*((avgLevel-1) // 5))
                    # ensure a minimum 10% chance to get the lower enchantment level
                    if (lowEnchantChance == 0):
                        lowEnchantChance = 1
                    roll = random.randint(1,10)
                    if (roll <= lowEnchantChance):
                        enchantLevel = (avgLevel-1) // 5
                    else:
                        enchantLevel = (avgLevel+4) // 5
                rule += str(enchantLevel)
            elif (any(rule.find(Class) == 0 for Class in ['spellT','potionT','gemT','artT','magicitemT'])):
                oldRule = rule
                rule = convertClass(rule[:-1],DnDUtil.getInt(rule[-1]))
                if (rule.find(oldRule[:-2]) == 0 and rule[len(oldRule[:-2]):].isdigit()):
                    convertedTier = int(rule[len(oldRule[:-2]):])
                    # 20% chance for this to be an upcasted spell
                    if (rule.startswith('spell') and convertedTier > 1 and convertedTier < 10 and random.randint(1,5) == 5):
                        rule = rule.replace(str(convertedTier),str(random.randint(1,convertedTier-1)))
            elif (rule == 'trap'):
                if (avgLevel < 7):
                    rule += '1'
                elif (avgLevel < 14):
                    rule += '2'
                else:
                    rule += '3'

            classFile = open(CLASS_FILE, 'r', encoding='utf-8', newline='')
            csvClassReader = csv.reader(classFile)
            next(csvClassReader)

            found = False
            for row in csvClassReader:
                if (row[0] == rule):
                    roll = random.randint(1,trueLen(row)-1)
                    selectedItem = row[roll]

                    leftBraceIndex = selectedItem.find('[')
                    while (leftBraceIndex != -1):
                        rightBraceIndex = selectedItem.find(']')
                        if (rightBraceIndex != -1):
                            replacementRule = selectedItem[leftBraceIndex+1:rightBraceIndex]
                            if (not(replacementRule) in prevRules):
                                prevRules.append(rule)
                                selectedItem = selectedItem.replace('['+replacementRule+']',randomItem([replacementRule],'',prevRules))
                            else:
                                DnDUtil.printError("Infinite loop found starting with rule "+str(prevRules[0])+" when repeating rule "+str(replacementRule)+" in rule "+rule)
                                selectedItem = replacementRule
                        else:
                            DnDUtil.printError("Expected closing bracket since an opening bracket is present in "+rule)
                            break
                        leftBraceIndex = selectedItem.find('[')

                    if (convertedTier != -1):
                        selectedItem += ' (Tier '+str(convertedTier)+')'
                    elif (enchantLevel > 1):
                        if (enchantLevel == 2):
                            selectedItem = 'Greater ' + selectedItem
                        elif (enchantLevel == 3):
                            selectedItem = 'Superior ' + selectedItem
                        elif (enchantLevel == 4):
                            selectedItem = 'Supreme ' + selectedItem

                    if (baseItem == ''):
                        baseItem = selectedItem
                    else:
                        suffix += ' of ' + selectedItem
                    found = True
                    break

            classFile.close()
            if (not(found)):
                baseItem = rule

    item = prefix + baseItem + suffix

    return item

def getExpThresholdsForPlayer(level):

    if (level == 1):
        return [25,50,75,100]
    elif (level == 2):
        return [50,100,150,200]
    elif (level == 3):
        return [75,150,225,400]
    elif (level == 4):
        return [125,250,375,500]
    elif (level == 5):
        return [250,500,750,1100]
    elif (level == 6):
        return [300,600,900,1400]
    elif (level == 7):
        return [350,750,1100,1700]
    elif (level == 8):
        return [450,900,1400,2100]
    elif (level == 9):
        return [550,1100,1600,2400]
    elif (level == 10):
        return [600,1200,1900,2800]
    elif (level == 11):
        return [800,1600,2400,3600]
    elif (level == 12):
        return [1000,2000,3000,4500]
    elif (level == 13):
        return [1100,2200,3400,5100]
    elif (level == 14):
        return [1250,2500,3800,5700]
    elif (level == 15):
        return [1400,2800,4300,6400]
    elif (level == 16):
        return [1600,3200,4800,7200]
    elif (level == 17):
        return [2000,3900,5900,8800]
    elif (level == 18):
        return [2100,4200,6300,9500]
    elif (level == 19):
        return [2400,4900,7300,10900]
    elif (level == 20):
        return [2800,5700,8500,12700]
    else:
        DnDUtil.printWarning("Unknown exp threshold for player with level "+str(level))
        return [0,0,0,0]

def getExpForCreature(CR):

    if (CR == 0):
        return 10
    elif (CR == .125):
        return 25
    elif (CR == .25):
        return 50
    elif (CR == .5):
        return 100
    elif (CR == 1):
        return 200
    elif (CR == 2):
        return 450
    elif (CR == 3):
        return 700
    elif (CR == 4):
        return 1100
    elif (CR == 5):
        return 1800
    elif (CR == 6):
        return 2300
    elif (CR == 7):
        return 2900
    elif (CR == 8):
        return 3900
    elif (CR == 9):
        return 5000
    elif (CR == 10):
        return 5900
    elif (CR == 11):
        return 7200
    elif (CR == 12):
        return 8400
    elif (CR == 13):
        return 10000
    elif (CR == 14):
        return 11500
    elif (CR == 15):
        return 13000
    elif (CR == 16):
        return 15000
    elif (CR == 17):
        return 18000
    elif (CR == 18):
        return 20000
    elif (CR == 19):
        return 22000
    elif (CR == 20):
        return 25000
    elif (CR == 21):
        return 33000
    elif (CR == 22):
        return 41000
    elif (CR == 23):
        return 50000
    elif (CR == 24):
        return 62000
    elif (CR == 25):
        return 75000
    elif (CR == 26):
        return 90000
    elif (CR == 27):
        return 105000
    elif (CR == 28):
        return 120000
    elif (CR == 29):
        return 135000
    elif (CR == 30):
        return 155000
    elif (CR == -1):
        return 0
    else:
        DnDUtil.printWarning("Unknown exp value for creature with rating "+str(CR))
        return 0

def getDifficultyIndex(includeAll):

    options = ['Random','Easy','Medium','Hard','Lethal']
    if (includeAll):
        options.append('All')
    choice = DnDUtil.chooseOption('Choose a difficulty for the encounter',options)
    if (choice == 1):
        difficultyRoll = random.randint(1,100)
        if (difficultyRoll <= 10):
            print("Difficulty: Easy")
            difficultyIndex = 0
        elif (difficultyRoll <= 89):
            print("Difficulty: Medium")
            difficultyIndex = 1
        elif (difficultyRoll <= 99):
            print("Difficulty: Hard")
            difficultyIndex = 2
        else:
            print("Difficulty: Lethal")
            difficultyIndex = 3
    else:
        difficultyIndex = choice - 2

    return difficultyIndex

def getMaxCRForDifficultyIndex(difficultyIndex):

    maxCR = 0
    minExp = partyExpThresholds[difficultyIndex]
    if (numPlayers <= 2):
        expMod = 1.5
    elif (numPlayers >= 6):
        expMod = 0.5
    else:
        expMod = 1
    if (difficultyIndex < 3):
        maxExp = partyExpThresholds[difficultyIndex+1]
        for CR in [0,.125,.25,.5]+list(range(1,31)):
            exp = getExpForCreature(CR) * expMod
            if (exp >= maxExp):
                return maxCR
            maxCR = CR
    # for lethal difficulty, return the first CR that is at or over the threshold
    else:
        maxCR = 1
        exp = getExpForCreature(maxCR) * expMod
        while (exp < minExp and maxCR < 31):
            maxCR += 1
            exp = getExpForCreature(maxCR) * expMod

    return maxCR

def getTotalExp(creatures,numList,expDict):

    expModList = [0.5, 1, 1.5, 2, 2.5, 3, 4, 5]
    if (numPlayers <= 2):
        numPlayersIndexMod = -1
    elif (numPlayers >= 6):
        numPlayersIndexMod = 1
    else:
        numPlayersIndexMod = 0

    totalNumCreatures = sum(numList)
    if (totalNumCreatures <= 2):
        expModIndex = totalNumCreatures
    elif (totalNumCreatures <= 6):
        expModIndex = 3
    elif (totalNumCreatures <= 10):
        expModIndex = 4
    elif (totalNumCreatures <= 14):
        expModIndex = 5
    else:
        expModIndex = 6

    totalCreatureExp = 0
    i = 0
    while (i < len(creatures)):
        totalCreatureExp += numList[i] * expDict[creatures[i]]
        i += 1

    expMod = expModList[expModIndex+numPlayersIndexMod]
    totalExp = totalCreatureExp * expMod
    return totalExp

def generateDictForCRSet(difficultyIndex,CRSet):

    retDict = {}
    expModList = [0.5, 1, 1.5, 2, 2.5, 3, 4, 5]
    if (numPlayers <= 2):
        numPlayersIndexMod = -1
    elif (numPlayers >= 6):
        numPlayersIndexMod = 1
    else:
        numPlayersIndexMod = 0
    minExp = partyExpThresholds[difficultyIndex]
    if (difficultyIndex < 3):
        maxExp = partyExpThresholds[difficultyIndex+1]
        for CR in CRSet:
            expPerCreature = getExpForCreature(CR)
            numCreatures = 0
            totalExp = 0
            numList = []
            while (totalExp < maxExp):
                numCreatures += 1
                if (numCreatures <= 2):
                    expModIndex = numCreatures
                elif (numCreatures <= 6):
                    expModIndex = 3
                elif (numCreatures <= 10):
                    expModIndex = 4
                elif (numCreatures <= 14):
                    expModIndex = 5
                else:
                    expModIndex = 6
                expMod = expModList[expModIndex+numPlayersIndexMod]
                totalExp = numCreatures * expPerCreature * expMod
                if (totalExp >= minExp and totalExp < maxExp):
                    numList.append(numCreatures)
            retDict[str(CR)] = numList
    else:
        for CR in CRSet:
            expPerCreature = getExpForCreature(CR)
            numCreatures = 0
            totalExp = 0
            while (totalExp < minExp):
                numCreatures += 1
                if (numCreatures <= 2):
                    expModIndex = numCreatures
                elif (numCreatures <= 6):
                    expModIndex = 3
                elif (numCreatures <= 10):
                    expModIndex = 4
                elif (numCreatures <= 14):
                    expModIndex = 5
                else:
                    expModIndex = 6
                expMod = expModList[expModIndex+numPlayersIndexMod]
                totalExp = numCreatures * expPerCreature * expMod
            retDict[str(CR)] = [numCreatures]

    return retDict

def getGoldForCreature(CR):

    lootRoll = random.randint(1,100)

    if (CR < 0):
        return 0
    elif (CR < 5):
        if (lootRoll <= 30):
            return DnDUtil.calculate('5d6',False) * .01
        elif (lootRoll <= 60):
            return DnDUtil.calculate('4d6',False) * .1
        elif (lootRoll <= 70):
            return DnDUtil.calculate('3d6',False) * .5
        elif (lootRoll <= 95):
            return DnDUtil.calculate('3d6',False)
        else:
            return DnDUtil.calculate('1d6',False) * 10
    elif (CR < 11):
        if (lootRoll <= 30):
            return DnDUtil.calculate('4d6',False) + DnDUtil.calculate('1d6',False) * 5
        elif (lootRoll <= 60):
            return DnDUtil.calculate('6d6',False) + DnDUtil.calculate('2d6',False) * 10
        elif (lootRoll <= 70):
            return DnDUtil.calculate('3d6',False) * 5 + DnDUtil.calculate('2d6',False) * 10
        elif (lootRoll <= 95):
            return DnDUtil.calculate('4d6',False) * 10
        else:
            return DnDUtil.calculate('5d6',False) * 10
    elif (CR < 17):
        if (lootRoll <= 20):
            return DnDUtil.calculate('4d6',False) * 10 + DnDUtil.calculate('1d6',False) * 100
        elif (lootRoll <= 35):
            return DnDUtil.calculate('1d6',False) * 50 + DnDUtil.calculate('1d6',False) * 100
        elif (lootRoll <= 75):
            return DnDUtil.calculate('3d6',False) * 100
        else:
            return DnDUtil.calculate('4d6',False) * 100
    else:
        if (lootRoll <= 15):
            return DnDUtil.calculate('2d6',False) * 500 + DnDUtil.calculate('8d6',False) * 100
        elif (lootRoll <= 55):
            return DnDUtil.calculate('2d6',False) * 1000
        else:
            return DnDUtil.calculate('3d6',False) * 1000

def getLoot(lootRoll):

    lootFile = open(LOOT_FILE, 'r', encoding='utf-8', newline='')
    csvLootReader = csv.reader(lootFile)
    next(csvLootReader)

    if (lootRoll.isdigit()):
        lootRoll = DnDUtil.getInt(lootRoll)
        while (lootRoll > 100):
            print("Loot roll cannot be higher than 100!")
            lootRoll = DnDUtil.getInt(input("Enter a loot roll no higher than 100: "))
        for row in csvLootReader:
            if (lootRoll <= int(row[0])):
                break
    else:
        for row in csvLootReader:
            if (lootRoll == row[0]):
                break
        if (lootRoll != row[0]):
            lootRoll = input("Loot table not found, try again: ")
            getLoot(lootRoll)
            return

    lootFile.close()
    roll = random.randint(1,trueLen(row)-1)
    itemRules = row[roll]
    itemRules = itemRules.split(',')
    item = randomItem(itemRules)

    print("Suggested Loot:", item)

def trueLen(row):

    count = 0
    for item in row:
        if (item == ''):
            return count
        count += 1

    return count

def gcd(a,b):

    while b:
        a, b = b, a % b
    return a

def lcm(a,b):

    return (a*b) // gcd(a,b)

def lcmm(*args):
     
    return reduce(lcm,args)

def getTargets(actor,playerActor,targetPrompt):

    targets = DnDUtil.mySplit(input(targetPrompt+': '),',')
    i = 0
    while (i < len(targets)):
        target = targets[i]
        if (not(target in playerData) and not(target in encounter)):
            if (target == 'self'):
                targets[i] = actor
            elif (target == 'enemies'):
                if (playerActor):
                    targets.extend(list(encounter.keys()))
                else:
                    targets.extend(list(playerData.keys()))
                targets.pop(i)
                i -= 1
            elif (target == 'allies'):
                if (playerActor):
                    targets.extend(list(playerData.keys()))
                else:
                    targets.extend(list(encounter.keys()))
                targets.pop(i)
                i -= 1
            elif (target == 'all'):
                targets.extend(list(playerData.keys()))
                targets.extend(list(encounter.keys()))
                targets.pop(i)
                i -= 1
            else:
                target = autoComplete(target,False)
                if (target):
                    targets[i] = target
                else:
                    print("Invalid target -", targets[i])
                    targets.pop(i)
                    i -= 1
        i += 1

    return targets

def checkTargets(targets,data):

    if (data == encounter):
        creature = True
    else:
        creature = False

    for i in range(0,len(targets)):
        target = targets[i]
        if (not(target in data)):
            targets[i] = autoComplete(target,creature)
            if (targets[i] == '' or not(targets[i] in data)):
                print("Invalid target -", target)
                return False
    return True

def autoComplete(name,creatureNameOnly):

    length = len(name)
    matches = []

    if (creatureNameOnly):
        if (name in encounter):
            return name
    else:
        if (name in playerData or name in encounter):
            return name

    if (length == 0):
        None
    elif (length == 1):
        if (name.isdigit()):
            for creature in encounter:
                if (creature[-1].isdigit()):
                    creatureDigitIndex = 0
                    while (not(creature[creatureDigitIndex].isdigit())):
                        creatureDigitIndex += 1
                    creatureDigit = creature[creatureDigitIndex:]
                else:
                    creatureDigit = ''
                if (creatureDigit == name):
                    matches.append(creature)
        else:
            for creature in encounter:
                if (creature[0] == name):
                    matches.append(creature)
    elif (not(name[-1].isdigit())):
        for creature in encounter:
            if (creature.startswith(name)):
                matches.append(creature)
    else:
        digitIndex = 0
        while (not(name[digitIndex].isdigit())):
            digitIndex += 1
        for creature in encounter:
            if (creature.startswith(name[:digitIndex])):
                if (creature[-1].isdigit()):
                    creatureDigitIndex = 0
                    while (not(creature[creatureDigitIndex].isdigit())):
                        creatureDigitIndex += 1
                    creatureDigit = creature[creatureDigitIndex:]
                else:
                    creatureDigit = ''
                if (name[digitIndex:] == creatureDigit):
                    matches.append(creature)

    if (len(matches) == 0):
        return ''
    elif (len(matches) == 1):
        return matches[0]
    else:
        if (autoBattle):
            choice = 1
        else:
            choice = DnDUtil.chooseOption('Choose a target',matches,True)
        if (choice == len(matches)+1):
            return ''
        else:
            return matches[choice-1]

def autoCompleteTrigger(name):

    if (name in triggerData):
        return name

    matches = []

    for triggerAbility in triggerData:
        if (triggerAbility.startswith(name)):
            matches.append(triggerAbility)

    if (len(matches) == 0):
        return ''
    elif (len(matches) == 1):
        return matches[0]
    else:
        choice = DnDUtil.chooseOption('Choose a trigger',matches,True)
        if (choice == len(matches)+1):
            return ''
        else:
            return matches[choice-1]

def applyActorDot(actor,actorData,target,targetData,dotEffect,dotTiming):

    if (dotEffect[2] == dotTiming):
        dotSave = dotEffect[3]
        dotDamageCalculation = dotEffect[4]
        playerDot = dotEffect[5]
        dotTypes = dotEffect[6]
        dotSuccess = False
        dotHalf = False
        if (not(dotSave) or makeSave(target,targetData,dotSave[0],dotSave[1],dotTypes) > 0):
            dotSuccess = True
        elif (dotSave and dotSave[2] == 'half'):
            print(target, "will take half damage from this DoT")
            dotSuccess = True
            dotHalf = True

        if (dotSuccess):
            if (dotDamageCalculation.isdigit()):
                damage = int(dotDamageCalculation)
            elif (playerDot):
                damage = DnDUtil.getInt(input('Roll for DoT damage ('+dotDamageCalculation+'): '))
            else:
                damage = DnDUtil.calculate(dotDamageCalculation)

            damage = getNetDamage(damage,actorData,target,targetData,dotTypes,'DoT',False)
            if (dotHalf):
                damage /= 2

            if (damage > 0):
                if (dotTypes):
                    primaryDotType = dotTypes[0]
                else:
                    primaryDotType = ''
                print(target, "takes", DnDUtil.getDamageText(damage), primaryDotType, "damage from DoT")
                killed = applyDamage(target,targetData,damage,dotTypes,False)
                if (killed):
                    if (actor == target):
                        return True
                elif ('HP' in targetData):
                    dealDamage(target,targetData,damage)
                    if (checkKilled(target,targetData,damage,dotTypes,False)):
                        print(target, DnDUtil.getDeathText('dies'), "to DoT!")
                        kill(target)
                        if (actor == target):
                            return True
    return False

def applyCC(owner,target,targetData,ccType,extraCCTypes=None,saveType='',saveDC=0,clearTiming='',threeSaveClear=False):

    if (extraCCTypes is None):
        extraCCTypes = []

    if (ccType in ['stun','paralysis','sleep','unconscious','petrification','incapacitate']):
        dropConcentration(target,targetData)

    extraCCTypes.append(ccType)
    ccStatusEffect = [ccType,owner,saveType,saveDC,clearTiming,threeSaveClear,0,0,extraCCTypes]
    targetData['Status'].append(ccStatusEffect)
    return ccStatusEffect

def removeCCEffect(targetData,ccType,owner):

    for statusEffect in targetData['Status']:
        if (statusEffect[0] == ccType and statusEffect[1] == owner):
            targetData['Status'].remove(statusEffect)
            return

    DnDUtil.printWarning("Attempted to remove cc effect "+ccType+" with owner "+owner+" but the status effect could not be found")

def getCCEffectsForTarget(ownerData,target,ccType):

    returnEffects = []
    for effect in ownerData['Effects']:
        if (effect[0] == target and effect[1] == 'cc'):
            if (effect[2] == ccType):
                returnEffects.append(effect)
            else:
                for ccEffect in effect[3]:
                    if (ccEffect[0] == target and ccEffect[1] == 'cc' and ccEffect[2] == ccType):
                        returnEffects.append(effect)
                        break

    return returnEffects

def lairOwnerCanAct(lairBase):

    lairOwnerDataList = []
    for dataDict in [playerData,encounter]:
        for itActor in dataDict:
            if (dataDict[itActor]['Base'] == lairBase and itActor != 'lair'):
                lairOwnerDataList.append(dataDict[itActor])

    if (lairOwnerDataList):
        # the lair should be able to act as long as ANY actor that shares its base is able to act
        if (not(any(ActorUtil.canAct(data) for data in lairOwnerDataList))):
            print("The lair is unable to act since its owner", lairBase, "is", DnDUtil.getStatusText('incapacitated'))
            return False
    else:
        DnDUtil.printError("Could not find owner data for lair with owner "+lairBase)
        
    return True

def displayHP():

    sortedCreatures = list(encounter.keys())
    sortedCreatures.sort()
    for creature in sortedCreatures:
        print(creature+':', end=' ')
        percentHP = int((encounter[creature]['HP'] / encounter[creature]['MaxHP']) * 100)
        if (percentHP == 100):
            print(DnDUtil.getHealText(percentHP)+'%', end=' ')
        elif (percentHP >= 25):
            print(DnDUtil.getDamageText(percentHP)+'%', end=' ')
        else:
            print(DnDUtil.getDeathText(str(percentHP))+'%', end=' ')
        if (encounter[creature]['TempHP']):
            print('('+str(encounter[creature]['HP'])+'(+'+str(encounter[creature]['TempHP'])+')/'+str(encounter[creature]['MaxHP'])+')', 'HP')
        else: 
            print('('+str(encounter[creature]['HP'])+'/'+str(encounter[creature]['MaxHP'])+')', 'HP')

def displayMoveSpeed(actorData):

    print("Move Speed")
    print("--------------")
    print("Ground -", str(actorData['Move']['Ground'])+'ft')
    for moveType in ['Fly','Climb','Swim','Burrow']:
        if (actorData['Move'][moveType] > 0):
            print(moveType, "-", str(actorData['Move'][moveType])+'ft')

def displayStats(data):

    if ('HP' in data):
        player = False
    else:
        player = True
    
    print("Base:", data['Base'], "Type:", data['Size'], end=' ')
    if (data['Type']):
        if (len(data['Type']) == 1):
            print(data['Type'][0])
        else:
            typeString = ''
            for type in data['Type']:
                typeString += type+'/'
            typeString = typeString[:-1]
            print(typeString)
    else:
        print("UNKNOWN TYPE!")

    if (player):
        print("Level:", end=' ')
    else:
        print("CR:", end=' ')
    print(data['CR'])

    if (not(player)):
        if (data['TempHP']):
            print("HP:", str(data['HP'])+'(+'+str(data['TempHP'])+')/'+str(data['MaxHP']), "AC:", data['AC'])
        else: 
            print("HP:", str(data['HP'])+'/'+str(data['MaxHP']), "AC:", data['AC'])
    else:
        print("AC:", data['AC'])
    displayMoveSpeed(data)
    print("Immunities:", data['Immunities'], "Vulnerabilities:", data['Vulnerabilities'])
    print("Resistances:", data['Resistances'])
    print("Atk:", data['Atk'], "Damage:", data['Damage'], "Damage Bonus:", data['DmgBonus'])
    print("Weapon Types:", data['WeaponTypes'])
    print("Saves - Str:", data['StrSave'], "Dex:", data['DexSave'], "Con:", data['ConSave'], "Int:", data['IntSave'], "Wis:", data['WisSave'], "Cha:", data['ChaSave'])
    print("Init:", data['Init'], "Init Roll:", data['InitRoll'])
    print("Status:", data['Status'], "Concentration:", data['Concentration'], "Effects:", data['Effects'])
    print("Advantages:", data['Advantages'], "Disadvantages:", data['Disadvantages'])
    print("Reaction:", data['Reaction'], "Can React:", data['CanReact'], "Prone:", data['Prone'], "Last Action:", data['LastAction'])
    print("Spell Atk:", data['SpellAtk'], "Spell DC:", data['SpellDC'])
    print("Use Abilities:")
    for ability in data['UseAbilities']:
        print(ability, "-", data['UseAbilities'][ability])
    print("Hit Abilities:", data['OnHitAbilities'])
    print("Extra On Hit Abilities:", data['ExtraOnHitAbilities'])
    if (not(player)):
        print("Abilities:", data['AbilitiesInfo'])
    print("Misc:", data['Misc'])

def displayTriggerStats():

    for triggerAbilityName in triggerData:
        triggerAbility = triggerData[triggerAbilityName]
        print("-----------------------------------------------------------")
        print(triggerAbilityName)
        print("Owner:", triggerAbility['Owner'])
        print("Base Level:", triggerAbility['Base Level'], "Spell Level:", triggerAbility['Spell Level'], "Duration:", triggerAbility['Trigger Duration'])
        print("Player?:", triggerAbility['Player?'], "UT?:", triggerAbility['Use Turn?'], "Concentration?:", triggerAbility['Concentration?'], "SD?:", triggerAbility['Static Damage?'])
        if (triggerAbility['Attack']):
            print("Attack Type:", triggerAbility['Attack'], "Atk Mod:", triggerAbility['Spell Atk'])
        if (triggerAbility['Save']):
            print("Save:", triggerAbility['Save'], triggerAbility['DC'], triggerAbility['Save Result'])
        print("Actions:", triggerAbility['Actions'])
        for optionalActionKey in ['Actions2','Scaled Actions','Scaled Actions2']:
            if (optionalActionKey in triggerAbility):
                print(optionalActionKey+':', triggerAbility[optionalActionKey])
        print("Types:", triggerAbility['Type'])
        print("-----------------------------------------------------------")

def isValidAttackType(attackType):

   return attackType in ['m','r','flank','dm','dr','am','ar','gwm','ssr','ra','sa','sam','sar','fb','fob','melee','ranged','greatweaponmaster','sharpshooter','recklessattack','sneakattack','sneakattackm','sneakattackr','flurryofblows']

def getAttackAdvantage(attacker,atkData,defender,defData,meleeAttack,weaponAttack):

    nextAttackAdvantage = False
    if (ActorUtil.hasStatus(atkData,['invisibility'])):
        i = 0
        while (i < len(atkData['Status'])):
            statusEffect = atkData['Status'][i]
            if (statusEffect[0] == 'invisibility'):
                ownerData = getData(statusEffect[1])
                invisibilityEffects = getCCEffectsForTarget(ownerData,attacker,'invisibility')
                for effect in invisibilityEffects:
                    dispel(effect,statusEffect[1],atkData)
                    ownerData['Effects'].remove(effect)
                    if (effect in ownerData['Concentration']):
                        ownerData['Concentration'].remove(effect)
                    print(attacker, "is no longer invisible!")
                    nextAttackAdvantage = True
            else:
                i += 1
    
    #ensure that all effects granting the next attack advantage are used
    while ('nextattack' in atkData['Advantages']):
        nextAttackAdvantage = True
        removeAdvantage(atkData,'nextattack')
    while ('next'+defender in atkData['Advantages']):
        nextAttackAdvantage = True
        removeAdvantage(atkData,'next'+defender)
    while ('nextincattack' in defData['Advantages']):
        nextAttackAdvantage = True
        removeAdvantage(defData,'nextincattack')
    if (nextAttackAdvantage):
        return True

    if (meleeAttack):
        rangeString = 'melee'
    else:
        rangeString = 'ranged'
    if (weaponAttack):
        weaponString = 'weapon'
    else:
        weaponString = 'spell'

    for advantage in atkData['Advantages']:
        if ('attacks' in advantage and (advantage == 'attacks' or advantage == weaponString+'attacks' or advantage == rangeString+'attacks' or advantage == rangeString+weaponString+'attacks')):
            return True

    for advantage in defData['Advantages']:
        if ('inc' in advantage and 'attacks' in advantage and (advantage == 'incattacks' or advantage == 'inc'+weaponString+'attacks' or advantage == 'inc'+rangeString+'attacks' or advantage == 'inc'+rangeString+weaponString+'attacks')):
            return True

    return (defender in atkData['Advantages']
            or ActorUtil.hasStatus(atkData,['greaterinvisibility'])
            or 'grappled' in atkData['Advantages'] and isGrappling(atkData,defender)
            or 'incattacks' in defData['Advantages']
            or meleeAttack and defData['Prone']
            or ActorUtil.hasStatus(defData,['blind','paralysis','petrification','restrain','prestrain','stun','sleep','unconscious'])
            or 'bfrenzy' in atkData['Misc'] and meleeAttack and ('HP' in defData and defData['HP'] < defData['MaxHP']
            or not('HP' in defData) and DnDUtil.getAnswer('Is '+defender+' at full health') == 'n')
            or len([advantage for advantage in [advantage for advantage in atkData['Advantages'] if advantage in ['strattacks','dexattacks','conattacks','intattacks','wisattacks','chaattacks']] if DnDUtil.getAnswer('Is this a '+advantage[:3]+'-based attack') == 'y']) > 0)

def getAttackDisadvantage(atkData,defender,defData,meleeAttack,weaponAttack):

    nextAttackDisadvantage = False
    # ensure that all effects grating the next attack disadvantage are used
    while ('nextattack' in atkData['Disadvantages']):
        nextAttackDisadvantage = True
        removeDisadvantage(atkData,'nextattack')
    while ('next'+defender in atkData['Disadvantages']):
        nextAttackDisadvantage = True
        removeDisadvantage(atkData,'next'+defender)
    while ('nextincattack' in defData['Disadvantages']):
        nextAttackDisadvantage = True
        removeDisadvantage(defData,'nextincattack')
    if (nextAttackDisadvantage):
        return True

    if (meleeAttack):
        rangeString = 'melee'
    else:
        rangeString = 'ranged'
    if (weaponAttack):
        weaponString = 'weapon'
    else:
        weaponString = 'spell'

    for disadvantage in atkData['Disadvantages']:
        if ('attacks' in disadvantage and (disadvantage == 'attacks' or disadvantage == weaponString+'attacks' or disadvantage == rangeString+'attacks' or disadvantage == rangeString+weaponString+'attacks')):
            return True

    for disadvantage in defData['Disadvantages']:
        if ('inc' in disadvantage and 'attacks' in disadvantage and (disadvantage == 'incattacks' or disadvantage == 'inc'+weaponString+'attacks' or disadvantage == 'inc'+rangeString+'attacks' or disadvantage == 'inc'+rangeString+weaponString+'attacks')):
            return True

    return (defender in atkData['Disadvantages']
            or atkData['Prone']
            or ActorUtil.hasStatus(atkData,['blind','poison','restrain','prestrain'])
            or ActorUtil.hasStatus(atkData,['fear']) and (autoBattle or DnDUtil.getAnswer('Is the attacker\'s source of fear in line of sight') == 'y')
            or 'incattacks' in defData['Disadvantages']
            or not(meleeAttack) and defData['Prone']
            or ActorUtil.hasStatus(defData,['invisibility','greaterinvisibility'])
            or len([disadvantage for disadvantage in [disadvantage for disadvantage in atkData['Disadvantages'] if disadvantage in ['strattacks','dexattacks','conattacks','intattacks','wisattacks','chaattacks']] if DnDUtil.getAnswer('Is this a '+disadvantage[:3]+'-based attack') == 'y']) > 0)

def getOnHitTypes(actorData,rangeIndex,atkIndex1,atkIndex2):

    if (rangeIndex == 0):
        rangePrefix = 'm'
    else:
        rangePrefix = 'r'

    if ('oh'+rangePrefix+str(atkIndex1)+str(atkIndex2) in actorData['Misc']):
        return DnDUtil.mySplit(actorData['Misc']['oh'+rangePrefix+str(atkIndex1)+str(atkIndex2)],',')
    elif ('oh'+rangePrefix+str(atkIndex1) in actorData['Misc']):
        return DnDUtil.mySplit(actorData['Misc']['oh'+rangePrefix+str(atkIndex1)],',')
    elif ('oh'+rangePrefix in actorData['Misc']):
        return DnDUtil.mySplit(actorData['Misc']['oh'+rangePrefix],',')
    elif ('oh' in actorData['Misc']):
        return DnDUtil.mySplit(actorData['Misc']['oh'],',')
    else:
        return []

def attack(actor,actorData,defaultTarget,attackType,rangeIndex,atkIndex,roll=-1,singleAttack=False):
    
    # list containing the names of abilities or actions that have been used this round and should not be triggered again
    usedAbilities = []
    damageSummary = {}
    playerAttack = not('HP' in actorData)

    if (rangeIndex >= len(actorData['Atk'])):
        DnDUtil.printError(actor+" does not have a ranged attack")
        return damageSummary

    if (atkIndex >= len(actorData['Atk'][rangeIndex])):
        DnDUtil.printError("No attack bonuses at index "+str(atkIndex)+" for "+actor)
        return damageSummary

    if (singleAttack):
        maxAtks = 1
    else:
        maxAtks = len(actorData['Atk'][rangeIndex][atkIndex])

    # atk bonus index
    j = 0
    atkCount = 0
    while (atkCount < maxAtks):
        hit = False
        crit = False
        killed = False
        uncannyDodge = False
        flank = False
        sneakAttack = False
        flurryOfBlows = False
        advantage = False
        disadvantage = False
        cleave = False
        bonus = 0
        dmgBonus = 0
        onHitAbilities = []

        if (j == len(actorData['Atk'][rangeIndex][atkIndex])-1):
            lastAttack = True
        else:
            lastAttack = False

        # for every attack after the first, allow inputting of a new attack command or simply get the roll for the next attack
        if ('firstAttack' in usedAbilities):
            attackCommand = ['loop']
            while (attackCommand == ['loop']):
                if (autoBattle):
                    attackCommand = ['m',defaultTarget]
                    if (playerAttack):
                        attackCommand.append(' '+str(random.randint(1,20)))
                else:
                    attackCommand = DnDUtil.mySplit(input('Input command for attack '+str(atkCount+1)+'/'+str(maxAtks)+' (default - '+attackType+' '+defaultTarget+'): '),' ')
                if (attackCommand == ['done']):
                    return damageSummary
                numArgs = len(attackCommand)
                if (playerAttack):
                    maxAttackArgs = 3
                else:
                    maxAttackArgs = 2
                if (numArgs > maxAttackArgs):
                    print("Too many arguments given! There can only be a maximum of "+str(maxAttackArgs)+" attack arguments!")
                    attackCommand = ['loop']
                elif (playerAttack and numArgs == 0):
                    print("Must input at least a roll for player attacks!")
                    attackCommand = ['loop']
                else:
                    if (playerAttack):
                        if (numArgs > 1):
                            if (isValidAttackType(attackCommand[0])):
                                attackType = attackCommand[0]
                            else:
                                print("Invalid attack type", attackCommand[0])
                                attackCommand = ['loop']
                        if (attackCommand != ['loop']):
                            if (numArgs == 3):
                                nextTarget = attackCommand[1]
                            else:
                                nextTarget = defaultTarget
                            target = autoComplete(nextTarget,False)
                            if (target):
                                defaultTarget = target
                            elif (autoBattle):
                                defaultTarget = getRandomTarget(actor)
                            else:
                                print("Invalid attack target", nextTarget)
                                attackCommand = ['loop']
                        if (attackCommand != ['loop']):
                            roll = DnDUtil.getInt(attackCommand[-1])
                    else:
                        if (numArgs == 0):
                            target = autoComplete(defaultTarget,False)
                            if (target):
                                defaultTarget = target
                            elif (autoBattle):
                                defaultTarget = getRandomTarget(actor)
                            else:
                                print("Invalid attack target", defaultTarget)
                                attackCommand = ['loop']
                        elif (numArgs == 1):
                            if (isValidAttackType(attackCommand[0])):
                                attackType = attackCommand[0]
                            else:
                                target = autoComplete(attackCommand[0],False)
                                if (target):
                                    defaultTarget = target
                                else:
                                    print(attackCommand[0], "is neither a target nor a valid attack command!")
                                    attackCommand = ['loop']
                        else:
                            if (isValidAttackType(attackCommand[0])):
                                attackType = attackCommand[0]
                                target = autoComplete(attackCommand[1],False)
                                if (target):
                                    defaultTarget = target
                                elif (autoBattle):
                                    defaultTarget = getRandomTarget(actor)
                                else:
                                    print("Invalid attack target", attackCommand[1])
                                    attackCommand = ['loop']
                            else:
                                print("Invalid attack type", attackCommand[0])
                                attackCommand = ['loop']           

        # alter variables based on the attack type
        # the vast majority of attack commands will be made with the m and r commands, so check for those first to save time
        if (attackType in ['m','r']):
            None
        elif (attackType == 'flank'):
            flank = True
        elif (attackType in ['dm','dr']):
            disadvantage = True
        elif (attackType in ['am','ar']):
            advantage = True
        elif (attackType in ['gwm','ssr','greatweaponmaster','sharpshooter']):
            if (not(playerAttack) or not(PLAYERS_ADD_BONUS)):
                bonus = -5
                dmgBonus = 10
        # reckless attack only works when declared on the first attack but should not print an error if input later
        elif (attackType in ['ra','recklessattack']):
            None
        elif (attackType in ['sa','sam','sar','sneakattack','sneakattackm','sneakattackr']):
            sneakAttack = True
        elif (attackType in ['fb','fob','flurryofblows']):
            flurryOfBlows = True
        else:
            DnDUtil.printError("Invalid attack type "+attackType+" passed to attack function")
            return damageSummary

        target = chooseAttackTarget(actor,actorData,defaultTarget,rangeIndex,atkIndex,j)
        # if this is a single attack, but our first attack is grabbing someone, look for another attack to use
        if (singleAttack and target != defaultTarget):
            print(actor, "is grabbing an opponent with this attack! Looking for another available attack...")
            for i in range(1,len(actorData['Atk'][rangeIndex][atkIndex])):
                target = chooseAttackTarget(actor,actorData,defaultTarget,rangeIndex,atkIndex,i)
                if (target == defaultTarget):
                    print("Another valid attack was found!")
                    j = i
                    break
            if (j == 0):
                print(actor, "was unable to make an attack on", defaultTarget)
                return damageSummary

        targetData = getData(target)
        if (targetData is None):
            print(actor, "will instead resume attacking", defaultTarget, "since", target, "has died!")
            target = defaultTarget
            targetData = getData(target)
        playerTarget = not('HP' in targetData)
        defense = getAC(targetData)
        if (flank):
            if ('flank' in targetData['Immunities']):
                print(target, "is", DnDUtil.getFailText('immune'), "to being flanked!")
                flank = False
            elif ('iflank' in actorData['Misc']):
                dmgBonus = actorData['Misc']['iflank']

        attackAdvantage = getAttackAdvantage(actor,actorData,target,targetData,rangeIndex == 0,not('spell' in actorData['WeaponTypes'][rangeIndex][atkIndex][j])) or advantage or flank
        attackDisadvantage = getAttackDisadvantage(actorData,target,targetData,rangeIndex == 0,not('spell' in actorData['WeaponTypes'][rangeIndex][atkIndex][j])) or disadvantage
        atkBonus = actorData['Atk'][rangeIndex][atkIndex][j] + bonus
        if (playerAttack):
            roll = getAdvantageDisadvantageRoll(roll,attackAdvantage,attackDisadvantage)
        else:
            roll = ActorUtil.makeRoll(actor,playerAttack,attackAdvantage,attackDisadvantage,atkBonus,False)
        if (playerAttack and PLAYERS_ADD_BONUS):
            if (roll == 100):
                roll = 20
            elif (roll >= 20):
                atkBonus = roll - 2
                roll = 2
        attackRoll = roll + atkBonus
        if (not(playerAttack) or not(PLAYERS_ADD_BONUS)):
            attackRoll = ActorUtil.applyBlessBane(actor,actorData,attackRoll,defense)

        if (not(autoBattle) and not(checkTemporalShunt(actor,actorData,playerAttack))):
            return damageSummary

        if (applyMirrorImage(roll,attackRoll,target,targetData,playerTarget) and roll != 1 and (roll == 20 or attackRoll >= defense)):
            if (roll != 20 and 'parry' in targetData['Misc'] and rangeIndex == 0 and defense + targetData['Misc']['parry'] > attackRoll and ActorUtil.canReact(targetData) and (autoBattle or DnDUtil.getAnswer('Use '+target+'\'s reaction to parry') == 'y')):
                print(target, "uses its reaction to parry the attack!")
                targetData['Reaction'] = False
            elif (roll != 20 and 'ad' in targetData['Misc'] and defense + 2 > attackRoll and ActorUtil.canReact(targetData) and (autoBattle or DnDUtil.getAnswer('Use '+target+'\'s reaction to use arcane deflection') == 'y')):
                print(target, "uses its reaction to use arcane deflection and negate the attack!")
                targetData['Reaction'] = False
                applyCC(target,target,targetData,'arcane deflection')
                targetData['Effects'].append([target,'cc','arcane deflection',[],1.5])
            elif (roll != 20 and 'shield' in targetData['UseAbilities'] and defense + 5 > attackRoll and ActorUtil.canReact(targetData) and (autoBattle or DnDUtil.getAnswer('Use '+target+'\'s reaction to cast Shield') == 'y')):
                print(target, "uses its reaction to cast Shield and block the attack!")
                targetData['Reaction'] = False
                ability = targetData['UseAbilities']['shield']
                useAbility(playerTarget,'shield',ability['Type'],ability['Duration'],ability['Actions'],playerTarget,[target],target,targetData,target,targetData,ability['Attack Mod'],ability['Save'],ability['DC'],0,ability['Base Level'],ability['Base Level'],False,False,False,ability['Concentration?'],{})
            else:
                hit = True
                critC = getCritStat(actorData,rangeIndex,atkIndex,j,0)
                damageData = actorData['Damage'][rangeIndex][atkIndex][j]
                dmgBonusData = actorData['DmgBonus'][rangeIndex][atkIndex][j]
                weaponTypeData = actorData['WeaponTypes'][rangeIndex][atkIndex][j]
                if (roll >= critC or rangeIndex == 0 and ActorUtil.hasStatus(targetData,['paralysis','sleep','unconscious'])):
                    if (not(ActorUtil.isImmuneToType(targetData,['crit']))):
                        crit = True
                    else:
                        print(target, "can't be", DnDUtil.getFailText('crit')+'!')

        if (hit):
            print(actor, "successfully", DnDUtil.getPassText('hits'), target+'!')

            if (crit):
                print("This is a crit!")
                if (playerAttack and PLAYERS_ADD_BONUS):
                    critMultiplier = 1
                else:
                    critMultiplier = getCritStat(actorData,rangeIndex,atkIndex,j,1)
                print("This attack's damage will be multiplied by", critMultiplier)
                    
                if (rangeIndex == 0 and 'gwm' in actorData['Misc'] and not('cleave' in usedAbilities)):
                    print("Cleave activated!")
                    cleave = True
                if ('bc' in actorData['Misc'] and rangeIndex == 0):
                    if (playerAttack and not(autoBattle)):
                        dmgBonus += DnDUtil.getInt(input("Roll for brutal critical ("+actorData['Misc']['bc']+"): "))
                    else:
                        bcBonus = DnDUtil.calculate(actorData['Misc']['bc'])
                        print(actor, "deals", bcBonus, "extra damage from brutal critical!")
                        dmgBonus += bcBonus
            else:
                critMultiplier = 1

            if ('ud' in targetData['Misc'] and ActorUtil.canReact(targetData) and (autoBattle or DnDUtil.getAnswer('Use '+target+'\'s reaction to use uncanny dodge on this attack') == 'y')):
                uncannyDodge = True
                targetData['Reaction'] = False

            if (playerAttack and not(autoBattle)):
                done = False
                while (not(done)):
                    damage = input("Roll for weapon damage "+"("+damageData+"): ")
                    if (damage in ['dsmite','sstrike','logtoss']):
                        if (rangeIndex != 0 and damage in ['dsmite','sstrike']):
                            print("You can only activate", damage, "on melee attacks!")
                        elif (rangeIndex == 0 and damage in ['logtoss']):
                            print("You can only activate", damage, "on ranged attacks!")
                        elif (not(damage in actorData['UseAbilities'])):
                            print(actor, "does not have access to", damage+'!')
                        else:
                            print(damage, "activated!")
                            ability = copy(actorData['UseAbilities'][damage])
                            ability['Trigger Condition'] = ability['Attack']
                            ability['Charges'] = 1
                            onHitAbilities.append([damage,ability])
                    elif (damage.isdigit()):
                        done = True
                        damage = int(damage)
            else:
                damage = DnDUtil.calculate(damageData)

            if (ActorUtil.hasStatus(targetData,['huntersmark']) and any(effect[0] == target and effect[1] == 'cc' and effect[2] == 'huntersmark' and effect[-1] == -1 for effect in actorData['Effects'])):
                if (playerAttack and not(autoBattle)):
                    damage += DnDUtil.getInt(input('Roll for hunter\'s mark damage (1d6): '))
                else:
                    huntersMarkDamage = DnDUtil.calculate('1d6')
                    damage += huntersMarkDamage
                    print(actor, "deals an additional", huntersMarkDamage, "damage from hunter's mark!")

            damage = int(damage*critMultiplier) + dmgBonusData

            if (dmgBonus):
                if (isinstance(dmgBonus,int)):
                    damage += dmgBonus
                elif (dmgBonus.isdigit()):
                    damage += int(dmgBonus)
                elif (playerAttack and not(autoBattle)):
                    damage += int(DnDUtil.getInt(input('Roll for bonus damage ('+dmgBonus+'): '))*critMultiplier)
                else:
                    damage += int(DnDUtil.calculate(dmgBonus)*critMultiplier)

            if (damage < 0):
                damage = 0

            for type in targetData['Type']:
                if (type in actorData['Misc']):
                    if (not(playerAttack)):
                        print(actor, "deals bonus damage since", target, "is", type)
                    if (actorData['Misc'][type].isdigit()):
                        damage += actorData['Misc'][type]
                    elif (playerAttack and not(autoBattle)):
                        damage += int(critMultiplier*DnDUtil.getInt(input('Roll for bonus damage since '+target+' is '+type+' ('+actorData['Misc'][type]+'): ')))
                    else:
                        damage += int(critMultiplier*DnDUtil.calculate(actorData['Misc'][type]))

            if (not('sneakAttack' in usedAbilities) and (sneakAttack or attackAdvantage and not(attackDisadvantage)) and 'sa' in actorData['Misc'] and not(ActorUtil.isImmuneToType(targetData,['crit']))):
                sneakAttack = True
                usedAbilities.append('sneakAttack')
                parsedSneakAttackDamage = DnDUtil.parseDamageCalculation(actorData['Misc']['sa'])
                if (playerAttack and PLAYERS_ADD_BONUS):
                    sneakAttackDamage = 0
                elif (playerAttack and not(autoBattle)):
                    sneakAttackDamage = int(critMultiplier*DnDUtil.getInt(input("Roll for sneak attack damage "+"("+parsedSneakAttackDamage[0]+"): "))) + parsedSneakAttackDamage[1]
                else:
                    sneakAttackDamage = int(critMultiplier*DnDUtil.calculate(parsedSneakAttackDamage[0])) + parsedSneakAttackDamage[1]
                    print(target, "takes", sneakAttackDamage, "extra damage from sneak attack!")
                damage += sneakAttackDamage

            if (not('lightningLauncher' in usedAbilities) and rangeIndex != 0 and 'lightning' in weaponTypeData and 'll' in actorData['Misc']):
                usedAbilities.append('lightningLauncher')
                if (playerAttack and not(autoBattle)):
                    lightningLauncherDamage = int(critMultiplier*DnDUtil.getInt(input("Roll for lightning launcher damage (1d6): ")))
                else:
                    lightningLauncherDamage = int(critMultiplier*DnDUtil.calculate('1d6'))
                    print(target, "takes", lightningLauncherDamage, "extra damage from lightning launcher!")
                damage += lightningLauncherDamage

            if (damage > 0):
                damage = getNetDamage(damage,actorData,target,targetData,weaponTypeData,'this attack',not('spell' in weaponTypeData),uncannyDodge)

                if ('ham' in targetData['Misc'] and (weaponTypeData and 'nonmagic' in weaponTypeData or not(weaponTypeData) and (autoBattle or DnDUtil.getAnswer('Is this an attack from a magic weapon') == 'n'))):
                    damage -= 3
                    if (damage < 0):
                        damage = 0

            if (ActorUtil.hasStatus(targetData,['hex']) and any(effect[0] == target and effect[1] == 'cc' and effect[2] == 'hex' and effect[-1] == -1 for effect in actorData['Effects'])):
                if (playerAttack and not(autoBattle)):
                    hexDamage = DnDUtil.getInt(input('Roll for hex damage (1d6): '))
                else:
                    hexDamage = DnDUtil.calculate('1d6')
                hexDamage = int(getNetDamage(hexDamage,actorData,target,targetData,['necrotic'],'hex',False)*critMultiplier)
                if (not(playerAttack)):
                    print(actor, "deals an additional", DnDUtil.getDamageText(hexDamage), "necrotic damage from hex!")
                damage += hexDamage

            if (ActorUtil.hasStatus(actorData,['spiritshroud']) and (rangeIndex == 0 or DnDUtil.getAnswer('Is '+target+' within 10ft of '+actor) == 'y')):
                if (not('spiritshroudtype' in actorData['Misc'])):
                    DnDUtil.printWarning("Missing spiritshroudtype misc data in "+actor)
                elif (not('spiritshrouddamage' in actorData['Misc'])):
                    DnDUtil.printWarning("Missing spiritshrouddamage misc data in "+actor)
                else:
                    if (playerAttack and not(autoBattle)):
                        spiritShroudDamage = DnDUtil.getInt(input('Roll for spirit shroud damage ('+actorData['Misc']['spiritshrouddamage']+'): '))
                    else:
                        spiritShroudDamage = DnDUtil.calculate(actorData['Misc']['spiritshrouddamage'])
                    spiritShroudDamage = int(getNetDamage(spiritShroudDamage,actorData,target,targetData,[actorData['Misc']['spiritshroudtype']],'spritshroud',False)*critMultiplier)
                    damage += spiritShroudDamage
                    if (spiritShroudDamage):
                        if (not(playerAttack)):
                            print(actor, "deals an additional", DnDUtil.getDamageText(spiritShroudDamage), actorData['Misc']['spiritshroudtype'], "damage from spirit shroud!")
                        useAbility(playerAttack,'spirit shroud antiheal',[],1.5,[['immunity','heal']],playerTarget,[target],target,targetData,actor,actorData,0,'',0,0,0,0,False,False,False,False,{})

            if (not('divineFury' in usedAbilities) and ('dfn' in actorData['Misc'] or 'dfr' in actorData['Misc']) and ActorUtil.hasStatus(actorData,['rage'])):
                usedAbilities.append('divineFury')
                if ('dfn' in actorData['Misc']):
                    dfKey = 'dfn'
                    damageType = 'necrotic'
                else:
                    dfKey = 'dfr'
                    damageType = 'radiant'
                if (playerAttack and not(autoBattle)):
                    dfDamage = DnDUtil.getInt(input('Roll for divine fury damage (1d6): '))
                else:
                    dfDamage = DnDUtil.calculate('1d6')
                if (not(playerAttack) or not(PLAYERS_ADD_BONUS)):
                    if (actorData['Misc'][dfKey]):
                        dfDmgBonus = actorData['Misc'][dfKey] // 2
                    else:
                        dfDmgBonus = actorData['CR'] // 2
                else:
                    dfDmgBonus = 0

                dfDamage = getNetDamage(int(dfDamage*critMultiplier)+dfDmgBonus,actorData,target,targetData,[damageType],'divine fury',False)
                damage += dfDamage
                if (not(playerAttack)):
                    print(actor, "deals an additional", DnDUtil.getDamageText(dfDamage), damageType, "damage from divine fury!")

            if (rangeIndex == 1 and not('spell' in weaponTypeData) and 'dm' in targetData['Misc'] and ActorUtil.canReact(targetData) and (autoBattle or DnDUtil.getAnswer('Use '+target+'\'s reaction to deflect missile') == 'y')):
                targetData['Reaction'] = False
                if (damage > 0):
                    if (playerTarget and not(autoBattle)):
                        deflectRoll = DnDUtil.getInt(input('Roll for damage reduction (1d10): '))
                    else:
                        deflectRoll = random.randint(1,10)
                        print(target, "rolls a", deflectRoll, "for damage reduction")
                    deflectDmgReduction = deflectRoll + targetData['Misc']['dm']
                    print("This attack's damage will be reduced by", deflectDmgReduction)
                    damage -= deflectDmgReduction
                    if (damage < 0):
                        damage = 0
                if (damage == 0 and (autoBattle or DnDUtil.getAnswer('Spend a ki point to attack with this missile') == 'y')):
                    deflectAttackTarget = ''
                    finished = False
                    while (not(finished)):
                        if (autoBattle):
                            deflectAttackTarget = getRandomTarget(target)
                        else:
                            deflectAttackTarget = input('Choose a target for this attack: ')
                        if (deflectAttackTarget == ''):
                            finished = True
                        else:
                            deflectAttackTarget = autoComplete(deflectAttackTarget,False)
                            if (deflectAttackTarget):
                                finished = True
                    if (deflectAttackTarget):
                        if (playerTarget and not(autoBattle)):
                            deflectAttackRoll = DnDUtil.getInt(input('Roll for deflect attack: '))
                        else:
                            deflectAttackRoll = -1
                        deflectDamageSummary = attack(target,targetData,deflectAttackTarget,'r',1,0,deflectAttackRoll,True)
                        extendDamageSummary(damageSummary,deflectDamageSummary)
                        if (not(getData(actor)) or not(getData(target))):
                            return damageSummary

            if (damage > 0):
                if (weaponTypeData):
                    primaryWeaponType = weaponTypeData[0]
                else:
                    primaryWeaponType = ''
                print(actor, "deals", DnDUtil.getDamageText(damage), primaryWeaponType, "damage to", target)
                if (not(playerTarget)):
                    dealDamage(target,targetData,damage)
                killed = applyDamage(target,targetData,damage,weaponTypeData,crit)
                updateDamageSummary(damageSummary,target,damage)

            if (not(killed)):
                if (rangeIndex < len(actorData['OnHitAbilities']) and atkIndex < len(actorData['OnHitAbilities'][rangeIndex])):
                    if (len(actorData['OnHitAbilities'][rangeIndex][atkIndex]) == 1):
                        onHitAbilities.append([actor+' On Hit Ability '+str(rangeIndex)+str(atkIndex)+str(j),actorData['OnHitAbilities'][rangeIndex][atkIndex][0]])
                    elif (len(actorData['OnHitAbilities'][rangeIndex][atkIndex]) == len(actorData['Atk'][rangeIndex][atkIndex])):
                        onHitAbilities.append([actor+' On Hit Ability '+str(rangeIndex)+str(atkIndex)+str(j),actorData['OnHitAbilities'][rangeIndex][atkIndex][j]])
                    else:
                        DnDUtil.printError("Invalid on hit abilities format")

                for onHitAbility,onHitAbilityData in list(actorData['ExtraOnHitAbilities'].items()):
                    onHitAbilities.append([onHitAbility,onHitAbilityData])

                i = 0
                while (i < len(onHitAbilities)):
                    abilityName = onHitAbilities[i][0]
                    ability = onHitAbilities[i][1]
                    if (ability and ability['Charges']):
                        triggerConditionSuccess = True
                        success = True
                        half = False
                        actionData = deepcopy(ability['Actions'])
                        saveDC = ability['DC'] if ability['DC'] != 0 else actorData['SpellDC']
                        # don't perform any actions from this ability that would create effects already active from the attacker
                        for effect in actorData['Effects']:
                            if (effect[0] == target and effect[1] == 'cc' and effect[2] == abilityName):
                                if (abilityName.find('On Hit Ability') != -1):
                                    for ccEffect in effect[3]:
                                        for action in actionData:
                                            # remove non-cc actions that would repeat an action other than wound
                                            if (action[0] == ccEffect[1] and not(action[0] in ['cc','ccsave','ccsave3','wound'])):
                                                actionData.remove(action)
                                                break
                                            # remove cc actions that would apply the same cc
                                            elif (ccEffect[1] == 'cc' and action[0] in ['cc','ccsave','ccsave3'] and action[1] == ccEffect[2]):
                                                actionData.remove(action)
                                                break
                                    # if we removed all the actions because they were duplicate effects, indicate that the ability did not succeed
                                    if (not(actionData)):
                                        success = False
                                        break
                                else:
                                    success = False
                                    break

                        if (success):
                            triggerCondition = ability['Trigger Condition']
                            if (triggerCondition):
                                if (triggerCondition == 'crit'):
                                    if (not(crit)):
                                        triggerConditionSuccess = False
                                elif (triggerCondition == 'melee'):
                                    if (rangeIndex != 0):
                                        triggerConditionSuccess = False
                                elif (triggerCondition == 'ranged'):
                                    if (rangeIndex != 1):
                                        triggerConditionSuccess = False
                                elif (triggerCondition == 'sneakattack'):
                                    if (not(sneakAttack)):
                                        triggerConditionSuccess = False
                                elif (triggerCondition == 'kill'):
                                    if (playerTarget):
                                        triggerConditionSuccess = False
                                    elif (targetData['HP'] > 0):
                                        triggerConditionSuccess = False
                                elif (len(triggerCondition) == 3 and all(c.isdigit() for c in triggerCondition) and triggerCondition != str(rangeIndex)+str(atkIndex)+str(j)):
                                    triggerConditionSuccess = False

                            if (not(triggerConditionSuccess)):
                                # if we failed the initial trigger condition and this ability rerquires a save, we have already failed since secondary actions would then apply to the save result instead
                                if (ability['Save'] or not('Actions2' in ability)):
                                    success = False
                                else:
                                    actionData = deepcopy(ability['Actions2'])

                        if (success):
                            if (abilityName.find('On Hit Ability') != -1):
                                ohTypes = getOnHitTypes(actorData,rangeIndex,atkIndex,j)
                            else:
                                ohTypes = ability['Type']

                        if (success and ability['Save'] and ability['Save Result'] != 'none'):
                            saveDiff = makeSave(target,targetData,ability['Save'],saveDC,ohTypes)
                            if (saveDiff == 0):
                                if (ability['Save Result'] == 'negates'):
                                    if ('Actions2' in ability):
                                        actionData = deepcopy(ability['Actions2'])
                                    else:
                                        success = False
                                elif (ability['Save Result'] == 'half'):
                                    if ('Actions2' in ability):
                                        actionData = deepcopy(ability['Actions2'])
                                    half = True
                        else:
                            saveDiff = -1

                        if (success):
                            if (ActorUtil.isImmuneToType(targetData,ohTypes)):
                                print(target, "is", DnDUtil.getFailText('immune'), "to this on-hit ability!")
                            else:
                                if ('Base Level' in ability and 'Spell Level' in ability):
                                    baseLevel = ability['Base Level']
                                    spellLevel = ability['Spell Level']
                                else:
                                    baseLevel = -1
                                    spellLevel = -1
                                abilityDamageSummary = useAbility(playerAttack,abilityName,ohTypes,ability['Duration'],actionData,playerTarget,[target],target,targetData,actor,actorData,0,ability['Save'],saveDC,saveDiff,baseLevel,spellLevel,half,crit,uncannyDodge,ability['Concentration?'],{})
                                extendDamageSummary(damageSummary,abilityDamageSummary)
                                if (not(getData(target))):
                                    killed = True

                        if (triggerConditionSuccess):
                            if (ability['Charges'] != -1):
                                ability['Charges'] -= 1
                                if (ability['Charges'] == 0):
                                    if (abilityName in actorData['ExtraOnHitAbilities']):
                                        print(actor, "no longer has the on-hit ability", abilityName)
                                        # since the effect that created this on-ability is very likely to reside in the attacker, it is worth it to check and try to remove it
                                        found = False
                                        for effect in actorData['Effects']:
                                            if (effect[0] == actor):
                                                if (effect[1] == 'cc'):
                                                    for ccEffect in effect[3]:
                                                        if (ccEffect[1] == 'onhit' and ccEffect[2] == abilityName):
                                                            found = True
                                                            break
                                                elif (effect[1] == 'onhit' and effect[2] == abilityName):
                                                    found = True
                                                if (found):
                                                    dispel(effect,actor,actorData)
                                                    actorData['Effects'].remove(effect)
                                                    if (effect in actorData['Concentration']):
                                                        actorData['Concentration'].remove(effect)
                                                    break
                    i += 1

            if (not(killed)):
                if (flurryOfBlows and lastAttack and not('openHandedTechnique' in usedAbilities) and 'oht' in actorData['Misc']):
                    usedAbilities.append('openHandedTechnique')
                    if (autoBattle):
                        choice = 1
                    else:
                        choice = DnDUtil.chooseOption('Choose an effect for Open Hand Technique',['Dex save or knocked prone','Str save or pushed 15 feet away','Can\'t take reactions until next turn'])
                    if (choice == 1):
                        if (makeSave(target,targetData,'dex',actorData['SpellDC'],['prone']) > 0):
                            knockProne(target,targetData)
                    elif (choice == 2):
                        if (makeSave(target,targetData,'str',actorData['SpellDC'],['push']) > 0):
                            print(target, "is knocked back 15 feet!")
                    else:
                        targetData['CanReact'] = False
                        actorData['Effects'].append([target,'react',1.5])
                        print(target, "can't take reactions for a turn!")

                actorKilled = False
                if (rangeIndex == 0 and 'thorns' in targetData['Misc']):
                    thornsArgs = targetData['Misc']['thorns'].split(',')
                    thornsDamageString = str(thornsArgs[0])
                    thornsTypes = thornsArgs[1:]
                    if (thornsDamageString.isdigit()):
                        thornsDamage = int(thornsDamageString)
                    elif (playerTarget and not(autoBattle)):
                        thornsDamage = DnDUtil.getInt(input('Roll for thorns damage ('+thornsDamageString+'): '))
                    else:
                        thornsDamage = DnDUtil.calculate(thornsDamageString)

                    thornsDamage = getNetDamage(thornsDamage,targetData,actor,actorData,thornsTypes,'thorns',False)
                    if (thornsDamage > 0):
                        if (thornsTypes):
                            primaryThornsType = thornsTypes[0]
                        else:
                            primaryThornsType = ''
                        print(actor, "takes", DnDUtil.getDamageText(thornsDamage), primaryThornsType, "damage from thorns!")
                        applyDamage(actor,actorData,thornsDamage,thornsTypes,False)
                        updateDamageSummary(damageSummary,actor,thornsDamage)
                        if (not(playerAttack)):
                            dealDamage(actor,actorData,thornsDamage)
                            if (checkKilled(actor,actorData,thornsDamage,thornsTypes,False)):
                                print(actor, DnDUtil.getDeathText('dies'), "from thorns!")
                                kill(actor)
                                setDamageSummaryKilled(damageSummary,actor)
                                actorKilled = True
                    
                if (killed or not(playerTarget) and checkKilled(target,targetData,damage,weaponTypeData,crit)):
                    print(actor, "has", DnDUtil.getDeathText('slain'), target+'!')
                    setDamageSummaryKilled(damageSummary,target)
                    if (not(killed)):
                        kill(target)
                    if (rangeIndex == 0 and ('gwm' in actorData['Misc'] or 'cleave' in actorData['Misc']) and not('cleave' in usedAbilities)):
                        print("Cleave activated!")
                        cleave = True
  
                    if (rangeIndex == 0 and 'icleave' in actorData['Misc']):
                        print("Cleave activated!")
                        cleave = True

                if (actorKilled):
                    return damageSummary
        else:
            if (PLAYERS_ADD_BONUS and playerAttack):
                print(actor, DnDUtil.getFailText('misses'), target, "(AC", str(defense)+')')
            else:
                print(actor, DnDUtil.getFailText('misses'), target)
                print(actor, "will need a roll of", defense - atkBonus, '('+str(defense)+')', "to hit", target)

        if (singleAttack):
            return damageSummary

        if (cleave):
            usedAbilities.append('cleave')
            maxAtks += 1
            j = 0
        elif (lastAttack and flurryOfBlows and not('flurryOfBlows' in usedAbilities)):
            usedAbilities.append('flurryOfBlows')
            maxAtks += 1
        else:
            j += 1
        usedAbilities.append('firstAttack')
        atkCount += 1

    if ('sm' in actorData['Misc'] and rangeIndex == 0):
        shoveTarget = ''
        while (shoveTarget == ''):
            if (autoBattle):
                rawInput = ''
            else:
                rawInput = input('Input shove target for shield master (default - '+defaultTarget+'): ')
            if (rawInput == 'done'):
                return damageSummary
            elif (rawInput == ''):
                rawInput = defaultTarget

            shoveTarget = autoComplete(rawInput,False)
            if (shoveTarget):
                shove(actor,actorData,playerAttack,shoveTarget,getData(shoveTarget),playerTarget)
            else:
                print("Invalid target -", rawInput)

    return damageSummary

def extendDamageSummary(damageSummary,extensionDamageSummary):

    for target in extensionDamageSummary:
        updateDamageSummary(damageSummary,target,extensionDamageSummary[target][0])
        damageSummary[target][1] = extensionDamageSummary[target][1]

def updateDamageSummary(damageSummary,target,damage):

    if (target in damageSummary):
        damageSummary[target][0] += damage
    else:
        damageSummary[target] = [damage,False]

def setDamageSummaryKilled(damageSummary,target):

    if (target in damageSummary):
        damageSummary[target][1] = True

def printDamageSummary(damageSummary):

    for target in damageSummary:
        if (damageSummary[target][0] != 0):
            if (damageSummary[target][1]):
                deadString = DnDUtil.getDeathText('(DEAD)')
            else:
                deadString = ""
            if (damageSummary[target][0] > 0):
                print(target, "took a total of", DnDUtil.getDamageText(damageSummary[target][0]), "damage!", deadString)
            else:
                print(target, "was healed a total of", DnDUtil.getHealText(-damageSummary[target][0]), "health!", deadString)

def getScrollSpellAtk(spellLevel):

    if (spellLevel < 0 or spellLevel > 9):
        DnDUtil.printWarning("Casting outside spell level range: spell level "+str(spellLevel))
        return 0
    elif (spellLevel <= 2):
        return 5
    elif (spellLevel <= 4):
        return 7
    elif (spellLevel <= 6):
        return 9
    elif (spellLevel <= 8):
        return 10
    else:
        return 11
    
def getScrollSpellDC(spellLevel):
    
    if (spellLevel < 0 or spellLevel > 9):
        DnDUtil.printWarning("Casting outside spell level range: spell level "+str(spellLevel))
        return 0
    elif (spellLevel <= 2):
        return 13
    elif (spellLevel <= 4):
        return 15
    elif (spellLevel <= 6):
        return 17
    elif (spellLevel <= 8):
        return 18
    else:
        return 19

def spellAttack(attacker,attackerData,defender,defenderData,atkBonus,playerActor,meleeAttack,spellLevel,spellName):

    if (not(attackerData is None)):
        attackAdvantage = getAttackAdvantage(attacker,attackerData,defender,defenderData,meleeAttack,False) or 'spellattacks' in attackerData['Advantages'] or 'incspellattacks' in defenderData['Advantages']
        attackDisadvantage = getAttackDisadvantage(attackerData,defender,defenderData,meleeAttack,False) or 'spellattacks' in attackerData['Disadvantages'] or 'incspellattacks' in defenderData['Disadvantages']
    else:
        attackAdvantage = False
        attackDisadvantage = False
         
    roll = ActorUtil.makeRoll(attacker,playerActor,attackAdvantage,attackDisadvantage,atkBonus,False,"Roll for spell attack")
    defense = getAC(defenderData)

    if (not(attackerData is None)):
        if (playerActor and PLAYERS_ADD_BONUS):
            if (roll == 100):
                roll = 20
            elif (roll >= 20):
                atkBonus += roll - 2
                roll = 2
            attack = roll + atkBonus
        else:
            attack = ActorUtil.applyBlessBane(attacker,attackerData,roll+atkBonus,defense)
    else:
        if (playerActor and PLAYERS_ADD_BONUS):
            if (roll == 100):
                roll = 20
            elif (roll >= 20):
                atkBonus += roll - 2
                roll = 2
        attack = roll + atkBonus

    if (applyMirrorImage(roll,attack,defender,defenderData,not('HP' in defenderData)) and (roll == 20 or roll != 1 and attack >= defense)):
        if (roll != 20 and 'ad' in defenderData['Misc'] and defense + 2 > attack and ActorUtil.canReact(defenderData) and DnDUtil.getAnswer('Use '+defender+'\'s reaction to use arcane deflection') == 'y'):
            print(defender, "uses its reaction to use arcane deflection and negate the attack!")
            defenderData['Reaction'] = False
            applyCC(defender,defender,defenderData,'arcane deflection')
            defenderData['Effects'].append([defender,'cc','arcane deflection',[],1.5])
            return 0
        elif (roll != 20 and 'shield' in defenderData['UseAbilities'] and defense + 5 > attack and ActorUtil.canReact(defenderData) and DnDUtil.getAnswer('Use '+defender+'\'s reaction to cast Shield') == 'y'):
            print(defender, "uses its reaction to cast Shield and block the attack!")
            defenderData['Reaction'] = False
            ability = defenderData['UseAbilities']['shield']
            useAbility(not('HP' in defenderData),'shield',ability['Type'],ability['Duration'],ability['Actions'],not('HP' in defenderData),[defender],defender,defenderData,defender,defenderData,ability['Attack Mod'],ability['Save'],ability['DC'],0,ability['Base Level'],ability['Base Level'],False,False,False,ability['Concentration?'],{})
            return 0

        print(attacker, "successfully", DnDUtil.getPassText('hits'), defender+'!')
        if (roll == 20 or roll >= 18 and spellName == 'bladeofdisaster' or meleeAttack and ActorUtil.hasStatus(defenderData,['paralysis','sleep','unconscious'])):
            if (ActorUtil.isImmuneToType(defenderData,['crit'])):
                print(defender, "can't be", DnDUtil.getFailText('crit')+'!')
                return 1
            else:
                return 2
        else:
            return 1
    else:
        if (PLAYERS_ADD_BONUS and playerActor):
            print(attacker, DnDUtil.getFailText('misses'), defender, "(AC", str(defense)+')')
        else:
            print(attacker, DnDUtil.getFailText('misses'), defender)
            print(attacker, "will need a roll of", defense - atkBonus, '('+str(defense)+')', "to hit", defender)
        return 0

def isConcentrating(actorData):

    return actorData['Concentration'] != []

def checkConcentration(actor,actorData,damage):

    if (isConcentrating(actorData) and damage > 0):
        # concentration check DC is equal to the higher of 10 and damage taken divided by 2
        if (damage <= 20):
            saveDC = 10
        else:
            saveDC = damage // 2

        print(actor, "must make a concentration check DC", saveDC, "to maintain a spell")

        if (makeSave(actor,actorData,'con',saveDC,['concentration']) == 0):
            print(actor, "maintains concentration on the spell")
        else:
            print(actor, "loses concentration on the spell!")
            dropConcentration(actor,actorData)

def dropConcentration(actor,actorData,hardDispel=False):

    for effect in actorData['Concentration']:
        target = effect[0]
        targetData = getData(target)
        if (not(targetData is None)):
            dispel(effect,actor,targetData,hardDispel)
        if (effect in actorData['Effects']):
            actorData['Effects'].remove(effect)
        else:
            DnDUtil.printWarning("Effect "+str(effect)+" present in concentration data, but not in effect data for "+actor)

    del actorData['Concentration'][:]

# return 0 if the save was made, otherwise, return the amount by which the save was failed
def makeSave(actor,actorData,saveType,dc,abilityTypes,saveAdvantage=False,saveDisadvantage=False):

    if (dc == 0):
        return 0
    print(actor, "must make a", saveType, "save DC", dc)

    if ((saveType == 'str' or saveType == 'dex') and ActorUtil.hasStatus(actorData,['stun','paralysis','petrification','sleep','unconscious'])):
        print(actor, "automatically", DnDUtil.getFailText('fails'), "the save due to stun/paralysis/petrification/sleep/unconscious!")
        return 1000

    playerActor = not('HP' in actorData)

    # ensure that all advantages and disadvantages that affect the next saving throw are consumed
    advantage = False
    if ('nextsave' in actorData['Advantages']):
        advantage = True
        actorData['Advantages'].remove('nextsave')
    if ('next'+saveType+'save' in actorData['Advantages']):
        advantage = True
        actorData['Advantages'].remove('next'+saveType+'save')
    for advantageType in [advantageType for advantageType in actorData['Advantages'] if len(advantageType) > 4 and advantageType[:4] == 'next' and advantageType[4:] in abilityTypes]:
        advantage = True
        actorData['Advantages'].remove(advantageType)
    disadvantage = False
    if ('nextsave' in actorData['Disadvantages']):
        disadvantage = True
        actorData['Disadvantages'].remove('nextsave')
    if ('next'+saveType+'save' in actorData['Disadvantages']):
        disadvantage = True
        actorData['Disadvantages'].remove('next'+saveType+'save')
    for disadvantageType in [disadvantageType for disadvantageType in actorData['Disadvantages'] if len(disadvantageType) > 4 and disadvantageType[:4] == 'next' and disadvantageType[4:] in abilityTypes]:
        disadvantage = True
        actorData['Disadvantages'].remove(disadvantageType)

    if (not(advantage)):
        advantage = saveAdvantage or 'saves' in actorData['Advantages'] or saveType+'saves' in actorData['Advantages'] or DnDUtil.haveCommonItem(actorData['Advantages'],abilityTypes)
    if (not(disadvantage)):
        disadvantage = saveDisadvantage or 'saves' in actorData['Disadvantages'] or saveType+'saves' in actorData['Disadvantages'] or DnDUtil.haveCommonItem(actorData['Disadvantages'],abilityTypes) or saveType == 'dex' and ActorUtil.hasStatus(actorData,['restrain','prestrain'])

    if (saveType == 'death'):
        if ('deathsave' in actorData['Misc']):
            saveBonus = actorData['Misc']['deathsave']
        else:
            saveBonus = 0
    else:
        saveBonus = actorData[saveType.capitalize()+'Save']
        if ('concentration' in abilityTypes and 'conc' in actorData['Misc']):
            saveBonus += actorData['Misc']['conc']

    roll = ActorUtil.makeRoll(actor,playerActor,advantage,disadvantage,saveBonus,False,'Make a '+saveType+' save')
    if (saveType == 'dex' and 'sm' in actorData['Misc'] and not(ActorUtil.hasStatus(actorData,['incapacitate'])) and DnDUtil.getAnswer('Does this effect specifically target only '+actor) == 'y'):
        saveBonus += actorData['Misc']['sm']
    if (playerActor and PLAYERS_ADD_BONUS):
        if (roll == 100):
            roll = 20
        elif (roll >= 20):
            saveBonus = roll - 2
            roll = 2
    result = roll + saveBonus

    if (ActorUtil.hasStatus(actorData,['mindsliver'])):
        if (not(playerActor)):
            mindSliverRoll = random.randint(1,4)
            print(actor, "rolls a", mindSliverRoll, "for mind sliver penalty")
        else:
            mindSliverRoll = DnDUtil.getInt(input('Roll for mind sliver penalty (1d4): '))
        result -= mindSliverRoll
        # remove all mind sliver effects on this actor
        i = 0
        while (i < len(actorData['Status'])):
            statusEffect = actorData['Status'][i]
            if (statusEffect[0] == 'mindsliver'):
                ownerData = getData(statusEffect[1])
                mindSliverEffects = getCCEffectsForTarget(ownerData,actor,'mindsliver')
                for effect in mindSliverEffects:
                    dispel(effect,statusEffect[1],actorData)
                    ownerData['Effects'].remove(effect)
                    if (effect in ownerData['Concentration']):
                        ownerData['Concentration'].remove(effect)
            else:
                i += 1

    hasBless = ActorUtil.hasStatus(actorData,['bless']) and (not(playerActor) or not(PLAYERS_ADD_BONUS))
    hasBane = ActorUtil.hasStatus(actorData,['bane']) and (not(playerActor) or not(PLAYERS_ADD_BONUS))
    
    # if we did not pass the save without evaluating extra bonuses, find all conscious allies with aura of protection, and order them based on aura value
    if (hasBane and not(hasBless) and result-4 < dc or result < dc and (not(hasBless) or result+1 < dc)):
        if (not(playerActor)):
            alliedDict = encounter
        else:
            alliedDict = playerData
        aopSources = []
        for ally in alliedDict:
            if ('aop' in alliedDict[ally]['Misc'] and not(ActorUtil.hasStatus(alliedDict[ally],['unconscious','sleep']))):
                aopValue = alliedDict[ally]['Misc']['aop']
                for i in range(0,len(aopSources)):
                    if (aopValue >= aopSources[i][1]):
                        aopSources.insert(i,[ally,aopValue])
                        break
                else:
                    aopSources.append([ally,aopValue])

        if (aopSources):
            # try to apply an aura of protection bonus first where it matters before moving on to bless bonuses
            for aopData in aopSources:
                aopSource = aopData[0]
                aopValue = aopData[1]
                if (not(hasBane) and (result+aopValue >= dc or hasBless and result+aopValue+4 >= dc) or hasBane and (hasBless and result+aopValue >= dc or not(hasBless) and result+aopValue-2 >= dc)):
                    if (actor == aopSource or DnDUtil.getAnswer('Is '+actor+' within 10ft of '+aopSource) == 'y'):
                        print(actor, "gains a +"+str(aopValue), "bonus from", aopSource+'\'s', "aura of protection")
                        result += aopValue
                        break
                # if the current aop bonus wasn't enough to make a difference, just exit the loop
                else:
                    break

        if (not(playerActor) or not(PLAYERS_ADD_BONUS)):
            result = ActorUtil.applyBlessBane(actor,actorData,result,dc)

    # check for arcane deflection first since it is the least expensive ability to use to recover from a failed saved
    if ('ad' in actorData['Misc'] and roll != 1 and result < dc and result + 4 >= dc and ActorUtil.canReact(actorData) and (autoBattle or DnDUtil.getAnswer('Use '+actor+'\'s reaction to use arcane deflection') == 'y')):
        actorData['Reaction'] = False
        applyCC(actor,actor,actorData,'arcane deflection')
        actorData['Effects'].append([actor,'cc','arcane deflection',[],1.5])
        result += 4
    # check for indomitable reroll so we can choose to use legendary resistance if we fail on the reroll
    elif ('indomitable' in actorData['Misc'] and actorData['Misc']['indomitable'] > 0 and (roll == 1 or result < dc) and (autoBattle or DnDUtil.getAnswer('Use indomitable to reroll this failed saving throw ('+str(actorData['Misc']['indomitable'])+' remaining)') == 'y')):
        actorData['Misc']['indomitable'] -= 1
        roll = ActorUtil.makeRoll(actor,playerActor,False,False,saveBonus,False,'Reroll the save')
        if (playerActor and PLAYERS_ADD_BONUS):
            if (roll == 100):
                roll = 20
            elif (roll >= 20):
                saveBonus = roll - 2
                roll = 2
        result = roll + saveBonus
        # if we did not pass the save without evaluating extra bonuses, find all conscious allies with aura of protection, and order them based on aura value
        if (hasBane and not(hasBless) and result-4 < dc or result < dc and (not(hasBless) or result+1 < dc)):
            if (playerActor):
                alliedDict = playerData
            else:
                alliedDict = encounter
            aopSources = []
            for ally in alliedDict:
                if ('aop' in alliedDict[ally]['Misc'] and not(ActorUtil.hasStatus(alliedDict[ally],['unconscious','sleep']))):
                    aopValue = alliedDict[ally]['Misc']['aop']
                    for i in range(0,len(aopSources)):
                        if (aopValue >= aopSources[i][1]):
                            aopSources.insert(i,[ally,aopValue])
                            break
                    else:
                        aopSources.append([ally,aopValue])

            if (aopSources):
                # try to apply an aura of protection bonus first where it matters before moving on to bless bonuses
                for aopData in aopSources:
                    aopSource = aopData[0]
                    aopValue = aopData[1]
                    if (not(hasBane) and (result+aopValue >= dc or hasBless and result+aopValue+4 >= dc) or hasBane and (hasBless and result+aopValue >= dc or not(hasBless) and result+aopValue-2 >= dc)):
                        if (actor == aopSource or DnDUtil.getAnswer('Is '+actor+' within 10ft of '+aopSource) == 'y'):
                            print(actor, "gains a +"+str(aopValue), "bonus from", aopSource+'\'s', "aura of protection")
                            result += aopValue
                            break
                    # if the current aop bonus wasn't enough to make a difference, just exit the loop
                    else:
                        break

        if (not(playerActor) or not(PLAYERS_ADD_BONUS)):
            result = ActorUtil.applyBlessBane(actor,actorData,result,dc)

    if (roll == 20 or roll != 1 and result >= dc):
        print(actor, DnDUtil.getPassText('passes'), "the save!")
        # give a special return value when rolling a 20 on a death save so we know to immediately clear the unconscious effect and allow the actor to take its turn
        if (saveType == 'death' and roll == 20):
            return -1
        return 0
    elif ('lresist' in actorData['Misc'] and actorData['Misc']['lresist'] > 0 and (autoBattle or DnDUtil.getAnswer('Use legendary resistance to pass this save ('+str(actorData['Misc']['lresist'])+' remaining)') == 'y')):
        actorData['Misc']['lresist'] -= 1
        print(actor, DnDUtil.getPassText('passes'), "due to legendary resistance!")
        print(actor, "has", actorData['Misc']['lresist'], "legendary resistances remaining")
        return 0
    else:
        print(actor, DnDUtil.getFailText('fails'), "the save")
        # handle the case where a natural 1 with high bonuses could have returned a value suggesting the save was made
        if (result >= dc):
            return 1
        else:
            return dc - result

def printMessage(msg):

    print("---------------------------------------------------------------------")
    print("MESSAGE:", msg)
    print("---------------------------------------------------------------------")

def createTriggerAbility(actorData,triggerAbilityName,triggerAbility,actor,playerActor,spellAtk,saveDC,spellLevel,actionData,actionData2):

    triggerAbility['Owner'] = actor
    triggerAbility['Player?'] = playerActor
    triggerAbility['Spell Atk'] = spellAtk
    triggerAbility['DC'] = saveDC
    triggerAbility['Spell Level'] = spellLevel
    triggerAbility['Actions'] = actionData
    if (actionData2):
        triggerAbility['Actions2'] = actionData2

    for existingTriggerAbilityName in triggerData:
        if (existingTriggerAbilityName == triggerAbilityName):
            sameAbility = True
            for abilityDataKey in triggerData[existingTriggerAbilityName]:
                if (abilityDataKey != 'Owner' and triggerData[existingTriggerAbilityName][abilityDataKey] != triggerAbility[abilityDataKey]):
                    sameAbility = False
                    break
            if (sameAbility):
                print("Trigger", triggerAbilityName, "was not created since an identical ability already exists (owned by", triggerData[triggerAbilityName]['Owner']+")!")
                return
            else:
                triggerAbilityName += '|'+actor
                if (existingTriggerAbilityName.find('|') == -1):
                    newTriggerName = existingTriggerAbilityName+'|'+triggerData[existingTriggerAbilityName]['Owner']
                    # since we are going to rename this trigger, we'll have to update its respective trigger ability
                    ownerData = getData(triggerData[existingTriggerAbilityName]['Owner'])
                    if (not(ownerData is None)):
                        for effect in ownerData['Effects']:
                            if (effect[1] == 'trigger'):
                                effect[2] = newTriggerName
                                break
                            elif (effect[1] == 'cc'):
                                for ccEffect in effect[3]:
                                    if (ccEffect[1] == 'trigger'):
                                        ccEffect[2] = newTriggerName
                                        break

                    triggerData[newTriggerName] = triggerData.pop(existingTriggerAbilityName)
                    
        elif (existingTriggerAbilityName.find('|')):
            parsedExistingTriggerAbilityName = existingTriggerAbilityName.split('|')
            if (parsedExistingTriggerAbilityName[0] == triggerAbilityName):
                if (parsedExistingTriggerAbilityName[1] == actor):
                    print("Trigger", triggerAbilityName, "was not created since an identical ability already exists (owned by", actor+")!")
                    return
                else:
                    triggerAbilityName += '|'+actor

    triggerData[triggerAbilityName] = triggerAbility
    triggerEffect = [actor,'trigger',triggerAbilityName,triggerData[triggerAbilityName],triggerAbility['Trigger Duration']]
    actorData['Effects'].append(triggerEffect)
    if (triggerAbility['Concentration?']):
        actorData['Concentration'].append(triggerEffect)
    print("Trigger", triggerAbilityName, "created!")

def usePassiveAbilities(actor,actorData,playerActor):

    if ('passive' in actorData['Misc']):
        passiveAbilities = actorData['Misc']['passive'].split(',')
        for passiveAbilityName in passiveAbilities:
            if (passiveAbilityName in actorData['UseAbilities']):
                passiveAbility = actorData['UseAbilities'][passiveAbilityName]
                if (not(passiveAbility['Concentration?']) or not(isConcentrating(actorData)) or DnDUtil.getAnswer(actor+" is concentrating on another spell. Drop concentration in favor of this spell") == 'y'):
                    if (passiveAbility['Concentration?'] and isConcentrating(actorData)):
                        for effect in actorData['Concentration']:
                            dispel(effect,actor,actorData)
                            if (effect in actorData['Effects']):
                                actorData['Effects'].remove(effect)
                            else:
                                DnDUtil.printWarning("Effect "+str(effect)+" present in concentration data, but not effect data for "+actor)

                        del actorData['Concentration'][:]

                    actionKey = 'Actions'
                    spellLevel = passiveAbility['Base Level']
                    if ('Scaled Actions' in passiveAbility and spellLevel > 0):
                        spellLevel = SpellUtil.inputSpellLevel(passiveAbilityName,spellLevel)
                        if (spellLevel > ability['Base Level']):
                            actionKey = 'Scaled Actions'
                    elif (spellLevel == 0 and 'Scaled Actions' in passiveAbility):
                        actionKey = 'Scaled Actions'

                    if (passiveAbility['Attack Mod']):
                        spellAtk = passiveAbility['Attack Mod']
                    else:
                        spellAtk = actorData['SpellAtk']

                    if (passiveAbility['DC'] == 0):
                        spellDC = actorData['SpellDC']
                    else:
                        spellDC = passiveAbility['DC']

                    actionData = deepcopy(passiveAbility[actionKey])
                    actionData = SpellUtil.replaceSpellMod(actionData,actorData)
                    actionData2 = []
                    if (actionKey == 'Scaled Actions'):
                        if (spellLevel != 0):
                            lvlReplacement = spellLevel-passiveAbility['Base Level']
                        else:
                            lvlReplacement = SpellUtil.getCantripModifierForActor(actor,actorData)
                        actionData = SpellUtil.replaceLvl(actionData,lvlReplacement)
                        if ('Scaled Actions2' in passiveAbility):
                            actionData2 = SpellUtil.replaceLvl(deepcopy(passiveAbility[actionKey+'2']),lvlReplacement)
                            actionData2 = SpellUtil.replaceSpellMod(actionData2,actorData)
                    elif ('Actions2' in passiveAbility):
                        actionData2 = deepcopy(passiveAbility['Actions2'])
                        actionData2 = SpellUtil.replaceSpellMod(actionData2,actorData)

                    if (passiveAbility['Trigger Duration']):
                        createTriggerAbility(actorData,passiveAbilityName,passiveAbility,actor,playerActor,spellAtk,spellDC,spellLevel,actionData,actionData2)
                    else:
                        useAbility(playerActor,passiveAbilityName,passiveAbility['Type'],passiveAbility['Duration'],actionData,playerActor,[actor],actor,actorData,actor,actorData,0,'',0,0,passiveAbility['Base Level'],spellLevel,False,False,False,passiveAbility['Concentration?'],{})
            else:
                DnDUtil.printError("Ability "+passiveAbilityName+" marked as passive but this ability was not found in the Use Abilities")


def useAbility(playerTurn,abilityName,abilityTypes,abilityDuration,actions,playerTarget,targets,target,targetData,actor,actorData,spellAtk,saveType,saveDC,saveDiff,baseLevel,spellLevel,half,crit,uncannyDodge,concentration,savedDamageRolls):

    returnDamageSummary = {}
    abilityEffects = []
    clearCondition = ''
    threeSaveClear = False
    escapeDC = 0
    # we want to ensure that the cc effect created by the container is placed before any other cc effects caused by this ability
    containerStatusEffectIndex = len(targetData['Status'])
    if (abilityDuration == 'targetstart' or abilityDuration == 'targetend'):
        clearCondition = abilityDuration
        abilityDuration = 1
    i = 0
    while (i < len(actions)):
        action = actions[i]
        actionType = action[0]
        numArgs = len(action)

        if (actionType == 'damage' or actionType == 'idamage' or actionType == 'lifesteal' or actionType == 'ilifesteal' or actionType == 'halfsteal' or actionType == 'ihalfsteal' or actionType == 'soulharvest' or actionType == 'isoulharvest'):
            if (numArgs >= 2):
                parsedDamage = DnDUtil.parseDamageCalculation(action[1])
                damageTypes = action[2:]
                if ('spell' in abilityTypes):
                    damageTypes.append(['spell'])
                if ('magic' in abilityTypes and not('nonmagic' in damageTypes)):
                    damageTypes.append(['magic'])
                if (damageTypes and damageTypes[0] in savedDamageRolls or not(damageTypes) and '' in savedDamageRolls):
                    if (damageTypes):
                        baseDamage = savedDamageRolls[damageTypes[0]]
                    else:
                        baseDamage = savedDamageRolls['']
                else:
                    if (action[1].isdigit()):
                        baseDamage = int(action[1])
                    elif (playerTurn):
                        baseDamage = DnDUtil.getInt(input("Roll for "+abilityName+" damage ("+parsedDamage[0]+"): "))
                    else:
                        baseDamage = DnDUtil.calculate(parsedDamage[0])
                    if (damageTypes):
                        savedDamageRolls[damageTypes[0]] = baseDamage
                    else:
                        savedDamageRolls[''] = baseDamage

                damage = baseDamage + parsedDamage[1]
                if (crit and (not(playerTurn) or not(PLAYERS_ADD_BONUS))):
                    damage += baseDamage
                damage = getNetDamage(damage,actorData,target,targetData,damageTypes,abilityName,False,uncannyDodge)
                if (half):
                    damage /= 2

                if (damage > 0):
                    if (damageTypes):
                        print(target, "takes", DnDUtil.getDamageText(damage), damageTypes[0], "damage from", abilityName)
                    else:
                        print(target, "takes", DnDUtil.getDamageText(damage), "damage from", abilityName)
                    killed = applyDamage(target,targetData,damage,damageTypes,crit)
                    updateDamageSummary(returnDamageSummary,target,damage)
                    # re-evaluate whether it's a player's turn since we could have dropped concentration on a spell that mind-controlled the current actor
                    if ('HP' in actorData):
                        playerTurn = False
                    else:
                        playerTurn = True
                    # same logic for the target
                    if ('HP' in targetData):
                        playerTarget = False
                    else:
                        playerTarget = True
                else:
                    killed = False

                if (actionType.find('lifesteal') != -1):
                    if ('dol' in actorData['Misc'] and spellLevel >= 1):
                        healBonus = 2 + spellLevel
                        print(abilityName, "will heal for an additional", healBonus, "hp due to", actor+"'s disciple of life!")
                    else:
                        healBonus = 0
                    healAmount = heal(actor,actorData,damage+healBonus)
                    updateDamageSummary(returnDamageSummary,actor,-healAmount)
                elif (actionType.find('halfsteal') != -1):
                    if ('dol' in actorData['Misc'] and spellLevel >= 1):
                        healBonus = 2 + spellLevel
                        print(abilityName, "will heal for an additional", healBonus, "hp due to", actor+"'s disciple of life!")
                    else:
                        healBonus = 0
                    healAmount = heal(actor,actorData,damage // 2 + healBonus)
                    updateDamageSummary(returnDamageSummary,actor,-healAmount)
                elif (actionType.find('soulharvest') != -1):
                    if (setTempHP(actor,actorData,damage)):
                        abilityEffects.append([actor,'temphp',damage])
                # wait until after actor has been healed to check if the target died from failed death saves caused by this damage
                if (killed):
                    setDamageSummaryKilled(returnDamageSummary,target)
                    return returnDamageSummary

                if (actionType[0] == 'i'):
                    if (not(playerTarget)):
                        targetData['MaxHP'] -= damage
                    printMessage(target+'\'s max hp is also reduced by '+str(damage))
                    abilityEffects.append([target,'buff','hp',-damage])

                if (not(playerTarget) and damage > 0):
                    dealDamage(target,targetData,damage)
                    if (checkKilled(target,targetData,damage,damageTypes,crit)):
                        print(target, DnDUtil.getDeathText('dies'), "to", abilityName+'!')
                        kill(target)
                        setDamageSummaryKilled(returnDamageSummary,target)
                        return returnDamageSummary
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'heal'):
            if (numArgs == 2):
                if (DnDUtil.haveCommonItem(targetData['Type'],['undead','construct'])):
                    print(target, "is", DnDUtil.getFailText('immune'), "to being healed!")
                else:
                    if ('bh' in actorData['Misc'] and not('heal' in savedDamageRolls) and spellLevel >= 1):
                        selfHeal = 2 + spellLevel
                        # trigger blessed hands healing as long as we're healing another target with this ability
                        if (target != actor or target == actor and len(targets) > 1):
                            print(abilityName, "heals", actor, "for", selfHeal, "hp due to", actor+"'s blessed healer!")
                            selfHealAmount = heal(actor,actorData,selfHeal)
                            updateDamageSummary(returnDamageSummary,actor,-selfHealAmount)
                    if ('dol' in actorData['Misc'] and not('heal' in savedDamageRolls) and spellLevel >= 1):
                        healBonus = 2 + spellLevel
                        print(abilityName, "will heal for an additional", healBonus, "hp due to", actor+"'s disciple of life!")
                    else:
                        healBonus = 0
                    if (action[1].isdigit()):
                        amount = int(action[1]) + healBonus
                    elif (ActorUtil.hasStatus(targetData,['beaconofhope'])):
                        print(target, "will receive max healing since it is affected by beacon of hope!")
                        amount = DnDUtil.maxCalculate(action[1]) + healBonus
                    elif ('heal' in savedDamageRolls):
                        amount = savedDamageRolls['heal']
                    elif (playerTurn):
                        amount = DnDUtil.getInt(input("Roll for healing ("+action[1]+"): ")) + healBonus
                        savedDamageRolls['heal'] = amount
                    else:
                        amount = DnDUtil.calculate(action[1]) + healBonus
                        savedDamageRolls['heal'] = amount
                    healAmount = heal(target,targetData,amount)
                    updateDamageSummary(returnDamageSummary,target,-healAmount)
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'temphp'):
            if (numArgs == 2):
                if (action[1].isdigit()):
                    tempHP = int(action[1])
                elif (playerTurn):
                    tempHP = DnDUtil.getInt(input("Roll for temporary hp ("+action[1]+"): "))
                else:
                    tempHP = DnDUtil.calculate(action[1])

                if (setTempHP(target,targetData,tempHP)):
                    abilityEffects.append([target,'temphp',tempHP])
            else:
                 print("Invalid number of arguments for action", actionType)

        elif (actionType == 'kill'):
            if (numArgs == 1):
                if (ActorUtil.isImmuneToType(targetData,['death'])):
                    print(target, "is", DnDUtil.getFailText('immune'), "to insta-kill effects!")
                else:
                    print(target, "is instantly", DnDUtil.getDeathText('killed'), "by", abilityName+'!')
                    if (not(playerTarget)):
                        kill(target)
                    setDamageSummaryKilled(returnDamageSummary,target)
                    return returnDamageSummary
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'cc'):
            if (numArgs == 2 or numArgs == 3):
                type = action[1]
                if (ActorUtil.isImmuneToType(targetData,[type])):
                    print(target, "is", DnDUtil.getFailText('immune'), "to the cc type", type+'!')
                else:
                    if (numArgs == 3):
                        if (action[2].isdigit()):
                            duration = int(action[2])
                        elif (action[2] == 'actorstart'):
                            duration = 1
                        elif (action[2] == 'actorend'):
                            duration = 1.5
                        elif (action[2] == 'targetstart' or action[2] == 'targetend'):
                            duration = 1
                            clearTiming = action[2]
                            if (clearCondition and clearCondition != clearTiming):
                                DnDUtil.printWarning("Attempting to overwrite previously given clear condition of "+clearCondition+" with "+clearTiming+"! Defaulting to original clear condition")
                            else:
                                clearCondition = clearTiming
                        elif (playerTurn):
                            duration = DnDUtil.getInt(input("Roll for duration ("+action[2]+"): "))
                        else:
                            duration = DnDUtil.calculate(action[2])
                        if (abilityDuration and abilityDuration != duration):
                            DnDUtil.printWarning("Attempting to overwrite previously given ability duration of "+str(abilityDuration)+" with cc duration of "+str(duration)+"! Defaulting to original duration")
                            duration = abilityDuration
                        else:
                            abilityDuration = duration
                    else:
                        if (abilityDuration):
                            duration = abilityDuration
                        else:
                            duration = -1
                            abilityDuration = -1
                    # don't apply the cc if it's the name of the ability since the container will do this job anyway
                    if (type != abilityName):
                        applyCC(actor,target,targetData,type)
                    abilityEffects.append([target,'cc',type,[]])
                    print(target, "will be under the effect of", DnDUtil.getStatusText(type), "for", duration, "turns")
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'ccsave' or actionType == 'ccsave3'):
            if (numArgs == 3 or numArgs == 4):
                type = action[1]
                if (ActorUtil.isImmuneToType(targetData,[type])):
                    print(target, "is", DnDUtil.getFailText('immune'), "to the cc type", type+'!')
                else:
                    if (numArgs == 4):
                        if (action[3].isdigit()):
                            duration = int(action[3])
                        elif (action[3] == 'actorstart'):
                            duration = 1
                        elif (action[3] == 'actorend'):
                            duration = 1.5
                        elif (action[2] == 'targetstart' or action[2] == 'targetend'):
                            duration = 1
                            clearTiming = action[2]
                            if (clearCondition and clearCondition != clearTiming):
                                DnDUtil.printWarning("Attempting to overwrite previously given clear condition of "+clearCondition+" with "+clearTiming+"! Defaulting to original clear condition")
                            else:
                                clearCondition = clearTiming
                        elif (playerTurn):
                            duration = DnDUtil.getInt(input("Roll for duration ("+action[3]+"): "))
                        else:
                            duration = DnDUtil.calculate(action[3])
                        if (abilityDuration and abilityDuration != duration):
                            DnDUtil.printWarning("Attempting to overwrite previously given ability duration of "+str(abilityDuration)+" with cc duration of "+str(duration)+"! Defaulting to original duration")
                            duration = abilityDuration
                        else:
                            abilityDuration = duration
                    else:
                        if (abilityDuration):
                            duration = abilityDuration
                        else:
                            duration = -1
                            abilityDuration = -1

                    clearTiming = action[2]
                    if (actionType == 'ccsave'):
                        threeSaveClearAction = False
                    else:
                        threeSaveClearAction = True
                    if (clearCondition):
                        if (clearCondition != clearTiming):
                            DnDUtil.printWarning("Attempting to overwrite previously given clear condition of "+clearCondition+" with "+clearTiming+"! Defaulting to original clear condition")
                        elif (threeSaveClear != threeSaveClearAction):
                            DnDUtil.printWarning("Attempting to overwrite previously given threeSaveClear value of "+str(threeSaveClear)+" with "+str(threeSaveClearAction)+"! Defaulting to original value")
                    else:
                        clearCondition = clearTiming
                        threeSaveClear = threeSaveClearAction
                    # don't apply the cc if it's the name of the ability since the container will do this job anyway
                    if (type != abilityName):
                        applyCC(actor,target,targetData,type)
                    abilityEffects.append([target,'cc',type,[]])
                    print(target, "will be under the effect of", DnDUtil.getStatusText(type), "for", duration, "turns")
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'buff' or actionType == 'debuff' or actionType == 'drain'):
            if (numArgs == 3):
                type = action[1]
                if (action[2].isdigit()):
                    amount = int(action[2])
                elif (playerTurn):
                    amount = DnDUtil.getInt(input("Roll for amount: ("+action[2]+"): "))
                else:
                    amount = DnDUtil.calculate(action[2])

                if (actionType == 'buff'):
                    buff(target,targetData,type,amount)
                    abilityEffects.append([target,'buff',type,amount])
                    print(target, type, "increases by", amount)
                elif (actionType == 'debuff'):
                    buff(target,targetData,type,-amount)
                    abilityEffects.append([target,'buff',type,-amount])
                    print(target, type, "decreases by", amount)
                else:
                    buff(target,targetData,type,-amount)
                    buff(target,actorData,type,amount)
                    abilityEffects.append([target,'buff',type,-amount])
                    abilityEffects.append([actor,'buff',type,amount])
                    print(actor, "drains", amount, type, "from target")
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'move'):
            if (numArgs == 2 or numArgs == 3):
                oldMoveDict = copy(targetData['Move'])
                if (numArgs == 2):
                    moveDelta = action[1]
                    if (moveDelta.isdigit()):
                        moveDelta = int(moveDelta)
                        print(target, "has increased its move speed by", moveDelta)
                        for moveType in targetData['Move']:
                            if (targetData['Move'][moveType] > 0):
                                targetData['Move'][moveType] += moveDelta
                    elif (moveDelta == 'double'):
                        print(target, "has doubled its move speed!")
                        for moveType in targetData['Move']:
                            if (targetData['Move'][moveType] > 0):
                                targetData['Move'][moveType] *= 2
                    elif (moveDelta == 'half'):
                        print(target, "has halved its move speed!")
                        for moveType in targetData['Move']:
                            if (targetData['Move'][moveType] > 0):
                                targetData['Move'][moveType] /= 2
                    else:
                        DnDUtil.printError("Unknown move delta "+moveDelta+" valid deltas are double, half, and any integer")
                else:
                    moveType = action[1].capitalize()
                    if (moveType in targetData['Move']):
                        if (action[2] == 'same'):
                            moveValue = targetData['Move']['Ground']
                        else:
                            moveValue = int(action[2])
                        targetData['Move'][moveType] = moveValue
                        print(target+'\'s', moveType, "speed has been set to", moveValue)
                    else:
                        DnDUtil.printError("Invalid movement type "+ moveType+" valid movement types are ground, fly, climb, swim, and burrow")
                abilityEffects.append([target,'move',oldMoveDict])
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'immobilize'):
            if (numArgs == 1):
                oldMoveDict = copy(targetData['Move'])
                for moveType in targetData['Move']:
                    targetData['Move'][moveType] = 0
                abilityEffects.append([target,'move',oldMoveDict])
                print(target, "is immobilized!")
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'grapple'):
            if (numArgs == 1 or numArgs == 2):
                if (ActorUtil.isImmuneToType(targetData,['grapple'])):
                    print(target, "is", DnDUtil.getFailText('immune'), "to being grappled!")
                    return returnDamageSummary
                else:
                    if (clearCondition):
                        DnDUtil.printWarning("Attempting to overwrite previously given clear condition of "+clearCondition+" with escape! The grapple will not be applied!")
                    elif (clearCondition == 'escape'):
                        DnDUtil.printWarning("A grapple action has already been given for this ability!")
                    elif (abilityName.find("On Hit Ability") != -1):
                        # make sure we wouldn't exceed our grab limit with this grapple
                        if ('grablimit' in actorData['Misc']):
                            grabLimit = actorData['Misc']['grablimit']
                            grabCount = 0
                            for effect in actorData['Effects']:
                                if (effect[1] == 'grapple' and effect[2]):
                                    grabCount += 1
                            if (grabCount >= grabLimit):
                                print(actor, "is unable to grab", target, "since its grab limit has already been reached")
                                return returnDamageSummary
                        # make sure we aren't already grabbing target with this attack
                        duplicateGrab = False
                        if (abilityName[-2].isdigit() and abilityName[-1].isdigit()):
                            atkIndex1 = int(abilityName[-2])
                            atkIndex2 = int(abilityName[-1])
                            for effect in actorData['Effects']:
                                if (effect[0] == target and effect[1] == 'grapple' and effect[2] == [atkIndex1,atkIndex2]):
                                    duplicateGrab = True
                                    break
                        else:
                            DnDUtil.printError("Invalid on hit ability name "+abilityName+"! Expected name to end with at least 2 digits")
                            return returnDamageSummary

                        if (not(duplicateGrab)):
                            # if this is a valid grapple, mark it as our clear condition along with the escape DC
                            clearCondition = 'escape'
                            if (numArgs == 2):
                                escapeDC = int(action[1])
                            abilityDuration = -1
                    # if this isn't a grab and we aren't already grappling target, mark this as a valid grapple
                    elif (not(isGrappling(actorData,target))):
                        clearCondition = 'escape'
                        if (numArgs == 2):
                            escapeDC = int(action[1])
                        abilityDuration = -1
                    else:
                        print(actor, "is already grappling", target+'!')
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'attack'):
            if (numArgs == 3):
                rangeIndex = int(action[1])
                atkIndex = int(action[2])
                atkType = 'm' if rangeIndex == 0 else 'r'
                if (playerTurn):
                    roll = DnDUtil.getInt(input('Roll for attack: '))
                else:
                    roll = -1
                attackDamageSummary = attack(actor,actorData,target,atkType,rangeIndex,atkIndex,roll,True)
                extendDamageSummary(returnDamageSummary,attackDamageSummary)
            else:
                print("Invalid number of arguments for action", actionType)
                
        elif (actionType == 'summon'):
            if (numArgs == 2 or numArgs == 3):
                creatureTypes = []
                creatureType = action[1]
                if (numArgs == 3):
                    if (action[2].isdigit()):
                        number = int(action[2])
                    elif (playerTurn):
                        number = DnDUtil.getInt(input("Roll for number of summons ("+action[2]+"): "))
                    else:
                        number = DnDUtil.calculate(action[2])
                elif (creatureType != 'input'):
                    DnDUtil.printError("Not enough arguments for a non-input creature type! Converting to input")
                    creatureType = 'input'

                if (creatureType != 'input'):
                    creatureTypes.append([creatureType,number])
                else:
                    done = False
                    while (not(done)):
                        summonInput = input('Enter the creature to summon followed by the number (press enter to exit): ').split()
                        if (len(summonInput) == 2):
                            creatureTypes.append([summonInput[0],DnDUtil.getInt(summonInput[1])])
                        elif (len(summonInput) == 0):
                            done = True
                        
                for creatureAdd in creatureTypes:
                    creatureType = creatureAdd[0]
                    number = creatureAdd[1]
                    names = add(creatureType,number,not(playerTurn))
                    for name in names:
                        newCreatureData = getData(name)
                        initRoll = ActorUtil.makeRoll(name,playerTurn,DnDUtil.haveCommonItem(['init','dex','checks'],newCreatureData['Advantages']),DnDUtil.haveCommonItem(['init','dex','checks'],newCreatureData['Disadvantages']),newCreatureData['Init'],True,'Roll for initiative')
                        if (ActorUtil.hasStatus(newCreatureData,['giftofalacrity'])):
                            if (not(playerTurn)):
                                goaRoll = random.randint(1,8)
                                print(name, "rolls a", goaRoll, "for gift of alacrity bonus")
                            else:
                                goaRoll = DnDUtil.getInt(input('Roll for gift of alacrity bonus (1d8): '))
                            initRoll += goaRoll
                        newCreatureData['InitRoll'] = initRoll
                        insertNewActor(name,newCreatureData)
                        abilityEffects.append([name,'summon'])
                        # set target and targetData to the summon in case we need to modify it through this spell
                        target = name
                        targetData = newCreatureData
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'immunity'):
            if (numArgs >= 2):
                immunityTypes = action[1:]
                for immunityType in immunityTypes:
                    addImmunity(targetData,immunityType)
                    print(target, "now has", immunityType, "immunity!")
                    abilityEffects.append([target,'immunity',immunityType])
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'mc'):
            if (numArgs == 1):
                mindControl(target)
                targetData = getData(target)
                if (target == actor):
                    actorData = targetData
                abilityEffects.append([target,'mc'])
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'ss'):
            if (numArgs == 2):
                oldType = targetData['Base']
                if (action[1] == 'input'):
                    newType = input('What will '+target+' shapeshift into? ')
                else:
                    newType = action[1]
                shapeShift(target,targetData,newType)
                abilityEffects.append([target,'ss',oldType])
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'dot'):
            if (numArgs >= 3):
                dotTypeIndex = 3
                dotDamage = action[1]
                dotTiming = action[2]
                if (numArgs >= 6 and (action[5] == 'negates' or action[5] == 'half')):
                    dotTypeIndex = 6
                    if (action[4] == 'dc'):
                        dotSave = [action[3],saveDC,action[5]]
                    elif (not(action[4].isdigit())):
                        DnDUtil.printError("A save was given for this dot ability, but no DC was found")
                        dotSave = []
                    else:
                        dotSave = [action[3],int(action[4]),action[5]]
                else:
                    dotSave = []
                dotTypes = action[dotTypeIndex:]
                
                print("A DoT has been applied to", target)
                if (dotTiming == 'targetstart' or dotTiming == 'targetend'):
                    targetData['Status'].append(['dot',actor,dotTiming,dotSave,dotDamage,playerTurn,dotTypes])
                abilityEffects.append([target,'dot',dotTiming,dotSave,dotDamage,playerTurn,dotTypes])
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'wound'):
            if (numArgs == 2 or numArgs == 3):
                if (not(DnDUtil.haveCommonItem(targetData['Type'],['undead','construct']))):
                    woundDamage = action[1]
                    if (ActorUtil.hasStatus(targetData,['wound'])):
                        for j in range(0,len(targetData['Status'])):
                            statusEffect = targetData['Status'][j]
                            if (statusEffect[0] == 'wound'):
                                statusEffect[2] = DnDUtil.simplifyCalculation(statusEffect[2]+'+'+woundDamage)
                                print(target+"'s", "wound has opened further!", "("+statusEffect[2]+")")
                                break
                    else:
                        if (numArgs == 3):
                            woundDC = int(action[2])
                        else:
                            woundDC = saveDC

                        targetData['Status'].append(['wound',actor,woundDamage,playerTurn,woundDC])
                        abilityEffects.append([target,'wound'])
                        print(target, "is now wounded!")
                else:
                    print(target, "is not wounded because it is an undead or construct!")
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'resist'):
             if (numArgs >= 2):
                resistanceTypes = action[1:]
                for resistanceType in resistanceTypes:
                    addResistance(targetData,resistanceType)
                    print(target, "now has", resistanceType, "resistance")
                    abilityEffects.append([target,'resist',resistanceType])
             else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'vulnerability'):
            if (numArgs >= 2):
                vulnerabilityTypes = action[1:]
                for vulnerabilityType in vulnerabilityTypes:
                    addVulnerability(targetData,vulnerabilityType)
                    print(target, "now has", vulnerabilityType, "vulnerability!")
                    abilityEffects.append([target,'vulnerability',vulnerabilityType])
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'adv'):
            if (numArgs >= 2):
                advantageTypes = action[1:]
                for advantageType in advantageTypes:
                    addAdvantage(targetData,advantageType)
                    print(target, "now has advantage on", advantageType)
                    abilityEffects.append([target,'adv',advantageType])
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'dis'):
            if (numArgs >= 2):
                disadvantageTypes = action[1:]
                for disadvantageType in disadvantageTypes:
                    addDisadvantage(targetData,disadvantageType)
                    print(target, "now has disadvantage on", disadvantageType)
                    abilityEffects.append([target,'dis',disadvantageType])
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'react'):
            if (numArgs == 1):
                targetData['CanReact'] = False
                abilityEffects.append([target,'react'])
                print(target, "can't take reactions for", abilityDuration, "turns!")
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'prone'):
            if (numArgs == 1):
                knockProne(target,targetData)
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'misc'):
            if (numArgs >= 3):
                miscStat = action[1]
                miscArg = ''
                for arg in action[2:]:
                    miscArg += arg+','
                miscArg = miscArg[:-1]
                if (addMiscStat(target,targetData,miscStat,miscArg)):
                    print(target, "now has the misc stat", miscStat, "with argument", miscArg)
                    abilityEffects.append([target,'misc',miscStat,targetData['Misc'][miscStat]])
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'bonusattack'):
            if (numArgs == 1):
                addAttack(targetData)
                abilityEffects.append([target,'bonusattack'])
                print(target, "can make an extra attack!")
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'use' or actionType == 'useon'):
            if (numArgs == 2):
                secondaryAbilityName = action[1]
                if (secondaryAbilityName in actorData['UseAbilities']):
                    secondaryAbility = actorData['UseAbilities'][secondaryAbilityName]
                else:
                    secondaryAbility = ImportUtil.loadAbilityData(secondaryAbilityName,[''],True)
                if (secondaryAbility):
                    if (secondaryAbility['Actions'] == [['']]):
                        print("Ability", secondaryAbilityName, "not found!")
                    else:
                        if ('Scaled Actions' in secondaryAbility and (spellLevel > baseLevel or secondaryAbility['Base Level'] == 0)):
                            secondaryActionKey = 'Scaled Actions'
                        else:
                            secondaryActionKey = 'Actions'

                        secondaryActionData = secondaryAbility[secondaryActionKey]
                        secondaryActionData = SpellUtil.replaceSpellMod(secondaryActionData,actorData)
                        secondaryActionData2 = []
                        if (secondaryActionKey == 'Scaled Actions'):
                            if (spellLevel != 0):
                                lvlReplacement = spellLevel-baseLevel
                            else:
                                lvlReplacement = SpellUtil.getCantripModifierForActor(actor,actorData)
                            secondaryActionData = SpellUtil.replaceLvl(secondaryActionData,lvlReplacement)
                            if ('Scaled Actions2' in secondaryAbility):
                                secondaryActionData2 = SpellUtil.replaceLvl(deepcopy(secondaryAbility[secondaryActionKey+'2']),lvlReplacement)
                                secondaryActionData2 = SpellUtil.replaceSpellMod(secondaryActionData2,actorData)
                        elif ('Actions2' in secondaryAbility):
                            secondaryActionData2 = deepcopy(secondaryAbility['Actions2'])
                            secondaryActionData2 = SpellUtil.replaceSpellMod(secondaryActionData2,actorData)

                        currentSecondaryActionData = secondaryActionData

                        if (spellAtk):
                            secondarySpellAtk = spellAtk
                        else:
                            secondarySpellAtk = actorData['SpellAtk']

                        if (saveDC == 0):
                            secondarySaveDC = actorData['SpellDC']
                        else:
                            secondarySaveDC = saveDC
                    
                        if (secondaryAbility['Trigger Duration']):
                            createTriggerAbility(actorData,secondaryAbilityName,secondaryAbility,actor,playerTurn,secondarySpellAtk,secondarySaveDC,spellLevel,secondaryActionData,secondaryActionData2)
                        else:
                            if (actionType == 'useon'):
                                done = False
                                secondaryTargets = getTargets(actor,playerTurn,'Choose all targets for '+secondaryAbilityName)
                            else:
                                secondaryTargets = [target]

                            secondarySavedDamageRolls = {}
                            for secondaryTarget in secondaryTargets:
                                secondaryTargetData = getData(secondaryTarget)
                                secondaryPlayerTarget = not('HP' in secondaryTargetData)
                                if (ActorUtil.isImmuneToType(secondaryTargetData,secondaryAbility['Type'])):
                                    print(secondaryTarget, "is", DnDUtil.getFailText('immune'), "to", secondaryAbilityName)
                                elif ('Immune' in secondaryAbility['Target Type Mods'] and DnDUtil.haveCommonItem(secondaryAbility['Target Type Mods']['Immune'],secondaryTargetData['Type'])):
                                    print(secondaryTarget, "is", DnDUtil.getFailText('immune'), "to", secondaryAbilityName, "since it is one of these types:", secondaryAbility['Target Type Mods']['Immune'])
                                elif ('Required' in secondaryAbility['Target Type Mods'] and not(DnDUtil.haveCommonItem(secondaryAbility['Target Type Mods']['Required'],secondaryTargetData['Type']))):
                                    print(secondaryTarget, "is", DnDUtil.getFailText('immune'), "to", secondaryAbilityName, "since it is NOT one of these types:", secondaryAbility['Target Type Mods']['Required'])
                                else:
                                    secondaryHalf = False
                                    secondarySuccess = True
                                    if (secondaryAbility['Save'] and secondaryAbility['Save Result'] != 'none'):
                                        secondarySaveDiff = makeSave(secondaryTarget,secondaryTargetData,secondaryAbility['Save'],secondarySaveDC,secondaryAbility['Type'],'Advantage' in secondaryAbility['Target Type Mods'] and DnDUtil.haveCommonItem(secondaryAbility['Target Type Mods']['Advantage'],secondaryTargetData['Type']),'Disadvantage' in secondaryAbility['Target Type Mods'] and DnDUtil.haveCommonItem(secondaryAbility['Target Type Mods']['Disadvantage'],secondaryTargetData['Type']) or 'enemy'+secondaryAbility['Save']+'saves' in actorData['Disadvantages'])
                                        if (secondarySaveDiff == 0):
                                            if (secondaryAbility['Save Result'] == 'negates'):
                                                if (secondaryActionData2):
                                                    currentSecondaryActionData = secondaryActionData2
                                                else:
                                                    print(secondaryTarget, "is unaffected by", secondaryAbilityName)
                                                    secondarySuccess = False
                                            elif (secondaryAbility['Save Result'] == 'half'):
                                                if ('avoidance' in secondaryTargetData['Misc'] or 'evasion' in secondaryTargetData['Misc'] and secondaryAbility['Save'] == 'dex' or ActorUtil.hasStatus(secondaryTargetData,['circleofpower']) and DnDUtil.haveCommonItem(secondaryAbility['Type'],['magic','spell']) or checkShieldMaster(secondaryTarget,secondaryTargetData,secondaryAbility['Save'])):
                                                    print(secondaryTarget, "avoids all damage due to evasion/avoidance/circle of power/shield master")
                                                    secondarySuccess = False
                                                else:
                                                    if (secondaryActionData2):
                                                        currentSecondaryActionData = secondaryActionData2
                                                    print(secondaryTarget, "will take half damage from", secondaryAbilityName)
                                                    secondaryHalf = True
                                        else:
                                            if (secondaryAbility['Save Result'] == 'half' and ('avoidance' in secondaryTargetData['Misc'] or 'evasion' in secondaryTargetData['Misc'] and secondaryAbility['Save'] == 'dex')):
                                                print(secondaryTarget, "will take half damage due to evasion/avoidance")
                                                secondaryHalf = True
                                    else:
                                        secondarySaveDiff = -1
                                    if (secondarySuccess):
                                        abilityDamageSummary = useAbility(playerTurn,secondaryAbilityName,secondaryAbility['Type'],secondaryAbility['Duration'],currentSecondaryActionData,secondaryPlayerTarget,secondaryTargets,secondaryTarget,secondaryTargetData,actor,actorData,secondarySpellAtk,secondaryAbility['Save'],secondarySaveDC,secondarySaveDiff,secondaryAbility['Base Level'],spellLevel,secondaryHalf,crit,uncannyDodge,secondaryAbility['Concentration?'],secondarySavedDamageRolls)
                                        extendDamageSummary(returnDamageSummary,abilityDamageSummary)
                                        if (not(secondaryPlayerTarget) and not(secondaryTarget in encounter)):
                                            return returnDamageSummary
                                        if (not(secondaryAbility['Static Damage?'])):
                                            secondarySavedDamageRolls.clear()
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'onhit'):
            if (numArgs == 2 or numArgs == 3):
                onHitAbilityName = action[1]
                if (onHitAbilityName in actorData['ExtraOnHitAbilities']):
                    print(actor, "already has this on-hit ability!")
                else:
                    onHitAbilityActions = ''
                    # if this on-hit ability is in the actor's use abilities, use the actions listed there instead of those in the ability data file
                    if (onHitAbilityName in actorData['UseAbilities']):
                        for action in actorData['UseAbilities'][onHitAbilityName]['Actions']:
                            for actionArg in action:
                                onHitAbilityActions += actionArg+','
                            onHitAbilityActions = onHitAbilityActions[:-1]
                            onHitAbilityActions += ';'
                        onHitAbilityActions = onHitAbilityActions[:-1]
                        if ('Actions2' in actorData['UseAbilities'][onHitAbilityName]):
                            onHitAbilityActions += ':'
                            for action in actorData['UseAbilities'][onHitAbilityName]['Actions2']:
                                for actionArg in action:
                                    onHitAbilityActions += actionArg+','
                                onHitAbilityActions = onHitAbilityActions[:-1]
                                onHitAbilityActions += ';'
                            onHitAbilityActions = onHitAbilityActions[:-1]
                    onHitAbility = ImportUtil.loadAbilityData(onHitAbilityName,onHitAbilityActions.split(':'),False)
                    if (onHitAbility['Actions'] == [['']]):
                        print("Ability", onHitAbilityName, "not found!")
                    else:
                        onHitAbility['Spell Level'] = spellLevel
                        # strip unneeded data for an on-hit ability
                        del onHitAbility['Use Turn?']
                        del onHitAbility['Static Damage?']
                        del onHitAbility['Trigger Duration']
                        if ('spell' in onHitAbility['Type']):
                            onHitAbility['Type'].remove('spell')
                        # convert attack to trigger condition since this will be our hit condition
                        onHitAbility['Trigger Condition'] = onHitAbility.pop('Attack')
                        # use spellDC as the DC in case the ability needs one
                        onHitAbility['DC'] = saveDC

                        if ('Scaled Actions' in onHitAbility and (spellLevel > baseLevel or onHitAbility['Base Level'] == 0)):
                            onHitActionKey = 'Scaled Actions'
                        else:
                            onHitActionKey = 'Actions'

                        onHitActionData = onHitAbility[onHitActionKey]
                        onHitActionData = SpellUtil.replaceSpellMod(onHitActionData,actorData)
                        onHitActionData2 = []
                        if (onHitActionKey == 'Scaled Actions'):
                            if (spellLevel != 0):
                                lvlReplacement = spellLevel-baseLevel
                            else:
                                lvlReplacement = SpellUtil.getCantripModifierForActor(actor,actorData)
                            onHitActionData = SpellUtil.replaceLvl(onHitActionData,lvlReplacement)
                            if ('Scaled Actions2' in onHitAbility):
                                onHitActionData2 = SpellUtil.replaceLvl(deepcopy(onHitAbility[onHitActionKey+'2']),lvlReplacement)
                                onHitActionData2 = SpellUtil.replaceSpellMod(onHitActionData2,actorData)
                        elif ('Actions2' in onHitAbility):
                            onHitActionData2 = deepcopy(onHitAbility['Actions2'])
                            onHitActionData2 = SpellUtil.replaceSpellMod(onHitActionData2,actorData)

                        onHitAbility['Actions'] = onHitActionData
                        if (onHitActionData2):
                            onHitAbility['Actions2'] = onHitActionData2
                        # delete scaling data since we've already scaled the action, and on-hit abilities are not dynamic
                        if ('Scaled Actions' in onHitAbility):
                            del onHitAbility['Scaled Actions']
                        if ('Scaled Actions2' in onHitAbility):
                            del onHitAbility['Scaled Actions2']

                        if (numArgs == 3):
                            charges = int(action[2])
                        else:
                            charges = -1

                        onHitAbility['Charges'] = charges
                        targetData['ExtraOnHitAbilities'][onHitAbilityName] = onHitAbility
                        abilityEffects.append([target,'onhit',onHitAbilityName,onHitAbility])
                        print(target, "has gained the on-hit ability", onHitAbilityName)
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'magicweapon'):
            if (numArgs == 2):
                # automatically enchant the melee weapon if no ranged weapon exists
                if (len(targetData['Atk']) == 1):
                    rangeIndex = 0
                else:
                    choice = DnDUtil.chooseOption('Choose which weapon to enchant',['melee','ranged'])
                    rangeIndex = choice-1
                magicBonus = DnDUtil.getInt(action[1])
                # a weapon cannot be enchanted past +3
                if (magicBonus > 3):
                    magicBonus = 3

                if (playerTarget and PLAYERS_ADD_BONUS):
                    bonusDelta = 0
                else:
                    # if the weapon at this index is magical, get its magic bonus and take the difference as the buff unless it is already equal to or greater than the bonus this effect provides
                    if ('magic' in targetData['WeaponTypes'][rangeIndex][0][0]):
                        currentMagicBonus = -1
                        while (currentMagicBonus < 0 or currentMagicBonus > 3):
                            currentMagicBonus = DnDUtil.getInt(input('What is this weapon\'s current magic bonus? '))
                        bonusDelta = magicBonus - currentMagicBonus
                    else:
                        bonusDelta = magicBonus

                if (bonusDelta < 0):
                    print("This weapon already has a magic bonus higher than or equal to what the spell provides!")
                elif (bonusDelta > 0 or bonusDelta == 0 and not('magic' in targetData['WeaponTypes']) or playerTarget and PLAYERS_ADD_BONUS):
                    addMagicBonus(targetData,rangeIndex,bonusDelta)
                    abilityEffects.append([target,'magicweapon',rangeIndex,bonusDelta])
                    print(target, "now has a +"+str(magicBonus), "magic weapon!")
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'magicweapons'):
            if (numArgs == 1):
                addMagicBonus(targetData,0,0)
                abilityEffects.append([target,'magicweapon',0,0])
                if (len(targetData['Atk']) > 1):
                    addMagicBonus(targetData,1,0)
                    abilityEffects.append([target,'magicweapon',1,0])
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'msg'):
            if (numArgs == 2):
                msg = action[1]
                msg = msg.replace('actor',actor).replace('target',target)
                printMessage(msg)
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'script'):
            if (numArgs == 1 or numArgs == 2):
                if (numArgs == 2):
                    scriptAbilityName = action[1]
                else:
                    scriptAbilityName = abilityName

                scriptArgs = [playerTurn,scriptAbilityName,abilityTypes,abilityDuration,copy(actions),playerTarget,targets,target,targetData,actor,actorData,spellAtk,saveType,saveDC,saveDiff,baseLevel,spellLevel,half,crit,uncannyDodge,concentration,savedDamageRolls,abilityEffects]
                Spells.useAbility(scriptArgs)
                # overwrite the current ability arguments using the values from the script
                playerTurn = scriptArgs[0]
                scriptAbilityName = scriptArgs[1]
                abilityTypes = scriptArgs[2]
                abilityDuration = scriptArgs[3]
                actions = scriptArgs[4]
                playerTarget = scriptArgs[5]
                # no need to copy targets since it can already be easily modified within the script
                target = scriptArgs[7]
                targetData = scriptArgs[8]
                actor = scriptArgs[9]
                actorData = scriptArgs[10]
                spellAtk = scriptArgs[11]
                saveType = scriptArgs[12]
                saveDC = scriptArgs[13]
                saveDiff = scriptArgs[14]
                baseLevel = scriptArgs[15]
                spellLevel = scriptArgs[16]
                half = scriptArgs[17]
                crit = scriptArgs[18]
                uncannyDodge = scriptArgs[19]
                concentration = scriptArgs[20]
                # no need to copy savedDamageRolls since it can already be easily modified within the script
                # no need to copy abilityEffects since it can already be easily modified within the script
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == 'addtarget'):
            if (numArgs == 1 or numArgs == 2):
                if (numArgs == 2):
                    numExtraTargets = int(action[1])
                else:
                    numExtraTargets = 1

                for j in range(0,numExtraTargets):
                    validTarget = False
                    while (not(validTarget)):
                        rawInput = input('Input additional target for '+abilityName+': ')
                        if (rawInput):
                            newTarget = autoComplete(rawInput,False)
                            if (newTarget):
                                validTarget = True
                                targets.append(newTarget)
                            else:
                                print("Invalid target -", rawInput)
                        else:
                            validTarget = True
            else:
                print("Invalid number of arguments for action", actionType)

        elif (actionType == ''):
            return returnDamageSummary

        else:
            print("Invalid action type", actionType)
        i += 1

    if (abilityDuration or abilityEffects):
        if (not(abilityDuration)):
            abilityDuration = -1
        # prevent duplicate cc effects from arising due to the creation of the ability container effect
        if (clearCondition != 'escape'):
            i = 0
            while (i < len(abilityEffects)):
                abilityEffect = abilityEffects[i]
                if (abilityEffect[1] == 'cc' and abilityEffect[2] == abilityName):
                    abilityEffects.remove(abilityEffect)
                else:
                    i += 1
        # if we summoned anything using this ability, restore the target back to the actor so the effects are put in the proper location
        if (any(len(action) > 0 and action[0] == 'summon' for action in actions)):
            target = actor
            targetData = actorData

        if (clearCondition):
            if (clearCondition == 'escape'):
                containerStatusEffect = startGrapple(actor,actorData,target,targetData,escapeDC,abilityEffects)
                grappleIndices = []
                if (abilityName.find("On Hit Ability") != -1):
                    if (abilityName[-2].isdigit() and abilityName[-1].isdigit()):
                        grappleIndices = [int(abilityName[-2]),int(abilityName[-1])]
                    else:
                        DnDUtil.printError("Invalid on hit ability name "+abilityName+"! Expected name to end with at least 2 digits")
                abilityEffectsContainer = [target,'grapple',grappleIndices,abilityEffects,-1]
            else:
                containerStatusEffect = applyCC(actor,target,targetData,abilityName,copy(abilityTypes),saveType,saveDC,clearCondition,threeSaveClear)
                abilityEffectsContainer = [target,'cc',abilityName,abilityEffects,abilityDuration]
        else:
            containerStatusEffect = applyCC(actor,target,targetData,abilityName)
            abilityEffectsContainer = [target,'cc',abilityName,abilityEffects,abilityDuration]
        # insert the container status effect BEFORE any other cc's that might have been added as a result of this ability
        targetData['Status'].remove(containerStatusEffect)
        targetData['Status'].insert(containerStatusEffectIndex,containerStatusEffect)
        actorData['Effects'].append(abilityEffectsContainer)
        if (concentration):
            actorData['Concentration'].append(abilityEffectsContainer)

    return returnDamageSummary

def add(type,number,addEnemy):

    names = []        
                    
    if (addEnemy):
        data = encounter
    else:
        data = playerData

    if (type in data):
        if (addEnemy):
            name = type+'1'
        else:
            name = input("What would you like to name your "+type+"? ")
        while (name in turnOrder):
            name = input("This name already exists! Choose a new name for "+name+": ")
        data[name] = data.pop(type)
        turnOrder[turnOrder.index(type)] += '1'
        for j in range(2,number+2):
            if (addEnemy):
                name = type+str(j)
            else:
                name = input("What would you like to name your "+type+"? ")
            while (name in turnOrder):
                name = input("This name already exists! Choose a new name for "+name+": ")
            creatureData = getCreatureData(type)
            if (not(creatureData)):
                print("Creature not found.")
                return names
            if (not(addEnemy)):
                convertData(creatureData)
            usePassiveAbilities(name,creatureData,not(addEnemy))
            data[name] = creatureData
            print(name, "added")
            names.append(name)
    else:
        j = 1
        while (number > 0 and j < 10000):
            if (addEnemy):
                name = type+str(j)
            else:
                name = input("What would you like to name your "+type+"? ")
            if (not(name in data)):
                while (name in turnOrder):
                    name = input("This name already exists! Choose a new name for "+name+": ")
                creatureData = getCreatureData(type)
                if (not(creatureData)):
                    print("Creature not found.")
                    return names
                if (not(addEnemy)):
                    convertData(creatureData)
                usePassiveAbilities(name,creatureData,not(addEnemy))
                data[name] = creatureData
                print(name, "added")
                names.append(name)
                number -= 1
            j += 1

    return names

def insertNewActor(newActor,newActorData):

    global actorIndex
    initRoll = newActorData['InitRoll']
    added = False
    for i in range(0,len(turnOrder)):
        actor = turnOrder[i]
        actorData = getData(actor)
        if (initRoll > actorData['InitRoll'] or initRoll == actorData['InitRoll'] and newActorData['Init'] > actorData['Init']):
            added = True
            turnOrder.insert(i,newActor)
            if (i <= actorIndex):
                actorIndex += 1
            break

    if (not(added)):
        turnOrder.append(newActor)

def grapple(grappleOwner,grappleOwnerData,escapeDC,grappleTarget,grappleTargetData,playerGrappleOwner,playerGrappleTarget):

    if (escapeDC == 0):
        ownerResult = ActorUtil.makeCheck(grappleOwner,grappleOwnerData,playerGrappleOwner,'athletics','grapple' in grappleOwnerData['Advantages'],'grapple' in grappleOwnerData['Disadvantages'])
    else:
        ownerResult = escapeDC

    targetResult = ActorUtil.makeCheck(grappleTarget,grappleTargetData,playerGrappleTarget,'athletics/acrobatics','escape' in grappleOwnerData['Advantages'],'escape' in grappleOwnerData['Disadvantages'])

    if (escapeDC == 0):
        print(grappleOwner, "result is", ownerResult)
    else:
        print("DC to escape is", escapeDC)

    print(grappleTarget, "result is", targetResult)

    if (escapeDC != 0):
        if (targetResult >= escapeDC):
            print(grappleTarget, DnDUtil.getPassText('escapes'), "the grapple!")
            return grappleTarget
        else:
            print(grappleOwner, DnDUtil.getFailText('maintains'), "its grapple")
            return grappleOwner
    else:
        if (ownerResult > targetResult):
            print(grappleOwner, "wins")
            return grappleOwner
        elif (targetResult > ownerResult):
            print(grappleTarget, "wins")
            return grappleTarget
        else:
            print("It's a tie, try again.")
            return grapple(grappleOwner,grappleOwnerData,escapeDC,grappleTarget,grappleTargetData,playerGrappleOwner,playerGrappleTarget)

def startGrapple(grappleOwner,grappleOwnerData,grappleTarget,grappleTargetData,escapeDC,grappleEffects):

    print(grappleOwner, "is now", DnDUtil.getStatusText('grappling'), grappleTarget)
    grappleStatusEffect = ['grapple',grappleOwner,escapeDC]
    grappleTargetData['Status'].append(grappleStatusEffect)

    oldMoveDict = copy(grappleTargetData['Move'])
    for moveType in grappleTargetData['Move']:
        grappleTargetData['Move'][moveType] = 0
    grappleEffects.append([grappleTarget,'move',oldMoveDict,-1])

    if ('igrapple' in grappleOwnerData['Misc']):
        if (ActorUtil.isImmuneToType(grappleTargetData,'restrain')):
            print(grappleTarget, "is", DnDUtil.getFailText('immune'), "to being restrained!")
        else:
            print(grappleTarget, "is", DnDUtil.getStatusText('restrained'), "by this grapple!")
            grappleEffects.append([grappleTarget,'cc','restrain',[]])
            grappleTargetData['Status'].append(['restrain',grappleOwner,'',0,'',False,0,0])

    return grappleStatusEffect

def isGrappling(actorData,target):

    for effect in actorData['Effects']:
        if (effect[0] == target and effect[1] == 'grapple'):
            return True

    return False

def breakGrapple(grappleOwner,grappleOwnerData,grappleTarget,grappleTargetData):

    grappleEffects = None
    for effect in grappleOwnerData['Effects']:
        if (effect[1] == 'grapple' and effect[0] == grappleTarget):
            removeCCEffect(grappleTargetData,'grapple',grappleOwner)
            grappleOwnerData['Effects'].remove(effect)
            for grappleEffect in effect[3]:
                dispel(grappleEffect,grappleOwner,grappleTargetData)
            print(grappleOwner, "is no longer", DnDUtil.getStatusText('grappling'), grappleTarget)
            return
    
    DnDUtil.printWarning("Attempted to remove grapple on "+grappleTarget+" from "+grappleOwner+", but no grapple effect was found")

def shove(actor,actorData,playerActor,target,targetData,playerTarget):

    if (actorData['SizeMod'] - targetData['SizeMod'] >= -1):
        actorResult = ActorUtil.makeCheck(actor,actorData,playerActor,'athletics')
        targetResult = ActorUtil.makeCheck(target,targetData,playerTarget,'athletics/acrobatics')
        print(actor, "result is", actorResult)
        print(target, "result is", targetResult)
        if (actorResult > targetResult):
            print(actor, DnDUtil.getPassText('wins')+'!')
            if (autoBattle):
                option = 1
            else:
                option = DnDUtil.chooseOption('Choose an effect for shoving',['Knock '+target+' prone','Shove '+target+' up to '+str(5+5*((actorResult-targetResult) // 5))+' feet'])
            if (option == 1):
                knockProne(target,targetData)
            else:
                print(target, "is pushed back up to", 5+5*((actorResult-targetResult) // 5), "feet")
        elif (actorResult < targetResult):
            print(target, "wins. Shove attempt", DnDUtil.getFailText('unsuccessful'))
        else:
            print("It's a tie! Try again.")
            shove(actor,actorData,playerActor,target,targetData,playerTarget)
    else:
        print(target, "is", DnDUtil.getFailText("too large"), "for", actor, "to shove!")

def chooseAttackTarget(actor,actorData,defaultTarget,rangeIndex,atkIndex1,atkIndex2):

    if (rangeIndex != 0):
        return defaultTarget

    grabCount = 0
    currentGrabTargets = []
    for effect in actorData['Effects']:
        if (effect[1] == 'grapple' and effect[2]):
            grabCount += 1
            if ('grablimit' in actorData['Misc'] and effect[2][0] == atkIndex1 and effect[2][1] == atkIndex2):
                currentGrabTargets.append(effect[0])
            elif (effect[2][0] == atkIndex1 and effect[2][1] == atkIndex2):
                print(actor, "will use this attack on its grappled target")
                return effect[0]
            
    if (currentGrabTargets):
        if (grabCount >= actorData['Misc']['grablimit']):
            print(actor, "will use this attack on a grappled target since it has reached its grab limit")
            if (autoBattle):
                option = 1
            else:
                option = DnDUtil.chooseOption('Which grappled opponent to attack?',currentGrabTargets)
            return currentGrabTargets[option-1]
        elif (defaultTarget in currentGrabTargets):
            newTarget = input('Choose a new target for '+actor+' to grab with this attack (press enter to attack the grappled target): ')
            if (newTarget):
                while (True):
                    newTarget = autoComplete(newTarget,False)
                    if (newTarget):
                        return newTarget
                    newTarget = input('Choose a new target for '+actor+' to grab with this attack (press enter to attack the grappled target): ')
                    if (newTarget == ''):
                        return defaultTarget
        else:
            return defaultTarget

    return defaultTarget

def applyEffect(effect,owner,target,targetData):

    type = effect[1]
    if (type == 'cc'):
        applyCC(owner,target,targetData,effect[2])
        if (effect[3]):
            for ccEffect in effect[3]:
                applyEffect(ccEffect,owner,target,targetData)
    elif (type == 'buff'):
        buff(target,targetData,effect[2],effect[3])
    elif (type == 'move'):
        oldMoveDict = targetData['Move']
        targetData['Move'] = effect[2]
        effect[2] = oldMoveDict
    elif (type == 'temphp'):
        setTempHP(target,targetData,effect[2])
    elif (type == 'resist'):
        addResistance(targetData,effect[2])
    elif (type == 'vulnerability'):
        addVulnerability(targetData,effect[2])
    elif (type == 'adv'):
        addAdvantage(targetData,effect[2])
    elif (type == 'dis'):
        addDisadvantage(targetData,effect[2])
    elif (type == 'misc'):
        addMiscStat(target,targetData,effect[2],effect[3])
    elif (type == 'trigger'):
        triggerData[effect[2]] = effect[3]
    elif (type == 'onhit'):
        targetData['ExtraOnHitAbilities'][effect[2]] = effect[3]
    elif (type == 'magicweapon'):
        addMagicBonus(targetData,effect[2],effect[3])
    elif (type == 'immunity'):
        addImmunity(targetData,effect[2])
    elif (type == 'react'):
        targetData['CanReact'] = False
    elif (type == 'mc'):
        mindControl(target)
    elif (type == 'ss'):
        oldType = targetData['Base']
        shapeShift(target,targetData,effect[2])
        effect[2] = oldType
    elif (type == 'bonusattack'):
        addAttack(targetData)
    elif (type == 'script'):
        # we assume that the owner of any script effect is the target
        scriptArgs = [not('HP' in targetData),effect[2],[],-1,[],not('HP' in targetData),[target],target,targetData,target,targetData,'',0,0,-2,-2,False,False,False,False,{effect[2]: effect[3]},[]]
        Spells.useAbility(scriptArgs)

def dispel(effect,owner,targetData,hardDispel=False):
    
    target = effect[0]
    type = effect[1]
    if (type == 'buff'):
        buff(target,targetData,effect[2],-effect[3])
    elif (type == 'temphp'):
        clearTempHP(targetData)
    elif (type == 'resist'):
        removeResistance(targetData,effect[2])
    elif (type == 'vulnerability'):
        removeVulnerability(targetData,effect[2])
    elif (type == 'adv'):
        removeAdvantage(targetData,effect[2])
    elif (type == 'dis'):
        removeDisadvantage(targetData,effect[2])
    elif (type == 'misc'):
        removeMiscStat(targetData,effect[2])
    elif (type == 'immunity'):
        removeImmunity(targetData,effect[2])
    elif (type == 'react'):
        targetData['CanReact'] = True
    elif (type == 'dot'):
        if (effect[2] == 'targetstart' or effect[2] == 'targetend'):
            removeCCEffect(targetData,'dot',owner)
        print(target, "is", DnDUtil.getPassText('freed'), "of the DoT effect")
    elif (type == 'wound'):
        removeCCEffect(targetData,'wound',owner)
        print(target, "is no longer wounded")
    elif (type == 'cc'):
        removeCCEffect(targetData,effect[2],owner)
        for extraEffect in effect[3]:
            if (extraEffect[0] != target):
                target = extraEffect[0]
                targetData = getData(target)
                if (targetData is None):
                    break
            dispel(extraEffect,owner,targetData,hardDispel)
            if (hardDispel and not(target in turnOrder)):
                break
        print(target, "is", DnDUtil.getPassText('freed'), "of the effects of", DnDUtil.getStatusText(effect[2]))
    elif (type == 'move'):
        targetData['Move'] = effect[2]
    elif (type == 'grapple'):
        breakGrapple(owner,getData(owner),target,targetData)
    elif (type == 'mc'):
        if (hardDispel):
            mindControl(target)
        else:
            print("The effect has been removed, please use the mc command to reverse the mc effect on", target)
    elif (type == 'summon'):
        if (hardDispel):
            kill(target)
        else:
            print("The effect has been removed, please use the kill command to kill", target)
    elif (type == 'ss'):
        shapeShift(target,targetData,effect[2])
    elif (type == 'bonusattack'):
        removeAttack(targetData)
    elif (type == 'trigger'):
        del triggerData[effect[2]]
        print("The trigger", effect[2], "has been removed")
    elif (type == 'onhit'):
        if (effect[2] in targetData['ExtraOnHitAbilities']):
            del targetData['ExtraOnHitAbilities'][effect[2]]
    elif (type == 'magicweapon'):
        removeMagicBonus(targetData,effect[2],effect[3])
    elif (type == 'script'):
        DnDUtil.printWarning("Removing script effect will likely result in inaccurate data for this actor upon reloading encounter")
    else:
        print("Unknown effect type", type, "has been removed")
    
def getSizeMod(size):
    
    if (size == 'medium' or size == ''):
        return 0
    elif (size == 'large'):
        return 1
    elif (size == 'small'):
        return -1
    elif (size == 'huge'):
        return 2
    elif (size == 'tiny'):
        return -2
    elif (size == 'gargantuan'):
        return 3
    elif (size == 'diminutive'):
        return -3
    elif (size == 'colossal'):
        return 4
    elif (size == 'fine'):
        return -4
    else:
        DnDUtil.printError("Illegal size "+size)
        return 0
    
def getSizeClass(sizeMod):

    if (sizeMod == 0):
        return 'medium'
    elif (sizeMod == 1):
        return 'large'
    elif (sizeMod == -1):
        return 'small'
    elif (sizeMod == 2):
        return 'huge'
    elif (sizeMod == -2):
        return 'tiny'
    elif (sizeMod == 3):
        return 'gargantuan'
    elif (sizeMod == -3):
        return 'diminutive'
    elif (sizeMod == 4):
        return 'colossal'
    elif (sizeMod == -4):
        return 'fine'
    else:
        DnDUtil.printError("Illegal size mod "+str(sizeMod))
        return 'Unknown'

def kill(target):
    global actorIndex

    index = turnOrder.index(target)
    if (index != len(turnOrder)-1):
        nextActor = turnOrder[index+1]
    else:
        nextActor = turnOrder[0]

    nextActorData = getData(nextActor)
    targetData = getData(target)
    dropConcentration(target,targetData)
    useDeathBurst(target,targetData)

    # if this creature owned a lair, kill the lair as well
    if ('lair' in turnOrder and target != 'lair' and targetData['Base'] == getData('lair')['Base']):
        kill('lair')
        print(target+'\'s', "lair is no longer active!")

    i = 0
    while (i < len(targetData['Effects'])):
        effect = targetData['Effects'][i]
        if (effect[1] == 'grapple'):
            grappleTargetData = getData(effect[0])
            if (not(grappleTargetData is None)):
                breakGrapple(target,targetData,effect[0],grappleTargetData)
            else:
                i += 1
        else:
            if (index == actorIndex and effect[-1] != -1):
                effect[-1] += 1
            if (effect[1] == 'cc' or effect[1] == 'dot' or effect[1] == 'wound'):
                ccTargetData = getData(effect[0])
                if (not(ccTargetData is None)):
                    for j in range(0,len(ccTargetData['Status'])):
                        if ((effect[1] == 'cc' and ccTargetData['Status'][j][0] == effect[2] or effect[1] != 'cc' and ccTargetData['Status'][j][0] == effect[1]) and ccTargetData['Status'][j][1] == target):
                            ccTargetData['Status'][j][1] = nextActor
                            break
            nextActorData['Effects'].append(effect)
            i += 1

    # if this creature was a small or medium beast or humanoid check for fungal infestation
    if (DnDUtil.haveCommonItem(['beast','humanoid'],targetData['Type']) and (targetData['Size'] == 'small' or targetData['Size'] == 'medium')):
        for data in [playerData,encounter]:
            for actor in data:
                actorData = data[actor]
                if ('fi' in actorData['Misc'] and ActorUtil.canReact(actorData)):
                    playerActor = not('HP' in actorData)
                    if (not(playerActor) and DnDUtil.getAnswer('Is '+target+' within 10ft of '+actor) == 'y' or playerActor and DnDUtil.getAnswer('Is '+target+' within 10ft of '+actor+' and use reaction for fungal infestation') == 'y'):
                        actorData['Reaction'] = False
                        names = add('zombie',1,not(playerActor))
                        for name in names:
                            newCreatureData = getData(name)
                            newCreatureData['InitRoll'] = actorData['InitRoll']
                            newCreatureData['Init'] = -100
                            if (not(playerActor)):
                                newCreatureData['HP'] = 1
                            insertNewActor(name,newCreatureData)
                        break

    if (target in encounter):
        del encounter[target]
    else:
        del playerData[target]

    if (index <= actorIndex):
        actorIndex -= 1
    turnOrder.remove(target)

def useDeathBurst(actor,actorData):

    if (not('db' in actorData['Misc'])):
        return

    print(actor+'\'s', "death burst activates!")
    deathBurstName = actorData['Misc']['db']

    if (not(deathBurstName in actorData['UseAbilities'])):
        DnDUtil.printError(actor+" was indicated to have a death burst ability named "+deathBurstName+" but this ability was not found")
        option = DnDUtil.chooseOption('Which ability is the death burst ability?',list(actorData['UseAbilities'].keys()),True)
        if (option > len(actorData['UseAbilities'])):
            return
        deathBurstName = list(actorData['UseAbilities'].keys())[option-1]

    playerActor = not('HP' in actorData)
    if (autoBattle):
        numTargets = random.randint(1,3)
        targets = []
        for i in range(0,numTargets):
            targets.append(getRandomTarget(actor))
    else:
        targets = getTargets(actor,playerActor,'Choose targets for this death burst')
    ability = actorData['UseAbilities'][deathBurstName]
    actionData = ability['Actions']
    if ('Actions2' in ability):
        actionData2 = ability['Actions2']
    else:
        actionData2 = {}

    # we assume that a death burst ability does not have these things:
    # - Level scaling
    # - Attack to hit
    # - A trigger duration
    # - Counterspell susceptibility
    # - A Save DC that relies on the actor's spell DC
    savedDamageRolls = {}
    abilityDamageSummary = {}

    for target in targets:
        targetData = getData(target)
        if ('HP' in targetData):
            playerTarget = False
        else:
            playerTarget = True
                                 
        if (ActorUtil.isImmuneToType(targetData,ability['Type'])):
            print(target, "is", DnDUtil.getFailText('immune'), "to", deathBurstName)
        elif ('Immune' in ability['Target Type Mods'] and DnDUtil.haveCommonItem(ability['Target Type Mods']['Immune'],targetData['Type'])):
            print(target, "is", DnDUtil.getFailText('immune'), "to", abilityName, "since it is one of these types:", ability['Target Type Mods']['Immune'])
        elif ('Required' in ability['Target Type Mods'] and not(DnDUtil.haveCommonItem(ability['Target Type Mods']['Required'],targetData['Type']))):
            print(target, "is", DnDUtil.getFailText('immune'), "to", abilityName, "since it is NOT one of these types:", ability['Target Type Mods']['Required'])
        else:
            success = True                       
            half = False
            currentActionData = actionData

            if (ability['Save'] and ability['Save Result'] != 'none'):
                saveDiff = makeSave(target,targetData,ability['Save'],ability['DC'],ability['Type'],'Advantage' in ability['Target Type Mods'] and DnDUtil.haveCommonItem(ability['Target Type Mods']['Advantage'],targetData['Type']),'Disadvantage' in ability['Target Type Mods'] and DnDUtil.haveCommonItem(ability['Target Type Mods']['Disadvantage'],targetData['Type']) or 'enemy'+ability['Save']+'saves' in actorData['Disadvantages'])
                if (saveDiff == 0):
                    if (ability['Save Result'] == 'negates'):
                        if (actionData2):
                            currentActionData = actionData2
                        else:
                            print(target, "is unaffected by", deathBurstName)
                            success = False
                    elif (ability['Save Result'] == 'half'):
                        if ('avoidance' in targetData['Misc'] or 'evasion' in targetData['Misc'] and ability['Save'] == 'dex' or ActorUtil.hasStatus(targetData,['circleofpower']) and DnDUtil.haveCommonItem(ability['Type'],['magic','spell']) or checkShieldMaster(target,targetData,ability['Save'])):
                            print(target, "avoids all damage due to evasion/avoidance/circle of power/shield master")
                            success = False
                        else:
                            if (actionData2):
                                currentActionData = actionData2
                            print(target, "will take half damage from", deathBurstName)
                            half = True
                else:
                    if (ability['Save Result'] == 'half' and ('avoidance' in targetData['Misc'] or 'evasion' in targetData['Misc'] and ability['Save'] == 'dex')):
                        print(target, "will take half damage due to evasion/avoidance")
                        half = True
            else:
                saveDiff = -1

            if (success):
                damageSummary = useAbility(playerActor,deathBurstName,ability['Type'],ability['Duration'],currentActionData,playerTarget,targets,target,targetData,actor,actorData,ability['Attack Mod'],ability['Save'],ability['DC'],saveDiff,ability['Base Level'],ability['Base Level'],half,False,False,ability['Concentration?'],savedDamageRolls)
                extendDamageSummary(abilityDamageSummary,damageSummary)
                if (not(ability['Static Damage?'])):
                    savedDamageRolls.clear()
    printDamageSummary(abilityDamageSummary)

def buff(target,targetData,type,value):

    # if players add bonus and we are buffing a player, do not modify stats that a player would be adding
    if (PLAYERS_ADD_BONUS and not('HP' in targetData)):
        if (type.endswith('saves') or type.endswith('atk') or type.endswith('dmg') or type in ['str','dex','con','int','wis','cha']):
            return True

    if (type == 'ac'):
        targetData['AC'] += value
    elif (type == 'str'): 
        if (value%2 == 0):
            value /= 2
        else:
            roll = random.randint(0,1)
            value += 2*roll - 1

        rangeIndices = []
        if (not('mdex' in targetData['Misc'])):
            rangeIndices.append(0)
        if ('rstr' in targetData['Misc']):
            rangeIndices.append(1)

        for rangeIndex in rangeIndices:
            if (rangeIndex < len(targetData['Atk'])):
                for i in range(0,len(targetData['Atk'][rangeIndex])):
                    for j in range(0,len(targetData['Atk'][rangeIndex][i])):
                        targetData['Atk'][rangeIndex][i][j] += value
    elif (type == 'dex'):
        if (value%2 == 0):
            value /= 2
        else:
            roll = random.randint(0,1)
            value += 2*roll - 1
        targetData['AC'] += value
        targetData['DexSave'] += value
        targetData['Init'] += value
        
        rangeIndices = []
        if ('mdex' in targetData['Misc']):
            rangeIndices.append(0)
        if (not('rstr' in targetData['Misc'])):
            rangeIndices.append(1)

        for rangeIndex in rangeIndices:
            if (rangeIndex < len(targetData['Atk'])): 
                for i in range(0,len(targetData['Atk'][rangeIndex])):
                    for j in range(0,len(targetData['Atk'][rangeIndex][i])):
                        targetData['Atk'][rangeIndex][i][j] += value
    elif (type in ['con','int','wis','cha']):
        if (value%2 == 0):
            value /= 2
        else:
            roll = random.randint(0,1)
            value += 2*roll - 1
        targetData[type.capitalize()+'Save'] += value
    elif (type == 'atk'):
        for i in range(0,len(targetData['Atk'])):
            for j in range(0,len(targetData['Atk'][i])):
                for k in range(0,len(targetData['Atk'][i][j])):
                    targetData['Atk'][i][j][k] += value
    elif (type == 'matk'):
        for i in range(0,len(targetData['Atk'][0])):
            for j in range(0,len(targetData['Atk'][0][i])):
                targetData['Atk'][0][i][j] += value
    elif (type == 'ratk'):
        if (len(targetData['Atk']) > 1):
            for i in range(0,len(targetData['Atk'][1])):
                for j in range(0,len(targetData['Atk'][1][i])):
                    targetData['Atk'][1][i][j] += value
    elif (type == 'dmg'):
        for i in range(0,len(targetData['DmgBonus'])):
            for j in range(0,len(targetData['DmgBonus'][i])):
                for k in range(0,len(targetData['DmgBonus'][i][j])):
                    targetData['DmgBonus'][i][j][k] += value
    elif (type == 'mdmg'):
        for i in range(0,len(targetData['DmgBonus'][0])):
            for j in range(0,len(targetData['DmgBonus'][0][i])):
                targetData['DmgBonus'][0][i][j] += value
    elif (type == 'rdmg'):
        if (len(targetData['DmgBonus']) > 1):
            for i in range(0,len(targetData['DmgBonus'][1])):
                for j in range(0,len(targetData['DmgBonus'][1][i])):
                    targetData['DmgBonus'][1][i][j] += value
    elif (type == 'hp'):
        if ('HP' in targetData):
            targetData['MaxHP'] += value
            targetData['HP'] += value
            if (targetData['HP'] <= 0):
                print(target+"'s HP has dropped to 0, please kill this creature!")
    elif (type == 'saves'):
        targetData['StrSave'] += value
        targetData['DexSave'] += value
        targetData['ConSave'] += value
        targetData['IntSave'] += value
        targetData['WisSave'] += value
        targetData['ChaSave'] += value
    elif (type == 'strsaves' or type == 'dexsaves' or type == 'consaves' or type == 'intsaves' or type == 'wissaves' or type == 'chasaves'):
        targetData[type[:3].capitalize()+'Save'] += value
    elif (type == 'move'):
        for moveType in targetData['Move']:
            if (targetData['Move'][moveType] > 0):
                targetData['Move'][moveType] += value
    elif (type == 'size'):
        targetData['SizeMod'] += value
        targetData['Size'] = getSizeClass(targetData['SizeMod'])
    elif (type == 'spelldc'):
        # also update the value of any trigger abilities this actor owns if its dc matches up with the actor's spell dc
        for triggerAbility in list(triggerData.values()):
            if (triggerAbility['Owner'] == target and triggerAbility['Save'] != '' and triggerAbility['DC'] == targetData['SpellDC']):
                triggerAbility['DC'] += value
        targetData['SpellDC'] += value
    else:
        print("Invalid buff type", type)
        return False

    return True

def addAttack(data):

    for i in range(0,len(data['Atk'])):
        for j in range(0,len(data['Atk'][i])):
            for statKey in ['Atk','Damage','DmgBonus']:
                data[statKey][i][j].insert(0,data[statKey][i][j][0])
            data['WeaponTypes'][i][j].insert(0,data['WeaponTypes'][i][j][0][:])
            if (i < len(data['OnHitAbilities']) and j < len(data['OnHitAbilities'][i]) and len(data['OnHitAbilities'][i][j]) > 1):
                data['OnHitAbilities'][i][j].insert(0,data['OnHitAbilities'][i][j][0])

def removeAttack(data):

    for i in range(0,len(data['Atk'])):
        for j in range(0,len(data['Atk'][i])):
            for statKey in ['Atk','Damage','DmgBonus','WeaponTypes']:
                if (len(data[statKey][i][j]) > 1):
                    data[statKey][i][j].pop(0)
                else:
                    DnDUtil.printWarning("Attempted to remove an attack when there was only one attack given in "+statKey)

            if (i < len(data['OnHitAbilities']) and j < len(data['OnHitAbilities'][i]) and len(data['OnHitAbilities'][i][j]) > 1):
                data['OnHitAbilities'][i][j].pop(0)

def knockProne(target,targetData):

    if (ActorUtil.isImmuneToType(targetData,['prone'])):
        print(target, "is", DnDUtil.getFailText('immune'), "to being knocked prone!")
    else:
        targetData['Prone'] = True
        print(target, "is knocked", DnDUtil.getStatusText('prone')+'!')
                
def addImmunity(data,immunityType):

    data['Immunities'].append(immunityType)

def removeImmunity(data,immunityType):

    if (immunityType in data['Immunities']):
        data['Immunities'].remove(immunityType)
    else:
        DnDUtil.printWarning("Attempted to remove immunity "+immunityType+" but immunity not found")

def addResistance(data,resistType):

    data['Resistances'].append(resistType)

def removeResistance(data,resistType):

    if (resistType in data['Resistances']):
        data['Resistances'].remove(resistType)
    else:
        DnDUtil.printWarning("Attempted to remove resistance "+resistType+" but resistance not found")

def addVulnerability(data,vulnerabilityType):

    data['Vulnerabilities'].append(vulnerabilityType)

def removeVulnerability(data,vulnerabilityType):

    if (vulnerabilityType in data['Vulnerabilities']):
        data['Vulnerabilities'].remove(vulnerabilityType)
    else:
        DnDUtil.printWarning("Attempted to remove vulnerability "+vulnerabilityType+" but vulnerability not found")

def addAdvantage(data,advantageType):

    data['Advantages'].append(advantageType)

def removeAdvantage(data,advantageType):

    if (advantageType in data['Advantages']):
        data['Advantages'].remove(advantageType)
    # don't print the warning when attempting to remove a 'next' advantage since it was likely removed after the roll was made
    elif (len(advantageType) <= 4 or len(advantageType) > 4 and advantageType[:4] != 'next'):
        DnDUtil.printWarning("Attempted to remove advantage "+advantageType+" but advantage not found")

def addDisadvantage(data,disadvantageType):

    data['Disadvantages'].append(disadvantageType)

def removeDisadvantage(data,disadvantageType):

    if (disadvantageType in data['Disadvantages']):
        data['Disadvantages'].remove(disadvantageType)
    # don't print the warning when attempting to remove a 'next' disadvantage since it was likely removed after the roll was made
    elif (len(disadvantageType) <= 4 or len(disadvantageType) > 4 and disadvantageType[:4] != 'next'):
        DnDUtil.printWarning("Attempted to remove disadvantage "+disadvantageType+" but disadvantage not found")

def addMiscStat(target,targetData,miscStat,miscArg):

    if (miscArg.isdigit()):
        miscArg = int(miscArg)
    if (not(miscStat in targetData['Misc'])):
        targetData['Misc'][miscStat] = miscArg
        return True
    else:
        print(target, "already has the stat", miscStat+'!', "Use the editmisc command if you wish to edit this stat's argument")
        return False

def removeMiscStat(targetData,miscStat):

    if (miscStat in targetData['Misc']):
        del targetData['Misc'][miscStat]
    else:
        DnDUtil.printWarning("Attempted to remove misc stat "+miscStat+" but the misc stat was not found")

def addMagicBonus(targetData,rangeIndex,magicBonusDelta):

    # add the difference in magic bonuses to atk and damage
    for key in ['Atk','DmgBonus']:
        for i in range(0,len(targetData[key][rangeIndex])):
            for j in range(0,len(targetData[key][rangeIndex][i])):
                targetData[key][rangeIndex][i][j] += magicBonusDelta
    # make all weapons with this range magical
    for i in range(0,len(targetData['WeaponTypes'][rangeIndex])):
        for j in range(0,len(targetData['WeaponTypes'][rangeIndex][i])):
            weaponTypes = targetData['WeaponTypes'][rangeIndex][i][j]
            weaponTypes.append('magic')
            if ('nonmagic' in weaponTypes):
                weaponTypes.remove('nonmagic')

def removeMagicBonus(targetData,rangeIndex,magicBonusDelta):

    # subtract the magic bonus gained from atk and damage
    for key in ['Atk','DmgBonus']:
        for i in range(0,len(targetData[key][rangeIndex])):
            for j in range(0,len(targetData[key][rangeIndex][i])):
                targetData[key][rangeIndex][i][j] -= magicBonusDelta
    # remove the magic tag added to weapon types
    for i in range(0,len(targetData['WeaponTypes'][rangeIndex])):
        for j in range(0,len(targetData['WeaponTypes'][rangeIndex][i])):
            weaponTypes = targetData['WeaponTypes'][rangeIndex][i][j]
            if ('magic' in weaponTypes):
                weaponTypes.remove('magic')
            elif (weaponTypes):
                DnDUtil.printWarning("Attempted to dispel magic weapon, but no magic tag found in weapon types: "+str(weaponTypes))
            # re-add the nonmagic tag if this weapon reverts to being nonmagical
            if (not('magic' in weaponTypes) and DnDUtil.haveCommonItem(['slashing','piercing','bludgeoning'],weaponTypes)):
                weaponTypes.append('nonmagic')

def setTempHP(target,targetData,amount):

    if ('TempHP' in targetData):
        if (targetData['TempHP'] >= amount):
            print(target, "does not gain temp hp, since it already has temp hp of at least", amount)
            return False
        else:
            # if there is a previous effect granting temporary hp, remove it since we are overwriting it
            if (targetData['TempHP'] > 0):
                removeTempHPEffect(target)
            targetData['TempHP'] = amount

    print(target, "now has", amount, "temporary hp!")
    return True

def clearTempHP(targetData):

    if ('TempHP' in targetData):
        tempHP = targetData['TempHP']
        targetData['TempHP'] = 0
    else:
        tempHP = 0

    return tempHP

def removeTempHPEffect(target):

    # we assume that there is only ever 1 temphp effect on a given target at one time, since we call this function whenever a temp hp effect is overwritten
    for dict in [encounter,playerData]:
        for actor in dict:
            for effect in dict[actor]['Effects']:
                if (effect[0] == target):
                    if (effect[1] == 'temphp'):
                        dict[actor]['Effects'].remove(effect)
                        if (effect in dict[actor]['Concentration']):
                            dict[actor]['Concentration'].remove(effect)
                        return
                    elif (effect[1] == 'cc'):
                        for ccEffect in effect[3]:
                            if (ccEffect[1] == 'temphp'):
                                effect[3].remove(ccEffect)
                                # remove the entire cc effect if this cc only held the temp hp effect
                                if (not(effect[3])):
                                    removeCCEffect(getData(target),effect[2],actor)
                                    dict[actor]['Effects'].remove(effect)
                                    if (effect in dict[actor]['Concentration']):
                                        dict[actor]['Concentration'].remove(effect)
                                return

def mindControl(target):

    if (target in encounter):
        targetData = encounter.pop(target)
        convertData(targetData)
        playerData[target] = targetData
        print(target, "is now a player!")
        return True
    elif (target in playerData):
        targetData = playerData.pop(target)
        convertData(targetData)
        encounter[target] = targetData
        print(target, "is now an enemy!")
        return True
    else:
        return False

def shapeShift(target,targetData,newType):

    playerTarget = not('HP' in targetData)
    
    newData = getPlayerData(newType)
    if (newData == {}):
        newData = getCreatureData(newType,False)
    while (newData == {}):
        newType = input("Creature "+newType+" not found, try again: ")
        newData = getPlayerData(newType)
        if (newData == {}):
            newData = getCreatureData(newType,False)

    if (playerTarget == ('HP' in newData)):
        convertData(newData)
    if (not(playerTarget)):
        # if we're reverting to base form, remove all temp hp
        if (target.startswith(newType)):
            targetData['TempHP'] = 0
        # otherwise, grant temp hp equal to the new form's max hp
        else:
            targetData['TempHP'] = newData['MaxHP']
    for key in newData:
        if (not(key in ['HP','MaxHP','TempHP','Effects','Status','InitRoll','Prone','Reaction','CanReact','Concentration'])):
            targetData[key] = newData[key]
    for dataDict in [playerData,encounter]:
        for actor in dataDict:
            actorData = dataDict[actor]
            for effect in actorData['Effects']:
                if (effect[0] == target):
                    type = effect[1]
                    if (type == 'cc' or type == 'grapple'):
                        for subEffect in effect[3]:
                            if (not(subEffect[1] in ['cc','move','ss','mc','script'])):
                                applyEffect(subEffect,actor,target,targetData)
                    elif (not(type in ['move','ss','mc','script'])):
                        applyEffect(effect,actor,target,targetData)
    
    print(target, "is now a", newType+'!')

def applyMirrorImage(attackRoll,attack,defender,defenderData,playerDefender):

    mirrorImageStatusEffect = []
    for statusEffect in defenderData['Status']:
        if (statusEffect[0] == 'mirrorimage'):
            if (playerDefender):
                if (PLAYERS_ADD_BONUS):
                    if (DnDUtil.getAnswer('Does this attack target a duplicate') == 'y'):
                        roll = 20
                    else:
                        roll = 1
                else:
                    roll = DnDUtil.getInt(input('Roll for Mirror Image: '))
            else:
                roll = random.randint(1,20)
                print(defender, "rolls a", roll, "for mirror image")
            numImages = int(statusEffect[4])
            if (numImages == 3 and roll < 6 or numImages == 2 and roll < 8 or numImages == 1 and roll < 11):
                print("This attack will target", defender)
                return True
            print("This attack will instead target a mirror image!")
            # we need the defender's dex mod in order to figure out its mirror image's AC
            # to determine that, we use the initiative value if it is 5 or less. Otherwise, ask the dm for the dex mod
            initValue = defenderData['Init']
            if ((not(playerDefender) or not(PLAYERS_ADD_BONUS)) and initValue <= 5):
                defense = 10 + initValue
            else:
                dexMod = DnDUtil.getInt(input('What is '+defender+'\'s dex mod? '))
                defense = 10 + dexMod
            if (attackRoll == 20 or attackRoll != 1 and attack >= defense):
                print(defender+'\'s', "mirror image was", DnDUtil.getPassText('hit')+'!')
                numImages -= 1
                statusEffect[4] = numImages
                if (numImages > 0):
                    print(defender, "has", numImages, "mirror images remaining")
                else:
                    print(defender, "has no mirror images remaining!")
                    mirrorImageEffects = getCCEffectsForTarget(defenderData,defender,'mirrorimage')
                    for effect in mirrorImageEffects:
                        dispel(effect,defender,defenderData)
                        defenderData['Effects'].remove(effect)
                        if (effect in defenderData['Concentration']):
                            defenderData['Concentration'].remove(effect)
                    if (mirrorImageEffects):
                        return False
                    DnDUtil.printWarning("Tried to remove mirror image effect, but none was found")
            else:
                print("This attack", DnDUtil.getFailText('misses'), "mirror image")
                    
            return False

    return True

def getNetDamage(damage,actorData,target,targetData,damageTypes,damageSource,weaponAttack,uncannyDodge=False):

    if (damage <= 0):
        return 0

    if (weaponAttack):
        isImmune = isImmuneToWeapon(targetData,damageTypes)
        isVulnerable = isVulnerableToWeapon(targetData,damageTypes)
        hasResist = hasResistFromWeapon(targetData,damageTypes)
    else:
        isImmune = ActorUtil.isImmuneToType(targetData,damageTypes)
        isVulnerable = ActorUtil.isVulnerableToType(targetData,damageTypes)
        hasResist = ActorUtil.hasResistFromType(targetData,damageTypes)

    if ('damage' in targetData['Immunities']):
        isImmune = True
    # check if target can trigger primordial ward in response to this damage
    elif (ActorUtil.hasStatus(targetData,['primordialward']) and ActorUtil.canReact(targetData)):
        element = ''
        i = 0
        while (not(element) and i < len(damageTypes)):
            type = damageTypes[i]
            if (type in ['acid','cold','fire','lightning','thunder']):
                element = type
            i += 1
        if (element and DnDUtil.getAnswer('Use '+target+'\'s reaction to trigger primordial ward') == 'y'):
            isImmune = True
            targetData['Reaction'] = False
            for statusEffect in targetData['Status']:
                if (statusEffect[0] == 'primordialward'):
                    owner = statusEffect[1]
                    ownerData = getData(owner)
                    for effect in ownerData['Effects']:
                        if (effect[0] == target and effect[1] == 'cc' and effect[2] == 'primordialward'):
                            dispel(effect,owner,targetData)
                            ownerData['Effects'].remove(effect)
                            if (effect in ownerData['Concentration']):
                                ownerData['Concentration'].remove(effect)
                            break
                    break
            print(target, "is no longer under the effect of", DnDUtil.getStatusText('primordialward'))
            print(target, "now has", element, "immunity until the end of its next turn")
            newEffect = [target,'cc','primordialwardr',[[target,'immunity',element]],1.5]
            targetData['Effects'].append(newEffect)
            targetData['Concentration'].append(newEffect)
            applyCC(target,target,targetData,'primordialwardr')
            addImmunity(targetData,element)

    if (isImmune):
        print(target, "takes", DnDUtil.getFailText("no damage"), "from", damageSource, "due to immunity!")
        return 0
    else:
        # check if target can cast absorb elements in response to this damage
        if ('absorbelements' in targetData['UseAbilities'] and ActorUtil.canReact(targetData)):
            element = ''
            i = 0
            while (not(element) and i < len(damageTypes)):
                type = damageTypes[i]
                if (type in ['acid','cold','fire','lightning','thunder']):
                    element = type
                i += 1
            if (element and DnDUtil.getAnswer('Use '+target+'\'s reaction to cast absorb elements') == 'y'):
                print(target, "now has", element, "resistance until next turn")
                targetData['Reaction'] = False
                hasResist = True
                addResistance(targetData,element)
                targetData['Effects'].append([target,'resist',element,1])
                spellLevel = SpellUtil.inputSpellLevel('absorb elements',1)
                actions = [['cc','absorbelements','actorend'],['onhit','absorbelementsOH'+element,'1']]
                useAbility(not('HP' in targetData),'absorbelements',[],0,actions,not('HP' in targetData),[target],target,targetData,target,targetData,0,'',0,0,1,spellLevel,False,False,False,False,{})

        if (weaponAttack and ActorUtil.hasStatus(actorData,['weakening']) and DnDUtil.getAnswer('Is this a strength-based weapon attack') == 'y'):
            print(target, "takes half damage from", damageSource, "since the attacker is weakened")
            damage /= 2
        if (uncannyDodge):
            print(target, "takes half damage from", damageSource, "due to uncanny dodge")
            damage /= 2
        if (isVulnerable and not(hasResist)):
            print(target, "takes double damage from", damageSource, "due to vulnerability!")
            damage *= 2
        elif (hasResist and not(isVulnerable)):
            print(target, "takes half damage from", damageSource, "due to resistance")
            damage /= 2
        elif (isVulnerable and hasResist):
            print(target, "takes normal damage from", damageSource, "since its resistance and vulnerability cancel out")
        
    return damage

def applyDamage(actor,actorData,damage,damageTypes,crit,applyConcentration=True):

    i = 0
    while (i < len(actorData['Status'])):
        statusEffect = actorData['Status'][i]
        # remove status effects that should be removed upon taking damage, such as sleep and touchofmadness
        removeOnDamagedEffects = ['sleep','touchofmadness']
        if (statusEffect[0] in removeOnDamagedEffects):
            owner = statusEffect[1]
            ownerData = getData(owner)
            if (ownerData is None):
                DnDUtil.printWarning("Attempted to remove "+statusEffect[0]+" effect from owner "+owner+" but data not found")
            else:
                for effect in ownerData['Effects']:
                    if (effect[0] == actor and effect[1] == 'cc'):
                        if (effect[2] in removeOnDamagedEffects):
                            dispel(effect,owner,actorData)
                            ownerData['Effects'].remove(effect)
                            if (effect in ownerData['Concentration']):
                                ownerData['Concentration'].remove(effect)
                            i -= 1
                        else:
                            for ccEffect in effect[3]:
                                if (ccEffect[1] == 'cc' and ccEffect[2] in removeOnDamagedEffects):
                                    actorData['Status'].remove(statusEffect)
                                    effect[3].remove(ccEffect)
                                    i -= 1
                                    if (not(effect[3])):
                                        dispel(effect,owner,actorData)
                                        ownerData['Effects'].remove(effect)
                                        if (effect in ownerData['Concentration']):
                                            ownerData['Concentration'].remove(effect)
                                        i -= 1
                i += 1
        elif (statusEffect[0] == 'unconscious' and statusEffect[2] == 'death'):
            if (statusEffect[7] == 3):
                print(actor, "is no longer stable due to taking damage!")
                statusEffect[7] = 0
            if (crit):
                print(actor, DnDUtil.getFailText('fails'), "2 death saving throws due to taking critical damage!")
                statusEffect[6] += 2
            else:
                print(actor, DnDUtil.getFailText('fails'), "1 death saving throw due to taking damage!")
                statusEffect[6] += 1
            print(actor, "has now failed", DnDUtil.getFailText(statusEffect[6]), "death saving throws and passed", DnDUtil.getPassText(statusEffect[7]), "death saving throws")
            if (statusEffect[6] >= 3):
                print(actor, "has", DnDUtil.getDeathText('died')+'!')
                kill(actor)
                return True
            i += 1
        else:
            i += 1

    if ('regen' in actorData['Misc'] and not(isinstance(actorData['Misc']['regen'],int)) and ',' in actorData['Misc']['regen'] and not('regendisable' in actorData['Misc']) and DnDUtil.haveCommonItem(damageTypes,actorData['Misc']['regen'].split(',')[1:])):
        print(actor+'\'s', "regeneration will be disabled next turn!")
        actorData['Misc']['regendisable'] = 0

    # TODO: replace this code to ACTUALLY make the save and reverse the effect within this function
    if (ActorUtil.hasStatus(actorData,['mc'])):
        printMessage('Make a save to reverse the mc effect on '+actor+'if required!')

    if (applyConcentration):
        checkConcentration(actor,actorData,damage)

    return False

def dealDamage(target,targetData,damage):
    
    if ('HP' in targetData):
        isBloodied = targetData['MaxHP'] - targetData['HP'] >= targetData['HP']
        if (targetData['TempHP'] > 0):
            if (targetData['TempHP'] >= damage):
                targetData['TempHP'] -= damage
            else:
                remainingDamage = damage - targetData['TempHP']
                targetData['TempHP'] = 0
                targetData['HP'] -= remainingDamage
        else:
            targetData['HP'] -= damage

        if (not(isBloodied) and targetData['MaxHP'] - targetData['HP'] >= targetData['HP']):
            print(target, "is now", DnDUtil.getDamageText("bloodied"))

def checkKilled(actor,actorData,damage,damageTypes,crit):

    if (not('HP' in actorData)):
        return False

    if (actorData['HP'] <= 0 and 'regen' in actorData['Misc'] and not(isinstance(actorData['Misc']['regen'],int)) and ',' in actorData['Misc']['regen'] and not('regendisable' in actorData['Misc'])):
        print(actor, "stays alive since its regeneration hasn't been disabled!")
        actorData['HP'] = 1

    if (actorData['HP'] <= 0 and not(crit) and 'uf' in actorData['Misc'] and not('radiant' in damageTypes)):
        print(actor, "attempts to stay alive with Undead Fortitude!")
        if (makeSave(actor,actorData,'con',5+damage,[]) == 0):
            print(actor, "returns to life with 1 HP!")
            actorData['HP'] = 1

    if (actorData['HP'] <= 0 and 'relentless' in actorData['Misc'] and damage <= actorData['Misc']['relentless']):
        print(actor, "stays alive with relentless since the damage dealt was", actorData['Misc']['relentless'], "or less!")
        actorData['Misc']['relentless'] = 0
        actorData['HP'] = 1

    return actorData['HP'] <= 0

def heal(target,targetData,amount):

    if (ActorUtil.isImmuneToType(targetData,['heal'])):
        print(target, "can't be", DnDUtil.getFailText('healed')+'!')
        return 0

    if (amount > 0):
        # see if the healed target had a wound effect or was unconscious at 0 hp and clear it if so
        i = 0
        while (i < len(targetData['Status'])):
            statusEffect = targetData['Status'][i]
            if (statusEffect[0] == 'wound'):
                ownerData = getData(statusEffect[1])
                for effect in ownerData['Effects']:
                    if (effect[0] == target):
                        if (effect[1] == 'wound'):
                            targetData['Status'].remove(statusEffect)
                            ownerData['Effects'].remove(effect)
                            if (effect in ownerData['Concentration']):
                                ownerData['Concentration'].remove(effect)
                            i -= 1
                        elif (effect[1] == 'cc'):
                            for ccEffect in effect[3]:
                                if (ccEffect[1] == 'wound'):
                                    targetData['Status'].remove(statusEffect)
                                    effect[3].remove(ccEffect)
                                    i -= 1
                                    if (not(effect[3])):
                                        dispel(effect,statusEffect[1],targetData)
                                        ownerData['Effects'].remove(effect)
                                        if (effect in ownerData['Concentration']):
                                            ownerData['Concentration'].remove(effect)
                                        i -= 1
                print(target, "has healed its wound!")
                i += 1
            elif (statusEffect[0] == 'unconscious' and statusEffect[2] == 'death'):
                ownerData = getData(statusEffect[1])
                for effect in ownerData['Effects']:
                    if (effect[0] == target and effect[1] == statusEffect[0]):
                        ownerData['Effects'].remove(effect)
                        if (effect in ownerData['Concentration']):
                            ownerData['Concentration'].remove(effect)
                        break
                targetData['Status'].remove(statusEffect)
                print(target, "is revived, but is still", DnDUtil.getStatusText('prone')+'!')
                # for creatures, reset hp and temp hp to 0 since that is what the values should be while unconscious
                if ('HP' in targetData):
                    targetData['TempHP'] = 0
                    targetData['HP'] = 0
            else:
                i += 1

        if ('HP' in targetData):
            if (targetData['HP'] + amount > targetData['MaxHP']):
                amount = targetData['MaxHP'] - targetData['HP']
                targetData['HP'] = targetData['MaxHP']
            else:
                targetData['HP'] += amount
        if (amount > 0):
            print(target, "heals for", DnDUtil.getHealText(amount), "hp")

    return amount

def checkCounterSpell(caster,casterData,playerCaster,spellLevel):

    # return immediately if this isn't a spell since magical abilities can't be countered
    if (spellLevel < 0):
        return True

    if (playerCaster):
        enemyData = encounter
    else:
        enemyData = playerData

    for enemy in enemyData:
        if ('counterspell' in enemyData[enemy]['UseAbilities'] and ActorUtil.canReact(enemyData[enemy]) and DnDUtil.getAnswer('Use '+enemy+'\'s reaction to cast counterspell (60ft)') == 'y'):
            enemyData[enemy]['Reaction'] = False
            counterSpellLevel = SpellUtil.inputSpellLevel('counterspell',3)
            if (counterSpellLevel >= spellLevel):
                print(enemy, DnDUtil.getPassText('successfully'), "countered the spell!")
                return False
            else:
                counterSpellDC = 10 + spellLevel
                print("The DC to counterspell this spell is", counterSpellDC)
                result = ActorUtil.makeCheck(enemy,enemyData,not(playerCaster),'spellcasting ability')
                print(enemy, "result is", result)
                
                if (result >= counterSpellDC):
                    print(enemy, DnDUtil.getPassText('successfully'), "countered the spell!")
                    return False
                else:
                    print(enemy, DnDUtil.getFailText('failed'), "to counter the spell")

    if (not(checkTemporalShunt(caster,casterData,playerCaster))):
        return False

    return True

def checkTemporalShunt(actor,actorData,playerActor):

    if (playerActor):
        enemyData = encounter
    else:
        enemyData = playerData

    for enemy in enemyData:
        if ('temporalshunt' in enemyData[enemy]['UseAbilities'] and ActorUtil.canReact(enemyData[enemy]) and DnDUtil.getAnswer('Use '+enemy+'\'s reaction to cast temporal shunt (120ft)') == 'y'):
            enemyData[enemy]['Reaction'] = False
            if (enemyData[enemy]['UseAbilities']['temporalshunt']['DC']):
                spellDC = enemyData[enemy]['UseAbilities']['temporalshunt']['DC']
            else:
                spellDC = enemyData[enemy]['SpellDC']
            if (makeSave(actor,actorData,'wis',spellDC,['temporalshunt']) > 0):
                print(actor, "loses its spell/attack and disappears until the start of its next turn!")
                return False

    return True

def checkShieldMaster(actor,actorData,saveType):

    if ('sm' in actorData['Misc'] and saveType == 'dex' and ActorUtil.canReact(actorData) and DnDUtil.getAnswer('Use '+actor+'\'s reaction to take no damage instead of half damage') == 'y'):
        actorData['Reaction'] = False
        return True
    else:
        return False

def getAdvantageDisadvantageRoll(roll,advantage,disadvantage):

    if (advantage == disadvantage):
        return roll
    elif (advantage):
        rawInput = input("Make a second roll for advantage (skip if you already have): ")
        if (rawInput == ''):
            return roll
        else:
            roll2 = DnDUtil.getInt(rawInput)
            return max(roll,roll2)
    else:
        rawInput = input("Make a second roll for disadvantage (skip if you already have): ")
        if (rawInput == ''):
            return roll
        else:
            roll2 = DnDUtil.getInt(rawInput)
            return min(roll,roll2)

def getCritStat(actorData,rangeIndex,atkIndex1,atkIndex2,critType):

    #0: crit chance, 1: crit damage
    if (critType == 0):
        critSuffix = 'c'
        baseCrit = 20
    elif (critType == 1):
        critSuffix = 'd'
        baseCrit = 2
    else:
        DnDUtil.printError("Unknown crit type "+str(critType)+" valid crit types are 0 and 1")
        return 0

    critKey = 'crit'+critSuffix

    # first, check if any of the misc stats are for this crit type before checking specifics since the vast majority of creatures will not have this stat
    found = False
    for stat in actorData['Misc']:
        if (stat.find(critKey) != -1):
            found = True
            break

    if (not(found)):
        return baseCrit

    if (rangeIndex == 0):
        rangePrefix = 'm'
    else:
        rangePrefix = 'r'

    if (rangePrefix+critKey+str(atkIndex1)+str(atkIndex2) in actorData['Misc']):
        return actorData['Misc'][rangePrefix+critKey+str(atkIndex1)+str(atkIndex2)]
    elif (rangePrefix+critKey+str(atkIndex1) in actorData['Misc']):
        return actorData['Misc'][rangePrefix+critKey+str(atkIndex1)]
    elif (rangePrefix+critKey in actorData['Misc']):
        return actorData['Misc'][rangePrefix+critKey]
    elif (critKey in actorData['Misc']):
        return actorData['Misc'][critKey]
    else:
        return baseCrit

def isImmuneToWeapon(data,weaponTypes):

    if (weaponTypes):
        return ActorUtil.isImmuneToType(data,weaponTypes)
    elif (ActorUtil.isImmuneToType(data,['nonmagic']) and (autoBattle or DnDUtil.getAnswer('Is this an attack from a magical weapon') == 'n')):
        return True
    elif (ActorUtil.isImmuneToType(data,['slashing','piercing','bludgeoning'])):
        matchingImmunities = ''
        if ('slashing' in data['Immunities']):
            matchingImmunities += ' slashing '
        if ('piercing' in data['Immunities']):
            matchingImmunities += ' piercing '
        if ('bludgeoning' in data['Immunities']):
            matchingImmunities += ' bludgeoning '

        if (DnDUtil.getAnswer('Does this attack deal any of these damage types' + matchingImmunities) == 'y'):
            return True
    else:
        return False

    return False
            
def hasResistFromWeapon(data,weaponTypes):

    if (ActorUtil.hasStatus(data,['petrification'])):
        return True

    if (weaponTypes):
        return ActorUtil.hasResistFromType(data,weaponTypes)
    elif (ActorUtil.hasResistFromType(data,['nonmagic']) and (autoBattle or DnDUtil.getAnswer('Is this an attack from a magical weapon') == 'n')):
        return True
    elif (ActorUtil.hasResistFromType(data,['slashing','piercing','bludgeoning'])):
        matchingResists = ''
        if ('slashing' in data['Resistances']):
            matchingResists += ' slashing '
        if ('piercing' in data['Resistances']):
            matchingResists += ' piercing '
        if ('bludgeoning' in data['Resistances']):
            matchingResists += ' bludgeoning '

        if (DnDUtil.getAnswer('Does this attack deal any of these damage types' + matchingResists) == 'y'):
            return True
    else:
        return False

    return False

def isVulnerableToWeapon(data,weaponTypes):

    if (weaponTypes):
        return ActorUtil.isVulnerableToType(data,weaponTypes)
    elif (ActorUtil.isVulnerableToType(data,['nonmagic']) and (autoBattle or DnDUtil.getAnswer('Is this an attack from a magical weapon') == 'n')):
        return True
    elif (ActorUtil.isVulnerableToType(data,['slashing','piercing','bludgeoning'])):
        matchingVulnerabilities = ''
        if ('slashing' in data['Vulnerabilities']):
            matchingVulnerabilities += ' slashing '
        if ('piercing' in data['Vulnerabilities']):
            matchingVulnerabilities += ' piercing '
        if ('bludgeoning' in data['Vulnerabilities']):
            matchingVulnerabilities += ' bludgeoning '

        if (DnDUtil.getAnswer('Does this attack deal any of these damage types' + matchingVulnerabilities) == 'y'):
            return True
    else:
        return False

    return False

def loadCreaturesFromFile(fileName):

    global totalExp, totalGold, actorIndex
    print("Loading creatures from file '"+fileName+"'...")
    encounterReader = open(fileName,'r')
    encounterData = json.load(encounterReader)
    if (encounterData):
        totalExp = encounterData['TotalExp']
        totalGold = encounterData['TotalGold']
        actorIndex = encounterData['ActorIndex']
        for encounterStat in ['TotalExp','TotalGold','ActorIndex']:
            del encounterData[encounterStat]
        for actor in encounterData:
            savedActorData = encounterData[actor]
            playerActor = not('HP' in savedActorData)
            if (playerActor):
                dataDict = playerData
            else:
                dataDict = encounter
            actorData = getPlayerData(savedActorData['Base'])
            if (not(actorData)):
                actorData = getCreatureData(savedActorData['Base'],False)
            if (actorData):
                if (playerActor == ('HP' in actorData)):
                    convertData(actorData)
                for key in savedActorData:
                    actorData[key] = savedActorData[key]
                dataDict[actor] = actorData
            else:
                DnDUtil.printError("Attempted to load actor data for actor "+savedActorData['Base']+" but this actor was not found")
    else:
        DnDUtil.printWarning("Attempted to load an encounter from an empty file")

    for dataDict in [playerData,encounter]:
        for actor in dataDict:
            actorData = dataDict[actor]
            for effect in actorData['Effects']:
                target = effect[0]
                targetData = getData(target)
                if (targetData is None):
                    DnDUtil.printError("Attempted to restore effect "+str(effect)+" with owner "+actor+" but the target "+target+" could not be found")
                else:
                    type = effect[1]
                    if (type == 'cc' or type == 'grapple'):
                        for subEffect in effect[3]:
                            if (not(subEffect[1] in ['cc','move','ss','mc'])):
                                applyEffect(subEffect,actor,target,targetData)
                    elif (not(type in ['move','ss','mc'])):
                        applyEffect(effect,actor,target,targetData)
                # point an equal effect in concentration data to this effect if present so it updates properly
                if (effect in actorData['Concentration']):
                    actorData['Concentration'][actorData['Concentration'].index(effect)] = effect

    if (actorIndex >= len(playerData) + len(encounter)):
        actorIndex = 0

    encounterReader.close()

def loadCreaturesFromDict(creatureDict):

    print("Creating a new encounter...")
    for creature in creatureDict:
        number = creatureDict[creature]
        if (number == 1):
            creatureData = getCreatureData(creature)
            if (creatureData):
                encounter[creature] = creatureData
            else:
                DnDUtil.printError("Could not find data for creature "+creature)
                return True
        else:
            creatureData = getCreatureData(creature)
            if (creatureData):
                encounter[creature+'1'] = creatureData
                for i in range(2,number+1):
                    encounter[creature+str(i)] = getCreatureData(creature)
            else:
                DnDUtil.printError("Could not find data for creature "+creature)
                return True

    return False

def loadCreaturesFromInput():

    print("Creating a new encounter...")
    rawInput = ''
    while rawInput != 'done':
        rawInput = input("Enter creature type and number: ")
        command = rawInput.split()
        numArgs = len(command)

        if (numArgs == 0):
            rawInput = 'done'

        if (rawInput != 'done'):
            while (numArgs != 2):
                rawInput = input("Must be a creature type followed by a number: ")
                command = rawInput.split()
                numArgs = len(command)
            type = command[0]
            number = DnDUtil.getInt(command[1])
            if (number == 1):
                result = getCreatureData(type)
                while (result == {}):
                    type = input("Creature not found, try again: ")
                    if (len(type) >= 2):
                        type = type.split()
                        type = type[0]
                        result = getCreatureData(type)
                encounter[type] = result 
            else:
                result = getCreatureData(type)
                while (result == {}):
                    type = input("Creature not found, try again: ")
                    if (len(type) >= 2):
                        type = type.split()
                        type = type[0]
                        result = getCreatureData(type)
                encounter[type+'1'] = result
                for i in range(2,number+1):
                    encounter[type+str(i)] = getCreatureData(type)

def initializeTurnOrder(rollForInitiative):

    global turnOrder
    turnOrder = []
    if (rollForInitiative):
        print("Roll for initiative:")
    initData = []
    for dataSource in [encounter,playerData]:
        for actor in dataSource:
            actorData = dataSource[actor]
            initBonus = actorData['Init']
            if (rollForInitiative and actor != 'lair'):
                initRoll = ActorUtil.makeRoll(actor,not('HP' in actorData),DnDUtil.haveCommonItem(['init','dex','checks'],actorData['Advantages']),DnDUtil.haveCommonItem(['init','dex','checks'],actorData['Disadvantages']),initBonus,True,actor)
                if (ActorUtil.hasStatus(actorData,['giftofalacrity'])):
                    if ('HP' in actorData):
                        goaRoll = random.randint(1,8)
                        print(actor, "rolls a", goaRoll, "for gift of alacrity bonus")
                    else:
                        goaRoll = DnDUtil.getInt(input('Roll for gift of alacrity bonus (1d8): '))
                    initRoll += goaRoll
                actorData['InitRoll'] = initRoll
            else:
                initRoll = actorData['InitRoll']
            length = len(initData)
            i = 0
            while (i < length and (initRoll < initData[i][1] or initRoll == initData[i][1] and initBonus < initData[i][2] and (PLAYERS_ADD_BONUS or actor in encounter))):
                i += 1
            initData.insert(i,[actor,initRoll,initBonus])

    print("The results are:")
    for item in initData:
        turnOrder.append(item[0])
        print(item[0]+':', item[1])

def updateEncounterFile():

    encounterWriter = open(ENCOUNTER_FILE,'w')
    encounterFileData = {'TotalExp': totalExp, 'TotalGold': totalGold, 'ActorIndex': actorIndex}
    for player in playerData:
        encounterFileData[player] = {}
        for key in ['Base','InitRoll','Move','Effects','Status','Concentration','Reaction','Prone']:
            encounterFileData[player][key] = playerData[player][key]
    for creature in encounter:
        creatureData = encounter[creature]
        encounterFileData[creature] = {}
        for key in ['Base','MaxHP','HP','InitRoll','Move','Effects','Status','Concentration','Reaction','Prone']:
            encounterFileData[creature][key] = creatureData[key]
    encounterFileDataJson = json.dumps(encounterFileData)
    encounterWriter.write(encounterFileDataJson)
    encounterWriter.close()

def createMagicShop(size):

    print("Generating", size.capitalize(), "Magic Shop...")
    shopWriter = open(MAGIC_SHOP_OUTPUT_FILE,'w')

    if (size == 'small'):
        sizeMod = 2
    elif (size == 'medium'):
        sizeMod = 3
    else:
        sizeMod = 4

    shopWriter.write("Potions:\n")
    items = []
    totalValue = 0
    potions = makeItems(['potionT0'],sizeMod,sizeMod+1,False)
    if (potions and '(Tier ' in potions[0] and potions[0][-1] == ')'):
        basePotionTier = DnDUtil.getInt(potions[0][potions[0].find('(Tier ')+len('(Tier '):-1])
        potionValue = getItemValue('potion',basePotionTier)
        totalValue += potionValue * len(potions)
    items.extend([str(potionValue)+'gp - '+potion for potion in potions])
    potions = makeItems(['potionT1'],sizeMod-1,sizeMod,False)
    potionValue = getItemValue('potion',basePotionTier+1)
    totalValue += potionValue * len(potions)
    items.extend([str(potionValue)+'gp - '+potion for potion in potions])
    potions = makeItems(['potionT2'],sizeMod-2,sizeMod-1,False)
    potionValue = getItemValue('potion',basePotionTier+2)
    totalValue += potionValue * len(potions)
    items.extend([str(potionValue)+'gp - '+potion for potion in potions])
    potions = makeItems(['potionT3'],sizeMod-3,sizeMod-2,False)
    potionValue = getItemValue('potion',basePotionTier+3)
    totalValue += potionValue * len(potions)
    items.extend([str(potionValue)+'gp - '+potion for potion in potions])
    potionDict = OrderedDict()
    for item in items:
        if (item in potionDict):
            potionDict[item] += 1
        else:
            potionDict[item] = 1
    for potion,number in list(potionDict.items()):
        priceIndex = potion.find('-')
        potionText = potion[:priceIndex]+'- '+str(number)+potion[priceIndex+1:]
        shopWriter.write(potionText+'\n')
    bundleSale = random.randint(sizeMod-1,sizeMod+3) * 5
    bundleValue = int(totalValue * (1 - .01 * bundleSale))
    shopWriter.write(str(bundleValue)+'gp - All Potions Bundle ('+str(bundleSale)+'% OFF)\n')
    potions = makeItems(['maxpotion'],sizeMod-5,sizeMod-3,False,'potion')
    potionValue = getItemValue('maxpotion',0)
    for potion in potions:
        shopWriter.write(str(potionValue)+'gp - '+potion+'\n')

    shopWriter.write("\nScrolls:\n")
    items = []
    scrolls = makeItems(['Scroll','spellT1'],sizeMod-1,sizeMod+1,True)
    if (scrolls and '(Tier ' in scrolls[0] and scrolls[0][-1] == ')'):
        baseScrollTier = DnDUtil.getInt(scrolls[0][scrolls[0].find('(Tier ')+len('(Tier '):-1])
        scrollValue = getItemValue('scroll',baseScrollTier)
        totalValue += scrollValue * len(scrolls)
    items.extend([str(scrollValue)+'gp - '+scroll for scroll in scrolls])
    scrolls = makeItems(['Scroll','spellT2'],sizeMod-2,sizeMod-1,True)
    scrollValue = getItemValue('scroll',baseScrollTier+1)
    totalValue += scrollValue * len(scrolls)
    items.extend([str(scrollValue)+'gp - '+scroll for scroll in scrolls])
    scrolls = makeItems(['Scroll','spellT3'],sizeMod-3,sizeMod-2,True)
    scrollValue = getItemValue('scroll',baseScrollTier+2)
    totalValue += scrollValue * len(scrolls)
    items.extend([str(scrollValue)+'gp - '+scroll for scroll in scrolls])
    for item in items:
        shopWriter.write(item+'\n')
    bundleSale = random.randint(sizeMod,sizeMod+4) * 5
    bundleValue = int(totalValue * (1 - .01 * bundleSale))
    shopWriter.write(str(bundleValue)+'gp - All Scrolls Bundle ('+str(bundleSale)+'% OFF)\n')

    numRobes = random.randint(sizeMod-2,sizeMod)
    if (numRobes > 0):
        shopWriter.write("\nRobes:\n")
    while (numRobes > 0):
        item = getItem(armorData,['robe'])
        shopWriter.write(makeItem(item,'robe')+'\n')
        numRobes -= 1

    numTrinkets = random.randint(sizeMod-3,sizeMod-1)
    if (numTrinkets > 0):
        shopWriter.write("\nJewelery:\n")
    while (numTrinkets > 0):
        typeRoll = random.randint(1,3)
        if (typeRoll == 3):
            type = 'Amulet'
        else:
            type = 'Ring'
        enchantRoll = random.randint(1,2)
        if (enchantRoll == 1):
            enchant = 'skill'
        else:
            enchant = 'enchant'
        item = randomItem([type,enchant])
        if (enchant == 'skill'):
            value = getItemValue('skill',0)
        elif ('Greater' in item):
            value = getItemValue('enchant',2)
        elif ('Superior' in item):
            value = getItemValue('enchant',3)
        elif ('Supreme' in item):
            value = getItemValue('enchant',4)
        else:
            value = getItemValue('enchant',1)
        shopWriter.write(str(value)+'gp - '+item+'\n')
        numTrinkets -= 1

    shopWriter.write("\nMagic Items (50-100/101-500/501-5000/5001-50000/50001+ gp):\n")
    items = []
    items.extend(makeItems(['magicitemT1'],sizeMod-1,sizeMod,False))
    items.extend(makeItems(['magicitemT2'],sizeMod-2,sizeMod-1,False))
    items.extend(makeItems(['magicitemT3'],sizeMod-3,sizeMod-2,False))
    items.extend(makeItems(['magicitemT4'],sizeMod-4,sizeMod-3,False))
    for item in items:
        shopWriter.write(item+'\n')

    numTomes = random.randint(sizeMod-4,sizeMod-3)
    if (numTomes > 0):
        shopWriter.write("\nTomes:\n")
    while (numTomes > 0):
        enchantRoll = random.randint(1,6)
        if (enchantRoll <= 3):
            enchant = 'skill'
            value = getItemValue('tome',1)
        elif (enchantRoll <= 5):
            enchant = 'stat'
            value = getItemValue('tome',2)
        else:
            enchant = 'feat'
            value = getItemValue('tome',3)
        item = randomItem(['Tome',enchant])
        shopWriter.write(str(value)+'gp - '+item+'\n')
        numTomes -= 1

    shopWriter.write("\nServices:\n")
    if (sizeMod > 2):
        boxValue = getItemValue('hitbox',0)
        shopWriter.write(str(boxValue)+"gp - Open Magic Box (contains a completely random item that will be bound to the party)\n")
    weaponBonusString = randomItem(['magicT'+str(sizeMod-1)])
    if (weaponBonusString):
        if (len(weaponBonusString) > 2 and weaponBonusString[1].isdigit()):
            maxWeaponBonus = int(weaponBonusString[1])
            for weaponBonus in range(1,maxWeaponBonus+1):
                value = getItemValue('magicbonus',weaponBonus)
                shopWriter.write(str(value)+'gp - +'+str(weaponBonus)+" weapon enchantment (+"+str(weaponBonus)+" bonus to attack and damage, bypass nonmagical weapon resistances, and can be further enchanted)\n")
        else:
            DnDUtil.printError("Invalid magic bonus string "+weaponBonusString)
    armorBonusString = randomItem(['magicT'+str(sizeMod-2)])
    if (armorBonusString):
        if (len(armorBonusString) > 2 and armorBonusString[1].isdigit()):
            maxArmorBonus = int(armorBonusString[1])
            for armorBonus in range(1,maxArmorBonus+1):
                value = getItemValue('magicbonus',armorBonus+1)
                shopWriter.write(str(value)+'gp - +'+str(armorBonus)+" armor enchantment (+"+str(armorBonus)+" bonus to AC and can be further enchanted)\n")
        else:
            DnDUtil.printError("Invalid magic bonus string "+armorBonusString)

    # generate a random enchantment to determine what tiers of enchantments should be offered for random enchanting and removing
    item = randomItem(['enchant'])
    if ('Greater' in item):
        maxEnchantTier = 2
    elif ('Superior' in item):
        maxEnchantTier = 3
    elif ('Supreme' in item):
        maxEnchantTier = 4
    else:
        maxEnchantTier = 1
    if (sizeMod > 2):
        for enchantTier in range(1,maxEnchantTier+1):
            # 25% discount for random enchantments
            value = int(getItemValue('enchant',enchantTier) * .75)
            shopWriter.write(str(value)+"gp - Random Tier "+str(enchantTier)+" Enchantment (can only be used on weapons and armor)\n")
    for enchantTier in range(1,maxEnchantTier+1):
        # Removing an enchantment costs 20% of what it costs to apply it
        value = int(getItemValue('enchant',enchantTier) * .20)
        shopWriter.write(str(value)+"gp - Remove Tier "+str(enchantTier)+" Enchantment\n")

    for itemClass in ['jewelry','robe','light','medium','heavy','shield','weapon']:
        if (itemClass in ['jewelry','robe','shield','weapon']):
            title = itemClass.capitalize()
        else:
            title = itemClass.capitalize()+" Armor"
        shopWriter.write("\n"+title+ " Enchantments:\n")
        if (itemClass == 'jewelry'):
            shopWriter.write("NOTE: All jewelry enchantments require attunement and do NOT stack with other enchantments of the same type!\n")
        if (itemClass == 'jewelry'):
            minEnchants = sizeMod-3
            maxEnchants = sizeMod-1
        elif (itemClass == 'weapon'):
            minEnchants = 2*(sizeMod-2)+1
            maxEnchants = 2*(sizeMod-1)
        else:
            minEnchants = 2*(sizeMod-2)
            maxEnchants = 2*(sizeMod-1)-1
        items = makeItems(['enchant'],minEnchants,maxEnchants,True,itemClass)
        if (itemClass == 'jewelry'):
            items.extend(makeItems(['skill'],minEnchants,maxEnchants,True,itemClass))
        for item in items:
            if ('-' in item):
                if ('Greater' in item):
                    value = getItemValue('enchant',2)
                elif ('Superior' in item):
                    value = getItemValue('enchant',3)
                elif ('Supreme' in item):
                    value = getItemValue('enchant',4)
                else:
                    value = getItemValue('enchant',1)
            else:
                value = getItemValue('skill',0)
            shopWriter.write(str(value)+"gp - "+item+'\n')
    print("Done!")
    shopWriter.close()
    webbrowser.open(MAGIC_SHOP_OUTPUT_FILE)

def createBlacksmith(size):

    print("Generating", size.capitalize(), "Blacksmith...")
    shopWriter = open(BLACKSMITH_OUTPUT_FILE,'w')

    if (size == 'small'):
        sizeMod = 2
    elif (size == 'medium'):
        sizeMod = 3
    else:
        sizeMod = 4

    simpleTable = []
    martialTable = []

    for weapon in weaponData:
        weaponClass = weaponData[weapon]['Class']
        if (weaponClass == 'simple'):
            simpleTable.append(weapon)
        elif (weaponClass == 'martial'):
            martialTable.append(weapon)
        else:
            DnDUtil.printError("Invalid class type "+weaponClass+" for weapon "+weapon)

    numSimpleWeapons = random.randint(2*sizeMod,2*(sizeMod+1))
    if (numSimpleWeapons > 0):
        shopWriter.write("Simple Weapons:\n")
    while (numSimpleWeapons > 0):
        item = getItem(weaponData,['simple'])
        shopWriter.write(makeItem(item,'weapon')+'\n')
        numSimpleWeapons -= 1

    numMartialWeapons = random.randint(2*(sizeMod-1),2*sizeMod)
    if (numMartialWeapons > 0):
        shopWriter.write("\nMartial Weapons:\n")
    while (numMartialWeapons > 0):
        item = getItem(weaponData,['martial'])
        shopWriter.write(makeItem(item,'weapon')+'\n')
        numMartialWeapons -= 1

    numArmors = random.randint(sizeMod,sizeMod+1)
    if (numArmors > 0):
        shopWriter.write("\nArmors and Shields:\n")
    while (numArmors > 0):
        item = getItem(armorData,['light','light','light','medium','medium','medium','heavy','heavy','heavy','shield','shield'])
        shopWriter.write(makeItem(item,armorData[item]['Class'])+'\n')
        numArmors -= 1

    if (sizeMod == 4):
        numWeaponUpgrades = 4
    else:
        numWeaponUpgrades = sizeMod - 1
    if (numWeaponUpgrades > 0):
        weaponModValue = getItemValue('enhanced',0)
        shopWriter.write("\nWeapon Upgrades ("+str(weaponModValue)+"gp):\nNOTE: A weapon can have up to 3 upgrades, but stacking the same upgrade costs double!\n")
        weaponUpgrades = ["Strong (increases damage by 1)","Deadly (increases crit damage multiplier by 1)","Keen (increases crit chance by 1)","Accurate (increases atk bonus by 1)"]
        while (numWeaponUpgrades > 0):
            weaponUpgradeIndex = random.randint(0,len(weaponUpgrades)-1)
            weaponUpgrade = weaponUpgrades.pop(weaponUpgradeIndex)
            shopWriter.write(weaponUpgrade+'\n')
            numWeaponUpgrades -= 1

    if (sizeMod == 4):
        numArmorUpgrades = 5
    else:
        numArmorUpgrades = sizeMod - 1
    if (numArmorUpgrades > 0):
        armorModValue = getItemValue('armormod',0)
        shopWriter.write("\nArmor Upgrades ("+str(armorModValue)+"gp):\n")
        shopWriter.write("NOTE: An armor can only have 1 upgrade!\n")
        armorUpgrades = ["Swift (robe only, +10 move speed)", "Agile (light armor only, immune to being flanked)", "Quiet (medium armor only, removes stealth disadvantage)", "Adamantine (heavy armor only, immune to being crit)"]
        if (sizeMod == 4):
            armorUpgrades.append("Mithril (any armor without an upgrade, makes the armor one class lighter: heavy->medium->light->robe)")
        while (numArmorUpgrades > 0):
            armorUpgradeIndex = random.randint(0,len(armorUpgrades)-1)
            armorUpgrade = armorUpgrades.pop(armorUpgradeIndex)
            shopWriter.write(armorUpgrade+'\n')
            numArmorUpgrades -= 1
    print("Done!")
    shopWriter.close()
    webbrowser.open(BLACKSMITH_OUTPUT_FILE)

def hitBox():
    
    weaponTable = list(weaponData.keys())
    armorTable = list(armorData.keys())
    magicItemTable = ['magicitemT1','magicitemT2','magicitemT3','magicitemT4']
    trinketTable = ['Ring','Amulet']
    tomeTable = ['Tome']
    whetstoneTable = ['Whetstone']
    boxTable = weaponTable + armorTable + magicItemTable + trinketTable + tomeTable + whetstoneTable
    numWeapons = len(weaponTable)
    numArmors = len(armorTable)

    roll = random.randint(0,len(boxTable)-1)
    item = boxTable[roll]

    if (roll < numWeapons):
        makeItem(item,'weapon',True)
    elif (roll < numWeapons + numArmors):
        makeItem(item,armorData[item]['Class'],True)
    elif (roll < numWeapons + numArmors + len(magicItemTable)):
        item = randomItem([item])
        print(item)
    elif (roll < numWeapons + numArmors + len(magicItemTable) + len(trinketTable)):
        typeRoll = random.randint(1,2)
        if (typeRoll == 1):
            type = 'skill'
        else:
            type = 'enchant'
        item = randomItem([item,type])
        print(item)
    elif (roll < numWeapons + numArmors + len(magicItemTable) + len(trinketTable) + len(tomeTable)):
        typeRoll = random.randint(1,3)
        if (typeRoll == 1):
            type = 'skill'
        elif (typeRoll == 2):
            type = 'stat'
        else:
            type = 'feat'
        item = randomItem([item,type])
        print(item)
    else:
        itemRoll = random.randint(1,4)
        if (itemRoll == 1):
            print("Deadly", item)
        elif (itemRoll == 2):
            print("Keen", item)
        elif (itemRoll == 3):
            print("Strong", item)
        else:
            print("Accurate", item)

def makeItems(Class,min,max,unique,itemClass=''):
    
    number = random.randint(min,max)
    items = []

    if (not(unique)):
        while (number > 0):
            item = stripCurse(randomItem(Class,itemClass))
            items.append(item)
            number -= 1
    else:
        if (number > 0):
            items = []
            item = stripCurse(randomItem(Class,itemClass))
            items.append(item)
            number -= 1
            while (number > 0):
                while (item in items):
                    item = stripCurse(randomItem(Class,itemClass))
                items.append(item)
                number -= 1

    return items

def makeItem(baseItem,itemClass,box=False):

    if (box):
        tripleMagicChance = 30
        doubleMagicChance = 12
        baseMagicChance = 5
        enhancedChance = 7
        enchantChance = 8
    else:
        tripleMagicChance = 50
        doubleMagicChance = 20
        baseMagicChance = 7
        enhancedChance = 9
        enchantChance = 10

    itemRules = [baseItem]

    tripleMagicRoll = random.randint(1,tripleMagicChance)
    doubleMagicRoll = random.randint(1,doubleMagicChance)
    baseMagicRoll = random.randint(1,baseMagicChance)
    if (tripleMagicRoll == tripleMagicChance):
        if (itemClass == 'weapon'):
            itemRules.append('magicT3')
        else:
            itemRules.append('magicT2')
    elif (doubleMagicRoll == doubleMagicChance):
        if (itemClass == 'weapon'):
            itemRules.append('magicT2')
        else:
            itemRules.append('magicT1')
    elif (baseMagicRoll == baseMagicChance):
        if (itemClass == 'weapon'):
            itemRules.append('magicT1')
        else:
            itemRules.append('magicT0')

    enhancedRoll = random.randint(1,enhancedChance)
    if (itemClass == 'weapon' and enhancedRoll == enhancedChance):
        itemRules.append('enhanced')

    enchantRoll = random.randint(1,enchantChance)
    if (enchantRoll == enchantChance):
        itemRules.append('enchant')

    item = randomItem(itemRules,itemClass)
    itemInfo = getEquipmentInfo(item,baseItem)
    itemDisplay = itemInfo[0]
    # if this item ended up with a modification, discount its total value by 15-25% since the enchantment and base item are random
    if (item != baseItem):
        value = int(itemInfo[1]*(1-(random.randint(15,25) / 100)))
    else:
        value = itemInfo[1]
    if (box):
        print(itemDisplay)
    else:
        itemDisplay = stripCurse(itemDisplay)
    return str(value)+' gp - '+itemDisplay

def stripCurse(item):

    curseStartIndex = item.find(' (CURSED:')
    if (curseStartIndex != -1):
        curseEndIndex = item[curseStartIndex:].find(')')
        if (curseEndIndex != -1):
            print("----------------------------------------------------------------------")
            print("Cursed Item Found:", item)
            print("----------------------------------------------------------------------")
            return item[:curseStartIndex] + item[curseEndIndex+len(item[:curseStartIndex])+1:]
        else:
            DnDUtil.printError("Could not find closing parenthesis for cursed item "+item)

    return item

def generateWeather():
    
    temperatureRoll = random.randint(1,20)
    windRoll = random.randint(1,20)
    precipitationRoll = random.randint(1,20)

    if (temperatureRoll <= 14):
        temperatureString = "Normal temperature"
    else:
        degreeVariance = random.randint(1,4) * 10
        if (temperatureRoll <= 17):
            temperatureString = str(degreeVariance) + " degrees below average"
        else:
            temperatureString = str(degreeVariance) + " degrees above average"

    if (windRoll <= 12):
        windString = "with no wind"
    elif (windRoll <= 17):
        windString = "with light wind"
    else:
        windString = "with strong wind"

    if (precipitationRoll <= 12):
        precipitationString = "and no rain/snow"
    elif (precipitationRoll <= 17):
        precipitationString = "and light rain/snow"
    else:
        precipitationString = "and heavy rain/snow"

    print(temperatureString, windString, precipitationString)

def getRandomTarget(actor):

    target = actor
    if (len(turnOrder) > 1):
        while (target == actor):
            targetIndex = random.randint(0,len(turnOrder)-1)
            target = turnOrder[targetIndex]
    return target

# wrapper function that creates and initializes the input and output lists for the recursive, worker function
def getSumPermutationsOfLength(sum,length):

    permutations = []
    initList = list(range(length))
    getSumPermutationsOfLengthRec(sum,length,initList,permutations)
    return permutations

# recursive function that does the work of iterating and returning all sum permutations
def getSumPermutationsOfLengthRec(sum,length,list,retList):

    if (length == 1):
        list[-1] = sum
        retList.append(list)
    else:
        for i in range(1,sum-length+2):
            list[len(list)-length] = i
            getSumPermutationsOfLengthRec(sum-i,length-1,copy(list),retList)

# wrapper function that creates and initializes the output list and input string for the recursive, worker function
def generateOptionsForEncounterWithSolution(solution,sortedCreatures,duplicatePermutationsDicts):

    options = []
    generateOptionsForEncounterWithSolutionRec(solution,sortedCreatures,duplicatePermutationsDicts,len(sortedCreatures),'',options)
    return options

# recursive function that does the work of generating the encounter strings given a solution
def generateOptionsForEncounterWithSolutionRec(solution,sortedCreatures,duplicatePermutationsDicts,length,optionString,retOptions):

    if (length == 0):
        difficultyIndex = solution['Difficulty']
        if (difficultyIndex == 0):
            difficultyString = DnDUtil.getPassText('Easy')
        elif (difficultyIndex == 1):
            difficultyString = DnDUtil.getDamageText('Medium')
        elif (difficultyIndex == 2):
            difficultyString = DnDUtil.getStatusText('Hard')
        elif (difficultyIndex == 3):
            difficultyString = DnDUtil.getDeathText('Lethal')
        else:
            DnDUtil.printWarning('Unknown difficulty for encounter with difficulty index '+difficultyIndex)
            difficultyString = 'Unknown'
        retOptions.append(optionString[:-1]+' ('+difficultyString+')')
    else:
        i = len(sortedCreatures)-length
        creatureList = sortedCreatures[i]
        if (len(creatureList) == 1):
            generateOptionsForEncounterWithSolutionRec(solution,sortedCreatures,duplicatePermutationsDicts,length-1,optionString+creatureList[0]+':'+str(solution['Solution'][i])+'|',retOptions)
        else:
            duplicatePermutations = duplicatePermutationsDicts[i][str(solution['Solution'][i])]
            for permutation in duplicatePermutations:
                permutationString = ''
                for j in range(0,len(permutation)):
                    permutationString += creatureList[j]+':'+str(permutation[j])+'|'
                generateOptionsForEncounterWithSolutionRec(solution,sortedCreatures,duplicatePermutationsDicts,length-1,optionString+permutationString,retOptions)

def autoGenerateEncounter(creatures):

    expDict = {}
    duplicateCRDict = {}
    # first, sort the creatures in order from highest CR to lowest CR
    for creature in creatures:
        creatureList = search([['name',creature]])
        for creatureArgs in creatureList:
            if (creatureArgs[0] == creature):
                expDict[creature] = getExpForCreature(float(creatureArgs[1]))
        if (not(creature in expDict)):
            DnDUtil.printError("Could not find data for creature "+creature)
            return

    sortedCreatures = []
    for creature in creatures:
        if (sortedCreatures):
            exp = expDict[creature]
            i = 0
            while (i < len(sortedCreatures) and exp < expDict[sortedCreatures[i]]):
                i += 1
            # store creatures with the same exp as an existing creature in a separate dictionary to simplify the number picking algorithm
            if (i < len(sortedCreatures) and exp == expDict[sortedCreatures[i]]):
                if (sortedCreatures[i] in duplicateCRDict):
                    duplicateCRDict[sortedCreatures[i]].append(creature)
                else:
                    duplicateCRDict[sortedCreatures[i]] = [creature]
            else:
                sortedCreatures.insert(i,creature)
        else:
            sortedCreatures.append(creature)

    uniqueCreatureCount = len(sortedCreatures)
    # next, determine the difficulty of the encounter
    difficultyIndex = getDifficultyIndex(True)
    if (difficultyIndex >= len(partyExpThresholds)):
        allDifficulties = True
        difficultyIndex = 0
    else:
        allDifficulties = False
    # determine all possible ways to use the given creatures to create an encounter of the given difficulty
    solutions = []
    firstLoop = True
    while (firstLoop or allDifficulties and difficultyIndex < 4):
        numList = [1]*uniqueCreatureCount
        minExp = partyExpThresholds[difficultyIndex]
        if (difficultyIndex < 3):
            maxExp = partyExpThresholds[difficultyIndex+1]
        else:
            maxExp = minExp
        lastIncrementedIndex = uniqueCreatureCount-1
        done = False
        while (not(done)):
            totalExp = getTotalExp(sortedCreatures,numList,expDict)
            if (difficultyIndex < 3):
                if (totalExp >= minExp and totalExp < maxExp):
                    solutions.append({'Solution': copy(numList), 'Difficulty': difficultyIndex})
                if (totalExp < maxExp):
                    numList[-1] += 1
                    lastIncrementedIndex = uniqueCreatureCount-1
                else:
                    if (lastIncrementedIndex == 0):
                        done = True
                    else:
                        for i in range(lastIncrementedIndex,uniqueCreatureCount):
                            numList[i] = 1
                        lastIncrementedIndex -= 1
                        numList[lastIncrementedIndex] += 1
            else:
                if (totalExp >= maxExp):
                    solutions.append({'Solution': copy(numList), 'Difficulty': difficultyIndex})
                    if (lastIncrementedIndex == 0):
                        done = True
                    else:
                        for i in range(lastIncrementedIndex,uniqueCreatureCount):
                            numList[i] = 1
                        lastIncrementedIndex -= 1
                        numList[lastIncrementedIndex] += 1
                else:
                    numList[-1] += 1
                    lastIncrementedIndex = uniqueCreatureCount-1
        firstLoop = False
        difficultyIndex += 1

    # list of dictionaries that maps each count of a creature to its corresponding duplicate permutations  
    duplicatePermutationsDicts = []
    # filter out all solutions that can't exist since each duplicate must be used at least once
    for i in range(0,uniqueCreatureCount):
        duplicatePermutationsDicts.append({})
        creature = sortedCreatures[i]
        if (creature in duplicateCRDict):
            numDuplicates = len(duplicateCRDict[creature])+1
            j = 0
            while (j < len(solutions)):
                if (solutions[j]['Solution'][i] < numDuplicates):
                    solutions.remove(solutions[j])
                else:
                    j += 1

    # fill the duplicate permutations dictionaries
    for solution in solutions:
        for i in range(0,uniqueCreatureCount):
            creature = sortedCreatures[i]
            number = solution['Solution'][i]
            if (creature in duplicateCRDict and not(str(number) in duplicatePermutationsDicts[i])):
                numDuplicates = len(duplicateCRDict[creature])+1
                # find all sum permutations using this number of duplicates
                duplicatePermutationsDicts[i][str(number)] = getSumPermutationsOfLength(number,numDuplicates)

    # load information from duplicateCRDict into sortedCreatures to prevent extra lookups while iterating through solutions
    for i in range(0,uniqueCreatureCount):
        creatureList = [sortedCreatures[i]]
        if (sortedCreatures[i] in duplicateCRDict):
            for duplicate in duplicateCRDict[sortedCreatures[i]]:
                creatureList.append(duplicate)
        sortedCreatures[i] = creatureList

    # generate the option strings for each possible solution
    options = []
    for solution in solutions:
        options.extend(generateOptionsForEncounterWithSolution(solution,sortedCreatures,duplicatePermutationsDicts))

    if (options):
        options.insert(0,'Random')
        choice = DnDUtil.chooseOption('Choose an encounter to generate',options,True)
        if (choice == 1):
            roll = random.randint(1,len(options)-1)
            encounterString = options[roll]
            print("Encounter:", encounterString)
        elif (choice < len(options)+1):
            encounterString = options[choice-1]
        else:
            encounterString = ''

        if (encounterString):
            encounterString = encounterString[:encounterString.find(' ')]
            parsedEncounterString = encounterString.split('|')
            encounterDict = {}
            # create the encounter using the option string
            for creatureString in parsedEncounterString:
                parsedCreatureString = creatureString.split(':')
                encounterDict[parsedCreatureString[0]] = int(parsedCreatureString[1])
            createEncounter('',encounterDict)
    else:
        print("There are too many creatures to make an encounter of this difficulty!")
        if (difficultyIndex < 4):
            print("Max Exp:", maxExp, end=' ')
        else:
            print("Min Exp:", minExp, end=' ')
        print("Min Encounter Exp:", getTotalExp(list(expDict.keys()),[1]*len(list(expDict.keys())),expDict))

def createEncounter(encounterFileName='',creatureDict=None,battleRoyale=False):

    global totalExp
    global totalGold
    global actorIndex
    global autoBattle
    totalExp = 0
    totalGold = 0
    actorIndex = 0
    if (creatureDict is None):
        creatureDict = {}

    if (encounterFileName):
        loadCreaturesFromFile(encounterFileName)
    elif (creatureDict):
        error = loadCreaturesFromDict(creatureDict)
        if (error):
            return
    elif (not(battleRoyale)):
        loadCreaturesFromInput()
    # only use passive abilities when NOT loading from a file since those effects will be reapplied anyway
    if (not(encounterFileName) and not(autoBattle)):
        for dataDict in [playerData,encounter]:
            # create a copy of the data dict to iterate through in case the passive abilities add new creatures
            dataDictCopy = copy(dataDict)
            for actor in dataDictCopy:
                usePassiveAbilities(actor,dataDict[actor],not('HP' in dataDict[actor]))
            del dataDictCopy

    if (not(battleRoyale)):
        print("Encounter created!")
        for creature in encounter:
            print(creature+':', str(encounter[creature]['HP'])+'/'+str(encounter[creature]['MaxHP']), "HP", "Size:", encounter[creature]['Size'])

    initializeTurnOrder(encounterFileName == '')
    # if we loaded the encounter from a file, we want to skip any start of turn effects since they would have happened before the encounter was closed
    tempTurn = encounterFileName != ''
    firstTurn = True
    endOfTurnEffects = []

    while (not(autoBattle) and encounter != {} or autoBattle and len(turnOrder) > 1 or battleRoyale):
        while (actorIndex < len(turnOrder)):

            actor = turnOrder[actorIndex]
            takenAction = False
            
            if (actor in playerData):
                actorData = playerData[actor]
                playerTurn = True
            else:
                actorData = encounter[actor]
                playerTurn = False
            
            backupEffects = []
            if (tempTurn):
                tempTurn = False
            else:
                # check for legendary actions using the previous actor as our reference point since legendary actions should trigger at the end of an actor's turn
                prevActor = turnOrder[actorIndex-1]
                for dataDict in [playerData, encounter]:
                    for itActor in dataDict:
                        if ('lactions' in dataDict[itActor]['Misc']):
                            if (itActor == prevActor):
                                dataDict[itActor]['Misc']['lactions'] = dataDict[itActor]['Misc']['maxlactions']
                            elif (not(tempTurn) and not(firstTurn) and prevActor != 'lair' and dataDict[itActor]['Misc']['lactions'] > 0 and ActorUtil.canAct(dataDict[itActor]) and (autoBattle or DnDUtil.getAnswer('Use one of '+itActor+'\'s legendary actions ('+str(dataDict[itActor]['Misc']['lactions'])+' remaining)') == 'y')):
                                if (autoBattle):
                                    actionsUsed = 1
                                else:
                                    actionsUsed = DnDUtil.chooseOption('Choose how many legendary actions to spend',list(range(1,dataDict[itActor]['Misc']['lactions']+1)))
                                dataDict[itActor]['Misc']['lactions'] -= actionsUsed
                                tempTurn = True
                                lastActor = actor
                                actor = itActor
                                actorData = dataDict[itActor]
                                playerTurn = dataDict is playerData

                if (not(tempTurn)):
                    j = 0
                    endOfTurnEffects = []
                    while (j < len(actorData['Effects']) and not(takenAction)):
                        effect = actorData['Effects'][j]
                        target = effect[0]
                        type = effect[1]
                        duration = effect[-1]
                        targetData = getData(target)
                        if (targetData is None):
                            type = 'clear'

                        if (duration == 1.5):
                            endOfTurnEffects.append([actor,effect])

                        if (duration == 1 and effect in actorData['Concentration']):
                            print(actor, "is no longer concentrating on effect", effect)
                            actorData['Concentration'].remove(effect)
                
                        if (type == 'dot'):
                            if (applyActorDot(actor,actorData,target,targetData,effect,'actorstart')):
                                takenAction = True
                            if (duration > 1):
                                effect[-1] -= 1
                                j += 1
                            elif (duration == -1):
                                j += 1
                            else:
                                print(target, "is no longer afflicted with this DoT!")
                                backupEffects.append(effect)
                                actorData['Effects'].remove(effect)
                                if (dotTiming == 'targetstart' or dotTiming == 'targetend'):
                                    dotStatusEffect = ['dot',actor,dotTiming,dotSave,dotDamageCalculation,playerDot,dotTypes]
                                    if (dotStatusEffect in targetData['Status']):
                                        targetData['Status'].remove(dotStatusEffect)
                                    else:
                                        DnDUtil.printWarning("Attempted to remove DoT status effect from "+target+" but no DoT status effect was found")
                        elif (type == 'wound'):
                            j += 1
                        elif (type == 'cc'):
                            if (duration > 1):
                                effect[-1] -= 1
                                if (effect[-1] == 0.5):
                                    print(effect[2], "will expire on", target, "at the end of this turn!")
                                elif (effect[-1] == 1):
                                    print("This is the last turn of", effect[2], "for", target)
                                elif (effect[-1] == -1):
                                    print(target, "is under the effect of", DnDUtil.getStatusText(effect[2]))
                                else:
                                    print(target, "is under the effect of", DnDUtil.getStatusText(effect[2]), "for", effect[-1], "more turns")
                                j += 1
                            elif (duration == -1):
                                j += 1
                            else:
                                dispel(effect,actor,targetData)
                                backupEffects.append(effect)
                                actorData['Effects'].remove(effect)
                        elif (type == 'grapple'):
                            print(actor, "is currently", DnDUtil.getStatusText('grappling'), target)
                            j += 1
                        elif (type == 'mc'):
                            if (duration == 1):
                                mindControl(target)
                                if (target == actor):
                                    actorData = getData(actor)
                                    playerTurn = not(playerTurn)
                                backupEffects.append(effect)
                                actorData['Effects'].remove(effect)
                            elif (duration == -1):
                                j += 1
                            else:
                                effect[-1] -= 1
                                j += 1
                        elif (type == 'ss'):
                            if (duration == 1):
                                oldType = actorData['Base']
                                shapeShift(target,targetData,effect[2])
                                backupEffects.append([target,type,oldType,duration])
                                actorData['Effects'].remove(effect)
                            elif (duration == -1):
                                j += 1
                            else:
                                effect[-1] -= 1
                                j += 1
                        elif (type == 'summon'):
                            if (duration == 1):
                                print(target, "has", DnDUtil.getDeathText('died')+'!')
                                kill(target)
                                backupEffects.append(effect)
                                actorData['Effects'].remove(effect)
                            elif (duration == -1):
                                j += 1
                            else:
                                effect[-1] -= 1
                                j += 1
                        elif (type == 'temphp'):
                            if (duration == 1):
                                tempHP = clearTempHP(targetData)
                                if (tempHP):
                                    backupEffects.append([target,type,tempHP,duration])
                                actorData['Effects'].remove(effect)
                            elif (duration == -1):
                                j += 1
                            else:
                                effect[-1] -= 1
                                j += 1
                        elif (type == 'buff'):
                            if (duration == 1):
                                if (buff(target,targetData,effect[2],-effect[3])):
                                    backupEffects.append(effect)
                                actorData['Effects'].remove(effect)
                            elif (duration == -1):
                                j += 1
                            else:
                                effect[-1] -= 1
                                j += 1
                        elif (type == 'move'):
                            if (duration == 1):
                                modMoveDict = targetData['Move']
                                targetData['Move'] = effect[2]
                                backupEffects.append([effect[0],effect[1],modMoveDict,effect[3]])
                                actorData['Effects'].remove(effect)
                                print(target+'\'s', "speed returns to normal")
                            elif (duration == -1):
                                j += 1
                            else:
                                effect[-1] -= 1
                                j += 1
                        elif (type == 'resist'):
                            if (duration == 1):
                                removeResistance(targetData,effect[2])
                                backupEffects.append(effect)
                                actorData['Effects'].remove(effect)
                                print(target, "no longer has", effect[2], "resistance!")
                            elif (duration == -1):
                                j += 1
                            else:
                                effect[-1] -= 1
                                j += 1
                        elif (type == 'vulnerability'):
                            if (duration == 1):
                                removeVulnerability(targetData,effect[2])
                                backupEffects.append(effect)
                                actorData['Effects'].remove(effect)
                                print(target, "no longer has", effect[2], "vulnerability!")
                            elif (duration == -1):
                                j += 1
                            else:
                                effect[-1] -= 1
                                j += 1
                        elif (type == 'adv'):
                            if (duration == 1):
                                removeAdvantage(targetData,effect[2])
                                backupEffects.append(effect)
                                actorData['Effects'].remove(effect)
                                print(target, "no longer has advantage on", effect[2])
                            elif (duration == -1):
                                j += 1
                            else:
                                effect[-1] -= 1
                                j += 1
                        elif (type == 'dis'):
                            if (duration == 1):
                                removeDisadvantage(targetData,effect[2])
                                backupEffects.append(effect)
                                actorData['Effects'].remove(effect)
                                print(target, "no longer has disadvantage on", effect[2])
                            elif (duration == -1):
                                j += 1
                            else:
                                effect[-1] -= 1
                                j += 1
                        elif (type == 'misc'):
                            if (duration == 1):
                                removeMiscStat(targetData,effect[2])
                                backupEffects.append(effect)
                                actorData['Effects'].remove(effect)
                                print(target, "no longer has the misc stat", effect[2])
                            elif (duration == -1):
                                j += 1
                            else:
                                effect[-1] -= 1
                                j += 1
                        elif (type == 'react'):
                            if (duration == 1):
                                targetData['CanReact'] = True
                                backupEffects.append(effect)
                                actorData['Effects'].remove(effect)
                                print(target, "can take reactions again")
                            elif (duration == -1):
                                j += 1
                            else:
                                effect[-1] -= 1
                                j += 1
                        elif (type == 'trigger'):
                            if (duration == 1):
                                del triggerData[effect[2]]
                                backupEffects.append(effect)
                                print("trigger", effect[2], "has been removed")
                                actorData['Effects'].remove(effect)
                            elif (duration == -1):
                                j += 1
                            else:
                                effect[-1] -= 1
                                j += 1
                        elif (type == 'onhit'):
                            if (duration == 1):
                                if (effect[2] in targetData['ExtraOnHitAbilities']):
                                    del targetData['ExtraOnHitAbilities'][effect[2]]
                                    backupEffects.append(effect)
                                    actorData['Effects'].remove(effect)
                                    print(target, "loses on-hit ability", effect[2])
                            elif (duration == -1):
                                j += 1
                            else:
                                effect[-1] -= 1
                                j += 1
                        elif (type == 'magicweapon'):
                            if (duration == 1):
                                removeMagicBonus(targetData,effect[2],effect[3])
                                backupEffects.append(effect)
                                actorData['Effects'].remove(effect)
                            elif (duration == -1):
                                j += 1
                            else:
                                effect[-1] -= 1
                                j += 1
                        elif (type == 'immunity'):
                            if (duration == 1):
                                removeImmunity(targetData,effect[2])
                                backupEffects.append(effect)
                                actorData['Effects'].remove(effect)
                            elif (duration == -1):
                                j += 1
                            else:
                                effect[-1] -= 1
                                j += 1
                        elif (type == 'bonusattack'):
                            if (duration == 1):
                                removeAttack(targetData)
                                backupEffects.append(effect)
                                actorData['Effects'].remove(effect)
                            elif (duration == -1):
                                j += 1
                            else:
                                effect[-1] -= 1
                                j += 1
                        elif (type == 'script'):
                            j += 1
                        elif (type == 'clear'):
                            actorData['Effects'].remove(effect)
                        else:
                            print("Illegal effect type", type, "found!")
                            actorData['Effects'].remove(effect)

                        # check for any dot effects that might be contained within a cc or grapple effect
                        if ((type == 'cc' or type == 'grapple') and effect in actorData['Effects']):
                            for subEffect in effect[3]:
                                if (subEffect[1] == 'dot'):
                                    if (applyActorDot(actor,actorData,target,targetData,subEffect,'actorstart')):
                                        takenAction = True

                    if ('survivor' in actorData['Misc']):
                        if (playerTurn or not(playerTurn) and actorData['HP'] < actorData['MaxHP'] // 2):
                            heal(actor,actorData,actorData['Misc']['survivor'])
                            if (playerTurn):
                                print(actor, "only gains this health if below half hp!")

                    if ('regen' in actorData['Misc']):
                        if ('regendisable' in actorData['Misc']):
                            print(actor, "is unable to regenerate this turn!")
                            del actorData['Misc']['regendisable']
                        else:
                            if (isinstance(actorData['Misc']['regen'],int)):
                                regenValue = actorData['Misc']['regen']
                            else:
                                regenValue = DnDUtil.getInt(actorData['Misc']['regen'].split(',')[0])
                            # heal 1 less if the creature is at 1 hp since it should have technically dropped to 0
                            if (not(playerTurn) and actorData['HP'] == 1):
                                regenValue -= 1
                            heal(actor,actorData,regenValue)

                    if ('recharge' in actorData['Misc']):
                        if (playerTurn):
                            roll = DnDUtil.getInt(input("Roll for recharge (1d6): "))
                        else:
                            roll = random.randint(1,6)
                            print(actor, "rolls a", roll, "for recharge")
                        if (roll >= actorData['Misc']['recharge']):
                            print(actor, "has recharged its ability!")

                if (actorData['Prone']):
                    print(actor, "is currently", DnDUtil.getStatusText('prone'))
                i = 0
                # check for status effects and apply ones that activate at the start of the turn
                while (i < len(actorData['Status'])):
                    statusEffect = actorData['Status'][i]
                    if (statusEffect[0] == 'grapple'):
                        print(actor, "is currently", DnDUtil.getStatusText('grappled'), "by", statusEffect[1])
                    elif (statusEffect[0] == 'dot'):
                        print(actor, "is currently under a", DnDUtil.getStatusText('DoT Effect'))
                    elif (statusEffect[0] == 'wound'):
                        print(actor, "is currently", DnDUtil.getStatusText('wounded'))
                    elif (statusEffect[0] == 'blind'):
                        print(actor, "is currently", DnDUtil.getStatusText('blinded'))
                    elif (statusEffect[0] == 'charm'):
                        print(actor, "is currently", DnDUtil.getStatusText('charmed'))
                    elif (statusEffect[0] == 'fear'):
                        print(actor, "is currently", DnDUtil.getStatusText('frightened'), "by", statusEffect[1])
                    elif (statusEffect[0] == 'invisibility'):
                        print(actor, "is currently", DnDUtil.getStatusText('invisible'))
                    elif (statusEffect[0] == 'greaterinvisibility'):
                        print(actor, "is currently", DnDUtil.getStatusText("permanently invisible"))
                    elif (statusEffect[0] == 'paralysis'):
                        print(actor, "is currently", DnDUtil.getStatusText('paralyzed'))
                    elif (statusEffect[0] == 'petrification'):
                        print(actor, "is currently", DnDUtil.getStatusText('petrified'))
                    elif (statusEffect[0] == 'poison'):
                        print(actor, "is currently", DnDUtil.getStatusText('poisoned'))
                    elif (statusEffect[0] == 'prestrain'):
                        print(actor, "is currently", DnDUtil.getStatusText('restrained'), "and slowly turning to stone")
                    elif (statusEffect[0] == 'restrain'):
                        print(actor, "is currently", DnDUtil.getStatusText('restrained'))
                    elif (statusEffect[0] == 'stun'):
                        print(actor, "is currently", DnDUtil.getStatusText('stunned'))
                    elif (statusEffect[0] == 'sleep'):
                        print(actor, "is currently", DnDUtil.getStatusText('asleep'))
                    elif (statusEffect[0] == 'incapacitate'):
                        print(actor, "is currently", DnDUtil.getStatusText('incapacitated'))
                    else:
                        print(actor, "is currently under the effect of", DnDUtil.getStatusText(statusEffect[0]))
                    # consume action if actor is incapacitated
                    if (statusEffect[0] in ['paralysis','petrification','stun','sleep','unconscious','incapacitate']):
                        takenAction = True

                    if (statusEffect[0] == 'dot'):
                        dotTiming = statusEffect[2]
                        if (dotTiming == 'targetstart'):
                            dotSave = statusEffect[3]
                            dotDamageCalculation = statusEffect[4]
                            playerDot = statusEffect[5]
                            dotTypes = statusEffect[6]
                            dotSuccess = False
                            dotHalf = False
                            if (not(dotSave) or makeSave(actor,actorData,dotSave[0],dotSave[1],dotTypes) > 0):
                                dotSuccess = True
                            elif (dotSave and dotSave[2] == 'half'):
                                print(actor, "will take half damage from this DoT")
                                dotSuccess = True
                                dotHalf = True

                            if (dotSuccess):
                                if (dotDamageCalculation.isdigit()):
                                    damage = int(dotDamageCalculation)
                                elif (playerDot):
                                    damage = DnDUtil.getInt(input('Roll for DoT damage ('+dotDamageCalculation+'): '))
                                else:
                                    damage = DnDUtil.calculate(dotDamageCalculation)

                                damage = getNetDamage(damage,actorData,actor,actorData,dotTypes,'DoT',False)
                                if (dotHalf):
                                    damage /= 2

                                if (damage > 0):
                                    if (dotTypes):
                                        primaryDotType = dotTypes[0]
                                    else:
                                        primaryDotType = ''
                                    print(actor, "takes", DnDUtil.getDamageText(damage), primaryDotType, "damage from DoT")
                                    killed = applyDamage(actor,actorData,damage,dotTypes,False)
                                    # re-evaluate whether it's a player's turn since we could have dropped concentration on a spell that mind-controlled the current actor
                                    if ('HP' in actorData):
                                        playerTurn = False
                                    else:
                                        playerTurn = True

                                    if (killed):
                                        takenAction = True
                                        break
                                    elif (not(playerTurn)):
                                        dealDamage(actor,actorData,damage)
                                        if (checkKilled(actor,actorData,damage,dotTypes,False)):
                                            print(actor, DnDUtil.getDeathText('dies'), "to DoT!")
                                            kill(actor)
                                            takenAction = True
                                            break
                        i += 1
                    elif (statusEffect[0] == 'wound'):
                        woundDamageCalculation = statusEffect[2]
                        playerWound = statusEffect[3]
                        woundDC = statusEffect[4]
                        if (woundDamageCalculation.isdigit()):
                            damage = int(woundDamageCalculation)
                        elif (playerWound and not(autoBattle)):
                            damage = DnDUtil.getInt(input('Roll for wound damage ('+woundDamageCalculation+'): '))
                        else:
                            damage = DnDUtil.calculate(woundDamageCalculation)

                        if (damage > 0):
                            print(actor, "takes", DnDUtil.getDamageText(damage), "damage from wound")
                            killed = applyDamage(actor,actorData,damage,[],False)
                            # re-evaluate whether it's a player's turn since we could have dropped concentration on a spell that mind-controlled the current actor
                            if ('HP' in actorData):
                                playerTurn = False
                            else:
                                playerTurn = True

                            if (killed):
                                takenAction = True
                                break
                            elif (not(playerTurn)):
                                dealDamage(actor,actorData,damage)
                                if (checkKilled(actor,actorData,damage,[],False)):
                                    print(actor, DnDUtil.getDeathText('dies'), "to wound!")
                                    kill(actor)
                                    takenAction = True
                                    break

                        if (not(takenAction) and (not(autoBattle) and DnDUtil.getAnswer('Use '+actor+'\'s action to make a medicine check to clear the wound') == 'y' or autoBattle and int(woundDamageCalculation[0]) > 2)):
                            takenAction = True
                            result = ActorUtil.makeCheck(actor,actorData,playerTurn,'medicine')
                            if (result >= woundDC):
                                ownerData = getData(statusEffect[1])
                                for effect in ownerData['Effects']:
                                    if (effect[0] == actor):
                                        if (effect[1] == 'wound'):
                                            actorData['Status'].remove(statusEffect)
                                            ownerData['Effects'].remove(effect)
                                            if (effect in ownerData['Concentration']):
                                                ownerData['Concentration'].remove(effect)
                                            i -= 1
                                        elif (effect[1] == 'cc'):
                                            for ccEffect in effect[3]:
                                                if (ccEffect[1] == 'wound'):
                                                    actorData['Status'].remove(statusEffect)
                                                    effect[3].remove(ccEffect)
                                                    i -= 1
                                                    if (not(effect[3])):
                                                        dispel(effect,statusEffect[1],actorData)
                                                        ownerData['Effects'].remove(effect)
                                                        if (effect in ownerData['Concentration']):
                                                            ownerData['Concentration'].remove(effect)
                                                        i -= 1
                                print(actor, "has", DnDUtil.getPassText('healed'), "its wound!")
                            else:
                                print(actor, DnDUtil.getFailText('fails'), "to heal its wound")
                        i += 1
                    elif (statusEffect[0] != 'grapple' and statusEffect[4] == 'targetstart'):
                        owner = statusEffect[1]
                        ownerData = getData(owner)
                        if (ownerData is None):
                            DnDUtil.printWarning("Attempting to remove status effect "+statusEffect[0]+" from "+actor+" but its owner "+owner+" could not be found")
                            actorData['Status'].remove(statusEffect)
                        else:
                            for effect in ownerData['Effects']:
                                if (effect[0] == actor and effect[1] == 'cc' and effect[2] == statusEffect[0] and effect[-1] == 1):
                                    dispel(effect,owner,actorData)
                                    ownerData['Effects'].remove(effect)
                                    if (effect in ownerData['Concentration']):
                                        ownerData['Concentration'].remove(effect)
                                    i -= 1
                                    break
                            i += 1
                    elif (statusEffect[0] != 'grapple' and statusEffect[4] == 'targetend'):
                        owner = statusEffect[1]
                        ownerData = getData(owner)
                        if (ownerData is None):
                            DnDUtil.printWarning("Attempting to remove status effect "+statusEffect[0]+" from "+actor+" but its owner "+owner+" could not be found")
                            actorData['Status'].remove(statusEffect)
                        else:
                            for effect in ownerData['Effects']:
                                if (effect[0] == actor and effect[1] == 'cc' and effect[2] == statusEffect[0] and effect[-1] == 1):
                                    print(statusEffect[0], "will expire on", actor, "at the end of this turn!")
                                    endOfTurnEffects.append([owner,effect])
                                    break
                            i += 1
                    elif (statusEffect[0] != 'grapple' and statusEffect[2] and statusEffect[4] == 'start'):
                        # handle death saving throw if needed
                        if (statusEffect[0] == 'unconscious' and statusEffect[2] == 'death'):
                            # only prompt for a save if actor is not stable, meaning actor has not already passed from the save 3 times
                            if (statusEffect[7] < 3):
                                saveDiff = makeSave(actor,actorData,statusEffect[2],statusEffect[3],statusEffect[8])
                                if (saveDiff == 0):
                                    statusEffect[7] += 1
                                    if (statusEffect[7] < 3):
                                        print(actor, "now has", DnDUtil.getPassText(statusEffect[7]), "successes and", DnDUtil.getFailText(statusEffect[6]), "failures")
                                    else:
                                        print(actor, "is now stable!")
                                        statusEffect[6] = 0
                                    i += 1
                                elif (saveDiff == -1):
                                    takenAction = False
                                    ownerData = getData(statusEffect[1])
                                    for effect in ownerData['Effects']:
                                        if (effect[0] == actor and effect[1] == 'cc' and effect[2] == statusEffect[0]):
                                            ownerData['Effects'].remove(effect)
                                            if (effect in ownerData['Concentration']):
                                                ownerData['Concentration'].remove(effect)
                                            break
                                    actorData['Status'].remove(statusEffect)
                                    print(actor, "is revived with 1 HP, but is still", DnDUtil.getStatusText('prone'))
                                    if (not(playerTurn)):
                                        actorData['TempHP'] = 0
                                        actorData['HP'] = 1
                                else:
                                    statusEffect[6] += 1
                                    if (statusEffect[6] < 3):
                                        print(actor, "now has", DnDUtil.getFailText(statusEffect[6]), "failures and", DnDUtil.getPassText(statusEffect[7]), "successes")
                                    else:
                                        print(actor, "has", DnDUtil.getDeathText('died')+'!')
                                        kill(actor)
                                        break
                                    i += 1
                            else:
                                i += 1
                        else:
                            threeSaveClear = statusEffect[5]
                            ownerData = getData(statusEffect[1])
                            if (makeSave(actor,actorData,statusEffect[2],statusEffect[3],statusEffect[8],False,'enemy'+statusEffect[2]+'saves' in ownerData['Disadvantages']) == 0):
                                if (threeSaveClear):
                                    statusEffect[7] += 1
                                    print(actor, "has now passed this save", DnDUtil.getPassText(statusEffect[7]), "times and failed", DnDUtil.getFailText(statusEffect[6]), "times")
                                if (not(threeSaveClear) or statusEffect[7] == 3):
                                    for effect in ownerData['Effects']:
                                        if (effect[0] == actor and effect[1] == 'cc' and effect[2] == statusEffect[0]):
                                            dispel(effect,statusEffect[1],actorData)
                                            ownerData['Effects'].remove(effect)
                                            if (effect in ownerData['Concentration']):
                                                ownerData['Concentration'].remove(effect)
                                            break
                                    print(actor, "has broken free of", statusEffect[0]+'!')
                                else:
                                    i += 1
                            else:
                                if (threeSaveClear):
                                    statusEffect[6] += 1
                                    print(actor, "has now failed this save", DnDUtil.getFailText(statusEffect[6]), "times and passed", DnDUtil.getPassText(statusEffect[7]), "times")
                                    if (statusEffect[6] == 3):
                                        print(actor, "can no longer save from this effect!")
                                        statusEffect[2] = ''
                                prestrainEffects = getCCEffectsForTarget(ownerData,actor,'prestrain')
                                if (prestrainEffects and (not(threeSaveClear) or statusEffect[6] == 3)):
                                    print(actor, "is now petrified!")
                                    statusEffect[2] = ''
                                    for effect in prestrainEffects:
                                        if (effect[1] == 'cc' and effect[2] == 'prestrain'):
                                            effect[2] = 'petrification'
                                        else:
                                            for subEffect in effect[3]:
                                                if (subEffect[1] == 'cc' and subEffect[2] == 'prestrain'):
                                                    subEffect[2] = 'petrification'
                                    for subStatusEffect in actorData['Status']:
                                        if (subStatusEffect[0] == 'prestrain' and subStatusEffect[1] == statusEffect[1]):
                                            subStatusEffect[0] = 'petrification'
                                i += 1
                    elif (statusEffect[0] != 'grapple' and statusEffect[2] and statusEffect[4] == 'action' and not(takenAction) and (autoBattle or DnDUtil.getAnswer('Use '+actor+'\'s action to make a '+statusEffect[2]+' check to clear '+statusEffect[0]) == 'y')):
                        takenAction = True
                        result = ActorUtil.makeCheck(actor,actorData,playerTurn,statusEffect[2])
                        if (result >= statusEffect[3]):
                            ownerData = getData(statusEffect[1])
                            for effect in ownerData['Effects']:
                                if (effect[0] == actor and effect[1] == 'cc' and effect[2] == statusEffect[0]):
                                    dispel(effect,statusEffect[1],actorData)
                                    ownerData['Effects'].remove(effect)
                                    if (effect in ownerData['Concentration']):
                                        ownerData['Concentration'].remove(effect)
                                    break
                            print(actor, "has", DnDUtil.getPassText("broken free"), "of", statusEffect[0]+'!')
                        else:
                            print(actor, DnDUtil.getFailText('fails'), "to break free of", statusEffect[0])
                            i += 1
                    else:
                        i += 1

            # if this is a lair turn, check to make sure the owner is not incapacitated before taking the turn
            if (actor == 'lair' and not(takenAction)):
                    takenAction = not(lairOwnerCanAct(actorData['Base']))

            while (not(takenAction)):
                updateEncounterFile()
                if (autoBattle):
                    rawInput = 'm '+getRandomTarget(actor)
                    actorData['Prone'] = False
                else:
                    rawInput = input(actor+': ')
                command = rawInput.split()
                numArgs = len(command)

                if (numArgs == 0):
                    initCommand = 'skip'
                else:
                    initCommand = command[0]

                if ((initCommand == 'j' or initCommand == 'jump' or initCommand == 'react') and not(tempTurn) and numArgs == 2):
                    target = autoComplete(command[1],False)
                    targetData = getData(target)
                    if (targetData is None):
                        print("Invalid target -", command[1])
                        initCommand = 'none'
                    elif (initCommand == 'react' and not(ActorUtil.canReact(targetData))):
                        print(target, "can't react!")
                        initCommand = 'none'
                    else:
                        tempTurn = True
                        lastActor = actor
                        actor = target
                        actorData = targetData
                        if (initCommand == 'react'):
                            actorData['Reaction'] = False
                        playerTurn = actor in playerData
                        rawInput = input(actor+': ')
                        command = rawInput.split()
                        numArgs = len(command)
                        if (numArgs == 0):
                            initCommand = 'skip'
                        else:
                            initCommand = command[0]

                if ((initCommand == 's' or initCommand == 'same') and numArgs <= 2):
                    if (numArgs == 2):
                        newRoll = command[1]
                    else:
                        newRoll = ''
                    if (actorData['LastAction']):
                        print(actor+':', actorData['LastAction'])
                        command = actorData['LastAction'].split()
                        initCommand = command[0]
                        numArgs = len(command)
                        if (playerTurn and (initCommand[-1].isdigit() and isValidAttackType(initCommand[:-1]) or not(initCommand[-1].isdigit()) and isValidAttackType(initCommand))):
                            if (newRoll):
                                command[-1] = newRoll
                            else:
                                command[-1] = input('Input new roll for this command: ')
                    else:
                        print("No previous action stored!")
                        initCommand = 'none'

                if (initCommand == 'none'):
                    None

                elif (initCommand == 'skip'):
                    takenAction = True

                elif ((initCommand == 'd' or initCommand == 'display') and (numArgs == 2 or numArgs == 3)):
                    if (command[1] == 'hp'):
                        displayHP()
                    elif (command[1] == 'order'):
                        i = 1
                        for character in turnOrder:
                            print(str(i)+'.', character)
                            i += 1
                    elif (command[1] == 'stats'):
                        if (numArgs == 3):
                            target = autoComplete(command[2],False)
                            data = getData(target)
                            if (data is None):
                                print("Invalid actor -", command[2])
                            else:
                                displayStats(data)
                        else:
                            displayStats(actorData)
                    elif (command[1] == 'trigger'):
                        displayTriggerStats()
                    else:
                        if (numArgs == 2):
                            targetData = actorData
                        else:
                            target = autoComplete(command[2],False)
                            targetData = getData(target)
                        if (targetData is None):
                            print("Invalid target -", command[2])
                        else:
                            stat = command[1][0].capitalize() + command[1][1:]
                            if (stat in targetData):
                                print(targetData[stat])
                            else:
                                stat = stat.upper()
                                if (stat in targetData):
                                    print(targetData[stat])
                                else:
                                    print("Invalid stat -", command[1])

                elif (initCommand == 'move' and (numArgs == 1 or numArgs == 2)):
                    if (numArgs == 1):
                        targetData = actorData
                    else:
                        target = autoComplete(command[1],False)
                        targetData = getData(target)
                    if (targetData is None):
                        if (numArgs == 2):
                            print("Invalid target -", command[1])
                        else:
                            print("Invalid target -", actor)
                    else: 
                        displayMoveSpeed(targetData)

                elif (initCommand == 'spell' and numArgs == 2):
                    SpellUtil.spellInfo(command[1])

                elif ((initCommand == 'sl' or initCommand == 'spl' or initCommand == 'spelllist') and (numArgs == 2 or numArgs == 3)):
                    SpellUtil.printSpellList(command[1].split(','),DnDUtil.getInt(command[2]) if numArgs == 3 else -1)

                elif ((initCommand == 'o' or initCommand == 'open') and (numArgs == 1 or numArgs == 2)):
                    if (numArgs == 1):
                        openArgs = actorData['Base']+',creature'
                    else:
                        openArgs = command[1]
                    PDFUtil.openBookmark(openArgs)

                elif (initCommand == 'b' or initCommand == 'back'):
                    takenAction = True
                    if (not(tempTurn)):
                        endOfTurnEffects = []
                        for i in range(0,len(actorData['Effects'])):
                            effect = actorData['Effects'][i]
                            if (effect[-1] != -1):
                                effect[-1] += 1

                        i = 0
                        while (i < len(backupEffects)):
                            effect = backupEffects[i]
                            target = effect[0]
                            targetData = getData(target)
                            type = effect[1]
                            if (type == 'cc'):
                                applyCC(actor,target,targetData,effect[2])
                                for ccEffect in effect[3]:
                                    if (ccEffect[1] != 'script'):
                                        applyEffect(ccEffect,actor,target,targetData)
                                        targetData = getData(target)
                                        if (target == actor):
                                            targetData = actorData
                            elif (type == 'buff'):
                                buff(target,targetData,effect[2],effect[3])
                            elif (type == 'move'):
                                oldMoveDict = targetData['Move']
                                targetData['Move'] = effect[2]
                                effect[2] = oldMoveDict
                            elif (type == 'temphp'):
                                setTempHP(target,targetData,effect[2])
                            elif (type == 'resist'):
                                addResistance(targetData,effect[2])
                            elif (type == 'vulnerability'):
                                addVulnerability(targetData,effect[2])
                            elif (type == 'adv'):
                                addAdvantage(targetData,effect[2])
                            elif (type == 'dis'):
                                addDisadvantage(targetData,effect[2])
                            elif (type == 'misc'):
                                # mark this effect to be cleared if we were unable to add the misc stat
                                if (not(addMiscStat(target,targetData,effect[2],effect[3]))):
                                    effect[0] = 'clear'
                            elif (type == 'trigger'):
                                triggerData[effect[2]] = effect[3]
                            elif (type == 'onhit'):
                                targetData['ExtraOnHitAbilities'][effect[2]] = effect[3]
                            elif (type == 'magicweapon'):
                                addMagicBonus(targetData,effect[2],effect[3])
                            elif (type == 'immunity'):
                                addImmunity(targetData,effect[2])
                            elif (type == 'react'):
                                targetData['CanReact'] = False
                            elif (type == 'mc'):
                                mindControl(target)
                                targetData = getData(target)
                                if (target == actor):
                                    actorData = targetData
                            elif (type == 'ss'):
                                oldType = targetData['Base']
                                shapeShift(target,targetData,effect[2])
                                effect[2] = oldType
                            elif (type == 'bonusattack'):
                                addAttack(targetData)

                            actorData['Effects'].append(effect)
                            i += 1

                        prevActorIndex = turnOrder.index(actor)-1
                        actorIndex = prevActorIndex-1
                        prevActor = turnOrder[prevActorIndex]
                        prevActorData = getData(prevActor)

                        for i in range(0,len(prevActorData['Effects'])):
                            effect = prevActorData['Effects'][i]
                            if (effect[-1] != -1):
                                effect[-1] += 1

                elif ((initCommand[-1].isdigit() and isValidAttackType(initCommand[:-1]) or not(initCommand[-1].isdigit()) and isValidAttackType(initCommand)) and ((numArgs == 3 and playerTurn) or ((numArgs == 2 or numArgs == 3) and not(playerTurn)))):
                    if (initCommand[-1].isdigit()):
                        attackType = initCommand[:-1]
                        atkIndex = int(initCommand[-1])
                    else:
                        attackType = initCommand
                        atkIndex = 0
                    if (attackType in ['m','flank','dm','am','gwm','ra','sa','sam','fb','fob','melee','greatweaponmaster','recklessattack','sneakattack','sneakattackm','flurryofblows']):
                        rangeIndex = 0
                    else:
                        rangeIndex = 1
                    target = command[1]
                    if (autoBattle):
                        takenAction = True
                        if (playerTurn):
                            roll = random.randint(1,20)
                        else:
                            roll = -1
                        damageSummary = attack(actor,actorData,target,attackType,rangeIndex,atkIndex,roll)
                        printDamageSummary(damageSummary)
                    else:
                        target = autoComplete(target,False)
                        if (target):
                            takenAction = True
                            if (playerTurn):
                                roll = DnDUtil.getInt(command[2])
                                atkBonus = 0
                            else:
                                roll = -1
                                if (numArgs == 3 and (command[2][0] == '+' or command[2][0] == '-')):
                                    atkBonus = DnDUtil.getInt(command[2])
                                else:
                                    atkBonus = 0
                            if (attackType == 'ra' or attackType == 'recklessattack'):
                                    addAdvantage(actorData,'meleeweaponattacks')
                            damageSummary = attack(actor,actorData,target,attackType,rangeIndex,atkIndex,roll)
                            printDamageSummary(damageSummary)
                            if (attackType == 'ra' or attackType == 'recklessattack'):
                                    removeAdvantage(actorData,'meleeweaponattacks')
                        else:
                                print("Invalid target -", command[1])

                elif ((initCommand == 'u' or initCommand == 'use' or initCommand == 'scroll') and (numArgs == 2 or numArgs == 3)):
                    if (initCommand == 'scroll'):
                        scroll = True
                    else:
                        scroll = False
                    abilityName = command[1]
                    if (numArgs == 3):
                        targets = command[2].split(',')
                    else:
                        targets = []

                    if (not(scroll)):
                        abilityName = SpellUtil.autoCompleteAbility(abilityName,actorData['UseAbilities'])

                    if (scroll or abilityName != ''):
                        if (scroll):
                            ability = ImportUtil.loadAbilityData(abilityName,[''],True)
                            if (ability and ability['Actions'] == [['']]):
                                print("Ability", abilityName, "not found!")
                        else:
                            ability = actorData['UseAbilities'][abilityName]

                        if (ability):
                            actionKey = 'Actions'
                            spellLevel = ability['Base Level']
                            if ('Scaled Actions' in ability and spellLevel > 0):
                                spellLevel = SpellUtil.inputSpellLevel(abilityName,spellLevel)
                                if (spellLevel > ability['Base Level']):
                                    actionKey = 'Scaled Actions'
                            elif (spellLevel == 0 and 'Scaled Actions' in ability):
                                actionKey = 'Scaled Actions'

                            if (scroll):
                                spellAtk = getScrollSpellAtk(spellLevel)
                                spellDC = getScrollSpellDC(spellLevel)
                            else:
                                if (ability['Attack Mod']):
                                    spellAtk = ability['Attack Mod']
                                else:
                                    spellAtk = actorData['SpellAtk']
                                if (ability['DC'] == 0):
                                    spellDC = actorData['SpellDC']
                                else:
                                    spellDC = ability['DC']

                            concentrating = isConcentrating(actorData)
                            if (checkCounterSpell(actor,actorData,playerTurn,spellLevel) and (not(ability['Concentration?']) or not(concentrating) or DnDUtil.getAnswer(actor+" is concentrating on another spell. Drop concentration in favor of this spell") == 'y')):
                            
                                if (ability['Concentration?'] and concentrating):
                                    dropConcentration(actor,actorData)
                                    # re-evaluate whether it's a player's turn since we could have dropped concentration on a spell that mind-controlled the current actor
                                    if ('HP' in actorData):
                                        playerTurn = False
                                    else:
                                        playerTurn = True
                                                           
                                actionData = deepcopy(ability[actionKey])
                                actionData = SpellUtil.replaceSpellMod(actionData,actorData)
                                actionData2 = []
                                if (actionKey == 'Scaled Actions'):
                                    if (spellLevel != 0):
                                        lvlReplacement = spellLevel-ability['Base Level']
                                    else:
                                        lvlReplacement = SpellUtil.getCantripModifierForActor(actor,actorData)
                                    actionData = SpellUtil.replaceLvl(actionData,lvlReplacement)
                                    if ('Scaled Actions2' in ability):
                                        actionData2 = SpellUtil.replaceLvl(deepcopy(ability[actionKey+'2']),lvlReplacement)
                                        actionData2 = SpellUtil.replaceSpellMod(actionData2,actorData)
                                elif ('Actions2' in ability):
                                    actionData2 = deepcopy(ability['Actions2'])
                                    actionData2 = SpellUtil.replaceSpellMod(actionData2,actorData)

                                if (ability['Use Turn?']):
                                    takenAction = True

                                if (ability['Trigger Duration']):
                                    createTriggerAbility(actorData,abilityName,ability,actor,playerTurn,spellAtk,spellDC,spellLevel,actionData,actionData2)
                                elif (not(targets)):
                                    takenAction = False
                                    print("No targets were given for this ability! Only abilities that create a trigger do not require targets.")

                                savedDamageRolls = {}
                                abilityDamageSummary = {}
                                targetIndex = 0
                                while (targetIndex < len(targets)):
                                    target = targets[targetIndex]
                                    crit = False
                                    if (target == 'self'):
                                        validTarget = True
                                        target = actor
                                        targets[targetIndex] = target
                                        targetData = actorData
                                        playerTarget = playerTurn
                                    elif (target == 'allies'):
                                        if (playerTurn):
                                            for player in playerData:
                                                targets.append(player)
                                        else:
                                            for creature in encounter:
                                                targets.append(creature)
                                        validTarget = False
                                    elif (target == 'enemies'):
                                        if (playerTurn):
                                            for creature in encounter:
                                                targets.append(creature)
                                        else:
                                            for player in playerData:
                                                targets.append(player)
                                        validTarget = False
                                    elif (target == 'all'):
                                        for creature in encounter:
                                            targets.append(creature)
                                        for player in playerData:
                                            targets.append(player)
                                        validTarget = False
                                    else:
                                        oldTarget = target
                                        target = autoComplete(target,False)
                                        targetData = getData(target)
                                        if (targetData is None):
                                            validTarget = False
                                            takenAction = False
                                            print("Invalid target -", oldTarget)
                                        else:
                                            validTarget = True
                                            targets[targetIndex] = target
                                            if ('HP' in targetData):
                                                playerTarget = False
                                            else:
                                                playerTarget = True

                                    if (validTarget):
                                        targetIndex += 1
                                        uncannyDodge = False
                                        currentActionData = actionData
                                        if (ability['Attack']):
                                            # SpellAttack Results - 0: Miss | 1: Hit | 2: Crit
                                            spellAttackResult = spellAttack(actor,actorData,target,targetData,spellAtk,playerTurn,ability['Attack'] == 'melee',spellLevel,abilityName)
                                            if (spellAttackResult > 0):
                                                success = True
                                                if (spellAttackResult == 2):
                                                    crit = True
                                                    print("This spell will crit!")
                                                if ('ud' in targetData['Misc'] and ActorUtil.canReact(targetData) and DnDUtil.getAnswer('Use '+target+'\'s reaction to use uncanny dodge on this attack') == 'y'):
                                                    uncannyDodge = True
                                                    targetData['Reaction'] = False
                                            else:
                                                if ('spellreflect' in targetData['Misc'] and (len(targets) == 1 or not(ability['Static Damage?'])) and ActorUtil.canReact(targetData) and DnDUtil.getAnswer('Use '+target+'\'s reaction to reflect '+abilityName+' to another creature within '+str(targetData['Misc']['spellreflect'])+'ft of '+target) == 'y'):
                                                    success = False
                                                    targetData['Reaction'] = False
                                                    reflectTarget = ''
                                                    while (reflectTarget == ''):
                                                        reflectTarget = autoComplete(input('Input the target for the reflected spell: '),False)
                                                    targets.append(reflectTarget)
                                                elif (actionData2 and not(ability['Save'])):
                                                    success = True
                                                    currentActionData = actionData2
                                                else:
                                                    success = False
                                        else:
                                            success = True
                                        # reveal the actor if it is invisible since a spell was cast
                                        if (ActorUtil.hasStatus(actorData,['invisibility'])):
                                            i = 0
                                            while (i < len(actorData['Status'])):
                                                statusEffect = actorData['Status'][i]
                                                if (statusEffect[0] == 'invisibility'):
                                                    ownerData = getData(statusEffect[1])
                                                    invisibilityEffects = getCCEffectsForTarget(ownerData,actor,'invisibility')
                                                    for effect in invisibilityEffects:
                                                        dispel(effect,statusEffect[1],actorData)
                                                        ownerData['Effects'].remove(effect)
                                                        if (effect in ownerData['Concentration']):
                                                            ownerData['Concentration'].remove(effect)
                                                        print(actor, "is no longer invisible!")
                                                else:
                                                    i += 1
                                    else:
                                        success = False
                                        targets.pop(targetIndex)
                                 
                                    if (success):
                                        if (ActorUtil.isImmuneToType(targetData,ability['Type'])):
                                            print(target, "is", DnDUtil.getFailText('immune'), "to", abilityName)
                                            success = False
                                        elif ('Immune' in ability['Target Type Mods'] and DnDUtil.haveCommonItem(ability['Target Type Mods']['Immune'],targetData['Type'])):
                                            print(target, "is", DnDUtil.getFailText('immune'), "to", abilityName, "since it is one of these types:", ability['Target Type Mods']['Immune'])
                                            success = False
                                        elif ('Required' in ability['Target Type Mods'] and not(DnDUtil.haveCommonItem(ability['Target Type Mods']['Required'],targetData['Type']))):
                                            print(target, "is", DnDUtil.getFailText('immune'), "to", abilityName, "since it is NOT one of these types:", ability['Target Type Mods']['Required'])
                                            success = False
                                
                                        if (success):
                                            half = False

                                            if (ability['Save'] and ability['Save Result'] != 'none'):
                                                saveDiff = makeSave(target,targetData,ability['Save'],spellDC,ability['Type'],'Advantage' in ability['Target Type Mods'] and DnDUtil.haveCommonItem(ability['Target Type Mods']['Advantage'],targetData['Type']),'Disadvantage' in ability['Target Type Mods'] and DnDUtil.haveCommonItem(ability['Target Type Mods']['Disadvantage'],targetData['Type']) or 'enemy'+ability['Save']+'saves' in actorData['Disadvantages'])
                                                if (saveDiff == 0):
                                                    if ('spell' in ability['Type'] and 'spellreflect' in targetData['Misc'] and (len(targets) == 1 or not(ability['Static Damage?'])) and ActorUtil.canReact(targetData) and DnDUtil.getAnswer('Use '+target+'\'s reaction to reflect '+abilityName+' to another creature within '+str(targetData['Misc']['spellreflect'])+'ft of '+target) == 'y'):
                                                        targetData['Reaction'] = False
                                                        reflectTarget = ''
                                                        while (reflectTarget == ''):
                                                            reflectTarget = autoComplete(input('Input the target for the reflected spell: '),False)
                                                        targets.append(reflectTarget)
                                                        success = False
                                                    elif (ability['Save Result'] == 'negates'):
                                                        if (actionData2):
                                                            currentActionData = actionData2
                                                        else:
                                                            print(target, "is unaffected by", abilityName)
                                                            success = False
                                                    elif (ability['Save Result'] == 'half'):
                                                        if ('avoidance' in targetData['Misc'] or 'evasion' in targetData['Misc'] and ability['Save'] == 'dex' or ActorUtil.hasStatus(targetData,['circleofpower']) and DnDUtil.haveCommonItem(ability['Type'],['magic','spell']) or checkShieldMaster(target,targetData,ability['Save'])):
                                                            print(target, "avoids all damage due to evasion/avoidance/circle of power/shield master")
                                                            success = False
                                                        else:
                                                            if (actionData2):
                                                                currentActionData = actionData2
                                                            print(target, "will take half damage from", abilityName)
                                                            half = True
                                                else:
                                                    if (ability['Save Result'] == 'half' and ('avoidance' in targetData['Misc'] or 'evasion' in targetData['Misc'] and ability['Save'] == 'dex')):
                                                        print(target, "will take half damage due to evasion/avoidance")
                                                        half = True
                                            else:
                                                saveDiff = -1

                                            if (success):
                                                if (ability['Attack']):
                                                    if (ActorUtil.hasStatus(targetData,['hex']) and any(effect[0] == target and effect[1] == 'cc' and effect[2] == 'hex' and effect[-1] == -1 for effect in actorData['Effects'])):
                                                        currentActionData = copy(currentActionData)
                                                        currentActionData.append(['damage','1d6','necrotic'])
                                                        print(abilityName, "will deal 1d6 additional necrotic damage due to hex!")

                                                    if (ActorUtil.hasStatus(actorData,['spiritshroud']) and (ability['Attack'] == 'melee' or DnDUtil.getAnswer('Is '+actor+' within 10ft of '+target) == 'y')):
                                                        if (not('spiritshroudtype' in actorData['Misc'])):
                                                            DnDUtil.printWarning("Missing spiritshroudtype misc data in "+actor)
                                                        elif (not('spiritshrouddamage' in actorData['Misc'])):
                                                            DnDUtil.printWarning("Missing spiritshrouddamage misc data in "+actor)
                                                        else:
                                                            currentActionData = copy(currentActionData)
                                                            currentActionData.append(['damage',actorData['Misc']['spiritshrouddamage'],actorData['Misc']['spiritshroudtype']])
                                                            print(abilityName, "will deal", actorData['Misc']['spiritshrouddamage'], "additional", actorData['Misc']['spiritshroudtype'], "damage due to spirit shroud!")
                                                            useAbility(playerTurn,'spirit shroud antiheal',[actorData['Misc']['spiritshroudtype']],1.5,[['immunity','heal']],playerTarget,targets,target,targetData,actor,actorData,0,'',0,0,0,0,False,False,False,False,{})
                                                
                                                damageSummary = useAbility(playerTurn,abilityName,ability['Type'],ability['Duration'],currentActionData,playerTarget,targets,target,targetData,actor,actorData,spellAtk,ability['Save'],spellDC,saveDiff,ability['Base Level'],spellLevel,half,crit,uncannyDodge,ability['Concentration?'],savedDamageRolls)
                                                extendDamageSummary(abilityDamageSummary,damageSummary)
                                                if (not(ability['Static Damage?'])):
                                                    savedDamageRolls.clear()
                                printDamageSummary(abilityDamageSummary)
                    else:
                        print("Use ability", command[1], "not found.")
                        print("Valid use abilities are:")
                        for ability in actorData['UseAbilities']:
                            print(ability)

                elif ((initCommand == 't' or initCommand == 'trigger') and (numArgs == 2 or numArgs == 3)):
                    abilityName = autoCompleteTrigger(command[1])
                    if (abilityName):
                        ability = triggerData[abilityName]
                        playerTrigger = ability['Player?']
                        triggerOwner = ability['Owner']
                        triggerOwnerData = getData(triggerOwner)
                        if (triggerOwnerData is None):
                            DnDUtil.printWarning("The trigger owner "+triggerOwner+" could not be found! Using the current actor "+actor+" instead")
                            triggerOwner = actor
                            triggerOwnerData = actorData

                        if (numArgs == 2):
                            targets = [actor]
                        else:
                            targets = command[2].split(',')

                        savedDamageRolls = {}
                        abilityDamageSummary = {}
                        for target in targets:
                            validTarget = False
                            if (target == 'self'):
                                target = actor
                                targetData = actorData
                                validTarget = True
                                playerTarget = playerTurn
                            elif (target == 'allies'):
                                if (playerTurn):
                                    for player in playerData:
                                        targets.append(player)
                                else:
                                    for creature in encounter:
                                        targets.append(creature)
                            elif (target == 'enemies'):
                                if (playerTurn):
                                    for creature in encounter:
                                        targets.append(creature)
                                else:
                                    for player in playerData:
                                        targets.append(player)
                            elif (target == 'all'):
                                for player in playerData:
                                    targets.append(player)
                                for creature in encounter:
                                    targets.append(creature)
                            else:
                                oldTarget = target
                                target = autoComplete(target,False)
                                targetData = getData(target)
                                if (targetData is None):
                                    print("Invalid target -", oldTarget)
                                else:
                                    validTarget = True
                                    if ('HP' in targetData):
                                        playerTarget = False
                                    else:
                                        playerTarget = True

                            if (validTarget):
                                hit = False
                                crit = False
                                uncannyDodge = False
                                actionData = ability['Actions']
                                if (ability['Attack']):
                                    # SpellAttack Results - 0: Miss | 1: Hit | 2: Crit
                                    spellAttackResult = spellAttack(triggerOwner,triggerOwnerData,target,targetData,ability['Spell Atk'],playerTrigger,ability['Attack'] == 'melee',ability['Spell Level'],abilityName)
                                    if (spellAttackResult > 0):
                                        hit = True
                                        if (spellAttackResult == 2):
                                            crit = True
                                            print("This spell will crit!")
                                        if ('ud' in targetData['Misc'] and ActorUtil.canReact(targetData) and DnDUtil.getAnswer('Use '+target+'\'s reaction to use uncanny dodge on this attack') == 'y'):
                                                uncannyDodge = True
                                                targetData['Reaction'] = False
                                    elif ('spellreflect' in targetData['Misc'] and (len(targets) == 1 or not(ability['Static Damage?'])) and ActorUtil.canReact(targetData) and DnDUtil.getAnswer('Use '+target+'\'s reaction to reflect '+abilityName+' to another creature within '+str(targetData['Misc']['spellreflect'])+'ft of '+target) == 'y'):
                                        targetData['Reaction'] = False
                                        reflectTarget = ''
                                        while (reflectTarget == ''):
                                            reflectTarget = autoComplete(input('Input the target for the reflected spell: '),False)
                                        targets.append(reflectTarget)
                                    elif ('Actions2' in ability and not(ability['Save'])):
                                        hit = True
                                        actionData = ability['Actions2']
                                else:
                                    hit = True

                                if (hit):
                                    if (ActorUtil.isImmuneToType(targetData,ability['Type'])):
                                        print(target, "is", DnDUtil.getFailText('immune'), "to", abilityName)
                                    elif ('Immune' in ability['Target Type Mods'] and DnDUtil.haveCommonItem(ability['Target Type Mods']['Immune'],targetData['Type'])):
                                        print(target, "is", DnDUtil.getFailText('immune'), "to", abilityName, "since it is one of these types:", ability['Target Type Mods']['Immune'])
                                    elif ('Required' in ability['Target Type Mods'] and not(DnDUtil.haveCommonItem(ability['Target Type Mods']['Required'],targetData['Type']))):
                                        print(target, "is", DnDUtil.getFailText('immune'), "to", abilityName, "since it is NOT one of these types:", ability['Target Type Mods']['Required'])
                                    else:
                                        success = True
                                        half = False

                                        if (ability['Save'] and ability['Save Result'] != 'none'):
                                            saveDiff = makeSave(target,targetData,ability['Save'],ability['DC'],ability['Type'],'Advantage' in ability['Target Type Mods'] and DnDUtil.haveCommonItem(ability['Target Type Mods']['Advantage'],targetData['Type']),'Disadvantage' in ability['Target Type Mods'] and DnDUtil.haveCommonItem(ability['Target Type Mods']['Disadvantage'],targetData['Type']) or 'enemy'+ability['Save']+'saves' in triggerOwnerData['Disadvantages'])
                                            if (saveDiff == 0):
                                                if ('spell' in ability['Type'] and 'spellreflect' in targetData['Misc'] and (len(targets) == 1 or not(ability['Static Damage?'])) and ActorUtil.canReact(targetData) and DnDUtil.getAnswer('Use '+target+'\'s reaction to reflect '+abilityName+' to another creature within '+str(targetData['Misc']['spellreflect'])+'ft of '+target) == 'y'):
                                                    targetData['Reaction'] = False
                                                    reflectTarget = ''
                                                    while (reflectTarget == ''):
                                                        reflectTarget = autoComplete(input('Input the target for the reflected spell: '),False)
                                                    targets.append(reflectTarget)
                                                    success = False
                                                elif (ability['Save Result'] == 'negates'):
                                                    if ('Actions2' in ability):
                                                        actionData = ability['Actions2']
                                                    else:
                                                        print(target, "is unaffected by", abilityName)
                                                        success = False
                                                elif (ability['Save Result'] == 'half'):
                                                    if ('avoidance' in targetData['Misc'] or 'evasion' in targetData['Misc'] and ability['Save'] == 'dex' or ActorUtil.hasStatus(targetData,['circleofpower']) and DnDUtil.haveCommonItem(ability['Type'],['magic','spell']) or checkShieldMaster(target,targetData,ability['Save'])):
                                                        print(target, "avoids all damage due to evasion/avoidance/circle of power/shield master")
                                                        success = False
                                                    else:
                                                        if ('Actions2' in ability):
                                                            actionData = ability['Actions2']
                                                        print(target, "will take half damage from", abilityName)
                                                        half = True
                                            else:
                                                if (ability['Save Result'] == 'half' and ('avoidance' in targetData['Misc'] or 'evasion' in targetData['Misc'] and ability['Save'] == 'dex')):
                                                    print(target, "will take half damage due to evasion/avoidance")
                                                    half = True
                                        else:
                                            saveDiff = -1

                                        if (success):
                                            if (ability['Attack']):
                                                if (ActorUtil.hasStatus(targetData,['hex']) and any(effect[0] == target and effect[1] == 'cc' and effect[2] == 'hex' and effect[-1] == -1 for effect in triggerOwnerData['Effects'])):
                                                    actionData = copy(actionData)
                                                    actionData.append(['damage','1d6','necrotic'])
                                                    print(abilityName, "will deal 1d6 additional necrotic damage due to hex!")

                                                if (ActorUtil.hasStatus(triggerOwnerData,['spiritshroud']) and (ability['Attack'] == 'melee' or DnDUtil.getAnswer('Is '+triggerOwner+' within 10ft of '+target) == 'y')):
                                                    if (not('spiritshroudtype' in triggerOwnerData['Misc'])):
                                                        DnDUtil.printWarning("Missing spiritshroudtype misc data in "+triggerOwner)
                                                    elif (not('spiritshrouddamage' in triggerOwnerData['Misc'])):
                                                        DnDUtil.printWarning("Missing spiritshrouddamage misc data in "+triggerOwner)
                                                    else:
                                                        actionData = copy(actionData)
                                                        actionData.append(['damage',triggerOwnerData['Misc']['spiritshrouddamage'],triggerOwnerData['Misc']['spiritshroudtype']])
                                                        print(abilityName, "will deal", triggerOwnerData['Misc']['spiritshrouddamage'], "additional", triggerOwnerData['Misc']['spiritshroudtype'], "damage due to spirit shroud!")
                                                        useAbility(playerTrigger,'spirit shroud antiheal',[triggerOwnerData['Misc']['spiritshroudtype']],1.5,[['immunity','heal']],playerTarget,targets,target,targetData,triggerOwner,triggerOwnerData,0,'',0,0,0,0,False,False,False,False,{})

                                            damageSummary = useAbility(playerTrigger,abilityName,ability['Type'],ability['Duration'],actionData,playerTarget,targets,target,targetData,triggerOwner,triggerOwnerData,ability['Spell Atk'],ability['Save'],ability['DC'],saveDiff,ability['Base Level'],ability['Spell Level'],half,crit,uncannyDodge,False,savedDamageRolls)
                                            extendDamageSummary(abilityDamageSummary,damageSummary)
                                            if (not(ability['Static Damage?'])):
                                                savedDamageRolls.clear()
                        printDamageSummary(abilityDamageSummary)
                    else:
                        print("Trigger", command[1], "not found.")
                        print("Valid triggers are:")
                        for ability in triggerData:
                            print(ability)

                elif (initCommand == 'aoo' and (numArgs == 2 or numArgs == 3 and command[1].count(',') == command[2].count(','))):
                    attackers = command[1].split(',')
                    if (numArgs == 3):
                        rolls = command[2].split(',')
                    else:
                        rolls = ['-1'] * len(attackers)
                    if (numArgs == 3 and checkTargets(attackers,playerData) or numArgs == 2 and checkTargets(attackers,encounter)):
                        if ('mobility' in actorData['Misc']):
                            hasMobility = True
                            addDisadvantage(actorData,'incattacks')
                        else:
                            hasMobility = False
                        damageSummary = {}
                        for j in range(0,len(attackers)):
                            attacker = attackers[j]
                            attackerData = getData(attacker)
                            if (ActorUtil.canReact(attackerData)):
                                attackerData['Reaction'] = False
                                roll = DnDUtil.getInt(rolls[j])
                                newDamageSummary = attack(attacker,attackerData,actor,'m',0,0,roll,True)
                                extendDamageSummary(damageSummary,newDamageSummary)
                                if (not(actor in turnOrder)):
                                    break
                            else:
                                print(attacker, "can't react!")
                        printDamageSummary(damageSummary)
                        if (hasMobility):
                            removeDisadvantage(actorData,'incattacks')
                        
                elif (initCommand == 'attack' and (numArgs == 4 and command[1] in playerData or not(command[1] in playerData) and numArgs == 3)):
                    if (command[1] in playerData):
                        attacker = command[1]
                        attackerData = playerData[attacker]
                        roll = DnDUtil.getInt(command[3])
                    else:
                        attacker = autoComplete(command[1],True)
                        if (attacker):
                            attackerData = encounter[attacker]
                        else:
                            print("Invalid attacker -", command[1])
                        roll = -1
                    if (attacker):
                        target = autoComplete(command[2],False)
                        if (target):
                            damageSummary = attack(attacker,attackerData,target,'m',0,0,roll)
                            printDamageSummary(damageSummary)
                        else:
                            print("Invalid target -", command[2])

                elif ((initCommand == 'dmg' or initCommand == 'damage') and (numArgs == 3 or numArgs == 4)):
                    targets = command[1].split(',')
                    if (numArgs == 4):
                        types = command[3].split(',')
                    else:
                        types = []

                    if (playerTurn):
                        damage = DnDUtil.getInt(command[2])
                    else:
                        damage = DnDUtil.calculate(command[2])

                    for target in targets:
                        oldTarget = target
                        target = autoComplete(target,False)
                        targetData = getData(target)
                        if (targetData is None):
                            print("Invalid target - ", oldTarget)
                        else:
                            totalDamage = getNetDamage(damage,actorData,target,targetData,types,'this command',False)
                            if (totalDamage > 0):
                                print(target, "took", DnDUtil.getDamageText(totalDamage), "damage")
                                killed = applyDamage(target,targetData,totalDamage,types,False,False)
                                # re-evaluate whether it's a player's turn since we could have dropped concentration on a spell that mind-controlled the current actor
                                if ('HP' in actorData):
                                    playerTurn = False
                                else:
                                    playerTurn = True
                                if (not(killed) and 'HP' in targetData):
                                    dealDamage(target,targetData,totalDamage)
                                    if (checkKilled(target,targetData,totalDamage,types,False)):
                                        print(target, "has", DnDUtil.getDeathText('died')+'!')
                                        kill(target)

                elif (initCommand == 'roll' and (numArgs == 1 or numArgs == 2)):
                    if (numArgs == 1):
                        rollString = '1d20'
                    else:
                        rollString = command[1]
                    print(DnDUtil.calculate(rollString))

                elif ((initCommand == 'g' or initCommand == 'grapple') and numArgs == 2):
                    target = command[1]
                    if (playerTurn):
                        target = autoComplete(target,not(battleRoyale))

                    if (playerTurn and target != '' or not(playerTurn) and target in playerData):
                        targetData = getData(target)
                        if (isGrappling(actorData,target)):
                            if (DnDUtil.getAnswer("Do you want to release the grapple") == 'y'):
                                breakGrapple(actor,actorData,target,targetData)
                            else:
                                if (numArgs == 3):
                                    pRoll = DnDUtil.getInt(command[2])
                                else:
                                    pRoll = -1
                                grapple(actor,actorData,0,target,targetData,playerTurn,not('HP' in targetData))
                        else:
                            if (not(ActorUtil.isImmuneToType(targetData,['grapple']))):
                                if (actorData['SizeMod'] - targetData['SizeMod'] >= -1):
                                    if (len(actorData['Atk'][0][0]) == 1):
                                        takenAction = True

                                    if (grapple(actor,actorData,0,target,targetData,playerTurn,not('HP' in targetData)) == actor):
                                        grappleEffects = []
                                        startGrapple(actor,actorData,target,targetData,0,grappleEffects)
                                        actorData['Effects'].append([target,'grapple',[],grappleEffects,-1])
                                else:
                                    print(target, "is too large for", actor, "to grapple!")
                            else:
                                print(target, "is", DnDUtil.getFailText('immune'), "to being grappled!")
                    else:
                        print("Invalid target -", command[1])

                elif ((initCommand == 'esc' or initCommand == 'escape') and numArgs == 1):
                    if (ActorUtil.hasStatus(actorData,['grapple'])):
                        grapplerActorList = []
                        escapeDCList = []
                        for statusEffect in actorData['Status']:
                            if (statusEffect[0] == 'grapple'):
                                grapplerActorList.append(statusEffect[1])
                                escapeDCList.append(statusEffect[2])
                        option = DnDUtil.chooseOption("Choose a grapple to escape",grapplerActorList)
                        grappleOwner = grapplerActorList[option-1]
                        escapeDC = escapeDCList[option-1]
                        grappleOwnerData = getData(grappleOwner)
                        if (grappleOwnerData is None):
                            print("Invalid grapple owner -", grappleOwner)
                        else:
                            takenAction = True
                            if (grapple(grappleOwner,grappleOwnerData,escapeDC,actor,actorData,not('HP' in grappleOwnerData),playerTurn) == actor):
                                breakGrapple(grappleOwner,grappleOwnerData,actor,actorData)
                    else:
                        print(actor, "is not currently grappled!")

                elif (initCommand == 'aid' and numArgs == 3):
                    aidTarget = command[1]
                    attackTarget = command[2]
                    if (not(playerTurn)):
                        aidTarget = autoComplete(aidTarget,True)
                        if (not(attackTarget in playerData)):
                            attackTarget = ''
                    else:
                        if (not(aidTarget in playerData)):
                            aidTarget = ''
                        attackTarget = autoComplete(attackTarget,True)
                    aidTargetData = getData(aidTarget)
                    
                    if (not(aidTargetData is None) and attackTarget != ''):
                        takenAction = True
                        addAdvantage(aidTargetData,'next'+attackTarget)
                        actorData['Effects'].append([aidTarget,'adv','next'+attackTarget,1])
                        print(aidTarget, "will have advantage on its next attack against", attackTarget, "next turn")
                    else:
                        if (aidTargetData is None):
                            print("Invalid aid target -", command[1])
                        if (attackTarget == ''):
                            print("Invalid attack target -", command[2])

                elif (initCommand == 'dodge'):
                    if (ActorUtil.hasStatus(actorData,['grapple','restrain','prestrain'])):
                        print(actor, "can't dodge because it is", DnDUtil.getStatusText('grappled'), "or", DnDUtil.getStatusText('restrained')+'!')
                    elif (all(speed == 0 for speed in list(actorData['Move'].values()))):
                        print(actor, "can't dodge because its speed is 0!")
                    else:
                        takenAction = True
                        addDisadvantage(actorData,'incattacks')
                        actorData['Effects'].append([actor,'dis','incattacks',1])
                        addAdvantage(actorData,'dexsaves')
                        actorData['Effects'].append([actor,'adv','dexsaves',1])
                        print("Attacks made against", actor, "until next turn have disadvantage!")

                elif (initCommand == 'shove' and numArgs == 2):
                    target = command[1]
                    if (playerTurn):
                        target = autoComplete(target,not(battleRoyale))
                    targetData = getData(target)
                    if (targetData is None):
                        print("Invalid target -", command[1])
                    else:
                        takenAction = True
                        shove(actor,actorData,playerTurn,target,targetData,not('HP' in targetData))

                elif (initCommand == 'rage' and numArgs == 1):
                    if ('pr' in actorData['Misc']):
                        rageDuration = -1
                    else:
                        rageDuration = 10
                    rageEffects = []
                    applyCC(actor,actor,actorData,'rage')
                    addAdvantage(actorData,'str')
                    rageEffects.append([actor,'adv','str'])
                    addAdvantage(actorData,'strsaves')
                    rageEffects.append([actor,'adv','strsaves'])
                    if (playerTurn and PLAYERS_ADD_BONUS):
                        rageBonus = 0
                    elif ('rage' in actorData['Misc']):
                        rageBonus = actorData['Misc']['rage']
                    else:
                        rageBonus = DnDUtil.getInt(input('Input rage damage bonus: '))
                    buff(actor,actorData,'dmg',rageBonus)
                    rageEffects.append([actor,'buff','dmg',rageBonus])
                    for resistance in ['slashing','bludgeoning','piercing']:
                        addResistance(actorData,resistance)
                        rageEffects.append([actor,'resist',resistance])
                    actorData['Effects'].append([actor,'cc','rage',rageEffects,rageDuration])
                    print(actor, "is enraged!")

                elif (initCommand == 'frenzy' and numArgs == 1):
                    addAttack(actorData)
                    actorData['Effects'].append([actor,'bonusattack',10])
                    print(actor, "goes into a frenzy, gaining an extra attack!")

                elif (initCommand == 'dispel' and numArgs == 2):
                    targets = command[1].split(',')
                    for target in targets:
                        oldTarget = target
                        target = autoComplete(target,False)
                        targetData = getData(target)
                        if (targetData is None):
                            print("Target", oldTarget, "not found")
                        else:
                            ownerDataList = []
                            effectList = []
                            for dataDict in [playerData,encounter]:
                                for itActor in dataDict:
                                    for effect in dataDict[itActor]['Effects']:
                                        if (effect[0] == target):
                                            ownerDataList.append([itActor])
                                            effectList.append(effect)
                                            if (effect[1] == 'cc' or effect[1] == 'grapple'):
                                                for ccEffect in effect[3]:
                                                    ownerDataList.append([itActor,effect[3]])
                                                    effectList.append(ccEffect)
                            done = False
                            while (effectList and not(done)):
                                choice = DnDUtil.chooseOption('Choose an effect to dispel',effectList,True)
                                if (choice != len(effectList)+1):
                                    effect = effectList.pop(choice-1)
                                    ownerListData = ownerDataList.pop(choice-1)
                                    owner = ownerListData[0]
                                    if (effect[0] == target or effect[0] in turnOrder):
                                        if (effect[0] != target):
                                            targetData = getData(effect[0])
                                        dispel(effect,owner,targetData,True)
                                    
                                        if (len(ownerListData) == 2):
                                            ownerListData[1].remove(effect)
                                        else:
                                            if (effect[1] == 'cc' or effect[1] == 'grapple'):
                                                for i in range(0,len(effect[3])):
                                                    effectList.pop(choice-1)
                                                    ownerDataList.pop(choice-1)
                                            ownerData = getData(owner)
                                            # don't remove the effect if it was a grapple since breakGrapple will handle this
                                            if (effect[1] != 'grapple'):
                                                ownerData['Effects'].remove(effect)
                                            if (effect in ownerData['Concentration']):
                                                ownerData['Concentration'].remove(effect)
                                        # if our target died due to dispelling a summon effect, move on to the next target
                                        if (not(target in turnOrder)):
                                            done = True
                                    else:
                                        DnDUtil.printWarning("Could not find target "+effect[0])
                                        done = True
                                else:
                                    done = True
                            del ownerDataList
                            del effectList
                    # refresh playerTurn since we could have dispelled a mind control effect
                    playerTurn = not('HP' in actorData)

                elif (initCommand == 'turn' and numArgs == 2):
                    if ('turn' in actorData['Misc']):
                        turnLevel = actorData['Misc']['turn']
                    else:
                        turnLevel = actorData['CR']
                    targets = command[1].split(',')
                    takenAction = True
                    for target in targets:
                        oldTarget = target
                        target = autoComplete(target,False)
                        targetData = getData(target)
                        if (targetData is None):
                            print("Target", oldTarget, "not found!")
                        elif (not('undead' in targetData['Type'])):
                            print(target, "is not undead!")
                        else:
                            if (ActorUtil.isImmuneToType(targetData,['turning'])):
                                print(target, "is", DnDUtil.getFailText('immune'), "to turning!")
                            elif (makeSave(target,targetData,'wis',actorData['SpellDC'],['turning'],False,'enemywissaves' in actorData['Disadvantages']) > 0):
                                cr = targetData['CR']
                                if (cr <= 4 and turnLevel >= 17 or cr <= 3 and turnLevel >= 14 or cr <= 2 and turnLevel >= 11 or cr <= 1 and turnLevel >= 8 or cr <= 0.5 and turnLevel >= 5):
                                    print(target, "is", DnDUtil.getDeathText('destroyed'), "instead of being turned!")
                                    kill(target)
                                else:
                                    print(target, "must use its action to flee from", actor, "while turned or dodge if nowhere to move")
                                    applyCC(actor,target,targetData,'turning')
                                    actorData['Effects'].append([target,'cc','turning',[],10])

                elif ((initCommand == 'dc' or initCommand == 'dropconcentration') and numArgs <= 2):
                    if (numArgs == 1):
                        target = actor
                    else:
                        target = autoComplete(command[1],False)
                        
                    if (target != ''):
                        print("Clearing all concentration effects for", target)
                        targetData = getData(target)
                        dropConcentration(target,targetData,True)
                        # re-evaluate whether it's a player's turn since we could have dropped concentration on a spell that mind-controlled the current actor
                        if (actor == target):
                            if ('HP' in actorData):
                                playerTurn = False
                            else:
                                playerTurn = True
                    else:
                        print("Invalid target -", command[1])

                elif ((initCommand == 'adv' or initCommand == 'dis') and (numArgs == 3 or numArgs == 4)):
                    target = autoComplete(command[1],False)
                    targetData = getData(target)
                    if (targetData is None):
                        print("Invalid target -", command[1])
                    else:
                        type = command[2]
                        if (numArgs == 3):
                            duration = -1
                        else:
                            duration = DnDUtil.getInt(command[3])
                        if (initCommand == 'adv'):
                            addAdvantage(targetData,type)
                        else:
                            addDisadvantage(targetData,type)
                        actorData['Effects'].append([target,initCommand,type,duration])
                        print(target, "has", initCommand, "on", type, "for", duration, "turns")

                elif (initCommand == 'buff' and (numArgs == 5 or numArgs == 4)):
                    type = command[2]
                    target = autoComplete(command[1],False)
                    targetData = getData(target)
                    if (targetData is None):
                        print("Invalid target -", command[1])
                    else:
                        value = DnDUtil.getInt(command[3])
                        if (numArgs == 5):
                            duration = DnDUtil.getInt(command[4])
                        else:
                            duration = -1
                    
                        if (buff(target,targetData,type,value)):        
                            actorData['Effects'].append([target,'buff',type,value,duration])
                            print(target, "will get a", value, "bonus to", type, "for", duration, "turns")

                elif (initCommand == 'dot' and numArgs >= 4):
                    target = autoComplete(command[1],False)
                    if (target != ''):
                        dotTypeStartIndex = 4
                        dotTypeEndIndex = 0
                        dotDamage = command[2]
                        dotTiming = command[3]
                        if (numArgs >= 5 and command[-1].isdigit()):
                            dotDuration = int(command[-1])
                            dotTypeEndIndex = -1
                        else:
                            dotDuration = -1
                        if (numArgs >= 7 and (command[6] == 'negates' or command[6] == 'half')):
                            dotTypeStartIndex = 7
                            if (not(command[5].isdigit())):
                                DnDUtil.printError("A save was given for this dot ability, but no DC was found")
                                dotSave = []
                            else:
                                dotSave = [command[4],int(command[5]),command[6]]
                        else:
                            dotSave = []
                        if (dotTypeEndIndex):
                            dotTypes = command[dotTypeStartIndex:dotTypeEndIndex]
                        else:
                            dotTypes = command[dotTypeStartIndex:]
                
                        print("A DoT has been applied to", target)
                        actorData['Effects'].append([target,'dot',dotTiming,dotSave,dotDamage,playerTurn,dotTypes,dotDuration])
                        if (dotTiming == 'targetstart' or dotTiming == 'targetend'):
                            targetData = getData(target)
                            targetData['Status'].append(['dot',actor,dotTiming,dotSave,dotDamage,playerTurn,dotTypes])
                    else:
                        print("Invalid target -", command[1])

                elif (initCommand == 'cc' and (numArgs == 3 or numArgs == 4)):
                    target = autoComplete(command[1],False)
                    if (target != ''):
                        targetData = getData(target)
                        type = command[2]
                        if (numArgs == 3):
                            duration = -1
                        elif (command[3] == 'actorstart'):
                            duration = 1
                        elif (command[3] == 'actorend'):
                            duration = 1.5
                        else:
                            duration = DnDUtil.getInt(command[3])
                        applyCC(actor,target,targetData,type)
                        actorData['Effects'].append([target,'cc',type,[],duration])
                        print(target, "will be under the effect of", DnDUtil.getStatusText(type), "for", duration, "turns")
                    else:
                        print("Invalid target -", command[1])

                elif (initCommand == 'prone' and (numArgs == 1 or numArgs == 2)):
                    if (numArgs == 1):
                        target = actor
                        targetData = actorData
                    else:
                        target = autoComplete(command[1],False)
                        targetData = getData(target)
                    if (not(targetData is None)):
                        knockProne(target,targetData)
                    else:
                        print("Invalid target -", command[1])
                        
                elif (initCommand == 'stand' and (numArgs == 1 or numArgs == 2)):
                    if (numArgs == 1):
                        target = actor
                        targetData = actorData
                    else:
                        target = autoComplete(command[1],False)
                        targetData = getData(target)
                    if (not(targetData is None)):
                        targetData['Prone'] = False    
                        print(target, "is no longer", DnDUtil.getStatusText('prone')+'!')
                    else:
                        print("Invalid target -", command[1])
                        
                elif (initCommand == 'clear' and (numArgs == 1 or numArgs == 2)):
                    if (numArgs == 1):
                        target = actor
                        targetData = actorData
                    else:
                        target = autoComplete(command[1],False)
                        targetData = getData(target)
                    if (not(targetData is None)):
                        if (targetData['Status']):
                            i = 0
                            while (i < len(targetData['Status'])):
                                statusEffect = targetData['Status'][i]
                                if (statusEffect[0] == 'grapple'):
                                    print("Please use the escape command to clear grapples!")
                                    i += 1
                                else:
                                    ownerData = getData(statusEffect[1])
                                    ccEffects = getCCEffectsForTarget(ownerData,target,statusEffect[0])
                                    for effect in ccEffects:
                                        dispel(effect,statusEffect[1],targetData)
                                        ownerData['Effects'].remove(effect)
                                        if (effect in ownerData['Concentration']):
                                            ownerData['Concentration'].remove(effect)
                                    if (not(ccEffects)):
                                        i += 1
                            if (targetData['Status']):
                                unremovedEffects = []
                                for statusEffect in targetData['Status']:
                                    if (statusEffect[0] != 'grapple'):
                                        print(unremovedEffects.append(statusEffect))
                                if (unremovedEffects):
                                    DnDUtil.printWarning("Failed to clear these effects: "+str(unremovedEffects))
                        else:
                            print(target, "is not affected by any cc!")

                elif (initCommand == 'heal' and numArgs == 3):
                    targets = command[1].split(',')
                    if (playerTurn):
                        value = DnDUtil.getInt(command[2])
                    else:
                        value = DnDUtil.calculate(command[2])
                    for target in targets:
                        oldTarget = target
                        target = autoComplete(target,False)
                        targetData = getData(target)
                        if (targetData is None):
                            print("Target", oldTarget, "not found!")
                        else:
                            heal(target,targetData,value)
                      
                elif (initCommand == 'kill' and numArgs == 2):
                    targets = command[1].split(',')
                    for target in targets:
                        oldTarget = target
                        target = autoComplete(target,False)
                        targetData = getData(target)
                        if (targetData is None):
                            print("Target", oldTarget, "not found!")
                        else:
                            print(target, "is", DnDUtil.getDeathText('dead'))
                            kill(target)

                elif (initCommand == 'death' and numArgs == 2):
                    target = autoComplete(command[1],False)
                    targetData = getData(target)
                    if (targetData is None):
                        print("Target", command[1], "not found!")
                    else:
                        # ensure that the target isn't already under this effect
                        found = False
                        for statusEffect in targetData['Status']:
                            if (statusEffect[0] == 'unconscious' and statusEffect[2] == 'death'):
                                found = True
                                break
                        if (found):
                            print(target, "is already under this effect!")
                        else:
                            print(target, "has fallen to the ground", DnDUtil.getStatusText('unconscious')+'!')
                            dropConcentration(target,targetData)
                            targetData['Prone'] = True
                            applyCC(target,target,targetData,'unconscious',['death'],'death',10,'start',True)
                            targetData['Effects'].append([target,'cc','unconscious',[],-1])
                            # for creatures, set temp hp to max so that no amount of damage will kill it while unconscious and avoid bugs when healing
                            if ('HP' in targetData):
                                targetData['TempHP'] = sys.maxsize

                elif ((initCommand == 'add' or initCommand == 'adde' or initCommand == 'adda') and numArgs == 3):
                    type = command[1]
                    number = DnDUtil.getInt(command[2])
                    if (initCommand == 'add'):
                        response = ''
                        while (response != 'ally' and response != 'enemy'):
                            response = input("Do you want to add an enemy or an ally? ")
                        if (response == 'enemy'):
                            addEnemy = True
                        else:
                            addEnemy = False
                    elif (initCommand == 'adde'):
                        addEnemy = True
                    else:
                        addEnemy = False

                    names = add(type,number,addEnemy)
                    for name in names:
                        newCreatureData = getData(name)
                        initRoll = ActorUtil.makeRoll(name,not(addEnemy),DnDUtil.haveCommonItem(['init','dex','checks'],newCreatureData['Advantages']),DnDUtil.haveCommonItem(['init','dex','checks'],newCreatureData['Disadvantages']),newCreatureData['Init'],True,'Roll for initiative')
                        if (ActorUtil.hasStatus(newCreatureData,['giftofalacrity'])):
                            if (addEnemy):
                                goaRoll = random.randint(1,8)
                                print(name, "rolls a", goaRoll, "for gift of alacrity bonus")
                            else:
                                goaRoll = DnDUtil.getInt(input('Roll for gift of alacrity bonus (1d8): '))
                            initRoll += goaRoll
                        newCreatureData['InitRoll'] = initRoll
                        insertNewActor(name,newCreatureData)

                elif ((initCommand == 'mc' or initCommand == 'mindcontrol') and (numArgs == 2 or numArgs == 3)):
                    target = autoComplete(command[1],False)
                    if (numArgs == 2):
                        duration = -1
                    else:
                        duration = DnDUtil.getInt(command[2])
                    if (mindControl(target)):
                        actorData['Effects'].append([target,'mc',duration])
                        if (target == actor):
                            actorData = getData(actor)
                            playerTurn = not(playerTurn)
                    else:
                        print("Invalid target -", command[1])

                elif ((initCommand == 'ss' or initCommand == 'shapeshift') and (numArgs == 2 or numArgs == 3)):
                    if (numArgs == 3):
                        duration = DnDUtil.getInt(command[2])
                    else:
                        duration = -1

                    oldType = actorData['Base']
                    shapeShift(actor,actorData,command[1])
                    actorData['Effects'].append([actor,'ss',oldType,duration])

                elif ((initCommand == 'a' or initCommand == 'abilities') and numArgs <= 2):
                    if (numArgs == 1):
                        target = actor
                    else:
                        target = autoComplete(command[1],False)

                    if (target in encounter):
                        print(encounter[target]['AbilitiesInfo'])
                    elif (target in playerData):
                        for ability in playerData[target]['UseAbilities']:
                            print(ability)
                            print("Base Level:", playerData[target]['UseAbilities'][ability]['Base Level'])
                            if (playerData[target]['UseAbilities'][ability]['Save']):
                                print("Save:", playerData[target]['UseAbilities'][ability]['Save'], playerData[target]['UseAbilities'][ability]['DC'], playerData[target]['UseAbilities'][ability]['Save Result'])
                            print("Attack:", playerData[target]['UseAbilities'][ability]['Attack'], "Concentration?:", playerData[target]['UseAbilities'][ability]['Concentration?'], "UT?:", playerData[target]['UseAbilities'][ability]['Use Turn?'], "SD?:", playerData[target]['UseAbilities'][ability]['Static Damage?'], "Trigger Duration:", playerData[target]['UseAbilities'][ability]['Trigger Duration'], "Type:", playerData[target]['UseAbilities'][ability]['Type'], "Duration:", playerData[target]['UseAbilities'][ability]['Duration'])
                            print("Actions:", playerData[target]['UseAbilities'][ability]['Actions'])
                            if ('Actions2' in playerData[target]['UseAbilities'][ability]):
                                print("Actions 2:", playerData[target]['UseAbilities'][ability]['Actions2'])
                            if ('Scaled Actions' in playerData[target]['UseAbilities'][ability]):
                                print("Scaled Actions:", playerData[target]['UseAbilities'][ability]['Scaled Actions'])
                                if ('Scaled Actions2' in playerData[target]['UseAbilities'][ability]):
                                    print("Scaled Actions 2:", playerData[target]['UseAbilities'][ability]['Scaled Actions2'])
                    else:
                        print("target", target, "not found")

                elif (initCommand == 'sethp' and numArgs == 3):
                    target = autoComplete(command[1],True)
                    if (target):
                        newHP = DnDUtil.getInt(command[2])
                        if (newHP > 0):
                            encounter[target]['HP'] = encounter[target]['MaxHP'] = newHP
                        else:
                            print("HP cannot be set below 1!")
                    else:
                        print("Invalid target -", command[1])

                elif (initCommand == 'addtemphp' and numArgs == 3):
                    target = autoComplete(command[1],True)
                    if (target):
                        encounter[target]['TempHP'] += DnDUtil.getInt(command[2])
                    else:
                        print("Invalid target - ", command[1])

                elif ((initCommand == 'str' or initCommand == 'dex' or initCommand == 'con' or initCommand == 'int' or initCommand == 'wis' or initCommand == 'cha') and (numArgs == 3  or numArgs == 2)):
                    saveMakers = command[1].split(',')
                    if (numArgs == 2 and checkTargets(saveMakers,encounter)):
                        for saveMaker in saveMakers:
                            advantage = 'saves' in encounter[saveMaker]['Advantages'] or initCommand+'saves' in encounter[saveMaker]['Advantages']
                            disadvantage = 'saves' in encounter[saveMaker]['Disadvantages'] or initCommand+'saves' in encounter[saveMaker]['Disadvantages']
                            roll = ActorUtil.makeRoll(saveMaker,False,advantage,disadvantage,encounter[saveMaker][initCommand.capitalize()+'Save'])
                            print(saveMaker, "result is", roll)
                    elif (numArgs == 3 and checkTargets(saveMakers,playerData)):
                        rolls = command[2].split(',')
                        if (len(rolls) == len(saveMakers)):
                            i = 0
                            for saveMaker in saveMakers:
                                advantage = 'saves' in playerData[saveMaker]['Advantages'] or initCommand+'saves' in playerData[saveMaker]['Advantages']
                                disadvantage = 'saves' in playerData[saveMaker]['Disadvantages'] or initCommand+'saves' in playerData[saveMaker]['Disadvantages']
                                roll = DnDUtil.getInt(getAdvantageDisadvantageRoll(rolls[i],advantage,disadvantage))
                                print(saveMaker, "result is", roll+playerData[saveMaker][initCommand.capitalize()+'Save'])
                                i += 1
                        else:
                            print("Invalid number of rolls!")
                    else:
                        "Invalid Command"

                elif (initCommand == 'addmisc' and (numArgs == 3 or numArgs == 4)):
                    targets = command[1].split(',')
                    miscStat = command[2]
                    if (numArgs == 4):
                        miscArg = command[3]
                    else:
                        miscArg = '0'
                    for target in targets:
                        oldTarget = target
                        target = autoComplete(target,False)
                        targetData = getData(target)
                        if (targetData is None):
                            print("Target", oldTarget, "not found!")
                        else:
                            addMiscStat(target,targetData,miscStat,miscArg)

                elif (initCommand == 'editmisc' and numArgs == 4):
                    targets = command[1].split(',')
                    miscStat = command[2]
                    if (command[3].isdigit()):
                        miscArg = int(command[3])
                    else:
                        miscArg = command[3]
                    for target in targets:
                        oldTarget = target
                        target = autoComplete(target,False)
                        targetData = getData(target)
                        if (targetData is None):
                            print("Target", oldTarget, "not found!")
                        else:
                            hasStat = miscStat in targetData['Misc']
                            if (hasStat or not(hasStat) and DnDUtil.getAnswer(target+' does not have this stat. Would you like to add it') == 'y'):
                                targetData['Misc'][miscStat] = miscArg

                elif (initCommand == 'delmisc' and numArgs == 3):
                    targets = command[1].split(',')
                    miscStat = command[2]
                    for target in targets:
                        oldTarget = target
                        target = autoComplete(target,False)
                        targetData = getData(target)
                        if (targetData is None):
                            print("Target", oldTarget, "not found!")
                        elif (miscStat in targetData['Misc']):
                            del targetData['Misc'][miscStat]
                        else:
                            print(target, "does not have this stat!")

                elif (initCommand == 'h' or initCommand == 'help'):
                    if (numArgs > 1):
                        help(command[1],True)
                    else:
                        help('',True)

                elif (initCommand == 'done'):
                    takenAction = True
                    tempTurn = True
                    if (battleRoyale):
                        battleRoyale = False
                    else:
                        encounter.clear()

                else:
                    print("Invalid Command")

                # if our current actor died during this turn's action, ensure that the turn ends
                if (not(actor in turnOrder)):
                    takenAction = True
                if (not(initCommand in ['skip','s','same','b','back'])):
                    actorData['LastAction'] = rawInput

            if (not(tempTurn) and initCommand != 'b' and initCommand != 'back'):
                # at the end of the turn, check for cc effects that should expire or allow a save
                i = 0
                while (i < len(actorData['Status'])):
                    statusEffect = actorData['Status'][i]
                    if (statusEffect[0] == 'dot'):
                        dotTiming = statusEffect[2]
                        if (dotTiming == 'targetend'):
                            dotSave = statusEffect[3]
                            dotDamageCalculation = statusEffect[4]
                            playerDot = statusEffect[5]
                            dotTypes = statusEffect[6]
                            dotSuccess = False
                            dotHalf = False
                            if (not(dotSave) or makeSave(actor,actorData,dotSave[0],dotSave[1],dotTypes) > 0):
                                dotSuccess = True
                            elif (dotSave and dotSave[2] == 'half'):
                                print(actor, "will take half damage from this DoT")
                                dotSuccess = True
                                dotHalf = True

                            if (dotSuccess):
                                if (dotDamageCalculation.isdigit()):
                                    damage = int(dotDamageCalculation)
                                elif (playerDot and not(autoBattle)):
                                    damage = DnDUtil.getInt(input('Roll for DoT damage ('+dotDamageCalculation+'): '))
                                else:
                                    damage = DnDUtil.calculate(dotDamageCalculation)

                                damage = getNetDamage(damage,actorData,actor,actorData,dotTypes,'DoT',False)
                                if (dotHalf):
                                    damage /= 2

                                if (damage > 0):
                                    if (dotTypes):
                                        primaryDotType = dotTypes[0]
                                    else:
                                        primaryDotType = ''
                                    print(actor, "takes", DnDUtil.getDamageText(damage), primaryDotType, "damage from DoT")
                                    killed = applyDamage(actor,actorData,damage,dotTypes,False)
                                    # re-evaluate whether it's a player's turn since we could have dropped concentration on a spell that mind-controlled the current actor
                                    if ('HP' in actorData):
                                        playerTurn = False
                                    else:
                                        playerTurn = True

                                    if (killed):
                                        break
                                    elif (not(playerTurn)):
                                        dealDamage(actor,actorData,damage)
                                        if (checkKilled(actor,actorData,damage,dotTypes,False)):
                                            print(actor, DnDUtil.getDeathText('dies'), "to DoT!")
                                            kill(actor)
                                            break
                        i += 1
                    elif (statusEffect[0] != 'grapple' and statusEffect[0] != 'wound' and statusEffect[2] and statusEffect[4] == 'end'):
                        threeSaveClear = statusEffect[5]
                        ownerData = getData(statusEffect[1])
                        if (makeSave(actor,actorData,statusEffect[2],statusEffect[3],statusEffect[8],False,'enemy'+statusEffect[2]+'saves' in ownerData['Disadvantages']) == 0):
                            if (threeSaveClear):
                                statusEffect[7] += 1
                                print(actor, "has now passed this save", DnDUtil.getPassText(statusEffect[7]), "times and failed", DnDUtil.getFailText(statusEffect[6]), "times")
                            if (not(threeSaveClear) or statusEffect[7] == 3):
                                for effect in ownerData['Effects']:
                                    if (effect[0] == actor and effect[1] == 'cc' and effect[2] == statusEffect[0]):
                                        dispel(effect,statusEffect[1],actorData)
                                        ownerData['Effects'].remove(effect)
                                        if (effect in ownerData['Concentration']):
                                            ownerData['Concentration'].remove(effect)
                                        break
                                print(actor, "has broken free of", statusEffect[0]+'!')
                            else:
                                i += 1
                        else:
                            if (threeSaveClear):
                                statusEffect[6] += 1
                                print(actor, "has now failed this save", DnDUtil.getFailText(statusEffect[6]), "times and passed", DnDUtil.getPassText(statusEffect[7]), "times")
                                if (statusEffect[6] == 3):
                                    print(actor, "can no longer save from this effect!")
                                    statusEffect[2] = ''
                            prestrainEffects = getCCEffectsForTarget(ownerData,actor,'prestrain')
                            if (prestrainEffects and (not(threeSaveClear) or statusEffect[6] == 3)):
                                print(actor, "is now petrified!")
                                statusEffect[2] = ''
                                for effect in prestrainEffects:
                                    if (effect[1] == 'cc' and effect[2] == 'prestrain'):
                                        effect[2] = 'petrification'
                                    else:
                                        for subEffect in effect[3]:
                                            if (subEffect[1] == 'cc' and subEffect[2] == 'prestrain'):
                                                subEffect[2] = 'petrification'
                                for subStatusEffect in actorData['Status']:
                                    if (subStatusEffect[0] == 'prestrain' and subStatusEffect[1] == statusEffect[1]):
                                        subStatusEffect[0] = 'petrification'
                            i += 1
                    else:
                        i += 1

                # apply all dots that should trigger at the end of this actor's turn
                for effect in actorData['Effects']:
                    if (effect[1] == 'dot'):
                        target = effect[0]
                        targetData = getData(target)
                        if (not(targetData is None)):
                            if (applyActorDot(actor,actorData,target,targetData,effect,'actorend')):
                                break
                    elif (effect[1] == 'cc' or effect[1] == 'grapple'):
                        for subEffect in effect[3]:
                            if (subEffect[1] == 'dot'):
                                target = effect[0]
                                targetData = getData(target)
                                if (not(targetData is None)):
                                    if (applyActorDot(actor,actorData,target,targetData,subEffect,'actorend')):
                                        break

                # dispel all effects that should finish at the end of this turn
                for [owner,effect] in endOfTurnEffects:
                    ownerData = getData(owner)
                    if (ownerData is None):
                        DnDUtil.printWarning("Attempted to dispel effect "+str(effect)+" from "+owner+" but "+owner+" was not found") 
                    elif (effect in ownerData['Effects']):
                        targetData = getData(effect[0])
                        if (not(targetData is None)):
                            dispel(effect,owner,targetData,True)
                            # refresh actorData and ownerData if either was the target of this effect since we're doing a hard dispel
                            if (effect[0] == actor):
                                actorData = getData(actor)
                            if (effect[0] == owner):
                                ownerData = getData(owner)
                            if (effect in ownerData['Concentration']):
                                ownerData['Concentration'].remove(effect)
                        ownerData['Effects'].remove(effect)

            if (not(battleRoyale) and encounter == {}):
                break
            
            if (not(tempTurn)):
                if (initCommand != 'b' and initCommand != 'back'):
                    actorData['Reaction'] = True
                    # reset reaction for any actors with the reactive trait
                    for dataDict in [playerData, encounter]:
                        for itActor in dataDict:
                            if ('reactive' in dataDict[itActor]['Misc']):
                                dataDict[itActor]['Reaction'] = True

                actorIndex += 1
            # if the actor we jumped from died, advance the actor index so it will restore to the proper position
            if (tempTurn and not(lastActor in turnOrder)):
                actorIndex += 1
            if (firstTurn):
                firstTurn = False
        actorIndex = 0

    print("This encounter has been completed")

    if (numPlayers > 0):
        awardedExp = totalExp / numPlayers
        print("Suggested Exp:", awardedExp)

    print("Suggested Gold:", totalGold)

    if (autoBattle):
        rating = random.randint(1,5)
    else:
        rating = DnDUtil.getInt(input("Enter the difficulty rating for this encounter (1-5): "))

    if (rating == 1):
        lootRoll = random.randint(1,74)
    elif (rating == 2):
        lootRoll = random.randint(1,89)
    elif (rating == 3):
        lootRoll = random.randint(1,100)
        lootRoll2 = random.randint(1,89)
    elif (rating == 4):
        lootRoll = random.randint(25,100)
        lootRoll2 = random.randint(25,100)
    elif (rating == 5):
        lootRoll = random.randint(75,100)
        lootRoll2 = random.randint(75,100)
    else:
        lootRoll = 0
        lootRoll2 = 0

    print("Loot roll for this encounter is", lootRoll)
    getLoot(str(lootRoll))
    if (rating >= 2):
        getLoot('Potion')
    if (rating >= 3):
        print("Second loot roll for this encounter is", lootRoll2)
        getLoot(str(lootRoll2))
    if (rating >= 5):
        getLoot('Potion')

    if (autoBattle):
        print(DnDUtil.getPassText(turnOrder.pop()), "wins the duel!")

    autoBattle = False
    playerData.clear()
    encounter.clear()
    triggerData.clear()
    del turnOrder[:]
    loadPlayerData()

def formatHelp(section):

    print("Welcome to the format help section!")
    print("Here you can type the name of a field and read how the information should be formatted in that field.")
    print("Typing layout will display the proper ordering for the fields as well as all valid search terms.")
    print("Type done when you are finished to return to the main program.")
    print("There are 3 main sections: character, misc, and ability")

    if (section == ''):
        section = input('Which help section would you like to go to? ')

    while (section != 'done'):
        if (section == 'character'):
            print("Welcome to the character help section!")
            print("This section details the various fields present in the creature data and player data files.")
            field = input('What field would you like to learn about? ')
            while (field != 'done'):
                if (field == '' or field == 'layout'):
                    if (DnDUtil.getAnswer('Would you like to see the layout for Player Data') == 'y'):
                        print("The current Player Data layout is:")
                        print("name|level|size|type|ac|immunities|vulnerabilities|resistances|atk|damage|ohabilities|weapontypes|spellatk|spelldc|uabilities|strsave|dexsave|consave|intsave|wissave|chasave|advantages|disadvantages|init|misc")
                    else:
                        print("The current Creature Data Layout is:")
                        print("name|size|type|environments|hp|ac|immunities|vulnerabilities|resistances|atk|damage|ohabilities|weapontypes|strsave|dexsave|consave|intsave|wissave|chasave|advantages|disadvantages|init|spellatk|spelldc|uabilities|ainfo|misc|cr|notes")
                elif (field == 'name'):
                    print("name - the name to be displayed to refer to that character")
                    print("Having a short name is important since it can drastically reduce time spent typing. Try using abbreviations for longer names!")
                    print("Format Rules: A one-word name")
                elif (field == 'level'):
                    print("level - the player's total level")
                    print("A multiclassed player should add up all levels in various classes to arrive at this number.")
                    print("Format Rules: Must be an integer")
                elif (field == 'size'):
                    print("size - the size class of the character")
                    print("If an invalid size is given, the character will be assigned a medium size by default.")
                    print("Format Rules: Must be a valid size. Valid sizes are:")
                    print("medium, large, small, huge, tiny, gargantuan, diminutive, colossal, and fine")
                elif (field == 'type'):
                    print("type - the race or types of the character")
                    print("It is best to list all races or types that apply to a character. For example, give your orcs the types orc AND humanoid.")
                    print("For humanoid creatures that don't have a specific race, you can use humanoid as the type and a humanoid race will be randomly chosen.")
                    print("Format Rules: Each type separated by a ,")
                elif (field == 'ac'):
                    print("ac - the character's armor class")
                    print("Format Rules: Must be an integer")
                elif (field == 'immunities'):
                    print("immunities - the character's immunities")
                    print("Any ability used on this character which has a type that matches an immunity listed in this field will not affect the character.")
                    print("Format Rules: Each immunity is separated by a ,")
                    print("Example: We want a character to be immune to sleep, fire, and charm effects.")
                    print("We would put sleep,fire,charm for this field.")
                    print("Note: flank, crit, spell, and magic are also valid immunities.")
                elif (field == 'vulnerabilities'):
                    print("vulnerabilities - the character's vulnerabilities")
                    print("Format Rules: Each vulnerability is separated by a ,")
                    print("Example: We want a character to be vulnerable to cold and acid.")
                    print("We would put cold,acid for this field.")
                elif (field == 'resistances'):
                    print("resistances - the character's resistances")
                    print("Format Rules: Each resistance is separates by a ,")
                    print("Example: We want a character to have fire and psychic resistance.")
                    print("We would put fire,psychic for this field")
                elif (field == 'atk'):
                    print("atk - the character's total attack bonus for all possible weapon attacks")
                    print("This attack bonus is calculated by adding the base attack bonus, size bonus, and appropriate ability score modifier (typically, str for melee and dex for ranged).")
                    print("Format Rules: each melee attack bonus separated by , followed by ; and each ranged attack bonus separated by ,")
                    print("Example 1: A character has base attack bonus +2, no size modifier (because he/she is medium size), +3 str mod, and +1 dex mod.")
                    print("We would put 5;3 in this field since (2+3);(2+1) = 5;3")
                    print("Example 2: A character has base attack bonus +11/+6/+1, +1 size modifer (for being small size), +2 str mod, and +3 dex mod.")
                    print("We would put 14,9,4;15,10,5 for this field since (11+2+1),(6+2+1),(1+2+1);(11+3+1),(6+3+1),(1+3+1) = 14,9,4;15,10,5")
                    print("Note: a ranged attack bonus is not required for characters that do not have ranged attacks.")
                elif (field == 'damage'):
                    print("damage - the damage calculation used to determine how much damage each attack deals")
                    print("If each attack in a set (melee or ranged) deals the same damage, the damage calculation need only be listed once.")
                    print("Format Rules: Each damage calculation in a set separated by , and each set separated by ;")
                    print("Example 1: A character has 2 attacks in each set and the melee attacks each deal 1d6+1 damage and the ranged attacks each deal 1d8 damage.")
                    print("We would put 1d6+1;1d8 for this field.")
                    print("Example 2: A character only has 3 melee attacks. The first 2 attacks deal 2d6+4 damage and the third attack deals 1d8+2 damage.")
                    print("We would put 2d6+4,2d6+4,1d8+2 for this field.")
                    print("Note: while there can be multiple dice rolls involved in calculating damage, there can only be one flat modifier and it must be at the end of the calculation.")
                elif (field == 'ohabilities'):
                    print("ohabilities - any abilities that are used when an enemy is hit with a weapon attack")
                    print("If each attack in a set (melee or ranged) applies the same ability, the ability need only be listed once.")
                    print("Format Rules: The ability for each attack in a set separated by | and each set separated by /")
                    print("Example: A character has 3 melee attacks and 2 ranged attacks. The first melee attack applies ability1 and the second and third melee attacks apply ability2. The ranged attacks both apply ability3.")
                    print("We would put ability1|ability2|ability2/ability3 for this field, filling in the appropriate information describing each ability.")
                    print("Example 2: A character only has 4 melee attacks. Attack 1 applies ability1, attack 2 does not apply an ability, and attacks 3 and 4 apply ability2.")
                    print("We would put ability1||ability2|ability2 for this field, filling in the appropriate information describing each ability.")
                    print("If you want to learn how to format an ability, check the ability help section!")
                    print("Note: types can be assigned to ohabilities in the misc field.")
                elif (field == 'spellatk'):
                    print("spellatk - the character's total attack bonus when making a spell attack")
                    print("This bonus is calculated by adding a character's proficiency bonus, spell ability modifier, and any miscellaneous bonuses.")
                    print("Format Rules: Must be an integer.")
                    print("Example: A bard has a proficiency bonus of +4, a charisma mod of +3, and an enchantment granting +1 to spell attacks.")
                    print("We would put 8 for this field since 4+3+1 = 8")
                elif (field == 'spelldc'):
                    print("spelldc - the DC of spell cast by the character")
                    print("A character's spell DC is calculated by adding 8 to the sum of the character's proficiency bonus, spell ability modifier, and any miscellaneous bonuses.")
                    print("Format Rules: Must be an integer.")
                    print("Example: A druid has a proficiency bonus of +2, a wisdom mod of +4, and an enchantment granting +1 to spell DC.")
                    print("We would put 15 for this field since 8+2+4+1 = 15")
                elif (field == 'uabilities'):
                    print("uabilities - any abilities we want a character to be able to use through the use command")
                    print("Format Rules: each ability separated by |")
                    print("If you want to learn how to format an ability, check the ability help section!")
                elif (field == 'strsave'):
                    print("strsave - a character's total strength saving throw bonus")
                    print("This bonus is calculated by adding a character's strength modifier, proficiency bonus (if the character is proficient in strength saving throws), and any miscellaneous bonuses.")
                    print("Format Rules: Must be an integer.")
                    print("Example: A character has a strength mod of +2, is proficient in strength saving throws with a proficiency bonus of +3, and has an enchantment that grants +1 to strength saves.")
                    print("We would put 6 for this field since 2+3+1 = 6")
                elif (field == 'dexsave'):
                    print("dexsave - a character's total dexterity saving throw bonus")
                    print("This bonus is calculated by adding a character's dexterity modifier, proficiency bonus (if the character is proficient in dexterity saving throws), and any miscellaneous bonuses.")
                    print("Format Rules: Must be an integer.")
                    print("Example: A character has a dexterity mod of +2, is proficient in dexterity saving throws with a proficiency bonus of +3, and has an enchantment that grants +1 to dexterity saves.")
                    print("We would put 6 for this field since 2+3+1 = 6")
                elif (field == 'consave'):
                    print("consave - a character's total constitution saving throw bonus")
                    print("This bonus is calculated by adding a character's constitution modifier, proficiency bonus (if the character is proficient in constitution saving throws), and any miscellaneous bonuses.")
                    print("Format Rules: Must be an integer.")
                    print("Example: A character has a constitution mod of +2, is proficient in constitution saving throws with a proficiency bonus of +3, and has an enchantment that grants +1 to constitution saves.")
                    print("We would put 6 for this field since 2+3+1 = 6")
                elif (field == 'intsave'):
                    print("intsave - a character's total intelligence saving throw bonus")
                    print("This bonus is calculated by adding a character's intelligence modifier, proficiency bonus (if the character is proficient in intelligence saving throws), and any miscellaneous bonuses.")
                    print("Format Rules: Must be an integer.")
                    print("Example: A character has a intelligence mod of +2, is proficient in intelligence saving throws with a proficiency bonus of +3, and has an enchantment that grants +1 to intelligence saves.")
                    print("We would put 6 for this field since 2+3+1 = 6")
                elif (field == 'wissave'):
                    print("wissave - a character's total wisdom saving throw bonus")
                    print("This bonus is calculated by adding a character's wisdom modifier, proficiency bonus (if the character is proficient in wisdom saving throws), and any miscellaneous bonuses.")
                    print("Format Rules: Must be an integer.")
                    print("Example: A character has a wisdom mod of +2, is proficient in wisdom saving throws with a proficiency bonus of +3, and has an enchantment that grants +1 to wisdom saves.")
                    print("We would put 6 for this field since 2+3+1 = 6")
                elif (field == 'chasave'):
                    print("chasave - a character's total charisma saving throw bonus")
                    print("This bonus is calculated by adding a character's charisma modifier, proficiency bonus (if the character is proficient in charisma saving throws), and any miscellaneous bonuses.")
                    print("Format Rules: Must be an integer.")
                    print("Example: A character has a charisma mod of +2, is proficient in charisma saving throws with a proficiency bonus of +3, and has an enchantment that grants +1 to charisma saves.")
                    print("We would put 6 for this field since 2+3+1 = 6")
                elif (field == 'advantages'):
                    print("advantages - anything the character has advantage on")
                    print("Format Rules: Each advantage type separated by a ,")
                    print("Example: A character has advantage on intelligence checks, dexterity saving throws, and saves against cold effects")
                    print("We would put int,dexsaves,cold for this field")
                elif (field == 'disadvantages'):
                    print("disadvantages - anything the character has disadvantage on")
                    print("Format Rules: Each disadvantage type separated by a ,")
                    print("Example: A character has disadvantage on charisma checks, strength saving throws, and saves against lightning effects")
                    print("We would put cha,strsaves,lightning for this field")
                elif (field == 'init'):
                    print("init - a character's total bonus to initiative")
                    print("This bonus is calculated by adding a character's dexterity modifier and any miscellaneous bonuses such as the alert feat.")
                    print("Format Rules: Must be an integer.")
                elif (field == 'weapontypes'):
                    print("weapontypes - the type of damage a character's weapon attacks deal")
                    print("The types listed here are what is used to check if the defender has a resistance that applies to this weapon's damage.")
                    print("Format Rules: Each type in a set (melee or ranged) separated by , and each set separated by ;")
                    print("Example: A character wields a magical mace as their melee weapon and a shortbow as their ranged weapon.")
                    print("We would put bludgeoning,magic;piercing for this field.")
                elif (field == 'environments'):
                    print("environments - the type of environments that you would encounter this creature")
                    print("This field can be useful to find appropriate creatures to use based on the location players.")
                    print("Format Rules: Each environment separated by ,")
                    print("Example: A creature can be found in the forest or in a cave.")
                    print("We would put forest,cave for this field")
                elif (field == 'hp'):
                    print("hp - the calculation used to determine the starting health points of the creature")
                    print("Format Rules: Any calculation")
                    print("Example: A creature's starting hp is determined by 4d8+3d6+10.")
                    print("We would put 4d8+3d6+10 for this field.")
                    print("Note: if we wanted a creature's hp to always be 30, we could simple put 30 for this field.")
                elif (field == 'ainfo'):
                    print("ainfo - any information you will need to know about a creature during a battle.")
                    print("Format Rules: This field has no formatting rules, but you should have a system that is fairly consistent.")
                    print("For my purposes, I typically list the name of every ability and important feature a creature has at its disposal and separate them by semi-colon.")
                    print("I put all names in lowercase of abilities that are used through the use command and capitalize everything else.")
                    print("Also, I put in parenthesis any additional information I might need to know about the ability or feature, such as range, area, and number of uses.")
                elif (field == 'cr'):
                    print("cr - the creature's challenge rating")
                    print("One creature of a cr equal to a 4-man party's average level should provide a fair challenge.")
                    print("Format Rules: Must be a number.")
                elif (field == 'notes'):
                    print("notes - any additional information you want to store about the creature")
                    print("Format Rules: None")
                    print("Note: text typed in this field will not be visible within the program and can only be viewed from the data file itself.")
                elif (field == 'misc'):
                    print("misc - a character's additional stats that are not covered in the previous fields.")
                    print("This field includes things like feats and passive abilities.")
                    print("Format Rules: each stat is separated by ; and each stat can have an argument which is separated by a -")
                    print("Example: A character has the feats cleave and mobility, as well as combat reflexes with a +2 dex mod and 3 spellpower.")
                    print("We would put cleave;mobility;cr-2;sp-3 for this field.")
                    print("Note: see the misc help section to learn about each valid stat")
                else:
                    print("Invalid field! Type layout to see a list of all valid fields.")
                field = input('What field would you like to learn about? ')
        elif (section == 'misc'):
            print("Welcome to the misc help section!")
            print("misc is a field located in both the player and creature data files.")
            print("This field includes things like feats and passive abilities.")
            print("Format Rules: each stat is separated by ; and each stat can have an argument which is separated by a -")
            print("Example: A character has the feats cleave and mobility, as well as combat reflexes with a +2 dex mod and 3 spellpower.")
            print("We would put cleave;mobility;cr-2;sp-3 for this field.")
            print("The current list of all valid misc stats is:")
            print("bane|oh|critc|critd|thorns|cleave|icleave|regen|evasion|avoidance|iflank|mobility|grab|turn|sa|rage|bc|pr|ham|mdex|rstr|dm|oht|igrapple|uf|parry|spmod|splvl|relentless|bfrenzy|db|lresist|idsmite|pet|passive|reactive|spellreflect|lactions|indomitable|ud|survivor|deathsave|dol|bh|sm|gwm|aop|ad|dfn|dfr|lair|ll|fi|conc")
            print("Type done to return to the main format help section.")
            stat = input('What stat would you like to learn about? ')
            while (stat != 'done'):
                if (stat == 'stats' or stat == 'layout'):
                    print("The current list of all valid misc stats is:")
                    print("bane|oh|critc|critd|thorns|cleave|icleave|regen|evasion|avoidance|iflank|mobility|grab|turn|sa|rage|bc|pr|ham|mdex|rstr|dm|oht|igrapple|uf|parry|spmod|splvl|relentless|bfrenzy|db|lresist|idsmite|pet|passive|reactive|spellreflect|lactions|indomitable|ud|survivor|deathsave|dol|bh|sm|gwm|aop|ad|dfn|dfr|lair|ll|fi|conc")
                elif (stat == 'bane'):
                    print("bane - Bane effect such as favored enemy")
                    print("This stat is unique in that we do not use the stat's name as the actual stat in the misc field.")
                    print("Instead, we use the type of enemy we have the bonus against as the stat name")
                    print("Argument: Bonus damage granted by hitting the specified enemy type")
                    print("Example: A character inherently deals 2 bonus damage to beasts and has a weapon that deals 1d8 bonus damage to orcs.")
                    print("We would add beast-2;orc-1d8 to the misc field for these stats.")
                elif (stat == 'oh' or stat == 'ohm' or stat == 'ohr'):
                    print("oh - On Hit Type")
                    print("This stat is used to specify the types for the character's on-hit abilities")
                    print("The name of the stat changes based on which on-hit ability for which we want to specify the types.")
                    print("oh sets the types for all melee and ranged abilities.")
                    print("ohm sets the types for all melee abilities.")
                    print("ohr sets the types for all ranged abilities.")
                    print("ohm0 sets the types for the first set of melee abilities.")
                    print("ohm00 sets the types for the first ability in the first set set of melee abilities.")
                    print("Argument: Each type of the ability separated by ,")
                    print("Example 1: A character has a melee on-hit which poisons and paralyzes and a ranged on-hit that sleeps.")
                    print("We would add ohm-poison,paralyze;ohr-sleep to the misc field for these stats.")
                    print("Example 2: A character's first attack set has an ability that deals fire damage, but his second attack set has an ability that paralyzes.")
                    print("We would add ohm0-fire;ohm1-paralysis to the misc field for these stats.")
                    print("Note: A more specific type will always override a more general type (i.e. if ohm-fire and oh-poison are given, fire will be the type for melee abilities, otherwise poison will be)")
                elif (stat == 'critc'):
                    print("critc - Critical Chance")
                    print("This stat indicates the minimum number that can be rolled to score a critical hit with a weapon")
                    print("mcritc sets the crit chance for all melee weapon attacks.")
                    print("rcritc sets the crit chance for al ranged weapon attacks.")
                    print("mcritc0 sets the crit chance for all melee weapon attacks in the first set (when attacking with m)")
                    print("mcritc00 sets the crit chance for the first attack in the first set of melee attacks, etc.")
                    print("Note 1: if this stat is not given, 20 is assumed to be the crit chance.")
                    print("Note 2: If a more specific crit chance is given for an attack, that value will be used instead of a more general crit chance")
                elif (stat == 'critd'):
                    print("critd - Critical Damage")
                    print("This stat indicates the damage multiplier used when scoring a critical hit (usually 2)")
                    print("mcritd sets the crit damage for all melee weapon attacks.")
                    print("rcritd sets the crit damage for all ranged weapon attacks.")
                    print("mcritd0 sets the crit damage for all melee weapon attacks in the first set (when attacking with m)")
                    print("mcritd00 sets the crit damage for the first attack in the first set of melee attacks, etc.")
                    print("Note 1: if this stat is not given, 2 is assumed to be the crit damage.")
                    print("Note 2: If a more specific crit damage is given for an attack, that value will be used instead of a more general crit damage")
                elif (stat == 'thorns'):
                    print("thorns - This stat deals damage back to the attacker when struck")
                    print("Argument: The amount of damage dealt back to the attacker and the types of damage dealt, if any separated by ,")
                    print("Note: The damage argument can be a damage calculation")
                    print("Example: A creature deals 1d10 nonmagical piercing damage when struck by a melee attack. We would add thorns-1d10,piercing,nonmagic to the misc column.")
                elif (stat == 'cleave'):
                    print("cleave - Cleave feat")
                    print("Argument: None")
                elif (stat == 'icleave'):
                    print("icleave - Greater Cleave feat")
                    print("Argument: None")
                elif (stat == 'regen'):
                    print("regen - Regeneration")
                    print("This stat heals the character at the start of his/her turn for the amount given and also disables the regeneration for its next turn when taking damage of a specific type.")
                    print("Argument: the amount healing per round followed by each type that disables regeneration separated by ,")
                    print("Note: If at least one type is specified that disables the regeneration, the creature will not die until until it reaches 0 hp while its regeneration is disabled")
                    print("Example: A creature heals for 10 hp each turn, but loses this regen when taking fire or lightning damage. We would add regen-10,fire,lightning to the misc column.")
                elif (stat == 'evasion'):
                    print("evasion - the Evasion ability")
                    print("This stat indicates that when the character makes a DEX saving throw that allows it to take half damage, it will take no damage on success and half damage on failure.")
                    print("Argument: None")
                elif (stat == 'avoidance'):
                    print("avoidance - the Avoidance ability")
                    print("This stat indicates that when the character makes ANY saving throw that allows it to take half damage, it will take no damage on success and half damage on failure.")
                    print("Argument: None")
                elif (stat == 'iflank'):
                    print("iflank - Improved Flank")
                    print("This stat indicates the bonus damage dealt with weapon attacks while flanking.")
                    print("Argument: Bonus damage")
                elif (stat == 'mobility'):
                    print("mobility - Mobility ability")
                    print("This stat indicates that attacks of opportunity against this character have disadvantage")
                    print("Argument: None")
                elif (stat == 'grab'):
                    print("grab - Grab")
                    print("This stat specifies what size category a creature can attempt to grapple with its grab ability.")
                    print("Argument: the maximum number of size categories larger than itself the creature can grab")
                    print("Example: A creature can grab any opponent up to 1 size category larger than itself.")
                    print("We would add grab-1 to the misc field for this stat.")
                    print("Note: If the maximum size a creature can grapple is smaller than it's own size, then the grab stat is not needed")
                elif (stat == 'turn'):
                    print("Turn Undead")
                    print("This stat specifies what level the character is considered to be when using turn undead, which also affects the power of destroy undead.")
                    print("Argument: Turn Undead Level")
                    print("Note: If this stat is not given, the level is considered to be the character's level")
                elif (stat == 'sa'):
                    print("sa - Sneak Attack")
                    print("This stat gives the character sneak attack which deals the damage given as the argument.")
                    print("Argument: Sneak attack damage")
                elif (stat == 'rage'):
                    print("rage - Rage")
                    print("This stat gives the damage bonus provided as the argument when raging.")
                    print("Argument: Damage bonus when raging")
                elif (stat == 'bc'):
                    print("bc - Brutal Critical")
                    print("This stat gives the extra damage that is rolled when the character crits with a melee weapon attack.")
                    print("Argument: Brutal Critical damage")
                elif (stat == 'pr'):
                    print("pr - Persistent Rage")
                    print("This stat grants Persistent Rage, giving unlimited duration to the character's rage.")
                    print("Argument: None")
                elif (stat == 'ham'):
                    print("ham - Heavy Armor Master")
                    print("This stat grants the Heavy Armor Master feat, subtracting 3 damage from each hit by a nonmagical weapon.")
                    print("Argument: None")
                elif (stat == 'mdex'):
                    print("mdex - Melee Dexterity")
                    print("This stat is used to indicate that the character's melee attacks use dexterity as its modifier.")
                    print("Argument: None")
                elif (stat == 'rstr'):
                    print("rstr - Ranged Strength")
                    print("This stat is used to indicate that the character's ranged attacks use strength as its modifier.")
                    print("Argument: None")
                elif (stat == 'dm'):
                    print("dm - Deflect Missile")
                    print("This stat grants the monk ability Deflect Missile")
                    print("Argument: Total bonus (usually, dex mod + monk level)")
                elif (stat == 'oht'):
                    print("oht - Open Hand Technique")
                    print("This stat grants the monk ability Open Hand Technique")
                    print("Argument: None")
                elif (stat == 'igrapple'):
                    print("igrapple - Improved Grapple")
                    print("This stat indicates that when the character successfully grapples an opponent, that opponent is restrained.")
                    print("Argument: None")
                elif (stat == 'uf'):
                    print("uf - Undead Fortitude")
                    print("This stat grants Undead Fortitude, which allows the character to make a constitution saving throw when taking lethal damage to stay alive.")
                    print("Argument: None")
                elif (stat == 'parry'):
                    print("parry - Parry")
                    print("This stat indicates this creature has the parry ability, which means it can use its reaction to improve its AC by the argument given against a single melee attack.")
                    print("Argument: AC Bonus")
                elif (stat == 'spmod'):
                    print("spmod - Spellcasting modifier")
                    print("This stat indicates the creature's spellcasting modifier. Note that this is only necessary for creatures with spells that use the modifier directly, such as cure wounds and spiritual weapon.")
                    print("Argument: The creature's spellcasting modifier")
                    print("Note: Multiple spellcasting modifiers can be declared by adding a number to the end of 'spmod'")
                elif (stat == 'splvl'):
                    print("splvl - Spellcasting level")
                    print("This stat indicates the creature's spellcasting level. Note that this is only necessary for creatures with cantrips that change their effects based on level and have a different spellcasting level than their level or CR.")
                    print("Argument: The creature's spellcasting level")
                elif (stat == 'relentless'):
                    print("relentless - Relentless")
                    print("This stat indicates that the first time upon receiving fatal damage less than or equal to the given arugment, the creature will stay alive at 1 HP instead.")
                    print("Argument: The maximum damage the creature can receive and remain alive")
                elif (stat == 'grablimit'):
                    print("grablimit - Grab Limit")
                    print("This stat indicates the maximum number of opponents this creature can grapple at once.")
                    print("This affects whether the creature will seek out new targets with an attack while already grappling a target.")
                    print("Note: If a creature can only grab one opponent per attack that grapples, there is no need to include this stat.")
                    print("Argument: The maximum number of grappled opponents")
                elif (stat == 'bfrenzy'):
                    print("bfrenzy - Blood Frenzy")
                    print("This stat grants the creature blood frenzy, giving it advantage on melee attacks against creatures with less than max health.")
                    print("Argument: None")
                elif (stat == 'db'):
                    print("db - Death Burst")
                    print("This stat indicates that the creature has an ability which should be triggered when it is killed.")
                    print("You will be able to specify the targets for this ability when it is used.")
                    print("Argument: Name of the ability to use on death")
                    print("Note: The named ability must be present in the creature's 'Use Abilities'")
                elif (stat == 'lresist'):
                    print("lresist - Legendary Resistance")
                    print("This stat indicates that the creature has legendary resistances, meaning it can choose to automatically succeed a saving throw.")
                    print("Argument: The number of times the creature can use legendary resistance")
                elif (stat == 'idsmite'):
                    print("idsmite - Improved Divine Smite")
                    print("This stat indicates that the creature has improved divine smite and deals an additional 1d8 when using divine smite.")
                    print("Argument: None")
                elif (stat == 'pet'):
                    print("pet - Pet")
                    print("This stat indicates that this character is a summoned creature or pet of one of the players and should not count toward the average level of the party nor take a share of the party's experience.")
                    print("Argument: None")
                    print("Note: This stat only has significance for players")
                elif (stat == 'passive'):
                    print("passive - Passive Abilities")
                    print("This stat indicates abilities that should be used at the start of combat.")
                    print("Argument: The name of each ability to use at that start of combat separated by a ,")
                    print("Note: The abilities must be present in Use Abilities and can only be cast on the actor itself")
                    print("Note 2: Trigger abilities will be used without a target")
                elif (stat == 'reactive'):
                    print("reactive - Reactive Ability")
                    print("This stat indicates that the creature regains its reaction every turn of combat")
                    print("Argument: None")
                elif (stat == 'spellreflect'):
                    print("spellreflect - Spell Reflection Ability")
                    print("This stat indicates that the creature can use its reaction when a single target spell attack misses it or it saves from a single target spell to reflect the spell at another creature within the given range.")
                    print("Argument: The range of the spell reflect in feet")
                elif (stat == 'lactions'):
                    print("lactions - Legendary Actions")
                    print("This stat indicates that the creature has legendary actions and how many it can use per round of combat.")
                    print("Argument: Number of legendary actions (usually 3)")
                elif (stat == 'indomitable'):
                    print("indomitable - Indomitable Ability")
                    print("This stat indicates the creature can reroll a failed saving throw a number of times equal to its given argument.")
                    print("Argument: The number of times a saving throw can be rerolled")
                elif (stat == 'ud'):
                    print("ud - Uncanny Dodge Ability")
                    print("This stat indicates the creature can use its reaction after being hit by an attack to halve the attack's damage.")
                    print("Argument: None")
                elif (stat == 'survivor'):
                    print("survivor - Survivor Ability")
                    print("This stat indicates the creature regains the given number of health of the start of each of its turns while it is above 1 and below half its maximum.")
                    print("Argument: The amount of health gained each turn")
                elif (stat == 'deathsave'):
                    print("deathsave - Death Saving Throw Modifier")
                    print("This stat indicates what bonus should be given to death saving throws made by this creature.")
                    print("Argument: Death Save Bonus")
                elif (stat == 'dol'):
                    print("dol - Disciple of Life Ability")
                    print("This stat indicates that when the creature casts a healing spell of at least first level, the amount of healing will increase by 2 plus the spell's level for each target.")
                    print("Argument: None")
                elif (stat == 'bh'):
                    print("bh - Blessed Healer Ability")
                    print("This stat indicates that when the creatures casts a healing spell of at least first level that heals another creature, the caster heals for health equal to 2 plus the spell's level.")
                    print("Argument: None")
                elif (stat == 'sm'):
                    print("sm - Shield Master Feat")
                    print("This stat indicates the creature has the shield master feat, giving bonus to dex saves against effects that target only itself, the ability to use its reaction to instead take no damage when passing a dex save to take half damage, and the ability to shove following an attack action.")
                    print("Argument: The shield's AC bonus")
                elif (stat == 'gwm'):
                    print("gwm - Great Weapon Master Feat")
                    print("This stat indicates the creature has the great weapon master feat, giving an extra attack once per turn on a crit or kill")
                    print("Argument: None")
                elif (stat == 'aop'):
                    print("aop - Aura of Protection Ability")
                    print("This stat indicates the creature has the aura of protection ability, granting a bonus on saving throws to allies within 10ft while conscious")
                    print("Argument: The saving throw bonus")
                    print("Note: This bonus is only applied when it makes the difference between a passed and failed save!")
                elif (stat == 'ad'):
                    print("ad - Arcane Deflection Ability")
                    print("This stat indicates the creature has the arcane deflection ability, allowing +2 AC to be granted when hit by an attack or +4 save bonus when failing a save as a reaction")
                    print("Argument: None")
                elif (stat == 'dfn'):
                    print("dfn - Divine Fury Ability (Necrotic)")
                    print("This stat indicates the creature has the necrotic version of the divine fury ability, which deals 1d6 necrotic damage + half barb level extra damage on the first hit with a weapon attack while raging each round")
                    print("Argument: Barbarian Level")
                    print("Note: If no argument is given, the creature's level or CR will be used instead")
                elif (stat == 'dfr'):
                    print("dfr - Divine Fury Ability (Radiant)")
                    print("This stat indicates the creature has the radiant version of the divine fury ability, which deals 1d6 radiant damage + half barb level extra damage on the first hit with a weapon attack while raging each round")
                    print("Argument: Barbarian Level")
                    print("Note: If no argument is given, the creature's level or CR will be used instead")
                elif (stat == 'lair'):
                    print("lair - Monster Lair")
                    print("This stat indicates the creature has the option of being fought within its own special lair, adding lair actions and possibly increasing the CR of the encounter")
                    print("Argument: Name of the lair found in Lair Data (usually the creature's name)")
                    print("Note: If no argument is given, the creature's name will be used to search for a lair")
                elif (stat == 'll'):
                    print("ll - Lightning Launcher")
                    print("This stat gives the character lightning launcher which deals an extra 1d6 lightning damage on ranged attacks once per turn")
                    print("Argument: None")
                elif (stat == 'fi'):
                    print("fi - Fungal Infestation Ability")
                    print("This stat gives the character the fungal infestation ability which raises a 1 hp zombie when a small or large beast or humanoid dies within 10ft of the character as a reaction")
                    print("Argument: None")
                elif (stat == 'conc'):
                    print("conc - Concentration Bonus")
                    print("This stat adds the given bonus when the character makes a concentration check to maintain a spell (useful for bladesong)")
                    print("Argument: The saving throw bonus")
                else:
                    print("Invalid stat! Type stats to see a list of all valid stats.")
                stat = input('What stat would you like to learn about? ')
        elif (section == 'ability'):
            print("Welcome to the ability help section!")
            print("Here you will learn how to format abilities both in the ability data file and within various character fields that hold abilities.")
            print("The valid search terms in this section are layout|name|savetype|dc|saveresult|ut|sd|trigger|type|actions|prereqs|actions2|damage|heal|cc|buff|debuff|drain|grapple|summon|immunity|mc|ss|dot|resist|examples")
            print("Type done to return to the main help section.")
            field = input('What would you like to learn about? ')
            while (field != 'done'):
                if (field == 'layout'):
                    print("The current layout for ability data is:")
                    print("name|savetype|saveresult|ut|sd|trigger|type|actions")
                    print("The current layout for a use ability is:")
                    print("name-prereqs:actions:actions2")
                    print("The current layout for an on-hit ability is:")
                    print("prereqs:actions")
                elif (field == 'name'):
                    print("name - The name of the use ability")
                    print("As with character names, try to keep these abbreviated to reduce time spent typing.")
                    print("Format Rules: A one-word name.")
                elif (field == 'savetype'):
                    print("savetype - the type of save, if any, the target needs to make")
                    print("Format Rules: str/dex/con/int/wis/cha")
                elif (field == 'dc'):
                    print("dc - the dc, or difficulty class, of the abilities")
                    print("If the ability requires a save, then there must be a dc listed as well.")
                    print("Format Rules: Must be an integer.")
                elif (field == 'saveresult'):
                    print("saveresult - the result of the save")
                    print("If the ability is ignored (or actions2 are applied instead) put negates here.")
                    print("If the ability instead deals half damage, put half here.")
                    print("If the ability requires a save, then there must be a saveresult listed as well.")
                    print("Format Rules: negates/half")
                elif (field == 'ut'):
                    print("ut - use turn")
                    print("This field determines whether the actor's turn is used by using this ability.")
                    print("Format Rules: yes/no")
                elif (field == 'sd'):
                    print("sd - static damage")
                    print("This field determines whether the same damage should be applied to all targets.")
                    print("We would put no in this field for things like magic missile and scorching ray since we want to re-roll damage for each missile.")
                    print("Format Rules: yes/no")
                elif (field == 'trigger'):
                    print("trigger - trigger")
                    print("This field determines whether to designate the spell as a trigger spell.")
                    print("A trigger spell is one that we want to remember and trigger on another character's turn while the ability lasts.")
                    print("Examples of this would be fire shield, fire wall, blade barrier, and consecrate.")
                    print("Format Rules: yes/no")
                elif (field == 'type'):
                    print("type - The abilities types")
                    print("Format Rules: each type separated by ,")
                elif (field == 'actions'):
                    print("actions - what the ability does if it succeeds")
                    print("The actions describe what an ability does if the prereqs are met, spell resistance has been passed, and the target is not immune.")
                    print("Each action has it's own set of arguments which are separated by ,")
                    print("The current list of valid actions is:")
                    print("damage|heal|cc|buff|debuff|drain|grapple|summon|immunity|mc|ss|dot|resist")
                    print("Format Rules: each action separated by ; and the arguments of each action separated by ,")
                    print("Note: any integer can be replaced with lvl or lvl/integer to apply the actor's caster level to the ability.")
                elif (field == 'prereqs'):
                    print("prereqs - the prerequisites that must be met in order to use the ability")
                    print("This includes two major components: attack and save. Save is made up of savetype, dc, and saveresult.")
                    print("Format Rules: each prerequisite separated by , and attack always listed first")
                    print("Example: An ability requires an attack and a dc 15 wisdom save, which negates the effect.")
                    print("We would put yes,wis,15,negates if the ability did not already exist in ability data and 15 otherwise")
                elif (field == 'actions2'):
                    print("actions2 - describes the actions that take place instead if the save is met")
                    print("Some abilities still have effects even when a save is made, such as sound burst, this is where actions2 is useful.")
                    print("Format Rules: simply add : to the end of the normal actions and list the actions that would occur if the save is made")
                    print("Example: An ability stuns for 1 turn and deals 1d8 spell damage if the save is failed, but only deals the damage if the save is made.")
                    print("We would put cc,stun,1;damage,1d8:damage,1d8 for the actions of this ability.")
                elif (field == 'damage'):
                    print("damage - an action type which deals damage to the target")
                    print("Arguments: the damage calculation")
                elif (field == 'heal'):
                    print("heal - an action type which heals the target")
                    print("Arguments: the heal calculation")
                elif (field == 'cc'):
                    print("cc - an action type which can apply crowd-control effects or simply count the duration on buffs/debuffs")
                    print("Arguments: the name of the cc followed by the duration of the cc (optional)")
                    print("Note: any buff, debuff, drain, immunity, or resist actions appearing after a cc action will last for the same duration as the cc.")
                elif (field == 'buff'):
                    print("buff - an action type which buffs a stat of the target")
                    print("Arguments: stat to be buffed followed by the amount the stat should be buffed")
                    print("Note: this buff will last a duration equal to any previous cc actions in the same ability.")
                elif (field == 'debuff'):
                    print("debuff - an action type which debuffs a stat of the target")
                    print("This action functions the same as the buff action except that buff value becomes negative")
                    print("Arguments: stat to be debuffed followed by the amount the stat should be debuffed")
                    print("Note: this debuff will last a duration equal to any previous cc actions in the same ability.")
                elif (field == 'drain'):
                    print("drain - an action type which debuffs the target and buffs the actor for the same amount")
                    print("Arguments: stat to be drained followed by the amount of the stat that should be drained")
                    print("Note: this drain will last a duration equal to any previous cc actions in the same ability.")
                elif (field == 'grapple'):
                    print("grapple - an action type which makes a grapple check as the actor against the target")
                    print("If the actor fails the grapple check, then none of the actions after the grapple action will apply.")
                    print("Also, an on-hit ability which grapples will automatically fail if the target is not smaller than the actor in size, as per the rules of improved grab.")
                    print("Arguments: which attack bonus to use for the grapple")
                    print("Example: A character initiates a grapple on hitting its second and third attacks.")
                    print("We would put grapple,2 for the second on-hit ability and grapple,3 for the third on-hit ability.")
                elif (field == 'summon'):
                    print("summon - an action type which summons a creature/creatures as an ally to the one that summoned it/them")
                    print("Arguments: name of the creature to be summoned followed by the number of that creature to be summoned followed by how long the summon lasts (optional)")
                elif (field == 'immunity'):
                    print("immunity - an action type which grants the target immunity from the specified type")
                    print("Arguments: immunity type")
                    print("Note: this immunity will last a duration equal to any previous cc actions in the same ability.")
                #to be continued
                else:
                    print("Invalid search term!")
                    print("The valid search terms in this section are layout|name|savetype|dc|saveresult|ut|sd|trigger|type|actions|prereqs|actions2|damage|heal|cc|buff|debuff|drain|grapple|summon|immunity|mc|ss|dot|resist|examples")
                field = input('What would you like to learn about? ')
        else:
            print("Invalid section! The valid sections are character, misc, and ability.")
        section = input('Which help section would you like to go to? ')

def help(str,combat):
    
    if (str == 'j' or str == 'jump'):
        print("jump - Jumps to the given actor temporarily, then returns to the previous actor")
        print("Usage: j/jump [actor]")
        print("Note: If you want this jump to consume the actor's reaction, use react instead")
    elif (str == 'react'):
        print("react - Jumps to the given actor temporarily, using that actor's reaction, then returns to the previous actor")
        print("Usage: react [actor]")
        print("Note: If you don't want this jump to consume the actor's reaction, use jump instead")
    elif (str == 's' or str == 'same'):
        print("same - repeats the last stored action of the actor, asking for a reroll if needed (player weapon attacks only)")
        print("Usage: s/same ([new roll])")
    elif (str == 'skip'):
        print("skip - skips the current player's turn")
        print("Usage: skip")
        print("Note: Empty input will also result in skip")
    elif (str == 'd' or str == 'display'):
        print("display - displays different things based on the argument given")
        print("display hp - prints hp values of all creatures in the encounter")
        print("display order - prints the initiative order starting at the beginning")
        print("display trigger - prints the stats of all active trigger abiities")
        print("display stats - prints all stats of either the actor or the given target argument")
        print("display [stat] - prints the specific stat given of either the actor or the given target")
        print("Usage: d/display hp/order/trigger/stats/[stat] ([target])")
        print("Note: This command can also be used outside of an encounter to check player stats")
    elif (str == 'move'):
        print("move - displays the movespeed of the current actor or given actor")
        print("Usage: move ([target])")
    elif (str == 'spell'):
        print("spell - displays information on the given spell, pulled from the ability data table")
        print("Usage: spell [spell name]")
        print("Note: This command can also be used outside of an encounter")
    elif (str == 'sl' or str == 'spl' or str == 'spelllist'):
        print("spelllist - displays the list of spells that a given class can learn")
        print("Usage: sl/spl/spelllist [class](,[subclass]) ([spell level])")
        print("Example 1: sl druid would print all spells available to druids")
        print("Example 2: sl rogue,arcanetrickster 1 would print all first level spells available to an arcane trickster rogue")
        print("Note: This command can also be used outside of combat")
    elif (str == 'o' or str == 'open'):
        print("open - opens to the correct pdf page of the string given, inclduing things such as creatures, classes, races, and spells, using additional optional arguments to narrow the search")
        print("Usage: o/open [string](,[searchArg1],[searchArgs2],...)")
        print("Example: We want to reference the spell resurrection. We would type 'open resurrection' and the player's handbook would open to the page containing the resurrection spell.")
        print("Example 2: We want to reference the druid class, but not the creature named druid. We could either type 'open druid,class' to specify the class OR 'open druid,phb' to specify that we want the druid from the player's handbook")
        print("Note: This command can also be used outside of an encounter")
        print("Note 2: This command requires some pdf reader, such as Acrobat Reader DC, to be installed")
        print("Note 3: Additional bookmarks can be set using the 'Bookmark Data' file")
        print("Note 4: If used during an encounter on a creature's turn, simply entering 'open' will try to open the bookmark for the current creature")
    elif (str == 'b' or str == 'back'):
        print("back - returns to the previous actor and restores all statuses")
        print("Usage: b/back")
    elif (str == 'm' or str == 'melee'):
        print("melee - executes a standard melee attack on the specified target")
        print("Player Usage: m([attack index])/melee [target] [roll]")
        print("Enemy Usage: m([attack index])/melee [target] (+/-[bonus])")
        print("Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)")
    elif (str == 'r' or str == 'ranged'):
        print("ranged - executes a standard ranged attack on the specified target")
        print("Player Usage: r([attack index])/ranged [target] [roll]")
        print("Enemy Usage: r([attack index])/ranged [target] (+/-[bonus])")
        print("Note: The attack index is used to indicate which ranged attack action should be performed if multiple are given (0 is the default index)")
    elif (str == 'fb' or str == 'fob'):
        print("fob - simulates flurry of blows")
        print("Player Usage: fb([attack index])/fob [target] [roll]")
        print("Enemy Usage: fb([attack index])/fob [target]")
        print("Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)")
    elif (str == 'u' or str == 'use'):
        print("use - uses the specified ability given in the creature data table on the specified targets")
        print("Usage: u/use [ability] ([target],[target2]...)")
        print("Note: targets are only optional for abilities that create a trigger")
        print("Note 2: self, allies, enemies, and all are all valid targets")
        print("Note 3: This command can also be used outside of combat")
    elif (str == 'scroll'):
        print("scroll - uses the given ability from abilityData on the specified targets")
        print("Usage: scroll [ability] [target](,[target2]...) ([dc bonus])")
        print("Note: self, allies, enemies, and all are all valid targets")
    elif (str == 't' or str == 'trigger'):
        print("trigger - triggers a stored ability designated as a trigger ability on the current actor or a target actor")
        print("Usage: t/trigger [name] ([target])")
        print("Note: in order for trigger to work, the trigger ability must have already been used by another character")
        print("Example: druid2 has the use ability fshield. fshield is a trigger spell that we would use when anyone attacks druid2 with fshield active.")
        print("First, we use fshield (giving an invalid target so as not to damage any characters) on druid2's turn to cast the spell, then when anyone attacks druid2 while fshield is on, we type 'trigger fshield' to apply the fshield's damage to the attacker")
        print("Note 2: if we wanted to cast a trigger spell that can trigger immediately, such as fwall, proper targets would be given on the initial cast.")
        print("Note 3: 'self', 'allies', 'enemies', and 'all' are valid target names.")
    elif (str == 'flank'):
        print("flank - executes a melee attack from a flanking position")
        print("Player Usage: flank([attack index]) [target] [roll]")
        print("Enemy Usage: flank([attack index]) [target]")
        print("Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)")
    elif (str == 'ra' or str == 'recklessattack'):
        print("recklessattack - executes a reckless attack on target, giving advantage on all attacks for and against the actor for a turn")
        print("Player Usage: ra([attack index])/recklessattack [target] [roll]")
        print("Enemy Usage: ra([attack index])/recklessattack [target]")
        print("Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)")
    elif (str == 'am'):
        print("am - executes a melee attack with advantage")
        print("Player Usage: am([attack index]) [target] [roll]")
        print("Enemy Usage: am([attack index]) [target]")
        print("Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)")
    elif (str == 'ar'):
        print("ar - executes a ranged attack with advantage")
        print("Player Usage: ar([attack index]) [target] [roll]")
        print("Enemy Usage: ar([attack index]) [target]")
        print("Note: The attack index is used to indicate which ranged attack action should be performed if multiple are given (0 is the default index)")
    elif (str == 'dm'):
        print("dm - executes a melee attack with disadvantage")
        print("Player Usage: dm([attack index]) [target] [roll]")
        print("Enemy Usage: dm([attack index]) [target]")
        print("Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)")
    elif (str == 'dr'):
        print("dr - executes a ranged attack with disadvantage")
        print("Player Usage: dr([attack index]) [target] [roll]")
        print("Enemy Usage: dr([attack index]) [target]")
        print("Note: The attack index is used to indicate which ranged attack action should be performed if multiple are given (0 is the default index)")
    elif (str == 'sa' or str == 'sneakattack'):
        print("sneakattack - executes a sneak attack on the target")
        print("Player Usage: sa([attack index])/sneakattack [target] [roll]")
        print("Enemy Usage: sa([attack index])/sneakattack [target]")
        print("Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)")
        print("Note 2: in order to sneak attack with a ranged attack, use sar or sneakattackr instead")
    elif (str == 'gwm' or str == 'greatweaponmaster'):
        print("greatweaponmaster - performs a great weapon master attack, giving the attacker -5 to hit and +10 to damage")
        print("Player Usage: gwm([attack index])/greatweaponmaster [target] [roll]")
        print("Enemy Usage: gwm([attack index])/greatweaponmaster [target]")
        print("Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)")
    elif (str == 'ssr' or str == 'sharpshooter'):
        print("sharpshooter - performs a sharpshooter attack, giving the attacker -5 to hit and +10 to damage")
        print("Player Usage: ssr([attack index])/sharpshooter [target] [roll]")
        print("Enemy Usage: ssr([attack index])/sharpshooter [target]")
        print("Note: The attack index is used to indicate which ranged attack action should be performed if multiple are given (0 is the default index)")
    elif (str == 'aoo'):
        print("aoo - allows another character to perform a melee attack on the current actor, used for attacks of opportunity")
        print("Player Usage: aoo [attacker] [roll]")
        print("Enemy Usage: aoo [attacker]")
    elif (str == 'attack'):
        print("attack - when all else fails, allows someone to make an attack out of turn order, might be used to check values or rare cases of AoOs")
        print("Player Usage: attack [player] [target] [roll]")
        print("Enemy Usage: attack [enemy] [target]")
    elif (str == 'dmg' or str == 'damage'):
        print("damage - deals damage to a creature or creatures out of turn order, used for hp adjustments and misc cases")
        print("Usage: dmg/damage [creature](,[creature2]...) [amount] ([type],[type2]...)")
        print("Note: the types of the damage dealt can be specified at the end to apply immunities, vulnerabilities, and resistances")
    elif (str == 'roll'):
        print("roll - simulates rolling dice and prints the total result")
        print("Usage: roll ([number of rolls]d[type of die](+[number of rolls]d[type of die]...))")
        print("Note: the roll command will also accept whole integers as input")
        print("Note 2: this command can also be used outside of combat")
        print("Note 3: if no dice are given, it will roll 1d20")
        print("Example: roll 2d4+3 will roll a d4 twice, then add 3 and print the total")
    elif (str == 'g' or str == 'grapple'):
        print("grapple - used for making grapple check with the target")
        print("Usage: g/grapple [target]")
        print("Note: this command can be used to start a grapple, make grapple checks, and escape a grapple")
    elif (str == 'esc' or str == 'escape'):
        print("escape - used to escape a grapple")
        print("Usage: esc/escape")
        print("Note: if the current actor is grappled by more than one enemy, you will be asked to choose which grapple to escape")
    elif (str == 'aid'):
        print("aid - executes the help combat maneuver, giving the target ally advantage on his/her next attack against a target enemy in your melee range")
        print("Usage: aid [ally] [enemy]")
        print("Note: the program actually gives advantage on the next attack regardless of the target. Try to remind the player to attack the target he/she has advantage on")
    elif (str == 'dodge'):
        print("dodge - executes the dodge combat maneuver, giving the user advantage on dexterity saving throws and enemies disadvantages on their attacks made against the user for a turn")
        print("Usage: dodge")
    elif (str == 'shove'):
        print("shove - executes the shove combat maneuver, allowing the actor to prone an enemy or push them back")
        print("Usage: shove [target]")
    elif (str == 'rage'):
        print("rage - simulates the barbarian's rage ability")
        print("Usage: rage")
    elif (str == 'dispel'):
        print("dispel - gives the DM the option to remove any effects on the target")
        print("Usage: dispel [target](,[target2]...)")
    elif (str == 'turn'):
        print("turn - used to Turn Undead on the given targets")
        print("Usage: turn [target](,[target2]...)")
    elif (str == 'adv'):
        print("advantage - gives the target advantage on the specified check")
        print("Usage: adv [target] [check type] ([duration])")
        print("Example: adv player1 con 3 would give player1 advantage on constitution checks for 3 turns")
    elif (str == 'dis'):
        print("disadvantage - gives the target disadvantage on the specified check")
        print("Usage: dis [target] [check type] ([duration])")
        print("Example: dis orc2 chasaves 5 would give orc2 disadvantage on charisma saving throws for 5 turns")
    elif (str == 'dc' or str == 'dropconcentration'):
        print("dropconcentration - dispels all effects that the given actor is currently concentrating on")
        print("Usage: dc/dropconcentration ([target])")
        print("Note: if no target is given, it will default to the current actor")
    elif (str == 'buff'):
        print("buff - gives a buff that lasts a specified number of rounds or until the end of the encounter")
        print("Usage: buff [target] [stat] [amount] ([duration])")
        print("Note: debuffs can be given by inputting a negative value for amount")
        print("Note: the duration variable should be given in number of turns")
        print("Note: the valid [stat] arguments are currently ac, str, dex, atk, dmg, hp, saves, strsave, dexsave, consave, intsave, wissave, chasave, and size")
    elif (str == 'dot'):
        print("dot - applies a DoT to the target")
        print("Player Usage: dot [target] [damage] actor/target ([save type] [save DC] negates/half) ([damageType1],[damageType2]...) ([duration])")
        print("Note: a calculation can be provided for the damage or duration")
        print("Note: the fourth parameter indicates whether the DoT deals damage at the start of the DoT owner's turn (actor) or the DoT target's turn (target)")
    elif (str == 'cc'):
        print("cc - places a status effect on the target for a number of turns, and reminds the DM on that player's turn")
        print("Usage: cc [target] [effect] ([duration])")
        print("Note: if no duration is given, the effect will last until it is manually cleared")
        print("Note: actorstart/actorend/targetstart/targetend are all valid durations meaning that at the start or end of the actor or target's next turn, the cc will expire")
    elif (str == 'prone'):
        print("prone - Prones the given actor")
        print("Usage: prone ([target])")
        print("Note: the action can be undone using the stand command")
    elif (str == 'stand'):
        print("stand - Stands the given actor, removing the prone effect")
        print("Usage: stand ([target])")
        print("Note: this command has no effect on an actor that is not prone")
    elif (str == 'heal'):
        print("heal - heals a creature out of turn order, used for spells, potions, and misc cases")
        print("Usage: heal [creature](,[creature2]...) [amount]")
        print("Note: on an enemy's turn, heal will accept an equation such as 1d8+3 as the amount argument")
    elif (str == 'kill'):
        print("kill - instantly kills a creature or player, removing it from the encounter")
        print("Usage: kill [target](,[target2]...)")
    elif (str == 'add'):
        print("add - adds allies or enemies to the encounter")
        print("Usage: add/adda/adde [creature] [number]")
        print("Note: use adda to add allies and adde to add enemies")
    elif (str == 'mc' or str == 'mindcontrol'):
        print("mindcontrol - simulates a mindcontrol, turning a player into a creature and a creature into an enemy")
        print("Usage: mc/mindcontrol [target] ([duration])")
    elif (str == 'ss' or str == 'shapeshift'):
        print("shapeshift - simulates a shapeshift by replacing a creature's current data  with that of another creature type")
        print("Usage: ss/shapeshift [creature] ([duration])")
    elif (str == 'a' or str == 'abilities'):
        print("abilities - prints the abilities cell of the given creature from the creature data table or print all use abilities of a player")
        print("Usage: a/abilities ([target])")
        print("Note: if no target is given, it will attempt to display the abilities of the current actor")
    elif (str == 'sethp'):
        print("sethp - sets a creature's hp to the given value, useful for recovering from crashes and errors")
        print("Usage: sethp [creature] [new hp]")
    elif (str == 'addtemphp'):
        print("addtemphp - Adds a given number of temporary hit points to the given creature")
        print("Usage: addtemphp [creature] [temp hp]")
        print("Note: This will give temporary hit point regradless or whether the creature previously had temporary hp")
    elif (str == 'str'):
        print("str - makes a strength save for every target given, but the targets must be all players or all enemies")
        print("Player Usage: str [target](,[target2]...) [roll](,[roll2]...)")
        print("Enemy Usage: str [target](,[target2]...)")
    elif (str == 'dex'):
        print("dex - makes a dexterity save for every target given, but the targets must be all players or all enemies")
        print("Player Usage: dex [target](,[target2]...) [roll](,[roll2]...)")
        print("Enemy Usage: dex [target](,[target2]...)")
    elif (str == 'con'):
        print("con - makes a constitution save for every target given, but the targets must be all players or all enemies")
        print("Player Usage: con [target](,[target2]...) [roll](,[roll2]...)")
        print("Enemy Usage: con [target](,[target2]...)")
    elif (str == 'int'):
        print("int - makes a intelligence save for every target given, but the targets must be all players or all enemies")
        print("Player Usage: int [target](,[target2]...) [roll](,[roll2]...)")
        print("Enemy Usage: int [target](,[target2]...)")
    elif (str == 'wis'):
        print("wis - makes a wisdom save for every target given, but the targets must be all players or all enemies")
        print("Player Usage: wis [target](,[target2]...) [roll](,[roll2]...)")
        print("Enemy Usage: wis [target](,[target2]...)")
    elif (str == 'cha'):
        print("cha - makes a charisma save for every target given, but the targets must be all players or all enemies")
        print("Player Usage: cha [target](,[target2]...) [roll](,[roll2]...)")
        print("Enemy Usage: cha [target](,[target2]...)")
    elif (str == 'addmisc'):
        print("addmisc - Adds a miscellaneous stat with the given argument to the given target (or targets)")
        print("Usage: addmisc [target](,[target2]...) [stat] ([argument])")
        print("Example: addmisc orc1,orc2,skeleton1 parry 2 would give orc1, orc2, and skeleton1 the parry ability, grating +2 AC when used")
    elif (str == 'editmisc'):
        print("editmisc - Edits a miscellaneous stat, replacing its argument with the given argument on the given target (or targets)")
        print("Usage: editmisc [target](,[target2]...) [stat] [argument]")
        print("Example: editmisc veteran1,veteran2 parry 4 would change captain1 and captain2's parry arguments to 4 (assuming they had the parry ability)")
    elif (str == 'delmisc'):
        print("delmisc - Deletes a miscellaneous stat from the given target (or targets)")
        print("Usage: delmisc [target](,[target2]..) [stat]")
        print("Example: delmisc zombie1,zombie2 uf would remove zombie1 and zombie2's undead fortitude ability")
    elif (str == 'done'):
        print("done - instantly ends the encounter")
        print("Usage: done")
    elif (str == 'help'):
        print("help - gives a short description of a command followed by usage information or lists all commands")
        print("Usage: h/help ([command])")
        print("Note: variables are enclosed in braces i.e. [command] and optional arguments are given in parenthesis i.e. ([command])")
    elif (str == '' and combat):
        print("The full list of combat commands is:")
        print("jump, react, same, skip, display, move, spell, spelllist, open, back, melee, ranged, fob, use, scroll, trigger, flank, recklessattack, am, ar, dm, dr, sneakattack, greatweaponmaster, sharpshooter, aoo, attack, damage, roll, grapple, escape, aid, dodge, shove, rage, dispel, turn, adv, dis, dropconcentration, buff, dot, cc, prone, stand, heal, kill, add, mc, abilities, sethp, addtemphp, str, dex, con, int, wis, cha, addmisc, editmisc, delmisc, done, help")
    elif (combat):
        print("Command", str, "not found")
        print("The full list of combat commands is:")
        print("jump, react, same, skip, display, move, spell, spelllist, open, back, melee, ranged, fob, use, scroll, trigger, flank, recklessattack, am, ar, dm, dr, sneakattack, greatweaponmaster, sharpshooter, aoo, attack, damage, roll, grapple, escape, aid, dodge, shove, rage, dispel, turn, adv, dis, dropconcentration, buff, dot, cc, prone, stand, heal, kill, add, mc, abilities, sethp, addtemphp, str, dex, con, int, wis, cha, addmisc, editmisc, delmisc, done, help")
    elif (not(combat)):
        if (str == 'test'):
            print("test - quickly loads a test encounter from the test encounter file")
            print("Usage: test")
        elif (str == 'player'):
            print("player - initiates player mode, loading the given characters from the character data table")
            print("Usage: player ([player name1],[player name2],...)")
            print("Note: if no players are given, it will prompt the user to enter character names")
        elif (str == 'casino'):
            print("casino - initiates casino mode, allowing the dm to access the casino games")
            print("Usage: casino")
        elif (str == 'load'):
            print("load - loads an encounter or battle royale from the encounter file")
            print("Usage: load encounter/battleroyale")
            print("Note: this command is particularly useful for recovering an encounter that was lost due to a crash")
        elif (str == 'create'):
            print("create - creates an encounter, a blacksmith, or magicshop")
            print("Usage: create [thing] (size)")
            print("Note: blacksmith and magic shop take an extra argument - size; the valid inputs for size are small, medium, and large")
        elif (str == 'battleroyale'):
            print("battleroyale - creates a battle royale encounter in which players may attack each other and there are no enemy creatures")
            print("Usage: br/battleroyale")
        elif (str == 'random'):
            print("random - prints a random item from the given class from the class data file")
            print("Usage: random [class]")
        elif (str == 'e' or str == 'encounter'):
            print("encounter - generates a list of potential encounters for the given environment using either a random or user-given difficulty")
            print("Usage: e/encounter [environment]")
            print("Note: urban is also a valid environment, with its own rules for generating an encounter")
        elif (str == 'auto'):
            print("auto - automatically genrates an encounter using the given creatures and a random or given difficulty")
            print("Usage: auto [creature1](,[creature2]...)")
            print("Note: you will be able to choose out of a list of valid encounters")
        elif (str == 'loot'):
            print("loot - prints a random loot item based on the given roll and loot data table")
            print("Usage: loot [roll]")
        elif (str == 'info'):
            print("info - prints detailed information about an armor or weapon")
            print("Usage: info [weapon/armor]")
        elif (str == 'hit'):
            print("hit - used with box to generate a random item")
            print("Usage: hit box")
        elif (str == 'weather'):
            print("weather - generates a random weather condition based on the table in the DM guide")
            print("Usage: weather")
        elif (str == 'setlvls'):
            print("setlvls - Overrides the average level of the party, number of players in the party, and exp thresholds of the party, affecting the loot drops, items available in shops, and generated encounters")
            print("Usage: setlvls [level1](,[level2],...)")
            print("Example: setlvls 2,2,3 would set up a party consisting of two level 2s and one level 3")
        elif (str == 'find' or str == 'search'):
            print("find - displays all creatures that meet the given parameters")
            print("Usage: find/search [parameter1],[value1] ([parameter2],[value2])...")
            print("Example 1: find cr,4 would print all creatures with a cr of 4")
            print("Example 2: find ac,>20 would print all creatures with an ac of at least 20")
            print("Example 3: find cr,2,3 environment,hills,plains would print all creatures found in hills or plains that have a cr of 2 or 3")
            print("Example 4: find environment,forest cr,>3 type,beast,fey would print all beasts or fey creatures found in the forest that have at least 3 cr")
        elif (str == 'addp' or str == 'addparty'):
            print("addparty - adds a new party member to the player file from the creature file and updates the program with the new party member's data")
            print("Usage: addparty/addp [creature]")
        elif (str == 'format'):
            print("format - launches the format help section to give information about how to format player and creature data")
            print("Usage: format ([field])")
            print("Note: the optional field argument will have the program display information about the specific field given")
        elif (str == ''):
            print("The full list of commands is:")
            print("test, player, casino, load, create, battleroyale, random, encounter, loot, info, hit box, weather, setlvls, find, addparty, format, jump, react, same, skip, display, move, spell, spelllist, open, back, melee, ranged, fob, use, scroll, trigger, flank, recklessattack, am, ar, dm, dr, sneakattack, surpriseattack, greatweaponmaster, sharpshooter, aoo, attack, damage, roll, grapple, escape, aid, dodge, shove, rage, dispel, turn, adv, dis, dropconcentration, buff, dot, cc, prone, stand, heal, kill, add, mc, abilities, sethp, addtemphp, str, dex, con, int, wis, cha, addmisc, editmisc, delmisc, done, help")
        else:
            print("Command", str, "not found")
            print("The full list of commands is:")
            print("test, player, casino, load, create, battleroyale, random, encounter, loot, info, hit box, weather, setlvls, find, addparty, format, jump, react, same, skip, display, move, spell, spelllist, open, back, melee, ranged, fob, use, scroll, trigger, flank, recklessattack, am, ar, dm, dr, sneakattack, surpriseattack, greatweaponmaster, sharpshooter, aoo, attack, damage, roll, grapple, escape, aid, dodge, shove, rage, dispel, turn, adv, dis, dropconcentration, buff, dot, cc, prone, stand, heal, kill, add, mc, abilities, sethp, addtemphp, str, dex, con, int, wis, cha, addmisc, editmisc, delmisc, done, help")

def startRollMode():
    
    roll = input("Input roll: ")

    while (len(roll) > 0 and roll[0]):
        print(DnDUtil.calculate(roll))
        roll = input("Input roll: ")

def startPlayerMode(players):

    if (not(players)):
        players = DnDUtil.mySplit(input('Which characters do you want to load data for? '),',')
    characterData = {}
    for player in players:
        playerCharacterData = Player.getCharacterData(player)
        if (playerCharacterData):
            characterData[player.capitalize()] = playerCharacterData
        else:
            print("Character", player, "not found!")
            return

    Player.main(characterData)

def startCasinoMode():

    CasinoGames.main()
    
# playerData is a dictionary of dictionaries, where each key is a player name and each value is the player's data
PLAYER_FILE = 'Player Data/' + PLAYER_FILE
playerData = {}
encounter = {}
triggerData = {}
turnOrder = []
actorIndex = 0
totalExp = 0
totalGold = 0
weaponData = {}
armorData = {}
avgLevel = 0
numPlayers = 0
partyExpThresholds = [0,0,0,0]
autoBattle = False
onProgramStart()

while True:

    rawInput = input("What would you like to do? (type \'help\' for help)\n")
    rawInput = rawInput.split()

    while (len(rawInput) == 0):
        rawInput = input()
        rawInput = rawInput.split()

    numArgs = len(rawInput)

    if (rawInput[0] == 'roll' and (numArgs == 1 or numArgs == 2)):
        if (numArgs == 1):
            rollString = '1d20'
        else:
            rollString = rawInput[1]
        if (rollString == 'mode'):
            startRollMode()
        else:
            print(DnDUtil.calculate(rollString))

    elif (rawInput[0] == 'test' and numArgs == 1):
        testEncounter()

    elif (rawInput[0] == 'test' and numArgs == 2):
        if (rawInput[1] == 'test'):
            test()
        elif (rawInput[1] == 'encounter'):
            testEncounter()
        elif (rawInput[1] == 'creatures'):
            testCreatures()
        else:
            print("Unknown test! Valid tests are: encounter/creatures/test")

    elif (rawInput[0] == 'player' and (numArgs == 1 or numArgs == 2)):
        if (numArgs == 2):
            players = DnDUtil.mySplit(rawInput[1],',')
        else:
            players = []
        startPlayerMode(players)

    elif (rawInput[0] == 'casino' and numArgs == 1):
        startCasinoMode()

    elif (rawInput[0] == 'go' or rawInput[0] == 'fight'):
        createEncounter()

    elif (rawInput[0] == 'load' and numArgs == 2):
        if (rawInput[1] == 'encounter'):
            createEncounter(ENCOUNTER_FILE)
        elif (rawInput[1] == 'br' or rawInput[1] == 'battleroyale'):
            createEncounter(ENCOUNTER_FILE,None,True)

    elif (rawInput[0] == 'create' and (numArgs == 2 or numArgs == 3)):
        if (rawInput[1] == 'encounter' and numArgs == 2):
            createEncounter()
        elif ((rawInput[1] == 'blacksmith' or rawInput[1] == 'magicshop') and numArgs == 3 and rawInput[2] in ['small','medium','large']):
            if (rawInput[1] == 'blacksmith'):
                createBlacksmith(rawInput[2])
            else:
                createMagicShop(rawInput[2])

    elif ((rawInput[0] == 'br' or rawInput[0] == 'battleroyale') and numArgs == 1):
        createEncounter('',None,True)

    elif ((rawInput[0] == 'o' or rawInput[0] == 'open') and numArgs == 2):
        PDFUtil.openBookmark(rawInput[1])

    elif ((rawInput[0] == 'd' or rawInput[0] == 'display') and numArgs == 3):
        player = rawInput[2]
        if (player in playerData):
            data = playerData[player]
            stat = rawInput[1]
            if (stat == 'stats'):
                displayStats(data)
            else:
                stat = stat[0].capitalize() + stat[1:]
                if (stat in data):
                    print(data[stat])
                else:
                    stat = stat.upper()
                    if (stat in data):
                        print(data[stat])
                    else:
                        print("Invalid stat -", rawInput[1])
        else:
            print("Invalid target -", player)

    elif (rawInput[0] == 'random' and numArgs == 2):
        if (rawInput[1] == 'npc'):
            gender = randomItem(['gender'])
            race = randomItem(['race'])
            alignment = randomItem(['alignment'])
            trait = randomItem(['trait'])
            print(gender, race, "-", alignment)
            print(trait)
        else:
            item = randomItem(rawInput[1].split(','))
            print(item)

    elif ((rawInput[0] == 'e' or rawInput[0] == 'encounter') and numArgs == 2):
        if (rawInput[1] == 'urban'):
            roll = random.randint(1,20)
            if (DnDUtil.getAnswer('Is this a small city') == 'y'):
                bonus1 = 1
            elif (DnDUtil.getAnswer('Is this a medium city') == 'y'):
                bonus1 = 2
            elif (DnDUtil.getAnswer('Is this a large city') == 'y'):
                bonus1 = 3
            else:
                bonus1 = 0
            if (avgLevel >= 6 and DnDUtil.getAnswer('Are the players new in town and at least level 6 or laying low') == 'y'):
                bonus2 = -2
            elif (DnDUtil.getAnswer('Are the players well-known in town or looking for action') == 'y'):
                bonus2 = 2
            else:
                bonus2 = 0
            bonus3 = (avgLevel-1) // 5
            result = roll + bonus1 + bonus2 + bonus3
            if (result >= 20):
                roll = random.randint(1,20)
                result = roll + bonus1 + bonus2 + bonus3
                encounterTable = ['Bullies','Muggers','Guard harassment','Pickpockets','Spectacle','Found item','Lost child','Corpse','Animal','Overturned/runaway cart','District-specific encounter','District-specific encounter','Contest in progress','Duel/mageduel in progress','Brawl/street fight/ gang war in progress','robbery in progress','escaped prisoner','monster','fire','Construction accident','Spell gone awry','Prominent personage','Mistaken identity','Guards need help','Employment offer','Admirer']
                if (result >= len(encounterTable)):
                    print(encounterTable[-1])
                else:
                    print(encounterTable[result])
            else:
                print("No encounter")
        else:
            difficultyIndex = getDifficultyIndex(False)
            maxCR = getMaxCRForDifficultyIndex(difficultyIndex)
            if (maxCR >= 4):
                minCR = maxCR // 4
            else:
                minCR = maxCR / 4

            environmentList = ['environments',rawInput[1],'any']
            if (DnDUtil.getAnswer('Include creatures from other planes') == 'y'):
                environmentList.append('plane')
            # get the list of all creatures in this environment that are between the min and max CR
            creatureList = search([environmentList,['cr','>'+str(minCR)],['cr','<'+str(maxCR)]])
            CRSet = set([])
            for creature in creatureList:
                CRSet.add(float(creature[1]))
            CRToNumDict = generateDictForCRSet(difficultyIndex,CRSet)

            finalCreatureList = []
            for creature in creatureList:
                numList = CRToNumDict[str(float(creature[1]))]
                # don't display creatures that cannot be encountered in any number to satisfy the given difficulty
                if (numList):
                    if (len(numList) == 1):
                        numString = str(numList[0])
                    else:
                        numString = str(numList[0])+'-'+str(numList[-1])
                    finalCreatureList.append([numString,creature[0],creature[1]])
                    print(numString, creature[0], "(CR", creature[1]+')')

            if (finalCreatureList):
                while (DnDUtil.getAnswer('Would you like to randomly select an encounter') == 'y'):
                    roll = random.randint(0,len(finalCreatureList)-1)
                    creature = finalCreatureList[roll]
                    print(creature[0], creature[1], "(CR", creature[2]+')')
                    if (DnDUtil.getAnswer('Generate an encounter using these creatures') == 'y'):
                        if (creature[0].isdigit()):
                            number = int(creature[0])
                        else:
                            parsedNumString = creature[0].split('-')
                            number = random.randint(int(parsedNumString[0]),int(parsedNumString[1]))
                        createEncounter('',{creature[1]: number})
                        break

    elif (rawInput[0] == 'auto' and numArgs == 2):
        autoGenerateEncounter(rawInput[1].split(','))

    elif (rawInput[0] == 'loot' and numArgs == 2):
        getLoot(rawInput[1])

    elif (rawInput[0] == 'info' and numArgs >= 2):
        rawInput[1] = rawInput[1].capitalize()
        for i in range(2,numArgs):
            rawInput[1] += ' ' + rawInput[i].capitalize()
        item = rawInput[1]
        printEquipmentInfo(item)

    elif (rawInput[0] == 'spell' and numArgs == 2):
        SpellUtil.spellInfo(rawInput[1])

    elif ((rawInput[0] == 'sl' or rawInput[0] == 'spl' or rawInput[0] == 'spelllist') and (numArgs == 2 or numArgs == 3)):
        SpellUtil.printSpellList(rawInput[1].split(','),DnDUtil.getInt(rawInput[2]) if numArgs == 3 else -1)

    elif (rawInput[0] == 'hit' and numArgs == 2 and rawInput[1] == 'box'):
        hitBox()

    elif (rawInput[0] == 'weather'):
        generateWeather()

    elif (rawInput[0] == 'setlvls' and numArgs == 2):
        playerLevels = DnDUtil.mySplit(rawInput[1],',')
        try:
            for i in range(0,len(playerLevels)):
                playerLevels[i] = int(playerLevels[i])
            numPlayers = 0
            totalLevels = 0.0
            avgLevel = 0
            partyExpThresholds = [0,0,0,0]
            for level in playerLevels:
                numPlayers += 1
                totalLevels += level
                levelThresholds = getExpThresholdsForPlayer(level)
                for i in range(0,len(levelThresholds)):
                    partyExpThresholds[i] += levelThresholds[i]
            avgLevel = int(totalLevels / numPlayers)
            loadEquipmentData()
            print("NumPlayers is now", numPlayers)
            print("AvgLevel is now", avgLevel)
            print("PartyExpThresholds is now", partyExpThresholds)
        except ValueError:
            print("Invalid argument for levels! Must be any number of integers separated by ,")

    elif ((rawInput[0] == 'find' or rawInput[0] == 'search') and numArgs >= 2):
        arguments = []
        for i in range(1,len(rawInput)):
            argument = rawInput[i].split(',')
            if (len(argument) == 1):
                print("No matching argument given for", argument[0])
            else:
                arguments.append(argument)

        if (len(arguments) > 0):
            creatureList = search(arguments)
            if (creatureList):
                print("Found", len(creatureList), "matches!")
            else:
                print("No matches found")
            for creature in creatureList:
                if (len(creature) > 2):
                    print(creature[0], "(CR", creature[1]+')', "-", creature[2])
                else:
                    print(creature[0], "(CR", creature[1]+')')

    elif ((rawInput[0] == 'addparty' or rawInput[0] == 'addp') and numArgs == 2):
        addPartyMember(rawInput[1])

    elif ((rawInput[0] == 'u' or rawInput[0] == 'use' or rawInput[0] == 'scroll') and numArgs == 3):
        if (rawInput[0] == 'scroll'):
            scroll = True
        else:
            scroll = False
        abilityName = rawInput[1]
        targets = rawInput[2].split(',')
        actor = ''
        if (scroll):
            playerList = list(playerData.keys())
            choice = DnDUtil.chooseOption('Choose the player using this scroll',playerList)
            actor = playerList[choice-1]
        else:
            abilitySources = []
            for player in playerData:
                if (abilityName in playerData[player]['UseAbilities']):
                    abilitySources.append(player)
            
            if (len(abilitySources) == 0):
                print("Ability", abilityName, "not found in any of the players!")
            elif (len(abilitySources) == 1):
                actor = abilitySources[0]
            else:
                choice = DnDUtil.chooseOption('Choose the player using this ability',abilitySources)
                actor = abilitySources[choice-1]
        if (actor):
            abilityDamageSummary = {}
            savedDamageRolls = {}
            actorData = playerData[actor]
            if (scroll):
                ability = ImportUtil.loadAbilityData(abilityName,[''],True)
                if (ability and ability['Actions'] == [['']]):
                    print("Ability", abilityName, "not found!")
            else:
                ability = actorData['UseAbilities'][abilityName]

            if (ability):
                actionKey = 'Actions'
                spellLevel = ability['Base Level']
                if ('Scaled Actions' in ability and spellLevel > 0):
                    spellLevel = SpellUtil.inputSpellLevel(abilityName,spellLevel)
                    if (spellLevel > ability['Base Level']):
                        actionKey = 'Scaled Actions'
                elif (spellLevel == 0 and 'Scaled Actions' in ability):
                    actionKey = 'Scaled Actions'

                if (scroll):
                    spellAtk = getScrollSpellAtk(spellLevel)
                    spellDC = getScrollSpellDC(spellLevel)
                else:
                    if (ability['Attack Mod']):
                        spellAtk = ability['Attack Mod']
                    else:
                        spellAtk = actorData['SpellAtk']
                    if (ability['DC'] == 0):
                        spellDC = actorData['SpellDC']
                    else:
                        spellDC = ability['DC']

                concentrating = isConcentrating(actorData)
                if (not(ability['Concentration?']) or not(concentrating) or DnDUtil.getAnswer(actor+" is concentrating on another spell. Drop concentration in favor of this spell") == 'y'):
                    if (ability['Concentration?'] and concentrating):
                        dropConcentration(actor,actorData,True)
                                                           
                    actionData = deepcopy(ability[actionKey])
                    actionData = SpellUtil.replaceSpellMod(actionData,actorData)
                    if (actionKey == 'Scaled Actions'):
                        if (spellLevel != 0):
                            lvlReplacement = spellLevel-ability['Base Level']
                        else:
                            lvlReplacement = SpellUtil.getCantripModifierForActor(actor,actorData)
                        actionData = SpellUtil.replaceLvl(actionData,lvlReplacement)

                    for target in targets:
                        if (target == 'all' or target == 'allies'):
                            targets.extend(list(playerData.keys()))
                        else:
                            if (target == 'self'):
                                target = actor
                            if (target in playerData):
                                targetData = playerData[target]
                                damageSummary = useAbility(True,abilityName,ability['Type'],ability['Duration'],actionData,True,targets,target,targetData,actor,actorData,spellAtk,ability['Save'],spellDC,0,ability['Base Level'],spellLevel,False,False,False,ability['Concentration?'],savedDamageRolls)
                                extendDamageSummary(abilityDamageSummary,damageSummary)
                                if (not(ability['Static Damage?'])):
                                    savedDamageRolls.clear()
                            else:
                                print("Invalid target -", target)
                    printDamageSummary(abilityDamageSummary)

    elif (rawInput[0] == 'duel' and numArgs == 2):
        duelistList = DnDUtil.mySplit(rawInput[1],',')
        if (len(duelistList) < 2):
            print("There must be at least two creatures to duel!")
        else:
            encounterDict = {}
            for duelist in duelistList:
                duelistData = getPlayerData(duelist)
                if (duelistData):
                    convertData(duelistData)
                    encounter[duelist] = duelistData
                else:
                    encounterDict[duelist] = 1
            playerData.clear()
            autoBattle = True
            createEncounter('',encounterDict)

    elif (rawInput[0] == 'format' and numArgs <= 2):
        if (numArgs == 2):
            field = rawInput[1]
        else:
            field = ''
        formatHelp(field)

    elif (rawInput[0] == 'h' or rawInput[0] == 'help'):
        if (numArgs > 1):
            help(rawInput[1],False)
        else:
            help('',False)

    else:
        print("Invalid Command")