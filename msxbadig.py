#!/usr/bin/env python3
"""
MSX Basic Dignified
v1.5
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

New: v1.5 13-02-2020
    Ported to Python 3.8!
    No more forcing an 8 character file name for output (we are all adults here and understand the limitations of the MSX disk system.)
    Added Loop Labels.
    Added Line Toggles.
    Added Rem Blocks with '' and ###.
    Added the possibility of DEFINEs as a variables to other DEFINEs.
        Re coded and streamlined the entire DEFINE replacement routine.
    Added -rh and rem_header= to remove the two info REM header lines on the converted code.
    Added -tr and translate= to translate unicode special characters to a MSX ASCII similar.
    Added linefeed to last line of code to force parsing it.
    Changed the standing characters for the DATA, REM, QUOTES and LABELS placeholders to way above the usual ASCII range of the old computers to prevent misinterpretation.
    Changed colon spaces to preserve spacing if keep spacing is used
    Changed defaults to provide a more compact code.
        General spacing default now is 0 spaces.
        Label line default is now 2 (no REM labels.).
        Strip the GOTOs after THEN/ELSE is now the default.
    Changed -fb to -frb to standardize the nomenclature (3 letters are for internal arguments).
    Integrated colon spacing arguments -bc, -ac, nnbr_spaces_bef_colon= and nnbr_spaces_aft_colon= into -cs and colon_spaces= that takes b, a and ba for before, after and before and after.
    Integrated label line spacing arguments -br, -ar, rem_bef_label and rem_aft_label into -lg and label_gap= that takes b, a, ba for before, after and before and after.
    Integrated spacing arguments -ks and keep_original_spaces= into -gs and general_spaces= that now takes 0, 1 and k for no space, one space and keep original spacing (there is no more option for more the 1 general space.)
    Integrated indent arguments -ci, -si, keep_indent_space_chars= and indent_tab_spaces= into -ki and keep_indent= and made it take the number of TAB spaces.
    Integrated REM format arguments -lr, -rr, label_rem_format= and regul_rem_format= into -nr and new_rem_format= (there is no more distinction between label and regular REMs.)
    Improved verbose output
        Optimised a little.
        Standardised the arguments help text.
        Added reporting of [?@] arguments on detailed verbose.
        Comments after a label without ' generates a warning.
        Undefined DEFINEs demoted to warning from error (while bug picking [...] constructs inside DATA, REM and QUOTES is not fixed.
        -vb 0 now quit silently on errors.
    Fixed a bug with parentheses on function call variables and improved the underlying code.
    Fixed a potential small bug with spaces before colon.
    Fixed small bug converting existing REMs.
    Fixed potential small bug removing line numbers.
    Removed Known Bugs section here, they were growing too fast.
"""

# Use on terminal for benchmarking
# for run in {1..100}; do  python msxbadig.py cgk-source.bas cgk-conv.bas -vb 0; done > test.txt

import re
import os.path
import argparse
import subprocess
import configparser
from itertools import zip_longest
# import time
# start = time.time()

# Config
file_load = ''              # Source file
file_save = ''              # Destination file
line_start = 10             # Start line number
line_step = 10              # Line step amount
leading_zero = False        # Add leading zeros
rem_header = True           # Add leading zeros
colon_spaces = ''           # Space before and after ':' : b-before a-after ba-before and after
general_spaces = '0'        # Strip all general spaces to this amount
unpack_operators = False    # keep spaces around +-=<>*/^\
keep_blank_lines = False    # Keep blank lines using REM
label_gap = ''              # Space before and after a label: b-before a-after ba-before and after
show_labels = False         # Show labels on lines with branching instructions
label_lines = 2             # Handle label lines: 0-label_name 1-REM_only 2-delete
new_rem_format = "s"        # Format of the automatically added REM: s-single_quote rem-rem
convert_rems = False        # Convert all REMs
keep_indent = 0             # Keep indentation
capitalise_all = True       # Capitalize
convert_print = False       # Convert ? to PRINT
strip_then_goto = 'g'       # Strip adjacent THEN/ELSE or GOTO: t-THEN/ELSE g-GOTO
translate = False           # Translate Unicode characters to native similar
long_var_summary = 0        # Show long variables summary on rems at the end of the program (0-none 1+-var per line)
verbose_level = 3           # Show processing status: 0-silent 1-+erros 2-+warnings 3-+steps 4-+details
output_format = 'b'         # Tokenized or ASCII output: t-tokenized a-ASCII b-both
tokenize_tool = 'b'         # Tool used to tokenize the ASCII code: b-MSX Basic Tokenizer(def) o-openMSX Basic Tokenizer
export_list = 0             # Save a .mlt list file detailing the tokenization: [#] number of bytes per line (def 16) (max 32) (0 no)
monitor_exec = False        # Monitor the execution on the emulator and catch errors (only works with From Build)
is_from_build = False       # Tell if it is being called from a build system (show file name on error messages and other stuff)
batoken_filepath = ''       # Path to MSX Basic Tokenizer ('' = local path)
openbatoken_filepath = ''   # Path to openMSX Basic Tokenizer ('' = local path)


