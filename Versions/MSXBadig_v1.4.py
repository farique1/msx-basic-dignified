"""
MSX Basic Dignified
v1.4
Convert modern MSX Basic Dignified to traditional MSX Basic format.

Copyright (C) 2019-2020 - Fred Rique (farique)
https://github.com/farique1/msx-basic-dignified

Better experienced with MSX Sublime Tools at:
https://github.com/farique1/MSX-Sublime-Tools
Syntax Highlight, Theme, Build System, Comment Preference and Auto Completion.

MSX Basic Tokenizer at
https://github.com/farique1/MSX-Basic-Tokenizer

msxbadig.py <source> <destination> [args...]
msxbadig.py -h for help.

New: 18-1-2020 v1.4
    Added integration with MXS Basic Tonekizer and openMSX Basic (de)Tokenizer to export tokenized code.
        Verbose setting propagate down to tokenizers.
    Added ability to monitor the Basic program execution on openMSX after the conversion.
        Will catch error messages, display them on Sublime and tag the offending line.
    Better integration with MSX Sublime Tools' build system.
    Better -fb (from build) argument handling.
    Verbose level redefined to: 0 silent, 1 errors, 2 +warnings, 3 +steps, 4 +details
    Fixed bug offsetting lines on INCLUDEd code by 1.
    Fixed a bug with uppercase true and false.
    Several log improvements.

Known bugs:
    Not removing end line ## if there are quotes after it
    Leading number on a REM line broken with : being removed (if the line is a REM they don't need to be removed)
    All lone endifs being removed even after a _ line break on a DATA or REM line (implicating they are not endifs but part of the instruction)
"""

# Use on terminal for benchmarking
# for run in {1..100}; do  python msxbadig.py cgk-source.bas cgk-conv.bas -vb 0; done > test.txt

import re
import os.path
import argparse
import subprocess
import ConfigParser
from itertools import izip_longest
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
strip_then_goto = 'k'       # Strip adjacent THEN/ELSE or GOTO: t-THEN/ELSE g-GOTO
output_format = 'b'         # Tokenized or ASCII output: t-tokenized a-ASCII b-both
export_list = 0             # Save a .mlt list file detailing the tokenization: [#] number of bytes per line (def 16) (max 32) (0 no)
tokenize_tool = 'b'         # Tool used to tokenize the ASCII code: b-MSX Basic Tokenizer(def) o-openMSX Basic Tokenizer
long_var_summary = 0        # Show long variables summary on rems at the end of the program (0-none 1+-var per line)
verbose_level = 3           # Show processing status: 0-silent 1-+erros 2-+warnings 3-+steps 4-+details
is_from_build = False       # Tell if it is being called from a build system (show file name on error messages and other stuff)
monitor_exec = False        # Monitor the execution on the emulator and catch errors (only works with From Build)
batoken_filepath = ''       # Path to MSX Basic Tokenizer ('' = local path)
openbatoken_filepath = ''   # Path to openMSX Basic Tokenizer ('' = local path)


def show_log(line, text, level, **kwargs):
    bullets = ['', '*** ', '  * ', '--- ', '  - ', '    ']

    if line != '':
        line_num, line_alt, line_file = line
    else:
        line_num, line_file = '', ''

    try:
        bullet = kwargs['bullet']
    except KeyError:
        bullet = level

    display_file_name = ''
    if is_from_build and line_file != '' and (bullet == 1 or bullet == 2):
        display_file_name = included_dict[line_file] + ': '

    line_num = '(' + str(line_num) + '): ' if line_num != '' else ''

    if verbose_level >= level:
        print bullets[bullet] + display_file_name + line_num + text

    if bullet == 1:
        print '    Execution_stoped'
        raise SystemExit(0)


