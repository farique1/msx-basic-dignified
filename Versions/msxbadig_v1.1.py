"""


MSX Basic Dignified
v1.1 (19_9_3_21_42)
Converts modern typed MSX Basic to native format.

Copyright (C) 2019 - Fred Rique (farique) https://github.com/farique1

Better experienced with MSX Sublime tools at:
https://github.com/farique1/MSX-Sublime-Tools
Syntax Highlight, Theme, Build System and Comment Preference.

msxbadig.py <source> <destination> [args...]
msxbadig.py -h for help.

New: Reworked code
     Arbitrary length variable names
     and a lot more (see the changelog)

Todo: Ultracompact code. produce a code trying for speed and not readability (join lines, remove spaces, variables in NEXT, etc.)
      Allow use of 'true' and 'false' variables substituting for 1 and 0. Mind thongs like flipping(negating) status (x=not x or x=!x becomes x=abs(x-1) and so forth)
      Allow to choose the short var assossiated with a long var (declare variable:vr ?). Allow reserve of some short var names.
      Separate the name of the error/warning from the rest of the line with a : (as in the file name and number line)

Bugs: Not removing end line ## if there are quotes after it
      Leading number on a REM line broken with : being removed (if the line is a REM they dont need to be removed)
      All lone endifs being removed even after a _ line break on a DATA or REM line (implicating they are not endifs but part of the instruction)
"""

# Use on terminal for benchmarking
# for run in {1..100}; do  python msxbadig.py cgk-source.bas cgk-conv.bas -vb 0; done > test.txt

import re
import argparse
import ConfigParser
import os.path
# import time
# start = time.time()

# Config
file_load = ''  # '/Users/Farique/Documents/Dev/Change-Graph-Kit/CGK-Source.bas'   # Source file
file_save = ''  # '/Users/Farique/desktop/msx projects/msxdsk1/cgk-clas.bas'       # Destination file
line_start = 10             # Start line number
line_step = 10              # Line step amount
leading_zero = False        # Add leading zeros
space_bef_colon = 0         # Number of spaces before :
space_aft_colon = 0         # Number of spaces after :
general_spaces = 1          # Strip all general spaces to this amount
unpack_operators = False    # keep spaces around +-=<>*/^\
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
verbose_level = 2           # Show processing status: 0-silent 1-steps+erros 2-+warnings 3-+details
strip_then_goto = 'k'       # Strip adjacent THEN/ELSE or GOTO: t-THEN/ELSE g-GOTO
long_var_summary = 0        # Show long variables summary on rems at the end of the program (0-none 1+-var per line)
is_from_build = False       # Tell if is being called from a build system (show file name on error messages)

