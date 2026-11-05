import random
import csv
from copy import deepcopy

import DnDUtil
import ImportUtil
import SpellUtil
import Spells
import PDFUtil

CHARACTER_FILE = 'Character Data/Character Data.csv'

Player = ''
PlayerData = {}
PlayerDataDict = {}

def getInitCharacterData():
    
    initCharacterData = {}
    dataKeys = ['CR','Size','HP','HD','Move','ProfBonus','Proficiencies','Expertise','Atk','Damage','OnHitAbilities','WeaponTypes','SpellAtk','SpellDC','UseAbilities','Str','Dex','Con','Int','Wis','Cha','Advantages','Disadvantages','Misc']
    for dataKey in dataKeys:
        initCharacterData[dataKey] = None
    return initCharacterData

def parseCharacterData(row,header):

    numDataColumns = len(header)
    # remove all spaces from the header
    for i in range(0,numDataColumns):
        header[i] = header[i].replace(' ','')
    # attempt to get the name of the character first so we can reference it in case an error occurs
    try:
        nameIndex = header.index('Name')
        name = row.pop(nameIndex)
        header.remove('Name')
    except ValueError:
        DnDUtil.printError("No 'Name' column found in "+CHARACTER_FILE)
        return {}
    except IndexError:
        DnDUtil.printError("Not enough data columns in "+CHARACTER_FILE+"! Expected "+str(numDataColumns)+" columns, but only "+str(len(row))+" columns were given")
        return {}
    
    # remove notes from the header since we don't want to load this data
    if ('Notes' in header):
        header.remove('Notes')
    # initialize character data with default values
    retCharacterData = getInitCharacterData()
    # for every other data key, load from the data given in the player file
    i = 0
    while (header):
        try:
            dataKey = header.pop(0)
            # handle keys that copy the string
            if (dataKey in ['Size','HP']):
                retCharacterData[dataKey] = row[i]
            # handle keys that convert the string to int
            elif (dataKey in ['HD','ProfBonus','SpellAtk','SpellDC','Str','Dex','Con','Int','Wis','Cha']):
                retCharacterData[dataKey] = int(row[i])
            # handle keys that convert the string to float
            elif (dataKey == 'Level/CR'):
                retCharacterData['CR'] = float(row[i])
            # handle keys that parse the string by ,
            elif (dataKey in ['Move','Proficiencies','Expertise','Advantages','Disadvantages']):
                retCharacterData[dataKey] = DnDUtil.mySplit(row[i],',')
            # handle keys that parse the string by ;
            elif (dataKey == 'Misc'):
                retCharacterData[dataKey] = DnDUtil.mySplit(row[i],';')
            # handle keys that parse the string by |
            elif (dataKey in ['Atk','Damage','UseAbilities']):
                retCharacterData[dataKey] = DnDUtil.mySplit(row[i],'|')
            # handle keys that parse the string by /
            elif (dataKey == 'WeaponTypes'):
                retCharacterData[dataKey] = DnDUtil.mySplit(row[i],'/')
            # handle keys that parse the string by _
            elif (dataKey == 'OnHitAbilities'):
                retCharacterData[dataKey] = DnDUtil.mySplit(row[i],'_')
            else:
                DnDUtil.printError("Unknown column '"+dataKey+"' found in "+CHARACTER_FILE)
                return {}
            i += 1
        except IndexError:
            DnDUtil.printError("Not enough data columns for character "+name+"! Expected "+str(numDataColumns)+" columns, but only "+str(len(row))+" columns were given")
            return {}
        except ValueError:
            DnDUtil.printError("Invalid data given for character "+name+" in column "+str(i+1)+". Expected "+dataKey+" data")
            return {}

    # ensure that every data key was set
    missingDataKeys = []
    for dataKey in retCharacterData:
        if (retCharacterData[dataKey] is None):
            missingDataKeys.append(dataKey)
    
    if (missingDataKeys):
        DnDUtil.printError("Missing data for character "+name) 
        print "The following data is missing from the character data file:"
        for dataKey in missingDataKeys:
            print dataKey
        return {}

    if (retCharacterData['HP'] != '0'):
        hp = DnDUtil.calculate(retCharacterData['HP'])
        print "-----------------------"
        print "HP for this form is", hp
        print "-----------------------"
    retCharacterData['Move'] = ImportUtil.parseMoveData(retCharacterData['Move'])
    ImportUtil.formatAtkDamageData(retCharacterData,name)
    ImportUtil.formatOnHitAbilitiesData(retCharacterData['OnHitAbilities'])
    retCharacterData['UseAbilities'] = ImportUtil.parseUseAbilitiesData(retCharacterData['UseAbilities'])
    ImportUtil.formatWeaponTypesData(retCharacterData['WeaponTypes'],retCharacterData['Atk'],name)
    retCharacterData['Misc'] = ImportUtil.parseMiscData(retCharacterData['Misc'],name)

    return retCharacterData

def getCharacterData(name):

    characterFile = open(CHARACTER_FILE,'rb')
    csvCharacterReader = csv.reader(characterFile)
    header = csvCharacterReader.next()

    for row in csvCharacterReader:
        if (row[0] == name):
            characterFile.close()
            return parseCharacterData(row,header)
    characterFile.close()
    return {}

# mostly copied from main script
def displayMoveSpeed():

    print "Move Speed"
    print "--------------"
    print "Ground -", str(PlayerData['Move']['Ground'])+'ft'
    for moveType in ['Fly','Climb','Swim','Burrow']:
        if (PlayerData['Move'][moveType] > 0):
            print moveType, "-", str(PlayerData['Move'][moveType])+'ft'

# mostly copied from main script
def getCritStat(rangeIndex,atkIndex1,atkIndex2,critType):

    # 0: crit chance, 1: crit damage
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
    for stat in PlayerData['Misc']:
        if (stat.find(critKey) != -1):
            found = True
            break

    if (not(found)):
        return baseCrit

    if (rangeIndex == 0):
        rangePrefix = 'm'
    else:
        rangePrefix = 'r'

    if (rangePrefix+critKey+str(atkIndex1)+str(atkIndex2) in PlayerData['Misc']):
        return PlayerData['Misc'][rangePrefix+critKey+str(atkIndex1)+str(atkIndex2)]
    elif (rangePrefix+critKey+str(atkIndex1) in PlayerData['Misc']):
        return PlayerData['Misc'][rangePrefix+critKey+str(atkIndex1)]
    elif (rangePrefix+critKey in PlayerData['Misc']):
        return PlayerData['Misc'][rangePrefix+critKey]
    elif (critKey in PlayerData['Misc']):
        return PlayerData['Misc'][critKey]
    else:
        return baseCrit

def extendDamageSummary(damageSummary,extensionDamageSummary):

    for damageType in extensionDamageSummary:
        updateDamageSummary(damageSummary,damageType,extensionDamageSummary[damageType])

def updateDamageSummary(damageSummary,type,damage):

    if (type in damageSummary):
        damageSummary[type] += damage
    else:
        damageSummary[type] = damage

def printDamageSummary(damageSummary):

    totalDamage = 0
    damageString = "("
    for damageType in damageSummary:
        damageString += str(damageSummary[damageType])+" "+damageType+"/"
        totalDamage += damageSummary[damageType]

    totalDamageString = DnDUtil.getDamageText(totalDamage)
    print "Target took", totalDamageString, "total damage!", damageString[:-1]+")"

