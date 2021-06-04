import os
import math

### 
# FERN Pattern Generator
# This script is meant to be run in drawbot
# https://www.drawbot.com
# https://github.com/justvanrossum/drawbot-skia (with some tweaks)
#
# The Fern Ornaments font should be installed
# or a relative path to the font can # be set in the fontPath variable
# 
# User guide: https://github.com/djrrb/fern-ornaments
# More about Fern: https://djr.com/notes/junes-font-of-the-month-fern-text
# Purchase Fern: https://djr.com/font-of-the-month-club#2021-06

# QWERTY keyboard guide: https://djr.com/pdf/fern-djr-specimen.pdf
# Lowercase contains undotted variants
# ==================================
# Leaves, arcs, swoops, semicircles
# QWE     RT    YU      IOP # ASD     FG    HJ       L# ZXC     VB 
# qwe     rt    yu# a d     fg    hj  # zxc
# S or space = full space, s = half space
# asterisk (*) is a special charater that separates prefix and suffix from the main repeating section

###################################
####### DEFINE THE PATTERNS #######
###################################
patterns = [
"""
q*w
av*x
adS*O
*
adi*yh
adi*uj
adi*yh
adi*ju
"""
]
fontPath = 'Fern Ornaments'
# define a constant width
baseWidth = 1000
# the number of cells for the main pattern
# in drawbot, cmd + ← ↑ → ↓ to change values
cellsX, cellsY = 14, 23
# make the entire pattern symmetrical?
totalXSymmetry, totalYSymmetry = True, True
# add symmetry to the main section
localXSymmetry, localYSymmetry = True, True
# define colors (r,g,b or r,g,b,a)
backgroundColor = 0, .5, 0
foregroundColor = 1, 1, 1
# add a margin to the document
margin = baseWidth * .05

# test to see if we are in drawbot and should draw the results
# otherwise just return plaintext
inDrawBot = 'BezierPath' in dir()
# convert the text to outlines?
createOutlines = False

# if the patterns list above is empty
# read all text files from a /patterns folder located next to this script 

###################################
############ CONSTANTS ############
###################################

# if no patterns are set, read from the patterns list
def getPatternsFromFolder(path):
    patterns = []
    for filename in os.listdir(path):
        if filename.endswith('.txt'):
            path = os.path.join(os.path.join(os.path.split(__file__)[0], 'patterns'), filename)
            with open(path) as myFile:
                patterns.append(myFile.read())
    return patterns
if not patterns or patterns and not patterns[0].strip():
    patterns = getPatternsFromFolder('patterns')
    
# these dictionaries 
xSymmetryMap = {
    'Q': 'E', 'A': 'D', 'Z': 'C', 'q': 'e', 'a': 'd', 'z': 'c',
    'R': 'T', 'F': 'G', 'r': 't', 'f': 'g',
    'Y': 'U', 'H': 'J', 'y': 'u', 'h': 'j',
    'I': 'P', 'B': 'V', 'i': 'p', 'b': 'v'
    }
ySymmetryMap = {
    'Q': 'Z', 'W': 'X', 'E': 'C', 'q': 'z', 'w': 'x', 'e': 'c',
    'R': 'F', 'T': 'G', 'r': 'f', 't': 'g',
    'Y': 'U', 'H': 'J', 'y': 'u', 'h': 'j',
    'O': 'L', 'B': 'V', 'o': 'l', 'b': 'v'
    }
# add reverse
xSymmetryMap.update({v: k for k, v in xSymmetryMap.items()})
ySymmetryMap.update({v: k for k, v in ySymmetryMap.items()})

###################################
######## HELPER FUNCTIONS #########
###################################

def getSymmetry(line, symmetryMap):
    output = ''
    for char in line:
        if char in symmetryMap:
            output += symmetryMap[char]
        else:
            output += char
    return output



def parsePattern(pattern):
    """Take a pattern string and turn it into a matrix"""
    # [ 
    #    [colprefix] * [main] * [colsuffix], # rowprefix
    #    [colprefix] * [main] * [colsuffix], # main
    #    [colprefix] * [main] * [colsuffix], # rowsuffix
    # ]
    
    # split a pattern into lines and add each line to a section
    lines = pattern.strip().split('\n')
    patternSections = []
    section = []
    for line in lines:
        line = line.strip()
        # if a line starts with an asterisk, then make a new section
        if line[0] == '*':
            patternSections.append(section)
            section  = []
        else:
            lineSegments = line.split('*')
            if len(lineSegments) == 1:
                lineSegments = [''] + lineSegments + ['']
            elif len(lineSegments) == 2:
                lineSegments.append('')
            if localXSymmetry:
                for lineIndex, lineSegment in enumerate(lineSegments):
                    if lineIndex != 0 and lineIndex != len(lineSegments)-1:
                        lineSegments[lineIndex] = lineSegment + getSymmetry(lineSegment[::-1], xSymmetryMap)
            section.append(lineSegments) 
    # add any remainders
    if section:
        patternSections.append(section)
        
    # this script expects 3 sections: prefix, main, suffix. 
    # Handle situations where this is not the case
    if len(patternSections) == 1:
        patternSections = [[]] + patternSections + [[]]
    elif len(patternSections) == 2:
        patternSections.append([])
    elif len(patternSections) > 3:
        mainLines = []
        for patternSection in patternSections[1:-1]:
            for line in patternSection:
                mainLines.append(line)
        patternSections = [patternSections[0], mainLines, patternSections[-1]]
        
    if localYSymmetry:
        reverseMain = patternSections[1][:]
        reverseMain.reverse()
        newLines = []
        for line in reverseMain:
            newLines.append([line[0], getSymmetry(line[1], ySymmetryMap), line[2]])
            
        patternSections[1] += newLines
        
    return patternSections


