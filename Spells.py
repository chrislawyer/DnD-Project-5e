import random
from copy import copy

import DnDUtil
import ActorUtil
import ImportUtil
import SpellUtil

NUM_ABILITY_ARGS = 23
PlayerTurn = None
AbilityName = None
AbilityTypes = None
AbilityDuration = None
Actions = None
PlayerTarget = None
Targets = None
Target = None
TargetData = None
Actor = None
ActorData = None
SpellAtk = None
SaveType = None
SaveDC = None
SaveDiff = None
BaseLevel = None
SpellLevel = None
Half = None
Crit = None
UncannyDodge = None
Concentration = None
SavedDamageRolls = None
AbilityEffects = None

def loadGlobals(abilityArgs):

    if (len(abilityArgs) == NUM_ABILITY_ARGS):
        global PlayerTurn
        PlayerTurn = abilityArgs[0]
        global AbilityName
        AbilityName = abilityArgs[1]
        global AbilityTypes
        AbilityTypes = abilityArgs[2]
        global AbilityDuration
        AbilityDuration = abilityArgs[3]
        global Actions
        Actions = abilityArgs[4]
        global PlayerTarget
        PlayerTarget = abilityArgs[5]
        global Targets
        Targets = abilityArgs[6]
        global Target
        Target = abilityArgs[7]
        global TargetData
        TargetData = abilityArgs[8]
        global Actor
        Actor = abilityArgs[9]
        global ActorData
        ActorData = abilityArgs[10]
        global SpellAtk
        SpellAtk = abilityArgs[11]
        global SaveType
        SaveType = abilityArgs[12]
        global SaveDC
        SaveDC = abilityArgs[13]
        global SaveDiff
        SaveDiff = abilityArgs[14]
        global BaseLevel
        BaseLevel = abilityArgs[15]
        global SpellLevel
        SpellLevel = abilityArgs[16]
        global Half
        Half = abilityArgs[17]
        global Crit
        Crit = abilityArgs[18]
        global UncannyDodge
        UncannyDodge = abilityArgs[19]
        global Concentration
        Concentration = abilityArgs[20]
        global SavedDamageRolls
        SavedDamageRolls = abilityArgs[21]
        global AbilityEffects
        AbilityEffects = abilityArgs[22]
        return True
    else:
        DnDUtil.printError("Global constant NUM_ABILITY_ARGS does not match the number of ability arguments passed to Spells.useAbility")
        print("Expected", NUM_ABILITY_ARGS, "but received", len(abilityArgs))
        return False

def saveGlobals(abilityArgs):

    if (len(abilityArgs) == NUM_ABILITY_ARGS):
        abilityArgs[0] = PlayerTurn
        abilityArgs[1] = AbilityName
        abilityArgs[2] = AbilityTypes
        abilityArgs[3] = AbilityDuration
        abilityArgs[4] = Actions
        abilityArgs[5] = PlayerTarget
        abilityArgs[6] = Targets
        abilityArgs[7] = Target
        abilityArgs[8] = TargetData
        abilityArgs[9] = Actor
        abilityArgs[10] = ActorData
        abilityArgs[11] = SpellAtk
        abilityArgs[12] = SaveType
        abilityArgs[13] = SaveDC
        abilityArgs[14] = SaveDiff
        abilityArgs[15] = BaseLevel
        abilityArgs[16] = SpellLevel
        abilityArgs[17] = Half
        abilityArgs[18] = Crit
        abilityArgs[19] = UncannyDodge
        abilityArgs[20] = Concentration
        abilityArgs[21] = SavedDamageRolls
        abilityArgs[22] = AbilityEffects
    else:
        DnDUtil.printError("Global constant NUM_ABILITY_ARGS does not match the number of ability aruments being passed out of Spells.useAbility")
        print("Expected", NUM_ABILITY_ARGS, "but received", len(abilityArgs))

def useAbility(abilityArgs):

    scriptActions = []
    # don't run the script if there was an error loading the global ability arguments
    if (loadGlobals(abilityArgs)):
        globalDict = globals()
        if (AbilityName in globalDict):
            globalDict[AbilityName]()
            saveGlobals(abilityArgs)
        else:
            DnDUtil.printError("Attempted to run a custom script for ability "+AbilityName+" but no function with this name was found")

# below are the ability scripts themselves
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# deal 1d6 radiant damage if the target is undead
def lightBringer():

    if ('undead' in TargetData['Type']):
        print(Actor, "deals bonus radiant damage from Lightbringer since", Target, "is undead!")
        Actions.append(['damage','1d6','radiant'])

# set the target's AC to 16 if it is lower than 16
def barkskin():
    
    diff = 16 - TargetData['AC']
    if (diff > 0):
        print(Target+"'s AC will be buffed by", diff, "to increase it to 16")
        Actions.append(['cc','barkskin'])
        Actions.append(['buff','ac',str(diff)])
    else:
        print(Target, "already has an AC of at least 16, so this spell will have no effect")

# give the target disadvantage on attacks for a turn if it is undead 
def chilltouch():
    
    if ('undead' in TargetData['Type']):
        print(Target, "has disadvantage on attacks against", Actor, "for a turn because it is undead")
        Actions.append(['dis',Actor])

# choose the damage type for the orb then scale the damage if needed
def chromaticorb():
    
    # only ask for the damage type if we have no saved damage since don't want to ask again if this choice has already been made
    if (not(SavedDamageRolls)):
        options = ['acid','cold','fire','lightning','poison','thunder']
        choice = DnDUtil.chooseOption('Choose a damage type for the orb',options)
        damageType = options[choice-1]
        print("The orb will deal", damageType, "damage")
    else:
        damageType = next(iter(SavedDamageRolls.keys()))

    Actions.append(['damage',str(3+SpellLevel-BaseLevel)+'d8',damageType])

# roll 6d10+lvl*2d10 and blind the target if its hp is lower than the result, then keep track of the remaining amount and apply it to the rest of the targets
def colorspray():

    if ('colorspray' in SavedDamageRolls):
        blindPoints = SavedDamageRolls['colorspray']
    else:
        blindPointCalculation = str(6+2*(SpellLevel-BaseLevel))+'d10'
        if (PlayerTurn):
            blindPoints = DnDUtil.getInt(getInput('Roll for blind points ('+blindPointCalculation+'): '))
        else:
            blindPoints = DnDUtil.calculate(blindPointCalculation)

    if (PlayerTarget):
        hp = DnDUtil.getInt(getInput('What is '+Target+'\'s current hp? '))
    else:
        hp = TargetData['HP']

    if (blindPoints >= hp):
        print(Target, "will be blinded by colorspray")
        Actions.append(['cc','blind','actorend'])
        SavedDamageRolls['colorspray'] = blindPoints - hp
    else:
        print("There are not enough blind points remaining to affect", Target)
        SavedDamageRolls['colorspray'] = blindPoints

# get the damage type of the weapon used
def conjurebarrage():

    if (SavedDamageRolls):
        damageType = next(iter(SavedDamageRolls.keys()))
    else:
        options = ['slashing','piercing','bludgeoning']
        choice = DnDUtil.chooseOption('Choose the damage type of the weapon used',options)
        damageType = options[choice-1]
        
    Actions.append(['damage','3d8',damageType])

# get the damage type of the weapon used
def conjurevolley():

    if (SavedDamageRolls):
        damageType = next(iter(SavedDamageRolls.keys()))
    else:
        options = ['slashing','piercing','bludgeoning']
        choice = DnDUtil.chooseOption('Choose the damage type of the weapon used',options)
        damageType = options[choice-1]
        
    Actions.append(['damage','8d8',damageType])

# remove contagion's poison effect if it was failed 3 times and choose the disease to inflict and apply it
def contagiont():

    contagionEffect = []
    for effect in ActorData['Effects']:
        if (effect[0] == Target and effect[1] == 'cc' and effect[2] == 'contagion' and effect[3] and effect[3][0][1] == 'cc' and effect[3][0][2] == 'poison'):
            contagionEffect = effect
            break

    if (contagionEffect):
        contagionStatusEffect = []
        poisonStatusEffect = []
        for statusEffect in TargetData['Status']:
            if (statusEffect[0] == 'contagion' and statusEffect[1] == Actor and statusEffect[6] >= 3):
                contagionStatusEffect = statusEffect
            elif (statusEffect[0] == 'poison' and statusEffect[1] == Actor and statusEffect[2] == ''):
                poisonStatusEffect = statusEffect
        if (contagionStatusEffect and poisonStatusEffect):
            ActorData['Effects'].remove(contagionEffect)
            TargetData['Status'].remove(contagionStatusEffect)
            TargetData['Status'].remove(poisonStatusEffect)
            print(Target, "is no longer poisoned from contagion")
        else:
            DnDUtil.printWarning("Script contagiont: Expected poison and contagion with 3 fails status effects in "+Target+", but one or both were not found")
            return
    else:
        DnDUtil.printWarning("Script contagiont: Expected poison effect in "+Actor+" targeting "+Target+", but none was found")
        return

    global AbilityName
    choice = DnDUtil.chooseOption('Choose an effect for contagion',['blind, dis on wis saves and checks','dis on str saves, checks, and attacks that use str','vulnerability to all damage, dis on cha checks','confusion, dis on int checks and saves','dis on dex saves, checks, and attacks that use dex','stunned for a turn upon taking damage, dis on con saves and checks'])
    if (choice == 1):
        AbilityName = 'blinding sickness'
        Actions.append(['cc','blind'])
        Actions.append(['dis','wis','wissaves'])
    elif (choice == 2):
        AbilityName = 'filth fever'
        Actions.append(['dis','str','strsaves','strattacks'])
    elif (choice == 3):
        AbilityName = 'flesh rot'
        Actions.append(['dis','cha'])
        Actions.append(['vulnerability','all'])
    elif (choice == 4):
        AbilityName = 'mindfire'
        Actions.append(['msg','target acts as though affected by the confusion spell!'])
        Actions.append(['dis','int','intsaves'])
    elif (choice == 5):
        AbilityName = 'seizure'
        Actions.append(['dis','dex','dexsaves','dexattacks'])
    else:
        AbilityName = 'slimy doom'
        Actions.append(['dis','con','consaves'])
        Actions.append(['msg','Whenever target takes damage, it is stunned until the end of its next turn!'])