def show_log(line, text, level, **kwargs):
    # Use bullet 0 with -vb 0 to debug.
    bullets = ['', '*** ', '  * ', '--- ', '  - ', '    ']
    try:
        bullet = kwargs['bullet']
    except KeyError:
        bullet = level

    if verbose_level >= level:

        if line != '':
            line_num, line_alt, line_file = line
        else:
            line_num, line_file = '', ''

        display_file_name = ''
        if is_from_build and line_file != '' and (bullet == 1 or bullet == 2):
            display_file_name = included_dict[line_file] + ': '

        line_num = '(' + str(line_num) + '): ' if line_num != '' else ''

        print(bullets[bullet] + display_file_name + line_num + text)

    if bullet == 1:
        if verbose_level > 0:
            print('    Execution_stoped')
        raise SystemExit(0)


local_path = os.path.split(os.path.abspath(__file__))[0] + '/'
if os.path.isfile(local_path + 'msxbadig.ini'):
    config = configparser.ConfigParser()
    config.sections()
    try:
        config.read(local_path + 'msxbadig.ini')
        use_ini_file = config.getboolean('DEFAULT', 'use_ini_file') if config.get('DEFAULT', 'use_ini_file') else False
        if use_ini_file:
            file_load = config.get('DEFAULT', 'source_file') if config.get('DEFAULT', 'source_file') else file_load
            file_save = config.get('DEFAULT', 'destin_file') if config.get('DEFAULT', 'destin_file') else file_save
            line_start = config.getint('DEFAULT', 'line_start') if config.get('DEFAULT', 'line_start') else line_start
            line_step = config.getint('DEFAULT', 'line_step') if config.get('DEFAULT', 'line_step') else line_step
            leading_zero = config.getboolean('DEFAULT', 'leading_zeros') if config.get('DEFAULT', 'leading_zeros') else leading_zero
            rem_header = config.getboolean('DEFAULT', 'rem_header') if config.get('DEFAULT', 'rem_header') else rem_header
            colon_spaces = config.getint('DEFAULT', 'colon_spaces') if config.get('DEFAULT', 'colon_spaces') else colon_spaces
            general_spaces = str(config.getint('DEFAULT', 'general_spaces')) if config.get('DEFAULT', 'general_spaces') else general_spaces
            unpack_operators = config.getboolean('DEFAULT', 'unpack_operators') if config.get('DEFAULT', 'unpack_operators') else unpack_operators
            keep_blank_lines = config.getboolean('DEFAULT', 'keep_blank_lines') if config.get('DEFAULT', 'keep_blank_lines') else keep_blank_lines
            label_gap = config.getboolean('DEFAULT', 'label_gap') if config.get('DEFAULT', 'label_gap') else label_gap
            show_labels = config.getboolean('DEFAULT', 'show_branches_labels') if config.get('DEFAULT', 'show_branches_labels') else show_labels
            label_lines = config.getint('DEFAULT', 'handle_label_lines') if config.get('DEFAULT', 'handle_label_lines') else label_lines
            new_rem_format = config.get('DEFAULT', 'new_rem_format') if config.get('DEFAULT', 'new_rem_format') else new_rem_format
            convert_rems = config.getboolean('DEFAULT', 'convert_rem_formats') if config.get('DEFAULT', 'convert_rem_formats') else convert_rems
            keep_indent = config.getboolean('DEFAULT', 'keep_indent') if config.get('DEFAULT', 'keep_indent') else keep_indent
            capitalise_all = config.getboolean('DEFAULT', 'capitalize_all') if config.get('DEFAULT', 'capitalize_all') else capitalise_all
            convert_print = config.getboolean('DEFAULT', 'convert_interr_to_print') if config.get('DEFAULT', 'convert_interr_to_print') else convert_print
            strip_then_goto = config.get('DEFAULT', 'strip_then_goto') if config.get('DEFAULT', 'strip_then_goto') else strip_then_goto
            translate = config.getboolean('DEFAULT', 'translate') if config.get('DEFAULT', 'translate') else translate
            long_var_summary = config.getint('DEFAULT', 'long_var_summary') if config.get('DEFAULT', 'long_var_summary') else long_var_summary
            verbose_level = config.getint('DEFAULT', 'verbose_level') if config.get('DEFAULT', 'verbose_level') else verbose_level
            output_format = config.get('DEFAULT', 'output_format') if config.get('DEFAULT', 'output_format') else output_format
            tokenize_tool = config.get('DEFAULT', 'tokenize_tool') if config.get('DEFAULT', 'tokenize_tool') else tokenize_tool
            export_list = config.getint('DEFAULT', 'export_list') if config.get('DEFAULT', 'export_list') else export_list
            batoken_filepath = config.get('DEFAULT', 'batoken_filepath') if config.get('DEFAULT', 'batoken_filepath') else batoken_filepath
            openbatoken_filepath = config.get('DEFAULT', 'openbatoken_filepath') if config.get('DEFAULT', 'openbatoken_filepath') else openbatoken_filepath
    except (ValueError, configparser.NoOptionError) as e:
        show_log('', 'msxbadig.ini: ' + str(e), 1)

