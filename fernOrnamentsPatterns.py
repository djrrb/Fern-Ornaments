import os
### 
# FERN Pattern Generator
# This script is meant to be run in drawbot
# https://www.drawbot.com
# https://github.com/justvanrossum/drawbot-skia (with some tweaks)

###################################
########## BASIC OPTIONS ##########
###################################

# define a constant width
baseWidth = 1000

# the number of cells for the main pattern
# note! this excludes prefixes and suffixes
cells = 16

# if we want to define separate x and y repeating cell values
cellsXY = cells, cells
# otherwise this will make them the same
#cellsXY = cells, cells

# name of the font
# this font should be installed, or you can replace 'Fern Ornaments' below with a relative or absolute path to the font file
# Fern ornaments can be purchased at https://djr.com/font-of-the-month-club#2021-06
fontPath = 'Fern Ornaments'

###################################
####### DEFINE THE PATTERNS #######
###################################

# QWERTY keyboard guide: https://djr.com/pdf/fern-djr-specimen.pdf
# Lowercase contains undotted variants
# ==================================
# Leaves, arcs, swoops, semicircles
# QWE     RT    YU      IOP # ASD     FG    HJ       L# ZXC     VB 
# qwe     rt    yu# a d     fg    hj  # zxc
# S or space = full space, s = half space
# asterisk (*) is a special charater that separates prefix and suffix from the main repeating section

patterns = [
"""
"""
]

# if the patterns list above is empty
# read all text files from a /patterns folder located next to this script 
if not patterns or patterns and not patterns[0].strip():
    patterns = []
    for filename in os.listdir('patterns'):
        if filename.endswith('.txt'):
            path = os.path.join(os.path.join(os.path.split(__file__)[0], 'patterns'), filename)
            with open(path) as myFile:
                patterns.append(myFile.read())

###################################
########## OTHER OPTIONS ##########
###################################

# define colors
background = 1,1,1 # r,g,b or r,g,b,a
foreground = 0,0,0 # r,g,b or r,g,b,a

# add a margin to the document
margin = baseWidth * .05

# do we want to convert the text to outlines
createOutlines = False

inDrawBot = 'BezierPath' in dir()
    

###################################
######## HELPER FUNCTIONS #########
###################################

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
            section.append(lineSegments) 
    # add any remainders
    if section:
        patternSections.append(section)
        
    # this script expects 3 sections: prefix, main, suffix. Handle situations where 
    if len(patternSections) == 1:
        patternSections = [[]] + patternSections + [[]]
    elif len(patternSections) == 2:
        patternSections.append([])
    return patternSections


def processLine(lineSegments):
    """Take a prefix, repeating segment, and suffix, and return the string for a single row"""
    prefix = lineSegments[0]
    suffix = lineSegments[-1]
    # get the number of cells we have to fill with the repeating pattern
    # by subtracting the prefix and suffix
    mainColCount = cellsXY[0]-len(prefix)-len(suffix)
    # get the repeating pattern
    mainCol = ''.join(lineSegments[1:-1])    # the main repeating pattern
    repeatsX = mainColCount // len(mainCol)     # repeats
    remainderX = mainColCount % len(mainCol) or 0
    # get the string for the line by adding the prefix, the repeats, the remainder, and the suffix
    lineString = prefix + mainCol*repeatsX + mainCol[:remainderX] + suffix
    # if necessary, clip it to the number of cells we want
    return lineString[:cellsXY[0]]

def drawPattern(patternString, createOutlines=False):
    # this takes a pattern and draws it
    # all of the drawbottery happens here
    theFontSize = baseWidth / cellsXY[0]
    baseHeight = cellsXY[1] * theFontSize
    
    # make a new page
    newPage(baseWidth+margin*2, baseHeight+margin*2)
    frameDuration(.75)
    # draw a background
    fill(*background)
    rect(0, 0, width(), height())
    # set the formatting
    fill(*foreground)
    fs = FormattedString(patternString, fontSize=theFontSize, lineHeight=theFontSize, font=fontPath)
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

# loop through our patterns
for pattern in patterns:
    # parse the text file into a list of sections
    patternSections = parsePattern(pattern)            
    # here’s an empty string where we will put our output
    patternString = ''
    # the first and last are the prefix and suffix
    rowprefix = patternSections[0]
    rowsuffix = patternSections[-1]
    # the number of rows that the repeating pattern needs to cover
    mainRowCount = cellsXY[1]-len(rowprefix)-len(rowsuffix)
    # we are assuming there is one main section, 
    # but if there is more than one, just mush them together
    mainRows = []
    for section in patternSections[1:-1]:
        for line in section:
            mainRows.append(line)
    # get the number of times that the main section need to repeat to fill the cells
    # and also if there is any partial section that needs to appear
    repeatsY = mainRowCount // len(mainRows)
    remainderY = mainRowCount % len(mainRows) or 0
    
    # process the prefix lines and add them to the output
    for line in rowprefix:
        patternString += processLine(line) + '\n'
        
    # repeat the main section, process each line, and add it to the output
    for rep in range(repeatsY):
        for lineSegments in mainRows:
            patternString += processLine(lineSegments) + '\n'
    # if the cells we have to fill is not equally divisible by our repeating section
    # add more lines to fill the space
    for remainderIndex in range(remainderY): 
        patternString += processLine(mainRows[remainderIndex]) + '\n'
            
    # process the suffix lines and add them to the output
    for line in rowsuffix:
        patternString += processLine(line) + '\n'
        
    # draw the output
    if inDrawBot:
        drawPattern(patternString, createOutlines=createOutlines)
    # print the results for easy copy/paste
    print(patternString+'\n')

# if we want to save the output, do it here
#saveImage('ornaments.gif')