def main(playerData):

    global Player
    global PlayerData
    global PlayerDataDict
    PlayerDataDict = playerData
    weaponData = ImportUtil.loadWeaponData()
    armorData = ImportUtil.loadArmorData()

    while PlayerDataDict:
        breakLoop = False
        for player in PlayerDataDict:
            takenAction = False
            Player = player
            PlayerData = playerData[player]
            while (not(takenAction)):
                input = raw_input(Player+': ')
                if (not(input)):
                    input = 'skip'
                command = input.split()
                initCommand = command[0]
                numArgs = len(command)

                if (initCommand == 'done'):
                    return

                advantage = False
                disadvantage = False
                guidance = False
                bane = False
                hex = False
                huntersMark = False
                hexbladesCurse = False
                bladesong = False
                extraRollMods = []
            
                if (initCommand == 'u' or initCommand == 'use'):
                    additionalCommands = command[2:]
                else:
                    additionalCommands = command[1:]
                # determine if any upcoming roll would have advantage, disadvantage, guidance, or bane
                for additionalCommand in additionalCommands:
                    if (additionalCommand == 'a'):
                        advantage = True
                    elif (additionalCommand == 'd'):
                        disadvantage = True
                    elif (additionalCommand == 'g'):
                        guidance = True
                    elif (additionalCommand == 'b'):
                        bane = True
                    elif (additionalCommand == 'h' or additionalCommand == 'hex'):
                        hex = True
                    elif (additionalCommand == 'hm'):
                        huntersMark = True
                    elif (additionalCommand == 'hc' or additionalCommand == 'curse'):
                        hexbladesCurse = True
                    elif (additionalCommand == 'bs' or additionalCommand == 'bladesong'):
                        bladesong = True
                    elif ('d' in additionalCommand):
                        extraRollMod = getExtraRollMod(additionalCommand)
                        if (extraRollMod):
                            extraRollMods.append(extraRollMod)

                if (initCommand in PlayerData['Advantages']):
                    advantage = True
                if (initCommand in PlayerData['Disadvantages']):
                    disadvantage = True
                # determine the bonus of any upcoming roll from proficiency
                proficiencyBonus = getProficiencyBonusForCommand(initCommand)

                if (initCommand == 'roll' and (numArgs == 1 or numArgs == 2)):
                    if (numArgs == 1):
                        rollString = '1d20'
                    else:
                        rollString = command[1]
                    print DnDUtil.calculate(rollString)

                elif (initCommand == 'd' and numArgs == 2):
                    stat = command[1]
                    if (stat == 'stats'):
                        displayStats()
                    else:
                        stat = stat[0].capitalize() + stat[1:]
                        if (stat in PlayerData):
                            print PlayerData[stat]
                        else:
                            stat = stat.upper()
                            if (stat in PlayerData):
                                print PlayerData[stat]
                            else:
                                print "Invalid stat -", command[1]

                elif (initCommand == 'move' and numArgs == 1):
                    displayMoveSpeed()

                elif (initCommand == 'size' and numArgs == 1):
                    print Player+"'s size is", PlayerData['Size']

                elif ((initCommand == 'a' or initCommand == 'abilities') and numArgs == 1):
                    for ability in PlayerData['UseAbilities']:
                        print ability

                elif (initCommand == 'spell' and numArgs == 2):
                    SpellUtil.spellInfo(command[1])

                elif ((initCommand == 'sl' or initCommand == 'spl' or initCommand == 'spelllist') and (numArgs == 2 or numArgs == 3)):
                    SpellUtil.printSpellList(command[1].split(','),DnDUtil.getInt(command[2]) if numArgs == 3 else -1)

                elif ((initCommand == 'o' or initCommand == 'open') and numArgs == 2):
                    PDFUtil.openBookmark(command[1])

                elif (initCommand == 'info' and numArgs >= 2):
                    command[1] = command[1].capitalize()
                    for i in range(2,numArgs):
                        command[1] += ' ' + command[i].capitalize()
                    item = command[1]
                    # code copied from printEquipmentInfo in main script
                    if (item in weaponData):
                        itemData = weaponData[item]
                        print item+':', itemData['Class'], "weapon", '('+itemData['Damage'], itemData['Damage Type'], "damage)", "worth", itemData['Value'], "gp"
                        if (itemData['Traits']):
                            print "Traits:", itemData['Traits']
                    elif (item in armorData):
                        itemData = armorData[item]
                        print item+':', itemData['Class'], "armor worth", itemData['Value'], "gp"
                        print "AC:", str(itemData['Base AC'])+itemData['AC Mod']
                        if (itemData['Str Req'] > 0):
                            print "Strength Requirement:", itemData['Str Req']
                        if (itemData['Stealth']):
                            print "Stealth:", itemData['Stealth']
                    else:
                        print "Item not found."

                elif (initCommand == 'hd' and (numArgs == 1 or numArgs == 2)):
                    if (numArgs == 2):
                        numHitDice = DnDUtil.getInt(command[1])
                        hitDieString = "hit dice"
                    else:
                        numHitDice = 1
                        hitDieString = "hit die"
                    hitDieCalculation = str(numHitDice)+'d'+str(PlayerData['HD'])+'+'+str(numHitDice*PlayerData['Con'])
                    health = DnDUtil.calculate(hitDieCalculation)
                    print Player, "uses", numHitDice, hitDieString, "to recover", DnDUtil.getHealText(health), "health"

                elif (initCommand == 'u' or initCommand == 'use' and numArgs >= 2):
                    abilityName = SpellUtil.autoCompleteAbility(command[1],PlayerData['UseAbilities'])
                    if (abilityName):
                        ability = PlayerData['UseAbilities'][abilityName]
                        takenAction = ability['Use Turn?']
                        actionKey = 'Actions'
                        baseLevel = ability['Base Level']
                        if (baseLevel == 0):
                            spellLevel = 0
                        elif (numArgs >= 3 and command[2].isdigit()):
                            spellLevel = int(command[2])
                        else:
                            spellLevel = baseLevel

                        if (baseLevel > 0):
                            while (spellLevel < 1 or spellLevel > 9 or spellLevel < baseLevel):
                                spellLevel = DnDUtil.getInt(raw_input("Invalid spell level! Try again (base level "+str(baseLevel)+"): "))
                            if (spellLevel > baseLevel and 'Scaled Actions' in ability):
                                actionKey = 'Scaled Actions'
                        elif (spellLevel == 0 and 'Scaled Actions' in ability):
                            actionKey = 'Scaled Actions'

                        if (ability['Attack Mod']):
                            spellAtk = ability['Attack Mod']
                        else:
                            spellAtk = PlayerData['SpellAtk']
                        if (ability['DC'] == 0):
                            spellDC = PlayerData['SpellDC']
                        else:
                            spellDC = ability['DC']

                        actionData = deepcopy(ability[actionKey])
                        actionData = SpellUtil.replaceSpellMod(actionData,PlayerData)
                        actionData2 = []
                        if (actionKey == 'Scaled Actions'):
                            if (spellLevel != 0):
                                lvlReplacement = spellLevel-ability['Base Level']
                            else:
                                lvlReplacement = SpellUtil.getCantripModifierForActor(Player,PlayerData)
                            actionData = SpellUtil.replaceLvl(actionData,lvlReplacement)
                            if ('Scaled Actions2' in ability):
                                actionData2 = SpellUtil.replaceLvl(deepcopy(ability[actionKey+'2']),lvlReplacement)
                                actionData2 = SpellUtil.replaceSpellMod(actionData2,PlayerData)
                        elif ('Actions2' in ability):
                            actionData2 = deepcopy(ability['Actions2'])
                            actionData2 = SpellUtil.replaceSpellMod(actionData2,PlayerData)

                        half = False
                        if (hex and ability['Attack']):
                            actionData.append(['damage','1d6','necrotic'])
                            actionData2.append(['damage','1d6','necrotic'])
                            print abilityName, "will deal 1d6 additional necrotic damage due to hex!"
                        if (ability['Save']):
                            print "SAVE:", ability['Save'], "(DC", str(spellDC)+')'
                            if (ability['Save Result'] == 'half'):
                                half = True
                    
                        multiHitSpell = abilityName in ['eldritchblast','eldritchblast2','scorchingray','magicmissile']
                        if (multiHitSpell):
                            if (abilityName.startswith('eldritchblast')):
                                maxHits = SpellUtil.getCantripModifierForActor(Player,PlayerData)
                            else:
                                maxHits = spellLevel-ability['Base Level']+3
                        else:
                            maxHits = 1
                        numCrits = 0
                        numMisses = 0
                        print "---------------------------------------------------"
                        for i in range(0,maxHits):
                            if (ability['Attack']):
                                attackRoll = makeRoll(spellAtk,advantage,disadvantage,guidance,bane,0,extraRollMods)[0]
                                if (attackRoll == 1):
                                    numMisses += 1
                                elif (attackRoll == 20 or hexbladesCurse and attackRoll == 19):
                                    numCrits += 1
                                print "---------------------------------------------------"

                        if (maxHits > 1 and not(ability['Attack'])):
                            numHits = maxHits
                        elif (maxHits > 1):
                            numHits = -1
                            while (numHits < 0 or numHits > maxHits-numMisses):
                                numHits = DnDUtil.getInt(raw_input("How many times did "+abilityName+" hit the target? (max "+str(maxHits-numMisses)+") "))
                            print "---------------------------------------------------"
                        else:
                            numHits = 1-numMisses

                        abilityDamageSummary = {}
                        dataDictSize = len(PlayerDataDict)
                        firstHit = True
                        for i in range(0,numHits):
                            damageSummary = useAbility(abilityName,ability['Duration'],actionData,actionData2,ability['Save'],half,numCrits > 0,firstHit,spellDC,ability['Base Level'],spellLevel,advantage,disadvantage,guidance,bane,hex,huntersMark,hexbladesCurse,extraRollMods)
                            extendDamageSummary(abilityDamageSummary,damageSummary)
                            numCrits -= 1
                            firstHit = False
                        if (numHits > 1):
                            printDamageSummary(abilityDamageSummary)
                        if (dataDictSize != len(PlayerDataDict)):
                            takenAction = True
                            breakLoop = True
                    else:
                        print "Invalid ability", command[1]

                elif (initCommand == 'ss' and numArgs == 2):
                    shapeShift(command[1])

                elif (initCommand == 'revert' and numArgs == 1):
                    revertForm()

                elif (initCommand == 'add' and numArgs == 2):
                    newCharacterData = getCharacterData(command[1])
                    if (newCharacterData):
                        takenAction = True
                        breakLoop = True
                        PlayerDataDict[command[1].capitalize()] = newCharacterData
                        print "Player", command[1].capitalize(), "has been added!"
                    else:
                        print "Could not find player", command[1], "in", CHARACTER_FILE+'!'

                elif (initCommand == 'kill' and (numArgs == 1 or numArgs == 2)):
                    if (numArgs == 1):
                        target = Player
                    else:
                        target = command[1].capitalize()
                    if (target in PlayerDataDict):
                        takenAction = True
                        breakLoop = True
                        del PlayerDataDict[target]
                        print target, "has been removed!"
                    else:
                        print "Invalid kill target", target

                elif ((initCommand == 'm' or initCommand == 'r' or initCommand == 'melee' or initCommand == 'ranged' or ((initCommand[0] == 'm' or initCommand[0] == 'r') and len(initCommand) > 1 and initCommand[1:].isdigit()))):
                    takenAction = True
                    if (initCommand[0] == 'm'):
                        rangeIndex = 0
                    else:
                        rangeIndex = 1
                    if (len(initCommand) > 1 and initCommand[1:].isdigit()):
                        atkIndex = int(initCommand[1:])
                    else:
                        atkIndex = 0
                    makeAttack(rangeIndex,atkIndex,advantage,disadvantage,guidance,bane,hex,huntersMark,hexbladesCurse,extraRollMods)

                elif (initCommand == 'str' or initCommand == 'ath'):
                    makeAbilityCheck('str',initCommand,advantage,disadvantage,guidance,bane,proficiencyBonus,extraRollMods)

                elif (initCommand == 'dex' or initCommand == 'init' or initCommand == 'acr' or initCommand == 'sle' or initCommand == 'ste'):
                    makeAbilityCheck('dex',initCommand,advantage,disadvantage,guidance,bane,proficiencyBonus,extraRollMods)
                    if (initCommand == 'init'):
                        takenAction = True

                elif (initCommand == 'con'):
                    makeAbilityCheck('con',initCommand,advantage,disadvantage,guidance,bane,proficiencyBonus,extraRollMods)

                elif (initCommand == 'int' or initCommand == 'arc' or initCommand == 'his' or initCommand == 'inv' or initCommand == 'nat' or initCommand == 'rel'):
                    makeAbilityCheck('int',initCommand,advantage,disadvantage,guidance,bane,proficiencyBonus,extraRollMods)

                elif (initCommand == 'wis' or initCommand == 'ani' or initCommand == 'ins' or initCommand == 'med' or initCommand == 'perc' or initCommand == 'sur'):
                    makeAbilityCheck('wis',initCommand,advantage,disadvantage,guidance,bane,proficiencyBonus,extraRollMods)

                elif (initCommand == 'cha' or initCommand == 'dec' or initCommand == 'inti' or initCommand == 'perf' or initCommand == 'pers'):
                    makeAbilityCheck('cha',initCommand,advantage,disadvantage,guidance,bane,proficiencyBonus,extraRollMods)

                elif (initCommand == 'strs' or initCommand == 'dexs' or initCommand == 'cons' or initCommand == 'ints' or initCommand == 'wiss' or initCommand == 'chas'):
                    ability = initCommand[:3].capitalize()
                    makeRoll(PlayerData[ability],advantage,disadvantage,guidance,bane,proficiencyBonus,extraRollMods)

                elif (initCommand == 'deaths'):
                    if ('deathsave' in PlayerData['Misc']):
                        deathSaveBonus = PlayerData['Misc']['deathsave']
                    else:
                        deathSaveBonus = 0
                    makeRoll(deathSaveBonus,advantage,disadvantage,guidance,bane,proficiencyBonus,extraRollMods)

                elif (initCommand == 'conc' and numArgs >= 1):
                    if (numArgs == 1 or not(command[1].isdigit())):
                        damage = -1
                    else:
                        damage = int(command[1])
                    while (damage < 0):
                        damageString = raw_input('How much damage was taken? ')
                        if (damageString):
                            damage = DnDUtil.getInt(damageString)
                        else:
                            damage = 20
                    concDC = max(10,damage/2)
                    print "Concentration DC is", concDC
                    proficiencyBonus = getProficiencyBonusForCommand('cons')
                    if (bladesong):
                        proficiencyBonus += PlayerData['Int']
                    resultList = makeRoll(PlayerData['Con'],advantage,disadvantage,guidance,bane,proficiencyBonus,extraRollMods)
                    concRoll = resultList[0]
                    concResult = resultList[1]
                    if (concRoll == 20 or concRoll != 1 and concResult >= concDC):
                        print Player, DnDUtil.getPassText('passed'), "the concentration check!"
                    else:
                        print Player, DnDUtil.getFailText('failed'), "the conecentration check"

                elif (initCommand in ['aov','aove','auraofvitality','auraofvitalitye'] and numArgs == 2):
                    if (initCommand[-1] == 'e'):
                        extended = True
                    else:
                        extended = False
                    hpStringList = DnDUtil.mySplit(command[1],',')
                    hpValues = []
                    for hpString in hpStringList:
                        hpValues.append(DnDUtil.getInt(hpString))
                    auraOfVitality(hpValues,extended,'dol' in PlayerData['Misc'])

                elif (proficiencyBonus > 0):
                    makeRoll(0,advantage,disadvantage,guidance,bane,proficiencyBonus,extraRollMods)

                elif (initCommand == 'skip'):
                    takenAction = True

                else:
                    print "Invalid Command"
            # triggered if PlayerDataDict's size changes during iteration (i.e. add/kill commands)
            if (breakLoop):
                break

