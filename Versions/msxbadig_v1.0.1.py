"""


MSX Basic Dignified
v1.0.1
Converts modern typed MSX Basic to native format.

Copyright (C) 2019 - Fred Rique (farique) https://github.com/farique1

Better experienced with Basic.sublime-syntax and MSX Basic.tmThem
https://github.com/farique1/msx-basic-dignified/tree/master/SublimeTools

msxbadig.py <source> <destination> [args...]
msxbadig.py -h for help.

New: Conformmed to PEP-8 (sorta)
"""

import re
import argparse
import ConfigParser

# Config
fileeLad = '/Users/Farique/Documents/Dev/Change-Graph-Kit/CGK-Source.bas'       # Source file
fileeSve = '/Users/Farique/desktop/msx projects/msxdsk1/cgk-clas.bas'       # Destination file
linesSrt = 10       # Start line number
linesStp = 10       # Line step amount
leadgZro = False    # Add leading zeros
colonBef = 0        # Number of spaces before :
colonAft = 0        # Number of spaces after :
shortSpc = 1        # Strip all general spaces to this amount
keeppSpc = False    # Keep original spaces format
blankLns = False    # Keep blank lines using REM
remrkBfr = False    # Add blank REM line before label
remrkAft = False    # Add blank REM line after label
labelShw = False    # Show labels on lines with branching instructions
labelLin = 0        # Handle label lines: 0-label_name 1-REM_only 2-delete
remrkLbl = "s"      # Labels REM format: s-single_quote
remrkReg = "s"      # General REM format: s-single_quote
remrkChg = False    # Convert all REMs
identKep = False    # Keep indentation
idtspKep = False    # Keep space characters on indents
identSze = 2        # Number of spaces per TAB on indentation
cptlzAll = True     # Capitalize
cnvrtPrt = False    # Convert ? to PRINT
thngtStp = 'k'      # Strip adjacent THEN/ELSE or GOTO: t-THEN/ELSE g-GOTO

# Variables
lineNo = []     # Line numbers
idntSz = []     # Indent sizes
lablNa = []     # Label names
lablNo = []     # Label line numbers
quotLb = []     # Original quotes
remkLb = []     # Original comments
dataLb = []     # Original data
lbleLb = []     # Original labels
lbleRm = []     # Branchong label REMs
verbos = 2      # Show processing status: 0-no 1-headers 2-errors 3-details
firstL = ' Refactored with MSX Basic Dignified'

# Set .ini file (if used and active overwites built in settings)
config = ConfigParser.ConfigParser()
config.sections()
config.read('msxbadig.ini')
if config.read('msxbadig.ini') and config.getboolean('DEFAULT', 'Use_Ini_File'):
    fileeLad = config.get('DEFAULT', 'Source_File')
    fileeSve = config.get('DEFAULT', 'Destin_File')
    linesSrt = config.getint('DEFAULT', 'Line_Start')
    linesStp = config.getint('DEFAULT', 'Line_Step')
    leadgZro = config.getboolean('DEFAULT', 'Leading_Zeros')
    colonBef = config.getint('DEFAULT', 'Nnbr_Spaces_Bef_Colon')
    colonAft = config.getint('DEFAULT', 'Nnbr_Spaces_Aft_Colon')
    shortSpc = config.getint('DEFAULT', 'Nmbr_Spaces_General')
    keeppSpc = config.getboolean('DEFAULT', 'Keep_Original_Spaces')
    blankLns = config.getboolean('DEFAULT', 'Keep_Blank_Lines')
    remrkBfr = config.getboolean('DEFAULT', 'REM_Bef_Label')
    remrkAft = config.getboolean('DEFAULT', 'REM_Aft_Label')
    labelShw = config.getboolean('DEFAULT', 'Show_Branches_Labels')
    labelLin = config.getint('DEFAULT', 'Handle_Label_Lines')
    remrkLbl = config.get('DEFAULT', 'Label_REM_Format')
    remrkReg = config.get('DEFAULT', 'Regul_REM_Format')
    remrkChg = config.getboolean('DEFAULT', 'Convert_REM_Formats')
    identKep = config.getboolean('DEFAULT', 'Keep_Indent')
    idtspKep = config.getboolean('DEFAULT', 'Keep_Indent_Space_Chars')
    identSze = config.getint('DEFAULT', 'Indent_TAB_Spaces')
    cptlzAll = config.getboolean('DEFAULT', 'Capitalize_All')
    cnvrtPrt = config.getboolean('DEFAULT', 'Convert_Interr_To_Print')
    thngtStp = config.get('DEFAULT', 'Strip_Then_Goto')
    verbos = config.get('DEFAULT', 'Verbose_Level')