local_path = os.path.split(os.path.abspath(__file__))[0] + '/'
if os.path.isfile(local_path + 'msxbadig.ini'):
    config = ConfigParser.ConfigParser()
    config.sections()
    try:
        config.read(local_path + 'msxbadig.ini')
        use_Ini_File = config.getboolean('DEFAULT', 'Use_Ini_File') if config.get('DEFAULT', 'Use_Ini_File') else False
        if use_Ini_File:
            file_load = config.get('DEFAULT', 'Source_File') if config.get('DEFAULT', 'Source_File') else file_load
            file_save = config.get('DEFAULT', 'Destin_File') if config.get('DEFAULT', 'Destin_File') else file_save
            line_start = config.getint('DEFAULT', 'Line_Start') if config.get('DEFAULT', 'Line_Start') else line_start
            line_step = config.getint('DEFAULT', 'Line_Step') if config.get('DEFAULT', 'Line_Step') else line_step
            leading_zero = config.getboolean('DEFAULT', 'Leading_Zeros') if config.get('DEFAULT', 'Leading_Zeros') else leading_zero
            space_bef_colon = config.getint('DEFAULT', 'Nnbr_Spaces_Bef_Colon') if config.get('DEFAULT', 'Nnbr_Spaces_Bef_Colon') else space_bef_colon
            space_aft_colon = config.getint('DEFAULT', 'Nnbr_Spaces_Aft_Colon') if config.get('DEFAULT', 'Nnbr_Spaces_Aft_Colon') else space_aft_colon
            general_spaces = config.getint('DEFAULT', 'Nmbr_Spaces_General') if config.get('DEFAULT', 'Nmbr_Spaces_General') else general_spaces
            keep_spaces = config.getboolean('DEFAULT', 'Keep_Original_Spaces') if config.get('DEFAULT', 'Keep_Original_Spaces') else keep_spaces
            unpack_operators = config.getboolean('DEFAULT', 'Unpack_Operators') if config.get('DEFAULT', 'Unpack_Operators') else unpack_operators
            keep_blank_lines = config.getboolean('DEFAULT', 'Keep_Blank_Lines') if config.get('DEFAULT', 'Keep_Blank_Lines') else keep_blank_lines
            blank_bef_rem = config.getboolean('DEFAULT', 'REM_Bef_Label') if config.get('DEFAULT', 'REM_Bef_Label') else blank_bef_rem
            blank_aft_rem = config.getboolean('DEFAULT', 'REM_Aft_Label') if config.get('DEFAULT', 'REM_Aft_Label') else blank_aft_rem
            show_labels = config.getboolean('DEFAULT', 'Show_Branches_Labels') if config.get('DEFAULT', 'Show_Branches_Labels') else show_labels
            label_lines = config.getint('DEFAULT', 'Handle_Label_Lines') if config.get('DEFAULT', 'Handle_Label_Lines') else label_lines
            label_rem_format = config.get('DEFAULT', 'Label_REM_Format') if config.get('DEFAULT', 'Label_REM_Format') else label_rem_format
            general_rem_format = config.get('DEFAULT', 'Regul_REM_Format') if config.get('DEFAULT', 'Regul_REM_Format') else general_rem_format
            convert_rems = config.getboolean('DEFAULT', 'Convert_REM_Formats') if config.get('DEFAULT', 'Convert_REM_Formats') else convert_rems
            keep_indent = config.getboolean('DEFAULT', 'Keep_Indent') if config.get('DEFAULT', 'Keep_Indent') else keep_indent
            keep_indent_spaces = config.getboolean('DEFAULT', 'Keep_Indent_Space_Chars') if config.get('DEFAULT', 'Keep_Indent_Space_Chars') else keep_indent_spaces
            ident_tab_size = config.getint('DEFAULT', 'Indent_TAB_Spaces') if config.get('DEFAULT', 'Indent_TAB_Spaces') else ident_tab_size
            capitalise_all = config.getboolean('DEFAULT', 'Capitalize_All') if config.get('DEFAULT', 'Capitalize_All') else capitalise_all
            convert_print = config.getboolean('DEFAULT', 'Convert_Interr_To_Print') if config.get('DEFAULT', 'Convert_Interr_To_Print') else convert_print
            strip_then_goto = config.get('DEFAULT', 'Strip_Then_Goto') if config.get('DEFAULT', 'Strip_Then_Goto') else strip_then_goto
            output_format = config.get('DEFAULT', 'Output_format') if config.get('DEFAULT', 'Output_format') else output_format
            export_list = config.getint('DEFAULT', 'Export_list') if config.get('DEFAULT', 'Export_list') else export_list
            tokenize_tool = config.get('DEFAULT', 'Tokenize_tool') if config.get('DEFAULT', 'Tokenize_tool') else tokenize_tool
            long_var_summary = config.getint('DEFAULT', 'Long_Var_Summary') if config.get('DEFAULT', 'Long_Var_Summary') else long_var_summary
            verbose_level = config.getint('DEFAULT', 'Verbose_Level') if config.get('DEFAULT', 'Verbose_Level') else verbose_level
            batoken_filepath = config.get('DEFAULT', 'Batoken_filepath') if config.get('DEFAULT', 'Batoken_filepath') else batoken_filepath
            openbatoken_filepath = config.get('DEFAULT', 'openBatoken_filepath') if config.get('DEFAULT', 'openBatoken_filepath') else openbatoken_filepath
    except (ValueError, ConfigParser.NoOptionError) as e:
        show_log('', 'msxbadig.ini: ' + str(e), 1)

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
parser.add_argument("-of", default=output_format, choices=['t', 'T', 'a', 'A', 'b', 'B'], help="Tokenized or ASCII output: t-tokenized a-ASCII b-both(def)")
parser.add_argument("-el", default=export_list, const=16, type=int, nargs='?', help="Save a .mlt list file detailing the tokenization: [#] number of bytes per line (def 16) (max 32) (0 no)")
parser.add_argument("-tt", default=tokenize_tool, choices=['b', 'B', 'o', 'O'], help="Tool used to tokenize the ASCII code: b-MSX Basic Tokenizer(def) o-openMSX Basic Tokenizer")
parser.add_argument("-vs", default=long_var_summary, type=int, nargs='?', help="Show long variables summary on REMs at the end of the program: 0 none(def), 1+ vars per line")
parser.add_argument("-vb", default=verbose_level, type=int, help="Verbosity level: 0 silent, 1 errors, 2 +warnings, 3 +steps(def), 4 +details")
parser.add_argument("-exe", default=monitor_exec, action='store_true', help="Send line info to build system to catch errors during execution (only with From Build)")
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
    config.set('DEFAULT', 'Output_format', output_format)
    config.set('DEFAULT', 'Export_list', export_list)
    config.set('DEFAULT', 'Tokenize_tool', tokenize_tool)
    config.set('DEFAULT', 'Long_Var_Summary', long_var_summary)
    config.set('DEFAULT', 'Verbose_Level', verbose_level)
    config.set('DEFAULT', 'Batoken_filepath', batoken_filepath)
    config.set('DEFAULT', 'openBatoken_filepath', openbatoken_filepath)
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
output_format = args.of.upper()
export_list = min(abs(args.el), 32)
tokenize_tool = 'O' if args.tt.upper() == 'O' else 'B'
if args.vs is None:
    long_var_summary = 5