# Set command line (if used overwrites previous settings)
parser = argparse.ArgumentParser(description='Convert modern styled MSX Basic to native format')
parser.add_argument("input", nargs='?', default=file_load, help='Source file (.bad)')
parser.add_argument("output", nargs='?', default=file_save, help='Destination file ([source].asc) if missing')
parser.add_argument("-ls", default=line_start, type=int, help='Starting line (def 10)')
parser.add_argument("-lp", default=line_step, type=int, help='Line steps (def 10)')
parser.add_argument("-lz", default=leading_zero, action='store_true', help='Leading zeros on line numbers')
parser.add_argument("-rh", default=rem_header, action='store_false', help='Show the info REM header')
parser.add_argument("-cs", default=colon_spaces, choices=['b', 'B', 'a', 'A', 'ba', 'BA'], help="Add spaces before and after ':': b=before, a=after, ba=before and after")
parser.add_argument("-gs", default=general_spaces, choices=['0', '1', 'k', 'K'], help='Control the general use of space: 0=no spaces(def), 1=one space, k=keep original spacing')
parser.add_argument("-uo", default=unpack_operators, action='store_true', help="Keep spaces around +-=<>*/^\\.,;")
parser.add_argument("-bl", default=keep_blank_lines, action='store_true', help='Keep blank lines as REM')
parser.add_argument("-lg", default=label_gap, choices=['b', 'B', 'a', 'A', 'ba', 'BA'], help="Add spaces before and after a label line: b=before, a=after, ba=before and after")
parser.add_argument("-sl", default=show_labels, action='store_true', help='Show labels on lines with branching commands')
parser.add_argument("-ll", default=label_lines, type=int, choices=[0, 1, 2], help="Handle label lines: 0=label name, 1=REM only, 2=no labels(def)")
parser.add_argument("-nr", default=new_rem_format, choices=["s", 'S', 'rem', 'REM', 'Rem'], help="Format of the automatically added REMs: s=single quote(def), rem=rem")
parser.add_argument("-cr", default=convert_rems, action='store_true', help='Convert existing REMs to the new REM format')
parser.add_argument("-ki", default=keep_indent, const=2, type=int, nargs='?', help='Keep indents: [#]=space characters per TAB (def 2) (0 off)')
parser.add_argument("-nc", default=capitalise_all, action='store_false', help='Do not capitalize')
parser.add_argument("-cp", default=convert_print, action='store_true', help='Convert ? to PRINT')
parser.add_argument("-tg", default=strip_then_goto, choices=['t', 'T', 'g', 'G', 'k', 'K'], help="Remove adjacent THEN/ELSE or GOTO: t=THEN/ELSE, g=GOTO(def), k=keep_all")
parser.add_argument("-tr", default=translate, action='store_true', help='Translate Unicode characters to native similar')
parser.add_argument("-vs", default=long_var_summary, const=5, type=int, nargs='?', help="Show long variables summary on REMs at the end of the program: [#]=variables per line, (def 5) (0 off)")
parser.add_argument("-vb", default=verbose_level, type=int, help="Verbosity level: 0=silent, 1=errors, 2=1+warnings, 3=2+steps(def), 4=3+details")
parser.add_argument("-of", default=output_format, choices=['t', 'T', 'a', 'A', 'b', 'B'], help="Tokenized or ASCII output: t=tokenized, a=ASCII, b=both(def)")
parser.add_argument("-tt", default=tokenize_tool, choices=['b', 'B', 'o', 'O'], help="Tool used to tokenize the ASCII code: b=MSX Basic Tokenizer(def), o=openMSX Basic Tokenizer")
parser.add_argument("-el", default=export_list, const=16, type=int, nargs='?', help="Save a .mlt list file detailing the tokenization: [#]=number of bytes per line (def 16) (max 32) (0 off)")
parser.add_argument("-exe", default=monitor_exec, action='store_true', help="Send line numbers to build system to catch errors during execution (only works with From Build)")
parser.add_argument("-frb", default=is_from_build, action='store_true', help="Tell Badig it is running from a build system or an external application")
parser.add_argument("-ini", action='store_true', help="Create msxbadig.ini")
args = parser.parse_args()

# Write .ini file if told to
if args.ini:
    config.set('DEFAULT', 'use_ini_file', 'True')
    config.set('DEFAULT', 'source_file', file_load)
    config.set('DEFAULT', 'destin_file', file_save)
    config.set('DEFAULT', 'line_start', line_start)
    config.set('DEFAULT', 'line_step', line_step)
    config.set('DEFAULT', 'leading_zeros', leading_zero)
    config.set('DEFAULT', 'rem_header', rem_header)
    config.set('DEFAULT', 'colon_spaces', colon_spaces)
    config.set('DEFAULT', 'general_spaces', general_spaces)
    config.set('DEFAULT', 'unpack_operators', unpack_operators)
    config.set('DEFAULT', 'keep_blank_lines', keep_blank_lines)
    config.set('DEFAULT', 'label_gap', label_gap)
    config.set('DEFAULT', 'show_branches_labels', show_labels)
    config.set('DEFAULT', 'handle_label_lines', label_lines)
    config.set('DEFAULT', 'new_rem_format', new_rem_format)
    config.set('DEFAULT', 'convert_rem_formats', convert_rems)
    config.set('DEFAULT', 'keep_indent', keep_indent)
    config.set('DEFAULT', 'capitalize_all', capitalise_all)
    config.set('DEFAULT', 'convert_interr_to_print', convert_print)
    config.set('DEFAULT', 'strip_then_goto', strip_then_goto)
    config.set('DEFAULT', 'translate', translate)
    config.set('DEFAULT', 'long_var_summary', long_var_summary)
    config.set('DEFAULT', 'verbose_level', verbose_level)
    config.set('DEFAULT', 'output_format', output_format)
    config.set('DEFAULT', 'tokenize_tool', tokenize_tool)
    config.set('DEFAULT', 'export_list', export_list)
    config.set('DEFAULT', 'batoken_filepath', batoken_filepath)
    config.set('DEFAULT', 'openbatoken_filepath', openbatoken_filepath)
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
    save_file = os.path.splitext(save_file)[0] + '.asc'
    file_save = save_path + save_file
