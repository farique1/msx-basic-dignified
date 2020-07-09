#!/usr/bin/env python3
'''
MSX Basic DignifiER
v1.0
Convert traditional MSX Basic to modern MSX Basic Dignified format.

Copyright (C) 2020 - Fred Rique (farique)
https://github.com/farique1/msx-basic-dignified
'''

import re
import os.path
import argparse

instr = ['AND', 'AS', 'BASE', 'BEEP', 'BLOAD', 'BSAVE', 'CALL', 'CIRCLE',
         'CLEAR', 'CLOAD', 'CLOSE', 'CLS', 'CMD', 'COLOR', 'CONT', 'COPY',
         'CSAVE', 'CSRLIN', 'DATA', 'DEF', 'DEFDBL', 'DEFINT', 'DEFSNG',
         'DEFSTR', 'DIM', 'DRAW', 'DSKI', 'END', 'EQV', 'ERASE', 'ERR',
         'ERROR', 'FIELD', 'FILES', 'FN', 'FOR', 'GET', 'IF', 'IMP', 'IPL',
         'KILL', 'LET', 'LFILES', 'LINE', 'LOAD', 'LOCATE', 'LPRINT', 'LSET',
         'MAX', 'MERGE', 'MOD', 'MOTOR', 'NAME', 'NEW', 'NEXT', 'NOT', 'OFF',
         'ON', 'OPEN', 'OR', 'OUT', 'PAINT', 'POINT', 'POKE', 'PRESET', 'PRINT',
         'PSET', 'PUT', 'READ', 'REM', 'RSET', 'SAVE', 'SCREEN', 'SET', 'SOUND',
         'STEP', 'STOP', 'SWAP', 'TIME', 'TO', 'TROFF', 'TRON', 'USING',
         'VPOKE', 'WAIT', 'WIDTH', 'XOR', "'"]

funct = ['ABS', 'ASC', 'ATN', r'ATTR\$', r'BIN\$', 'CDBL', r'CHR\$', 'CINT',
         'COS', 'CSNG', 'CVD', 'CVI', 'CVS', 'DSKF', r'DSKO\$', 'EOF', 'EXP',
         'FIX', 'FPOS', 'FRE', r'HEX\$', r'INKEY\$', 'INP', r'INPUT\$', 'INSTR',
         'INT', 'KEY', r'LEFT\$', 'LEN', 'LOC', 'LOF', 'LOG', 'LPOS', r'MID\$',
         r'MKD\$', r'MKI\$', r'MKS\$', r'OCT\$', 'PAD', 'PDL', 'PEEK', 'PLAY',
         'POS', r'RIGHT\$', 'RND', 'SGN', 'SIN', r'SPACE\$', 'SPC', r'SPRITE\$',
         'SPRITE', 'SQR', 'STICK', r'STR\$', 'STRIG', r'STRING\$', 'TAB',
         'TAN', 'USR', 'VAL', 'VARPTR', 'VDP', 'VPEEK']

branc = ['AUTO', 'DELETE', 'ELSE', 'ERL', 'GOSUB', 'GOTO', 'LIST', 'LLIST',
         'RENUM', 'RESTORE', 'RESUME', 'RETURN', 'RUN', 'THEN']


def show_log(line_number, text, level, **kwargs):
    bullets = ['', '*** ', '  * ', '--- ', '  - ', '    ']

    try:
        bullet = kwargs['bullet']
    except KeyError:
        bullet = level

    display_file_name = ''
    line_number = '(' + str(line_number) + '): ' if line_number != '' else ''

    if verbose_level >= level:
        print(bullets[bullet] + display_file_name + line_number + text)

    if bullet == 1:
        print('    Execution_stoped')
        print()
        raise SystemExit(0)


def load_file(file_load):
    classic_code = []
    if file_load:
        try:
            with open(file_load, 'r', encoding='latin1') as f:
                for line in f:
                    classic_code.append(line.strip() + '\n')
            return classic_code
        except IOError:
            show_log('', ' '.join(['Source_not_found', file_load]), 1)  # Exit
    else:
        show_log('', 'Source_not_given', 1)  # Exit