else:
    long_var_summary = args.vs
verbose_level = args.vb
monitor_exec = args.exe
is_from_build = args.fb
if batoken_filepath == '':
    batoken_filepath = local_path + 'MSXBatoken.py'
if openbatoken_filepath == '':
    openbatoken_filepath = local_path + 'openMSXBatoken.py'
if tokenize_tool == 'O':
    batoken_filepath = openbatoken_filepath

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


def get_short_var(get_long_var):
    global short_cur
    global var_dict

    # Test if variable has invalid characters
    long_var = get_long_var[0]
    var_type = get_long_var[1]
    short_var = get_long_var[2]

    if re.search(r'\W', long_var) or long_var.isdigit() or len(long_var) < 3 or long_var.strip() == '':
        show_log(line, ' '.join(['invalid_variable_name:', long_var]), 1)  # Exit

    if short_var == '':
        if long_var in var_dict:
            show_log(line, ' '.join(['variable_already_declared:', long_var + var_type, var_dict[long_var] + var_type]), 2)
            return long_var, var_dict[long_var]
    else:
        if long_var in var_dict:
            if var_dict[long_var] == short_var:
                show_log(line, ' '.join(['variable_already_declared:', long_var, var_dict[long_var]]), 2)
                return long_var, var_dict[long_var]
            else:
                show_log(line, ' '.join(['long_name_already_declared:', long_var, short_var, '(' + var_dict[long_var] + ')']), 1)  # Exit
        for long_V, short_V in var_dict.iteritems():
            if short_var == short_V:
                show_log(line, ' '.join(['short_name_already_declared:', long_var, short_V, '(' + long_V + ')']), 1)  # Exit
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
            show_log(line, ' '.join(['out_of_short_variable_names:', long_var]), 1)  # Exit
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
        show_log('', ' '.join(['load_file:', file_load]), 4)
        try:
            with open(file_load, 'r') as f:
                for i, line in enumerate(f):
                    array.append((i + 1, line, line_file))
            return array
        except IOError:
            show_log(line, ' '.join([file_type + '_not_found:', file_load]), 1)  # Exit
    else:
        show_log('', file_type + '_not_given', 1)  # Exit


show_log('', '', 3, bullet=0)

show_log('', 'Loading file', 3)
array = load_file(file_load, 0, '', "source")

show_log('', 'INCLUDing external code', 3)
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
            show_log(line, ' '.join(['file_included:', file_include[0]]), 4)
            continue
        else:
            show_log(line, ' '.join(['no_include_given']), 1)  # Exit

    arrayB.append((line_num, line_alt, line_file))
array = arrayB