# Set .ini file (if used and active overwites built in settings)
local_path = os.path.dirname(__file__) + '/'
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
    unpack_operators = config.get('DEFAULT', 'Unpack_Operators')
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
    long_var_summary = config.get('DEFAULT', 'Long_Var_Summary')
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
parser.add_argument("-uo", default=unpack_operators, action='store_true', help="Keep spaces around +-=<>*/^\\.,;")
parser.add_argument("-ks", default=keep_spaces, action='store_true', help='Keep original spacing')
parser.add_argument("-bl", default=keep_blank_lines, action='store_true', help='Keep blank lines as REM lines')
parser.add_argument("-br", default=blank_bef_rem, action='store_true', help='Add REM line before labels')
parser.add_argument("-ar", default=blank_aft_rem, action='store_true', help='Add REM line after labels')
parser.add_argument("-sl", default=show_labels, action='store_true', help='Show labels on lines with branching commands')
parser.add_argument("-ll", default=label_lines, type=int, choices=[0, 1, 2], help="Handle label lines: 0 label_name(def), 1 REM_only, 2 delete")
parser.add_argument("-lr", default=label_rem_format, choices=["s", 'S', 'rem', 'REM'], help="Labels REM format: s=single_quote(def)")
parser.add_argument("-rr", default=general_rem_format, choices=["s", 'S', 'rem', 'REM'], help="Regular REM format: s=single_quote(def)")
parser.add_argument("-cr", default=convert_rems, action='store_true', help='Convert existing REMs')
parser.add_argument("-ki", default=keep_indent, action='store_true', help='Keep indent')
parser.add_argument("-ci", default=keep_indent_spaces, action='store_true', help='Keep indent space characters')
parser.add_argument("-si", default=ident_tab_size, type=int, help='Spaces per TAB on indents (def 2)')
parser.add_argument("-nc", default=capitalise_all, action='store_false', help='Do not capitalize')
parser.add_argument("-cp", default=convert_print, action='store_true', help='Convert ? to PRINT')
parser.add_argument("-tg", default=strip_then_goto, choices=['t', 'T', 'g', 'G', 'k', 'K'], help="Remove adjacent THEN/ELSE or GOTO: t THEN/ELSE, g GOTO, k keep_all(def)")
parser.add_argument("-vs", default=long_var_summary, type=int, nargs='?', help="Show long variables summary on REMs at the end of the program: 0 none(def), 1+ vars per line")
parser.add_argument("-vb", default=verbose_level, type=int, choices=[0, 1, 2, 3], help="Verbosity level: 0 silent, 1 steps+erros, 2 +warnings(def), 3 +details")
parser.add_argument("-fb", default=is_from_build, action='store_true', help="Tell Badig it is running from a build system")
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
    config.set('DEFAULT', 'Unpack_Operators', unpack_operators)
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
    config.set('DEFAULT', 'Long_Var_Summary', long_var_summary)
    config.set('DEFAULT', 'Verbose_Level', verbose_level)
    with open('msxbadig.ini', 'wb') as configfile:
        config.write(configfile)
    raise SystemExit(0)

# Apply chosen settings
file_load = args.input
file_save = args.output
if args.output == '':
    save_path = os.path.dirname(file_load)
    save_path = '' if save_path == '' else save_path + '/'
    save_file = os.path.basename(file_load)
    save_file = os.path.splitext(save_file)[0][0:8] + '.bas'
    file_save = save_path + save_file
line_start = abs(args.ls)
line_step = abs(args.lp)
leading_zero = args.lz
space_bef_colon = ' ' * args.bc
space_aft_colon = ' ' * args.ac
general_spaces = ' ' * args.gs
unpack_operators = args.uo
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
if args.vs is None:
    long_var_summary = 5
else:
    long_var_summary = args.vs
verbose_level = args.vb
is_from_build = args.fb

print_format = 'print'
xor_format = 'x or'
if capitalise_all:
    label_rem_format = label_rem_format.upper()
    general_rem_format = general_rem_format.upper()
    print_format = print_format.upper()
    xor_format = xor_format.upper()
first_line = 'Refactored with MSX Basic Dignified'
var_dict = {}
short_cur_int = 'z{'
short_cur_str = 'z{$'


def show_log(line_number, text, level, **kwargs):
    global is_from_build
    global file_load
    bullets = ['    ', '--- ', '*** ', '  - ', '  * ']

    try:
        bullet = kwargs['bullet']
    except KeyError:
        bullet = level

    display_file_name = ''
    if is_from_build and bullet == 2:
        display_file_name = os.path.basename(file_load) + ': '
    line_number = str(line_number) if line_number == '' else '(' + str(line_number) + '): '

    if verbose_level >= level:
        print bullets[bullet] + display_file_name + line_number + text


