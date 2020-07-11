#!/usr/bin/env python3
'''
MSX Basic DignifiER
v1.1
Convert traditional MSX Basic to modern MSX Basic Dignified format.

Copyright (C) 2020 - Fred Rique (farique)
https://github.com/farique1/msx-basic-dignified

TODO:
    Make an .ini file
    Redirect broken jumps to the next line on removed REMs
    Option to normalize all spaces
    Remove spaces around : before reapplying
    Force together character pairs without capturing a group
    Check for : when unraveling at the beginning of ELSE
    Unravel only FORs (with indentation option)
    Unravel only IFs (with indentation option)
    Centralize all unravel/indent options on a single variable:
        ie. 'adidfdtbe' a=all f=for i=if t=then b=bef_else e=aft_else
                        d=indentation, modify the item before, id=indent_if
'''

import re
import os.path
import argparse

instr = ['AND', 'BASE', 'BEEP', 'BLOAD', 'BSAVE', 'CALL', 'CIRCLE',
         'CLEAR', 'CLOAD', 'CLOSE', 'CLS', 'CMD', 'COLOR', 'CONT', 'COPY',
         'CSAVE', 'CSRLIN', 'DATA', 'DEF', 'DEFDBL', 'DEFINT', 'DEFSNG',
         'DEFSTR', 'DIM', 'DRAW', 'DSKI', 'END', 'EQV', 'ERASE', 'ERR',
         'ERROR', 'FIELD', 'FILES', 'FN', 'FOR', 'GET', 'IF', 'INPUT', 'IMP',
         'IPL', 'KILL', 'LET', 'LFILES', 'LINE', 'LOAD', 'LOCATE', 'LPRINT',
         'LSET', 'MAX', 'MERGE', 'MOD', 'MOTOR', 'NAME', 'NEW', 'NEXT', 'NOT',
         'OFF', 'ON', 'OPEN', 'OR', 'OUT', 'PAINT', 'POINT', 'POKE', 'PRESET',
         'PRINT', 'PSET', 'PUT', 'READ', 'REM', 'RSET', 'SAVE', 'SCREEN', 'SET',
         'SOUND', 'STEP', 'STOP', 'SWAP', 'TIME', 'TO', 'TROFF', 'TRON',
         'USING', 'VPOKE', 'WAIT', 'WIDTH', 'XOR', r'\?', "'"]  # 'AS',

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

file_load = 'basictests/Trek3T.asc'         # Source file
file_save = ''         # Destination file
ident_tgl = True       # Add indent to non label lines
lline_tgl = True       # Add blank line before labels
print_tgl = False      # Convert locate:print to [?@]
remove_rem = ''        # Remove REMs. l=line, i=inline
unravel_then = ''      # Break after THEN/ELSE. t=after THEN, e=after ELSE b=before ELSE
unravel_lines = ''     # Break lines at ':'. i=with indent, w=without indent
verbose_level = 2      # Show processing status: 0-silent 1-+errors 2-+warnings 3-+steps 4-+details
# Put a space before and/or after a keyword if preceded/followed by this matches
repelcbef = r'[a-z0-9{}")]'
repelcaft = r'[a-z0-9{}"(]'
# Force this matches to be together
forcetogt = r'(<=|>=|=<|=>|\)-\()'
# Force a space before and/or after this matches
spacesbef = r'^(#|\+|-|\*|/|\^|\\)$'
spacesaft = r'^(\+|-|\*|/|\^|\\)$'

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
                    help='Convert locatex,y:print to [?@]x,y')
parser.add_argument("-rr", default=remove_rem, choices=['l', 'i'], type=str.lower,
                    help='Remove REMs: l=Line REMs, i=inline REMs'
                    ' (Can mix letters together)')
parser.add_argument("-ut", default=unravel_then, choices=['t', 'e', 'b'], type=str.lower,
                    help='Break after THEN/ELSE. t=after THEN, e=after ELSE b=before ELSE'
                    ' (Can mix letters together)')
parser.add_argument("-ul", default=unravel_lines, choices=['i', 'w'], type=str.lower,
                    help='Break lines after ":". i=with indent, w=without indent')
parser.add_argument("-rb", default=repelcbef, type=str,
                    help='Regex matches to add a space before a keyword and them: '
                         f'def {repelcbef}')
parser.add_argument("-ra", default=repelcaft, type=str,
                    help='Regex matches to add a space after a keyword and them: '
                         f'def {repelcaft}')