line_start = abs(args.ls)
line_step = abs(args.lp)
leading_zero = args.lz
rem_header = args.rh
space_bef_colon = ' ' if 'B' in args.cs.upper() else ''
space_aft_colon = ' ' if 'A' in args.cs.upper() else ''
general_spaces = ' ' if args.gs == '1' else ''
keep_spaces = True if args.gs.upper() == 'K' else False
unpack_operators = args.uo
keep_blank_lines = args.bl
blank_bef_rem = True if 'B' in args.lg.upper() else False
blank_aft_rem = True if 'A' in args.lg.upper() else False
show_labels = args.sl
label_lines = args.ll
general_rem_format = "'" if args.nr.upper() == 'S' else args.nr + ' '
label_rem_format = general_rem_format
convert_rems = args.cr
keep_indent = args.ki
capitalise_all = args.nc
convert_print = args.cp
strip_then_goto = args.tg.upper()
translate = args.tr
verbose_level = args.vb
output_format = args.of.upper()
tokenize_tool = 'O' if args.tt.upper() == 'O' else 'B'
long_var_summary = args.vs
export_list = min(abs(args.el), 32)
monitor_exec = args.exe
is_from_build = args.frb
if batoken_filepath == '':
    batoken_filepath = local_path + 'MSXBatoken.py'
if openbatoken_filepath == '':
    openbatoken_filepath = local_path + 'openMSXBatoken.py'
if tokenize_tool == 'O':
    batoken_filepath = openbatoken_filepath

load_format = 'utf-8' if translate else 'latin1'
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
        for long_V, short_V in var_dict.items():
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
        for long_V, short_V in var_dict.items():
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


def trans_char(text):
    if not translate:
        return text

    # ☺☻♥♦♣♠·◘○◙♂♀♪♬☼┿┴┬┤├┼│─┌┐└┘╳╱╲╂
    replacements = {'☺': 'A', '☻': 'B', '♥': 'C', '♦': 'D', '♣': 'E', '♠': 'F',
                    '·': 'G', '◘': 'H', '○': 'I', '◙': 'J', '♂': 'K', '♀': 'L',
                    '♪': 'M', '♬': 'N', '☼': 'O', '┿': 'P', '┴': 'Q', '┬': 'R',
                    '┤': 'S', '├': 'T', '┼': 'U', '│': 'V', '─': 'W', '┌': 'X',
                    '┐': 'Y', '└': 'Z', '┘': '[', '╳': ']', '╱': '\\', '╲': '^',
                    '╂': '_'}

    text = ''.join([replacements.get(c, c) for c in text])

    original = 'ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜ¢£¥₧ƒáíóúñÑªº¿⌐¬½¼¡«»ÃãĨĩÕõŨũĲĳ¾∽◇‰¶§▂▚▆▔◾▇▎▞▊▕▉▨▧▼▲▶◀⧗⧓▘▗▝▖▒Δǂω█▄▌▐▀αβΓπΣσμτΦθΩδ∞φ∈∩≡±≥≤⌠⌡÷≈°∙‐√ⁿ²❚■'
    translat = ('\u0080\u0081\u0082\u0083\u0084\u0085\u0086\u0087\u0088\u0089\u008A\u008B\u008C\u008D\u008E\u008F'
                '\u0090\u0091\u0092\u0093\u0094\u0095\u0096\u0097\u0098\u0099\u009A\u009B\u009C\u009D\u009E\u009F'
                '\u00A0\u00A1\u00A2\u00A3\u00A4\u00A5\u00A6\u00A7\u00A8\u00A9\u00AA\u00AB\u00AC\u00AD\u00AE\u00AF'
                '\u00B0\u00B1\u00B2\u00B3\u00B4\u00B5\u00B6\u00B7\u00B8\u00B9\u00BA\u00BB\u00BC\u00BD\u00BE\u00BF'
                '\u00C0\u00C1\u00C2\u00C3\u00C4\u00C5\u00C6\u00C7\u00C8\u00C9\u00CA\u00CB\u00CC\u00CD\u00CE\u00CF'
                '\u00D0\u00D1\u00D2\u00D3\u00D4\u00D5\u00D6\u00D7\u00D8\u00D9\u00DA\u00DB\u00DC\u00DD\u00DE\u00DF'
                '\u00E0\u00E1\u00E2\u00E3\u00E4\u00E5\u00E6\u00E7\u00E8\u00E9\u00EA\u00EB\u00EC\u00ED\u00EE\u00EF'
                '\u00F0\u00F1\u00F2\u00F3\u00F4\u00F5\u00F6\u00F7\u00F8\u00F9\u00FA\u00FB\u00FC\u00FD\u00FE\u00FF')

    translation = text.maketrans(original, translat)
    text = text.translate(translation)

    return text


def load_file(file_load, line_file, line, file_type):
    array = []
    if file_load:
        show_log('', ' '.join(['load_file:', file_load]), 4)
        try:
            with open(file_load, 'r', encoding=load_format) as f:
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

if array[-1:][0][1][-1] != '\n':
    last_line = array.pop()
    array.append((last_line[0], str(last_line[1]) + '\n', last_line[2]))

