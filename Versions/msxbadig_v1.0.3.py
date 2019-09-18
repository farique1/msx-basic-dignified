"""


MSX Basic Dignified
v1.0.3
Converts modern typed MSX Basic to native format.

Copyright (C) 2019 - Fred Rique (farique) https://github.com/farique1

Better experienced with Basic.sublime-syntax and MSX Basic.tmThem
https://github.com/farique1/msx-basic-dignified/tree/master/SublimeTools

msxbadig.py <source> <destination> [args...]
msxbadig.py -h for help.

New: Local path; TODOs
"""

# TODO: (Build) Move main program paths to .ini on Packages folder
# TODO: (Build) Maybe REM tags on the source with build instructions: paths and args
# TODO: Keep spaces on AX OR BX to avoid confusion with A XOR BX
#       Replece all 'X OR' with '||', strip spaces and replace back

# TODO: Ultracompact code. Make a code trying for speed and not readability (join lines, remove spaces, variables in NEXT, etc.)
# TODO: Arbitrary length variable names, automatically picking an unused 2-character one in the conversion.

import re
import argparse
import ConfigParser
import os.path

# Config
file_load = '/Users/Farique/Documents/Dev/Change-Graph-Kit/CGK-Source.bas'   # Source file
file_save = '/Users/Farique/desktop/msx projects/msxdsk1/cgk-clas.bas'       # Destination file
line_start = 10             # Start line number
line_step = 10              # Line step amount
leading_zero = False        # Add leading zeros
space_bef_colon = 0         # Number of spaces before :
space_aft_colon = 0         # Number of spaces after :
general_spaces = 1          # Strip all general spaces to this amount
keep_spaces = False         # Keep original spaces format
keep_blank_lines = False    # Keep blank lines using REM
blank_bef_rem = False       # Add blank REM line before label
blank_aft_rem = False       # Add blank REM line after label
show_labels = False         # Show labels on lines with branching instructions
label_lines = 0             # Handle label lines: 0-label_name 1-REM_only 2-delete
label_rem_format = "s"      # Labels REM format: s-single_quote
general_rem_format = "s"    # General REM format: s-single_quote
convert_rems = False        # Convert all REMs
keep_indent = False         # Keep indentation
keep_indent_spaces = False  # Keep space characters on indents
ident_tab_size = 2          # Number of spaces per TAB on indentation
capitalise_all = True       # Capitalize
convert_print = False       # Convert ? to PRINT
strip_then_goto = 'k'       # Strip adjacent THEN/ELSE or GOTO: t-THEN/ELSE g-GOTO

# Variables
line_numbers = []      # Line numbers
ident_sizes = []       # Indent sizes
label_names = []       # Label names
label_numbers = []       # Label line numbers
stored_quotes = []     # Original quotes
stored_comments = []   # Original comments
stored_datas = []      # Original data
stored_labels = []     # Original labels
branching_labels = []  # Branching label REMs
verbose_level = 2      # Show processing status: 0-no 1-headers 2-errors 3-details
first_line = ' Refactored with MSX Basic Dignified'

local_path = os.path.dirname(__file__) + '/'