# Set command line (if used overwites previous settings)
parser = argparse.ArgumentParser(description='Converts modern typed MSX Basic to native format')
parser.add_argument("input", nargs='?', default=fileeLad, help='Source file')
parser.add_argument("output", nargs='?', default=fileeSve, help='Destination file ([source]_) if missing')
parser.add_argument("-ls", default=linesSrt, type=int, help='Starting line (def 10)')
parser.add_argument("-lp", default=linesStp, type=int, help='Line steps (def 10)')
parser.add_argument("-lz", default=leadgZro, action='store_true', help='Leading zeros on line numbers')
parser.add_argument("-bc", default=colonBef, type=int, help="Spaces before ':' (def 0)")
parser.add_argument("-ac", default=colonAft, type=int, help="Spaces after ':' (def 0)")
parser.add_argument("-gs", default=shortSpc, type=int, help='General spacing (def 1)')
parser.add_argument("-ks", default=keeppSpc, action='store_true', help='Keep original spacing')
parser.add_argument("-bl", default=blankLns, action='store_true', help='Keep blank lines as REM lines')
parser.add_argument("-br", default=remrkBfr, action='store_true', help='Add REM line before labels')
parser.add_argument("-ar", default=remrkAft, action='store_true', help='Add REM line after labels')
parser.add_argument("-sl", default=labelShw, action='store_true', help='Show labels on lines with branching commands')
parser.add_argument("-ll", default=labelLin, type=int, choices=[0, 1, 2], help="Handle label lines: 0-label_name(def) 1-REM_only 2-delete")
parser.add_argument("-lr", default=remrkLbl, choices=["s", 'S', 'rem', 'REM'], help="Labels REM format: s-single_quote (def s)")
parser.add_argument("-rr", default=remrkReg, choices=["s", 'S', 'rem', 'REM'], help="Regular REM format: s-single_quote (def rem)")
parser.add_argument("-cr", default=remrkChg, action='store_true', help='Convert existing REMs')
parser.add_argument("-ki", default=identKep, action='store_true', help='Keep indent')
parser.add_argument("-ci", default=idtspKep, action='store_true', help='Keep indent space characters')
parser.add_argument("-si", default=identSze, type=int, help='Spaces per TAB on indents (def 2)')
parser.add_argument("-nc", default=cptlzAll, action='store_false', help='Do not capitalize')
parser.add_argument("-cp", default=cnvrtPrt, action='store_true', help='Convert ? to PRINT')
parser.add_argument("-tg", default=thngtStp, choices=['t', 'T', 'g', 'G', 'k', 'K'], help="Remove adjacent THEN/ELSE or GOTO: t-THEN/ELSE g-GOTO k-keep_all(def)")
parser.add_argument("-vb", default=verbos, type=int, choices=[0, 1, 2, 3], help="Verbosity level: 0-silent 1-steps 2-errors(def) 3-details")
parser.add_argument("-ini", action='store_true', help="Create msxbadig.ini")
args = parser.parse_args()