show_log('', 'Processing REM blocks', 3)
arrayB = []
inside_rem = False
inside_ex_rem = False
inside_rem_prev = False
inside_ex_rem_prev = False
for line in array:
    line_num, line_alt, line_file = line

    if inside_rem != inside_rem_prev:
        brem_status = 'entering' if inside_rem else 'exiting'
        inside_rem_prev = inside_rem
        line = line_num - 1, line_alt, line_file
        show_log(line, ' '.join([brem_status + '_rem_block:']), 4)

    if inside_ex_rem != inside_ex_rem_prev:
        brem_status = 'entering' if inside_ex_rem else 'exiting'
        inside_ex_rem_prev = inside_ex_rem
        line = line_num - 1, line_alt, line_file
        show_log(line, ' '.join([brem_status + '_exclude_rem_block:']), 4)

    brem_line = re.findall(r"^('')?(.*?)('')?$", line_alt.strip())
    if brem_line and not inside_ex_rem:
        brem_line = brem_line[0]
        if brem_line[0] == "''" or brem_line[2] == "''":
            brem_indent = re.match(r'^(\s*)', line_alt)[0] if keep_indent else ''
            brem_char = ''.join(list(set(brem_line[0] + brem_line[1] + brem_line[2])))
            if brem_char == "'":
                brem_size = len(brem_line[0] + brem_line[1] + brem_line[2])
                if brem_size == 2:
                    inside_rem = not inside_rem
                    continue
                elif not inside_rem:
                    if brem_size == 3:
                        inside_rem = True
                        line_alt = "'"
                    elif brem_size == 4:
                        continue
                    elif brem_size > 4:
                        line_alt = "'" * (brem_size - 4)
                elif inside_rem:
                    if brem_size > 2:
                        inside_rem = False
                        line_alt = "'" * (brem_size - 1)
            elif inside_rem and brem_line[2] == "''":
                inside_rem = False
                brem_indent = re.match(r'^(\s*)', line_alt)[0]
                line_alt = general_rem_format + brem_indent + general_spaces + brem_line[0] + brem_line[1]
            elif brem_line[0] == "''" and brem_line[2] == "''":
                line_alt = general_rem_format + brem_indent + general_spaces + brem_line[1]
            elif not inside_rem and brem_line[0] == "''":
                inside_rem = True
                line_alt = brem_indent + brem_line[1]

    brem_line = re.findall(r"^(###)?(.*?)(###)?$", line_alt.strip())
    if brem_line and not inside_rem:
        brem_line = brem_line[0]
        if brem_line[0] == "###" or brem_line[2] == "###":
            brem_char = ''.join(list(set(brem_line[0] + brem_line[1] + brem_line[2])))
            if brem_char == "#":
                brem_size = len(brem_line[0] + brem_line[1] + brem_line[2])
                if 3 <= brem_size <= 5:
                    inside_ex_rem = not inside_ex_rem
                    continue
                elif not inside_ex_rem:
                    if brem_size > 5:
                        continue
                elif inside_ex_rem:
                    if brem_size > 3:
                        inside_ex_rem = False
                        continue
            elif inside_ex_rem and brem_line[2] == "###":
                inside_ex_rem = False
                continue
            elif brem_line[0] == "###" and brem_line[2] == "###":
                continue
            elif not inside_ex_rem and brem_line[0] == "###":
                inside_ex_rem = True
                continue

    if inside_rem:
        line_alt = general_rem_format + general_spaces + line_alt
    elif inside_ex_rem:
        continue

    arrayB.append((line_num, line_alt, line_file))

array = arrayB


show_log('', 'Getting and processing line toggles', 3)
arrayB = []
line_toggle = []
saved_lone_tags = [('', False)]
inside_toggle = False
current_inside_toggle = False
current_toggle_tag = ''
for line in array:
    line_num, line_alt, line_file = line

    if re.match(r'^\s*(#\w+)\s+$', line_alt):
        current_toggle_tag = re.match(r'^\s*(#\w+)', line_alt)[1].strip()
        if current_toggle_tag in (item[0] for item in saved_lone_tags[:-1]):
            show_log(line, ' '.join(['line_toggle_interleaved:', saved_lone_tags.pop()[0]]), 1)  # Exit
        if current_toggle_tag != saved_lone_tags[-1:][0][0]:
            current_inside_toggle = False if current_toggle_tag in line_toggle else True
            saved_lone_tags.append((current_toggle_tag, current_inside_toggle))
            inside_toggle = current_inside_toggle
            show_log(line, ' '.join(['line_toggle_block_opened:', current_toggle_tag]), 4)
        else:
            saved_lone_tags.pop()
            inside_toggle = saved_lone_tags[-1:][0][1]
            show_log(line, ' '.join(['line_toggle_block_closed:', current_toggle_tag]), 4)
        continue

    if not inside_toggle:
        if re.match(r'^\s*keep\s*', line_alt, re.IGNORECASE):
            local_toggles = re.findall(r'\s+(#\w+)(?=\s+)', line_alt)
            line_toggle.extend(local_toggles)
            line_alt = line_alt.replace('keep', '')
            for x in line_toggle:
                line_alt = line_alt.replace(x, '')
            if line_alt.strip() != '':
                show_log(line, ' '.join(['invalid_line_toggle:', line_alt]), 1)  # Exit
            else:
                for local_toggle in local_toggles:
                    show_log(line, ' '.join(['line_toggle_found:', local_toggle]), 4)

        elif re.match(r'^\s*(#\w+)\s+\S', line_alt):
            toggle_tag = re.match(r'^\s*(#\w+)(\s+)', line_alt)
            if toggle_tag[1] in line_toggle:
                line_alt = line_alt.replace(toggle_tag[1] + toggle_tag[2], '')
                arrayB.append((line_num, line_alt, line_file))
                show_log(line, ' '.join(['line_toggle_kept:', toggle_tag[1]]), 4)
            else:
                show_log(line, ' '.join(['line_toggle_discarded:', toggle_tag[1]]), 4)

        else:
            arrayB.append((line_num, line_alt, line_file))

