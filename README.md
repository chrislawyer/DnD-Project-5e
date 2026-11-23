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

Below is documentation for every available command in the app along with a description and example of how to use it. Each of these descriptions is also available within the app using the 'help' command followed by the name of the command. Most commands have a shorthand to make typing them faster which, is denoted by a '/' in the usage line. For example, the "dropconcentration" command can also be executed by typing simply `dc`. Any word in the usage description enclosed in square brackets is a variable and any text enclosed in parenthesis is optional.

### Universal Commands

These commands can be used both inside and outside of combat.

#### help
Gives a short description of a command followed by usage information or lists all commands\
Usage: h/help ([command])\
Note: variables are enclosed in square breackets i.e. [command] and optional arguments are given in parenthesis i.e. ([command])

#### spell
Displays information on the given spell, pulled from the ability data table\
Usage: spell [spell name]

#### spelllist
Displays the list of spells that a given class can learn\
Usage: sl/spl/spelllist \[class](,[subclass]) ([spell level])\
Example 1: `sl druid` would print all spells available to druids\
Example 2: `sl rogue,arcanetrickster 1` would print all first level spells available to an arcane trickster rogue

#### open
Opens to the correct pdf page of the string given, including things such as creatures, classes, races, and spells, using additional optional arguments to narrow the search\
Usage: o/open \[string](,[searchArg1],[searchArgs2],...)\
Example: We want to reference the spell resurrection. We would type `open resurrection` and the player's handbook would open to the page containing the resurrection spell.\
Example 2: We want to reference the druid class, but not the creature named druid. We could either type `open druid,class` to specify we specifically want the druid class OR `open druid,phb` to specify that we want the druid from the player's handbook\
Note: This command requires some pdf reader, such as Acrobat Reader DC, to be installed\
Note 2: Additional bookmarks can be set using the 'Bookmark Data' file\
Note 3: If used during an encounter on a creature's turn, simply entering 'open' will try to open the bookmark for the current creature

#### roll
Simulates rolling dice and prints the total result\
Usage: roll ([number of rolls]d\[type of die](+[number of rolls]d[type of die]...))\
Note: the roll command will also accept whole integers as input\
Note 2: if no dice are given, it will roll 1d20\
Example: `roll 2d4+3` will roll a d4 twice, then add 3 and print the total

### Combat-Only Commands

These commands can only be used inside of a combat encounter.

#### jump
Jumps to the given actor's turn temporarily, then returns to the previous actor when the turn is over\
Usage: j/jump [actor]\
Note: If you want this jump to consume the actor's reaction, use react instead

#### react
Jumps to the given actor's turn temporarily, using that actor's reaction, then returns to the previous actor when the turn is over\
Usage: react [actor]\
Note: If you don't want this jump to consume the actor's reaction, use jump instead

#### same
Repeats the last stored action of the actor, asking for a reroll if needed (player weapon attacks only)\
Usage: s/same ([new roll])

#### skip
Skips the current player's turn\
Usage: skip\
Note: Empty input will also result in skip

#### display
Displays different information based on the argument given\
display hp - prints hp values of all creatures in the encounter\
display order - prints the initiative order, starting at the top\
display trigger - prints the stats of all active trigger abiities\
display stats - prints all stats of either the current actor or the given target argument\
display [stat] - prints the specific stat given of either the current actor or the given target\
Usage: d/display hp/order/trigger/stats/[stat] ([target])\
Note: This command can also be used outside of an encounter to check player stats (TODO: link to noncombat version)

#### move
Displays the movespeed of the current actor or given actor\
Usage: move ([target])

#### back
Returns to the previous actor's turn and restores all statuses\
Usage: b/back

#### melee
Executes a standard melee attack on the specified target\
Player Usage: m([attack index])/melee [target] [roll]\
Enemy Usage: m([attack index])/melee [target] (+/-[bonus])\
Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)

#### ranged
Executes a standard ranged attack on the specified target\
Player Usage: r([attack index])/ranged [target] [roll]\
Enemy Usage: r([attack index])/ranged [target] (+/-[bonus])\
Note: The attack index is used to indicate which ranged attack action should be performed if multiple are given (0 is the default index)

#### fob
Executes the monk's Flurry of Blows ability by adding an extra off-hand attack\
Player Usage: fb([attack index])/fob [target] [roll]\
Enemy Usage: fb([attack index])/fob [target]\
Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)

#### use
Uses the specified ability given in the creature or player data table on the specified targets\
Usage: u/use [ability] ([target],[target2]...)\
Note: targets are only optional for abilities that create a trigger\
Note 2: self, allies, enemies, and all are all valid targets\
Note 3: This command can also be used outside of combat to set up buffs before combat begins (TODO: link to noncombat version)