show_log('', 'Removing ## and trailing spaces', 3)
show_log('', 'Deleting or REMarking blank lines', 3, bullet=5)
show_log('', 'Storing and deleting DEFINE lines', 3, bullet=5)
show_log('', 'Storing and deleting DECLARE lines', 3, bullet=5)
show_log('', 'Storing and labelizing FUNC lines', 3, bullet=5)
arrayB = []
defines = {}
prerv_dignified_command = False
define_reg = re.compile(r'(?<=\])\s*(?=\[)')
define_reg_line = re.compile(r'(\[[^\]]+\])')
define_reg_local = re.compile(r'(\[[^\]]*\])')
define_reg_split = re.compile(r'(?<=\])\s*,\s*(?=\[)')
proto_functions = {}
found_proto_func = False
prev_proto_func_name = ''
prev_proto_func_line = 0
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
                show_log(line, ' '.join(['define_error:', str(define_split)]), 1)  # Exit

            define_split_alt = define_split.replace('][', '] [')
            found_def = define_reg.split(define_split_alt)
            try:
                if found_def[0] in defines:
                    show_log(line, ' '.join(['duplicated_define:', found_def[0], defines[found_def[0]]]), 1)  # Exit
                defines[found_def[0]] = found_def[1][1:-1]
                show_log(line, ' '.join(['Define_found:', found_def[0], found_def[1]]), 4)
            except IndexError:
                show_log(line, ' '.join(['define_error:', str(found_def)]), 1)  # Exit

    elif re.match(r'^\s*declare\s+', line_alt, re.IGNORECASE):
        prerv_dignified_command = True
        line_alt = re.sub(r'##.*$', '', line_alt)
        line_alt = re.sub(r'^\s*declare\s+', '', line_alt, flags=re.I).strip()
        if line_alt == '':
            show_log(line, ' '.join(['declare_empty']), 2)
            continue

        declares_split = line_alt.split(',')
        for declare_split in declares_split:
            new_long_var = re.findall(r'^(\w{3,})()(?=$|:([a-z][a-z0-9]?$))', declare_split.strip())
            if not new_long_var:
                show_log(line, ' '.join(['invalid_variable:', declare_split.strip()]), 1)  # Exit
            long_var, short_var = get_short_var(new_long_var[0])
            method = '' if new_long_var[0][2] == '' else '(:)'
            show_log(line, ' '.join(['declare_found' + method + ':', long_var, short_var]), 4)

    elif re.match(r'^\s*func\s+\.\w+', line_alt, re.IGNORECASE):
        new_proto_func = re.match(r'(?:^\s*func\s+)(\.\w+)(?:\()(.*(?=\)))\)(.*$)', line_alt, re.IGNORECASE)
        if new_proto_func:
            if found_proto_func:
                line = prev_proto_func_line, line_alt, line_file
                show_log(line, ' '.join(['func_without_return:', prev_proto_func_name]), 1)  # Exit

            proto_func_name = new_proto_func.group(1)
            proto_func_var = new_proto_func.group(2).replace(' ', '').split(',')
            prev_proto_func_name = proto_func_name
            prev_proto_func_line = line_num
            proto_func_line_end = '' if re.match(r'(^\s*##.*$)', new_proto_func.group(3)) else new_proto_func.group(3)

            arrayB.append((line_num, '{' + proto_func_name[1:] + '}' + proto_func_line_end, line_file))
            show_log(line, ' '.join(['func_found:', prev_proto_func_name, new_proto_func.group(2).replace(' ', '')]), 4)
            found_proto_func = True

    elif found_proto_func and re.match(r'^\s*:?\s*return\s+', line_alt, re.IGNORECASE):
        proto_func_return = re.match(r'(?:^\s*(:?)\s*return\s+)(.*?(?=(:| _|$)))(:| _)?', line_alt, re.IGNORECASE)
        if proto_func_return:
            proto_func_return_vars = proto_func_return.group(2).replace(' ', '').split(',')
            proto_functions[proto_func_name] = (proto_func_var, proto_func_return_vars)
            arrayB.append((line_num, proto_func_return.group(1) + 'return' + proto_func_return.group(3), line_file))
            show_log(line, ' '.join(['func_return_found:', prev_proto_func_name, proto_func_return.group(2).replace(' ', '')]), 4)
            found_proto_func = False

    else:
        prerv_dignified_command = False
        line_alt = re.sub(r'(?![^"]*")(?<!\S)##.*', '', line_alt).rstrip() + '\n'
        # Above line not removing endline ## if there are quotes after it (but preserve ## inside)

        arrayB.append((line_num, line_alt, line_file))

if found_proto_func:
    line = prev_proto_func_line, line_alt, line_file
    show_log(line, ' '.join(['func_without_return:', prev_proto_func_name]), 1)  # Exit

array = arrayB