def getExtraRollMod(command):

    parsedCommand = command.split('d')
    try:
        if (parsedCommand[0] == '' or parsedCommand[0] == '+' or parsedCommand[0] == '-'):
            parsedCommand[0] += '1'
        numRolls = int(parsedCommand[0])
        dieNum = int(parsedCommand[1])
        if (numRolls < 0):
            signMult = -1
            numRolls *= -1
        else:
            signMult = 1
        return signMult*DnDUtil.calculate(str(numRolls)+'d'+str(dieNum),False)
    except ValueError:
        return 0

    return 0

def getProficiencyBonusForCommand(initCommand):

    if (initCommand in PlayerData['Misc']):
        proficiencyBonus = PlayerData['Misc'][initCommand]
    elif (initCommand in PlayerData['Expertise']):
        proficiencyBonus = 2*PlayerData['ProfBonus']
    elif (initCommand in PlayerData['Proficiencies']):
        proficiencyBonus = PlayerData['ProfBonus']
    elif ('joat' in PlayerData['Misc'] and not(initCommand in ['strs','dexs','cons','ints','wiss','chas','deaths'])):
        proficiencyBonus = PlayerData['ProfBonus']/2
    else:
        proficiencyBonus = 0
    return proficiencyBonus

def displayStats():

    print "Name:", Player
    print "Level/CR:", PlayerData['CR']
    print "Size:", PlayerData['Size']
    if (PlayerData['HP'] != '0'):
        print "HP:", PlayerData['HP']
    print "Hit Die:", PlayerData['HD']
    print "Move Speed:", PlayerData['Move']
    print "Proficiency Bonus:", PlayerData['ProfBonus']
    print "Proficiencies:", PlayerData['Proficiencies']
    print "Expertise:", PlayerData['Expertise']
    print "Atk:", PlayerData['Atk']
    print "Damage:", PlayerData['Damage'], "Damage Bonus:", PlayerData['DmgBonus']
    print "On-Hit Abilities:", PlayerData['OnHitAbilities']
    print "Weapon Types:", PlayerData['WeaponTypes']
    print "Spell Atk:", PlayerData['SpellAtk'], "Spell DC:", PlayerData['SpellDC']
    print "UseAbilities:"
    for ability in PlayerData['UseAbilities']:
        print ability, "-", PlayerData['UseAbilities'][ability]
    print "Str:", PlayerData['Str'], "Dex:", PlayerData['Dex'], "Con:", PlayerData['Con'], "Int:", PlayerData['Int'], "Wis:", PlayerData['Wis'], "Cha:", PlayerData['Cha']
    print "Advantages:", PlayerData['Advantages'], "Disadvantages:", PlayerData['Disadvantages']
    print "Misc:", PlayerData['Misc']