# Write .ini file if told to
if args.ini:
    config.set('DEFAULT', 'Use_Ini_File', 'True')
    config.set('DEFAULT', 'Source_File', fileeLad)
    config.set('DEFAULT', 'Destin_File', fileeSve)
    config.set('DEFAULT', 'Line_Start', linesSrt)
    config.set('DEFAULT', 'Line_Step', linesStp)
    config.set('DEFAULT', 'Leading_Zeros', leadgZro)
    config.set('DEFAULT', 'Nnbr_Spaces_Bef_Colon', colonBef)
    config.set('DEFAULT', 'Nnbr_Spaces_Aft_Colon', colonAft)
    config.set('DEFAULT', 'Nmbr_Spaces_General', shortSpc)
    config.set('DEFAULT', 'Keep_Original_Spaces', keeppSpc)
    config.set('DEFAULT', 'Keep_Blank_Lines', blankLns)
    config.set('DEFAULT', 'REM_Bef_Label', remrkBfr)
    config.set('DEFAULT', 'REM_Aft_Label', remrkAft)
    config.set('DEFAULT', 'Show_Branches_Labels', labelShw)
    config.set('DEFAULT', 'Handle_Label_Lines', labelLin)
    config.set('DEFAULT', 'Label_REM_Format', remrkLbl)
    config.set('DEFAULT', 'Regul_REM_Format', remrkReg)
    config.set('DEFAULT', 'Convert_REM_Formats', remrkChg)
    config.set('DEFAULT', 'Keep_Indent', identKep)
    config.set('DEFAULT', 'Keep_Indent_Space_Chars', idtspKep)
    config.set('DEFAULT', 'Indent_TAB_Spaces', identSze)
    config.set('DEFAULT', 'Capitalize_All', cptlzAll)
    config.set('DEFAULT', 'Convert_Interr_To_Print', cnvrtPrt)
    config.set('DEFAULT', 'Strip_Then_Goto', thngtStp)
    config.set('DEFAULT', 'Verbose_Level', verbos)
    with open('msxbadig.ini', 'wb') as configfile:
        config.write(configfile)
    raise SystemExit(0)

# Apply chosen settings
fileeLad = args.input
fileeSve = args.output
if args.output == '':
    fileeSve = re.sub(r'(.*)\.(.*)', r'\_.\2', fileeLad)
linesSrt = abs(args.ls)
linesStp = abs(args.lp)
leadgZro = args.lz
colonBef = ' ' * args.bc
colonAft = ' ' * args.ac
shortSpc = ' ' * args.gs
keeppSpc = args.ks
blankLns = args.bl
remrkBfr = args.br
remrkAft = args.ar
labelShw = args.sl
remrkLbl = args.lr
labelLin = args.ll
if remrkLbl.upper() == 'S':
    remrkLbl = "'"
remrkReg = args.rr
if remrkReg.upper() == 'S':
    remrkReg = "'"
remrkChg = args.cr
identKep = args.ki
idtspKep = args.ci
identSze = args.si
cptlzAll = args.nc
cnvrtPrt = args.cp
thngtStp = args.tg.upper()
verbos = args.vb

# If there is a file to be oppened after all this
if fileeLad:
    with open(fileeLad, 'r') as f:
        array = f.readlines()
else:
    parser.error('Source file not found')
    raise SystemExit(0)


# Just a little breath
if verbos > 0:
    print


if verbos > 0:
    print '--- remove lone ## and ENDIFs'

array[:] = [c for c in array if not re.match(r'(^.*endif.*$|^\s*##.*$)', c, re.IGNORECASE)]


if verbos > 0:
    print '--- remove endline ## and trailing spaces'

# Not removing ## if there are quotes after
array[:] = [re.sub(r'(?![^"]*")(?<!,)##.*', '', c).rstrip() + '\n' for c in array]
# array[:] = [re.sub(r'##.*".*".*$', '', c).rstrip()+'\n' for c in array]
# works with quotes after ## but do not work with two sets of quotes