show_log('', 'Replacing proto-function calls with GOSUBs and vars', 3)
arrayB = []
for line in array:
    line_num, line_alt, line_file = line

    proto_func_call = re.findall(r'(\.\w+)\(.*?\)', line_alt)
    if proto_func_call:

        for functions in range(0, len(proto_func_call)):
            proto_func_call = re.findall(r'(\.\w+)\(.*?\)', line_alt)
            curr_func = proto_func_call[0]
            if curr_func in proto_functions.keys():

                proto_func_find_elements = re.findall(r'^(.*?\s*)(\=)?\s*' + curr_func + r'\((.*?)\)(.*$)', line_alt)
                if proto_func_find_elements[0][1] == '=':
                    func_line_start = re.match(r'(.*(?:^|then|else|:)\s*)(.*)', proto_func_find_elements[0][0], re.IGNORECASE)
                    proto_func_call_elements = [func_line_start.group(2), proto_func_find_elements[0][2]]
                    proto_func_call_line = [func_line_start.group(1), proto_func_find_elements[0][3]]
                else:
                    proto_func_call_elements = [proto_func_find_elements[0][1], proto_func_find_elements[0][2]]
                    proto_func_call_line = [proto_func_find_elements[0][0], proto_func_find_elements[0][3]]

                proto_func_call_return = proto_func_call_elements[0].replace(' ', '').split(',')
                proto_func_call_variables = proto_func_call_elements[1].replace(' ', '').split(',')
                proto_functions[curr_func] = (proto_functions[curr_func][0], proto_functions[curr_func][1], proto_func_call_variables, proto_func_call_return)

                func_line = ''
                func_colon = space_bef_colon + ':' + space_aft_colon
                func_oper = ' ' if unpack_operators else ''

                for i in range(0, 2):  # do the function calling vars and return vars
                    for fdef_var, fcal_var in izip_longest(proto_functions[curr_func][i], proto_functions[curr_func][i + 2]):

                        if i == 1:
                            fdef_var, fcal_var = fcal_var, fdef_var

                        if fcal_var is None or fdef_var is None:
                            show_log(line, ' '.join(['func_require_' + str(len(proto_functions[curr_func][i])) + '_args:', curr_func]), 1)  # Exit

                        fcal_var = fcal_var.replace(' ', '')
                        fdef_var = fdef_var.replace(' ', '')
                        has_def = True if '=' in fdef_var else False

                        if fcal_var.replace('~', '') != fdef_var.split('=')[0].replace('~', ''):
                            if fcal_var == '' and has_def and i == 0:
                                fcal_var = fdef_var.split('=')[1]
                                fdef_var = fdef_var.split('=')[0]
                                if fcal_var.replace('~', '') != fdef_var.replace('~', ''):
                                    func_line += fdef_var + func_oper + '=' + func_oper + fcal_var + func_colon
                            elif fcal_var == '' or fdef_var == '':
                                show_log(line, ' '.join(['func_missing_arg:', curr_func]), 1)  # Exit
                            else:
                                fdef_var = fdef_var.split('=')[0]
                                func_line += fdef_var + func_oper + '=' + func_oper + fcal_var + func_colon

                    if i == 0:
                        func_line += 'gosub' + general_spaces + '{' + curr_func[1:] + '}' + func_colon

                line_alt = proto_func_call_line[0] + func_line[:-len(func_colon)] + proto_func_call_line[1]
                show_log(line, ' '.join(['func_call_found:', proto_func_call_elements[0].replace(' ', ''), curr_func, proto_func_call_elements[1].replace(' ', '')]), 4)
            else:
                show_log(line, ' '.join(['func_not_defined:', curr_func]), 1)  # Exit

    arrayB.append((line_num, line_alt, line_file))

array = arrayB


show_log('', 'Replacing DEFINES and [?@]', 3)
arrayB = []
for line in array:
    line_num, line_alt, line_file = line

    if define_reg_line.findall(line_alt):
        if '[?@]' in line_alt:
            line_alt = re.sub(r'(\[\?@\])(\S+,\S+|\S+)', r'locate' + general_spaces + r'\2:print', line_alt)
            show_log(line, ' '.join(['replaced_[?@]']), 4)

        line_defs = re.findall(r'(\[[^\]]+\])(\S*?)(?=\s|:|$|\[)', line_alt, re.IGNORECASE)
        line_defs = list(set(line_defs))
        if line_defs:
            defines_local = []
            for defs in line_defs:
                def_arg = None
                try:
                    def_alt = defines[defs[0]]
                except KeyError as e:
                    show_log(line, ' '.join(['define_not_found:', str(e)]), 2)
                    continue
                def_var = define_reg_local.findall(defines[defs[0]])
                def_var = None if not def_var else def_var[0]
                def_arg = defs[1]
                if def_var:
                    if def_arg:
                        def_alt = defines[defs[0]].replace(def_var, def_arg)
                    else:
                        def_alt = defines[defs[0]].replace(def_var, def_var[1:-1])
                else:
                    def_arg = ''
                defines_local.append([defs[0], def_alt, def_arg])

            for def_local in defines_local:
                line_alt = line_alt.replace(def_local[0] + def_local[2], def_local[1])
                show_log(line, ' '.join(['replaced_defines:', defs[0], '->', defs[1]]), 4)

    arrayB.append((line_num, line_alt, line_file))
array = arrayB


show_log('', 'Joining lines with _ and :', 3)
show_log('', 'Removing ENDIFs and line numbers', 3, bullet=5)
arrayB = []
arrayB.append((0, general_rem_format + general_spaces + first_line, 0))
previous_line = ''
prev_line_number = 0
prev_line_file = 0
join_line_num = None
for line in array:
    line_num, line_alt, line_file = line

    if re.match(r'^\s*\d', line_alt.lstrip()) and previous_line.rstrip()[-1:] != '_':
        line_alt = re.sub(r'^([0-9 ]+)', '', line_alt)
        if line_alt.strip() == '':
            continue
        show_log(line, ' '.join(['removed_line_number']), 2)

    if re.match(r'(^\s*endif\s*$)', line_alt, re.IGNORECASE):
        show_log(line, ' '.join(['endif_removed']), 4)
        if re.match(r'.*(:|_)$', previous_line):
            previous_line = previous_line[:-1]

    elif re.match(r'.*(:|_)$', previous_line) or re.match(r'^\s*:', line_alt):
        previous_line = re.sub(r'( *)\s*_$', r'\1', previous_line) + re.sub(r'^\s*', '', line_alt).rstrip()
        if not join_line_num:
            join_line_num = line_num

    else:
        if join_line_num:
            arrayB.append((join_line_num - 1, previous_line, prev_line_file))
            endif_line = join_line_num - 1
            show_log((join_line_num - 1, line_alt, prev_line_file), ' '.join(['Joined_line']), 4)
        else:
            arrayB.append((prev_line_number, previous_line, prev_line_file))
            endif_line = prev_line_number

        clean_line = get_clean_line(previous_line)
        if 'endif' in clean_line.lower():
            show_log(endif_line, ' '.join(['endif_not_alone']), 2)

        previous_line = line_alt.rstrip()
        prev_line_number = line_num
        prev_line_file = line_file
        join_line_num = None