def makeAttack(rangeIndex,atkIndex,advantage,disadvantage,guidance,bane,hex,huntersMark,hexbladesCurse,extraRollMods,atkBonus=0,dmgBonus=0):

    if (rangeIndex >= len(PlayerData['Atk'])):
        DnDUtil.printError(Player+" does not have a ranged attack")
    elif (atkIndex >= len(PlayerData['Atk'][rangeIndex])):
        DnDUtil.printError(Player+" does not have an attack at index "+str(rangeIndex)+str(atkIndex))
    else:
        print "---------------------------------------------------"
        for i in range(0,len(PlayerData['Atk'][rangeIndex][atkIndex])):
            attackRoll = makeRoll(PlayerData['Atk'][rangeIndex][atkIndex][i]+atkBonus,advantage,disadvantage,guidance,bane,0,extraRollMods)[0]
            if (attackRoll != 1):
                crit = False
                critC = getCritStat(rangeIndex,atkIndex,i,0)
                if (attackRoll >= critC or hexbladesCurse and attackRoll == 19):
                    print "This attack crits!"
                    crit = True
                    critMultiplier = getCritStat(rangeIndex,atkIndex,i,1)
                else:
                    critMultiplier = 1
                baseWeaponDamage = DnDUtil.calculate(PlayerData['Damage'][rangeIndex][atkIndex][i])
                if (huntersMark):
                    print Player, "will deal an additional 1d6 damage from hunter's mark!"
                    baseWeaponDamage += DnDUtil.calculate('1d6')
                if (hex):
                    print Player, "will deal an additional 1d6 necrotic damage from hex!"
                    hexDamage = critMultiplier*DnDUtil.calculate('1d6')
                if (hexbladesCurse):
                    print Player, "will deal an additional", PlayerData['ProfBonus'], "damage from hexblade's curse!"
                    dmgBonus += PlayerData['ProfBonus']
                    
                damage = int(critMultiplier*baseWeaponDamage) + PlayerData['DmgBonus'][rangeIndex][atkIndex][i] + dmgBonus
                weaponTypes = PlayerData['WeaponTypes'][rangeIndex][atkIndex][i]
                if (weaponTypes):
                    if ('nonmagic' in weaponTypes):
                        magicString = 'nonmagical '
                    elif ('magic' in weaponTypes):
                        magicString = 'magical '
                    else:
                        magicString = ''
                    mainWeaponType = weaponTypes[0]
                else:
                    magicString = ''
                    mainWeaponType = ''

                print Player, "deals", DnDUtil.getDamageText(damage), magicString+mainWeaponType, "damage"
                if (hex):
                    print Player, "deals", DnDUtil.getDamageText(hexDamage), "necrotic damage"

                if (rangeIndex < len(PlayerData['OnHitAbilities']) and atkIndex < len(PlayerData['OnHitAbilities'][rangeIndex])):
                    if (len(PlayerData['OnHitAbilities'][rangeIndex][atkIndex]) == 1):
                        onHitAbility = PlayerData['OnHitAbilities'][rangeIndex][atkIndex][0]
                    elif (len(PlayerData['OnHitAbilities'][rangeIndex][atkIndex]) == len(PlayerData['Atk'][rangeIndex][atkIndex])):
                        onHitAbility = PlayerData['OnHitAbilities'][rangeIndex][atkIndex][i]
                    else:
                        DnDUtil.printError("Invalid on hit abilities format!")
                        onHitAbility = {}
                else:
                    onHitAbility = {}

                if (onHitAbility):
                    success = True
                    actionData = deepcopy(onHitAbility['Actions'])
                    if ('Actions2' in onHitAbility):
                        actionData2 = deepcopy(onHitAbility['Actions2'])
                    else:
                        actionData2 = {}
                    triggerCondition = onHitAbility['Trigger Condition']
                    triggerConditionSuccess = True
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

                    if (not(triggerConditionSuccess)):
                        # if we failed the initial trigger condition and this ability rerquires a save, we have already failed since secondary actions would then apply to the save result instead
                        if (onHitAbility['Save'] or not(actionData2)):
                            success = False

                    if (success):
                        print "---------------------------------------------------"
                        half = False
                        if (onHitAbility['Save']):
                            print "SAVE:", onHitAbility['Save'], "(DC", str(onHitAbility['DC'])+')'
                            if (onHitAbility['Save Result'] == 'half'):
                                half = True
                        useAbility('On Hit Ability',onHitAbility['Duration'],actionData,actionData2,onHitAbility['Save'] != '',half,crit,True,onHitAbility['DC'],-1,-1,advantage,disadvantage,guidance,bane,False,False,False,extraRollMods)
            print "---------------------------------------------------"