if verbos > 0:
    print '--- delete or REMark blank lines and convert existing REMs'

if remrkChg:
    array[:] = [re.sub(r"(^|.*:)\s*?(rem|')", r'\1' + remrkReg, c) for c in array]

if blankLns:
    array[:] = [re.sub(r'(^\s*$)', remrkReg, c) for c in array]
else:
    array[:] = [c for c in array if not re.match(r'(^\s*$)', c)]


if verbos > 0:
    print '--- join lines with _ and :'

prev = ''
arrayB = []

for item in array:

    if re.match(r'.*(:|_)$', prev) or re.match(r'^\s*:', item):
        prev = re.sub(r'( *)\s*_$', r'\1', prev) + re.sub(r'^\s*', '', item).rstrip()
    else:
        arrayB.append(prev)
        prev = item.rstrip()

arrayB.append(prev)
arrayB[0] = remrkReg + firstL
array = arrayB


if verbos > 0:
    print '--- add line before and after label'

# Only if using REMs as label
if labelLin < 2:
    arrayB = []

    for item in array:
        label = re.match(r'(^\s*{.+?})', item)

        if label and remrkBfr:
            arrayB.append(remrkLbl)
        arrayB.append(item)

        if label and remrkAft:
            arrayB.append(remrkLbl)

    array = arrayB


if verbos > 0:
    print '--- remove and replace defines and [?@]'
# Get define name

defnLb = ['[' + re.findall(r'\[([^\]]*)\]', c)[0] + ']' for c in array if re.match(r'^\s*define', c)]

# Get define content
defnCt = [re.findall(r'\[([^\]]*)\]', c)[1] for c in array if re.match(r'^\s*define', c)]

array[:] = [c for c in array if not re.match(r'^\s*define', c)]

# Make [?@] become LOCATE:PRINT
array[:] = [re.sub(r'(\[\?@\])(\d+,\d+)', r'locate' + shortSpc + r'\2:print', c) for c in array]

for defLabl, defCont in zip(defnLb, defnCt):
    array[:] = [c.replace(defLabl, defCont) for c in array]

    if verbos > 2:
        print defLabl, ':', defCont

# If a define still remais (could not be replaced)
if verbos > 1:
    defnAl = [re.findall(r'\[([^\]]*)\]', c) for c in array]
    defnAl[:] = [item for sublist in defnAl for item in sublist]
    defnAl[:] = list(set(defnAl))

    for item in defnAl:
        itemBracket = '[' + item + ']'

        if itemBracket not in defnLb:
            print '> define not found', '[' + item + ']'

# Store items that should remain unchanged
if verbos > 0:
    print '--- save REMs, DATAs and quotes'

qotNmbr = 0  # Quotes number place marker
remNmbr = 0  # REMs number place marker
datNmbr = 0  # DATAs number place marker

for c, _ in enumerate(array):
    remark = re.findall(r'(^|:)\s*(\'|rem)(.*$)', array[c], re.IGNORECASE)
    # remark = re.findall(r'((^|:)\s*\'|(^|:)\s*rem)(.*$)', array[c], re.IGNORECASE))

    if remark:

        for item in remark:
            remkLb.append(item[2])
            array[c] = array[c].replace(item[1] + str(item[2]), item[1] + str(remNmbr))

            remNmbr += 1

    data = re.findall(r'(^|:)\s*data(.*?(?=:|$))', array[c])

    if data:

        for item in data:
            # print item[1]
            dataLb.append(item[1])
            array[c] = array[c].replace(str(item[1]), str(datNmbr))
            datNmbr += 1

    quotes = re.findall(r'\"([^\"]*)\"', array[c])  # r"(\"[^\"]+\"|"  capt with quotes

    if quotes:

        for item in quotes:
            quotLb.append(item)
            array[c] = array[c].replace('"' + item + '"', '"' + str(qotNmbr) + '"')
            qotNmbr += 1