#### scroll
Uses the given ability from abilityData on the specified targets, assigning the Spell DC as appropriate for a spell scroll of that level\
Usage: scroll [ability] \[target](,[target2]...) ([dc bonus])\
Note: self, allies, enemies, and all are all valid targets

#### trigger
Triggers a stored ability designated as a trigger ability on the current actor or a target actor\
Usage: t/trigger [name] ([target])\
Note: in order for trigger to work, the trigger ability must have already been used by another character\
Example: druid2 has the use ability moonbeam. moonbeam is a trigger spell that we would activate whenever a creature enters the spell's area for the first time on a turn or starts its turn there, as per the description of the spell.\
First, we type `u moonbeam` (giving no target since it does not activate when cast) on druid2's turn to cast the spell, then, when any creature triggers the spell by walking into it on their turn or starting their turn in its area, we type `t moonbeam` to activate the spell on them, which forces them to make a con save or take 2d10 radiant damage, half on a success.\
Note 2: If we wanted to cast a trigger spell that can trigger immediately, such as spiritualwepaon, a target would be given on the initial cast.\
Note 3: 'self', 'allies', 'enemies', and 'all' are valid target names.

#### flank
Executes a melee attack from a flanking position, giving advantage on all attacks assuming the creature is not immune to being flanked\
Player Usage: flank([attack index]) [target] [roll]\
Enemy Usage: flank([attack index]) [target]\
Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)

#### recklessattack
Executes a reckless attack on target, giving advantage on all attacks for and against the actor for a turn\
Player Usage: ra([attack index])/recklessattack [target] [roll]\
Enemy Usage: ra([attack index])/recklessattack [target]\
Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)

#### am
Executes a melee attack with advantage\
Player Usage: am([attack index]) [target] [roll]\
Enemy Usage: am([attack index]) [target]\
Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)

#### ar
Executes a ranged attack with advantage\
Player Usage: ar([attack index]) [target] [roll]\
Enemy Usage: ar([attack index]) [target]\
Note: The attack index is used to indicate which ranged attack action should be performed if multiple are given (0 is the default index)

#### dm
Executes a melee attack with disadvantage\
Player Usage: dm([attack index]) [target] [roll]\
Enemy Usage: dm([attack index]) [target]\
Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)

#### dr
Executes a ranged attack with disadvantage\
Player Usage: dr([attack index]) [target] [roll]\
Enemy Usage: dr([attack index]) [target]\
Note: The attack index is used to indicate which ranged attack action should be performed if multiple are given (0 is the default index)

#### sneakattack
Executes a sneak attack on the target\
Player Usage: sa([attack index])/sneakattack [target] [roll]\
Enemy Usage: sa([attack index])/sneakattack [target]\
Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)\
Note 2: Only the first attack that hits will trigger the sneak attack damage as expected\
Note 3: in order to sneak attack with a ranged attack, use sar or sneakattackr instead

#### greatweaponmaster
Performs a great weapon master attack, giving the attacker -5 to hit and +10 to damage\
Player Usage: gwm([attack index])/greatweaponmaster [target] [roll]\
Enemy Usage: gwm([attack index])/greatweaponmaster [target]\
Note: The attack index is used to indicate which melee attack action should be performed if multiple are given (0 is the default index)

#### sharpshooter
Performs a sharpshooter attack, giving the attacker -5 to hit and +10 to damage\
Player Usage: ssr([attack index])/sharpshooter [target] [roll]\
Enemy Usage: ssr([attack index])/sharpshooter [target]\
Note: The attack index is used to indicate which ranged attack action should be performed if multiple are given (0 is the default index)

#### aoo
Allows another character to perform a melee attack on the current actor, used for attacks of opportunity\
Player Usage: aoo [attacker] [roll]\
Enemy Usage: aoo [attacker]

#### attack
Excutes an attack from one character to another out of turn order, might be used to check values or in rare cases of AoOs\
Player Usage: attack [player] [target] [roll]\
Enemy Usage: attack [enemy] [target]

#### damage
Deals damage to a creature or creatures out of turn order, used for hp adjustments and misc cases where damage should be dealt\
Usage: dmg/damage \[creature](,[creature2]...) [amount] ([type],[type2]...)\
Note: the types of the damage dealt can be specified at the end to apply immunities, vulnerabilities, and resistances

#### grapple
Used for making a grapple check with the target\
Usage: g/grapple [target]\
Note: this command can be used to start a grapple, make grapple checks, or escape a grapple

#### escape
Used to escape a grapple\
Usage: esc/escape\
Note: if the current actor is grappled by more than one enemy, you will be asked to choose which grapple to escape

#### aid
Executes the help combat maneuver, giving the target ally advantage on his/her next attack against a target enemy in their melee range\
Usage: aid [ally] [enemy]\
Note: the app actually gives advantage on the next attack regardless of the target. Try to remind the player to attack the target he/she has advantage on

