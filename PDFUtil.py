import subprocess
import csv
import DnDUtil

USE_2024_RULES = False

PDF_READER_EXE_FILE = "C:\\Program Files\\Adobe\\Acrobat DC\\Acrobat\\Acrobat.exe"
PDF_RULES_PATH = "C:\\Users\\Fya Masta\\Documents\\Chris Lawyer\\DnD\\5\\Rules and References\\"
PDF_ADVENTURES_PATH = "C:\\Users\\Fya Masta\\Documents\\Chris Lawyer\\DnD\\5\\Adventures\\"
PDF_2024_PATH = "2024 Core Books\\"
BOOKMARK_FILE = "Bookmark Data 2024.csv" if USE_2024_RULES else "Bookmark Data.csv"
PHB_FILE = "Player's Handbook.pdf"
DMG_FILE = "Dungeon Master's Guide.pdf"
MM_FILE = "Monster Manual.pdf"
XGE_FILE = "Xanathar's Guide To Everything.pdf"
VGM_FILE = "Volo's Guide To Monsters.pdf"
GGR_FILE = "Guildmasters' Guide To Ravnica.pdf"
MTF_FILE = "Mordenkainen's Tome of Foes.pdf"
SCAG_FILE = "Sword Coast Adventurer's Guide.pdf"
TCE_FILE = "Tasha's Cauldron of Everything.pdf"
EGW_FILE = "Explorer's Guide to Wildemount.pdf"
BH_FILE = "Blood Hunter 2020.pdf"
FTD_FILE = "Fizban's Treasury of Dragons.pdf"
MOM_FILE = "Monsters of the Multiverse.pdf"
SXH_FILE = "Strixhaven.pdf"
BOF_FILE = "Book of Fiends.pdf"
DIA_FILE = "Descent Into Avernus.pdf"

def openBookmark(searchArgs):

    searchArgs = searchArgs.split(',')
    searchName = searchArgs.pop(0)
    fileName = ''
    pageNum = ''
    if (searchName.isdigit()):
        if (len(searchArgs) == 1):
            # adding 1 to offset the cover page
            pageNum = str(int(searchName)+1)
            fileName = getFileName(searchArgs[0])
        else:
            print("Page number must be followed only by the file name acronym!")
            return
    else:
        bookmarkFile = open(BOOKMARK_FILE, 'r', encoding='utf-8', newline='')
        csvBookmarkReader = csv.reader(bookmarkFile)
        header = next(csvBookmarkReader)
        numHeaderColumns = len(header)

        try:
            nameIndex = header.index('Name')
            typeIndex = header.index('Type')
            fileIndex = header.index('File')
            pageIndex = header.index('Page')
            extraIndex = header.index('Extra')
        except ValueError:
            DnDUtil.printError("Missing data column in bookmark file "+BOOKMARK_FILE+"! Required columns are 'Name', 'Type', 'File', 'Page', and 'Extra'")
            return

        results = []
        for row in csvBookmarkReader:
            try:
                if (searchName in row[nameIndex] and all((searchArg in row or searchArg in DnDUtil.mySplit(row[extraIndex],',')) for searchArg in searchArgs)):
                    if (len(row) == numHeaderColumns):
                        results.append(row)
                    else:
                        DnDUtil.printError("Not enough data columns for row "+str(row)+"! Expected "+str(numHeaderColumns)+" columns, but only "+str(len(row))+" were found for this row")
            except IndexError:
                DnDUtil.printError("Not enough data columns for row "+str(row)+"! Expected "+str(numHeaderColumns)+" columns, but only "+str(len(row))+" were found for this row")

        bookmarkFile.close()
    
        if (len(results) == 0):
            argsString = searchName
            for searchArg in searchArgs:
                argsString += " AND "+searchArg
            print("Could not find any bookmarks containing", argsString+'!')
            return
        exactMatches = [result for result in results if result[nameIndex] == searchName]
        if (len(exactMatches) == 1):
            row = exactMatches[0]
        else:
            choice = DnDUtil.chooseOption('Choose which bookmark to open',getResultStrings(results,nameIndex,typeIndex,fileIndex,pageIndex,extraIndex),True)
            if (choice > len(results)):
                return
            row = results[choice-1]
        
        fileName = getFileName(row[fileIndex])
        pageNum = row[pageIndex]
        if (not(pageNum.isdigit())):
            DnDUtil.printError("The page number is not an integer for bookmark "+row[nameIndex])

    if (fileName and pageNum):
        openPDFToPage(fileName,pageNum)

def openPDFToPage(fileName,pageNum):

    subprocess.Popen([PDF_READER_EXE_FILE, '/n', '/A', 'page='+pageNum, fileName], shell=False, stdout=subprocess.PIPE)

def getFileName(file):

    if (file == 'phb'):
        return PDF_RULES_PATH + PDF_2024_PATH + PHB_FILE if USE_2024_RULES else PDF_RULES_PATH + PHB_FILE
    elif (file == 'dmg'):
        return PDF_RULES_PATH + PDF_2024_PATH + DMG_FILE if USE_2024_RULES else PDF_RULES_PATH + DMG_FILE
    elif (file == 'mm'):
        return PDF_RULES_PATH + PDF_2024_PATH + MM_FILE if USE_2024_RULES else PDF_RULES_PATH + MM_FILE
    elif (file == 'xge'):
        return PDF_RULES_PATH + XGE_FILE
    elif (file == 'vgm'):
        return PDF_RULES_PATH + VGM_FILE
    elif (file == 'ggr'):
        return PDF_RULES_PATH + GGR_FILE
    elif (file == 'mtf'):
        return PDF_RULES_PATH + MTF_FILE
    elif (file == 'scag'):
        return PDF_RULES_PATH + SCAG_FILE
    elif (file == 'tce'):
        return PDF_RULES_PATH + TCE_FILE
    elif (file == 'egw'):
        return PDF_RULES_PATH + EGW_FILE
    elif (file == 'bh'):
        return PDF_RULES_PATH + BH_FILE
    elif (file == 'ftd'):
        return PDF_RULES_PATH + FTD_FILE
    elif (file == 'mom'):
        return PDF_RULES_PATH + MOM_FILE
    elif (file == 'sxh'):
        return PDF_RULES_PATH + SXH_FILE
    elif (file == 'bof'):
        return PDF_RULES_PATH + BOF_FILE
    elif (file == 'dia'):
        return PDF_ADVENTURES_PATH + DIA_FILE
    else:
        DnDUtil.printError("Unrecognized file abbreviation "+file)
        return ''

def getResultStrings(results,nameIndex,typeIndex,fileIndex,pageIndex,extraIndex):

    resultStrings = []
    for result in results:
        resultString = result[nameIndex]+" ("+result[typeIndex]+") - "+result[fileIndex]+" "+result[pageIndex]
        if (result[extraIndex]):
            resultString += ' ('+result[extraIndex]+')'
        resultStrings.append(resultString)
    return resultStrings