arrayB.append((line_num, previous_line, line_file))
arrayB[1] = (0, general_rem_format + general_spaces + second_line, 0)
array = arrayB


show_log('', 'Adding line before and after labels', 3)
if label_lines < 2:
    arrayB = []
    for line in array:
        line_num, line_alt, line_file = line

        label = re.match(r'(^\s*{.+?})', line_alt)
        if label and blank_bef_rem:
            arrayB.append(('0', label_rem_format, line_file))
            show_log(line, ' '.join(['space_before_label:', str(label.group(1)).strip()]), 4)

        arrayB.append(line)

        if label and blank_aft_rem:
            arrayB.append(('0', label_rem_format, line_file))
            show_log(line, ' '.join(['space_after_label:', str(label.group(1)).strip()]), 4)

    array = arrayB


show_log('', 'Getting line numbers, indent sizes and label positions', 3)
show_log('', 'Removing leading spaces', 3, bullet=5)
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

    label = re.match(r'(^\s*{.+?})(.*$)', line_alt)
    if label:
        if label.group(1).lstrip() in labels_store:
            show_log(line, ' '.join(['duplicated_label:', label.group(1).lstrip()]), 1)  # Exit
        labels_store[label.group(1).lstrip()] = line_current
        show_log(line, ' '.join(['got_label_line:', label.group(1).lstrip(), str(line_current)]), 4)
        if label_lines == 1:
            label_line_end = label.group(2).lstrip()[1:] if label.group(2).lstrip()[:1] == "'" else label.group(2)
            line_alt = label_rem_format + label_line_end
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


show_log('', 'Storing REMs, DATAs and quotes', 3)
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
            show_log(line, ' '.join(['stored_quote:', str(quote_number), str(item)]), 4)
            quote_number += 1

    data = re.findall(r'(?:^|:)\s*(data\s*)(.+?)(?=:|$)', line_alt, re.IGNORECASE)
    if data:
        for item in data:
            # print "--- data item --->", item
            stored_datas.append(item[1])
            line_alt = line_alt.replace(item[0] + item[1], item[0] + '@' + str(data_number) + '@')
            show_log(line, ' '.join(['stored_data:', str(data_number), str(item)]), 4)
            data_number += 1

    remark = re.findall(r'((?:^|:)\s*rem|(?:^|:|)\s*\')(.+)', line_alt, re.IGNORECASE)
    if remark:
        for item in remark:
            # print "  - rem item --->>", item
            stored_comments.append(item[1])
            line_alt = line_alt.replace(item[0] + item[1], item[0] + "|" + str(comment_number) + "|")
            show_log(line, ' '.join(['stored_rem:', str(comment_number), str(item)]), 4)
            comment_number += 1

    arrayB.append((line_num, line_alt, line_file))
array = arrayB


show_log('', 'Storing labels', 3)
arrayB = []
label_number = 0
stored_labels = []
for line in array:
    line_num, line_alt, line_file = line

    labels = re.findall(r'{[^}]*}', line_alt)
    if labels:
        for item in labels:
            if (re.search(r'\W', item[1:-1]) or item[1:-1].isdigit()) and item != "{@}":
                show_log(line, ' '.join(['invalid_label_name:', item]), 1)
            stored_labels.append(item)
            line_alt = line_alt.replace(item, '{' + str(label_number) + '}')
            show_log(line, ' '.join(['stored_label:', str(label_number), str(item)]), 4)
            label_number += 1

    arrayB.append((line_num, line_alt, line_file))
array = arrayB


show_log('', 'Replacing long variables', 3)
# First get all new declared variables
arrayB = []
for line in array:
    line_num, line_alt, line_file = line
    new_long_vars = re.findall(r'~(\w{3,})([!%#$]?())', line_alt, re.IGNORECASE)
    if new_long_vars:
        for new_long_var in new_long_vars:
            long_var, short_var = get_short_var(new_long_var)
            line_alt = line_alt.replace('~' + long_var, short_var)
            show_log(line, ' '.join(['replaced_variable(~):', long_var, "->", short_var]), 4)
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
                line_alt = re.sub(r'((?<=^)|(?<=\W))' + lone_word[0] + r'(?=\W|$)', var_dict[lone_word[0]], line_alt)
                show_log(line, ' '.join(['replaced_variable:', lone_word[0] + lone_word[1], "->", var_dict[lone_word[0]] + lone_word[1]]), 4)
    arrayB.append((line_num, line_alt, line_file))
array = arrayB


