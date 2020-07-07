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

file_load = ''      # Source file
file_save = ''      # Destination file
ident_tgl = True    # Add indent to non label lines
lline_tgl = True    # Add blank line before labels
print_tgl = False    # Convert locate:print to [?@]
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

keywords = ['STRING', 'RESTORE', 'SPACE', 'RIGHT', 'VARPTR', 'DELETE', 'DEFSNG',
            'DEFSTR', 'DEFINT', 'DEFDBL', 'LPRINT', 'CSRLIN', 'LOCATE', 'SPRITE',
            'LFILES', 'CIRCLE', 'SCREEN', 'RETURN', 'INKEY', 'RESUME', 'PRESET',
            'VPEEK', 'STRIG', 'STICK', 'LEFT', 'ERASE', 'WIDTH', 'VPOKE', 'DSKO',
            'DSKI', 'MOTOR', 'USING', 'TROFF', 'MERGE', 'CSAVE', 'LLIST', 'COLOR',
            'CLOSE', 'SOUND', 'CLOAD', 'CLEAR', 'INSTR', 'BSAVE', 'INPUT', 'BLOAD',
            'RENUM', 'ATTR', 'GOSUB', 'PRINT', 'POINT', 'FILES', 'FIELD', 'ERROR',
            'PAINT', 'ELSE', 'OCT', 'DSKF', 'MKS', 'MKI', 'MKD', 'MID', 'LPOS',
            'CSNG', 'STR', 'CINT', 'CHR', 'CDBL', 'BIN', 'HEX', 'FPOS', 'PEEK',
            'OPEN', 'WAIT', 'NEXT', 'DRAW', 'NAME', 'TRON', 'TIME', 'THEN', 'DATA',
            'LSET', 'SWAP', 'STOP', 'COPY', 'STEP', 'LOAD', 'CONT', 'LIST', 'LINE',
            'KILL', 'SAVE', 'CALL', 'RSET', 'BEEP', 'BASE', 'AUTO', 'GOTO', 'READ',
            'PSET', 'POKE', 'PLAY', 'PAD', 'EOF', 'VAL', 'TAN', 'CVS', 'CVI', 'CVD',
            'LOG', 'LOF', 'COS', 'LOC', 'SQR', 'SIN', 'LEN', 'SGN', 'INT', 'RND',
            'INP', 'ATN', 'ASC', 'FRE', 'ABS', 'POS', 'FIX', 'EXP', 'PDL', 'REM',
            'ERL', 'OUT', 'EQV', 'XOR', 'END', 'OFF', 'NOT', 'VDP', 'NEW', 'DIM',
            'USR', 'MOD', 'DEF', 'MAX', 'TAB', 'CMD', 'SPC', 'CLS', 'LET', 'SET',
            'KEY', 'IPL', 'RUN', 'IMP', 'PUT', 'GET', 'AND', 'FOR', 'ERR', 'AS',
            'OR', 'ON', 'TO', 'IF', 'FN']

branching = ['RESTORE', 'AUTO', 'RENUM', 'DELETE', 'RESUME', 'ERL', 'ELSE',
             'RUN', 'LIST', 'LLIST', 'GOTO', 'RETURN', 'THEN', 'GOSUB']


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


show_log('', 'Loading file', 3)
classic_code = []
if file_load:
    show_log('', ' '.join(['Load_file:', file_load]), 4)
    try:
        with open(file_load, 'r', encoding='latin1') as f:
            for line in f:
                classic_code.append(line.strip())
    except IOError:
        show_log('', ' '.join(['Source_not_found', file_load]), 1)  # Exit
else:
    show_log('', 'Source_not_given', 1)  # Exit


elements = (r'(?:'
            r'(?P<num>[0-9]+)'
            r"|(?P<rem>(?:REM|').*)"
            r'|(?P<dat>(?:DATA).*?(?=\:|$))'
            r'%s'
            r'|(?P<key>' + r'|'.join(keywords) + r')'
            r'|(?P<str>"(?:[^"]*)(?:"|$))'
            r'|(?P<all>.)'
            r')'
            )