def makeAbilityCheck(abilityUsed,checkType,advantage,disadvantage,guidance,bane,proficiencyBonus,extraRollMods):

    ability = abilityUsed.capitalize()
    makeRoll(PlayerData[ability],advantage,disadvantage,guidance,bane,proficiencyBonus,extraRollMods)

def makeRoll(rollBonus,advantage,disadvantage,guidance,bane,proficiencyBonus,extraRollMods):

    rollString = ''

    if (advantage and not(disadvantage)):
        rollType = 1
        rollString += '(with advantage) '
    elif (disadvantage and not(advantage)):
        rollType = -1
        rollString += '(with disadvantage) '
    else:
        rollType = 0

    roll = random.randint(1,20)
    if (rollType):
        roll2 = random.randint(1,20)
        rollString += '(' + str(roll) + ',' + str(roll2) + ')'
        if (rollType == 1):
            roll = max(roll,roll2)
        else:
            roll = min(roll,roll2)

    result = roll + proficiencyBonus + rollBonus
    if (guidance and not(bane)):
        guidanceBonus = random.randint(1,4)
        result += guidanceBonus
        if (rollString):
            rollString += ' '
        rollString += '(+'+str(guidanceBonus)+' guidance)'
    elif (bane and not(guidance)):
        banePenalty = random.randint(1,4)
        result -= banePenalty
        if (rollString):
            rollString += ' '
        rollString += '(-'+str(banePenalty)+' bane)'

    for extraRollMod in extraRollMods:
        result += extraRollMod
        if (rollString):
            rollString += ' '
        if (extraRollMod > 0):
            rollString += '(+'+str(extraRollMod)+' extra)'
        else:
            rollString += '('+str(extraRollMod)+' extra)'
        
    if (roll == 20):
        print "You rolled a", DnDUtil.getPassText("NATURAL 20")+'!', "^_^", '('+str(result)+')', rollString
    elif (roll == 1):
        print "You rolled a", DnDUtil.getFailText(1), "D:", '('+str(result)+')', rollString
    else:
        print "You rolled a", result, "(natural", str(roll)+')', rollString

    return [roll, result]