# Set .ini file (if used and active overwites built in settings)
config = ConfigParser.ConfigParser()
config.sections()
config.read(local_path + 'msxbadig.ini')
if config.read(local_path + 'msxbadig.ini') and config.getboolean('DEFAULT', 'Use_Ini_File'):
    file_load = config.get('DEFAULT', 'Source_File')
    file_save = config.get('DEFAULT', 'Destin_File')
    line_start = config.getint('DEFAULT', 'Line_Start')
    line_step = config.getint('DEFAULT', 'Line_Step')
    leading_zero = config.getboolean('DEFAULT', 'Leading_Zeros')
    space_bef_colon = config.getint('DEFAULT', 'Nnbr_Spaces_Bef_Colon')
    space_aft_colon = config.getint('DEFAULT', 'Nnbr_Spaces_Aft_Colon')
    general_spaces = config.getint('DEFAULT', 'Nmbr_Spaces_General')
    keep_spaces = config.getboolean('DEFAULT', 'Keep_Original_Spaces')
    keep_blank_lines = config.getboolean('DEFAULT', 'Keep_Blank_Lines')
    blank_bef_rem = config.getboolean('DEFAULT', 'REM_Bef_Label')
    blank_aft_rem = config.getboolean('DEFAULT', 'REM_Aft_Label')
    show_labels = config.getboolean('DEFAULT', 'Show_Branches_Labels')
    label_lines = config.getint('DEFAULT', 'Handle_Label_Lines')
    label_rem_format = config.get('DEFAULT', 'Label_REM_Format')
    general_rem_format = config.get('DEFAULT', 'Regul_REM_Format')
    convert_rems = config.getboolean('DEFAULT', 'Convert_REM_Formats')
    keep_indent = config.getboolean('DEFAULT', 'Keep_Indent')
    keep_indent_spaces = config.getboolean('DEFAULT', 'Keep_Indent_Space_Chars')
    ident_tab_size = config.getint('DEFAULT', 'Indent_TAB_Spaces')
    capitalise_all = config.getboolean('DEFAULT', 'Capitalize_All')
    convert_print = config.getboolean('DEFAULT', 'Convert_Interr_To_Print')
    strip_then_goto = config.get('DEFAULT', 'Strip_Then_Goto')
    verbose_level = config.get('DEFAULT', 'Verbose_Level')

# Set command line (if used overwites previous settings)
parser = argparse.ArgumentParser(description='Converts modern typed MSX Basic to native format')
parser.add_argument("input", nargs='?', default=file_load, help='Source file')
parser.add_argument("output", nargs='?', default=file_save, help='Destination file ([source]_) if missing')
parser.add_argument("-ls", default=line_start, type=int, help='Starting line (def 10)')
parser.add_argument("-lp", default=line_step, type=int, help='Line steps (def 10)')
parser.add_argument("-lz", default=leading_zero, action='store_true', help='Leading zeros on line numbers')
parser.add_argument("-bc", default=space_bef_colon, type=int, help="Spaces before ':' (def 0)")
parser.add_argument("-ac", default=space_aft_colon, type=int, help="Spaces after ':' (def 0)")
parser.add_argument("-gs", default=general_spaces, type=int, help='General spacing (def 1)')
parser.add_argument("-ks", default=keep_spaces, action='store_true', help='Keep original spacing')
parser.add_argument("-bl", default=keep_blank_lines, action='store_true', help='Keep blank lines as REM lines')
parser.add_argument("-br", default=blank_bef_rem, action='store_true', help='Add REM line before labels')
parser.add_argument("-ar", default=blank_aft_rem, action='store_true', help='Add REM line after labels')
parser.add_argument("-sl", default=show_labels, action='store_true', help='Show labels on lines with branching commands')
parser.add_argument("-ll", default=label_lines, type=int, choices=[0, 1, 2], help="Handle label lines: 0-label_name(def) 1-REM_only 2-delete")
parser.add_argument("-lr", default=label_rem_format, choices=["s", 'S', 'rem', 'REM'], help="Labels REM format: s-single_quote (def s)")
parser.add_argument("-rr", default=general_rem_format, choices=["s", 'S', 'rem', 'REM'], help="Regular REM format: s-single_quote (def rem)")
parser.add_argument("-cr", default=convert_rems, action='store_true', help='Convert existing REMs')
parser.add_argument("-ki", default=keep_indent, action='store_true', help='Keep indent')
parser.add_argument("-ci", default=keep_indent_spaces, action='store_true', help='Keep indent space characters')
parser.add_argument("-si", default=ident_tab_size, type=int, help='Spaces per TAB on indents (def 2)')
parser.add_argument("-nc", default=capitalise_all, action='store_false', help='Do not capitalize')
parser.add_argument("-cp", default=convert_print, action='store_true', help='Convert ? to PRINT')
parser.add_argument("-tg", default=strip_then_goto, choices=['t', 'T', 'g', 'G', 'k', 'K'], help="Remove adjacent THEN/ELSE or GOTO: t-THEN/ELSE g-GOTO k-keep_all(def)")
parser.add_argument("-vb", default=verbose_level, type=int, choices=[0, 1, 2, 3], help="Verbosity level: 0-silent 1-steps 2-errors(def) 3-details")
parser.add_argument("-ini", action='store_true', help="Create msxbadig.ini")
args = parser.parse_args()