def check_space(char, patt):
    esc_match = match.upper().replace('$', r'\$')
    if g.lastgroup == 'key' and esc_match in funct:
        patt = patt.replace('(', '')
    space = ''
    if re.match(patt, char):
        space = ' '
    return space


def force_space(match):
    if re.match(spacesbef, match.strip()):
        match = ' ' + match
    if re.match(spacesaft, match.strip()):
        match = match + ' '
    return match


file_load = 'BasicTests/testDFR.asc'    # Source file
file_save = ''      # Destination file
ident_tgl = True    # Add indent to non label lines
lline_tgl = True    # Add blank line before labels
print_tgl = True    # Convert locate:print to [?@]
verbose_level = 2   # Show processing status: 0-silent 1-+erros 2-+warnings 3-+steps 4-+details

# Set command line (if used overwrites previous settings)
parser = argparse.ArgumentParser(description='Convert traditional MSX Basic to '
                                             'modern MSX Basic Dignified format.')
parser.add_argument('input', nargs='?', default=file_load,
                    help='Source file (.asc)')
parser.add_argument('output', nargs='?', default=file_save,
                    help='Destination file ([source].bad) if missing')
parser.add_argument('-it', default=ident_tgl, action='store_false',
                    help='Add indent to non label lines')
parser.add_argument('-lt', default=lline_tgl, action='store_false',
                    help='Add blank line before labels')
parser.add_argument('-pt', default=print_tgl, action='store_true',
                    help='Convert locate:print to [?@]')
parser.add_argument('-vb', default=verbose_level, type=int,
                    help='Verbosity level: 0=silent, 1=errors,'
                    '2=1+warnings, 3=2+steps(def), 4=3+details')
args = parser.parse_args()

# Apply chosen settings
file_load = args.input
file_save = args.output
if args.output == '':
    save_path = os.path.dirname(file_load)
    save_path = '' if save_path == '' else save_path + '/'
    save_file = os.path.basename(file_load)
    save_file = os.path.splitext(save_file)[0] + '.bad'
    file_save = save_path + save_file
ident_tgl = args.it
lline_tgl = args.lt
print_tgl = args.pt
verbose_level = args.vb

keywords = instr + funct + branc
keywords.sort(key=len, reverse=True)

keyw_list = '|'.join(keywords)
elements = (r'(?:'
            r'%s'
            r'|(?P<flo>\d*\.(\d+[EDed][+-]\d+|\d*))'
            r'|(?P<int>\d+)'
            r'|(?P<key>' + keyw_list + r')'
            r'|(?P<cmp>(<=|>=|=<|=>))'
            r'|(?P<all>.)'
            r')'
            )

variables = r'[A-Za-z0-9$#!%]'

repelcbef = r'[A-Za-z0-9{}")]'
repelcaft = r'[A-Za-z0-9{}"(]'

spacesbef = r'^(:|\+|-|\*|/|\^|\\|and|or|not|xor|eqv|imp|mod)$'
spacesaft = r'^(\+|-|\*|/|\^|\\|and|or|not|xor|eqv|imp|mod)$'

getstrings = r'(?P<lit>"(?:[^"]*)(?:"|$))'
to_endline = r'(?P<lit>.*$)'
to_endsect = r'(?P<lit>.*?(?=\:|$))'

match_elements = re.compile(elements % getstrings, re.I)
match_tendline = re.compile(elements % to_endline, re.I)
match_tendsect = re.compile(elements % to_endsect, re.I)

show_log('', 'Loading file', 3)
classic_code = load_file(file_load)