# choose a damage type
def destructivewave():
    
    if ('radiant' in SavedDamageRolls):
        damageType = 'radiant'
    elif ('necrotic' in SavedDamageRolls):
        damageType = 'necrotic'
    else:
        options = ['radiant','necrotic']
        choice = DnDUtil.chooseOption('Choose a damage type',options)
        damageType = options[choice-1]

    Actions.append(['damage','5d6',damageType])

# banish the target if it is a celestial, elemental, fey, or fiend. Otherwise, do the appropriate effect based on hp
def divineword():

    if (DnDUtil.haveCommonItem(TargetData['Type'],['celestial','elemental','fey','fiend'])):
        Actions.append(['msg','target is forced back to its plane of origin!'])
    else:
        if (PlayerTarget):
            hp = DnDUtil.getInt(getInput('What is '+Target+'\'s current hp? '))
        else:
            hp = TargetData['HP']

        if (hp <= 20):
            Actions.append(['kill'])
        elif (hp <= 30):
            Actions.append(['cc','blind'])
            Actions.append(['cc','stun'])
            Actions.append(['cc','deaf'])
        elif (hp <= 40):
            Actions.append(['cc','blind','100'])
            Actions.append(['cc','deaf','100'])
        elif (hp <= 50):
            Actions.append(['cc','deaf','10'])

# choose an effect and apply it
def eyebite():
    
    choice = DnDUtil.chooseOption('Choose an effect for eyebite',['sleep','fear until 60ft away and out of LoS','dis on attacks and checks until making a wis save'])
    if (choice == 1):
        Actions.append(['cc','sleep'])
    elif (choice == 2):
        Actions.append(['cc','fear'])
        Actions.append(['msg','target spend its actions dashing away from actor until it is 60ft away and out of line of sight of actor. Then this effect ends'])
    else:
        Actions.append(['ccsave','eyebite','end'])
        Actions.append(['dis','str','dex','con','int','wis','cha','attacks'])

# choose a shield type and apply the appropriate effects
def fireshield():
    
    choice = DnDUtil.chooseOption('Choose a shield type',['warm shield - cold resist and fire thorns','cold shield - fire resist and cold thorns'])
    if (choice == 1):
        Actions.append(['cc','warm shield'])
        Actions.append(['resist','cold'])
        Actions.append(['misc','thorns','2d8','fire'])
    else:
        Actions.append(['cc','cold shield'])
        Actions.append(['resist','fire'])
        Actions.append(['misc','thorns','2d8','cold'])

# choose which damage type should be scaled
def flamestrike():

    if (not(SavedDamageRolls)):
        baseDamage = '4d6'
        scaledDamage = str(4+SpellLevel-BaseLevel)+'d6'
        choice = DnDUtil.chooseOption('Choose which damage type to scale',['fire','radiant'])
        if (choice == 1):
            fireDamage = scaledDamage
            radiantDamage = baseDamage
        else:
            fireDamage = baseDamage
            radiantDamage = scaledDamage
    else:
        fireDamage = '0'
        radiantDamage = '0'

    Actions.append(['damage',fireDamage,'fire'])
    Actions.append(['damage',radiantDamage,'radiant'])

# ensure that the target does not die from the 14d6 necrotic damage
def harm():

    if ('necrotic' in SavedDamageRolls):
        damage = SavedDamageRolls['necrotic']
    else:
        damage = DnDUtil.calculate('14d6')
        SavedDamageRolls['necrotic'] = damage

    # if the save was failed, max hp should be reduced as well
    if (not(Half)):
        Actions.append(['idamage','14d6','necrotc'])
    else:
        Actions.append(['damage','14d6','necrotic'])
    # ensure that this damage doesn't kill the target
    if (PlayerTarget):
        Actions.append(['msg','This spell cannot put target below 1 hp!'])
    else:
        # calculate how much damage this spell would deal to the target
        if (ActorUtil.isImmuneToType(TargetData,['necrotic'])):
            damage = 0
        else:
            if (ActorUtil.isVulnerableToType(TargetData,['necrotic'])):
                damage *= 2
            if (ActorUtil.hasResistFromType(TargetData,['necrotic'])):
                damage /= 2
            if (Half):
                damage /= 2
        if (damage >= TargetData['HP']):
            TargetData['HP'] = damage + 1
            if (not(Half) and damage >= TargetData['MaxHP']):
                TargetData['MaxHP'] = damage + 1

# ask if the target is able to drop the heated metal to apply attack and check disadvantage for a turn when appropriate
def heatmetal():

    global AbilityDuration

    if (DnDUtil.getAnswer('Is '+Target+' able to drop the heated object') == 'y'):
        AbilityDuration = 0
        Actions.append(['msg','target drops the heated object!'])
    else:
        Actions.append(['dis','attacks','checks'])

# buff the target's AC to 13 + dex mod
def magearmor():

    global AbilityDuration
    # we need the target's dex mod in order to figure out its new AC with mage armor
    # to determine that, we use the initiative value if it is 5 or less. Otherwise, ask the dm for the dex mod
    initValue = TargetData['Init']
    if (initValue <= 5):
        newAC = 13 + initValue
    else:
        dexMod = DnDUtil.getInt(getInput('What is '+Target+'\'s dex mod? '))
        newAC = 13 + dexMod
    
    diff = newAC - TargetData['AC']
    if (diff > 0):
        print(Target+"'s AC will be buffed by", diff, "to increase it to", newAC)
        AbilityDuration = -1
        Actions.append(['buff','ac',str(diff)])
    else:
        print(Target, "already has an AC of at least", newAC, "so this spell will have no effect")

# get the target's hp and kill if its hp is at or below 100
def powerwordkill():

    if (PlayerTarget):
        hp = DnDUtil.getInt(getInput('What is '+Target+'\'s current hp? '))
    else:
        hp = TargetData['HP']

    if (hp > 100):
        print("This spell will have no effect since", Target, "is above 100 hp!")
    else:
        Actions.append(['kill'])

# get the target's hp and stun if its hp is at or below 150
def powerwordstun():

    if (PlayerTarget):
        hp = DnDUtil.getInt(getInput('What is '+Target+'\'s current hp? '))
    else:
        hp = TargetData['HP']

    if (hp > 150):
        print("This spell will have no effect since", Target, "is above 150 hp!")
    else:
        Actions.append(['ccsave','stun','end'])

# roll for the ray or rays hitting the target and apply the appropriate effect
def prismaticspray():

    global SaveType
    
    # keep track of the rays that are rolled to hit, we use a list since up to 2 rays can hit a single target
    rayIDs = []

    if (PlayerTurn):
        rayID = 0
        while (rayID < 1 or rayID > 8):
            rayID = DnDUtil.getInt(getInput('Roll for which ray hits '+Target+' (1d8): '))
        if (rayID != 8):
            rayIDs.append(rayID)
        else:
            print(Target, "will be hit by 2 rays!")
            rayID1 = 0
            rayID2 = 0
            while (rayID1 < 1 or rayID1 > 7):
                rayID1 = DnDUtil.getInt(getInput('Roll for the first ray, rerolling any 8s (1d8): '))
            while (rayID2 < 1 or rayID2 > 7 or rayID2 == rayID1):
                rayID2 = DnDUtil.getInt(getInput('Roll for the second ray, rerolling any 8s and avoiding a duplicate ray (1d8): '))
            rayIDs.append(rayID1)
            rayIDs.append(rayID2)
    else:
        rayID = random.randint(1,8)
        print(Actor, "rolls a", rayID, "for which ray hits", Target)
        if (rayID != 8):
            rayIDs.append(rayID)
        else:
            print(Target, "will be hit by 2 rays!")
            rayID1 = random.randint(1,7)
            rayID2 = random.randint(1,7)
            while (rayID2 == rayID1):
                rayID2 = random.randint(1,7)
            print(Actor, "rolls a", rayID1, "for the first ray and", rayID2, "for the second ray")
            rayIDs.append(rayID1)
            rayIDs.append(rayID2)

    for rayID in rayIDs:
        if (rayID < 6):
            if (rayID == 1):
                print("This ray is red")
                damageType = 'fire'
            elif (rayID == 2):
                print("This ray is orange")
                damageType = 'acid'
            elif (rayID == 3):
                print("This ray is yellow")
                damageType = 'lightning'
            elif (rayID == 4):
                print("This ray is green")
                damageType = 'poison'
            else:
                print("This ray is blue")
                damageType = 'cold'
            Actions.append(['damage','10d6',damageType])
        elif (rayID == 6):
            print("This ray is indigo")
            if (Half):
                print(Target, "resists the ray!")
            else:
                SaveType = 'con'
                Actions.append(['ccsave3','prestrain','end'])
        else:
            print("This ray is violet")
            if (Half):
                print(Target, "resists the ray!")
            else:
                SaveType = 'wis'
                Actions.append(['ccsave','blind','end','1'])
                Actions.append(['msg','If target fails the next save, target is transported to another plane!'])