def get_short_var(long_var):
    global short_cur_int
    global short_cur_str
    global var_dict
    global line_num

    # Test if variable has invalid characters
    long_var = '    ' if long_var == '' else long_var  # just to pass the next 2 lines if '' 
    long_var = long_var[1:] if long_var[0] == '~' else long_var
    long_var_test = long_var[:-1] if long_var[-1:] == '$' else long_var
    if re.search(r'\W', long_var_test) or long_var_test.isdigit() \
            or len(long_var_test) < 3 or long_var_test.strip() == '':
        show_log(line_num, ' '.join(['invalid_variable_name', long_var]), 1, bullet=2)
        show_log('', 'Execution_stoped\n', 1, bullet=0)
        raise SystemExit(0)

    if long_var in var_dict:
        return var_dict[long_var]

    if long_var[-1:] == '$':
        short_cur = short_cur_str
    else:
        short_cur = short_cur_int

    # Decrement initial short variable ZZ if it is below AA stop.
    short_A = short_cur[0]
    short_B = short_cur[1]
    short_B = chr(ord(short_B) - 1)
    if short_B < 'a':
        short_A = chr(ord(short_A) - 1)
        short_B = 'z'
    short_cur = short_A + short_B
    if short_A < 'a':
        show_log(line_num, ' '.join(['out_of_short_name_variables', long_var]), 1, bullet=2)
        show_log('', 'Execution_stoped\n', 1, bullet=0)
        raise SystemExit(0)

    if long_var[-1:] == '$':
        short_cur += '$'
        short_cur_str = short_cur
    else:
        short_cur_int = short_cur

    var_dict[long_var] = short_cur
    return short_cur


def get_clean_line(line):
    quotes = re.findall(r'\"[^\"]*\"', line)
    if quotes:
        for item in quotes:
            line = line.replace(item, '')
    data = re.findall(r'(?:^|:)\s*data(.+?(?=:|$))', line, re.IGNORECASE)
    if data:
        for item in data:
            line = line.replace(item, '')
    remark = re.findall(r'(?:(?:^|:)\s*rem|\')(.+)', line, re.IGNORECASE)
    if remark:
        for item in remark:
            line = line.replace(item, '')
    return line


array = []
if file_load:
    try:
        with open(file_load, 'r') as f:
            for i, line in enumerate(f):
                array.append((i + 1, line))
    except IOError:
        show_log('', ' '.join(['source_not_found', file_load]), 1, bullet=2)
        show_log('', 'Execution_stoped\n', 1, bullet=0)
        raise SystemExit(0)
else:
    show_log('', 'source_not_given', 1, bullet=2)
    show_log('', 'Execution_stoped\n', 1, bullet=0)
    raise SystemExit(0)


show_log('', '', 1, bullet=0)


show_log('', 'Removing ## and lone number lines', 1)
show_log('', 'Deleting or REMarking blank lines', 1, bullet=0)
show_log('', 'Storing and deleting define lines', 1, bullet=0)
show_log('', 'Storing and deleting declare lines', 1, bullet=0)
show_log('', 'Removing endline ## and trailing spaces', 1, bullet=0)
arrayB = []
defines = {}
define = re.compile(r'\[[^\]]+\]')
for line in array:
    line_num, line_alt = line

    if re.match(r'(^\s*##.*$)', line_alt, re.IGNORECASE):
        pass

    # if re.match(r'(^\s*\d+\s*$)', line_alt, re.IGNORECASE):
    #     pass

    elif re.match(r'(^\s*$)', line_alt):
        if keep_blank_lines:
            line_alt = re.sub(r'(^\s*$)', general_rem_format, line_alt)
            arrayB.append((line_num, line_alt))
        else:
            pass

    elif re.match(r'^\s*define', line_alt, re.IGNORECASE):
        defines_split = line_alt.split(',')
        for define_split in defines_split:
            found_def = define.findall(define_split)
            try:
                defines[found_def[0]] = found_def[1][1:-1]
                show_log(line_num, ' '.join(['Define_found', found_def[0], found_def[1]]), 3)
            except IndexError:
                show_log(line_num, ' '.join(['define_error', str(found_def)]), 1, bullet=2)
                show_log('', 'Execution_stoped\n', 1, bullet=0)
                raise SystemExit(0)

    elif re.match(r'^\s*declare', line_alt, re.IGNORECASE):
        line_alt = line_alt.replace('declare', '')
        line_alt = re.sub(r'##.*$', '', line_alt)
        declares_split = line_alt.split(',')
        for declare_split in declares_split:
            long_var = declare_split.strip()
            if not long_var:
                show_log(line_num, ' '.join(['declare_warning']), 2, bullet=4)
                continue
            short_var = get_short_var(long_var)
            show_log(line_num, ' '.join(['declare_found', long_var, short_var]), 3)

    else:
        line_alt = re.sub(r'(?![^"]*")(?<!\S)##.*', '', line_alt).rstrip() + '\n'
        # Above line not removing endline ## if there are quotes after it (but preserve ## inside)
        arrayB.append((line_num, line_alt))

