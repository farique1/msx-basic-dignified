"""
MSX Basic Dignified
v1.2
Converts modern typed MSX Basic to native format.

Copyright (C) 2019 - Fred Rique (farique) https://github.com/farique1

Better experienced with MSX Sublime tools at:
https://github.com/farique1/MSX-Sublime-Tools
Syntax Highlight, Theme, Build System and Comment Preference.

msxbadig.py <source> <destination> [args...]
msxbadig.py -h for help.

New: Variables on DEFINES. A [] inside a DEFINE will be substituted for an argument touching the closing bracket.
       If the variable bracket is not empty, the text inside will be used as default in case no argument is found
       ex: using 'DEFINE [var] [poke 100,[10]]', a subsequent '[var]30' will be replaced by 'poke 100,30'
     New way of assigning long name variables:
       A long name now is attached to a short name independently of the variable type, it only need to be declared
       once and can be used for all types, int, single, double, string and typeless of the same name.
       The DECLARE command now takes only the base name of the variable, without the type symbol,
       it also can assign explicit short names in the format AAAA:BB where the AAAA is the long name and BB the short.
       This will reduce the available names but will be more compatible with the MSX basic conventions
       and will still give ~700 variables (26*26) not counting the ~300 (letter+number and single letters) not assignable.
     Added support for all types of variables. Int, single, double, string and none.
     Added GitHub link to REM header
     Added True and False statements, converts to -1 and 0. Can use NOT operator to flip or check.
     Added an INCLUDE command to insert and external .bad file into the current code.
     Fixed a bug misinterpreting commas inside the DEFINES
     Fixed a bug potentially causing REM and DATA being mixed with normal instructions and QUOTES mixed with itself.
     Fixed handling of leading line numbers
     Error if duplicated DEFINES are found.
     Error if duplicated line labels are found.
     Warning if variable DECLARED more than once.
     Better handling of DEFINEs and DECLAREs
     Handles error when destination folder is not found.
     Blank lines removed after a  Dignified command (define, declare,...) even when opted to keep blank lines.
     Keep space to prevent ST OR A confusion with S TO AR.
     Minor log output tweak

Bugs: Not removing end line ## if there are quotes after it
      Leading number on a REM line broken with : being removed (if the line is a REM they don't need to be removed)
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
file_load = ''              # Source file
file_save = ''              # Destination file
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
verbose_level = 1           # Show processing status: 0-silent 1-steps+erros 2-+warnings 3-+details
strip_then_goto = 'k'       # Strip adjacent THEN/ELSE or GOTO: t-THEN/ELSE g-GOTO
long_var_summary = 0        # Show long variables summary on rems at the end of the program (0-none 1+-var per line)
is_from_build = False       # Tell if is being called from a build system (show file name on error messages)

# Set .ini file (if used and active overwrites built in settings)
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

# Set command line (if used overwrites previous settings)
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
    save_file = os.path.splitext(save_file)[0][0:8] + '.asc'
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
if capitalise_all:
    label_rem_format = label_rem_format.upper()
    general_rem_format = general_rem_format.upper()
    print_format = print_format.upper()
first_line = 'Converted with MSX Basic Dignified'
second_line = 'https://github.com/farique1/msx-basic-dignified'
var_dict = {}
short_cur = 'z{'  # 'z{' is one above 'zz'
load_path = os.path.dirname(file_load) + '/'


def show_log(line, text, level, **kwargs):
    if line != '':
        line_num, line_alt, line_file = line
    else:
        line_num, line_file = '', ''

    global included_dict
    global is_from_build
    global file_load
    bullets = ['    ', '--- ', '*** ', '  - ', '  * ']

    try:
        bullet = kwargs['bullet']
    except KeyError:
        bullet = level

    display_file_name = ''
    if is_from_build and bullet == 2:
        display_file_name = included_dict[line_file] + ': '

    line_num = str(line_num) if line_num == '' else '(' + str(line_num) + '): '

    if verbose_level >= level:
        print bullets[bullet] + display_file_name + line_num + text


def get_short_var(get_long_var):
    global short_cur
    global var_dict
    global line

    # Test if variable has invalid characters
    long_var = get_long_var[0]
    var_type = get_long_var[1]
    short_var = get_long_var[2]

    if re.search(r'\W', long_var) or long_var.isdigit() or len(long_var) < 3 or long_var.strip() == '':
        show_log(line, ' '.join(['invalid_variable_name:', long_var]), 1, bullet=2)
        show_log('', 'Execution_stoped\n', 1, bullet=0)
        raise SystemExit(0)

    if short_var == '':
        if long_var in var_dict:
            show_log(line, ' '.join(['variable_already_declared:', long_var + var_type, var_dict[long_var] + var_type]), 2, bullet=4)
            return long_var, var_dict[long_var]
    else:
        if long_var in var_dict:
            if var_dict[long_var] == short_var:
                show_log(line, ' '.join(['variable_already_declared:', long_var, var_dict[long_var]]), 2, bullet=4)
                return long_var, var_dict[long_var]
            else:
                show_log(line, ' '.join(['long_name_already_declared:', long_var, short_var, '(' + var_dict[long_var] + ')']), 1, bullet=2)
                show_log('', 'Execution_stoped\n', 1, bullet=0)
                raise SystemExit(0)
        for long_V, short_V in var_dict.iteritems():
            if short_var == short_V:
                show_log(line, ' '.join(['short_name_already_declared:', long_var, short_V, '(' + long_V + ')']), 1, bullet=2)
                show_log('', 'Execution_stoped\n', 1, bullet=0)
                raise SystemExit(0)
        else:
            var_dict[long_var] = short_var
            return long_var, short_var

    # Decrement initial short variable ZZ, if it is below AA stop.
    match = True
    while match:
        short_A = short_cur[0]
        short_B = short_cur[1]
        short_B = chr(ord(short_B) - 1)
        if short_B < 'a':
            short_A = chr(ord(short_A) - 1)
            short_B = 'z'
        short_cur = short_A + short_B
        if short_A < 'a':
            show_log(line, ' '.join(['out_of_short_variable_names:', long_var]), 1, bullet=2)
            show_log('', 'Execution_stoped\n', 1, bullet=0)
            raise SystemExit(0)
        match = False
        for long_V, short_V in var_dict.iteritems():
            if short_cur == short_V:
                match = True

    var_dict[long_var] = short_cur
    return long_var + var_type, short_cur + var_type


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


def load_file(file_load, line_file, line, file_type):
    array = []
    if file_load:
        try:
            with open(file_load, 'r') as f:
                for i, line in enumerate(f):
                    array.append((i + 1, line, line_file))
            return array
        except IOError:
            show_log(line, ' '.join([file_type + '_not_found:', file_load]), 1, bullet=2)
            show_log('', 'Execution_stoped\n', 1, bullet=0)
            raise SystemExit(0)
    else:
        show_log('', file_type + '_not_given', 1, bullet=2)
        show_log('', 'Execution_stoped\n', 1, bullet=0)
        raise SystemExit(0)


array = load_file(file_load, 0, '', "source")


show_log('', '', 1, bullet=0)


show_log('', 'INCLUDing external code.', 1)
arrayB = []
included_dict = {0: os.path.basename(file_load)}
included_files = 0
for line in array:
    line_num, line_alt, line_file = line

    if re.match(r'^\s*include', line_alt, re.IGNORECASE):
        file_include = re.findall(r'"(.+)"', line_alt, re.IGNORECASE)
        if file_include:
            included_files += 1
            included_dict[included_files] = file_include[0]
            if os.path.isabs(file_include[0]):
                load_path = ''
            arrayC = load_file(load_path + file_include[0], included_files, line, 'include')
            arrayB.extend(arrayC)
            show_log(line, ' '.join(['file_included:', file_include[0]]), 3)
            continue
        else:
            show_log(line, ' '.join(['no_include_given']), 1, bullet=2)
            show_log('', 'Execution_stoped\n', 1, bullet=0)
            raise SystemExit(0)

    arrayB.append((line_num, line_alt, line_file))
array = arrayB


show_log('', 'Removing ## and trailing spaces', 1)
show_log('', 'Deleting or REMarking blank lines', 1, bullet=0)
show_log('', 'Storing and deleting DEFINE lines', 1, bullet=0)
show_log('', 'Storing and deleting DECLARE lines', 1, bullet=0)
arrayB = []
defines = {}
prerv_dignified_command = False
define_reg = re.compile(r'(?<=\])\s*(?=\[)')
define_reg_line = re.compile(r'(\[[^\]]+\])')
define_reg_local = re.compile(r'(\[[^\]]*\])')
define_reg_split = re.compile(r'(?<=\])\s*,\s*(?=\[)')
for line in array:
    line_num, line_alt, line_file = line

    if re.match(r'(^\s*##.*$)', line_alt, re.IGNORECASE):
        prerv_dignified_command = True

    elif re.match(r'(^\s*$)', line_alt):
        if keep_blank_lines and not prerv_dignified_command:
            line_alt = re.sub(r'(^\s*$)', general_rem_format, line_alt)
            arrayB.append((line_num, line_alt, line_file))
        else:
            prerv_dignified_command = False

    elif re.match(r'^\s*define', line_alt, re.IGNORECASE):
        prerv_dignified_command = True
        line_alt = re.sub(r'##.*$', '', line_alt)
        line_alt = re.sub(r'^\s*define', '', line_alt, flags=re.I).strip()
        if line_alt == '':
            continue

        defines_split = define_reg_split.split(line_alt.strip())
        for define_split in defines_split:
            if define_split[0] != '[' or define_split[-1] != ']':
                show_log(line, ' '.join(['define_error:', str(define_split)]), 1, bullet=2)
                show_log('', 'Execution_stoped\n', 1, bullet=0)
                raise SystemExit(0)

            define_split_alt = define_split.replace('][', '] [')
            found_def = define_reg.split(define_split_alt)
            try:
                if found_def[0] in defines:
                    show_log(line, ' '.join(['duplicated_define:', found_def[0], defines[found_def[0]]]), 1, bullet=2)
                    show_log('', 'Execution_stoped\n', 1, bullet=0)
                    raise SystemExit(0)
                defines[found_def[0]] = found_def[1][1:-1]
                show_log(line, ' '.join(['Define_found:', found_def[0], found_def[1]]), 3)
            except IndexError:
                show_log(line, ' '.join(['define_error:', str(found_def)]), 1, bullet=2)
                show_log('', 'Execution_stoped\n', 1, bullet=0)
                raise SystemExit(0)

    elif re.match(r'^\s*declare\s+', line_alt, re.IGNORECASE):
        prerv_dignified_command = True
        line_alt = re.sub(r'##.*$', '', line_alt)
        line_alt = re.sub(r'^\s*declare\s+', '', line_alt, flags=re.I).strip()
        if line_alt == '':
            show_log(line, ' '.join(['declare_empty']), 2, bullet=4)
            continue

        declares_split = line_alt.split(',')
        for declare_split in declares_split:
            new_long_var = re.findall(r'^(\w{3,})()(?=$|:([a-z][a-z0-9]?$))', declare_split.strip())
            if not new_long_var:
                show_log(line, ' '.join(['invalid_variable:', declare_split.strip()]), 1, bullet=2)
                show_log('', 'Execution_stoped\n', 1, bullet=0)
                raise SystemExit(0)
            long_var, short_var = get_short_var(new_long_var[0])
            method = '' if new_long_var[0][2] == '' else '(:)'
            show_log(line, ' '.join(['declare_found' + method + ':', long_var, short_var]), 3)

    else:
        prerv_dignified_command = False
        line_alt = re.sub(r'(?![^"]*")(?<!\S)##.*', '', line_alt).rstrip() + '\n'
        # Above line not removing endline ## if there are quotes after it (but preserve ## inside)

        arrayB.append((line_num, line_alt, line_file))
array = arrayB


show_log('', 'Replacing DEFINES and [?@]', 1)
arrayB = []
for line in array:
    line_num, line_alt, line_file = line

    if define_reg_line.findall(line_alt):
        if '[?@]' in line_alt:
            line_alt = re.sub(r'(\[\?@\])(\S+,\S+|\S+)', r'locate' + general_spaces + r'\2:print', line_alt)
            show_log(line, ' '.join(['replaced_[?@]']), 3)

        line_defs = list(set(define_reg_line.findall(line_alt)))
        if line_defs:
            defines_local = []
            for defs in line_defs:
                def_arg = None
                try:
                    def_alt = defines[defs]
                except KeyError as e:
                    show_log(line, ' '.join(['define_not_found:', str(e)]), 2, bullet=4)
                    continue
                def_var = define_reg_local.findall(defines[defs])
                if def_var:
                    def_arg = re.search(r'(?<=\[' + defs[1:-1] + r'\])' + r'\S*?(?=\s|:|$|\[)', line_alt).group(0)
                    if def_arg:
                        def_alt = defines[defs].replace(def_var[0], def_arg)
                    else:
                        def_alt = defines[defs].replace(def_var[0], def_var[0][1:-1])
                if def_arg is None:
                    def_arg = ''
                defines_local.append([defs, def_alt, def_arg])

            for defs in defines_local:
                line_alt = line_alt.replace(defs[0] + defs[2], defs[1])
                show_log(line, ' '.join(['replaced_defines:', defs[0], '->', defs[1]]), 3)

    arrayB.append((line_num, line_alt, line_file))
array = arrayB


show_log('', 'Joining lines with _ and :', 1)
show_log('', 'Removing ENDIFs and line numbers', 1, bullet=0)
arrayB = []
arrayB.append((0, general_rem_format + general_spaces + first_line, 0))
previous_line = ''
prev_line_number = 0
join_line_num = None
for line in array:
    line_num, line_alt, line_file = line

    if re.match(r'^\s*\d', line_alt.lstrip()) and previous_line.rstrip()[-1:] != '_':
        line_alt = re.sub(r'^([0-9 ]+)', '', line_alt)
        if line_alt.strip() == '':
            continue
        show_log(line, ' '.join(['removed_line_number']), 2, bullet=4)

    if re.match(r'(^\s*endif\s*$)', line_alt, re.IGNORECASE):
        show_log(line, ' '.join(['endif_removed']), 3)
        if re.match(r'.*(:|_)$', previous_line):
            previous_line = previous_line[:-1]

    elif re.match(r'.*(:|_)$', previous_line) or re.match(r'^\s*:', line_alt):
        previous_line = re.sub(r'( *)\s*_$', r'\1', previous_line) + re.sub(r'^\s*', '', line_alt).rstrip()
        if not join_line_num:
            join_line_num = line_num

    else:
        if join_line_num:
            arrayB.append((join_line_num - 1, previous_line, line_file))
            endif_line = join_line_num - 1
            show_log((join_line_num - 1, line_alt, line_file), ' '.join(['Joined_line']), 3)
        else:
            arrayB.append((prev_line_number, previous_line, line_file))
            endif_line = prev_line_number

        clean_line = get_clean_line(previous_line)
        if 'endif' in clean_line.lower():
            show_log(endif_line, ' '.join(['endif_not_alone']), 2, bullet=4)

        previous_line = line_alt.rstrip()
        prev_line_number = line_num
        join_line_num = None

arrayB.append((line_num, previous_line, line_file))
arrayB[1] = (0, general_rem_format + general_spaces + second_line, 0)
array = arrayB


show_log('', 'Adding line before and after labels', 1)
if label_lines < 2:
    arrayB = []
    for line in array:
        line_num, line_alt, line_file = line

        label = re.match(r'(^\s*{.+?})', line_alt)
        if label and blank_bef_rem:
            arrayB.append(('0', label_rem_format, line_file))
            show_log(line, ' '.join(['space_before_label:', str(label.group(1)).strip()]), 3)

        arrayB.append(line)

        if label and blank_aft_rem:
            arrayB.append(('0', label_rem_format, line_file))
            show_log(line, ' '.join(['space_after_label:', str(label.group(1)).strip()]), 3)

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
    line_num, line_alt, line_file = line

    label = re.match(r'(^\s*{.+?})', line_alt)
    if label:
        if label.group(1).lstrip() in labels_store:
            show_log(line, ' '.join(['duplicated_label:', label.group(1).lstrip()]), 1, bullet=2)
            show_log('', 'Execution_stoped\n', 1, bullet=0)
            raise SystemExit(0)
        labels_store[label.group(1).lstrip()] = line_current
        show_log(line, ' '.join(['got_label_line:', label.group(1).lstrip(), str(line_current)]), 3)
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

    arrayB.append((line_num, line_alt, line_file))
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
    line_num, line_alt, line_file = line

    quotes = re.findall(r'"[^"]*(?:"|$)', line_alt)
    if quotes:
        for item in quotes:
            # print "--- quote item --->>", item
            stored_quotes.append(item)
            line_alt = line_alt.replace(item, '``' + str(quote_number) + '``')
            show_log(line, ' '.join(['stored_quote:', str(quote_number), str(item)]), 3)
            quote_number += 1

    data = re.findall(r'(?:^|:)\s*(data\s*)(.+?)(?=:|$)', line_alt, re.IGNORECASE)
    if data:
        for item in data:
            # print "--- data item --->", item
            stored_datas.append(item[1])
            line_alt = line_alt.replace(item[0] + item[1], item[0] + '@' + str(data_number) + '@')
            show_log(line, ' '.join(['stored_data:', str(data_number), str(item)]), 3)
            data_number += 1

    remark = re.findall(r'(?:^|:|)\s*(rem|\')(.+)', line_alt, re.IGNORECASE)
    if remark:
        for item in remark:
            # print "--- rem item --->>", item
            stored_comments.append(item[1])
            line_alt = line_alt.replace(item[0] + item[1], item[0] + "|" + str(comment_number) + "|")
            show_log(line, ' '.join(['stored_rem:', str(comment_number), str(item)]), 3)
            comment_number += 1

    arrayB.append((line_num, line_alt, line_file))
array = arrayB


show_log('', 'Storing labels', 1)
arrayB = []
label_number = 0
stored_labels = []
for line in array:
    line_num, line_alt, line_file = line

    labels = re.findall(r'{[^}]*}', line_alt)
    if labels:
        for item in labels:
            if (re.search(r'\W', item[1:-1]) or item[1:-1].isdigit()) and item != "{@}":
                show_log(line, ' '.join(['invalid_label_name:', item]), 1, bullet=2)
                show_log('', 'Execution_stoped\n', 1, bullet=0)
                raise SystemExit(0)
            stored_labels.append(item)
            line_alt = line_alt.replace(item, '{' + str(label_number) + '}')
            show_log(line, ' '.join(['stored_label:', str(label_number), str(item)]), 3)
            label_number += 1

    arrayB.append((line_num, line_alt, line_file))
array = arrayB

show_log('', 'Replacing long variables', 1)
# First get all new declared variables
arrayB = []
for line in array:
    line_num, line_alt, line_file = line
    new_long_vars = re.findall(r'~(\w{3,})([!%#$]?())', line_alt, re.IGNORECASE)
    if new_long_vars:
        for new_long_var in new_long_vars:
            long_var, short_var = get_short_var(new_long_var)
            line_alt = line_alt.replace('~' + long_var, short_var)
            show_log(line, ' '.join(['replaced_variable(~):', long_var, "->", short_var]), 3)
    arrayB.append((line_num, line_alt, line_file))
array = arrayB

# Then go through all the variables again
arrayB = []
for line in array:
    line_num, line_alt, line_file = line
    lone_words = re.findall(r'(\w{3,})([!%#$]?)', line_alt, re.IGNORECASE)
    if lone_words:
        for lone_word in lone_words:
            if lone_word[0] in var_dict:
                line_alt = line_alt.replace(lone_word[0], var_dict[lone_word[0]])
                show_log(line, ' '.join(['replaced_variable:', lone_word[0] + lone_word[1], "->", var_dict[lone_word[0]] + lone_word[1]]), 3)
    arrayB.append((line_num, line_alt, line_file))
array = arrayB


show_log('', 'Removing THEN/GOTO, Converting ? to PRINT. True and False', 1)
show_log('', 'Capitalizing, converting REMs, adjusting spaces', 1, bullet=0)
show_log('', 'preserving X OR, T OR and changing spaces around :', 1, bullet=0)
arrayB = []
for line in array:
    line_num, line_alt, line_file = line

    then_goto = re.findall(r'(then|else)(\s*)(goto)', line_alt, re.IGNORECASE)
    if then_goto:
        for item in then_goto:
            if strip_then_goto == 'T' and 'else' != item[0]:
                line_alt = line_alt.replace(item[0], '')
                show_log(line, ' '.join(['removed_then']), 3)
            if strip_then_goto == 'G':
                line_alt = line_alt.replace(item[2], '')
                show_log(line, ' '.join(['removed_goto']), 3)

    if convert_print:
        prints = re.findall(r'(?:^|:)\s*(\?)', line_alt)
        if prints:
            line_alt = line_alt.replace('?', print_format)
            show_log(line, ' '.join(['converted_?:', str(len(prints)) + 'x']), 3)

    true_false = re.findall(r'(true|false)', line_alt, re.IGNORECASE)
    if true_false:
        line_alt = line_alt.replace('true', '-1')
        line_alt = line_alt.replace('false', '0')

    if capitalise_all:
        line_alt = line_alt.upper()

    if not keep_spaces:
        if len(general_spaces) == 0 and re.findall(r'(x|t) or', line_alt, flags=re.IGNORECASE):
            line_alt = re.sub(r'(x|t)( )(or)', r'\1|^|\3', line_alt, flags=re.IGNORECASE)
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

    arrayB.append((line_num, line_alt, line_file))
array = arrayB


show_log('', 'Restoring labels', 1)
arrayB = []
for line in array:
    line_num, line_alt, line_file = line

    labels = re.findall(r'{[^}]*}', line_alt)
    if labels:
        for item in labels:
            label = stored_labels[int(item[1:-1])]
            line_alt = line_alt.replace(item, label)
            show_log(line, ' '.join(['restored_label:', item[1:-1], label]), 3)

    arrayB.append((line_num, line_alt, line_file))
array = arrayB


show_log('', 'REMarking line labels, replacing branching labels and storing its REMs', 1)
arrayB = []
branching_labels = []
for line, number in zip(array, line_numbers):
    line_num, line_alt, line_file = line
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
                    show_log(line, ' '.join(['replaced_label:', item, str(labels_store[item])]), 3)
                except KeyError:
                    show_log(line, ' '.join(['label_not_found:', item]), 1, bullet=2)
                    show_log('', 'Execution_stoped\n', 1, bullet=0)
                    raise SystemExit(0)
            elif item == '{@}':
                line_alt = line_alt.replace('{@}', str(number))
                append_label += general_spaces + '{SELF}'
                show_log(line, ' '.join(['replaced_label:', item, number]), 3)

        if not show_labels:
            append_label = ''

    branching_labels.append(append_label)

    arrayB.append((line_num, line_alt, line_file))
array = arrayB


show_log('', 'Restoring quotes, DATAs and REMs', 1)
arrayB = []
for line in array:
    line_num, line_alt, line_file = line

    remarks = re.findall(r'(?:\'|rem)\s*(\|\d*\|)', line_alt, re.IGNORECASE)
    if remarks:
        for item in remarks:
            remark = stored_comments[int(item[1:-1])]
            line_alt = line_alt.replace(item, remark)
            show_log(line, ' '.join(['restored_comments:', item[1:-1], remark]), 3)

    datas = re.findall(r'(@\d+@)', line_alt, re.IGNORECASE)
    if datas:
        for item in datas:
            data = stored_datas[int(item[1:-1])]
            line_alt = line_alt.replace(item, data)
            show_log(line, ' '.join(['restored_data:', item[1:-1], data]), 3)

    quotes = re.findall(r'``\d+``', line_alt)
    if quotes:
        for item in quotes:
            quote = stored_quotes[int(item[2:-2])]
            line_alt = line_alt.replace(item, quote)
            show_log(line, ' '.join(['restored_quote:', item[2:-2], quote]), 3)

    arrayB.append((line_num, line_alt, line_file))
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
            array.append((extra_lines, report_line[0:-2], 0))
            report_line = general_rem_format + general_spaces
            last_line += line_step
            line_numbers.append(str(last_line))
            ident_sizes.append('')
            branching_labels.append('')
        n += 1
    if report_line != general_rem_format + general_spaces:
        extra_lines += 1
        array.append((extra_lines, report_line[0:-2], 0))
        last_line += line_step
        line_numbers.append(str(last_line))
        ident_sizes.append('')
        branching_labels.append('')


show_log('', 'Adding line numbers and indent, applying label REMs', 1)
show_log('', 'Converting CR and checking line size', 1, bullet=0)
arrayB = []
for line, number, ident, blabel in zip(array, line_numbers, ident_sizes, branching_labels):
    line_num, line_alt, line_file = line

    line_alt = number + ' ' + ident + line_alt + blabel.rstrip() + '\r\n'

    line_lenght = len(line_alt) - 1
    if line_lenght > 256:
        show_log(line, ' '.join(['line_too_long:', str(line_lenght) + ' chars']), 1, bullet=2)
        show_log('', 'Execution_stoped\n', 1, bullet=0)
        raise SystemExit(0)

    arrayB.append(line_alt)
array = arrayB

show_log('', '', 1, bullet=0)

try:
    with open(file_save, 'w') as f:
        for c in range(len(array)):
            f.write(array[c])
except IOError:
    show_log('', ' '.join(['destination_folder_not_found:', file_save]), 1, bullet=2)
    show_log('', 'Execution_stoped\n', 1, bullet=0)
    raise SystemExit(0)

# end = time.time()
# print(end - start)
# raise SystemExit(0)