# choose a damage type to grant resistance from
def protectionfromenergy():

    if (SavedDamageRolls):
        resistType = SavedDamageRolls['PfE']
    else:
        options = ['acid','cold','fire','lightning','thunder']
        choice = DnDUtil.chooseOption('Choose a damage type to grant resistance from',options)
        resistType = options[choice-1]
        SavedDamageRolls['PfE'] = resistType

    Actions.append(['resist',resistType])

# roll 5d8+lvl*2d8 and sleep the target if its hp is lower than the result and keep track of the remaining amount and apply it to the rest of the targets
def sleep():

    if ('sleep' in SavedDamageRolls):
        sleepPoints = SavedDamageRolls['sleep']
    else:
        sleepPointCalculation = str(5+2*(SpellLevel-BaseLevel))+'d8'
        if (PlayerTurn):
            sleepPoints = DnDUtil.getInt(getInput('Roll for sleep points ('+sleepPointCalculation+'): '))
        else:
            sleepPoints = DnDUtil.calculate(sleepPointCalculation)

    if (PlayerTarget):
        hp = DnDUtil.getInt(getInput('What is '+Target+'\'s current hp? '))
    else:
        hp = TargetData['HP']

    if (sleepPoints >= hp):
        print(Target, "will fall asleep for a minute")
        Actions.append(['cc','sleep','10'])
        SavedDamageRolls['sleep'] = sleepPoints - hp
    else:
        print("There are not enough sleep points remaining to affect", Target)
        SavedDamageRolls['sleep'] = sleepPoints

# paralyze the target for a turn if they failed the save by 5 or more
def paralyzingFear():
    
    if (SaveDiff >= 5):
        print(Target, "will also be paralyzed due to failing the save by 5 or more!")
        Actions.append(['cc','paralysis'])

# also paralyze the target if they failed the save by 5 or more
def paralyzingPoison():
    
    if (SaveDiff >= 5):
        print(Target, "will be paralyzed due to failing the save by 5 or more!")
        Actions.append(['ccsave','paralysis','end','10'])

# sleep the target equal to the poison duration if they failed the save by 5 or more
def sleepPoison():
    
    if (SaveDiff >= 5):
        poisoned = False
        for statusEffect in TargetData['Status']:
            if (statusEffect[0] == 'poison' and statusEffect[1] == Actor):
                poisoned = True
                break
        if (poisoned):
            print(Target, "will also fall asleep while poisoned due to failing the save by 5 or more!")
            Actions.append(['cc','sleep'])

# instantly petrify the target if they failed the save by 5 or more
def pgaze():
    
    if (SaveDiff >= 5):
        print(Target, "is instantly petrified due to failing the save by 5 or more!")
        Actions.append(['cc','petrification'])
    else:
        Actions.append(['ccsave','prestrain','end'])

# instantly kill the target if the target failed the save by 5 or more; otherwise, deal 3d10 psychic damage
def deathgaze():
    
    if (SaveDiff >= 5):
        print(Target, "is reduced to 0 hp due to failing the save by 5 or more!")
        Actions.append(['kill'])
    else:
        Actions.append(['damage','3d10','psychic'])

# deal 64 necrotic damage if the target failed the save by 5 or more; otherwise, deal 8d8 necrotic damage
def deathray2():
    
    if (SaveDiff >= 5):
        print(Target, "takes max damage due to failing the save by 5 or more!")
        Actions.append(['damage','64','necrotic'])
    else:
        Actions.append(['damage','8d8','necrotic'])

# prone the target and deal damage if the target failed the save by 5 or more; otherwise, push the target
def shieldCharge():
    
    if (SaveDiff >= 5):
        print(Target, "is knocked prone and takes additional damage due to failing the save by 5 or more!")
        if (TargetData['Prone']):
            print(Target, "takes extra damage since he/she was already prone!")
            Actions.append(['damage','6d6+8','bludgeoning','nonmagic'])
        else:
            Actions.append(['prone'])
            Actions.append(['damage','3d6+8','bludgeoning','nonmagic'])

    Actions.append(['msg','target is pushed along with actor for the remainder of the move!'])

# stun the target if they failed the save by 5 or more
def lightningstorm2():
    
    if (SaveDiff >= 5):
        print(Target, "is also stunned due to failing the save by 5 or more!")
        Actions.append(['cc','stun','targetend'])

# prone the target if they failed the save by 5 or more
def spewdebris():
    
    if (SaveDiff >= 5):
        print(Target, "is also knocked prone due to failing the save by 5 or more!")
        Actions.append(['prone'])

# deal 8d8 necrotic damage, with plants taking max damage
def blight():

    damageCalculation = str(8+SpellLevel-BaseLevel)+'d8'

    if ('plant' in TargetData['Type']):
        print(Target, "will take max damage since it is a plant!")
        damage = DnDUtil.maxCalculate(damageCalculation)
        Actions.append(['damage',str(damage),'necrotic'])
    else:
        Actions.append(['damage',damageCalculation,'necrotic'])

# give advantage on the next attack against the target on the next turn
def truestrike():

    global Target, TargetData, PlayerTarget
    Actions.append(['adv','next'+Target])
    Target = Actor
    TargetData = ActorData
    PlayerTarget = PlayerTurn

# choose a curse to inflict and apply the appropriate effect
def bestowcurse():

    global Concentration
    
    # when cast at 5th level or higher, bestow curse does not require concentration
    if (SpellLevel >= 5):
        Concentration = False

    if (SpellLevel == 3):
        Actions.append(['cc','curse','10'])
    else:
        Actions.append(['cc','curse',str((SpellLevel-BaseLevel)*100)])

    choice = DnDUtil.chooseOption('Choose a curse to inflict',['Disadvantage on all checks and saves make with a chosen ability score','Disadvantage on attacks made against you',Target+' must make a wisdom saving throw DC '+str(SaveDC)+' at the start of each turn or lose its action','Your attacks and spells deal an extra 1d8 necrotic damage to '+Target])
    
    if (choice == 1):
        options = ['str','dex','con','int','wis','cha']
        choice = DnDUtil.chooseOption('Choose which ability to grant disadvantage',options)
        ability = options[choice-1]
        Actions.append(['dis',ability,ability+'saves'])
    elif (choice == 2):
        Actions.append(['dis',Actor])
    elif (choice == 3):
        Actions.append(['msg','target must make a wis save DC '+str(SaveDC)+' at the start of each turn or lose its action'])
    else:
        Actions.append(['msg','actor\'s attacks and spells deal an extra 1d8 necrotic damage to target'])

# scale the damage based on the spell slot used and add 1d8 if the target is fiend or undead
def dsmite():
    
    divineSmiteLevel = -1
    while (divineSmiteLevel < 1):
        divineSmiteLevel = DnDUtil.getInt(getInput('What level spell slot was used for divine smite? '))
    if (divineSmiteLevel > 4):
        divineSmiteLevel = 4
    numDamageDice = divineSmiteLevel + 1
    if (DnDUtil.haveCommonItem(TargetData['Type'],['undead','fiend'])):
        print("Divine smite will deal an extra 1d8 damage since", Target, "is undead/fiend!")
        numDamageDice += 1
    if ('idsmite' in ActorData['Misc']):
        print("Divine smite will deal an extra 1d8 damage from improved divine smite!")
        numDamageDice += 1

    Actions.append(['damage',str(numDamageDice)+'d8','radiant'])

# change the save type to str since that is the check we make to break free
def web():
    
    global SaveType
    SaveType = 'str'

# set the save dc to the correct value for breaking free using an action
def maze():
    
    global SaveDC
    SaveDC = 20

# change the save type to str/dex since either check can be used to break free
def evardsblacktentacles():
    
    global SaveType
    SaveType = 'str/dex'

# change the save type to str/dex since either check can be used to break free
def bonesoftheearth():
    
    global SaveType
    SaveType = 'str/dex'