# Write .ini file if told to
if args.ini:
    config.set('DEFAULT', 'Use_Ini_File', 'True')
    config.set('DEFAULT', 'Source_File', file_load)
    config.set('DEFAULT', 'Destin_File', file_save)
    config.set('DEFAULT', 'Line_Start', line_start)
    config.set('DEFAULT', 'Line_Step', line_step)
    config.set('DEFAULT', 'Leading_Zeros', leading_zero)
    config.set('DEFAULT', 'Nnbr_Spaces_Bef_Colon', space_bef_colon)
    config.set('DEFAULT', 'Nnbr_Spaces_Aft_Colon', space_aft_colon)
    config.set('DEFAULT', 'Nmbr_Spaces_General', general_spaces)
    config.set('DEFAULT', 'Keep_Original_Spaces', keep_spaces)
    config.set('DEFAULT', 'Keep_Blank_Lines', keep_blank_lines)
    config.set('DEFAULT', 'REM_Bef_Label', blank_bef_rem)
    config.set('DEFAULT', 'REM_Aft_Label', blank_aft_rem)
    config.set('DEFAULT', 'Show_Branches_Labels', show_labels)
    config.set('DEFAULT', 'Handle_Label_Lines', label_lines)
    config.set('DEFAULT', 'Label_REM_Format', label_rem_format)
    config.set('DEFAULT', 'Regul_REM_Format', general_rem_format)
    config.set('DEFAULT', 'Convert_REM_Formats', convert_rems)
    config.set('DEFAULT', 'Keep_Indent', keep_indent)
    config.set('DEFAULT', 'Keep_Indent_Space_Chars', keep_indent_spaces)
    config.set('DEFAULT', 'Indent_TAB_Spaces', ident_tab_size)
    config.set('DEFAULT', 'Capitalize_All', capitalise_all)
    config.set('DEFAULT', 'Convert_Interr_To_Print', convert_print)
    config.set('DEFAULT', 'Strip_Then_Goto', strip_then_goto)
    config.set('DEFAULT', 'Verbose_Level', verbose_level)
    with open('msxbadig.ini', 'wb') as configfile:
        config.write(configfile)
    raise SystemExit(0)

# Apply chosen settings
file_load = args.input
file_save = args.output
if args.output == '':
    file_save = re.sub(r'(.*)\.(.*)', r'\_.\2', file_load)
line_start = abs(args.ls)
line_step = abs(args.lp)
leading_zero = args.lz
space_bef_colon = ' ' * args.bc
space_aft_colon = ' ' * args.ac
general_spaces = ' ' * args.gs
keep_spaces = args.ks
keep_blank_lines = args.bl
blank_bef_rem = args.br
blank_aft_rem = args.ar
show_labels = args.sl
label_rem_format = args.lr
label_lines = args.ll
if label_rem_format.upper() == 'S':
    label_rem_format = "'"
general_rem_format = args.rr
if general_rem_format.upper() == 'S':
    general_rem_format = "'"
convert_rems = args.cr
keep_indent = args.ki
keep_indent_spaces = args.ci
ident_tab_size = args.si
capitalise_all = args.nc
convert_print = args.cp
strip_then_goto = args.tg.upper()
verbose_level = args.vb

# If there is a file to be oppened after all this
if file_load:
    with open(file_load, 'r') as f:
        array = f.readlines()
else:
    parser.error('Source file not found')
    raise SystemExit(0)


# Just a little breath
if verbose_level > 0:
    print

if verbose_level > 0:
    print '--- remove lone ## and ENDIFs'

array[:] = [c for c in array if not re.match(r'(^.*endif.*$|^\s*##.*$)', c, re.IGNORECASE)]


if verbose_level > 0:
    print '--- remove endline ## and trailing spaces'