array = arrayB


show_log('', 'Replacing defines and [?@]', 1)
arrayB = []
for line in array:
    line_num, line_alt = line

    if define.findall(line_alt):
        if '[?@]' in line_alt:
            line_alt = re.sub(r'(\[\?@\])(\S+,\S+|\S+)', r'locate' + general_spaces + r'\2:print', line_alt)
            show_log(line_num, ' '.join(['replaced_[?@]']), 3)
        line_defs = list(set(define.findall(line_alt)))
        if line_defs:
            show_log(line_num, ' '.join(['replaced_defines', ' '.join(line_defs)]), 3)
            for defs in line_defs:
                try:
                    line_alt = line_alt.replace(defs, defines[defs])
                except KeyError as e:
                    show_log(line_num, ' '.join(['define_not_found', str(e)]), 1, bullet=2)
                    show_log('', 'Execution_stoped\n', 1, bullet=0)
                    raise SystemExit(0)

    arrayB.append((line_num, line_alt))
array = arrayB


show_log('', 'Joining lines with _ and :', 1)
show_log('', 'Removing ENDIFs and nunbers at begining of line', 1, bullet=0)
arrayB = []
previous_line = ''
prev_line_number = 0
join_line_num = None
for line in array:
    line_num, line_alt = line

    if re.match(r'^\d', line_alt.lstrip()) and previous_line.rstrip()[-1:] != '_':
        line_alt = re.sub(r'^\s*\d+\s*', '', line_alt)
        show_log(line_num, ' '.join(['removed_line_number']), 2, bullet=4)

    if re.match(r'(^\s*endif\s*$)', line_alt, re.IGNORECASE):
        show_log(line_num, ' '.join(['endif_removed']), 3)
        if re.match(r'.*(:|_)$', previous_line):
            previous_line = previous_line[:-1]

    elif re.match(r'.*(:|_)$', previous_line) or re.match(r'^\s*:', line_alt):
        previous_line = re.sub(r'( *)\s*_$', r'\1', previous_line) + re.sub(r'^\s*', '', line_alt).rstrip()
        if not join_line_num:
            join_line_num = line_num

    else:
        if join_line_num:
            arrayB.append((join_line_num - 1, previous_line))
            endif_line = join_line_num - 1
            show_log(join_line_num - 1, ' '.join(['Joined_line']), 3)
        else:
            arrayB.append((prev_line_number, previous_line))
            endif_line = prev_line_number

        clean_line = get_clean_line(previous_line)
        if 'endif' in clean_line.lower():
            show_log(endif_line, ' '.join(['endif_not_alone']), 2, bullet=4)

        previous_line = line_alt.rstrip()
        prev_line_number = line_num
        join_line_num = None

arrayB.append((line_num, previous_line))
arrayB[0] = (0, general_rem_format + general_spaces + first_line)
array = arrayB


show_log('', 'Adding line before and after labels', 1)
if label_lines < 2:
    arrayB = []
    for line in array:
        line_num, line_alt = line

        label = re.match(r'(^\s*{.+?})', line_alt)
        if label and blank_bef_rem:
            arrayB.append(('0', label_rem_format))
            show_log(line_num, ' '.join(['space_before_label', str(label.group(1)).strip()]), 3)

        arrayB.append(line)

        if label and blank_aft_rem:
            arrayB.append(('0', label_rem_format))
            show_log(line_num, ' '.join(['space_after_label', str(label.group(1)).strip()]), 3)

    array = arrayB