#### dodge
Executes the dodge combat maneuver, giving the user advantage on dexterity saving throws and enemies disadvantage on their attacks made against the user for a turn\
Usage: dodge

#### shove
Executes the shove combat maneuver, allowing the actor to prone an enemy or push them back\
Usage: shove [target]

#### rage
Executes the barbarian's rage ability by giving them a damage bonus to their melee weapon attacks and resistance to bludgeoning, piercing, and slashing damage\
Usage: rage

#### dispel
Displays all active effects on a target and gives the option to remove any of them\
Usage: dispel \[target](,[target2]...)

#### turn
Used to Turn Undead on the given targets\
Usage: turn \[target](,[target2]...)

#### adv
Gives the target advantage on the specified check\
Usage: adv [target] [check type] ([duration])\
Example: `adv player1 con 3` would give player1 advantage on constitution checks for 3 turns

#### dis
Gives the target disadvantage on the specified check\
Usage: dis [target] [check type] ([duration])\
Example: `dis orc2 chasaves 5` would give orc2 disadvantage on charisma saving throws for 5 turns

#### dropconcentration
Dispels all effects that the given actor is currently concentrating on\
Usage: dc/dropconcentration ([target])\
Note: if no target is given, it will default to the current actor

#### buff
Gives a buff that lasts a specified number of rounds or until the end of the encounter\
Usage: buff [target] [stat] [amount] ([duration])\
Note: debuffs can be given by inputting a negative value for amount\
Note: the duration variable should be given in number of turns\
Note: the valid stat arguments are currently ac, str, dex, atk, dmg, hp, saves, strsave, dexsave, consave, intsave, wissave, chasave, and size

#### dot
Applies a DoT to the target\
Player Usage: dot [target] [damage] actor/target ([save type] [save DC] negates/half) ([damageType1],[damageType2]...) ([duration])\
Note: a calculation can be provided for the damage or duration\
Note 2: the fourth parameter indicates whether the DoT deals damage at the start of the DoT owner's turn (actor) or the DoT target's turn (target)

#### cc
Places a status effect on the target for a number of turns, and reminds the DM on that player's turn\
Usage: cc [target] [effect] ([duration])\
Note: if no duration is given, the effect will last until it is manually cleared\
Note 2: actorstart/actorend/targetstart/targetend are all valid durations meaning that at the start or end of the actor or target's next turn, the cc will expire

#### prone
Prones the given actor\
Usage: prone ([target])\
Note: the action can be undone using the stand command

#### stand
Makes the given actor stand up, removing the prone effect\
Usage: stand ([target])\
Note: this command has no effect on an actor that is not prone

#### heal
Heals a creature out of turn order, used for spells, potions, and misc cases\
Usage: heal \[creature](,[creature2]...) [amount]\
Note: on an enemy's turn, heal will accept an equation such as 1d8+3 as the amount argument

#### kill
Instantly kills a creature or player, removing it from the encounter\
Usage: kill \[target](,[target2]...)

#### add
Adds allies or enemies to the encounter\
Usage: add/adda/adde [creature] [number]\
Note: use 'adda' to add allies and 'adde' to add enemies

#### mindcontrol
Simulates a mindcontrol, turning a player into a creature or a creature into a player\
Usage: mc/mindcontrol [target] ([duration])

#### shapeshift
Simulates a shapeshift by replacing the creature's current data  with that of another creature type\
Usage: ss/shapeshift [creature] ([duration])

#### abilities
Prints the "Abilities Info" cell of the given creature from the creature data table or print all use abilities of a player\
Usage: a/abilities ([target])\
Note: if no target is given, it will attempt to display the abilities of the current actor

#### sethp
Sets a creature's hp to the given value\
Usage: sethp [creature] [new hp]

#### addtemphp
Adds a given number of temporary hit points to the given creature\
Usage: addtemphp [creature] [temp hp]\
Note: This will give temporary hit point regradless or whether the creature previously had temporary hp

#### str
Makes a strength save for every target given, but the targets must be all players or all enemies\
Player Usage: str \[target](,[target2]...) \[roll](,[roll2]...)\
Enemy Usage: str \[target](,[target2]...)

#### dex
Makes a dexterity save for every target given, but the targets must be all players or all enemies\
Player Usage: dex \[target](,[target2]...) \[roll](,[roll2]...)\
Enemy Usage: dex \[target](,[target2]...)

#### con
Makes a constitution save for every target given, but the targets must be all players or all enemies\
Player Usage: con \[target](,[target2]...) \[roll](,[roll2]...)\
Enemy Usage: con \[target](,[target2]...)

#### int
Makes an intelligence save for every target given, but the targets must be all players or all enemies\
Player Usage: int \[target](,[target2]...) \[roll](,[roll2]...)\
Enemy Usage: int \[target](,[target2]...)