# give advantage to large or larger creatures
def ensnaringstrikeOH():

    if (TargetData['SizeMod'] >= 1):
        TargetData['Advantages'].append('ensnaringstrikeOH2')

# remove the advantage we may have given for this ability if this is at least a large creature
def ensnaringstrikeOH2():

    if ('ensnaringstrikeOH2' in TargetData['Advantages']):
        TargetData['Advantages'].remove('ensnaringstrikeOH2')

# choose whether to make a str or dex save
def natureswrath():

    strSaveValue = TargetData['StrSave']
    if ('strsaves' in TargetData['Advantages']):
        strSaveValue += 3.3
    if ('strsaves' in TargetData['Disadvantages']):
        strSaveValue -= 3.3
    dexSaveValue = TargetData['DexSave']
    if ('dexsaves' in TargetData['Advantages']):
        dexSaveValue += 3.3
    if ('dexsaves' in TargetData['Disadvantages'] or ActorUtil.hasStatus(TargetData,['restrain','prestrain'])):
        dexSaveValue -= 3.3

    if (strSaveValue >= dexSaveValue):
        saveChoice = 'str'
    else:
        saveChoice = 'dex'

    print(Target, "will make a", saveChoice, "save since it has a higher value")
    Actions.append(['use',AbilityName+saveChoice])

# if the dex save was failed, re-evaluate to see if this is still the best option since it will now be made with disadvantage
def natureswrathdex():

    global SaveType

    strSaveValue = TargetData['StrSave']
    if ('strsaves' in TargetData['Advantages']):
        strSaveValue += 3.3
    if ('strsaves' in TargetData['Disadvantages']):
        strSaveValue -= 3.3
    # subtract 3.3 from the value immediately since we already know we have disadvantage from failing the save
    dexSaveValue = TargetData['DexSave'] - 3.3
    if ('dexsaves' in TargetData['Advantages']):
        dexSaveValue += 3.3

    if (strSaveValue >= dexSaveValue):
        print(Target, "will instead use str saves to escape each turn since dex saves are now at disadvantage")
        SaveType = 'str'

# randomly choose 3 unique rays and use them
def eyerays():

    rayNames = ['charmray','pray','fearray','slowray','enervationray','telekineticray','sleepray','petrificationray','disintegrationray2','deathray']
    print("The rays are", end=' ')
    for i in range(0,3):
        randomRay = rayNames.pop(random.randint(0,len(rayNames)-1))
        if (i != 2):
            print(randomRay+',', end=' ')
        else:
            print(randomRay)
        Actions.append(['useon',randomRay])

# randomly choose 1 ray and use it, mostly copied from eyerays script
def eyeray():

    rayNames = ['charmray','pray','fearray','slowray','enervationray','telekineticray','sleepray','petrificationray','disintegrationray2','deathray']
    randomRay = rayNames[random.randint(0,len(rayNames)-1)]
    print("The ray is", randomRay)
    Actions.append(['useon',randomRay])

# randomly choose 3 unique rays and use them
def gauthEyeRays():

    rayNames = ['devourmagicray','enervationray2','pushingray','fireray','pray','sleepray']
    print("The rays are:", end=' ')
    for i in range(0,3):
        randomRay = rayNames.pop(random.randint(0,len(rayNames)-1))
        if (i != 2):
            print(randomRay+',', end=' ')
        else:
            print(randomRay)
        Actions.append(['useon',randomRay])

# randomly choose 2 unique rays and use them
def gazerEyeRays():

    rayNames = ['dazingray','fearray2','frostray','telekineticray2']
    print("The rays are", end=' ')
    for i in range(0,2):
        randomRay = rayNames.pop(random.randint(0,len(rayNames)-1))
        if (i == 0):
            print(randomRay, "and", end=' ')
        else:
            print(randomRay)
        Actions.append(['useon',randomRay])

# randomly choose 3 unique rays
def mindwitnessEyeRays():

    rayNames = ['aversionray','fearray','psychicray','slowray','stunray','telekineticray']
    print("The rays are:", end=' ')
    for i in range(0,3):
        randomRay = rayNames.pop(random.randint(0,len(rayNames)-1))
        if (i != 2):
            print(randomRay+',', end=' ')
        else:
            print(randomRay)
        Actions.append(['useon',randomRay])

# choose which damage type for the weapon
def elementalweapon():

    global SpellLevel
    # this spell does not scale to level 9
    if (SpellLevel == 9):
        SpellLevel = 8
    damageTypes = ['acid','cold','fire','lightning','thunder']
    choice = DnDUtil.chooseOption('Choose a damage type',damageTypes)
    damageType = damageTypes[choice-1]
    Actions.append(['onhit','elementalweaponOH'+damageType])

# set duration based on spell level
def dominateperson():

    global AbilityDuration
    if (SpellLevel == BaseLevel):
        AbilityDuration = 10
    else:
        AbilityDuration = -1

# send a message to revert a shapechanger's form if the save was failed
def moonbeam():

    if ('shapechanger' in TargetData['Type'] and not(Half)):
        Actions.append(['msg','target must revert to its original form!'])

# if target is at or below 100 hp, use the next part of the ability
def slayingLongbow():

    if (not(PlayerTarget) and TargetData['HP'] <= 100 or PlayerTarget and DnDUtil.getAnswer('Is '+Target+' at or below 100 hp') == 'y'):
        Actions.append(['use','slayinglongbow2'])

# choose a damage type
def bolt():

    options = ['acid', 'cold', 'fire', 'force', 'lightning', 'radiant', 'thunder']
    choice = DnDUtil.chooseOption('Choose a damage type',options)
    damageType = options[choice-1]
    Actions.append(['damage','7d6',damageType])

# choose an ability check to give disadvantage
def hex():

    options = ['str', 'dex', 'con', 'int', 'wis', 'cha']
    choice = DnDUtil.chooseOption('Choose which ability check to give disadvantage',options)
    checkType = options[choice-1]
    Actions.append(['dis',checkType])

# get the spell level of the spell that was absorbed and deal 1d6 force damage per level of that spell
def antimagicshellburst():

    # only ask for the spell level on the first target since we will use this same damage we rolled on all future targets
    if (not(SavedDamageRolls)):
        spellLevel = DnDUtil.getInt(getInput('What was the spell level of the absorbed spell? '))
        while (spellLevel < 0 or spellLevel > 9):
            print("Invalid input - spell level must be between 0 and 9!")
            spellLevel = DnDUtil.getInt(getInput('What was the spell level of the absorbed spell? '))
    else:
        spellLevel = 0

    Actions.append(['damage',str(spellLevel)+'d6','force'])

# choose or randomize the guard drake variant
def guarddrakevariant():

    options = ['black', 'blue', 'green', 'red', 'white', 'random']
    choice = DnDUtil.chooseOption('Choose the guard drake\'s color',options,True)
    if (choice == len(options)):
        choice = random.randint(1,len(options)-1)
        print("The chosen color is", options[choice-1])

    if (choice < len(options)):
        color = options[choice-1]
        if (color == 'black'):
            Actions.append(['move','swim','30'])
            Actions.append(['resist','acid'])
        elif (color == 'blue'):
            Actions.append(['move','burrow','20'])
            Actions.append(['resist','lightning'])
        elif (color == 'green'):
            Actions.append(['move','swim','30'])
            Actions.append(['resist','poison'])
        elif (color == 'red'):
            Actions.append(['move','climb','30'])
            Actions.append(['resist','fire'])
        elif (color == 'white'):
            Actions.append(['move','burrow','20'])
            Actions.append(['move','climb','30'])
            Actions.append(['resist','cold'])

# choose or randomize the kobold dragonshield variant
def kobolddragonshieldvariant():

    options = ['black', 'blue', 'green', 'red', 'white', 'random']
    choice = DnDUtil.chooseOption('Choose the kobold dragonshield\'s color',options)
    if (choice == len(options)):
        choice = random.randint(1,len(options)-1)
        print("The chosen color is", options[choice-1])

    color = options[choice-1]
    if (color == 'black'):
        Actions.append(['resist','acid'])
    elif (color == 'blue'):
        Actions.append(['resist','lightning'])
    elif (color == 'green'):
        Actions.append(['resist','poison'])
    elif (color == 'red'):
        Actions.append(['resist','fire'])
    elif (color == 'white'):
        Actions.append(['resist','cold']) 