show_log('', 'Removing THEN/GOTO, Converting ? to PRINT. True and False', 3)
show_log('', 'Capitalizing, converting REMs, adjusting spaces', 3, bullet=5)
show_log('', 'preserving X OR, T OR and changing spaces around :', 3, bullet=5)
arrayB = []
for line in array:
    line_num, line_alt, line_file = line

    then_goto = re.findall(r'(then|else)(\s*)(goto)', line_alt, re.IGNORECASE)
    if then_goto:
        for item in then_goto:
            if strip_then_goto == 'T' and 'else' != item[0]:
                line_alt = line_alt.replace(item[0], '')
                show_log(line, ' '.join(['removed_then']), 4)
            if strip_then_goto == 'G':
                line_alt = line_alt.replace(item[2], '')
                show_log(line, ' '.join(['removed_goto']), 4)

    if convert_print:
        prints = re.findall(r'(?:^|:)\s*(\?)', line_alt)
        if prints:
            line_alt = line_alt.replace('?', print_format)
            show_log(line, ' '.join(['converted_?:', str(len(prints)) + 'x']), 4)

    true_false = re.findall(r'(true|false)', line_alt, re.IGNORECASE)
    if true_false:
        line_alt = re.sub('true', '-1', line_alt, flags=re.IGNORECASE)
        line_alt = re.sub('false', '0', line_alt, flags=re.IGNORECASE)

    comp_oper = re.findall(r'(\w+\$?(?:\(.*\))?)(\s*)(\+\=|\-\=|\*\=|\/\=|\^\=)', line_alt, re.IGNORECASE)
    if comp_oper:
        for items in comp_oper:
            line_alt = line_alt.replace(items[0] + items[1] + items[2], items[0] + items[1] + '=' + items[1] + items[0] + items[1] + items[2][:1])

    arit_oper = re.findall(r'(\w+\$?(?:\(.*\))?)(\s*)(\+\+|\-\-)', line_alt, re.IGNORECASE)
    if arit_oper:
        for items in arit_oper:
            line_alt = line_alt.replace(items[0] + items[1] + items[2], items[0] + items[1] + '=' + items[1] + items[0] + items[1] + items[2][:1] + items[1] + '1')

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


show_log('', 'Restoring labels', 3)
arrayB = []
for line in array:
    line_num, line_alt, line_file = line

    labels = re.findall(r'{[^}]*}', line_alt)
    if labels:
        for item in labels:
            label = stored_labels[int(item[1:-1])]
            line_alt = line_alt.replace(item, label)
            show_log(line, ' '.join(['restored_label:', item[1:-1], label]), 4)

    arrayB.append((line_num, line_alt, line_file))
array = arrayB


show_log('', 'REMarking line labels, replacing branching labels and storing its REMs', 3)
arrayB = []
branching_labels = []
for line, number in zip(array, line_numbers):
    line_num, line_alt, line_file = line
    append_label = ''

    labels = re.findall(r'{[^}]*}', line_alt)
    if re.match(r'\s*{\w+?}', line_alt):
        line_alt = re.sub(r'(\s*)({\w+?})(.*$)', r'\1' + label_rem_format + general_spaces + r'\2\3', line_alt)

    elif labels:
        append_label = space_bef_colon + ':' + space_aft_colon + label_rem_format
        for item in labels:
            if item != '{@}':
                try:
                    line_alt = line_alt.replace(item, str(labels_store[item]))
                    append_label += general_spaces + item
                    show_log(line, ' '.join(['replaced_label:', item, str(labels_store[item])]), 4)
                except KeyError:
                    show_log(line, ' '.join(['label_not_found:', item]), 1)  # Exit
            elif item == '{@}':
                line_alt = line_alt.replace('{@}', str(number))
                append_label += general_spaces + '{SELF}'
                show_log(line, ' '.join(['replaced_label:', item, number]), 4)

        if not show_labels:
            append_label = ''

    branching_labels.append(append_label)

    arrayB.append((line_num, line_alt, line_file))
array = arrayB


show_log('', 'Restoring quotes, DATAs and REMs', 3)
arrayB = []
for line in array:
    line_num, line_alt, line_file = line

    remarks = re.findall(r'(?:\'|rem)\s*(\|\d*\|)', line_alt, re.IGNORECASE)
    if remarks:
        for item in remarks:
            remark = stored_comments[int(item[1:-1])]
            line_alt = line_alt.replace(item, remark)
            show_log(line, ' '.join(['restored_comments:', item[1:-1], remark]), 4)

    datas = re.findall(r'(@\d+@)', line_alt, re.IGNORECASE)
    if datas:
        for item in datas:
            data = stored_datas[int(item[1:-1])]
            line_alt = line_alt.replace(item, data)
            show_log(line, ' '.join(['restored_data:', item[1:-1], data]), 4)

    quotes = re.findall(r'``\d+``', line_alt)
    if quotes:
        for item in quotes:
            quote = stored_quotes[int(item[2:-2])]
            line_alt = line_alt.replace(item, quote)
            show_log(line, ' '.join(['restored_quote:', item[2:-2], quote]), 4)

    arrayB.append((line_num, line_alt, line_file))
array = arrayB


show_log('', 'Appending long variables summary', 3)
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


