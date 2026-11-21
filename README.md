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



### Non-Combat Commands

### Player-Exclusive Commands

### Casino Commands