# choose or randomize the sea spawn variant, remembering which variant was chosen 
def seaspawnvariant():

    options = ['shark jaw', 'urchin quills', 'squid tentacle', 'random']
    if (AbilityName in SavedDamageRolls):
        choice = SavedDamageRolls[AbilityName]
    else:
        choice = DnDUtil.chooseOption('Choose the sea spawn\'s mutation',options)
    if (choice == len(options)):
        choice = random.randint(1,len(options)-1)
        print("The chosen mutation is", options[choice-1])

    if (choice == 1):
        weaponBaseDamage = '1d4'
        weaponBonusDamage = 2
        weaponTypes = ['piercing','nonmagic']
        weaponOnHitAbility = ''
    elif (choice == 2):
        weaponBaseDamage = '1d6'
        weaponBonusDamage = 0
        weaponTypes = ['poison']
        weaponOnHitAbility = 'con,12,negates:ccsave,poison,end,10'
        ActorData['Misc']['ohm02'] = 'poison'
    else:
        weaponBaseDamage = '1d6'
        weaponBonusDamage = 2
        weaponTypes = ['bludgeoning','nonmagic']
        weaponOnHitAbility = 'grapple,12'

    ActorData['Damage'][0][0][2] = weaponBaseDamage
    ActorData['DmgBonus'][0][0][2] = weaponBonusDamage
    ActorData['WeaponTypes'][0][0][2] = weaponTypes
    if (weaponOnHitAbility):
        ActorData['OnHitAbilities'][0][0][2] = ImportUtil.loadAbilityData('',weaponOnHitAbility.split(':'),False)

    AbilityEffects.append([Target,'script',AbilityName,choice])

# determine how many rot grubs infest the target and set the appropriate effect and message, stacking the dot if needed
def rotGrubSwarmBite():

    global AbilityDuration
    numRotGrubs = DnDUtil.calculate('1d4')
    found = False
    for statusEffect in TargetData['Status']:
        if (statusEffect[0] == 'dot' and statusEffect[2] == [] and statusEffect[3][-2:] == 'd6' and statusEffect[5] == ['piercing','nonmagic']):
            print(Target, "has been infested by an additional", numRotGrubs, "rot grubs!")
            statusEffect[3] = str(int(statusEffect[3].split('d')[0])+numRotGrubs) + 'd6'
            found = True
            break

    if (not(found)):
        AbilityDuration = -1
        Actions.append(['dot',str(numRotGrubs)+'d6','target','piercing','nonmagic'])
        Actions.append(['msg','target is infested by '+str(numRotGrubs)+' rot grubs! If fire is not applied to target\'s bite wound by the end of his/her next turn, the rot grubs will burrow into the skin and continue to deal damage until target dies! (can be removed by disease cures)'])

# allow the dot to stack up to 10d6
def burrowingworm():

    global AbilityDuration
    found = False
    for statusEffect in TargetData['Status']:
        if (statusEffect[0] == 'dot' and statusEffect[2] == [] and statusEffect[3][-2:] == 'd6' and statusEffect[5] == ['necrotic']):
            dotDamage = int(statusEffect[3].split('d')[0])
            if (dotDamage == 10):
                print(Target, "is already taking the maximum dot damage, so this worm will not deal additional damage!")
            else:
                statusEffect[3] = str(dotDamage+2) + 'd6'
                print(Target, "has been infested by another burrowing worm, increasing the damage taken each turn!")
            found = True
            break

    if (not(found)):
        AbilityDuration = -1
        Actions.append(['dot','2d6','target','necrotic'])
        Actions.append(['msg','The worm burrows under target\'s skin and can no longer be removed except by effects that cure disease or curse!'])

# add damage to the spell based on how many turns have passed since it was cast
def delayedblastfireball():

    passedTurns = -1
    while (passedTurns < 0):
        passedTurns = DnDUtil.getInt(getInput('How many times has '+Actor+'\'s turn ended since this spell was cast? '))
    Actions.append(['damage',str(12+SpellLevel-BaseLevel+passedTurns)+'d6+','fire'])

# choose a buff to grant the transmuter and remove any previous buff granted by this ability
def transmutersstone():

    # determine the current buff from this ability, if any, and remove it
    for effect in ActorData['Effects']:
        if (effect[0] == Target and effect[1] == 'cc' and effect[2] == 'transmutersstone' and effect[-1] == -1):
            if (effect[3]):
                transmuteEffect = effect[3][0]
                if (transmuteEffect[1] == 'move' and transmuteEffect[2]['Ground'] == TargetData['Move']['Ground'] - 10):
                    TargetData['Move'] = transmuteEffect[2]
                    print(Target, "no longer has increased movement speed from transmuter's stone")
                elif (transmuteEffect[1] == 'buff' and transmuteEffect[2] == 'consaves' and transmuteEffect[3] == 3):
                    TargetData['ConSave'] -= 3
                    print(Target, "no longer has a +3 to con saves from transmuter's stone")
                elif (transmuteEffect[1] == 'resist' and transmuteEffect[2] in ['acid','cold','fire','lightning','thunder']):
                    if (transmuteEffect[2] in TargetData['Resistances']):
                        TargetData['Resistances'].remove(transmuteEffect[2])
                    else:
                        DnDUtil.printWarning("Attempted to remove resistance "+transmuteEffect[2]+" but resistance not found")
                    print(Target, "no longer has", transmuteEffect[2], "resistance from transmuter's stone")
                for statusEffect in TargetData['Status']:
                    if (statusEffect[0] == 'transmutersstone' and statusEffect[1] == Actor):
                        TargetData['Status'].remove(statusEffect)
                        break
            ActorData['Effects'].remove(effect)
            break

    choice = DnDUtil.chooseOption('Choose an effect for transmuter\'s stone',['Darkvision (60ft)','+10ft Movement Speed','+3 Con Saves','Acid Resistance','Cold Resistance','Fire Resistance','Lightning Resistance','Thunder Resistance','Random'])
    if (choice == 9):
        choice = random.randint(1,8)

    if (choice == 1):
        print(Target, "gains darkvision to 60ft from transmuter's stone")
    elif (choice == 2):
        print(Target, "gains 10ft of movement speed from transmuter's stone")
        Actions.append(['move','10'])
    elif (choice == 3):
        print(Target, "gains +3 to con saves from transmuter's stone")
        Actions.append(['buff','consaves','3'])
    elif (choice == 4):
        print(Target, "gains acid resist from transmuter's stone")
        Actions.append(['resist','acid'])
    elif (choice == 5):
        print(Target, "gains cold resist from transmuter's stone")
        Actions.append(['resist','cold'])
    elif (choice == 6):
        print(Target, "gains fire resist from transmuter's stone")
        Actions.append(['resist','fire'])
    elif (choice == 7):
        print(Target, "gains lightning resist from transmuter's stone")
        Actions.append(['resist','lightning'])
    elif (choice == 8):
        print(Target, "gains thunder resist from transmuter's stone")
        Actions.append(['resist','thunder'])

# give water elementals disadvantage on this ability's save
def abidalzimshorridwilting():

    if ('elemental' in TargetData['Type'] and DnDUtil.getAnswer('Is '+Target+'\'s element water') == 'y'):
        TargetData['Disadvantages'].append(AbilityName+'2')

# clear the disadvantage that may have been given for this ability in the previous script
def abidalzimshorridwilting2():

    if (AbilityName in TargetData['Disadvantages']):
        TargetData['Disadvantages'].remove(AbilityName)

# roll 2d8 and determine the type based on the result, then signal to add target if they match
def chaosbolt():

    damageTypes = ['acid','cold','fire','force','lightning','poison','psychic','thunder']
    if (PlayerTurn):
        roll1 = 0
        while (roll1 < 1 or roll1 > 8):
            roll1 = DnDUtil.getInt(getInput("Roll for first chaos bolt damage (1d8): "))
        roll2 = 0
        while (roll2 < 1 or roll2 > 8):
            roll2 = DnDUtil.getInt(getInput("Roll for second chaos bolt damage (1d8): "))
        roll3 = DnDUtil.getInt(getInput("Roll for third chaos bolt damage ("+str(1+SpellLevel-BaseLevel)+"d6): "))
    else:
        roll1 = DnDUtil.calculate('1d8')
        roll2 = DnDUtil.calculate('1d8')
        roll3 = DnDUtil.calculate(str(1+SpellLevel-BaseLevel)+'d6')

    if (roll1 == roll2):
        damageType = damageTypes[roll1-1]
        print(AbilityName, "can jump to an additional target within 30ft of", Target+'!')
    else:
        options = [damageTypes[roll1-1],damageTypes[roll2-1]]
        choice = DnDUtil.chooseOption('Choose a damage type for '+AbilityName,options)
        damageType = options[choice-1]

    damage = roll1 + roll2 + roll3

    Actions.append(['damage',str(damage),damageType])
    if (roll1 == roll2):
        Actions.append(['addtarget'])

# determine how many skeletons and zombies to summon, then buff them appropriately
def dansemacabre():

    numCorpses = -1
    maxCorpses = 2*(SpellLevel-BaseLevel)+5
    while (numCorpses < 0 or numCorpses > maxCorpses):
        numCorpses = DnDUtil.getInt(getInput('How many small/medium corpses are in range (max '+str(maxCorpses)+')? '))

    if (numCorpses > 0):
        numSkeletons = -1
        while (numSkeletons < 0 or numSkeletons > numCorpses):
            numSkeletons = DnDUtil.getInt(getInput('How many of these should be skeletons (as opposed to zombies)? '))
        numZombies = numCorpses - numSkeletons
        if ('spmod' in ActorData['Misc']):
            spellModString = str(ActorData['Misc']['spmod'])
        else:
            spellModString = str(DnDUtil.getInt(getInput('What is '+Actor+'\'s spellcasting ability modifier? ')))
        for i in range(0,numSkeletons):
            Actions.append(['summon','skeleton','1'])
            Actions.append(['buff','atk',spellModString])
            Actions.append(['buff','dmg',spellModString])
        for i in range(0,numZombies):
            Actions.append(['summon','zombie','1'])
            Actions.append(['buff','atk',spellModString])
            Actions.append(['buff','dmg',spellModString])