if len(saved_lone_tags) > 1:
    show_log(line, ' '.join(['line_toggle_not_closed:', ', '.join(item[0] for item in saved_lone_tags[1:])]), 2)  # Exit
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
                show_log(line, ' '.join(['define_found:', found_def[0], found_def[1]]), 4)
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
    proto_func_call = re.search(r'(\.\w+)\(', line_alt)

    while proto_func_call:
        if proto_func_call.group()[:-1] in list(proto_functions.keys()):

            count = 1
            temp_arg = ''
            line_end = ''
            line_temp = line_alt + '\n'
            for char in line_temp[proto_func_call.start() + len(proto_func_call.group()):]:
                if count > 0:
                    count = count + 1 if char == '(' else count if char != ')' else count - 1
                    if char == ':' or char == '\n':
                        show_log(line, ' '.join(['func_call_error:', proto_func_call.group()[:-1]]), 1)  # Exit
                    temp_arg = temp_arg + char if char != ' ' else temp_arg + ''
                else:
                    line_end = line_end + char

            curr_func = proto_func_call.group()[:-1]
            proto_func_call_variables = temp_arg[:-1].split(',')
            func_call_line_end = line_end[:-1]

            proto_func_find_elements = re.search(r'^(.*?\s*)(\=)?\s*\.' + curr_func[1:], line_alt)
            if proto_func_find_elements.group(2) == '=':
                func_line_start = re.match(r'(.*(?:^|then|else|:)\s*)(.*?)=', proto_func_find_elements.group(0), re.IGNORECASE)
                proto_func_call_return = func_line_start.group(2).replace(' ', '').split(',')
                func_call_line_str = func_line_start.group(1)
            else:
                proto_func_call_return = ''.replace(' ', '').split(',')
                func_call_line_str = proto_func_find_elements.group(1)

            proto_functions[curr_func] = (proto_functions[curr_func][0], proto_functions[curr_func][1], proto_func_call_variables, proto_func_call_return)

            func_line = ''
            func_colon = space_bef_colon + ':' + space_aft_colon
            func_oper = ' ' if unpack_operators else ''
            for i in range(0, 2):  # do the function calling vars and return vars
                for fdef_var, fcal_var in zip_longest(proto_functions[curr_func][i], proto_functions[curr_func][i + 2]):

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

            line_alt = func_call_line_str + func_line[:-len(func_colon)] + func_call_line_end
            show_log(line, ' '.join(['func_call_found:', ','.join(proto_func_call_return), curr_func, ','.join(proto_func_call_variables)]), 4)
            proto_func_call = re.search(r'(\.\w+)\(', line_alt)
        else:
            show_log(line, ' '.join(['func_not_defined:', proto_func_call.group()[:-1]]), 1)  # Exit

    arrayB.append((line_num, line_alt, line_file))

array = arrayB


show_log('', 'Replacing DEFINES and [?@]', 3)
arrayB = []
def_var = []
for line in array:
    line_num, line_alt, line_file = line

    def_with_vars = []
    def_without_args = []
    if define_reg_line.findall(line_alt):
        if '[?@]' in line_alt:
            print_ats = re.findall(r'(\[\?\@\])(\S+,\S+|\S+)', line_alt)
            line_alt = re.sub(r'(\[\?@\])(\S+,\S+|\S+)', r'locate' + ' ' + r'\2:print', line_alt)
            for print_at in print_ats:
                show_log(line, ' '.join(['replaced_[?@]', print_at[1]]), 4)

        line_defs = re.findall(r'(\[[^\]]+\])', line_alt, re.IGNORECASE)
        line_defs = list(set(line_defs))
        if line_defs:
            for defs in line_defs:
                try:
                    def_var = define_reg_local.findall(defines[defs])
                except KeyError as e:
                    show_log(line, ' '.join(['define_not_found:', str(e)]), 2)
                    continue
                if not def_var:
                    line_alt = line_alt.replace(defs, defines[defs])
                    show_log(line, ' '.join(['define_replaced(no var):', defs, '->', defines[defs]]), 4)
                else:
                    def_with_vars.append((defs, def_var[0]))
            if def_with_vars:
                for defs in def_with_vars:
                    def_args = re.findall(r'(?<=\[' + defs[0][1:-1] + r'\])(\S*?)(?:\s|:|$)', line_alt, re.IGNORECASE)
                    for have_args in def_args:
                        if have_args.strip() != '':
                            with_arg = defines[defs[0]].replace(defs[1], have_args)
                            line_alt = line_alt.replace(defs[0] + have_args, with_arg)
                            show_log(line, ' '.join(['define_replaced(wt arg):', defs[0] + have_args, '->', with_arg]), 4)
                        else:
                            def_without_args.append((defs[0], defs[1]))
                if def_without_args:
                    for defs in def_without_args:
                        without_arg = defines[defs[0]].replace(defs[1], defs[1][1:-1])
                        line_alt = line_alt.replace(defs[0], without_arg)
                        show_log(line, ' '.join(['define_replaced(no arg):', defs[0], '->', without_arg]), 4)

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
        line_alt = re.sub(r'(?!^\s*)\d+\s*', '', line_alt)
        if line_alt.strip() == '':
            continue
        show_log(line, ' '.join(['removed_line_number']), 2)

    if re.match(r'(^\s*endif\s*$)', line_alt, re.IGNORECASE):
        show_log(line, ' '.join(['removed_endif']), 4)
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
            show_log((join_line_num - 1, line_alt, prev_line_file), ' '.join(['joined_line']), 4)
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
if rem_header:
    arrayB[1] = (0, general_rem_format + general_spaces + second_line, 0)