def useAbility(abilityName,abilityDuration,actions,actions2,saveType,half,crit,firstHit,saveDC,baseLevel,spellLevel,advantage,disadvantage,guidance,bane,hex,huntersMark,hexbladesCurse,extraRollMods):

    failActionsResults = []
    passActionsResults = []
    damageSummary = {}
    if (abilityDuration):
        durationString = getDurationString(abilityDuration)
    else:
        durationString = ''
    
    for i in range(0,2):
        if (i == 0):
            currentActions = actions
            currentActionsResults = failActionsResults
        else:
            currentActions = actions2
            currentActionsResults = passActionsResults

        j = 0
        while (j < len(currentActions)):
            action = currentActions[j]
            actionType = action[0]
            numArgs = len(action)

            if (actionType == 'damage' or actionType == 'idamage' or actionType == 'lifesteal' or actionType == 'ilifesteal' or actionType == 'halfsteal' or actionType == 'ihalfsteal' or actionType == 'soulharvest' or actionType == 'isoulharvest'):
                if (numArgs >= 2):
                    if (i == 1 and actions2 and action in actions):
                        None
                    else:
                        parsedDamage = DnDUtil.parseDamageCalculation(action[1])
                        damageTypes = action[2:]
                        if (damageTypes):
                            mainDamageType = damageTypes[0]
                        else:
                            mainDamageType = ''

                        if ('eb' in PlayerData['Misc'] and 'fire' in damageTypes and 'Wildfirespirit' in PlayerDataDict and firstHit):
                            parsedDamage[0] = DnDUtil.simplifyCalculation(parsedDamage[0]+'+1d8')
                            print abilityName, "will deal an additional 1d8 damage due to", Player+"'s enhanced bond!"
                
                        if (parsedDamage[0].isdigit()):
                            baseDamage = int(parsedDamage[0])
                        else:
                            baseDamage = DnDUtil.calculate(parsedDamage[0])

                        damage = baseDamage + parsedDamage[1]
                        if (crit):
                            damage += baseDamage
                        if (hexbladesCurse):
                            print "Target takes an additional", PlayerData['ProfBonus'], "damage due to hexblade's curse"
                            damage += PlayerData['ProfBonus']

                    if (half and i == 1):
                        damage /= 2

                    if (actionType[0] == 'i'):
                        improvedDamageString = " and loses it from max hp!"
                    else:
                        improvedDamageString = ''

                    if (actionType.find('damage') != -1):
                        healString = ''
                    else:
                        healStringPrefix = ''
                        baseHealAmount = 0
                        healStringSuffix = ''
                        healBonus = 0
                        if (actionType.find('lifesteal') != -1):
                            healStringPrefix = Player+' heals '
                            baseHealAmount = damage
                            healStringSuffix = ' hp'
                            if ('dol' in PlayerData['Misc'] and spellLevel >= 1):
                                healBonus = 2 + spellLevel
                                print abilityName, "will heal for an additional", healBonus, "hp due to", Player+"'s disciple of life!"
                            if ('eb' in PlayerData['Misc'] and 'Wildfirespirit' in PlayerDataDict):
                                healBonus = DnDUtil.calculate('1d8')
                                print abilityName, "will heal for an additional", healBonus, "hp due to", Player+"'s enhanced bond!"
                        elif (actionType.find('halfsteal') != -1):
                            healStringPrefix = Player+' heals '
                            baseHealAmount = damage/2
                            healStringSuffix = ' hp'
                            if ('dol' in PlayerData['Misc'] and spellLevel >= 1):
                                healBonus = 2 + spellLevel
                                print abilityName, "will heal for an additional", healBonus, "hp due to", Player+"'s disciple of life!"
                            if ('eb' in PlayerData['Misc'] and 'Wildfirespirit' in PlayerDataDict):
                                healBonus = DnDUtil.calculate('1d8')
                                print abilityName, "will heal for an additional", healBonus, "hp due to", Player+"'s enhanced bond!"
                        elif (actionType.find('soulharvest') != -1):
                            healStringPrefix = Player+' gains '
                            baseHealAmount = damage
                            healStringSuffix = ' temp hp'
                        healString = healStringPrefix+str(baseHealAmount+healBonus)+healStringSuffix

                    currentActionsResults.append("Target takes "+DnDUtil.getDamageText(damage)+' '+mainDamageType+" damage"+improvedDamageString)
                    damageSummary[mainDamageType] = damage
                    if (healString):
                        currentActionsResults.append(healString)
                    if (half and i == 0 and not(actions2)):
                        passActionsResults.append("Target takes "+DnDUtil.getDamageText(damage/2)+' '+mainDamageType+" damage"+improvedDamageString)
                        if (healString):
                            passActionsResults.append(healStringPrefix+DnDUtil+healStringSuffix)
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == 'heal'):
                if (numArgs == 2):
                    if ('dol' in PlayerData['Misc'] and spellLevel >= 1):
                        healBonus = 2 + spellLevel
                        print abilityName, "will heal for an additional", healBonus, "hp due to", Player+"'s disciple of life!"
                    else:
                        healBonus = 0
                    if ('eb' in PlayerData['Misc'] and 'Wildfirespirit' in PlayerDataDict):
                        action[1] = DnDUtil.simplifyCalculation(action[1]+'+1d8')
                        print abilityName, "will heal for an additional 1d8 hp due to", Player+"'s enhanced bond!"
                        
                    if (action[1].isdigit()):
                        amount = int(action[1])
                    else:
                        amount = DnDUtil.calculate(action[1])
                    amount += healBonus
                    currentActionsResults.append("Target heals for "+DnDUtil.getHealText(amount))
                    if ('bh' in PlayerData['Misc'] and spellLevel >= 1):
                        currentActionsResults.append(Player+" heals for "+DnDUtil.getHealText(2+spellLevel)+" if "+abilityName+" healed another creature")
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == 'temphp'):
                if (numArgs == 2):
                    if (action[1].isdigit()):
                        tempHP = int(action[1])
                    else:
                        tempHP = DnDUtil.calculate(action[1])
                    currentActionsResults.append("Target gains "+str(tempHP)+" temp hp")
                else:
                     print "Invalid number of arguments for action", actionType

            elif (actionType == 'kill'):
                if (numArgs == 1):
                    currentActionsResults.append("Target is instantly killed!")
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == 'cc'):
                if (numArgs == 2 or numArgs == 3):
                    type = action[1]
                    if (numArgs == 3):
                        if (action[2].isdigit()):
                            duration = int(action[2])
                        else:
                            duration = DnDUtil.calculate(action[2])
                    else:
                        if (abilityDuration):
                            duration = abilityDuration
                        else:
                            duration = -1
                    if (abilityDuration and abilityDuration != duration):
                        DnDUtil.printWarning("Attempting to overwrite previously given ability duration of "+str(abilityDuration)+" with cc duration of "+str(duration)+"! Defaulting to original duration")
                        duration = abilityDuration
                    else:
                        abilityDuration = duration
                        durationString = getDurationString(abilityDuration)
                    
                    currentActionsResults.append("Target will be under the effect of "+type+' '+durationString)
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == 'ccsave' or actionType == 'ccsave3'):
                if (numArgs == 3 or numArgs == 4):
                    type = action[1]
                    clearTiming = action[2]
                    if (numArgs == 4):
                        if (action[3].isdigit()):
                            duration = int(action[3])
                        else:
                            duration = DnDUtil.calculate(action[3])
                    else:
                        if (abilityDuration):
                            duration = abilityDuration
                        else:
                            duration = -1
                    if (abilityDuration and abilityDuration != duration):
                        DnDUtil.printWarning("Attempting to overwrite previously given ability duration of "+str(abilityDuration)+" with cc duration of "+str(duration)+"! Defaulting to original duration")
                        duration = abilityDuration
                    else:
                        abilityDuration = duration
                        durationString = getDurationString(abilityDuration)
                    if (clearTiming == 'start' or clearTiming == 'end'):
                        clearTimingString = 'at the '+clearTiming+' of its turn'
                    elif (clearTiming == 'action'):
                        clearTimingString = 'using an action to make an ability check'
                    else:
                        clearTimingString = ''
                    if (actionType == 'ccsave'):
                        multiSaveString = ''
                    else:
                        multiSaveString = ' 3 times, otherwise, the effect is permanent'
                    currentActionsResults.append("Target will be under the effect of "+type+' '+durationString+" unless it makes the save "+clearTimingString+multiSaveString)
        
            elif (actionType == 'buff' or actionType == 'debuff' or actionType == 'drain'):
                if (numArgs == 3):
                    type = action[1]
                    if (action[2].isdigit()):
                        amount = int(action[2])
                    else:
                        amount = DnDUtil.calculate(action[2])

                    if (actionType == 'buff'):
                        currentActionsResults.append("Target gains "+str(amount)+' '+type)
                    elif (actionType == 'debuff'):
                        currentActionsResults.append("Target loses "+str(amount)+' '+type)
                    else:
                        currentActionsResults.append(Player+" gains "+str(amount)+' '+type+" and Target loses "+str(amount)+' '+type)
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == 'move'):
                if (numArgs == 2 or numArgs == 3):
                    if (numArgs == 2):
                        moveDelta = action[1]
                        if (moveDelta.isdigit()):
                            currentActionsResults.append("Target increases its move speed by "+moveDelta)
                        elif (moveDelta == 'double'):
                            currentActionsResults.append("Target doubles its move speed")
                        elif (moveDelta == 'half'):
                            currentActionsResults.append("Target halves its move speed")
                        else:
                            DnDUtil.printError("Unknown move delta "+moveDelta+" valid deltas are double, half, and any integer")
                    else:
                        moveType = action[1].capitalize()
                        currentActionsResults.append("Target's "+moveType+" speed is set to "+action[2])
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == 'immobilize'):
                if (numArgs == 1):
                    currentActionsResults.append("Target is immobilized!")
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == 'grapple'):
                if (numArgs == 1 or numArgs == 2):
                    if (numArgs == 2):
                        escapeDC = int(action[1])
                    else:
                        escapeDC = 0
                
                    if (escapeDC):
                        currentActionsResults.append(Player+" grapples Target with an escape DC of "+str(escapeDC))
                    else:
                        currentActionsResults.append(Player+" attempts to grapple Target")
                    if ('igrapple' in PlayerData['Misc']):
                        currentActionsResults.append("If the grapple succeeds, Target is restrained!")
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == 'attack'):
                if (numArgs == 3):
                    rangeIndex = int(action[1])
                    atkIndex = int(action[2])
                    makeAttack(rangeIndex,atkIndex,advantage,disadvantage,guidance,bane,hex,huntersMark,hexbladesCurse,extraRollMods)
                    currentActionsResults.append(Player+" makes an attack against target (see above)")
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == 'summon'):
                if (numArgs == 2 or numArgs == 3):
                    creatureType = action[1]
                    if (numArgs == 3):
                        if (action[2].isdigit()):
                            number = int(action[2])
                        else:
                            number = DnDUtil.calculate(action[2])
                    else:
                        if (creatureType != 'input'):
                            DnDUtil.printError("Not enough arguments for a non-input creature type! Converting to input")
                            creatureType = 'input'

                    if (creatureType == 'input'):
                        creatureType = raw_input('Enter a creature to summon: ')
                        number = 1

                    newCharacterData = getCharacterData(creatureType)
                    if (newCharacterData):
                        PlayerDataDict[creatureType.capitalize()] = newCharacterData
                        print "Player", creatureType.capitalize(), "has been added!"
                        resultString = Player+" summons "+str(number)+" "+creatureType+"(s) lasting "+durationString
                        currentActionsResults.append(resultString)
                    else:
                        print "Could not find player", creatureType, "in", CHARACTER_FILE+'!'
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == 'immunity' or actionType == 'resist' or actionType == 'vulnerability' or actionType == 'adv' or actionType == 'dis'):
                if (numArgs >= 2):
                    types = action[1:]
                    for type in types:
                        resultString = "Target now has "+type+' '+actionType+' '+durationString
                        currentActionsResults.append(resultString)
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == 'mc'):
                if (numArgs == 1):
                    currentActionsResults.append("Target is mind-controlled!")
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == 'ss'):
                if (numArgs == 2):
                    if (action[1] == 'input'):
                        currentActionsResults.append("Target shapeshifts into some unknown form")
                    else:
                        currentActionsResults.append("Target shapeshifts into a "+action[1])
                else:
                    print "Invalid number of arguments for action", actionType

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
                    if (dotTypes):
                        primaryDotType = dotTypes[0]
                    else:
                        primaryDotType = 'unknown'

                    if (dotTiming == 'target'):
                        timingString = "its"
                    else:
                        timingString = Player+"'s"
                
                    resultString = "Target has received a DoT, taking "+action[1]+" "+primaryDotType+" damage at the start of each of "+timingString+" turns lasting "+durationString
                    if (dotSave):
                        resultString += " ("+dotSave[0]+" save "+dotSave[2]+" DC "+str(dotSave[1])+")"
                    currentActionsResults.append(resultString)
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == 'wound'):
                if (numArgs == 2 or numArgs == 3):
                    woundDamage = action[1]
                    if (numArgs == 3):
                        woundDC = int(action[2])
                    else:
                        woundDC = saveDC
                    currentActionsResults.append("Target is wounded, taking "+woundDamage+" damage (this damage stacks with more hits) at the start of each of its turn until it receives magical healing or spends an action to make a DC "+str(saveDC)+" medicine check (undead and constructs are immune to this effect)")
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == 'react'):
                if (numArgs == 1):
                    resultString = "Target can't take reactions "+durationString
                    currentActionsResults.append(resultString)
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == 'prone'):
                if (numArgs == 1):
                    currentActionsResults.append("Target is now "+DnDUtil.getStatusText('prone')+'!')
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == 'misc'):
                if (numArgs == 3):
                    miscStat = action[1]
                    miscArg = action[2]
                    currentActionsResults.append("Target now has the misc stat "+miscStat+" with argument "+miscArg)
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == 'bonusattack'):
                if (numArgs == 1):
                    currentActionsResults.append("Target can make an extra attack!")
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == 'use' or actionType == 'useon'):
                if (numArgs == 2):
                    secondaryAbilityName = action[1]
                    secondaryAbility = ImportUtil.loadAbilityData(secondaryAbilityName,[''],True)
                    if (secondaryAbility):
                        if (secondaryAbility['Trigger Duration']):
                            resultString = "Trigger "+secondaryAbilityName+" is now active for "+str(secondaryAbility['Trigger Duration'])+" turns!"
                            currentActionsResults.append(resultString)
                        elif (secondaryAbility['Actions'] == [['']]):
                            print "Ability", secondaryAbilityName, "not found!"
                        else:
                            if ('Scaled Actions' in secondaryAbility and (spellLevel > secondaryAbility['Base Level'] or secondaryAbility['Base Level'] == 0)):
                                secondaryActionKey = 'Scaled Actions'
                            else:
                                secondaryActionKey = 'Actions'

                            secondaryActionData = secondaryAbility[secondaryActionKey]
                            secondaryActionData = SpellUtil.replaceSpellMod(secondaryActionData,PlayerData)
                            secondaryActionData2 = []
                            if (secondaryActionKey == 'Scaled Actions'):
                                if (spellLevel != 0):
                                    lvlReplacement = spellLevel-baseLevel
                                else:
                                    lvlReplacement = SpellUtil.getCantripModifierForActor(Player,PlayerData)
                                secondaryActionData = SpellUtil.replaceLvl(secondaryActionData,lvlReplacement)
                                if ('Scaled Actions2' in secondaryAbility):
                                    secondaryActionData2 = SpellUtil.replaceLvl(deepycopy(secondaryAbility[secondaryActionKey+'2']),lvlReplacement)
                                    secondaryActionData2 = SpellUtil.replaceSpellMod(secondaryActionData2,actorData)
                            elif ('Actions2' in secondaryAbility):
                                secondaryActionData2 = deepcopy(secondaryAbility['Actions2'])
                                secondaryActionData2 = SpellUtil.replaceSpellMod(secondaryActionData2,actorData)

                            if (saveDC == 0):
                                secondarySaveDC = actorData['SpellDC']
                            else:
                                secondarySaveDC = saveDC
                            
                            if (secondaryAbility['Save'] != ''):
                                print "SAVE:", secondaryAbility['Save'], "(DC", str(secondarySaveDC)+')'
                            useAbility(secondaryAbilityName,secondaryAbility['Duration'],secondaryActionData,secondaryActionData2,secondaryAbility['Save'],secondaryAbility['Save Result'] == 'half',crit,firstHit,secondarySaveDC,secondaryAbility['Base Level'],spellLevel,advantage,disadvantage,guidance,bane,hex,huntersMark,hexbladesCurse,extraRollMods)
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == 'onhit'):
                if (numArgs == 2 or numArgs == 3):
                    onHitAbilityName = action[1]
                    if (numArgs == 3):
                        charges = int(action[2])
                    else:
                        charges = -1
                    resultString = "Target gains the on-hit ability "+onHitAbilityName
                    if (charges != -1):
                        resultString += " lasting for "+str(charges)+ " hit(s)"
                    currentActionsResults.append(resultString)
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == 'msg'):
                if (numArgs == 2):
                    msg = action[1]
                    msg = msg.replace('actor',Player).replace('target','Target')
                    currentActionsResults.append(msg)
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == 'script'):
                if (numArgs == 1 or numArgs == 2):
                    if (numArgs == 2):
                        scriptAbilityName = action[1]
                    else:
                        scriptAbilityName = abilityName
                    scriptArgs = [False,scriptAbilityName,[],abilityDuration,currentActions[:],False,[],'Target',{},Player,PlayerData,PlayerData['SpellAtk'],saveType,saveDC,0 if i == 0 else 1,baseLevel,spellLevel,half,crit,False,False,{},[]]
                    # code copied and adapted from main useAbility function
                    try:
                        Spells.useAbility(scriptArgs)
                        # overwrite the current ability arguments using the values from the script
                        #playerTurn = scriptArgs[0]
                        scriptAbilityName = scriptArgs[1]
                        #abilityTypes = scriptArgs[2]
                        abilityDuration = scriptArgs[3]
                        currentActions = scriptArgs[4]
                        #playerTarget = scriptArgs[5]
                        # no need to copy targets since it can already be easily modified within the script
                        #target = scriptArgs[7]
                        #targetData = scriptArgs[8]
                        #actor = scriptArgs[9]
                        #actorData = scriptArgs[10]
                        spellAtk = scriptArgs[11]
                        saveType = scriptArgs[12]
                        saveDC = scriptArgs[13]
                        #saveDiff = scriptArgs[14]
                        baseLevel = scriptArgs[15]
                        spellLevel = scriptArgs[16]
                        half = scriptArgs[17]
                        crit = scriptArgs[18]
                        #uncannyDodge = scriptArgs[19]
                        #concentration = scriptArgs[20]
                        # no need to copy savedDamageRolls since it can already be easily modified within the script
                        # no need to copy abilityEffects since it can already be easily modified within the script
                    except KeyError:
                        print "Unable to run script", scriptAbilityName, "due to KeyError!"
                    except ValueError:
                        print "Unable to run script", scriptAbilityName, "due to ValueError!"
                    except IndexError:
                        print "Unable to run script", scriptAbilityName, "due to IndexError!"
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == 'addtarget'):
                if (numArgs == 1 or numArgs == 2):
                    if (numArgs == 2):
                        numExtraTargets = int(action[1])
                    else:
                        numExtraTargets = 1
                    currentActionsResults.append("Add "+str(numExtraTargets)+" additional targets to "+abilityName)
                else:
                    print "Invalid number of arguments for action", actionType

            elif (actionType == ''):
                return

            else:
                print "Invalid action type", actionType
            j += 1

    if (saveType):
        if (failActionsResults):
            print DnDUtil.getFailText("ON FAIL:"),
            for result in failActionsResults:
                print result
        if (passActionsResults):
            print DnDUtil.getPassText("ON PASS:"),
            for result in passActionsResults:
                print result
    elif (failActionsResults):
        for result in failActionsResults:
            print result
    print "---------------------------------------------------"
    return damageSummary