# choose a damage type for the breath, then create the appropriate trigger ability
def dragonsbreath():
    
    options = ['acid','cold','fire','lightning','poison']
    choice = DnDUtil.chooseOption('Choose a damage type for the breath weapon',options)
    damageType = options[choice-1]
    Actions.append(['use','dragonsbreath'+damageType])

# choose a form for the spell and use the appropriate ability
def guardianofnature():

    choice = DnDUtil.chooseOption('Choose a form to take',['Primal Beast','Great Tree'])
    if (choice == 1):
        Actions.append(['use','guardianofnaturebeast'])
    else:
        Actions.append(['use','guardianofnaturetree'])

# figure out which weapon was enchanted with this spell already and apply the appropriate on-hit ability
def holyweapon():

    rangeIndex = -1
    for effect in AbilityEffects:
        if (effect[0] == Target and effect[1] == 'magicweapon' and effect[3] == 0):
            rangeIndex = effect[2]
            break
    if (rangeIndex == -1):
        DnDUtil.printError("Script holyweapon: Expected to find magicweapon effect, but none was found")
    elif (rangeIndex == 0):
        Actions.append(['onhit','holyweaponmeleeOH'])
    else:
        Actions.append(['onhit','holyweaponrangedOH'])

# choose a damage type for the breath weapon and use the appropriate ability
def illusorydragon():

    # only run this script on the last target to prevent creating multiple triggers
    if (Target == Targets[-1]):
        options = ['acid','cold','fire','lightning','necrotic','poison']
        choice = DnDUtil.chooseOption('Choose a damage type for the breath weapon',options)
        damageType = options[choice-1]
        Actions.append(['use','illusorydragon'+damageType])

# determine how much healing should be done (twice the necrotic damage taken)
def lifetransference():

    if ('necrotic' in SavedDamageRolls):
        Actions.append(['heal',str(2*SavedDamageRolls['necrotic'])])

# determine if target was already restrained by this ability. If so, allow for half damage if the save was passed; otherwise, do nothing if the save was passed and restrain if the save was failed 
def mega():

    if (any(effect[0] == Target and effect[1] == 'cc' and effect[2] == 'maximiliansearthengrasp' for effect in ActorData['Effects']) and ActorUtil.hasStatus(TargetData,['restrain'])):
        Actions.append(['damage','2d6','bludgeoning','nonmagic'])
        if (SaveDiff == 0):
            global Half
            Half = True
            print(Target, "will take half damage from", AbilityName)
    elif (SaveDiff > 0):
        Actions.append(['damage','2d6','bludgeoning','nonmagic'])
        Actions.append(['cc','restrain'])

# deal damage if the target is not undead, otherwise, give half temp hp
def negativeenergyflood():

    if ('undead' in TargetData['Type']):
        print(Target, "will instead gain half the damage as temp hp since it is undead!")
        if (PlayerTurn):
            tempHP = DnDUtil.getInt(getInput("Roll for "+AbilityName+" damage (5d12): "))
        else:
            tempHP = DnDUtil.calculate('5d12')
        Actions.append(['temphp',str(DnDUtil.divide((tempHP), (2)))])
    else:
        Actions.append(['damage','5d12','necrotic'])
        Actions.append(['msg','If target dies from this damage, summon a zombie on actor\'s next turn'])

# only use the actions if target has 100 hp or lower
def powerwordpain():

    if (PlayerTarget):
        hp = DnDUtil.getInt(getInput('What is '+Target+'\'s current hp? '))
    else:
        hp = TargetData['HP']

    if (hp <= 100):
        Actions.append(['ccsave','powerwordpain','end'])
        Actions.append(['dis','attacks','str','dex','con','int','wis','cha','strsaves','dexsaves','intsaves','wissaves','chasaves'])
        Actions.append(['move','ground','10'])
        Actions.append(['msg','None of target\'s move speeds can be higher than 10'])
        Actions.append(['msg','If target attempts to cast a spell, it must succeed on a con save or the spell is wasted!'])
    else:
        print(AbilityName, "will have no effect since", Target, "is above 100 hp!")

# give str and con save proficiency and extra attack if needed
def tenserstransformation():

    profBonus = 0
    if (DnDUtil.getAnswer('Is '+Target+' proficient in str saves') == 'n'):
        profBonus = DnDUtil.getInt(getInput('What is '+Target+'\'s proficiency bonus? '))
        Actions.append(['buff','strsaves',str(profBonus)])
    if (DnDUtil.getAnswer('Is '+Target+' proficient in con saves') == 'n'):
        if (not(profBonus)):
            profBonus = DnDUtil.getInt(getInput('What is '+Target+'\'s proficiency bonus? '))
        Actions.append(['buff','consaves',str(profBonus)])
    if (DnDUtil.getAnswer('Does '+Target+' have the Extra Attack feature') == 'n'):
        Actions.append(['bonusattack'])

# deal 1d12 damage if the target has been hurt, otherwise, deal 1d8 damage
def tollthedead():

    cantripLvl = SpellUtil.getCantripModifierForActor(Actor,ActorData)

    maxHP = False
    if (PlayerTarget):
        if (DnDUtil.getAnswer('Is '+Target+' at max HP') == 'y'):
            maxHP = True
    elif (TargetData['HP'] == TargetData['MaxHP']):
        maxHP = True

    if (maxHP):
        damageDie = 'd8'
    else:
        damageDie = 'd12'

    Actions.append(['damage',str(cantripLvl)+damageDie,'necrotic'])

# choose an effect and apply the appropriate actions and remember our choice for future targets
def transmuterock():

    if (not('transmuterock' in SavedDamageRolls)):
        choice = DnDUtil.chooseOption('Choose which effect is happening with this spell',['Transmuting rock to mud','Transmuting mud to rock'])
        SavedDamageRolls['transmuterock'] = choice
    else:
        choice = SavedDamageRolls['transmuterock']

    if (choice == 1):
        Actions.append(['use','transmuterocktomud'])
    else:
        Actions.append(['use','transmutemudtorock'])

# choose an effect and apply the appropriate actions and remember our choice for future targets
def transmuterocktomud():

    if (not('transmuterocktomud' in SavedDamageRolls)):
        choice = DnDUtil.chooseOption('Choose where the effect is happening',['Floor','Ceiling'])
        SavedDamageRolls['transmuterocktomud'] = choice
    else:
        choice = SavedDamageRolls['transmuterocktomud']

    if (choice == 1):
        Actions.append(['use','transmuterocktomudfloor'])
    else:
        Actions.append(['use','transmuterocktomudceiling'])

# change the save to DC 20 str so the correct save is made to clear the effect
def transmutemudtorock():

    global SaveType, SaveDC
    SaveType = 'str'
    SaveDC = 20

# if the target is large or smaller, use the secondary ability
def whirlwind():

    if (TargetData['SizeMod'] <= 1):
        Actions.append(['use','whirlwindsecondary'])

# change the save type to allow a str or dex check to escape
def whirlwindsecondary():

    global SaveType
    SaveType = 'str/dex'

# choose an effect and apply the appropriate actions and remember our choice for future targets
def wrathofnature():

    if (not('wrathofnature' in SavedDamageRolls)):
        choice = DnDUtil.chooseOption('Choose what is created in the area',['Grasses and Undergrowth','Trees','Roots and Vines','Rocks'])
        SavedDamageRolls['wrathofnature'] = choice
    else:
        choice = SavedDamageRolls['wrathofnature']

    if (choice == 1):
        Actions.append(['msg','The area becomes difficult terrain for actor\'s enemies'])
    elif (choice == 2):
        Actions.append(['use','wrathofnaturetrees'])
    elif (choice == 3):
        Actions.append(['use','wrathofnatureroots'])
    else:
        Actions.append(['use','wrathofnaturerocks'])

# change the save type to allow an athletics check to escape
def wrathofnatureroots():

    global SaveType
    SaveType = 'str/athletics'

# clear the on hit ability added earlier since we don't want it to exist past this spell, then clear abilityEffects so the ability isn't recorded
def greenflameblade():

    if ('greenflamebladeOH' in ActorData['ExtraOnHitAbilities']):
        del ActorData['ExtraOnHitAbilities']['greenflamebladeOH']

    del AbilityEffects[:]

# clear the on hit ability added earlier since we don't want it to exist past this spell, then clear abilityEffects so the ability isn't recorded
def boomingblade():

    if ('boomingbladeOH' in ActorData['ExtraOnHitAbilities']):
        del ActorData['ExtraOnHitAbilities']['boomingbladeOH']

    del AbilityEffects[:]

# set the target to the actor and store target's data in SavedDamageRolls so we can retrieve it later
def setTargetToActor():

    global Target, TargetData, PlayerTarget
    SavedDamageRolls['TargetData'] = TargetData
    Target = Actor
    TargetData = ActorData
    PlayerTarget = PlayerTurn

