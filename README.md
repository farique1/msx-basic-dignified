# MSX Basic Dignified
**Or: My First Python Project.**  
Or: How to learn a new language?

- Find something that doesn't exist.
- This thing must be useful to someone.
- Bonus if you once really wanted it to exist.
- But the fate of the world should not rest upon it
- Sit down and do it on the language you want to learn. 

And so this project was born.  
And so this project is (for now) an atrocious example of Python coding.

**MSX Basic Dignified** allows you to code MSX Basic programs using modern coding standards on your preferred editor, convert them to the old MSX Basic structure and load into an MSX (emulated or not.)

I felt the need for something like this when I was redoing **Change Graph Kit**, an MSX program I did back in the day, just to see how much I could improve it. I coded on Sublime and used Excel, REM tags and a lot of patience to add line numbers, not pretty.

Long after the **CGK** episode I discovered [Tabmegx](http://ni.x0.com/msx/tabmegx/) and also found [Inliner](https://giovannireisnunes.wordpress.com/meu-software/inliner/) ([GitHub](https://github.com/plainspooky/inliner)) during research for **MBD**. They were both great sources of 'inspiration'.

> There is a syntax highlight, a theme and a comment setting available for Sublime 3 [here]() to improve the **MBD** experience. They work with the rules set by **MBD** but are an all around good MSX Basic syntax.

>Please, be aware that **MBD** is by no mean a finished product and is expected to misbehave sometimes. 

## Features and usage
### Standard behaviour

Run with `msxbadig.py [source] [destination] args...`  
`msxbadig.py` reads a text file containing the modern source code and write back a text file with the MSX Basic conformed code. If no `[destination]` name is given, the file will be saved as `[source]_.ext` (a single underscore after the original name)

**MBD** is highly configurable and can use the built in settings, an .ini file or command line instructions with an order of priority inverse to that.

>From now on, when showing code, usually the first excerpt is the source, followed by the program call and the converted output.

- The MSX Basic 'source code' can be written **without line numbers** and **indented** using TAB or spaces. *More on these later.*
```basic
{count_loop}
	for f = 1 to 10
		print f; 
	next
return
```
`msxbadig.py test.bas`
```basic
10 ' {count_loop}
20 FOR f = 1 TO 10
30 PRINT F;
40 NEXT
50 RETURN
```

- Branching instructions are done with **labels**.  
 Labels are created using curly brackets`{like_this}` and strongly advised to only contain letters, numbers and underscore.  
 `{@}` points to its own line (abraço, Giovanni!).  
Orphan labels and labels not following the naming convention are converted with `{{label}}` (double brackets) and higlighted when using [`MSX Basic.sublime-syntax`]().  
*More on labels later.*
```basic
{hello_loop}
print "hello world "; 
if inkey$ = "" then goto {@} else goto {hello_loop}
```
`msxbadig.py test.bas`
```basic
10 ' {hello_loop}
20 PRINT "hello world "; 
30 IF INKEY$ = "" THEN GOTO 30 ELSE GOTO 10
```


- **Defines** are used to create aliases on the code that are replaced upon conversion. They are created with `define [name] [content]` where the `[content]` will replace the `[name]`. There can be as many defines as necessary.  
`[?@]x,y` is a built in **Define** that becomes `LOCATEx,y:PRINT`
```basic
define [ifa] [if a$ = ]
[ifa]"1" then print "um"
[ifa]"2" then print "dois"
[?@]10,10 "quatro"
```
`msxbadig.py test.bas`
```basic
10 IF A$ = "1" THEN PRINT "um"
20 IF A$ = "2" THEN PRINT "dois"
30 LOCATE 10,10:PRINT "quatro"
```
- Multi line instructions can be **joined** using `:` or `_` to form a single line. Colons are retained, separating instructions, and can be used at the end or beginning of a line. Underscores are deleted and can join broken instructions.  
`endif`s can be used but are for cosmetical or organisational purpose only. They are stripped upon conversion without any check or validation.
```basic
if a$ = "C" then _
	for f = 1 to 10:
		locate 1,1:print f:
	next
	:locate 1,3:print "done"
	:end
endif
```
`msxbadig.py test.bas`
```basic
10 IF A$ = "C" THEN FOR F = 1 TO 10:LOCATE 1,1:PRINT F:NEXT:LOCATE 1,3:PRINT "done":END
```
- The source code can use exclusive **comments** `##` that are stripped on the conversion.  
Regular `rem`s are kept. (a bug keep the `##` if there is a `"` after it)
```
## this will not be converted
rem this will
' this also will
```

### Configurable arguments
Most of **MBD** functionality is configurable through an .ini file (`ini: ...`) or command line arguments (`arg: ...`) as follow. You can generate the .ini file with the `-ini` argument.

**Files**
- *Source file*  
The modern formatted code file to be read.  
`ini: source_file = ` `arg: <source>` 

- *Destination file*  

MSX Basic formatted code file to be saved.

`ini: destin_file = ` `args: <> <destination>`

`<source>_.ext`  will be used if no name is given.

**Numbering**
- *Starting line number*
The number of the first line.
`ini: line_start = ` `arg: -ls #` `Default: 10`

- *Line step value*
The line numbering increment amount.
`ini: line_step = ` `arg: -lp #` `Default: 10`

- *Add leading zeros*
Line numbers can be padded with zeroes, this helps to review the converted code on an editor.
`ini: leading_zeros = ` `arg: -lz` `Default: False`
###
`msxbadig.py test.bas -ls 5 -lp 5`
```basic
5 PRINT "Say something"
10 DO$ = "Do something"
15 GOTO 5
```
###
`msxbadig.py test.bas -ls 1 -lp 50 -lz`
```basic
001 PRINT "Say something"
051 DO$ = "Do something"
101 GOTO 1
``` 
**Labels**
- *Label conversions*
Handle how labels are converted.
`ini: handle_label_lines = ` `arg: -ll {0,1,2}` `Default: 0`
The labels can be left, as default, on a `rem` line with its name (option `0`) or without it (option `1`)  as an anchor and reminder; the branching lines are directed to the label line itself. Or they can be stripped altogether (option `2`), leaving a smaller, more concise code; the code flow is directed to the line mediately after where the label was.
###
`msxbadig.py test.bas`
```basic
10 ' {print_result}
20 PRINT "Result ";
30 GOTO 10
```
###
`msxbadig.py test.bas -ll 1`
```basic
10 '
20 PRINT "Result ";
30 GOTO 10
```
###
`msxbadig.py test.bas -ll 2`
```basic
10 PRINT "Result ";
20 GOTO 10
```
- *Show branching labels*
Show labels on lines with branching instructions.
`ini: show_branches_labels = ` `arg: -sl` `Default: False`
Add a `:rem` at the end of the line with the label names used on the branching instructions.
```basic
10 ' {print_result}
20 PRINT "Result ";
30 GOTO 10:' {print_result}
```
**Blank lines**
Blank lines are stripped from the source by default but they can be left as can extra lines be added for clarity and organization.

- *Keep blank lines*
Do not erase blank lines on the converted code, keep them with `rem`.
`ini: keep_blank_lines = ` `arg: -bl` `Default: False`

- Add line before a label
Add a blank line **before** a label. (has no effect if opted to strip labels)
`ini: rem_bef_label = ` `arg: -br` `Default: False`

- Add line after a label
Add a blank line **after** a label. (has no effect if opted to strip labels)
`ini: rem_aft_label = ` `arg: -ar` `Default: False`

```basic
{print_result}
	PRINT "Result ";
	
	GOTO {print_result}
```
`msxbadig.py test.bas -bl -ar`
```basic
10 ' {print_result}
20 '
30 PRINT "Result ";
40 '
50 GOTO 10
```
**Spacing**
Spacing and indentation are automatically streamlined and removed from the converted code.
This behaviour can be configured, however, to suit personal tastes.

- *Number of spaces before `:`*
Add a number of spaces **before** the instruction separating character (`:`) on multi instruction lines.
`ini: nnbr_spaces_bef_colon = ` `arg: -bc #` `Default: 0`

- *Number of spaces after `:`*
Add a number of spaces **after** the instruction separating character (`:`) on multi instruction lines.
`ini: nnbr_spaces_aft_colon = ` `arg: -ac #` `Default: 0`

- *Amount of general spacing*
The conversion automatically strips all blanks (**spaces** or **TAB**s) on the code (not including indents or `:`) leaving only 1 space throughout. This amount can be changed with:
`ini: nmbr_spaces_general = ` `arg: -gs #` `Default: 1`

- *Keep original spaces*
Mantains the original spacing used on the source code (**TAB**s and all).
`ini: keep_original_spaces = ` `arg: -ks` `Default: False`

```basic
for f = 10  to 7  :read a: print a  : next
for f = 0   to 9  :read a: print a  : next
for f = 100 to 300:read a: print a+1: next
```
`msxbadig.py test.bas -bc 1 -gs 0`
```basic
10 FORF=10TO7 :READA :PRINTA :NEXT
20 FORF=0TO9 :READA :PRINTA :NEXT
30 FORF=100TO300 :READA :PRINTA+1 :NEXT
```
**Indentation**
MBD by default also strips all indentation used on the source code.
This can be mitigated and refined in three ways.

- *Keep indentation*
Try to maintain the original indentation. **TAB**s are converted to **spaces** (2 by default).
`ini: keep_indent =`  `arg: -ki`  `Default: False`

- *Number of spaces per TAB on indentation*
Change the default amount of **spaces** per **TAB**.
`ini: indent_tab_spaces =`  `arg: -si #`  `Default: 2`

- *Keep space characters on indents*
**Spaces** to fine tune that tough indent (don't do this!) usually become too much on the conversion, they are removed by default but can be kept.
`ini: keep_indent_space_chars =`  `arg: -ci`  `Default: False`

```basic
for f = 1 to 200
	print "Beware"
	 if f = 100 then print "Middle point reached!"
next
```
`msxbadig.py test.bas -ki -ci`
```basic
10 FOR F = 1 TO 200
20   PRINT "Beware"
30    IF F = 100 THEN PRINT "Middle point reached!"
40 NEXT
```

**Comments**
The conversion needs `REM`s on occasion to keep some original formatting; they can be redefined as such:

- *Labels `REM` format*
When converted, **labels** are put on `REM` lines. By default they all are applied as `'` (option `s`).
They can, however, be told to use the regular form (option `rem`) : 
`ini: label_rem_format =`  `arg: -lr {s,rem}`  `Default: s`

- *Regular `REM` format*
Some **non label** `REM`s are also created sometimes, They are also applied as `'` (option `s`).
They can, however, be told to use the regular form (option `rem`) :
`ini: regul_rem_format =`  `arg: -rr {s,rem}`  `Default: s`

- *Convert all `REM`s*
All **pre existing** `REM`s can be changed to maintain coherence along the converted code. They will use the previously set conditions.
`ini: convert_rem_formats =`  `arg: -cr`  `Default: False`

```basic
{start_tutorial}
	print "What tutorial?"
	rem Nevermid
```
`msxbadig.py test.bas -lr rem -cr`
```basic
10 REM {start_tutorial}
20 PRINT "What tutorial?"
30 ' Nevermid
```

**General conversions**
- *Capitalise*
By default all text is **capitalised**, with the exception of `""`, `{labels}` and `REM`s
This can be controlled with:
`ini: capitalize_all =`  `arg: -nc`  `Default: True`

- *Convert `?` to `PRINT`*
`?` as `PRINT` are left alone on the conversion, they can be told to become `PRINT` with:
`ini: convert_interr_to_print =`  `arg: -cp`  `Default: False`

- *Strip adjacent `THEN`/`ELSE` or `GOTO`s*
MSX Basic doesn't need both `THEN` or `ELSE` and `GOTO` if they are adjacent.
The converted code can be told to strip the `THEN`/`ELSE` (option `t`), `GOTO` (option `g`) or they can all, as default, be left alone (option `k`)
`ini: strip_then_goto =`  `arg: -tg {t,g,k}`  `Default: k`

```basic
{at_last}
	? "What?"
	if me$ = "Come again!" then goto {at_last} else goto {i_agree}
	? "Bummer"
	end
{i_agree}
	rem That is all folks
```
`msxbadig.py test.bas -nc -cp -tg g`
```basic
10 ' {at_last}
20 print "What?"
30 if me$ = "Come again!" then 10 else 60
40 print "Bummer"
50 end
60 ' {i_agree}
70 rem That is all folks
```

**Misc**

- *Help*
Help is available using:
`msxbadig.py -h`

- *Verbose*
Set increasing leves of feedback given by the program.
`ini: verbose_level =`  `arg: -vb {0,1,2,3}`  `Default: 2`
`0` gives nothing, `1` shows the conversion steps, `2` the default, error and warning messages and `3` everything else.

- *Use the `.ini` file*
If the `.ini` file configuration should be used or not, allowing it to be disabled in place.
`ini: use_ini_file =` `Default: True`

- *Write the `.ini` file*
Rewites the `.ini` file in case its is missing.

## Technicalities and warnings
### Yes, they are one and the same

**MSX Basic Dignfied** was made  to run on a Mac OS stock Python installation, version 2.7.10.
The process of creating **MBD** was basically that I opened Sublime, Google and Terminal with zero Python knowledge and five days latter here we are (plus twoish more days to write this and understand Git (hey, I'm old))
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTEyOTI0OTg1MzAsLTE5MzkxNDgyMjFdfQ
==
-->