parser.add_argument("-sb", default=spacesbef, type=str,
                    help='Regex matches to force a space before them: '
                         f'def {spacesbef}')
parser.add_argument("-sa", default=spacesaft, type=str,
                    help='Regex matches to force a space after them: '
                         f'def {spacesaft}')
parser.add_argument("-ft", default=forcetogt, type=str,
                    help='Regex matches forcing them to stick together: '
                         f'def {forcetogt}')
parser.add_argument('-vb', default=verbose_level, type=int,
                    help='Verbosity level: 0=silent, 1=errors, '
                    '2=1+warnings, 3=2+steps(def), 4=3+details')
args = parser.parse_args()

# Apply chosen settings
file_load = args.input
file_save = args.output
if args.output == '':
    save_path = os.path.dirname(file_load)
    save_path = '' if save_path == '' else save_path + '/'
    save_temp = os.path.basename(file_load)
    save_temp = os.path.splitext(save_temp)[0] + '.bad'
    file_save = save_path + save_temp
ident_tgl = args.it
lline_tgl = args.lt
print_tgl = args.pt
remove_rem = args.rr
unravel_lines = args.ul
unravel_then = args.ut
if not unravel_lines:
    unravel_then = ''
repelcbef = args.rb
repelcaft = args.ra
spacesbef = args.sb
spacesaft = args.sa
forcetogt = args.ft
verbose_level = args.vb

keywords = instr + funct + branc
keywords.sort(key=len, reverse=True)

keyw_list = '|'.join(keywords)
elements = (r'(?:'
            r'%s'
            r'|(?P<flo>\d*\.(\d+[EDed][+-]\d+|\d*))'
            r'|(?P<int>\d+)'
            fr'|(?P<key>{keyw_list})'
            fr'|(?P<glu>{forcetogt})'
            r'|(?P<all>.)'
            r')'
            )

match_int = re.compile(r'\s*\d+')
variables = re.compile(r'[a-z0-9$#!%]', re.I)
has_print = re.compile(r'([^:]+?)(?::\s*print)', re.I)

getstrings = r'(?P<lit>"(?:[^"]*)(?:"|$))'
to_endline = r'(?P<lit>.*$)'
to_endsect = r'(?P<lit>.*?(?=\:|$))'

match_elements = re.compile(elements % getstrings, re.I)
match_tendline = re.compile(elements % to_endline, re.I)
match_tendsect = re.compile(elements % to_endsect, re.I)


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
    show_log('', 'Loading file', 3)
    classic_code = []
    if file_load:
        try:
            with open(file_load, 'r', encoding='latin1') as f:
                for line in f:
                    classic_code.append(line.strip())
            return classic_code
        except IOError:
            show_log('', f'Source_not_found {file_load}', 1)  # Exit
    else:
        show_log('', 'Source_not_given', 1)  # Exit


def save_file(dignified_code, file_save):
    show_log('', 'File saving', 3)
    try:
        with open(file_save, 'w') as f:
            for line in dignified_code:
                f.write(line)
    except IOError as e:
        show_log('', str(e), 1)  # Exit


def check_space(char, patt, g):
    match = g.group()
    esc_match = match.upper().replace('$', r'\$')
    if g.lastgroup == 'key' and esc_match in funct:
        patt = patt.replace('(', '')
    space = ''
    if re.match(patt, char, re.I):
        space = ' '
    return space


def force_space(match):
    if re.match(spacesbef, match.strip(), re.I):
        match = ' ' + match
    if re.match(spacesaft, match.strip(), re.I):
        match = match + ' '
    return match


def check_labels(dignified_dict, labels):
    show_log('', 'Checking for branching errors', 3)
    for lines in labels:
        if lines not in dignified_dict:
            for line in labels[lines]:
                show_log(line, f'Line_does_not_exist: {lines}', 2)


def assemble_dignified(dignified_dict, labels):
    show_log('', 'Assembling Dignified code', 3)
    ident = ''
    dignified_code = []
    for line in sorted(dignified_dict.keys()):

        if line in labels:

            if lline_tgl:
                dignified_code.append('\n')

            if ident_tgl:
                ident = '\t'

            dignified_code.append(f'{{l_{str(int(line))}}}\n')

        dignified_code.append(ident + dignified_dict[line] + '\n')

    return dignified_code