# restore the original target
def restoreTarget():

    global Target, TargetData, PlayerTarget
    if ('TargetData' in SavedDamageRolls):
        Target = Targets[0]
        TargetData = SavedDamageRolls['TargetData']
        PlayerTarget = not('HP' in TargetData)
    else:
        DnDUtil.printError("Script restoreTarget: Expected to find targetData in SavedDamageRolls, but it was not found")

# randomly choose an effect
def ironcobrapoison():

    roll = random.randint(1,3)
    if (roll == 1):
        Actions.append(['damage','3d8','poison'])
    elif (roll == 2):
        Actions.append(['cc','confusion','targetend'])
        Actions.append(['msg','On target\'s next turn, it must make a melee attack against a random creature in range, moving as necessary'])
    else:
        Actions.append(['cc','paralysis','targetend'])

# confuse the target if they failed the save by 5 or more; otherwise, give disadvantage on the next attack
def fomentmadness():
    
    if (SaveDiff >= 5):
        print(Target, "will be confused due to failing the save by 5 or more!")
        Actions.append(['ccsave','confusion','end'])
        Actions.append(['react'])
        Actions.append(['msg','On each of target\'s turns while confused, roll a d10. On 1, move in a random direction. On 2-6, do nothing. On 7-8, make a melee attack against a random creature in range. On 9-10, take turn as normal.'])
    else:
        Actions.append(['dis','nextattack'])

# randomly choose a flail effect and apply it
def yeenoghuflail():

    global SaveDC
    roll = random.randint(1,3)
    if (roll == 1):
        Actions.append(['damage','2d12','bludgeoning'])
    elif (roll == 2):
        SaveDC = 17
        Actions.append(['use','paralysisflailOH'])
    else:
        SaveDC = 17
        Actions.append(['use','confusionflailOH'])

# prone the target if they failed the save by 5 or more
def swataway():

    if (SaveDiff >= 5):
        print(Target, "will be knocked prone due to failing the save by 5 or more!")
        Actions.append(['prone'])

# choose which effect to use for this hit, also set the DC for the abilities
def orthonOH():

    global SaveDC
    SaveDC = 17

    options = ['acid damage', 'radiant damage + 20ft aoe blind (1/day)', '20ft aoe thunder damage', 'restrain', 'lightning damage + paralysis (1/day)', 'can track target for the next 24 hours']
    choice = DnDUtil.chooseOption('Choose what the orthon\'s crossbow does on hit',options)
    ability = ''
    if (choice == 1):
        ability = 'orthonacidOH'
    elif (choice == 2):
        ability = 'orthonblindnessOH'
    elif (choice == 3):
        ability = 'orthonconcussionAOE'
    elif (choice == 4):
        ability = 'orthonentanglementOH'
    elif (choice == 5):
        ability = 'orthonparalysisOH'
    else:
        Actions.append(['msg','actor can track target for the next 24 hours'])

    if (ability):
        if (choice == 3):
            Actions.append(['useon',ability])
        else:
            Actions.append(['use',ability])

# change the save type to str or dex so either check can be made to clear the effect
def orthonentanglementOH():

    global SaveType
    SaveType = 'str/dex'

# deal an extra 2d8 nonmagical bludgeoning damage to prone targets
def stompingfoot():

    if (TargetData['Prone']):
        print("This attack deals 2d8 additional damage since", Target, "is prone!")
        Actions.append(['damage','2d8','bludgeoning','nonmagic'])

# choose a damage type then deal 2d8 damage of that type
def wrathofthestorm():

    options = ['lightning','thunder']
    choice = DnDUtil.chooseOption('Choose a damage type',options)
    damageType = options[choice-1]
    Actions.append(['damage','2d8',damageType])

# give the demon disadvantage on its saves against this spell if it was summoned using its true name
def demoncontrol():

    if (DnDUtil.getAnswer('Was '+Target+' summoned using its true name') == 'y'):
        Actions.append(['dis','demoncontrol'])

# do nothing to huge or larger creatures, otherwise restrain for 1 minute
def waterysphere():

    if (TargetData['SizeMod'] >= 2):
        print(Target, "is too large to fit in the sphere!")
    else:
        Actions.append(['ccsave','restrain','end','10'])

# ensure that target is not larger than huge and have actor make a spellcasting ability check versus target's strength check and restrain target until the end of actor's next turn if actor wins 
def telekinesis():
    
    if (TargetData['SizeMod'] > 2):
        print(Target, "is too large to be affected by telekinesis!")
    else:
        actorResult = 0
        targetResult = 0
        while (actorResult == targetResult):
            actorResult = ActorUtil.makeCheck(Actor,ActorData,PlayerTurn,'spellcasting ability')
            targetResult = ActorUtil.makeCheck(Target,TargetData,PlayerTarget,'str')
            if (actorResult > targetResult):
                print(Actor, DnDUtil.getPassText('wins')+'!')
                Actions.append(['cc','restrain','actorend'])
                Actions.append(['msg','target can be moved up to 30ft in any direction as long as it is still within 60ft of actor!'])
            elif (actorResult < targetResult):
                print(Actor, DnDUtil.getFailText('loses'))
            else:
                print("It's a tie!")

# deal 2d6 bludgeoning if the target is prone
def grayrenderOH():

    if (TargetData['Prone']):
        Actions.append(['damage','2d6','bludgeoning','nonmagic'])

# deal 4d10 psychic damage if the target is feared
def howlerOH():

    if (ActorUtil.hasStatus(TargetData,['fear'])):
        Actions.append(['damage','4d10','psychic'])

# randomly select a short-term madness and apply its effects, saving the result for future targets
def touchofmadness():

    if (AbilityName in SavedDamageRolls):
        madnessRoll = SavedDamageRolls[AbilityName]
    else:
        madnessRoll = random.randint(1,100)
        SavedDamageRolls[AbilityName] = madnessRoll

    if (madnessRoll < 21):
        Actions.append(['cc','paralysis'])
        Actions.append(['msg','target retreats into his/her mind'])
    elif (madnessRoll < 31):
        Actions.append(['cc','incapacitate'])
        Actions.append(['msg','target begins to scream/laugh/weep'])
    elif (madnessRoll < 41):
        Actions.append(['cc','fear'])
        Actions.append(['msg','target must spend its turns fleeing from actor'])
    elif (madnessRoll < 51):
        Actions.append(['msg','target begins to babble and cannot speak normally or cast spells'])
    elif (madnessRoll < 61):
        Actions.append(['msg','target must use its action each round to attack the nearest creature'])
    elif (madnessRoll < 71):
        Actions.append(['dis','checks'])
        Actions.append(['msg','target experiences vivid hallucinations'])
    elif (madnessRoll < 76):
        Actions.append(['msg','target does whatever it is told that isn\'t obviously self-destructive'])
    elif (madnessRoll < 81):
        Actions.append(['msg','target experiences an overpowering urge to eat something strange'])
    elif (madnessRoll < 91):
        Actions.append(['cc','stun'])
    else:
        Actions.append(['cc','unconscious'])

# choose which rite to use and which weapon(s) to apply to and change the ability's trigger condition so it triggers on the correct attack, and load the ability into the appropriate OnHitAbilities slot(s)
def crimsonrite():

    crimsonRiteAbilityNames = []
    for useAbility in TargetData['UseAbilities']:
        if (useAbility.startswith('crimsonriteOH')):
            crimsonRiteAbilityNames.append(useAbility)

    if (crimsonRiteAbilityNames):
        choice = DnDUtil.chooseOption('Choose which rite to use',crimsonRiteAbilityNames)
        crimsonRiteAbilityName = crimsonRiteAbilityNames[choice-1]

        atkList = []
        atkStringList = []
        for rangeIndex in range(0,len(TargetData['Atk'])):
            for atkIndex1 in range(0,len(TargetData['Atk'][rangeIndex])):
                for atkIndex2 in range(0,len(TargetData['Atk'][rangeIndex][atkIndex1])):
                    atkList.append(str(rangeIndex)+str(atkIndex1)+str(atkIndex2))
                    atkStringList.append(str(TargetData['Atk'][rangeIndex][atkIndex1][atkIndex2])+' - '+atkList[-1])
    
        SavedDamageRolls[crimsonRiteAbilityName] = []
        done = False
        firstIt = True
        while (atkList and not(done)):
            choice = DnDUtil.chooseOption('Choose an attack to apply crimson rite',atkStringList,not(firstIt))
            if (choice <= len(atkList)):
                SavedDamageRolls[crimsonRiteAbilityName].append(atkList.pop(choice-1))
                atkStringList.pop(choice-1)
            else:
                done = True
            firstIt = False
        Actions.append(['onhit',crimsonRiteAbilityName])
        Actions.append(['script','crimsonriteend'])
    else:
        DnDUtil.printError("No ability starting with crimsonriteOH found in "+Target+"'s data")

