# This file holds old code that may need to be referenced in the future but is no longer in use

def playerAttack(player,attackType,defaultCreature,roll,battleRoyale,rangeIndex,atkIndex,singleAttack=False):

    # list containing the names of abilities or actions that have been used this round and should not be triggered again
    usedAbilities = []
    damageSummary = {}
    atkPlayerData = playerData[player]

    if (rangeIndex >= len(atkPlayerData['Atk'])):
        DnDUtil.printError("No ranged attacks for "+player)
        return damageSummary

    if (atkIndex >= len(atkPlayerData['Atk'][rangeIndex])):
        DnDUtil.printError("No attack bonuses at index "+str(atkIndex)+" for "+player)
        return damageSummary

    if (singleAttack):
        maxAtks = 1
    else:
        maxAtks = len(atkPlayerData['Atk'][rangeIndex][atkIndex])
    
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

        if (j == len(atkPlayerData['Atk'][rangeIndex][atkIndex])-1):
            lastAttack = True
        else:
            lastAttack = False

        # for every attack after the first, allow inputting of a new attack command or simply get the roll for the next attack
        if ('firstAttack' in usedAbilities):
            attackCommand = []
            while (attackCommand == []):
                attackCommand = DnDUtil.mySplit(raw_input('Input command for attack '+str(atkCount+1)+'/'+str(maxAtks)+' (default - '+attackType+' '+defaultCreature+'): '),' ')
                if (attackCommand == ['done']):
                    return damageSummary
                numArgs = len(attackCommand)
                if (numArgs == 1 or numArgs == 2 or numArgs == 3):
                    if (numArgs > 1):
                        if (isValidAttackType(attackCommand[0])):
                            attackType = attackCommand[0]
                        else:
                            print "Invalid attack type", attackCommand[0]
                            attackCommand = []
                    if (attackCommand):
                        if (numArgs == 3):
                            nextTarget = attackCommand[1]
                        else:
                            nextTarget = defaultCreature
                        target = autoComplete(nextTarget,not(battleRoyale))
                        if (target):
                            defaultCreature = target
                        else:
                            print "Invalid attack target", nextTarget
                            attackCommand = []
                    if (attackCommand):
                        roll = DnDUtil.getInt(attackCommand[-1])
                elif (numArgs > 3):
                    print "Too many arguments given for this attack! There can only be a maximum of 3 attack arguments!"
                    attackCommand = []
        
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
            DnDUtil.printError("Invalid attack type "+attackType+" passed to playerAttack function")
            return damageSummary

        creature = chooseAttackTarget(player,atkPlayerData,defaultCreature,rangeIndex,atkIndex,j)
        # if this is a single attack, but our first attack is grabbing someone, look for another attack to use
        if (singleAttack and creature != defaultCreature):
            print player, "is grabbing an opponent with this attack! Looking for another available attack..."
            for i in range(1,len(atkPlayerData['Atk'][rangeIndex][atkIndex])):
                creature = chooseAttackTarget(player,atkPlayerData,defaultCreature,rangeIndex,atkIndex,i)
                if (creature == defaultCreature):
                    print "Another valid attack was found!"
                    j = i
                    break
            if (j == 0):
                print player, "was unable to make an attack on", defaultCreature
                return damageSummary

        defCreatureData = getData(creature)
        if (flank):
            if ('flank' in defCreatureData['Immunities']):
                print creature, "is", DnDUtil.getFailText('immune'), "to being flanked!"
                flank = False
            elif ('iflank' in atkPlayerData['Misc']):
                dmgBonus = atkPlayerData['Misc']['iflank']

        attackAdvantage = getAttackAdvantage(player,atkPlayerData,creature,defCreatureData,rangeIndex == 0,not('spell' in atkPlayerData['WeaponTypes'][rangeIndex][atkIndex][j])) or advantage or flank
        attackDisadvantage = getAttackDisadvantage(atkPlayerData,creature,defCreatureData,rangeIndex == 0,not('spell' in atkPlayerData['WeaponTypes'][rangeIndex][atkIndex][j])) or disadvantage
        roll = getAdvantageDisadvantageRoll(roll,attackAdvantage,attackDisadvantage)
        atkBonus = atkPlayerData['Atk'][rangeIndex][atkIndex][j] + bonus
        attack = roll + atkBonus
        defense = getAC(defCreatureData)
        attack = ActorUtil.applyBlessBane(player,atkPlayerData,attack,defense)

        if (not(checkTemporalShunt(player,atkPlayerData,True))):
            return damageSummary

        if (applyMirrorImage(roll,attack,creature,defCreatureData,battleRoyale) and roll != 1 and (roll == 20 or attack >= defense)):
            if (roll != 20 and 'parry' in defCreatureData['Misc'] and rangeIndex == 0 and defense + defCreatureData['Misc']['parry'] > attack and ActorUtil.canReact(defCreatureData) and DnDUtil.getAnswer('Use '+creature+'\'s reaction to parry') == 'y'):
                print creature, "uses its reaction to parry the attack!"
                defCreatureData['Reaction'] = False
            elif (roll != 20 and 'ad' in defCreatureData['Misc'] and defense + 2 > attack and ActorUtil.canReact(defCreatureData) and DnDUtil.getAnswer('Use '+creature+'\'s reaction to use arcane deflection') == 'y'):
                print creature, "uses its reaction to use arcane deflection and negate the attack!"
                defCreatureData['Reaction'] = False
                applyCC(creature,creature,defCreatureData,'arcane deflection')
                defCreatureData['Effects'].append([creature,'cc','arcane deflection',[],1.5])
            elif (roll != 20 and 'shield' in defCreatureData['UseAbilities'] and defense + 5 > attack and ActorUtil.canReact(defCreatureData) and DnDUtil.getAnswer('Use '+creature+'\'s reaction to cast Shield') == 'y'):
                print creature, "uses its reaction to cast Shield and block the attack!"
                defCreatureData['Reaction'] = False
                ability = defCreatureData['UseAbilities']['shield']
                useAbility(battleRoyale,'shield',ability['Type'],ability['Duration'],ability['Actions'],battleRoyale,[creature],creature,defCreatureData,creature,defCreatureData,ability['Attack Mod'],ability['Save'],ability['DC'],0,ability['Base Level'],ability['Base Level'],False,False,False,ability['Concentration?'],{})
            else:
                hit = True
                critC = getCritStat(atkPlayerData,rangeIndex,atkIndex,j,0)
                damageData = atkPlayerData['Damage'][rangeIndex][atkIndex][j]
                dmgBonusData = atkPlayerData['DmgBonus'][rangeIndex][atkIndex][j]
                weaponTypeData = atkPlayerData['WeaponTypes'][rangeIndex][atkIndex][j]
                if (roll >= critC or rangeIndex == 0 and ActorUtil.hasStatus(defCreatureData,['paralysis','sleep','unconscious'])):
                    if (not(ActorUtil.isImmuneToType(defCreatureData,['crit']))):
                        crit = True
                    else:
                        print creature, "can't be", DnDUtil.getFailText('crit')+'!'

        if (hit):
            print player, "successfully hits", creature+'!'

            if (crit):
                critMultiplier = getCritStat(atkPlayerData,rangeIndex,atkIndex,j,1)
                print "This is a crit!"
                print "This attack's damage will be multiplied by", critMultiplier
                if (rangeIndex == 0 and 'gwm' in atkPlayerData['Misc'] and not('cleave' in usedAbilities)):
                    print "Cleave activated!"
                    cleave = True
                if ('bc' in atkPlayerData['Misc'] and rangeIndex == 0):
                    dmgBonus += DnDUtil.getInt(raw_input("Roll for brutal critical ("+atkPlayerData['Misc']['bc']+"): "))
            else:
                critMultiplier = 1

            if ('ud' in defCreatureData['Misc'] and ActorUtil.canReact(defCreatureData) and DnDUtil.getAnswer('Use '+creature+'\'s reaction to use uncanny dodge on this attack') == 'y'):
                uncannyDodge = True
                defCreatureData['Reaction'] = False

            done = False
            while (not(done)):
                damage = raw_input("Roll for weapon damage "+"("+damageData+"): ")
                if (damage in ['dsmite','sstrike']):
                    if (rangeIndex != 0):
                        print "You can only activate", damage, "on melee attacks!"
                    elif (not(damage in atkPlayerData['UseAbilities'])):
                        print player, "does not have access to", damage+'!'
                    else:
                        print damage, "activated!"
                        ability = copy(atkPlayerData['UseAbilities'][damage])
                        ability['Trigger Condition'] = ability['Attack']
                        ability['Charges'] = 1
                        onHitAbilities.append([damage,ability])
                elif (damage.isdigit()):
                    done = True
                    damage = int(damage)

            if (ActorUtil.hasStatus(defCreatureData,['huntersmark']) and any(effect[0] == creature and effect[1] == 'cc' and effect[2] == 'huntersmark' and effect[-1] == -1 for effect in atkPlayerData['Effects'])):
                damage += DnDUtil.getInt(raw_input('Roll for hunter\'s mark damage (1d6): '))

            damage = int(damage*critMultiplier) + dmgBonusData

            if (dmgBonus):
                if (isinstance(dmgBonus,int)):
                    damage += dmgBonus
                elif (dmgBonus.isdigit()):
                    damage += int(dmgBonus)
                else:
                    damage += int(DnDUtil.getInt(raw_input('Roll for bonus damage ('+dmgBonus+'): '))*critMultiplier)

            for creatureType in defCreatureData['Type']:
                if (creatureType in atkPlayerData['Misc']):
                    if (atkPlayerData['Misc'][creatureType].isdigit()):
                        damage += atkPlayerData['Misc'][creatureType]
                    else:
                        damage += int(critMultiplier*DnDUtil.getInt(raw_input('Roll for bonus damage since '+creature+' is '+creatureType+' ('+atkPlayerData['Misc'][creatureType]+'): ')))

            if (damage < 0):
                damage = 0
            if (not('sneakAttack' in usedAbilities) and (sneakAttack or attackAdvantage and not(attackDisadvantage)) and 'sa' in atkPlayerData['Misc'] and not(ActorUtil.isImmuneToType(defCreatureData,['crit']))):
                usedAbilities.append('sneakAttack')
                parsedSneakAttackDamage = DnDUtil.parseDamageCalculation(atkPlayerData['Misc']['sa'])
                sneakAttackDamage = int(critMultiplier*DnDUtil.getInt(raw_input("Roll for sneak attack damage "+"("+parsedSneakAttackDamage[0]+"): "))) + parsedSneakAttackDamage[1]
                damage += sneakAttackDamage

            if (damage > 0):
                damage = getNetDamage(damage,atkPlayerData,creature,defCreatureData,weaponTypeData,'this attack',True,uncannyDodge)

                if ('ham' in defCreatureData['Misc'] and (weaponTypeData and 'nonmagic' in weaponTypeData or not(weaponTypeData) and DnDUtil.getAnswer('Is this an attack from a magic weapon') == 'n')):
                    damage -= 3
                    if (damage < 0):
                        damage = 0

            if (ActorUtil.hasStatus(defCreatureData,['hex']) and any(effect[0] == creature and effect[1] == 'cc' and effect[2] == 'hex' and effect[-1] == -1 for effect in atkPlayerData['Effects'])):
                damage += int(getNetDamage(DnDUtil.getInt(raw_input('Roll for hex damage (1d6): ')),atkPlayerData,creature,defCreatureData,['necrotic'],'hex',False)*critMultiplier)

            if (ActorUtil.hasStatus(atkPlayerData,['spiritshroud']) and (rangeIndex == 0 or DnDUtil.getAnswer('Is '+creature+' within 10ft of '+player) == 'y')):
                if (not('spiritshroudtype' in atkPlayerData['Misc'])):
                    DnDUtil.printWarning("Missing spiritshroudtype misc data in "+player)
                elif (not('spiritshrouddamage' in atkPlayerData['Misc'])):
                    DnDUtil.printWarning("Missing spiritshrouddamage misc data in "+player)
                else:
                    spiritShroudDamage = int(getNetDamage(DnDUtil.getInt(raw_input('Roll for spirit shroud damage ('+atkPlayerData['Misc']['spiritshrouddamage']+'): ')),atkPlayerData,creature,defCreatureData,[atkPlayerData['Misc']['spiritshroudtype']],'spritshroud',False)*critMultiplier)
                    damage += spiritShroudDamage
                    if (spiritShroudDamage):
                        useAbility(True,'spirit shroud antiheal',[],1.5,[['immunity','heal']],battleRoyale,[creature],creature,defCreatureData,player,atkPlayerData,0,'',0,0,0,0,False,False,False,False,{})

            if (not('divineFury' in usedAbilities) and ('dfn' in atkPlayerData['Misc'] or 'dfr' in atkPlayerData['Misc']) and ActorUtil.hasStatus(atkPlayerData,['rage'])):
                usedAbilities.append('divineFury')
                if ('dfn' in atkPlayerData['Misc']):
                    dfKey = 'dfn'
                    damageType = 'necrotic'
                else:
                    dfKey = 'dfr'
                    damageType = 'radiant'
                damage += int(getNetDamage(DnDUtil.getInt(raw_input('Roll for divine fury damage (1d6): ')),atkPlayerData,creature,defCreatureData,[damageType],'divine fury',False)*critMultiplier)
                if (atkPlayerData['Misc'][dfKey]):
                    damage += atkPlayerData['Misc'][dfKey]/2
                else:
                    damage += atkPlayerData['CR']/2

            if (rangeIndex == 1 and 'dm' in defCreatureData['Misc'] and ActorUtil.canReact(defCreatureData)):
                if (not(battleRoyale)):
                    print creature, "activates deflect missile!"
                    defCreatureData['Reaction'] = False
                    if (damage > 0):
                        deflectRoll = random.randint(1,10)
                        print creature, "rolls a", deflectRoll, "for damage reduction"
                        deflectDmgReduction = deflectRoll + defCreatureData['Misc']['dm']
                        print "This attack's damage will be reduced by", deflectDmgReduction
                        damage -= deflectDmgReduction
                        if (damage < 0):
                            damage = 0
                    if (damage == 0):
                        print creature, "is redirecting the attack!"
                        deflectAttackTarget = ''
                        finished = False
                        while (not(finished)):
                            deflectAttackTarget = raw_input('Choose a target for this attack: ')
                            if (deflectAttackTarget == ''):
                                finished = True
                            elif (deflectAttackTarget in playerData):
                                finished = True
                            else:
                                print "Invalid player name!"
                        if (deflectAttackTarget != ''):
                            deflectDamageSummary = creatureAttack(creature,'r',deflectAttackTarget,1,0,True)
                            extendDamageSummary(damageSummary,deflectDamageSummary)
                            if (not(creature in encounter)):
                                return damageSummary

                elif (DnDUtil.getAnswer('Use your reaction to deflect missile') == 'y'):
                    defCreatureData['Reaction'] = False
                    if (damage > 0):
                        deflectDmgReduction = DnDUtil.getInt(raw_input('Roll for damage reduction (1d10): ')) + defCreatureData['Misc']['dm']
                        print "This attack's damage will be reduced by", deflectDmgReduction
                        damage -= deflectDmgReduction
                        if (damage < 0):
                            damage = 0
                    if (damage == 0 and DnDUtil.getAnswer('Spend a ki point to attack with this missile') == 'y'):
                        deflectAttackTarget = ''
                        finished = False
                        while (not(finished)):
                            deflectAttackTarget = raw_input('Choose a target for this attack: ')
                            if (deflectAttackTarget == ''):
                                finished = True
                            else:
                                deflectAttackTarget = autoComplete(deflectAttackTarget,False)
                                if (deflectAttackTarget != ''):
                                    finished = True
                        if (deflectAttackTarget != ''):
                            deflectAttackRoll = DnDUtil.getInt(raw_input('Roll for deflect attack: '))
                            deflectDamageSummary = playerAttack(creature,'r',player,deflectAttackRoll,True,1,0,True)
                            extendDamageSummary(damageSummary,deflectDamageSummary)

            if (damage > 0):
                if (weaponTypeData):
                    primaryWeaponType = weaponTypeData[0]
                else:
                    primaryWeaponType = ''
                print player, "deals", DnDUtil.getDamageText(damage), primaryWeaponType, "damage to", creature
                if (not(battleRoyale)):
                    dealDamage(defCreatureData,damage)
                killed = applyDamage(creature,defCreatureData,damage,weaponTypeData,crit)
                updateDamageSummary(damageSummary,creature,damage)

            if (not(killed)):
                if (rangeIndex < len(atkPlayerData['OnHitAbilities']) and atkIndex < len(atkPlayerData['OnHitAbilities'][rangeIndex])):
                    if (len(atkPlayerData['OnHitAbilities'][rangeIndex][atkIndex]) == 1):
                        onHitAbilities.append([player+' On Hit Ability '+str(rangeIndex)+str(atkIndex)+str(j),atkPlayerData['OnHitAbilities'][rangeIndex][atkIndex][0]])
                    elif (len(atkPlayerData['OnHitAbilities'][rangeIndex][atkIndex]) == len(atkPlayerData['Atk'][rangeIndex][atkIndex])):
                        onHitAbilities.append([player+' On Hit Ability '+str(rangeIndex)+str(atkIndex)+str(j),atkPlayerData['OnHitAbilities'][rangeIndex][atkIndex][j]])
                    else:
                        DnDUtil.printError("Invalid on hit abilities format")

                for onHitAbility,onHitAbilityData in atkPlayerData['ExtraOnHitAbilities'].items():
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
                        saveDC = ability['DC'] if ability['DC'] != 0 else atkPlayerData['SpellDC']
                        # don't perform any actions from this ability that would create effects already active from the attacker
                        for effect in atkPlayerData['Effects']:
                            if (effect[0] == creature and effect[1] == 'cc' and effect[2] == abilityName):
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
                                elif (triggerCondition == 'kill'):
                                    if (not(battleRoyale) and 'HP' in defCreatureData and defCreatureData['HP'] > 0):
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
                            # don't use any more abilities if the target is already dead, but still check if it would trigger so we can subtract a charge
                            if (killed):
                                success = False

                        if (success):
                            if (abilityName.find('On Hit Ability') != -1):
                                ohTypes = getOnHitTypes(atkPlayerData,rangeIndex,atkIndex,j)
                            else:
                                ohTypes = ability['Type']

                        if (success and ability['Save'] and ability['Save Result'] != 'none'):
                            saveDiff = makeSave(creature,defCreatureData,ability['Save'],saveDC,ohTypes)
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
                            if (ActorUtil.isImmuneToType(defCreatureData,ohTypes)):
                                print creature, "is", DnDUtil.getFailText('immune'), "to this on-hit ability!"
                            else:
                                if ('Base Level' in ability and 'Spell Level' in ability):
                                    baseLevel = ability['Base Level']
                                    spellLevel = ability['Spell Level']
                                else:
                                    baseLevel = -1
                                    spellLevel = -1
                                abilityDamageSummary = useAbility(not('HP' in atkPlayerData),abilityName,ohTypes,ability['Duration'],actionData,not('HP' in defCreatureData),[creature],creature,defCreatureData,player,atkPlayerData,0,ability['Save'],saveDC,saveDiff,baseLevel,spellLevel,half,crit,uncannyDodge,ability['Concentration?'],{})
                                extendDamageSummary(damageSummary,abilityDamageSummary)
                                if (not(battleRoyale) and not(creature in encounter)):
                                    killed = True

                        if (triggerConditionSuccess):
                            if (ability['Charges'] != -1):
                                ability['Charges'] -= 1
                                if (ability['Charges'] == 0):
                                    if (abilityName in atkPlayerData['ExtraOnHitAbilities']):
                                        print player, "no longer has the on-hit ability", abilityName
                                        # since the effect that created this on-ability is very likely to reside in the attacker, it is worth it to check and try to remove it
                                        found = False
                                        for effect in atkPlayerData['Effects']:
                                            if (effect[0] == player):
                                                if (effect[1] == 'cc'):
                                                    for ccEffect in effect[3]:
                                                        if (ccEffect[1] == 'onhit' and ccEffect[2] == abilityName):
                                                            found = True
                                                            break
                                                elif (effect[1] == 'onhit' and effect[2] == abilityName):
                                                    found = True
                                                if (found):
                                                    dispel(effect,player,atkPlayerData)
                                                    atkPlayerData['Effects'].remove(effect)
                                                    if (effect in atkPlayerData['Concentration']):
                                                        atkPlayerData['Concentration'].remove(effect)
                                                    break
                    i += 1

            if (flurryOfBlows and lastAttack and not('openHandedTechnique' in usedAbilities) and not(killed) and 'oht' in atkPlayerData['Misc']):
                usedAbilities.append('openHandedTechnique')
                choice = DnDUtil.chooseOption('Choose an effect for Open Hand Technique',['Dex save or knocked prone','Str save or pushed 15 feet away','Can\'t take reactions until next turn'])
                if (choice == 1):
                    if (makeSave(creature,defCreatureData,'dex',atkPlayerData['SpellDC'],['prone']) > 0):
                        knockProne(creature,defCreatureData)
                elif (choice == 2):
                    if (makeSave(creature,defCreatureData,'str',atkPlayerData['SpellDC'],['push']) > 0):
                        print creature, "is knocked back 15 feet!"
                else:
                    defCreatureData['CanReact'] = False
                    atkPlayerData['Effects'].append([creature,'react',1.5])
                    print creature, "can't take reactions for a turn!"

            if (rangeIndex == 0 and not(killed) and 'thorns' in defCreatureData['Misc']):
                thornsArgs = defCreatureData['Misc']['thorns'].split(',')
                thornsDamageString = str(thornsArgs[0])
                thornsTypes = thornsArgs[1:]
                if (thornsDamageString.isdigit()):
                    thornsDamage = int(thornsDamageString)
                elif (not(battleRoyale)):
                    thornsDamage = DnDUtil.calculate(thornsDamageString)
                else:
                    thornsDamage = DnDUtil.getInt(raw_input('Roll for thorns damage ('+thornsDamageString+'): '))

                thornsDamage = getNetDamage(thornsDamage,defCreatureData,player,atkPlayerData,thornsTypes,'thorns',False)
                if (thornsDamage > 0):
                    if (thornsTypes):
                        primaryThornsType = thornsTypes[0]
                    else:
                        primaryThornsType = ''
                    print player, "takes", DnDUtil.getDamageText(thornsDamage), primaryThornsType, "damage from thorns!"
                    applyDamage(player,atkPlayerData,thornsDamage,thornsTypes,False)
                    updateDamageSummary(damageSummary,player,thornsDamage)

            if (killed or not(battleRoyale) and checkKilled(creature,defCreatureData,damage,weaponTypeData,crit)):
                print player, "has", DnDUtil.getDeathText('slain'), creature+'!'
                setDamageSummaryKilled(damageSummary,creature)
                if (not(killed)):
                    kill(creature)
                if (rangeIndex == 0 and ('gwm' in atkPlayerData['Misc'] or 'cleave' in atkPlayerData['Misc']) and not('cleave' in usedAbilities)):
                    print "Cleave activated!"
                    cleave = True
  
                if (rangeIndex == 0 and 'icleave' in atkPlayerData['Misc']):
                    print "Cleave activated!"
                    cleave = True
        else:
            print player, "misses", creature
            print player, "will need a roll of", defense - atkBonus, '('+str(defense)+')', "to hit", creature

        if (singleAttack):
            return damageSummary

        if (cleave):
            usedAbilties.append('cleave')
            maxAtks += 1
            j = 0
        elif (lastAttack and flurryOfBlows and not('flurryOfBlows' in usedAbilities)):
            usedAbilities.append('flurryOfBlows')
            maxAtks += 1
        else:
            j += 1
        usedAbilities.append('firstAttack')
        atkCount += 1

    if ('sm' in atkPlayerData['Misc'] and rangeIndex == 0):
        shoveTarget = ''
        while (shoveTarget == ''):
            input = raw_input('Input shove target for shield master (default - '+defaultCreature+'): ')
            if (input == 'done'):
                return damageSummary
            elif (input == ''):
                input = defaultCreature

            shoveTarget = autoComplete(input,not(battleRoyale))
            if (shoveTarget):
                shove(player,atkPlayerData,True,shoveTarget,getData(shoveTarget),battleRoyale)
            else:
                print "Invalid target -", input

    return damageSummary