def getDurationString(duration):

    if (duration == 'actorstart'):
        return "until the start of "+Player+"'s next turn"
    elif (duration == 'actorend' or duration == 1.5):
        return "until the end of "+Player+"'s next turn"
    elif (duration == 'targetstart'):
        return "until the start of Target's next turn"
    elif (duration == 'targetend'):
        return "until the end of Target's next turn"
    elif (duration == -1):
        return "until cleared"
    elif (duration == 1):
        return "for 1 turn"
    else:
        return "for "+str(duration)+" turns"

def shapeShift(creatureName):

    global Player
    global PlayerData

    creatureData = getCharacterData(creatureName)
    if (creatureData):
        # if the player attempts to shapeshift while already in a form, we'll need to revert that form first
        if (Player.find('(') != -1):
            revertForm()
        # carry these stats over from the player to the new form
        for staticStat in ['Int', 'Wis', 'Cha', 'SpellAtk', 'SpellDC']:
            creatureData[staticStat] = PlayerData[staticStat]
        # carry over all abilities from the player to the creature
        for useAbility in PlayerData['UseAbilities']:
            if (not(useAbility in creatureData['UseAbilities'])):
                creatureData['UseAbilities'][useAbility] = PlayerData['UseAbilities'][useAbility]
        playerProfBonus = PlayerData['ProfBonus']
        creatureProfBonus = creatureData['ProfBonus']
        # if both forms have the same proficiency bonus, just combine all proficiencies and expertise
        if (playerProfBonus == creatureProfBonus):
            creatureData['Expertise'] = list(set(PlayerData['Expertise']+creatureData['Expertise']))
            creatureData['Proficiencies'] = list(set(PlayerData['Proficiencies']+creatureData['Proficiencies']))
        # otherwise, record the player's proficiency bonus for each proficiency that is higher than the creature's
        else:
            for profKey in ['Expertise', 'Proficiencies']:
                if (profKey == 'Expertise'):
                    profMult = 2
                else:
                    profMult = 1
                for proficiency in PlayerData[profKey]:
                    if (proficiency in creatureData['Expertise']):
                        if (playerProfBonus*profMult > creatureProfBonus*2):
                            creatureData['Misc'][proficiency] = playerProfBonus*profMult
                    elif (proficiency in creatureData['Proficiencies']):
                        if (playerProfBonus*profMult > creatureProfBonus):
                            creatureData['Misc'][proficiency] = playerProfBonus*profMult
                    else:
                        creatureData['Misc'][proficiency] = playerProfBonus*profMult

        print Player, "has transformed into a", creatureName+'!'
        del PlayerDataDict[Player]
        Player += ' ('+creatureName+')'
        PlayerData = creatureData
        PlayerDataDict[Player] = PlayerData
    else:
        print "Creature", creatureName, "not found in character data!"