show_log('', 'Getting line numbers, indent sizes and label positions', 1)
show_log('', 'Removing leading spaces', 1, bullet=0)
arrayB = []
line_digits = 0
line_numbers = []
ident_sizes = []
labels_store = {}
if leading_zero:
    line_digits = line_start + ((len(array) - 1) * line_step)
    line_digits = len(str(line_digits))
line_current = line_start
for line in array:
    line_num, line_alt = line

    label = re.match(r'(^\s*{.+?})', line_alt)
    if label:
        labels_store[label.group(1).lstrip()] = line_current
        show_log(line_num, ' '.join(['got_label_line', label.group(1).lstrip(), str(line_current)]), 3)
        if label_lines == 1:
            line_alt = label_rem_format
        elif label_lines == 2:
            continue

    new_indent = ''
    ident = re.match(r'(^\s*)\S', line_alt)
    if keep_indent:
        new_indent = ident.group(1)
        if not keep_indent_spaces:
            new_indent = new_indent.replace(' ', '')
        new_indent = new_indent.replace('\t', ' ' * ident_tab_size)

    line_alt = line_alt.lstrip()
    ident_sizes.append(new_indent)
    line_padded = str(line_current).zfill(line_digits)
    line_numbers.append(line_padded)
    line_current += line_step

    arrayB.append((line_num, line_alt))
array = arrayB


show_log('', 'Storing REMs, DATAs and quotes', 1)
quote_number = 0
comment_number = 0
data_number = 0
stored_quotes = []
stored_comments = []
stored_datas = []
arrayB = []
for line in array:
    line_num, line_alt = line

    quotes = re.findall(r'"[^"]*(?:"|$)', line_alt)
    if quotes:
        for item in quotes:
            stored_quotes.append(item)
            line_alt = line_alt.replace(item, '"' + str(quote_number) + '"')
            show_log(line_num, ' '.join(['stored_quote', str(quote_number), str(item)]), 3)
            quote_number += 1

    data = re.findall(r'(?:^|:)\s*data(.+?(?=:|$))', line_alt, re.IGNORECASE)
    if data:
        for item in data:
            stored_datas.append(item)
            line_alt = line_alt.replace(item, '^' + str(data_number) + '^')
            show_log(line_num, ' '.join(['stored_data', str(data_number), str(item)]), 3)
            data_number += 1

    remark = re.findall(r'(?:(?:^|:)\s*rem|\')(.+)', line_alt, re.IGNORECASE)
    if remark:
        for item in remark:
            stored_comments.append(item)
            line_alt = line_alt.replace(item, "|" + str(comment_number) + "|")
            show_log(line_num, ' '.join(['stored_rem', str(comment_number), str(item)]), 3)
            comment_number += 1

    arrayB.append((line_num, line_alt))
array = arrayB


show_log('', 'Storing labels', 1)
arrayB = []
label_number = 0
stored_labels = []
for line in array:
    line_num, line_alt = line

    labels = re.findall(r'{[^}]*}', line_alt)
    if labels:
        for item in labels:
            if (re.search(r'\W', item[1:-1]) or item[1:-1].isdigit()) and item != "{@}":
                show_log(line_num, ' '.join(['invalid_label_name', item]), 1, bullet=2)
                show_log('', 'Execution_stoped\n', 1, bullet=0)
                raise SystemExit(0)
            stored_labels.append(item)
            line_alt = line_alt.replace(item, '{' + str(label_number) + '}')
            show_log(line_num, ' '.join(['stored_label', str(label_number), str(item)]), 3)
            label_number += 1

    arrayB.append((line_num, line_alt))
array = arrayB