#### wis
Makes a wisdom save for every target given, but the targets must be all players or all enemies\
Player Usage: wis \[target](,[target2]...) \[roll](,[roll2]...)\
Enemy Usage: wis \[target](,[target2]...)

#### cha
Makes a charisma save for every target given, but the targets must be all players or all enemies\
Player Usage: cha \[target](,[target2]...) \[roll](,[roll2]...)\
Enemy Usage: cha \[target](,[target2]...)

#### addmisc
Adds a miscellaneous stat with the given argument to the given target (or targets)\
Usage: addmisc \[target](,[target2]...) [stat] ([argument])\
Example: `addmisc orc1,orc2,skeleton1 parry 2` would give orc1, orc2, and skeleton1 the parry ability, grating +2 AC when used

#### editmisc
Edits a miscellaneous stat, replacing its argument with the given argument on the given target (or targets)\
Usage: editmisc \[target](,[target2]...) [stat] [argument]\
Example: `editmisc veteran1,veteran2 parry 4` would change captain1 and captain2's parry arguments to 4 (assuming they had the parry ability)

#### delmisc
Deletes a miscellaneous stat from the given target (or targets)\
Usage: delmisc \[target](,[target2]..) [stat]\
Example: `delmisc zombie1,zombie2 uf` would remove zombie1 and zombie2's undead fortitude ability

#### done
Instantly ends the encounter\
Usage: done

### Non-Combat Commands

These commands can only be used outside of a combat encounter.

#### test
Loads the test encounter from the test encounter file\
Usage: test

#### player
Initiates player mode, loading the given characters from the character data table\
Usage: player ([player name1],[player name2],...)\
Note: if no players are given, it will prompt the user to enter character names

#### casino
Initiates casino mode, allowing access the casino games\
Usage: casino

#### load
Loads an encounter or battle royale from the encounter file\
Usage: load encounter/battleroyale\
Note: this command is useful for recovering an encounter that was lost due to ending the session or an unexpected crash

#### create
Creates an encounter, a blacksmith, or magic shop\
Usage: create encounter/blacksmith/magicshop ([size])\
Note: blacksmith and magic shop take an extra argument - size; the valid inputs for size are small, medium, and large

#### battleroyale
Creates a battle royale encounter, which means there are no enemy creatures and the players are expecting to fight amongst themselves\
Usage: br/battleroyale

#### random
Prints a random item from the given class from the class data file\
Usage: random [class]

#### encounter
Generates a list of potential encounters for the given environment using either a random or user-given difficulty\
Usage: e/encounter [environment]\
Note: urban is also a valid environment, with its own special rules for generating an encounter

#### auto
Automatically generates an encounter using the given creatures and a random or given difficulty\
Usage: auto \[creature1](,[creature2]...)\
Note: you will be able to choose out of a list of valid encounters

#### loot
Prints a random loot item based on the given roll and loot data table\
Usage: loot [roll]

#### info
Prints detailed information about an armor or weapon\
Usage: info [weapon/armor]

#### hit
Used with 'box' to generate a random item with better odds of receiving higher-tier items and items with enchantments\
Usage: hit box

#### weather
Generates a random weather condition based on the table in the Dungeon Master's Guide\
Usage: weather

#### setlvls
Overrides the average level of the party, number of players in the party, and exp thresholds of the party, affecting the loot drops, items available in shops, and generated encounters\
Usage: setlvls [level1](,[level2],...)\
Example: `setlvls 2,2,3` would set up a party consisting of two level 2s and one level 3

#### find
Displays all creatures that meet the given parameters\
Usage: find/search [parameter1],[value1] ([parameter2],[value2])...\
Example 1: `find cr,4` would print all creatures with a cr of 4\
Example 2: `find ac,>20` would print all creatures with an ac of at least 20\
Example 3: `find cr,2,3 environment,hills,plains` would print all creatures found in hills or plains that have a cr of 2 or 3\
Example 4: `find environment,forest cr,>3 type,beast,fey` would print all beasts or fey creatures found in the forest that have at least 3 cr

#### addparty
Adds a new party member to the player file from the creature file and updates the app with the new party member's data\
Usage: addparty/addp [creature]

#### format
Launches the format help section to give information about how to format player and creature data\
Usage: format ([field])\
Note: the optional field argument will have the app display information about the specific field given

#### display
Displays one or all of a given player's stats\
display stats - prints all stats of the given player\
display [stat] - prints the specific stat given of the given player\
Usage: d/display stats/[stat] [player]\
Note: This command can also be used inside of an encounter to check various encounter information (TODO: link to combat version)

#### use
Uses the player's specified ability on the specified targets\
Usage: u/use [ability] ([target],[target2]...)\
Note: targets are only optional for abilities that create a trigger\
Note 2: This command can also be used inside of combat (TODO: link to combat version)

### Player-Exclusive Commands

### Casino Commands