# Not removing ## if there are quotes after
array[:] = [re.sub(r'(?![^"]*")(?<!,)##.*', '', c).rstrip() + '\n' for c in array]
# array[:] = [re.sub(r'##.*".*".*$', '', c).rstrip()+'\n' for c in array]
# works with quotes after ## but do not work with two sets of quotes


if verbose_level > 0:
    print '--- delete or REMark blank lines and convert existing REMs'

if convert_rems:
    array[:] = [re.sub(r"(^|.*:)\s*?(rem|')", r'\1' + general_rem_format, c) for c in array]

if keep_blank_lines:
    array[:] = [re.sub(r'(^\s*$)', general_rem_format, c) for c in array]
else:
    array[:] = [c for c in array if not re.match(r'(^\s*$)', c)]


if verbose_level > 0:
    print '--- join lines with _ and :'

arrayB = []
previous_line = ''

for item in array:

    if re.match(r'.*(:|_)$', previous_line) or re.match(r'^\s*:', item):
        previous_line = re.sub(r'( *)\s*_$', r'\1', previous_line) + re.sub(r'^\s*', '', item).rstrip()
    else:
        arrayB.append(previous_line)
        previous_line = item.rstrip()

arrayB.append(previous_line)
arrayB[0] = general_rem_format + first_line
array = arrayB


if verbose_level > 0:
    print '--- add line before and after label'

# Only if using REMs as label
if label_lines < 2:
    arrayB = []

    for item in array:
        label = re.match(r'(^\s*{.+?})', item)

        if label and blank_bef_rem:
            arrayB.append(label_rem_format)
        arrayB.append(item)

        if label and blank_aft_rem:
            arrayB.append(label_rem_format)

    array = arrayB


if verbose_level > 0:
    print '--- remove and replace defines and [?@]'
# Get define name

define_labels = ['[' + re.findall(r'\[([^\]]*)\]', c)[0] + ']' for c in array if re.match(r'^\s*define', c)]

# Get define content
define_contents = [re.findall(r'\[([^\]]*)\]', c)[1] for c in array if re.match(r'^\s*define', c)]

array[:] = [c for c in array if not re.match(r'^\s*define', c)]

# Make [?@] become LOCATE:PRINT
array[:] = [re.sub(r'(\[\?@\])(\d+,\d+)', r'locate' + general_spaces + r'\2:print', c) for c in array]

for def_Labl, def_Cont in zip(define_labels, define_contents):
    array[:] = [c.replace(def_Labl, def_Cont) for c in array]

    if verbose_level > 2:
        print def_Labl, ':', def_Cont

# Find defines that could not be replaced
if verbose_level > 1:
    def_all = [re.findall(r'\[([^\]]*)\]', c) for c in array]
    def_all[:] = [item for sublist in def_all for item in sublist]
    def_all[:] = list(set(def_all))
    for item in def_all:
        item_bracket = '[' + item + ']'
        if item_bracket not in define_labels:
            print '> define not found', '[' + item + ']'

# Store items that should remain unchanged
if verbose_level > 0:
    print '--- save REMs, DATAs and quotes'

quote_number = 0  # Quotes number place marker
rem_number = 0    # REMs number place marker
data_number = 0   # DATAs number place marker

for c, _ in enumerate(array):
    remark = re.findall(r'(^|:)\s*(\'|rem)(.*$)', array[c], re.IGNORECASE)
    # remark = re.findall(r'((^|:)\s*\'|(^|:)\s*rem)(.*$)', array[c], re.IGNORECASE))

    if remark:

        for item in remark:
            stored_comments.append(item[2])
            array[c] = array[c].replace(item[1] + str(item[2]), item[1] + str(rem_number))

            rem_number += 1

    data = re.findall(r'(^|:)\s*data(.*?(?=:|$))', array[c])

    if data:

        for item in data:
            # print item[1]
            stored_datas.append(item[1])
            array[c] = array[c].replace(str(item[1]), str(data_number))
            data_number += 1

    quotes = re.findall(r'\"([^\"]*)\"', array[c])  # r"(\"[^\"]+\"|"  capt with quotes

    if quotes:

        for item in quotes:
            stored_quotes.append(item)
            array[c] = array[c].replace('"' + item + '"', '"' + str(quote_number) + '"')
            quote_number += 1