if verbos > 0:
    print '--- get line numbers, indent sizes and label positions'

arrayB = []
digNmb = 0  # Line number digits

if leadgZro:
    # Find the biggest line number
    digNmb = linesSrt + ((len(array) - 1) * linesStp)
    # Get its lenght
    digNmb = len(str(digNmb))

for item in array:
    addLine = True
    linha = item
    # If it is a label
    label = re.match(r'(^\s*{.+?})', item)

    # Save its line number
    if label:
        lablNa.append(label.group(1).lstrip())
        lablNo.append(linesSrt)

        # Is using REMs as label?
        if labelLin == 1:
            linha = remrkLbl
        elif labelLin == 2:
            addLine = False

    if addLine:
        arrayB.append(linha)
        lineNo.append(str(linesSrt).zfill(digNmb))
        linesSrt += linesStp

    ident = re.match(r'(^\s*)\S', item)
    # print ident.group(1).replace('\t', 't').replace(' ', 's')

    if identKep:
        identConv = ident.group(1)

        if not idtspKep:
            identConv = identConv.replace(' ', '')

        identConv = identConv.replace('\t', ' ' * identSze)
        idntSz.append(identConv)
    else:
        idntSz.append('')

array = arrayB


# Save labels to preserve formatting
if verbos > 0:
    print '--- save labels'

lblNmbr = 0  # Label numbers

for c, _ in enumerate(array):
    labels = re.findall(r'{([^}]*)}', array[c])

    if labels:

        for item in labels:

            if re.search(r'\W', item) and item is not "@" and verbos > 1:
                print '>', lineNo[c], 'non standard label name', '{' + item + '}'

            lbleLb.append(item)
            array[c] = array[c].replace('{' + item + '}', '{' + str(lblNmbr) + '}')
            lblNmbr += 1


if verbos > 0:
    print '--- convert ? to PRINT'

if cnvrtPrt:
    array[:] = [re.sub(r'(^|:)\s*(\?)', r'\1print', line) for line in array]


if verbos > 0:
    print '--- remove THEN / GOTO'

for c, _ in enumerate(array):
    thenGoto = re.findall(r'(then|else)(\s*)(goto)', array[c], re.IGNORECASE)

    if thenGoto:

        for item in thenGoto:

            if thngtStp == 'T' and 'else' not in item[0]:
                array[c] = array[c].replace(item[0], '')

            if thngtStp == 'G':
                array[c] = array[c].replace(item[2], '')
            # print array[c].rstrip()


if verbos > 0:
    print '--- capitalize, shrink multiple spaces and change spaces around :'

if cptlzAll:
    array[:] = [c.upper() for c in array]
    remrkLbl = remrkLbl.upper()
    remrkReg = remrkReg.upper()

if not keeppSpc:
    array[:] = [re.sub(r'\s+(?!$)', shortSpc, c) for c in array]

array[:] = [re.sub(r'(?:\s*(?=:))', colonBef, c) for c in array]
array[:] = [re.sub(r'(?:(?<=:)\s*)', colonAft, c) for c in array]


if verbos > 0:
    print '--- restore labels'

for c, _ in enumerate(array):
    labels = re.findall(r'{([^}]*)}', array[c])

    if labels:

        for item in labels:
            array[c] = array[c].replace('{' + item + '}', '{' + lbleLb[int(item)] + '}')
            # print int(item), lbleLb[int(item)]


if verbos > 0:
    print '--- replace label positions and save labels REM'