show_log('', 'Replacing long variables', 1)
arrayB = []
for line in array:
    line_num, line_alt = line

    # new_long_vars = re.findall(r'(~.+?)\s', line_alt, re.IGNORECASE)
    new_long_vars = re.findall(r'(~\w+\$?)', line_alt, re.IGNORECASE)
    if new_long_vars:
        for new_long_var in new_long_vars:
            short_var = get_short_var(new_long_var)
            line_alt = line_alt.replace(new_long_var, short_var)
            show_log(line_num, ' '.join(['replaced_variable', short_var, new_long_var[1:]]), 3)

    lone_words = re.findall(r'(\w+\$?)', line_alt, re.IGNORECASE)
    if lone_words:
        for lone_word in lone_words:
            if lone_word in var_dict:
                line_alt = line_alt.replace(lone_word, var_dict[lone_word])
                show_log(line_num, ' '.join(['replaced_variable', var_dict[lone_word], lone_word]), 3)

    arrayB.append((line_num, line_alt))
array = arrayB


show_log('', 'Removing THEN/GOTO, Converting ? to PRINT', 1)
show_log('', 'Capitalizing, converting REMs, adjusting spaces', 1, bullet=0)
show_log('', 'preserving X OR and changing spaces around :', 1, bullet=0)
arrayB = []
for line in array:
    line_num, line_alt = line

    then_goto = re.findall(r'(then|else)(\s*)(goto)', line_alt, re.IGNORECASE)
    if then_goto:
        for item in then_goto:
            if strip_then_goto == 'T' and 'else' != item[0]:
                line_alt = line_alt.replace(item[0], '')
                show_log(line_num, ' '.join(['removed_then']), 3)
            if strip_then_goto == 'G':
                line_alt = line_alt.replace(item[2], '')
                show_log(line_num, ' '.join(['removed_goto']), 3)

    if convert_print:
        prints = re.findall(r'(?:^|:)\s*(\?)', line_alt)
        if prints:
            line_alt = line_alt.replace('?', print_format)
            show_log(line_num, ' '.join(['converted_?', str(len(prints)) + 'x']), 3)

    if capitalise_all:
        line_alt = line_alt.upper()

    if not keep_spaces:
        if len(general_spaces) == 0 and re.findall(r'x or', line_alt, flags=re.IGNORECASE):
            line_alt = re.sub(r'(x)( )(or)', r'\1|^|\3', line_alt, flags=re.IGNORECASE)
            line_alt = re.sub(r'\s+(?!$)', general_spaces, line_alt)
            line_alt = line_alt.replace('|^|', ' ')
        else:
            line_alt = re.sub(r'\s+(?!$)', general_spaces, line_alt)

    if not unpack_operators:
        line_alt = re.sub(r'\s*([\+\-\=\<\>\*\/\^\\\,\;\.])\s*', r'\1', line_alt)

    if convert_rems:
        if re.findall(r'(rem|\')', line_alt, re.IGNORECASE):
            line_alt = re.sub(r'(rem|(?:^|:)\s*\')', general_rem_format, line_alt, flags=re.IGNORECASE)

    line_alt = re.sub(r'(?:\s*(?=:))', space_bef_colon, line_alt)
    line_alt = re.sub(r'(?:(?<=:)\s*)', space_aft_colon, line_alt)

    arrayB.append((line_num, line_alt))
array = arrayB


show_log('', 'Restoring labels', 1)
arrayB = []
for line in array:
    line_num, line_alt = line

    labels = re.findall(r'{[^}]*}', line_alt)
    if labels:
        for item in labels:
            label = stored_labels[int(item[1:-1])]
            line_alt = line_alt.replace(item, label)
            show_log(line_num, ' '.join(['restored_label', item[1:-1], label]), 3)

    arrayB.append((line_num, line_alt))
array = arrayB