print_at = r'|(?P<lpa>^\b$)'  # Create a lpa key that matches nothing
if print_tgl:
    print_at = r'|(?P<lpa>(?:LOCATE)(?P<cor>[^:]*?):\s*PRINT)'

match_elem = re.compile(elements % print_at, re.I)

show_log('', 'Converting lines', 3)
prev_grp = ''
prev_line = 0
dig_dict = {}
line_labels = {}
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

    g = match_elem.match(line)
    p = g.end()
    if not g.group('num'):
        show_log('', 'No_line_number', 1)  # Exit

    line_number = int(g.group().strip())
    if line_number < prev_line:
        show_log(line_number, 'Line_number_out_of_order', 1)  # Exit
    prev_line = line_number

    dig_line = ''
    get_lnumber = False
    while True:

        prev_ch = line[p - 1:p].upper()
        prev_spc = ''
        if (('A' <= prev_ch <= 'Z' or '0' <= prev_ch <= '9')
                and prev_grp != 'key' and prev_grp != 'lpa'):
            prev_spc = ' '

        next_ch = line[p:p + 1]
        if not next_ch.isdigit() and next_ch != ' ':
            if next_ch == ',' and get_lnumber:
                get_lnumber = True
            else:
                get_lnumber = False

        if p >= len(line):
            break

        g = match_elem.match(line, p)
        p = g.end()
        match = g.group()

        next_ch = line[p:p + 1].upper()
        next_spc = ''
        if 'A' <= next_ch <= 'Z' or '0' <= next_ch <= '9':
            next_spc = ' '

        prev_grp = ''
        if g.group('key'):
            prev_grp = 'key'
            match = prev_spc + g.group().lower() + next_spc
            if match.strip().upper() in branching:
                get_lnumber = True

        elif g.group('lpa'):
            prev_grp = 'lpa'
            item = g.group("cor")
            item = item.replace(' ', '')
            show_log(line_number, f'Converted_to: [?@]{item}', 4)
            space = '' if next_ch == ' ' else ' '
            match = f'[?@]{item}{space}'

        elif g.group('num') and get_lnumber:
            if int(match) == line_number:
                show_log(line_number, f'Found_self_jump: {match}', 4)
                match = '{@}'
            else:
                show_log(line_number, f'Found_jump: {match}', 4)
                item = line_labels.get(match.strip(), [])
                item.append(line_number)
                line_labels[int(match.strip())] = item
                match = f'{{l_{match.strip()}}}'

        elif g.group('rem'):
            if g.group().upper().startswith('R'):
                match = 'rem' + next_spc + match[3:]
            else:
                match = match

        elif g.group('dat'):
            match = 'data ' + next_spc + match[4:]

        elif g.group('str'):
            match = match

        else:
            match = match.lower()

        dig_line += match

    dig_dict[line_number] = dig_line.lstrip()

show_log('', 'Checking for branching errors', 3)
for lines in line_labels:
    if lines not in dig_dict:
        for line in line_labels[lines]:
            show_log(line, f'Line_does_not_exist: {lines}', 2)

show_log('', 'Assembling final code', 3)
n = 0
ident = ''
dignified_code = []
for line in sorted(dig_dict.keys()):
    n += 1
    if line in line_labels:
        show_log(n, f'Created_label: {{l_{str(line)}}}', 4)
        n += 1
        if lline_tgl:
            dignified_code.append('\n')
        if ident_tgl:
            ident = '\t'
        dignified_code.append(f'{{l_{str(line)}}}\n')
    dignified_code.append(ident + dig_dict[line] + '\n')

show_log('', ' '.join(['File saving']), 3)
try:
    with open(file_save, 'w') as f:
        show_log('', ' '.join(['Saving_file:', file_save]), 4)
        for line in dignified_code:
            f.write(line)
except IOError as e:
    show_log('', ' '.join([str(e)]), 1)  # Exit

# for line in dignified_code:
    # print(line.strip())