show_log('', 'Adding line numbers and indent, applying label REMs', 3)
show_log('', 'Converting CR and checking line size', 3, bullet=5)
arrayB = []
line_list = {}
for line, number, ident, blabel in zip(array, line_numbers, ident_sizes, branching_labels):
    line_num, line_alt, line_file = line

    line_alt = number + ' ' + ident + line_alt + blabel.rstrip() + '\r\n'

    line_lenght = len(line_alt) - 1
    if line_lenght > 256:
        show_log(line, ' '.join(['line_too_long:', str(line_lenght) + ' chars']), 1)  # Exit

    line_list[number] = [line_num, line_file]
    arrayB.append(line_alt)

array = arrayB
line_list[number] = [line_num, line_file]

if (monitor_exec or output_format == 'T' or output_format == 'B') and is_from_build:
    for line in line_list:
        print 'linelst-' + line + ',' + str(line_list[line][0]) + ',' + str(line_list[line][1])
    for line in included_dict:
        print 'includedict-' + str(line) + ',' + included_dict[line]


show_log('', 'Saving file', 3)
show_log('', ' '.join(['save_file:', file_save]), 4)
try:
    with open(file_save, 'w') as f:
        for c in range(len(array)):
            f.write(array[c])
except IOError:
    show_log('', ' '.join(['destination_folder_not_found:', file_save]), 1)  # Exit

show_log('', '', 3, bullet=0)

# Call MSX Basic Tokenizer
export_file = os.path.basename(file_save)
export_path = os.path.abspath(file_save)
if output_format == 'T' or output_format == 'B':
    name_prefix = '' if tokenize_tool == 'B' else 'open'
    show_log('', name_prefix + 'MSX Basic Tokenizer', 3, bullet=0)
    if is_from_build:
        show_log('', ''.join(['Converting ', file_save]), 3, bullet=0)
        show_log('', ''.join(['To ', export_path, '/', os.path.splitext(export_file)[0] + '.bas']), 3, bullet=0)
    if os.path.isfile(batoken_filepath):
        btline = ''
        btarg = ['-fb'] * 4
        btarg[2] = '-vb=' + str(verbose_level)
        if output_format == 'T':
            btarg[0] = '-do'
        if export_list > 0 and tokenize_tool == 'B':
            btarg[1] = '-el=' + str(export_list)
        if export_list > 0 and tokenize_tool == 'O':
            show_log('', 'openMSX Basic Tokenizer does not save lists', 2)
        if is_from_build:
            args_token = list(set(btarg))
            show_log('', ''.join(['With ', 'args ', ' '.join(args_token)]), 3, bullet=0)
        batoken = ['python', batoken_filepath, file_save, btarg[0], btarg[1], btarg[2], btarg[3]]
        btoutput = subprocess.check_output(batoken)
        for line in btoutput:
            btline += line
            if line == '\n':
                bterror = re.match(r'^\*\*\*\s(.*)\:\s\((\d+)\)\:(.*)', btline)
                btwarning = re.match(r'^\s\s\*\s(.*)\:\s\((\d+)\)\:(.*)', btline)
                if 'Tokenizing_aborted' in btline:
                    show_log('', btline.rstrip(), 1, bullet=0)
                elif btline == '\n':
                    show_log('', btline.rstrip(), 1, bullet=0)
                elif btwarning:
                    btwarning_line = line_list[btwarning.group(2)][0]
                    btwarning_file = included_dict[line_list[btwarning.group(2)][1]]
                    if is_from_build:
                        show_log('', ''.join(['  * ', btwarning_file, ': (', str(btwarning_line), '):', btwarning.group(3)]), 2, bullet=0)
                    else:
                        btwarning_file = (' on ' + btwarning_file + ':') if line_list[btwarning.group(2)][1] > 0 else ''
                        show_log('', ''.join(['  * (', str(btwarning_line), '):', btwarning_file, btwarning.group(3)]), 2, bullet=0)
                elif bterror:
                    bterror_line = line_list[bterror.group(2)][0]
                    bterror_file = included_dict[line_list[bterror.group(2)][1]]
                    if is_from_build:
                        show_log('', ''.join(['*** ', bterror_file, ': (', str(bterror_line), '):', bterror.group(3)]), 1, bullet=0)
                    else:
                        bterror_file = (' on ' + bterror_file + ':') if line_list[bterror.group(2)][1] > 0 else ''
                        show_log('', ''.join(['*** (', str(bterror_line), '):', bterror_file, bterror.group(3)]), 1, bullet=0)
                else:
                    show_log('', btline.rstrip(), verbose_level, bullet=0)
                btline = ''
        if 'Tokenizing_aborted' not in btoutput:
            export_file = os.path.splitext(export_file)[0] + '.bas'
    else:
        show_log('', '', 2, bullet=0)
        show_log('', ''.join([name_prefix + 'MSX_Basic_Tokenizer_not_found: ', batoken_filepath]), 2)

if is_from_build:
    print 'export_file-' + export_file

# end = time.time()
# print(end - start)
# raise SystemExit(0)