show_log('', 'REMarking line labels, replacing branching labels and storing its REMs', 1)
arrayB = []
branching_labels = []
for line, number in zip(array, line_numbers):
    line_num, line_alt = line
    append_label = ''

    labels = re.findall(r'{[^}]*}', line_alt)
    if re.match(r'\s*{\w+?}', line_alt):
        line_alt = re.sub(r'(\s*)({\w+?})', r'\1' + label_rem_format + general_spaces + r'\2', line_alt)

    elif labels:
        append_label = space_bef_colon + ':' + space_aft_colon + label_rem_format
        for item in labels:
            if item != '{@}':
                try:
                    line_alt = line_alt.replace(item, str(labels_store[item]))
                    append_label += general_spaces + item
                    show_log(line_num, ' '.join(['replaced_label', item, str(labels_store[item])]), 3)
                except KeyError:
                    show_log(line_num, ' '.join(['label_not_found', item]), 1, bullet=2)
                    show_log('', 'Execution_stoped\n', 1, bullet=0)
                    raise SystemExit(0)
            elif item == '{@}':
                line_alt = line_alt.replace('{@}', str(number))
                append_label += general_spaces + '{SELF}'
                show_log(line_num, ' '.join(['replaced_label', item, number]), 3)

        if not show_labels:
            append_label = ''

    branching_labels.append(append_label)

    arrayB.append((line_num, line_alt))
array = arrayB


show_log('', 'Restoring quotes, DATAs and REMs', 1)
arrayB = []
for line in array:
    line_num, line_alt = line

    remarks = re.findall(r'(?:\'|rem)\s*(\|\d*\|)', line_alt, re.IGNORECASE)
    if remarks:
        for item in remarks:
            remark = stored_comments[int(item[1:-1])]
            line_alt = line_alt.replace(item, remark)
            show_log(line_num, ' '.join(['restored_comments', item[1:-1], remark]), 3)

    datas = re.findall(r'(?:data)\s*(\^\d*\^(?=\s*:|$))', line_alt, re.IGNORECASE)
    if datas:
        for item in datas:
            data = stored_datas[int(item[1:-1])]
            line_alt = line_alt.replace(item, data)
            show_log(line_num, ' '.join(['restored_data', item[1:-1], data]), 3)

    quotes = re.findall(r'\"[^\"]\d*\"', line_alt)
    if quotes:
        for item in quotes:
            quote = stored_quotes[int(item[1:-1])]
            line_alt = line_alt.replace(item, quote)
            show_log(line_num, ' '.join(['restored_quote', item[1:-1], quote]), 3)

    arrayB.append((line_num, line_alt))
array = arrayB


show_log('', 'Appending long variables summary', 1)
if var_dict and long_var_summary > 0:
    report_line = general_rem_format + general_spaces
    last_line = int(line_numbers[len(line_numbers) - 1])
    extra_lines = array[len(array) - 1][0]
    n = 1
    for long_var, short_var in sorted(var_dict.items(), key=lambda item: item[1], reverse=True):
        short_var = short_var.upper() if capitalise_all else short_var
        report_line += short_var + '-' + long_var + ', '
        if n % long_var_summary == 0:
            extra_lines += 1
            array.append((extra_lines, report_line[0:-2]))
            report_line = general_rem_format + general_spaces
            last_line += line_step
            line_numbers.append(str(last_line))
            ident_sizes.append('')
            branching_labels.append('')
        n += 1
    if report_line != general_rem_format + general_spaces:
        extra_lines += 1
        array.append((extra_lines, report_line[0:-2]))
        last_line += line_step
        line_numbers.append(str(last_line))
        ident_sizes.append('')
        branching_labels.append('')


show_log('', 'Adding line numbers and ident, applying label REMs', 1)
show_log('', 'Converting CR and checking line size', 1, bullet=0)
arrayB = []
for line, number, ident, blabel in zip(array, line_numbers, ident_sizes, branching_labels):
    line_num, line_alt = line

    line_alt = number + ' ' + ident + line_alt + blabel.rstrip() + '\r\n'

    line_lenght = len(line_alt) - 1
    if line_lenght > 256:
        show_log(line_num, ' '.join(['line_too_long', str(line_lenght) + ' chars']), 1, bullet=2)
        show_log('', 'Execution_stoped\n', 1, bullet=0)
        raise SystemExit(0)

    arrayB.append(line_alt)
array = arrayB


show_log('', '', 1, bullet=0)


with open(file_save, 'w') as f:
    for c in range(len(array)):
        f.write(array[c])

# end = time.time()
# print(end - start)
# raise SystemExit(0)