else:
    arrayB.pop(0)
    arrayB.pop(0)
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

        loop_label = re.match(r'(^\s*)(\w+?{)\s*$', line_alt)
        if loop_label and blank_bef_rem:
            arrayB.append(('0', label_rem_format, line_file))
            show_log(line, ' '.join(['space_before_loop_label:', str(loop_label.group(2)).strip()]), 4)

        arrayB.append(line)

        if label and blank_aft_rem:
            arrayB.append(('0', label_rem_format, line_file))
            show_log(line, ' '.join(['space_after_label:', str(label.group(1)).strip()]), 4)

        if loop_label and blank_aft_rem:
            arrayB.append(('0', label_rem_format, line_file))
            show_log(line, ' '.join(['space_after_loop_label:', str(loop_label.group(1)).strip()]), 4)

    array = arrayB


show_log('', 'Getting line numbers, indent sizes and label positions', 3)
show_log('', 'Removing leading spaces', 3, bullet=5)
arrayB = []
line_digits = 0
line_numbers = []
ident_sizes = []
label_loop = []
labels_store = {}
if leading_zero:
    line_digits = line_start + ((len(array) - 1) * line_step)
    line_digits = len(str(line_digits))
line_current = line_start
for line in array:
    line_num, line_alt, line_file = line

    label = re.match(r'(^\s*)(\w+?){\s*$', line_alt)
    if label:
        line_alt = label.group(1) + '{' + label.group(2) + '}'
        label_loop.append((label.group(2), line))

    label = re.match(r'(^\s*)}\s*$', line_alt)
    if label:
        if len(label_loop) > 0:
            loop_name = label_loop.pop()[0]
        else:
            show_log(line, ' '.join(['loop_label_open_missing']), 1)  # Exit
        line_alt = label.group(1) + 'goto' + general_spaces + '{' + loop_name + '}'
        show_log(line, ' '.join(['closed_loop_label:', '{' + loop_name + '}']), 4)

    label = re.match(r'(^\s*{.+?})(.*$)', line_alt)
    if label:
        label_content = label.group(1).lstrip()[1:-1]
        if re.search(r'\W', label_content) or label_content.isdigit():
            show_log(line, ' '.join(['invalid_label_name:', label.group(1).lstrip()]), 1)  # Exit
        if label.group(1).lstrip() in labels_store:
            show_log(line, ' '.join(['duplicated_label:', label.group(1).lstrip()]), 1)  # Exit
        if label.group(2).lstrip()[:1] != "'" and label.group(2).strip()[:1] != '':
            show_log(line, ' '.join(["label_comment_without_('):", label.group(2)]), 2)
        labels_store[label.group(1).lstrip()] = line_current
        show_log(line, ' '.join(['got_label_line:', label.group(1).lstrip(), '->', str(line_current)]), 4)
        if label_lines == 1:
            label_line_end = label.group(2).lstrip()[1:] if label.group(2).lstrip()[:1] == "'" else label.group(2)
            line_alt = label_rem_format + label_line_end
        elif label_lines == 2:
            continue

    new_indent = ''
    if keep_indent > 0:
        ident = re.match(r'(^\s*)\S', line_alt)
        new_indent = ident.group(1)
        new_indent = new_indent.replace('\t', ' ' * keep_indent)

    line_alt = line_alt.lstrip()
    ident_sizes.append(new_indent)
    line_padded = str(line_current).zfill(line_digits)
    line_numbers.append(line_padded)
    line_current += line_step

    arrayB.append((line_num, line_alt, line_file))