if verbose_level > 0:
    print '--- get line numbers, indent sizes and label positions'

arrayB = []
line_digits = 0  # Line number digits

if leading_zero:
    # Find the biggest line number
    line_digits = line_start + ((len(array) - 1) * line_step)
    # Get its lenght
    line_digits = len(str(line_digits))

for item in array:
    add_line = True
    linha = item
    # If it is a label
    label = re.match(r'(^\s*{.+?})', item)

    # Save its line number
    if label:
        label_names.append(label.group(1).lstrip())
        label_numbers.append(line_start)

        # Is using REMs as label?
        if label_lines == 1:
            linha = label_rem_format
        elif label_lines == 2:
            add_line = False

    if add_line:
        arrayB.append(linha)
        line_numbers.append(str(line_start).zfill(line_digits))
        line_start += line_step

    ident = re.match(r'(^\s*)\S', item)
    # print ident.group(1).replace('\t', 't').replace(' ', 's')

    if keep_indent:
        new_indent = ident.group(1)

        if not keep_indent_spaces:
            new_indent = new_indent.replace(' ', '')

        new_indent = new_indent.replace('\t', ' ' * ident_tab_size)
        ident_sizes.append(new_indent)
    else:
        ident_sizes.append('')

array = arrayB


# Save labels to preserve formatting
if verbose_level > 0:
    print '--- save labels'

label_number = 0

for c, _ in enumerate(array):
    labels = re.findall(r'{([^}]*)}', array[c])

    if labels:

        for item in labels:

            if re.search(r'\W', item) and item is not "@" and verbose_level > 1:
                print '>', line_numbers[c], 'non standard label name', '{' + item + '}'

            stored_labels.append(item)
            array[c] = array[c].replace('{' + item + '}', '{' + str(label_number) + '}')
            label_number += 1


if verbose_level > 0:
    print '--- convert ? to PRINT'

if convert_print:
    array[:] = [re.sub(r'(^|:)\s*(\?)', r'\1print', line) for line in array]


if verbose_level > 0:
    print '--- remove THEN / GOTO'

for c, _ in enumerate(array):
    then_goto = re.findall(r'(then|else)(\s*)(goto)', array[c], re.IGNORECASE)

    if then_goto:

        for item in then_goto:

            if strip_then_goto == 'T' and 'else' not in item[0]:
                array[c] = array[c].replace(item[0], '')

            if strip_then_goto == 'G':
                array[c] = array[c].replace(item[2], '')
            # print array[c].rstrip()


if verbose_level > 0:
    print '--- capitalize, shrink multiple spaces and change spaces around :'

if capitalise_all:
    array[:] = [c.upper() for c in array]
    label_rem_format = label_rem_format.upper()
    general_rem_format = general_rem_format.upper()

if not keep_spaces:
    array[:] = [re.sub(r'\s+(?!$)', general_spaces, c) for c in array]

array[:] = [re.sub(r'(?:\s*(?=:))', space_bef_colon, c) for c in array]
array[:] = [re.sub(r'(?:(?<=:)\s*)', space_aft_colon, c) for c in array]


if verbose_level > 0:
    print '--- restore labels'

for c, _ in enumerate(array):
    labels = re.findall(r'{([^}]*)}', array[c])

    if labels:

        for item in labels:
            array[c] = array[c].replace('{' + item + '}', '{' + stored_labels[int(item)] + '}')
            # print int(item), stored_labels[int(item)]


if verbose_level > 0:
    print '--- replace label positions and save labels REM'