def do_lines(lnumber, line, g, p, labels):
    buff = ''
    match = ' '
    l_idnt = ''
    dig_line = ''
    dig_list = []
    keep_caps = False
    get_lnumber = False
    repeat_match = False
    match_current = match_elements
    while p < len(line):
        split = False

        l_match = match[-1].upper()
        prev_spc = check_space(l_match, repelcbef, g)

        g = match_current.match(line, p)
        p = g.end()
        match = g.group()
        match_current = match_elements
        next_int = match_int.match(line, p)

        l_match = line[p:p + 1].upper()
        next_spc = check_space(l_match, repelcaft, g)

        if get_lnumber and (g.lastgroup != 'int'
                            and match != ','
                            and match != ' '):
            get_lnumber = False

        if g.group('key'):
            match = match.upper()

            if p < len(line):
                if match == 'REM' or match == "'":
                    match_current = match_tendline

                    if (('l' in remove_rem and not dig_list)
                            or ('i' in remove_rem and dig_list)):
                        match = ''
                        p = len(line)
                        if dig_list and not dig_line.strip():
                            dig_list[-1] = dig_list[-1][:-1]

                if match == 'DATA':
                    match_current = match_tendsect

                if match == 'LOCATE' and print_tgl:
                    if haslocp := has_print.match(line, p):
                        locpgrp = haslocp.group(1)
                        locinfo, _ = do_lines(0, locpgrp, g, 0, [])
                        locinfo = ''.join(locinfo).replace(' ', '')
                        match = f'[?@]{locinfo}'
                        p = haslocp.end()
                        next_spc = ''
                        if line[p] != ' ':
                            next_spc = ' '

                if (match == 'THEN' and not next_int
                        and 't' in unravel_then):
                    match += ' _'
                    split = True

                if ((match == 'ELSE' and not next_int)
                        and ('e' in unravel_then or 'b' in unravel_then)):
                    if 'b' in unravel_then and not repeat_match:
                        match = '_'
                        p = g.start()
                        split = True
                        repeat_match = True
                    elif 'b' in unravel_then and repeat_match:
                        repeat_match = False
                    if 'e' in unravel_then and not repeat_match:
                        match += ' _'
                        split = True

            if match in branc:
                get_lnumber = True

            match = prev_spc + match + next_spc

        elif g.group('int') and get_lnumber:
            if int(match) == lnumber:
                match = '{@}'
            else:
                item = labels.get(int(match), [])
                item.append(lnumber)
                labels[int(match)] = item

                match = f'{{l_{match.strip()}}}'

        elif g.group('lit'):
            keep_caps = True

        match = force_space(match)

        if not keep_caps:
            match = match.lower()

        if match == ':' or p >= len(line):
            split = True

        keep_caps = False

        if (p < len(line)
                and not g.group('key')
                and variables.match(match)):
            buff += match
        else:

            # if buff != '' and buff != ' ':
            #     print(buff.strip())
            # if match != '' and match != ' ':
            #     print(match)

            dig_line += buff
            dig_line += match
            buff = ''

        if split:
            dig_list.append(l_idnt + dig_line.strip())
            line = line[p:]
            dig_line = ''
            p = 0
            if unravel_lines == 'i':
                l_idnt = '\t'

    dig_list = [x for x in dig_list if x.strip()]
    if not unravel_lines and dig_list:
        dig_list = [''.join(dig_list)]

    return dig_list, labels


def dignify(classic_code):
    show_log('', 'Converting lines', 3)
    prev_line = 0
    lnumber = 0
    dignified_dict = {}
    labels = {}
    for line in classic_code:
        line = line.strip() + '\r'

        if line == '\r':
            continue

        if line == '':
            show_log(prev_line, f'Blank_line_(after)', 2)
            continue

        if line.isdigit():
            show_log(line, 'Line_number_alone', 2)
            continue

        if not line[0].isdigit():
            show_log(lnumber, 'No_line_number_(after)', 1)  # Exit

        g = match_elements.match(line)
        p = g.end()

        lnumber = int(g.group().strip())
        if lnumber < prev_line:
            show_log(lnumber, 'Line_number_out_of_order', 1)  # Exit

        prev_line = lnumber

        dig_list, labels = do_lines(lnumber, line, g, p, labels)

        for n, dig_line in enumerate(dig_list):
            dig_line = dig_line
            clean_lnum = lnumber + (n / 10)
            dignified_dict[clean_lnum] = dig_line

    check_labels(dignified_dict, labels)
    return assemble_dignified(dignified_dict, labels)


def main():
    classic_code = load_file(file_load)

    dignified_code = dignify(classic_code)

    save_file(dignified_code, file_save)


if __name__ == '__main__':
    main()