show_log('', 'Converting lines', 3)
buff = ''
match = ' '
prev_line = 0
line_number = 0
keep_caps = False
dig_dict = {}
line_labels = {}
match_current = match_elements
for line in classic_code:
    line = line.strip()

    if line == '':
        continue

    if line == '':
        show_log(prev_line, f'Blank_line_(after)', 2)
        continue

    if line.isdigit():
        show_log(line, 'Line_number_alone', 2)
        continue

    if not line[0].isdigit():
        show_log(line_number, 'No_line_number_(after)', 1)  # Exit

    g = match_elements.match(line)
    p = g.end()

    line_number = int(g.group().strip())
    if line_number < prev_line:
        show_log(line_number, 'Line_number_out_of_order', 1)  # Exit

    prev_line = line_number

    dig_line = ''
    get_lnumber = False
    while p < len(line):

        prev_spc = check_space(match[-1].upper(), repelcbef)

        g = match_current.match(line, p)
        p = g.end()
        match = g.group()
        match_current = match_elements

        next_spc = check_space(line[p:p + 1].upper(), repelcaft)

        if get_lnumber and (g.lastgroup != 'int'
                            and match != ','
                            and match != ' '):
            get_lnumber = False

        if g.group('key'):
            match = match.upper()

            if p < len(line):
                if (match == 'REM' or match == "'"):
                    match_current = match_tendline

                if match == 'DATA':
                    match_current = match_tendsect

            if match in branc:
                get_lnumber = True

            match = prev_spc + match + next_spc

        elif g.group('int') and get_lnumber:
            if int(match) == line_number:
                match = '{@}'
            else:
                item = line_labels.get(int(match), [])
                item.append(line_number)
                line_labels[int(match)] = item

                match = f'{{l_{match.strip()}}}'

        elif g.group('lit'):
            keep_caps = True

        match = force_space(match)

        if not keep_caps:
            match = match.lower()

        if (p <= len(line)
                and not g.group('key')
                and re.match(variables, match)):
            buff += match
        else:

            # if buff != '' and buff != ' ':
            #     print(buff.strip())
            # if match != '' and match != ' ':
            #     print(match)

            dig_line += buff
            dig_line += match
            buff = ''

        keep_caps = False

    # if buff != '' and buff != ' ':
    #     print(buff.strip())
    dig_line += buff
    buff = ''
    dig_dict[line_number] = dig_line.lstrip()

show_log('', 'Checking for branching errors', 3)
for lines in line_labels:
    if lines not in dig_dict:
        for line in line_labels[lines]:
            show_log(line, f'Line_does_not_exist: {lines}', 2)

show_log('', 'Assembling final code', 3)
ident = ''
dignified_code = []
for line in sorted(dig_dict.keys()):
    if line in line_labels:
        if lline_tgl:
            dignified_code.append('\n')
        if ident_tgl:
            ident = '\t'
        dignified_code.append(f'{{l_{str(line)}}}\n')
    dignified_code.append(ident + dig_dict[line] + '\n')

show_log('', ' '.join(['File saving']), 3)
try:
    with open(file_save, 'w') as f:
        for line in dignified_code:
            f.write(line)
except IOError as e:
    show_log('', ' '.join([str(e)]), 1)  # Exit

# for line in dignified_code:
    # print(line.strip())


# numbers = (r'(?P<num>(?:'
#            r'(?:[0-9][0-9]*)?\.(?:[0-9]*[0-9])?'
#            r'|(?:[0-9](?:[0-9]*[0-9])?)'
#            r')'
#            r'(?:'
#            r'[%!\#]'
#            r'|[ED][-+]?(?:[0-9]*[0-9])?'
#            r')?)'
#            )

# print_at = r'(?P<lpa>^\b$)'  # Create a lpa key that matches nothing
# if print_tgl:
#     print_at = r'(?P<lpa>(?:LOCATE)(?P<cor>[^:]*?):\s*PRINT)'

# elif g.group('lpa'):
#     prev_grp = 'lpa'
#     item = g.group("cor").lower()
#     item = item.replace(' ', '')
#     show_log(line_number, f'Converted_to: [?@]{item}', 4)
#     space = '' if next_ch == ' ' else ' '
#     match = f'[?@]{item}{space}'