def revertForm():

    global Player
    global PlayerData
    
    formStartIndex = Player.find('(')
    if (formStartIndex != -1):
        del PlayerDataDict[Player]
        Player = Player[:formStartIndex-1]
        PlayerData = getCharacterData(Player.lower())
        PlayerDataDict[Player] = PlayerData
        print Player+"'s", "form has reverted to normal!"
    else:
        DnDUtil.printWarning(Player+"'s form does not need to be reverted")

def auraOfVitality(hpValues,extended,discipleOfLife):

    healCount = 0
    numHeals = 20 if extended else 10
    healMod = 5 if discipleOfLife else 0
    hpHistory = []
    for hpValue in hpValues:
        hpHistory.append([hpValue])
    while (healCount < numHeals and max(hpValues) > 0):
        maxIndex = hpValues.index(max(hpValues))
        healValue = random.randint(1,6) + random.randint(1,6) + healMod
        hpValues[maxIndex] -= healValue
        if (hpValues[maxIndex] < 0):
            hpValues[maxIndex] = 0
        hpHistory[maxIndex].append(hpValues[maxIndex])
        healCount += 1

    totalHealing = 0
    for i in range(0,len(hpHistory)):
        totalHealing += hpHistory[i][0] - hpHistory[i][-1]
        historyString = "Player " + str(i+1)+': '
        for hpValue in hpHistory[i]:
            historyString += str(hpValue)+' -> '
        historyString = historyString[:-4]
        print historyString

    print "Healed a total of", DnDUtil.getHealText(totalHealing), "hp!"
    if (max(hpValues) == 0):
        print DnDUtil.getHealText("Full healed the party in "+str(healCount)+" heals!")