def processLine(lineSegments):
    """Take a prefix, repeating segment, and suffix, and return the string for a single row"""
    prefix = lineSegments[0]
    suffix = lineSegments[-1]
    if totalXSymmetry:
        # if have symmetry, override any suffix with a flip of the prefix
        suffix = getSymmetry(prefix[::-1], xSymmetryMap)
    # get the number of cells we have to fill with the repeating pattern
    # by subtracting the prefix and suffix
    mainColCount = cellsX-len(prefix)-len(suffix)
    # get the repeating pattern
    mainCol = ''.join(lineSegments[1:-1])    # the main repeating pattern

    repeatsX = math.ceil(mainColCount / len(mainCol))     # repeats
    # if we are doing symmetry, cut the number of repeats in half
    if totalXSymmetry:
        repeatsX = math.ceil(repeatsX/2)
    # get the main content by repeating the base string
    mainContent = mainCol*repeatsX
    # deal with the remainder
    if totalXSymmetry:
        # duplicate the main content, this will be the flipped half
        mainContentReversed = mainContent[:]
        # this might be an overly elaborate way to do this
        # but deal with the remainder by alternating between
        # the content and flipped content, removing a character
        # at a time until we get the length we want
        flip = 0
        while len(mainContent) + len(mainContentReversed) > mainColCount:
            if flip == 1:
                mainContent = mainContent[:-1]
                flip = 0
            else:
                mainContentReversed = mainContentReversed[:-1]
                flip = 1
        # add the base half and flipped half together
        main = mainContent + getSymmetry(mainContentReversed[::-1], xSymmetryMap)
    else:
        # otherwise, just trim the content to the desired length
        main = mainContent[:mainColCount]
    
    # add in the prefix and suffix
    lineString = prefix + main + suffix
    return lineString[:cellsX]

def getPatternString(patternSections):
    """Take the list of pattern sections and turn them into a string."""
    # here’s an empty string where we will put our output
    patternString = ''
    # the first and last are the prefix and suffix
    rowprefix = patternSections[0]
    rowsuffix = patternSections[-1]
    # if symmetry is on, override the suffix with a flip of the prefix
    if totalYSymmetry:
        rowsuffix = rowprefix[:]
        rowsuffix.reverse()
    # process the prefix lines and add them to the output
    for line in rowprefix:
        patternString += processLine(line) + '\n'

    
    mainRowCount = cellsY-len(rowprefix)-len(rowsuffix)
    # we are assuming there is one main section, 
    # but if there is more than one, just mush them together
    mainRows = []
    for section in patternSections[1:-1]:
        for line in section:
            mainRows.append(line)
    # get the number of times that the main section need to repeat to fill the cells
    # and also if there is any partial section that needs to appear
    repeatsY = math.ceil(mainRowCount / len(mainRows))
    if totalYSymmetry:
        repeatsY = math.ceil(repeatsY/2)
    lines = []
    for rep in range(repeatsY):
        for lineSegments in mainRows:
            lines.append( processLine(lineSegments) )
        
    if totalYSymmetry:
        linesReversed = lines[:]
        flip = 1
        while len(lines) + len(linesReversed) > mainRowCount:
            if flip == 1:
                lines = lines[:-1]
                flip = 0
            else:
                linesReversed = linesReversed[:-1]
                flip = 1
        linesReversed.reverse()
    else:
        lines = lines[:mainRowCount]
    for line in lines:
        patternString += line + '\n'
    if totalYSymmetry:
        for line in linesReversed:
            patternString += getSymmetry(line, ySymmetryMap) + '\n'
    
    # process the suffix lines and add them to the output
    for line in rowsuffix:
        lineString = processLine(line) + '\n'
        if totalYSymmetry:
            lineString = getSymmetry(lineString, ySymmetryMap)
        patternString += lineString
   
    return patternString

def drawPattern(patternString, createOutlines=False):
    # this takes a pattern and draws it
    # all of the drawbottery happens here
    theFontSize = baseWidth / cellsX
    baseHeight = cellsY * theFontSize
    # make a new page
    newPage(baseWidth+margin*2, baseHeight+margin*2)
    frameDuration(.75)
    # draw a background
    fill(*backgroundColor)
    rect(0, 0, width(), height())
    # set the formatting
    fs = FormattedString(patternString, fontSize=theFontSize, lineHeight=theFontSize, font=fontPath, fill=foregroundColor)
    # draw the text box
    if createOutlines:
        bp = BezierPath()
        bp.textBox(fs, (margin, margin-fontDescender()/2, baseWidth, baseHeight))
        drawPath(bp)
    else:
        textBox(fs, (margin, margin-fontDescender()/2, baseWidth, baseHeight))

###################################
####### NOW RUN EVERYTHING ########
###################################

if __name__ == "__main__":
    # loop through our patterns
    for pattern in patterns:
        # parse the text file into a list of sections
        patternSections = parsePattern(pattern)            
        patternString = getPatternString(patternSections)
        # draw the output if in drawbot
        if inDrawBot:
            drawPattern(patternString, createOutlines=createOutlines)
            print(f'{width()} x {height()}')
        # print the results for easy copy/paste
        print(patternString+'\n')

    # if we want to save the output, do it here
    #saveImage('ornaments.gif')