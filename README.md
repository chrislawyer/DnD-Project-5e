# D&D 5E All-in-One App

## Introduction

This is a personal passion project created by me in 2012 for my D&D sessions to help automate and track some of the more tedious aspects of combat to keep the game running at a faster pace. Over the years, I have added an enormous number of features beyond just combat functionality, and I continue to use it on a weekly basis to this day. The app has been built and optimized around my own personal use, prioritizing very fast inputting and executing of commands. As such, this app does not have a UI, and instead operates like a console, executing commands the user inputs via keyboard. It was also designed with remote play in mind as my group has been playing exclusively online for years.

## Main Features

- run combat [Details](#running-combat)
- save between sessions [Details](#saving-encounter)
- all data stored in csv files [Details](#data-files)
- generate random encounters [Details](#generating-a-random-encounter)
- generate random loot [Details](#random-loot-generation)
- player functions [Details](#using-the-app-as-a-player)
- bookmarks [Details](#opening-a-bookmark)
- random misc tables [Details](#rolling-on-custom-random-tables)
- casino games [Details](#casino-games)
- documentation [Details](#documentation)

### Running Combat

### Saving Encounters

### Data Files

### Generating a Random Encounter

### Random Loot Generation

### Using the App as a Player

### Opening a Bookmark

Using the 'open' (or 'o') command, it is possible to search for any bookmark that has been defined in "Bookmark Data.csv" which will open the bookmark's source PDF to the page specified. This command requires Adobe Acrobat Reader to be installed on your machine, as well as your own digital copies of the PDFs. There are currently over 2000 bookmarks covering every class, subclass, spell, feat, creature, item, race, and other important sections across 16 different PDFs. For example, typing the command `open skeleton` will open the monster manual to the page where the skeleton's stat block resides. Additionally, each bookmark contains data that includes its type, sourcebook, or any other relavant categorizations relating to its type such as spell school for spells, item rarity for items, or source class for subclasses. For instance, the command `open ,item,veryrare` will present a list of every very rare item and give the option to open the PDF page of any of them.

### Rolling on Custom Random Tables

The 'random' command will return a random item from the given list "Class Data.csv". There are currently 120 random tables ranging from NPCs traits, urban encounters, taverns, and traps to various loot items such as enchantments, potions, gems, ans valuable art pieces. For example, `random feat` will return a random feat and `random spell5` will return a random 5th level spell. The loot system and a number of other commands that generate various random things make heavy use of the lists in this file. 

### Casino Games

Typing the command 'casino' will open the casino section of the app. Hitting the enter key or entering the commands 'done' or 'leave' will return to the main section of the app.

This app currently has 8 casino-style games that can be run to entertain the players should they have the desire to do some gambling:
- Roulette
- High-Low
- Slots
- 21 (dice-based blackjack)
- Gyp (a variation of craps)
- Dragon's Hoard
- Hand of Fate
- Faerun Keep 'Em (dice-based texas hold 'em)

Detailed descriptions of the games can be found in the help documentation, or by using the 'help' command along with the name of the game. The three table games that have rounds of betting and secret rolls to simulate cards (Dragon's Hoard, Hand of Fate, and Faerun Keep 'Em), have a similar set of features such as random NPC generation to fill the table, the ability to gain or conceal information with Insight and Deception checks respectively, and a set of commands for raising, folding, calling, checking the pot, adding or removing NPCs to the table, and seeing who is at the table. The DM controls the NPC's betting decisions. The app automatically tracks whose turn it is to bet, how much is required to be bet to continue playing the hand, what players are still active in the hand, the money in the pot, and which player has the winning hand.

## Documentation

Below is a documentation for every available command in the app along with a description and example of how to use it. Each of these descriptions is also available within the app using the 'help' command followed by the name of the command.

### Combat Commands

#### jump
jump - Jumps to the given actor temporarily, then returns to the previous actor
Usage: j/jump [actor]
Note: If you want this jump to consume the actor's reaction, use react instead

#### react
react - Jumps to the given actor temporarily, using that actor's reaction, then returns to the previous actor
Usage: react [actor]
Note: If you don't want this jump to consume the actor's reaction, use jump instead

#### same
same - repeats the last stored action of the actor, asking for a reroll if needed (player weapon attacks only)
Usage: s/same ([new roll])

#### skip
skip - skips the current player's turn
Usage: skip
Note: Empty input will also result in skip

#### display
display - displays different things based on the argument given
display hp - prints hp values of all creatures in the encounter
display order - prints the initiative order starting at the beginning
display trigger - prints the stats of all active trigger abiities
display stats - prints all stats of either the actor or the given target argument
display [stat] - prints the specific stat given of either the actor or the given target
Usage: d/display hp/order/trigger/stats/[stat] ([target])
Note: This command can also be used outside of an encounter to check player stats

#### move
move - displays the movespeed of the current actor or given actor
Usage: move ([target])

#### spell
spell - displays information on the given spell, pulled from the ability data table
Usage: spell [spell name]
Note: This command can also be used outside of an encounter

#### spelllist
spelllist - displays the list of spells that a given class can learn
Usage: sl/spl/spelllist [class](,[subclass]) ([spell level])
Example 1: sl druid would print all spells available to druids
Example 2: sl rogue,arcanetrickster 1 would print all first level spells available to an arcane trickster rogue
Note: This command can also be used outside of combat

#### open
open - opens to the correct pdf page of the string given, including things such as creatures, classes, races, and spells, using additional optional arguments to narrow the search
Usage: o/open [string](,[searchArg1],[searchArgs2],...)
Example: We want to reference the spell resurrection. We would type 'open resurrection' and the player's handbook would open to the page containing the resurrection spell.
Example 2: We want to reference the druid class, but not the creature named druid. We could either type 'open druid,class' to specify the class OR 'open druid,phb' to specify that we want the druid from the player's handbook
Note: This command can also be used outside of an encounter
Note 2: This command requires some pdf reader, such as Acrobat Reader DC, to be installed
Note 3: Additional bookmarks can be set using the 'Bookmark Data' file
Note 4: If used during an encounter on a creature's turn, simply entering 'open' will try to open the bookmark for the current creature

#### back
back - returns to the previous actor and restores all statuses
Usage: b/back

#### melee
melee - executes a standard melee attack on the specified target
Player Usage: m([attack index])/melee [target] [roll]
Enemy Usage: m([attack index])/melee [target] (+/-[bonus])
Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)

#### ranged
ranged - executes a standard ranged attack on the specified target
Player Usage: r([attack index])/ranged [target] [roll]
Enemy Usage: r([attack index])/ranged [target] (+/-[bonus])
Note: The attack index is used to indicate which ranged attack action should be performed if multiple are given (0 is the default index)

#### fob
fob - simulates flurry of blows
Player Usage: fb([attack index])/fob [target] [roll]
Enemy Usage: fb([attack index])/fob [target]
Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)

#### use
use - uses the specified ability given in the creature data table on the specified targets
Usage: u/use [ability] ([target],[target2]...)
Note: targets are only optional for abilities that create a trigger
Note 2: self, allies, enemies, and all are all valid targets
Note 3: This command can also be used outside of combat

#### scroll
scroll - uses the given ability from abilityData on the specified targets
Usage: scroll [ability] [target](,[target2]...) ([dc bonus])
Note: self, allies, enemies, and all are all valid targets

#### trigger
trigger - triggers a stored ability designated as a trigger ability on the current actor or a target actor
Usage: t/trigger [name] ([target])
Note: in order for trigger to work, the trigger ability must have already been used by another character
Example: druid2 has the use ability fshield. fshield is a trigger spell that we would use when anyone attacks druid2 with fshield active.
First, we use fshield (giving an invalid target so as not to damage any characters) on druid2's turn to cast the spell, then when anyone attacks druid2 while fshield is on, we type 'trigger fshield' to apply the fshield's damage to the attacker
Note 2: if we wanted to cast a trigger spell that can trigger immediately, such as fwall, proper targets would be given on the initial cast.
Note 3: 'self', 'allies', 'enemies', and 'all' are valid target names.

#### flank
flank - executes a melee attack from a flanking position
Player Usage: flank([attack index]) [target] [roll]
Enemy Usage: flank([attack index]) [target]
Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)

#### recklessattack
recklessattack - executes a reckless attack on target, giving advantage on all attacks for and against the actor for a turn
Player Usage: ra([attack index])/recklessattack [target] [roll]
Enemy Usage: ra([attack index])/recklessattack [target]
Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)

#### am
am - executes a melee attack with advantage
Player Usage: am([attack index]) [target] [roll]
Enemy Usage: am([attack index]) [target]
Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)

#### ar
ar - executes a ranged attack with advantage
Player Usage: ar([attack index]) [target] [roll]
Enemy Usage: ar([attack index]) [target]
Note: The attack index is used to indicate which ranged attack action should be performed if multiple are given (0 is the default index)

#### dm
dm - executes a melee attack with disadvantage
Player Usage: dm([attack index]) [target] [roll]
Enemy Usage: dm([attack index]) [target]
Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)

#### dr
dr - executes a ranged attack with disadvantage
Player Usage: dr([attack index]) [target] [roll]
Enemy Usage: dr([attack index]) [target]
Note: The attack index is used to indicate which ranged attack action should be performed if multiple are given (0 is the default index)

#### sneakattack
sneakattack - executes a sneak attack on the target
Player Usage: sa([attack index])/sneakattack [target] [roll]
Enemy Usage: sa([attack index])/sneakattack [target]
Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)
Note 2: in order to sneak attack with a ranged attack, use sar or sneakattackr instead

#### greatweaponmaster
greatweaponmaster - performs a great weapon master attack, giving the attacker -5 to hit and +10 to damage
Player Usage: gwm([attack index])/greatweaponmaster [target] [roll]
Enemy Usage: gwm([attack index])/greatweaponmaster [target]
Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)

#### sharpshooter
sharpshooter - performs a sharpshooter attack, giving the attacker -5 to hit and +10 to damage
Player Usage: ssr([attack index])/sharpshooter [target] [roll]
Enemy Usage: ssr([attack index])/sharpshooter [target]
Note: The attack index is used to indicate which ranged attack action should be performed if multiple are given (0 is the default index)

#### aoo
aoo - allows another character to perform a melee attack on the current actor, used for attacks of opportunity
Player Usage: aoo [attacker] [roll]
Enemy Usage: aoo [attacker]

#### attack
attack - when all else fails, allows someone to make an attack out of turn order, might be used to check values or rare cases of AoOs
Player Usage: attack [player] [target] [roll]
Enemy Usage: attack [enemy] [target]

#### damage
damage - deals damage to a creature or creatures out of turn order, used for hp adjustments and misc cases
Usage: dmg/damage [creature](,[creature2]...) [amount] ([type],[type2]...)
Note: the types of the damage dealt can be specified at the end to apply immunities, vulnerabilities, and resistances

#### roll
roll - simulates rolling dice and prints the total result
Usage: roll ([number of rolls]d[type of die](+[number of rolls]d[type of die]...))
Note: the roll command will also accept whole integers as input
Note 2: this command can also be used outside of combat
Note 3: if no dice are given, it will roll 1d20
Example: roll 2d4+3 will roll a d4 twice, then add 3 and print the total

#### grapple
grapple - used for making grapple check with the target
Usage: g/grapple [target]
Note: this command can be used to start a grapple, make grapple checks, and escape a grapple

#### escape
escape - used to escape a grapple
Usage: esc/escape
Note: if the current actor is grappled by more than one enemy, you will be asked to choose which grapple to escape

#### aid
aid - executes the help combat maneuver, giving the target ally advantage on his/her next attack against a target enemy in your melee range
Usage: aid [ally] [enemy]
Note: the program actually gives advantage on the next attack regardless of the target. Try to remind the player to attack the target he/she has advantage on

#### dodge
dodge - executes the dodge combat maneuver, giving the user advantage on dexterity saving throws and enemies disadvantages on their attacks made against the user for a turn
Usage: dodge

#### shove
shove - executes the shove combat maneuver, allowing the actor to prone an enemy or push them back
Usage: shove [target]

#### rage
rage - simulates the barbarian's rage ability
Usage: rage

#### dispel
dispel - gives the DM the option to remove any effects on the target
Usage: dispel [target](,[target2]...)

#### turn
turn - used to Turn Undead on the given targets
Usage: turn [target](,[target2]...)

#### adv
advantage - gives the target advantage on the specified check
Usage: adv [target] [check type] ([duration])
Example: adv player1 con 3 would give player1 advantage on constitution checks for 3 turns

#### dis
disadvantage - gives the target disadvantage on the specified check
Usage: dis [target] [check type] ([duration])
Example: dis orc2 chasaves 5 would give orc2 disadvantage on charisma saving throws for 5 turns

#### dropconcentration
dropconcentration - dispels all effects that the given actor is currently concentrating on
Usage: dc/dropconcentration ([target])
Note: if no target is given, it will default to the current actor

#### buff
buff - gives a buff that lasts a specified number of rounds or until the end of the encounter
Usage: buff [target] [stat] [amount] ([duration])
Note: debuffs can be given by inputting a negative value for amount
Note: the duration variable should be given in number of turns
Note: the valid [stat] arguments are currently ac, str, dex, atk, dmg, hp, saves, strsave, dexsave, consave, intsave, wissave, chasave, and size

#### dot
dot - applies a DoT to the target
Player Usage: dot [target] [damage] actor/target ([save type] [save DC] negates/half) ([damageType1],[damageType2]...) ([duration])
Note: a calculation can be provided for the damage or duration
Note: the fourth parameter indicates whether the DoT deals damage at the start of the DoT owner's turn (actor) or the DoT target's turn (target)

#### cc
cc - places a status effect on the target for a number of turns, and reminds the DM on that player's turn
Usage: cc [target] [effect] ([duration])
Note: if no duration is given, the effect will last until it is manually cleared
Note: actorstart/actorend/targetstart/targetend are all valid durations meaning that at the start or end of the actor or target's next turn, the cc will expire

#### prone
prone - Prones the given actor
Usage: prone ([target])
Note: the action can be undone using the stand command

#### stand
stand - Stands the given actor, removing the prone effect
Usage: stand ([target])
Note: this command has no effect on an actor that is not prone

#### heal
heal - heals a creature out of turn order, used for spells, potions, and misc cases
Usage: heal [creature](,[creature2]...) [amount]
Note: on an enemy's turn, heal will accept an equation such as 1d8+3 as the amount argument

#### kill
kill - instantly kills a creature or player, removing it from the encounter
Usage: kill [target](,[target2]...)

#### add
add - adds allies or enemies to the encounter
Usage: add/adda/adde [creature] [number]
Note: use adda to add allies and adde to add enemies

#### mindcontrol
mindcontrol - simulates a mindcontrol, turning a player into a creature and a creature into an enemy
Usage: mc/mindcontrol [target] ([duration])

#### shapeshift
shapeshift - simulates a shapeshift by replacing a creature's current data  with that of another creature type
Usage: ss/shapeshift [creature] ([duration])

#### abilities
abilities - prints the abilities cell of the given creature from the creature data table or print all use abilities of a player
Usage: a/abilities ([target])
Note: if no target is given, it will attempt to display the abilities of the current actor

#### sethp
sethp - sets a creature's hp to the given value, useful for recovering from crashes and errors
Usage: sethp [creature] [new hp]

#### addtemphp
addtemphp - Adds a given number of temporary hit points to the given creature
Usage: addtemphp [creature] [temp hp]
Note: This will give temporary hit point regradless or whether the creature previously had temporary hp

#### str
str - makes a strength save for every target given, but the targets must be all players or all enemies
Player Usage: str [target](,[target2]...) [roll](,[roll2]...)
Enemy Usage: str [target](,[target2]...)

#### dex
dex - makes a dexterity save for every target given, but the targets must be all players or all enemies
Player Usage: dex [target](,[target2]...) [roll](,[roll2]...)
Enemy Usage: dex [target](,[target2]...)

#### con
con - makes a constitution save for every target given, but the targets must be all players or all enemies
Player Usage: con [target](,[target2]...) [roll](,[roll2]...)
Enemy Usage: con [target](,[target2]...)

#### int
int - makes a intelligence save for every target given, but the targets must be all players or all enemies
Player Usage: int [target](,[target2]...) [roll](,[roll2]...)
Enemy Usage: int [target](,[target2]...)

#### wis
wis - makes a wisdom save for every target given, but the targets must be all players or all enemies
Player Usage: wis [target](,[target2]...) [roll](,[roll2]...)
Enemy Usage: wis [target](,[target2]...)

#### cha
cha - makes a charisma save for every target given, but the targets must be all players or all enemies
Player Usage: cha [target](,[target2]...) [roll](,[roll2]...)
Enemy Usage: cha [target](,[target2]...)

#### addmisc
addmisc - Adds a miscellaneous stat with the given argument to the given target (or targets)
Usage: addmisc [target](,[target2]...) [stat] ([argument])
Example: addmisc orc1,orc2,skeleton1 parry 2 would give orc1, orc2, and skeleton1 the parry ability, grating +2 AC when used

#### editmisc
editmisc - Edits a miscellaneous stat, replacing its argument with the given argument on the given target (or targets)
Usage: editmisc [target](,[target2]...) [stat] [argument]
Example: editmisc veteran1,veteran2 parry 4 would change captain1 and captain2's parry arguments to 4 (assuming they had the parry ability)

#### delmisc
delmisc - Deletes a miscellaneous stat from the given target (or targets)
Usage: delmisc [target](,[target2]..) [stat]
Example: delmisc zombie1,zombie2 uf would remove zombie1 and zombie2's undead fortitude ability

#### done
done - instantly ends the encounter
Usage: done

#### help
help - gives a short description of a command followed by usage information or lists all commands
Usage: h/help ([command])
Note: variables are enclosed in braces i.e. [command] and optional arguments are given in parenthesis i.e. ([command])

### Non-Combat Commands

### Player-Exclusive Commands

### Casino Commands