for c, _ in enumerate(array):
    addRem = ''
    # if line is a label
    solo = re.match(r'\s*{(.+?)}', array[c])

    if solo:
        lBra = ''
        rBra = ''

        # Make {{ }} if illegal name
        if re.search(r'\W', solo.group(1)):
            lBra = '{'
            rBra = '}'

        array[c] = re.sub(r'(\s*)()({.+?})', r'\1\2' + remrkLbl + shortSpc + lBra + r'\3' + rBra, array[c])
    elif re.match(r'.+?}', array[c]):
        addRem = colonBef + ':' + remrkLbl
        labels = re.findall(r'{([^}]*)}', array[c])

        for item in labels:

            if item is not '@':
                lBra = ''
                rBra = ''

                if re.search(r'\W', item):
                    lBra = '{'
                    rBra = '}'

                itemBracket = '{' + item + '}'

                try:
                    labelIndex = lablNa.index(itemBracket)
                    array[c] = array[c].replace(lablNa[labelIndex], str(lablNo[labelIndex]))
                    addRem = addRem + shortSpc + lBra + lablNa[labelIndex] + rBra
                except ValueError:
                    array[c] = array[c].replace(itemBracket, '{' + itemBracket + '}')
                    addRem = addRem + shortSpc + '{' + itemBracket + '}'

                    if verbos > 1:
                        print '>', lineNo[c], 'label not found', itemBracket

                # print lineNo[c], lablNa[labelIndex], lablNo[labelIndex]
            elif item is '@':
                array[c] = array[c].replace('{@}', str(lineNo[c]))
                addRem = addRem + shortSpc + '{SELF}'
                # print lineNo[c], '{@}', lineNo[c]

        if not labelShw:
            addRem = ''

    lbleRm.append(addRem)

if verbos > 2:

    for labelName, labelNmbr in zip(lablNa, lablNo):
        print labelNmbr, labelName


# After code modification restore items from place markers
if verbos > 0:
    print '--- restore quotes, DATAs and REMs'

for c, _ in enumerate(array):
    quotes = re.findall(r'\"([^\"]*)\"', array[c])

    if quotes:

        for item in quotes:

            if item.isdigit():
                array[c] = array[c].replace('"' + item + '"', '"' + quotLb[int(item)] + '"')
                # print int(item), quotLb[int(item)]
            elif verbos > 1:
                print ">", lineNo[c], " problem restoring quote", item

    data = re.findall(r'(^|:)\s*(data)(.*?(?=:|$))', array[c], re.IGNORECASE)

    if data:

        for item in data:

            if item[2].isdigit():
                array[c] = array[c].replace(item[1] + item[2], item[1] + dataLb[int(item[2])])
                # print int(item), dataLb[int(item)]
            elif verbos > 1:
                print ">", lineNo[c], " problem restoring DATA", item[2]

    remark = re.findall(r'(^|:)\s*(\'|rem)(.*$)', array[c], re.IGNORECASE)

    if remark:

        for item in remark:

            if item[2].isdigit():
                array[c] = array[c].replace(item[1] + item[2], item[1] + remkLb[int(item[2])])
                # print int(item), remkLb[int(item)]
            elif item[2].lstrip() not in lablNa and verbos > 1:
                print ">", lineNo[c], " problem restoring comment", item[2]


if verbos > 0:

    print '--- remove leading spaces and nunbers at begining of line'

for c, _ in enumerate(array):
    array[c] = array[c].lstrip()

    if re.match(r'^\d', array[c]):
        array[c] = re.sub(r'^\d+\s*', '', array[c])

        if verbos > 2:
            print lineNo[c], 'Line beginning with number'


if verbos > 0:
    print '--- add line numbers and ident, apply label REMs, convert CR and check line size'

array[:] = [str(lineNo[c]) + ' ' + idntSz[c] + item for c, item in enumerate(array)]
array[:] = [item.rstrip() + lbleRm[c] for c, item in enumerate(array)]
array[:] = [item.rstrip() + '\r\n' for item in array]

for c, item in enumerate(array):
    lineLen = len(item) - 1

    if lineLen > 256 and verbos > 1:
        print '>', lineNo[c], 'Line size exceeding 256 characters:', lineLen


# More breathing
if verbos > 0:
    print


with open(fileeSve, 'w') as f:
    for c in range(len(array)):
        f.write(array[c])