# alter all extraonhitabilities that were generated from this ability to trigger on the correct attacks
def crimsonriteend():

    name,atkIndices = list(SavedDamageRolls.items())[0]
    if (len(atkIndices) == 1):
        TargetData['ExtraOnHitAbilities'][name]['Trigger Condition'] = atkIndices[0]
    else:
        AbilityEffects.pop()
        ability = TargetData['ExtraOnHitAbilities'].pop(name)
        for atkIndex in atkIndices:
            ability['Trigger Condition'] = atkIndex
            newAbility = copy(ability)
            TargetData['ExtraOnHitAbilities'][name+atkIndex] = newAbility 
            AbilityEffects.append([Target,'onhit',name+atkIndex,newAbility])

# give the option to expend a spell slot to deal 2d8+lvld8 bludgeoning damage
def blackearthrod():

    if (DnDUtil.getAnswer('Expend a spell slot to deal extra damage with this attack') == 'y'):
        spellLevel = SpellUtil.inputSpellLevel('blackearthrod',1)
        Actions.append(['damage',str(2+spellLevel-1)+'d8','bludgeoning','nonmagic'])

# set save to str and set dc to 10
def ceilingcollapse():

    global SaveType, SaveDC
    SaveType = 'str'
    SaveDC = 10

# change save type to str for escape attempts
def turntomud():

    global SaveType
    SaveType = 'str'

# if this creature is restrained by turntomud, change the DC from 15 to 20
def hardenmud():

    turnToMudStatusEffect = []
    for statusEffect in TargetData['Status']:
        if (statusEffect[0] == 'turntomud'):
            turnToMudStatusEffect = statusEffect
            break
    if (turnToMudStatusEffect):
        turnToMudStatusEffect[3] = 20
        Actions.append(['msg','The mud around target has hardened and increased the escape DC to 20!'])
    else:
        DnDUtil.printWarning("Script hardenmud: Could not find turntomud status effect")

# if this spell crit, deal 12d12 damage; otherwise, deal the normal 4d12
def bladeofdisaster():

    global Crit
    if (Crit):
        Crit = False
        print(AbilityName, "deals an additional 8d12 force damage on a crit!")
        Actions.append(['damage','12d12','force'])
    else:
        Actions.append(['damage','4d12','force'])

# choose the damage type and store it along with the damage it should deal
def spiritshroud():

    options = ['radiant','necrotic','cold']
    choice = DnDUtil.chooseOption('Choose a damage type',options)
    damageType = options[choice-1]
    Actions.append(['misc','spiritshroudtype',damageType])
    Actions.append(['misc','spiritshrouddamage',str(1+DnDUtil.divide((SpellLevel-BaseLevel), (2)))+'d8'])

# choose the spirit to summon and alter its stats based on the caster and spell level
def summonSpirit(baseSpiritName,options,hpMult):

    choice = DnDUtil.chooseOption('Choose which spirit to summon',options)
    summon = options[choice-1].lower().replace(' ','')
    Actions.append(['summon',baseSpiritName+summon,'1'])
    Actions.append(['buff','ac',str(SpellLevel)])
    if (SpellLevel > BaseLevel):
        Actions.append(['buff','hp',str(hpMult*(SpellLevel-BaseLevel))])
    Actions.append(['buff','spelldc',str(SaveDC)])
    Actions.append(['buff','atk',str(SpellAtk)])
    Actions.append(['buff','dmg',str(SpellLevel)])
    for i in range(1,DnDUtil.divide((SpellLevel), (2))):
        Actions.append(['bonusattack'])
    return choice

def summonaberration():

    summonSpirit('aberrantspirit',['Beholderkin','Slaad','Star Spawn'],10)

def summonbeast():

    summonSpirit('beastialspirit',['Air','Land','Water'],5)

def summoncelestial():

    summonSpirit('celestialspirit',['Avenger','Defender'],10)
    Actions.append(['script','celestialSpiritHealingTouch'])

# increase healing touch's healing by the spell's level
def celestialSpiritHealingTouch():

    try:
        TargetData['UseAbilities']['healingtouch']['Actions'][0][1] += '+'+str(SpellLevel)
    except KeyError:
        DnDUtil.printError("Expected "+Target+" to have healingtouch ability")
    except IndexError:
        DnDUtil.printError("Expected "+Target+"'s healingtouch ability to have actions 'heal,2d8'")

def summonconstruct():

    summonSpirit('constructspirit',['Clay','Metal','Stone'],15)

def summonelemental():

    summonSpirit('elementalspirit',['Air','Earth','Fire','Water'],10)

def summonfey():

    summonSpirit('feyspirit',['Fuming','Mirthful','Tricksy'],10)

# increase the demon's death burst damage by the spell's level
def summonfiend():

    choice = summonSpirit('fiendishspirit',['Demon','Devil','Yugoloth'],15)
    if (choice == 1):
        try:
            TargetData['UseAbilities']['fiendishspiritdemondb']['Actions'][0][1] += '+'+str(SpellLevel)
        except KeyError:
            DnDUtil.printError("Expected "+Target+" to have findishspiritdemondb ability")
        except IndexError:
            DnDUtil.printError("Expected "+Target+"'s fiendishspiritdemondb ability to have action 'damage,2d10,fire'")

def summonshadowspawn():

    summonSpirit('shadowspirit',['Fury','Despair','Fear'],15)

def summonundead():

    summonSpirit('undeadspirit',['Ghostly','Putrid','Skeletal'],10)

# allow actor to choose a resistance to gain based on the type of dragon summoned
def summondraconicspirit():

    summonChoice = summonSpirit('draconicspirit',['Chromatic','Gem'],10)
    if (summonChoice == 1):
        resistanceChoices = ['acid','cold','fire','lightning','poison']
    else:
        resistanceChoices = ['force','necrotic','psychic','radiant','thunder']
    resistanceChoice = DnDUtil.chooseOption('Choose a resistance to gain',resistanceChoices)
    Actions.insert(1,['resist',resistanceChoices[resistanceChoice-1]])

# choose which version to apply and give actions accordingly; also, set weapon attack bonuses to spell attack and damage to spell mod and add another attack if there is only 1
def tashasotherworldlyguise():

    choice = DnDUtil.chooseOption('Choose magic source for this spell',['Lower Planes','Upper Planes'])
    if (choice == 1):
        Actions.append(['immunity','fire','poison'])
    else:
        Actions.append(['immunity','radiant','necrotic','charm'])

    meleeAtkDelta = ActorData['SpellAtk']-TargetData['Atk'][0][0][0]
    if (meleeAtkDelta > 0):
        Actions.append(['buff','matk',str(meleeAtkDelta)])
        Actions.append(['buff','mdmg',str(meleeAtkDelta)])
    if (len(TargetData['Atk']) > 1):
        rangedAtkDelta = ActorData['SpellAtk']-TargetData['Atk'][1][0][0]
        if (rangedAtkDelta > 0):
            Actions.append(['buff','ratk',str(rangedAtkDelta)])
            Actions.append(['buff','rdmg',str(rangedAtkDelta)])
    Actions.append(['magicweapons'])
    if (len(TargetData['Atk'][0][0]) == 1):
        Actions.append(['bonusattack'])

# paralyze the target until the end of its next turn if it is poisoned
def rottingClaw():

    if (ActorUtil.hasStatus(TargetData,['poison'])):
        Actions.append(['cc','paralysis','targetend'])
    else:
        Actions.append(['msg','Nothing happens since target is not poisoned'])

# roll to determine which ability to use and remember the choice for each target
def nathairsmischief():

    if (AbilityName in SavedDamageRolls):
        secondaryAbilityName = SavedDamageRolls[AbilityName]
    else:
        if (PlayerTurn):
            roll = 0
            while (roll < 1 or roll > 4):
                roll = DnDUtil.getInt(getInput('Roll for '+AbilityName+'\'s effect (1d4): '))
        else:
            roll = random.randint(1,4)
            print(Actor, "rolls a", roll, "for", AbilityName+'\'s', "effect")

        secondaryAbilityName = AbilityName
        if (roll == 1):
            secondaryAbilityName += 'pie'
        elif (roll == 2):
            secondaryAbilityName += 'flowers'
        elif (roll == 3):
            secondaryAbilityName += 'laughinggas'
        else:
            secondaryAbilityName += 'molasses'
        SavedDamageRolls[AbilityName] = secondaryAbilityName

    Actions.append(['use',secondaryAbilityName])

# make sure actor can react, then use reaction and trigger ability
def haloofspores():

    if (ActorUtil.canReact(ActorData)):
        ActorData['Reaction'] = False
        Actions.append(['use','haloofsporest'])
    else:
        print(Actor, "can't react!")

# calculate the damage based on level and double the dice if symbiotic entity is active
def haloofsporest():

    level = ActorData['CR']
    if (level < 6):
        damageDie = '4'
    elif (level < 10):
        damageDie = '6'
    elif (level < 14):
        damageDie = '8'
    else:
        damageDie = '10'
    if (ActorUtil.hasStatus(ActorData,['symbioticentity'])):
        numDice = '2'
    else:
        numDice = '1'

    Actions.append(['damage',numDice+'d'+damageDie,'necrotic'])