for c, _ in enumerate(array):
    append_label = ''  # branching labels at the end of line

    # if line is a label
    solo = re.match(r'\s*{(.+?)}', array[c])

    if solo:
        lft_brkt = ''
        rgt_brkt = ''

        # Make {{ }} if illegal name
        if re.search(r'\W', solo.group(1)):
            lft_brkt = '{'
            rgt_brkt = '}'

        array[c] = re.sub(r'(\s*)()({.+?})', r'\1\2' + label_rem_format + general_spaces + lft_brkt + r'\3' + rgt_brkt, array[c])
    elif re.match(r'.+?}', array[c]):
        append_label = space_bef_colon + ':' + label_rem_format
        labels = re.findall(r'{([^}]*)}', array[c])

        for item in labels:

            if item is not '@':
                lft_brkt = ''
                rgt_brkt = ''

                if re.search(r'\W', item):
                    lft_brkt = '{'
                    rgt_brkt = '}'

                item_bracket = '{' + item + '}'

                try:
                    label_index = label_names.index(item_bracket)
                    array[c] = array[c].replace(label_names[label_index], str(label_numbers[label_index]))
                    append_label = append_label + general_spaces + lft_brkt + label_names[label_index] + rgt_brkt
                except ValueError:
                    array[c] = array[c].replace(item_bracket, '{' + item_bracket + '}')
                    append_label = append_label + general_spaces + '{' + item_bracket + '}'

                    if verbose_level > 1:
                        print '>', line_numbers[c], 'label not found', item_bracket

                # print line_numbers[c], label_names[label_index], label_numbers[label_index]
            elif item is '@':
                array[c] = array[c].replace('{@}', str(line_numbers[c]))
                append_label = append_label + general_spaces + '{SELF}'
                # print line_numbers[c], '{@}', line_numbers[c]

        if not show_labels:
            append_label = ''

    branching_labels.append(append_label)

if verbose_level > 2:

    for labelName, labelNmbr in zip(label_names, label_numbers):
        print labelNmbr, labelName


# After code modification restore items from place markers
if verbose_level > 0:
    print '--- restore quotes, DATAs and REMs'

for c, _ in enumerate(array):
    quotes = re.findall(r'\"([^\"]*)\"', array[c])

    if quotes:

        for item in quotes:

            if item.isdigit():
                array[c] = array[c].replace('"' + item + '"', '"' + stored_quotes[int(item)] + '"')
                # print int(item), stored_quotes[int(item)]
            elif verbose_level > 1:
                print ">", line_numbers[c], " problem restoring quote", item

    data = re.findall(r'(^|:)\s*(data)(.*?(?=:|$))', array[c], re.IGNORECASE)

    if data:

        for item in data:

            if item[2].isdigit():
                array[c] = array[c].replace(item[1] + item[2], item[1] + stored_datas[int(item[2])])
                # print int(item), stored_datas[int(item)]
            elif verbose_level > 1:
                print ">", line_numbers[c], " problem restoring DATA", item[2]

    remark = re.findall(r'(^|:)\s*(\'|rem)(.*$)', array[c], re.IGNORECASE)

    if remark:

        for item in remark:

            if item[2].isdigit():
                array[c] = array[c].replace(item[1] + item[2], item[1] + stored_comments[int(item[2])])
                # print int(item), stored_comments[int(item)]
            elif item[2].lstrip() not in label_names and verbose_level > 1:
                print ">", line_numbers[c], " problem restoring comment", item[2]


if verbose_level > 0:

    print '--- remove leading spaces and nunbers at begining of line'

for c, _ in enumerate(array):
    array[c] = array[c].lstrip()

    if re.match(r'^\d', array[c]):
        array[c] = re.sub(r'^\d+\s*', '', array[c])

        if verbose_level > 2:
            print line_numbers[c], 'Line beginning with number'


if verbose_level > 0:
    print '--- add line numbers and ident, apply label REMs, convert CR and check line size'

array[:] = [str(line_numbers[c]) + ' ' + ident_sizes[c] + item for c, item in enumerate(array)]
array[:] = [item.rstrip() + branching_labels[c] for c, item in enumerate(array)]
array[:] = [item.rstrip() + '\r\n' for item in array]

for c, item in enumerate(array):
    line_lenght = len(item) - 1

    if line_lenght > 256 and verbose_level > 1:
        print '>', line_numbers[c], 'Line size exceeding 256 characters:', line_lenght


# More breathing
if verbose_level > 0:
    print


with open(file_save, 'w') as f:
    for c in range(len(array)):
        f.write(array[c])