def creatureAttack(creature,attackType,defaultPlayer,rangeIndex,atkIndex,singleAttack=False):

    # list containing the names of abilities or actions that have been used this round and should not be triggered again
    usedAbilities = []
    damageSummary = {}
    atkCreatureData = encounter[creature]

    if (rangeIndex >= len(atkCreatureData['Atk'])):
        DnDUtil.printError("No ranged attacks for this creature")
        return damageSummary

    if (atkIndex >= len(atkCreatureData['Atk'][rangeIndex])):
        DnDUtil.printError("No attack bonuses at index "+str(atkIndex)+" for this creature")
        return damageSummary

    if (singleAttack):
        maxAtks = 1
    else:
        maxAtks = len(atkCreatureData['Atk'][rangeIndex][atkIndex])
    
    # atk bonus index
    j = 0
    atkCount = 0
    while (atkCount < maxAtks):
        hit = False
        crit = False
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

        if (j == len(atkCreatureData['Atk'][rangeIndex][atkIndex])-1):
            lastAttack = True
        else:
            lastAttack = False

        # for every attack after the first, allow inputting of a new attack command
        if ('firstAttack' in usedAbilities):
            attackCommand = ['loop']
            while (attackCommand == ['loop']):
                attackCommand = DnDUtil.mySplit(raw_input('Input command for attack '+str(atkCount+1)+'/'+str(maxAtks)+' (default - '+attackType+' '+defaultPlayer+'): '),' ')
                if (attackCommand == ['done']):
                    return damageSummary
                numArgs = len(attackCommand)
                if (numArgs == 1):
                    if (attackCommand[0] in playerData):
                        defaultPlayer = attackCommand[0]
                    elif (isValidAttackType(attackCommand[0])):
                        attackType = attackCommand[0]
                    else:
                        print attackCommand[0], "is neither a player nor a valid attack command!"
                        attackCommand = ['loop']
                elif (numArgs == 2):
                    if (isValidAttackType(attackCommand[0])):
                        attackType = attackCommand[0]
                    else:
                        print "Invalid attack type", attackCommand[0]
                        attackCommand = ['loop']
                    if (attackCommand[1] in playerData):
                        defaultPlayer = attackCommand[1]
                    else:
                        print "Invalid attack target", attackCommand[1]
                        attackCommand = ['loop']
                elif (numArgs > 2):
                    print "Too many arguments given for this attack! There can only be a maximum of 2 attack arguments!"
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
            DnDUtil.printError("Invalid attack type "+attackType+" passed to creatureAttack function")
            return damageSummary

        player = chooseAttackTarget(creature,atkCreatureData,defaultPlayer,rangeIndex,atkIndex,j)
        # if this is a single attack, but our first attack is grabbing someone, look for another attack to use
        if (singleAttack and player != defaultPlayer):
            print creature, "is grabbing an opponent with this attack! Looking for another available attack..."
            for i in range(1,len(atkCreatureData['Atk'][rangeIndex][atkIndex])):
                player = chooseAttackTarget(creature,atkCreatureData,defaultPlayer,rangeIndex,atkIndex,i)
                if (player == defaultPlayer):
                    print "Another valid attack was found!"
                    j = i
                    break
            if (j == 0):
                print creature, "was unable to make an attack on", defaultPlayer
                return damageSummary

        defPlayerData = playerData[player]
        defense = getAC(defPlayerData)
        if (flank):
            if ('flank' in defPlayerData['Immunities']):
                print player, "is", DnDUtil.getFailText('immune'), "to being flanked!"
                flank = False
            elif ('iflank' in atkCreatureData['Misc']):
                dmgBonus = atkPlayerData['Misc']['iflank']

        attackAdvantage = getAttackAdvantage(creature,atkCreatureData,player,defPlayerData,rangeIndex == 0,not('spell' in atkCreatureData['WeaponTypes'][rangeIndex][atkIndex][j])) or advantage or flank
        attackDisadvantage = getAttackDisadvantage(atkCreatureData,player,defPlayerData,rangeIndex == 0,not('spell' in atkCreatureData['WeaponTypes'][rangeIndex][atkIndex][j])) or disadvantage
        atkBonus = atkCreatureData['Atk'][rangeIndex][atkIndex][j] + bonus
        roll = ActorUtil.makeRoll(creature,False,attackAdvantage,attackDisadvantage,atkBonus,False)
        attack = roll + atkBonus
        attack = ActorUtil.applyBlessBane(creature,atkCreatureData,attack,defense)

        if (not(checkTemporalShunt(creature,atkCreatureData,False))):
            return damageSummary
            
        if (applyMirrorImage(roll,attack,player,defPlayerData,True) and roll != 1 and (roll == 20 or attack >= defense)):
            if (roll != 20 and 'parry' in defPlayerData['Misc'] and rangeIndex == 0 and defense + defPlayerData['Misc']['parry'] > attack and ActorUtil.canReact(defPlayerData) and DnDUtil.getAnswer('Use '+player+'\'s reaction to parry') == 'y'):
                print player, "uses his/her reaction to parry the attack!"
                defPlayerData['Reaction'] = False
            elif (roll != 20 and 'ad' in defPlayerData['Misc'] and defense + 2 > attack and ActorUtil.canReact(defPlayerData) and DnDUtil.getAnswer('Use '+player+'\'s reaction to use arcane deflection') == 'y'):
                print player, "uses its reaction to use arcane deflection and negate the attack!"
                defPlayerData['Reaction'] = False
                applyCC(player,player,defPlayerData,'arcane deflection')
                defPlayerData['Effects'].append([player,'cc','arcane deflection',[],1.5])
            elif (roll != 20 and 'shield' in defPlayerData['UseAbilities'] and defense + 5 > attack and ActorUtil.canReact(defPlayerData) and DnDUtil.getAnswer('Use '+player+'\'s reaction to cast Shield') == 'y'):
                print player, "uses his/her reaction to cast Shield and block the attack!"
                defPlayerData['Reaction'] = False
                ability = defPlayerData['UseAbilities']['shield']
                useAbility(True,'shield',ability['Type'],ability['Duration'],ability['Actions'],True,[player],player,defPlayerData,player,defPlayerData,ability['Attack Mod'],ability['Save'],ability['DC'],0,ability['Base Level'],ability['Base Level'],False,False,False,ability['Concentration?'],{})
            else:
                hit = True
                critC = getCritStat(atkCreatureData,rangeIndex,atkIndex,j,0)
                damageData = atkCreatureData['Damage'][rangeIndex][atkIndex][j]
                dmgBonusData = atkCreatureData['DmgBonus'][rangeIndex][atkIndex][j]
                weaponTypes = atkCreatureData['WeaponTypes'][rangeIndex][atkIndex][j]
                
                if (roll >= critC or rangeIndex == 0 and ActorUtil.hasStatus(defPlayerData,['paralysis','sleep','unconscious'])):
                    if (not(ActorUtil.isImmuneToType(defPlayerData,['crit']))):
                        crit = True
                    else:
                        print player, "can't be", DnDUtil.getFailText('crit')+'!'

        if (hit):
            print creature, "successfully hits", player+'!'

            if (crit):
                print "This is a crit!"
                critMultiplier = getCritStat(atkCreatureData,rangeIndex,atkIndex,j,1)
                print "This attack's damage will be multiplied by", critMultiplier
                if (rangeIndex == 0 and 'gwm' in atkCreatureData['Misc'] and not('cleave' in usedAbilities)):
                    print "Cleave activated!"
                    cleave = True
                if ('bc' in atkCreatureData['Misc'] and rangeIndex == 0):
                    bcBonus = DnDUtil.calculate(atkCreatureData['Misc']['bc'])
                    print creature, "deals", bcBonus, "extra damage from brutal critical!"
                    dmgBonus += bcBonus
            else:
                critMultiplier = 1

            if ('ud' in defPlayerData['Misc'] and ActorUtil.canReact(defPlayerData) and DnDUtil.getAnswer('Use '+player+'\'s reaction to use uncanny dodge on this attack') == 'y'):
                uncannyDodge = True
                defPlayerData['Reaction'] = False

            weaponDamage = DnDUtil.calculate(damageData)

            if (ActorUtil.hasStatus(defPlayerData,['huntersmark']) and any(effect[0] == player and effect[1] == 'cc' and effect[2] == 'huntersmark' and effect[-1] == -1 for effect in atkCreatureData['Effects'])):
                huntersMarkDamage = DnDUtil.calculate('1d6')
                weaponDamage += huntersMarkDamage
                print creature, "deals an additional", huntersMarkDamage, "damage from hunter's mark!"

            damage = int(critMultiplier*weaponDamage) + dmgBonusData

            if (dmgBonus):
                if (isinstance(dmgBonus,int)):
                    damage += dmgBonus
                elif (dmgBonus.isdigit()):
                    damage += int(dmgBonus)
                else:
                    damage += int(DnDUtil.calculate(dmgBonus)*critMultiplier)

            if (damage < 0):
                damage = 0
            if (not('sneakAttack' in usedAbilities) and (sneakAttack or attackAdvantage and not(attackDisadvantage)) and 'sa' in atkCreatureData['Misc'] and not(ActorUtil.isImmuneToType(defPlayerData,['crit']))):
                usedAbilities.append('sneakAttack')
                parsedSneakAttackDamage = DnDUtil.parseDamageCalculation(atkCreatureData['Misc']['sa'])
                sneakAttackDamage = int(critMultiplier*DnDUtil.calculate(parsedSneakAttackDamage[0])) + parsedSneakAttackDamage[1]
                damage += sneakAttackDamage
                print player, "takes", sneakAttackDamage, "extra damage from sneak attack!"
                
            for playerType in defPlayerData['Type']:
                if (playerType in atkCreatureData['Misc']):
                    print creature, "deals bonus damage since", player, "is", playerType
                    if (atkCreatureData['Misc'][playerType].isdigit()):
                        damage += atkCreatureData['Misc'][playerType]
                    else:
                        damage += int(critMultiplier*DnDUtil.calculate(atkCreatureData['Misc'][playerType]))

            if (damage > 0):
                damage = getNetDamage(damage,atkCreatureData,player,defPlayerData,weaponTypes,'this attack',True,uncannyDodge)

                if ('ham' in defPlayerData['Misc'] and (weaponTypes and 'nonmagic' in weaponTypes or not(weaponTypes) and DnDUtil.getAnswer('Is this an attack from a magic weapon') == 'n')):
                    damage -= 3
                    if (damage < 0):
                        damage = 0

            if (ActorUtil.hasStatus(defPlayerData,['hex']) and any(effect[0] == player and effect[1] == 'cc' and effect[2] == 'hex' and effect[-1] == -1 for effect in atkCreatureData['Effects'])):
                hexDamage = int(getNetDamage(DnDUtil.calculate('1d6'),atkCreatureData,player,defPlayerData,['necrotic'],'hex',False)*critMultiplier)
                damage += hexDamage
                print creature, "deals an additional", DnDUtil.getDamageText(hexDamage), "necrotic damage from hex!"

            if (ActorUtil.hasStatus(atkCreatureData,['spiritshroud']) and (rangeIndex == 0 or DnDUtil.getAnswer('Is '+player+' within 10ft of '+creature) == 'y')):
                if (not('spiritshroudtype' in atkCreatureData['Misc'])):
                    DnDUtil.printWarning("Missing spiritshroudtype misc data in "+creature)
                elif (not('spiritshrouddamage' in atkCreatureData['Misc'])):
                    DnDUtil.printWarning("Missing spiritshrouddamage misc data in "+creature)
                else:
                    spiritShroudDamage = int(getNetDamage(DnDUtil.calculate(atkCreatureData['Misc']['spiritshrouddamage']),atkCreatureData,player,defPlayerData,[atkCreatureData['Misc']['spiritshroudtype']],'spiritshroud',False)*critMultiplier)
                    damage += spiritShroudDamage
                    if (spiritShroudDamage):
                        print creature, "deals an additional", DnDUtil.getDamageText(spiritShroudDamage), atkCreatureData['Misc']['spiritshroudtype'], "damage from spirit shroud!"
                        useAbility(False,'spirit shroud antiheal',[],1.5,[['immunity','heal']],True,[player],player,defPlayerData,creature,atkCreatureData,0,'',0,0,0,0,False,False,False,False,{})

            if (not('divineFury' in usedAbilities) and ('dfn' in atkCreatureData['Misc'] or 'dfr' in atkCreatureData['Misc']) and ActorUtil.hasStatus(atkCreatureData,['rage'])):
                usedAbilities.append('divineFury')
                if ('dfn' in atkCreatureData['Misc']):
                    dfKey = 'dfn'
                    damageType = 'necrotic'
                else:
                    dfKey = 'dfr'
                    damageType = 'radiant'
                dfDamage = int(getNetDamage(DnDUtil.calculate('1d6'),atkCreatureData,player,defPlayerData,[damageType],'divine fury',False)*critMultiplier)
                if (atkCreatureData['Misc'][dfKey]):
                    dfDamage += atkCreatureData['Misc'][dfKey]/2
                else:
                    dfDamage += atkCreatureData['CR']/2
                damage += dfDamage
                print creature, "deals an additional", DnDUtil.getDamageText(dfDamage), damageType, "damage from divine fury!" 

            if (rangeIndex == 1 and 'dm' in defPlayerData['Misc'] and ActorUtil.canReact(defPlayerData) and DnDUtil.getAnswer('Use your reaction to deflect missile') == 'y'):
                defPlayerData['Reaction'] = False
                if (damage > 0):
                    deflectDmgReduction = DnDUtil.getInt(raw_input('Roll for damage reduction (1d10): ')) + defPlayerData['Misc']['dm']
                    print "This attack's damage will be reduced by", deflectDmgReduction
                    damage -= deflectDmgReduction
                    if (damage < 0):
                        damage = 0
                if (damage == 0 and DnDUtil.getAnswer('Spend a ki point to attack with this missile') == 'y'):
                    deflectAttackTarget = ''
                    finished = False
                    while (not(finished)):
                        deflectAttackTarget = raw_input('Choose a target for this attack: ')
                        if (deflectAttackTarget == ''):
                            finished = True
                        else:
                            deflectAttackTarget = autoComplete(deflectAttackTarget,True)
                            if (deflectAttackTarget != ''):
                                finished = True
                    if (deflectAttackTarget != ''):
                        deflectAttackRoll = DnDUtil.getInt(raw_input('Roll for deflect attack: '))
                        deflectDamageSummary = playerAttack(player,'r',creature,deflectAttackRoll,False,1,0,True)
                        extendDamageSummary(damageSummary,deflectDamageSummary)
                        if (not(creature in encounter)):
                            return damageSummary

            if (weaponTypes):
                primaryWeaponType = weaponTypes[0]
            else:
                primaryWeaponType = ''
            print creature, "deals", DnDUtil.getDamageText(damage), primaryWeaponType, "damage to", player
            if (damage > 0):
                killed = applyDamage(player,defPlayerData,damage,weaponTypes,crit)
                updateDamageSummary(damageSummary,player,damage)
                if (killed):
                    setDamageSummaryKilled(damageSummary,player)
                    return damageSummary

            if (rangeIndex < len(atkCreatureData['OnHitAbilities']) and atkIndex < len(atkCreatureData['OnHitAbilities'][rangeIndex])):
                if (len(atkCreatureData['OnHitAbilities'][rangeIndex][atkIndex]) == 1):
                    onHitAbilities.append([creature+' On Hit Ability '+str(rangeIndex)+str(atkIndex)+str(j),atkCreatureData['OnHitAbilities'][rangeIndex][atkIndex][0]])
                elif (len(atkCreatureData['OnHitAbilities'][rangeIndex][atkIndex]) == len(atkCreatureData['Atk'][rangeIndex][atkIndex])):
                    onHitAbilities.append([creature+' On Hit Ability '+str(rangeIndex)+str(atkIndex)+str(j),atkCreatureData['OnHitAbilities'][rangeIndex][atkIndex][j]])
                else:
                    DnDUtil.printError("Invalid on hit abilities format")

            for onHitAbility,onHitAbilityData in atkCreatureData['ExtraOnHitAbilities'].items():
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
                    saveDC = ability['DC'] if ability['DC'] != 0 else atkCreatureData['SpellDC']
                    # don't perform any actions from this ability that would create effects already active from the attacker
                    for effect in atkCreatureData['Effects']:
                        if (effect[0] == player and effect[1] == 'cc' and effect[2] == abilityName):
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
                            elif (triggerCondition == 'kill'):
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
                            ohTypes = getOnHitTypes(atkCreatureData,rangeIndex,atkIndex,j)
                        else:
                            ohTypes = ability['Type']
                    if (success and ability['Save'] and ability['Save Result'] != 'none'):
                        saveDiff = makeSave(player,defPlayerData,ability['Save'],saveDC,ohTypes)
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
                        if (ActorUtil.isImmuneToType(defPlayerData,ohTypes)):
                            print player, "is", DnDUtil.getFailText('immune'), "to this on-hit ability!"
                        else:
                            if ('Base Level' in ability and 'Spell Level' in ability):
                                baseLevel = ability['Base Level']
                                spellLevel = ability['Spell Level']
                            else:
                                baseLevel = -1
                                spellLevel = -1
                            abilityDamageSummary = useAbility(False,abilityName,ohTypes,ability['Duration'],actionData,True,[player],player,defPlayerData,creature,atkCreatureData,0,ability['Save'],saveDC,saveDiff,baseLevel,spellLevel,half,crit,uncannyDodge,ability['Concentration?'],{})
                            extendDamageSummary(damageSummary,abilityDamageSummary)

                    if (triggerConditionSuccess):
                        if (ability['Charges'] != -1):
                            ability['Charges'] -= 1
                            if (ability['Charges'] == 0):
                                if (abilityName in atkCreatureData['ExtraOnHitAbilities']):
                                    print creature, "no longer has the on-hit ability", abilityName
                                    # since the effect that created this on-ability is very likely to reside in the attacker, it is worth it to check and try to remove it
                                    found = False
                                    for effect in atkCreatureData['Effects']:
                                        if (effect[0] == creature):
                                            if (effect[1] == 'cc'):
                                                for ccEffect in effect[3]:
                                                    if (ccEffect[1] == 'onhit' and ccEffect[2] == abilityName):
                                                        found = True
                                                        break
                                            elif (effect[1] == 'onhit' and effect[2] == abilityName):
                                                found = True
                                            if (found):
                                                dispel(effect,creature,atkCreatureData)
                                                atkCreatureData['Effects'].remove(effect)
                                                if (effect in atkCreatureData['Concentration']):
                                                    atkCreatureData['Concentration'].remove(effect)
                                                break
                i += 1

            if (flurryOfBlows and lastAttack and not('openHandedTechnique' in usedAbilities) and 'oht' in atkCreatureData['Misc']):
                usedAbilities.append('openHandedTechnique')
                choice = DnDUtil.chooseOption('Choose an effect for Open Hand Technique',['Dex save or knocked prone','Str save or pushed 15 feet away','Can\'t take reactions until next turn'])
                if (choice == 1):
                    if (makeSave(player,defPlayerData,'dex',atkCreatureData['SpellDC'],['prone']) > 0):
                        knockProne(player,defPlayerData)
                elif (choice == 2):
                    if (makeSave(player,defPlayerData,'str',atkCreatureData['SpellDC'],['push']) > 0):
                        print player, "is knocked back 15 feet!"
                else:
                    defPlayerData['CanReact'] = False
                    atkCreatureData['Effects'].append([player,'react',1.5])
                    print player, "can\'t take reactions for a turn!"

            if (rangeIndex == 0 and 'thorns' in defPlayerData['Misc']):
                thornsArgs = defPlayerData['Misc']['thorns'].split(',')
                thornsDamageString = str(thornsArgs[0])
                thornsTypes = thornsArgs[1:]
                if (thornsDamageString.isdigit()):
                    thornsDamage = int(thornsDamageString)
                else:
                    thornsDamage = DnDUtil.getInt(raw_input('Roll for thorns damage ('+thornsDamageString+'): '))

                thornsDamage = getNetDamage(thornsDamage,defPlayerData,creature,atkCreatureData,thornsTypes,'thorns',False)
                if (thornsDamage > 0):
                    if (thornsTypes):
                        primaryThornsType = thornsTypes[0]
                    else:
                        primaryThornsType = ''
                    print creature, "takes", DnDUtil.getDamageText(thornsDamage), primaryThornsType, "damage from thorns!"
                    applyDamage(creature,atkCreatureData,thornsDamage,thornsTypes,False)
                    updateDamageSummary(damageSummary,creature,thornsDamage)
                    dealDamage(atkCreatureData,thornsDamage)
                    if (checkKilled(creature,atkCreatureData,thornsDamage,thornsTypes,False)):
                        print creature, DnDUtil.getDeathText('dies'), "from thorns!"
                        kill(creature)
                        setDamageSummaryKilled(damageSummary,creature)
                        return damageSummary
        else:
            print creature, "misses", player
            print creature, "will need a roll of", defense - atkBonus, '('+str(defense)+')', "to hit", player

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

    if ('sm' in atkCreatureData['Misc'] and rangeIndex == 0):
        shoveTarget = ''
        while (shoveTarget == ''):
            input = raw_input('Input shove target for shield master (default - '+defaultPlayer+'): ')
            if (input == 'done'):
                return damageSummary
            elif (input == ''):
                input = defaultPlayer

            shoveTarget = autoComplete(input,False)
            if (shoveTarget):
                shove(creature,atkCreatureData,False,shoveTarget,getData(shoveTarget),True)
            else:
                print "Invalid target -", input
    
    return damageSummary