if len(label_loop) > 0:
    loop_err_line = label_loop[-1:][0][1]
    loop_err_label = label_loop[-1:][0][0]
    show_log(loop_err_line, ' '.join(['loop_label_close_missing:', loop_err_label + '{']), 1)  # Exit

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
            # print ("--- quote item --->>", item)
            stored_quotes.append(item)
            line_alt = line_alt.replace(item, chr(742) + str(quote_number) + chr(742))
            show_log(line, ' '.join(['stored_quote:', str(quote_number), '<-', str(item)]), 4)
            quote_number += 1

    data = re.findall(r'(?:^|:)\s*(data\s*)(.+?)(?=:|$)', line_alt, re.IGNORECASE)
    if data:
        for item in data:
            # print ("--- data item --->", item)
            stored_datas.append(item[1])
            line_alt = line_alt.replace(item[0] + item[1], item[0] + chr(743) + str(data_number) + chr(743))
            show_log(line, ' '.join(['stored_data:', str(data_number), '<-', str(item)]), 4)
            data_number += 1

    remark = re.findall(r'((?:^|:)\s*rem|(?:^|:|)\s*\')(.+)', line_alt, re.IGNORECASE)
    if remark:
        for item in remark:
            # print ("  - rem item --->>", item)
            stored_comments.append(item[1])
            line_alt = line_alt.replace(item[0] + item[1], item[0] + chr(744) + str(comment_number) + chr(744))
            show_log(line, ' '.join(['stored_rem:', str(comment_number), '<-', str(item)]), 4)
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
            line_alt = line_alt.replace(item, chr(741) + str(label_number) + chr(741))
            show_log(line, ' '.join(['stored_label:', str(label_number), '<-', str(item)]), 4)
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
            line_alt = re.sub(r'(rem|\')', general_rem_format, line_alt, flags=re.IGNORECASE)

    if not keep_spaces:
        line_alt = re.sub(r'(?:\s*\:)', space_bef_colon + ':', line_alt)
        line_alt = re.sub(r'(?:(?<=:)\s*)', space_aft_colon, line_alt)

    arrayB.append((line_num, line_alt, line_file))
array = arrayB


show_log('', 'Restoring labels', 3)
arrayB = []
for line in array:
    line_num, line_alt, line_file = line

    labels = re.findall(chr(741) + r'\d+' + chr(741), line_alt)
    if labels:
        for item in labels:
            label = stored_labels[int(item[1:-1])]
            line_alt = line_alt.replace(item, label)
            show_log(line, ' '.join(['restored_label:', item[1:-1], '->', label]), 4)

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
                    show_log(line, ' '.join(['replaced_label:', item, '->', str(labels_store[item])]), 4)
                except KeyError:
                    show_log(line, ' '.join(['label_not_found:', item]), 1)  # Exit
            elif item == '{@}':
                line_alt = line_alt.replace('{@}', str(number))
                append_label += general_spaces + '{SELF}'
                show_log(line, ' '.join(['replaced_label:', item, '->', number]), 4)

        if not show_labels:
            append_label = ''

    branching_labels.append(append_label)

    arrayB.append((line_num, line_alt, line_file))
array = arrayB


show_log('', 'Restoring quotes, DATAs and REMs', 3)
arrayB = []
for line in array:
    line_num, line_alt, line_file = line

    remarks = re.findall(r'(?:\'|rem)\s*(' + chr(744) + r'\d+' + chr(744) + ')', line_alt, re.IGNORECASE)
    if remarks:
        for item in remarks:
            remark = stored_comments[int(item[1:-1])]
            remark = trans_char(remark)
            line_alt = line_alt.replace(item, remark)
            show_log(line, ' '.join(['restored_comments:', item[1:-1], '->', remark]), 4)

    datas = re.findall(chr(743) + r'\d+' + chr(743), line_alt, re.IGNORECASE)
    if datas:
        for item in datas:
            data = stored_datas[int(item[1:-1])]
            data = trans_char(data)
            line_alt = line_alt.replace(item, data)
            show_log(line, ' '.join(['restored_data:', item[1:-1], '->', data]), 4)

    quotes = re.findall(chr(742) + r'\d+' + chr(742), line_alt)
    if quotes:
        for item in quotes:
            quote = stored_quotes[int(item[1:-1])]
            quote = trans_char(quote)
            line_alt = line_alt.replace(item, quote)
            show_log(line, ' '.join(['restored_quote:', item[2:-2], '->', quote]), 4)

    arrayB.append((line_num, line_alt, line_file))
array = arrayB


show_log('', 'Appending long variables summary', 3)
if var_dict and long_var_summary > 0:
    report_line = general_rem_format + general_spaces
    last_line = int(line_numbers[len(line_numbers) - 1])
    extra_lines = array[len(array) - 1][0]
    n = 1
    for long_var, short_var in sorted(list(var_dict.items()), key=lambda item: item[1], reverse=True):
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
        print('linelst-' + line + ',' + str(line_list[line][0]) + ',' + str(line_list[line][1]))
    for line in included_dict:
        print('includedict-' + str(line) + ',' + included_dict[line])


show_log('', 'Saving file', 3)
show_log('', ' '.join(['save_file:', file_save]), 4)
try:
    with open(file_save, 'w', encoding='latin1') as f:
        for c in range(len(array)):
            try:
                f.write(array[c])
            except UnicodeEncodeError as e:
                show_log('', ' '.join(['saving_encode_error:', str(e)]), 1)  # Exit
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
        btarg = ['-frb'] * 4
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
        batoken = ['python3', '-u', batoken_filepath, file_save, btarg[0], btarg[1], btarg[2], btarg[3]]
        btoutput = subprocess.check_output(batoken)
        for line in btoutput:
            btline += chr(line)
            if line == 10:
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
        if b'Tokenizing_aborted' not in btoutput:
            export_file = os.path.splitext(export_file)[0] + '.bas'
    else:
        show_log('', '', 2, bullet=0)
        show_log('', ''.join([name_prefix + 'MSX_Basic_Tokenizer_not_found: ', batoken_filepath]), 2)

if is_from_build:
    print('export_file-' + export_file)

# end = time.time()
# print(end - start)
# raise SystemExit(0)
