  
![# MSX Basic Dignified](https://github.com/farique1/msx-basic-dignified/blob/master/Images/msxbadig-logo.png)  
# MSX Basic Dignified  
  
## **`v1.1`**  
 >According to the Semantic Versioning it was supposed to be v2 (slightly incompatible with the previous version) but I'm not ready yet. Go see the [changelog](https://github.com/farique1/msx-basic-dignified/blob/master/changelog.md).
  
**Or: My First Python Project.**  
Or: How to learn a new language?  
  
- Find something that doesn't exist.  
(well, not so much, it turns out)  
- This thing must be useful to someone.  
- Bonus if you once really wanted it to exist.  
- But the fate of the world should not rest upon it  
- Sit down and do it on the language you want to learn.  
  
And so this project was born.  
And so this project is (~~for now~~ after some messing) an ~~atrocious~~ still not incredible example of Python coding.  
  
  
**MSX Basic Dignified** allows you to code MSX Basic programs using modern coding standards on your preferred editor, convert them to the old MSX Basic structure and load it into an MSX (emulated or not.)  
  
I felt the need for something like this when I was redoing [**Change Graph Kit**](https://github.com/farique1/Change-Graph-Kit), an MSX program I did back in the day, just to see how much I could improve it. I coded on Sublime and used Excel, REM tags and a lot of patience to add line numbers and such, not pretty.  
  
Long after the **CGK** episode I discovered [Tabmegx](http://ni.x0.com/msx/tabmegx/) and also found [Inliner](https://giovannireisnunes.wordpress.com/meu-software/inliner/) ([GitHub](https://github.com/plainspooky/inliner)) during research for **MBD**. They were both great sources of 'inspiration' but I wanted something even closer to the workflow I have been working on with other languages.  
  
> There is a [*Syntax Highlight*, a *Theme*, a *Comment Setting* and a *Build System*](https://github.com/farique1/MSX-Sublime-Syntax) available for **Sublime Text 3** working with the **MBD** rules to help improve the overall experience.  
There is also a specific syntax highlight for the Classic MSX Basic and a system to run the classic Basic straight from Sublime 3.  
  
![# Versions.png](https://github.com/farique1/msx-basic-dignified/blob/master/Images/Versions.png)  
  
>Please, be aware that **MBD** and its tools are by no mean finished products and are expected to misbehave.  
  
## Features and usage  
### Standard behaviour  
  
Run with `msxbadig.py [source] [destination] args...`  
`msxbadig.py` reads a text file containing the modern source code and write back a text file with the Classic MSX Basic code. If no `[destination]` name is given, the file will be saved as `[source].bas`.  
**MBD** displays a log with the steps taken (configurable) and will show warnings and errors, stopping execution, when needed.  
  
>Special characters do not translate nicely between MSX Basic ASCII and UTF. The best match so far is the  `Western (Windows 1252)` encoding; it will not translate the characters but will preserve the ones typed on the MSX.  
  
**MBD** is highly configurable and can use the built in settings, an .ini file or command line instructions with an order of priority inverse to that.  
  
>From now on, when showing code, usually the first excerpt is the source, followed by the program call and the converted output.  
  
- The MSX Basic Dignified 'source code' can be written **without line numbers**, **indented** using TAB or spaces and have **long name** variables.  
Different from the Classic MSX Basic, instructions, functions and variables must be separated by spaces from alphanumeric characters. The MSX Syntax Highlight will reflect this and there are several settings to conform the spacing when the conversion is made.  
The Dignified source code should have a `.bad` extension to avoid conflict with the classic code and to better integrate with the supported Sublime tools.  
*More on these later.*  
  
```BlitzBasic  
{count_loop}  
	for f = 1 to 10  
		print f  
	next  
return  
```  
`msxbadig.py test.bad`  
```BlitzBasic  
10 '{count_loop}  
20 FOR F=1 TO 10  
30 PRINT F  
40 NEXT  
50 RETURN  
```  
  
- Directing the code flow is done with **labels**.  
Labels are created using curly brackets`{like_this}` and can be used alone on a line to receive the code flow or on a branching (jump) instruction to direct the flow to the corresponding line label. They can only have letters, numbers and underscore and they cannot be only numbers. `{@}` points to its own line (abraço, Giovanni!).  
Labels marking a section are called line labels and labels on jump instructions  (`GOTO`, `GOSUB`, etc) are called branching labels.  
Labels not following the naming convention or branching to inexistent line labels will generate an error and stop the conversion. Labels with illegal characters are higlighted when using the MSX Syntax Highlight.  
*More on labels later.*  
```BlitzBasic  
{hello_loop}  
print "hello world"  
if inkey$ = "" then goto {@} else goto {hello_loop}  
```  
`msxbadig.py test.bad`  
```BlitzBasic  
10 ' {hello_loop}  
20 PRINT "hello world"  
30 IF INKEY$="" THEN GOTO 30 ELSE GOTO 10  
```  
  
- **Defines** are used to create aliases on the code that are replaced when the conversion is made. They are created with `define [name] [content]` where the `[content]` will replace the `[name]`. There can be as many as needed and there can be several on the same line, separated by commas: `define [name1] [content1], [name2] [content2], [name3] [content3]`.  
`[?@]x,y ` is a built in **Define** that becomes `LOCATEx,y:PRINT`, it must be followed by an empty space.  
```BlitzBasic  
define [ifa] [if a$ = ]  
[ifa]"2" then print "dois"  
[ifa]"4" then print "quatro"  
[?@]10,10 "dez"  
```  
`msxbadig.py test.bad`  
```BlitzBasic  
10 IF A$="2" THEN PRINT "dois"  
20 IF A$="4" THEN PRINT "quatro"  
30 LOCATE 10,10:PRINT "dez"  
```  
  
- **Long name variables** can be used with **MBD** code.  
They must have only letters, numbers and underscore and cannot be less than 3 characters or be only numbers. There are for the moment only two types: double precision (default) and strings (followed by an `$`). As is the case with the instructions, they must be separated by empty spaces from other alphanumeric characters or commands (the non alpha characters `~` or `$` on the variables can touch other commands).  
When converted they are replaced by associated standard two letter variables. They are assigned on a descending order from `ZZ` to `AA` and single letters or numbers are never used. There are two sets of short names assigned, one for the strings, with `$`, and one for the numeric.  
To use these variables they must be declared, there are two ways to do that:  
  -- On a `declare` line, separated by commas: `declare variable1, variable2, variable3`.  
  -- In place, preceded by an `~`: `~long_var = 3`.  
When the first long name is used with an `~` or on a `declare` line a new two letter variable is assigned to it, the next time it is used, even with the `~` the previous assignment is maintained.  
After it is assigned, a long name variable can be used without the `~` but a variable without the `~` that has not been previously assigned will not be converted, will not even generate any erros or warnings.  
Classic one and two letters variables can be used normally alongside long names ones, just be aware that the letters at the end of the alphabet are being used up and they may clash with the hard coded ones.  
The conversion will try to catch illegal variables when declared but is not always perfect so keep an eye on them.  
The MSX Syntax Highlight will show illegal variables on `declare` lines or when assigned with `~`.  
A summary of the long and short name associations can be generated on `REM`s at the end of the converted code.  
  
```BlitzBasic  
declare food$, drink  
if food$ = "cake" and drink = 3 then _  
	~result = "belly full":  
	~sleep$ = "now"  
endif  
```  
`msxbadig.py test.bad`  
```BlitzBasic  
10 IF ZZ$="cake" AND ZZ=3 THEN ZY="belly full":ZY$="now"  
```  
Optional:  
```BlitzBasic  
20 ' ZZ$-food$, ZZ-drink, ZY$-sleep$, ZY-result  
```  
  
- A single Classic MSX Basic line can be written on several lines on **MBD** using `:` or `_` breaks and **joined** when converting to form a single line.  
Colons `:` can be used at the end of a line (joining the next one) or the beginning of a line (joining the previous one) and are retained when joined. They are used the same way as the Classic MSX Basic, separating different instructions.  
Underscores `_` can only be used at the end of a line and they are deleted when the line is joined. They are useful to join broken instructions like `IF THEN ELSE`, long quotes or anything that must form a single command on the converted code.  
`endif`s can be used (not obligatory) but are for cosmetical or organisational purpose only. They must be alone on their lines and are removed upon conversion without any validation regarding to their `IF`s. If they are not alone and are not part of a `DATA`, `REM` or `QUOTE` they will generate a warning but will not be deleted. `endif`s that are part of any of the previous commands but are alone on a line due to a line break will be deleted.  
Numbers at the start of a line will be removed, generate a warning. Numbers at the beginning of a line after an underscore break `_` will be preserved but numbers at the beginning of a line after a colon `:` break will be removed, even if it is part of a `REM` (there is no need to break a `REM` line with an `:` anyway)  
All of the warning situations above are highlighted with the MSX Syntax Highlight.  
  
```BlitzBasic  
if a$ = "C" then _  
	for f = 1 to 10:  
		locate 1,1:print f:  
	next  
	:locate 1,3:print "done"  
	:end  
endif  
```  
`msxbadig.py test.bad`  
```BlitzBasic  
10 IF A$="C" THEN FOR F=1 TO 10:LOCATE 1,1:PRINT F:NEXT:LOCATE 1,3:PRINT "done":END  
```  
- The source code can use exclusive **comments** `##` that are stripped during the conversion.  
Regular `REM`s are kept. A bug prevents the `##` from being removed if there is a `"` after it.  
```BlitzBasic  
## this will not be converted  
rem this will  
' this also will  
```  
`msxbadig.py test.bad`  
```BlitzBasic  
10 rem this will  
20 ' this also will  
```  
  
### Configurable arguments  
Most of **MBD** functionality is configurable through an .ini file or command line arguments  (`ini:` and `arg:` on the examples below) as follow.  
You can generate the `.ini` file with the `-ini` argument.  
  
**Files**  
- *Source file*  
The modern formatted code file to be read.  
`ini: source_file` `arg: <source>`  
  
- *Destination file*  
MSX Basic formatted code file to be saved.  
`ini: destin_file` `args: <> <destination>`  
If no name is given, the file will be the first 8 characters from the source with a `.bas` extension.  
  
**Numbering**  
- *Starting line number*  
The number of the first line.  
`ini: line_start` `arg: -ls #` `Default: 10`  
  
- *Line step value*  
The line number increment amount.  
`ini: line_step` `arg: -lp #` `Default: 10`  
  
- *Add leading zeros*  
Line numbers can be padded with zeroes, this helps to review the converted code on an editor.  
`ini: leading_zeros` `arg: -lz` `Default: False`  
  
```BlitzBasic  
{do_stuff}  
	print "Say something"  
	do$ = "Do something"  
goto {do_stuff}  
```  
`msxbadig.py test.bad -ls 5 -lp 5`  
```BlitzBasic  
5 ' {do_stuff}  
10 PRINT "Say something"  
15 DO$="Do something"  
20 GOTO 5  
```  
`msxbadig.py test.bad -ls 1 -lp 50 -lz`  
```BlitzBasic  
001 ' {do_stuff}  
051 PRINT "Say something"  
101 DO$="Do something"  
151 GOTO 1  
```  
**Labels**  
- *Label conversions*  
Handle how labels are converted.  
`ini: handle_label_lines` `arg: -ll {0,1,2}` `Default: 0`  
By default (option `0`) line labels are left on the code on a `REM` line for reference.  
Their names can be removed, leaving only a blank `REM` on its place (option `1`)  as an anchor or separator.  
On both cases above the corresponding branching labels are replaced with the line number of the `REM` line where the label is.  
They can also be stripped altogether (option `2`), leaving a smaller, more concise code. In this case the code flow is directed to the line mediately after where the label was.  
###  
```BlitzBasic  
{print_result}  
	print "Result"  
goto {print_result}  
```  
###  
`msxbadig.py test.bad`  
```BlitzBasic  
10 ' {print_result}  
20 PRINT "Result"  
30 GOTO 10  
```  
###  
`msxbadig.py test.bad -ll 1`  
```BlitzBasic  
10 '  
20 PRINT "Result"  
30 GOTO 10  
```  
###  
`msxbadig.py test.bad -ll 2`  
```BlitzBasic  
10 PRINT "Result"  
20 GOTO 10  
```  
- *Show branching labels*  
Show labels on lines with branching instructions.  
`ini: show_branches_labels` `arg: -sl` `Default: False`  
Add a `:rem` at the end of the line with the name of the labels used on its branching instructions making it easier to visualize the flow on the converted code.  
  
```BlitzBasic  
{print_result}  
	print "Result"  
	if r$ = "Result" goto {print_result} else goto {@}  
```  
`msxbadig.py test.bad -sl`  
```BlitzBasic  
10 ' {print_result}  
20 PRINT "Result"  
30 IF R$="Result" GOTO 10 ELSE GOTO 30:' {print_result} {SELF}  
```  
**Blank lines**  
Blank lines are stripped from the source by default but they can also be left on the converted code.  
Extra lines can also be added close to labels for clarity and organization.  
  
- *Keep blank lines*  
Do not erase blank lines on the converted code, convert them to `rem`s.  
`ini: keep_blank_lines` `arg: -bl` `Default: False`  
  
- Add line before a label  
Add a blank line **before** a label. (has no effect if the line labels were removed)  
`ini: rem_bef_label` `arg: -br` `Default: False`  
  
- Add line after a label  
Add a blank line **after** a label. (has no effect if the line labels were removed)  
`ini: rem_aft_label` `arg: -ar` `Default: False`  
  
```BlitzBasic  
{print_result}  
	PRINT "Result"  
  
	GOTO {print_result}  
```  
`msxbadig.py test.bad -bl -ar`  
```BlitzBasic  
10 ' {print_result}  
20 '  
30 PRINT "Result"  
40 '  
50 GOTO 10  
```  
**Spacing**  
Spacing and indentation are automatically streamlined or removed from the converted code.  
This behaviour can be configured, however, as follows.  
  
- *Number of spaces before `:`*  
Add a number of spaces **before** the instruction separating character (`:`) on multi instruction lines.  
`ini: nnbr_spaces_bef_colon` `arg: -bc #` `Default: 0`  
  
- *Number of spaces after `:`*  
Add a number of spaces **after** the instruction separating character (`:`) on multi instruction lines.  
`ini: nnbr_spaces_aft_colon` `arg: -ac #` `Default: 0`  
  
- *Amount of general spacing*  
The conversion automatically strips all blanks (**spaces** and **TAB**s) from the code leaving only 1 space throughout. This amount can be changed with:  
`ini: nmbr_spaces_general` `arg: -gs #` `Default: 1`  
  
- *Unpack operators*  
All spaces surrounding mathematical operators and punctuation (`+-=<>*/^\.,;`) are stripped by default. They can be kept as they were by using:  
`ini: unpack_operators` `arg: -uo` `Default: False`  
  
- *Keep original spaces*  
Mantains the original spacing used on the source code (**TAB**s and **spaces**).  
`ini: keep_original_spaces` `arg: -ks` `Default: False`  
  
```BlitzBasic  
for f = 10  to 7  :read a: print a  : next  
for f = 0   to 9  :read a: print a  : next  
for f = 100 to 300:read a: print a+1: next  
```  
`msxbadig.py test.bad -bc 1 -gs 0`  
```BlitzBasic  
10 FORF=10TO7 :READA :PRINTA :NEXT  
20 FORF=0TO9 :READA :PRINTA :NEXT  
30 FORF=100TO300 :READA :PRINTA+1 :NEXT  
```  
**Indentation**  
**MBD**, by default, also strips all indentation used on the source code. This can be mitigated and refined in three ways.  
  
- *Keep indentation*  
Maintain the original **TAB** indentations by converting them to **spaces** (2 by default).  
`ini: keep_indent` `arg: -ki`  `Default: False`  
  
- *Number of spaces per TAB on indentation*  
Change the default amount of **spaces** per **TAB**.  
`ini: indent_tab_spaces` `arg: -si #`  `Default: 2`  
  
- *Keep space characters on indents*  
If **spaces** are being used to indent the code, this will keep them.  
`ini: keep_indent_space_chars` `arg: -ci`  `Default: False`  
  
```BlitzBasic  
for f = 1 to 200  
	print "Beware"  
	 if f = 100 then print "Middle point reached!"  
next  
```  
`msxbadig.py test.bad -ki -ci`  
```BlitzBasic  
10 FOR F=1 TO 200  
20   PRINT "Beware"  
30    IF F=100 THEN PRINT "Middle point reached!"  
40 NEXT  
```  
  
**Comments**  
The conversion uses `REM`s on certain occasions to keep some original formatting; they can be redefined as such:  
  
- *Labels `REM` format*  
When converted, **labels** are put on `REM` lines. By default they all are applied as `'` (option `s`).  
This also applies to lines added before and after a label by **MBD**.  
They can, however, be told to use the regular form (option `rem`) :  
`ini: label_rem_format`  `arg: -lr {s,rem}`  `Default: s`  
  
- *Regular `REM` format*  
Some **non label** `REM`s are also created sometimes by **MBD**; they are also applied as `'` (option `s`) but they can be told to use the regular form (option `rem`) :  
`ini: regul_rem_format`  `arg: -rr {s,rem}`  `Default: s`  
  
- *Convert all `REM`s*  
All **pre existing** `REM`s (not added by **MBD**) can be changed to maintain coherence along the converted code. The conversion will conform to the two conditions above.  
`ini: convert_rem_formats`  `arg: -cr`  `Default: False`  
  
```BlitzBasic  
{start_tutorial}  
	print "What tutorial?"  
	rem Nevermid  
```  
`msxbadig.py test.bad -lr rem -cr`  
```BlitzBasic  
10 REM {start_tutorial}  
20 PRINT "What tutorial?"  
30 ' Nevermid  
```  
  
**General conversions**  
- *Capitalise*  
By default all text is **capitalised** with the exception of texts inside `""`, `{labels}`, `REM`s and `DATA`s. The original case can be maintained by using:  
`ini: capitalize_all`  `arg: -nc`  `Default: True`  
  
- *Convert `?` to `PRINT`*  
`?` as `PRINT` are left alone on the conversion, they can be told to become `PRINT` with:  
`ini: convert_interr_to_print`  `arg: -cp`  `Default: False`  
  
- *Strip adjacent `THEN`/`ELSE` or `GOTO`s*  
MSX Basic doesn't need both `THEN` or `ELSE` and `GOTO` if they are adjacent. The converted code can be told to strip the `THEN`/`ELSE` (option `t`), `GOTO` (option `g`) or they can all, as default, be left alone (option `k`)  
`ini: strip_then_goto`  `arg: -tg {t,g,k}`  `Default: k`  
  
```BlitzBasic  
{at_last}  
	? "What?"  
	if me$ = "Huh?" then goto {at_last} else goto {i_agree}  
	?:? "Not here."  
{i_agree}  
	? "That is (almost) all folks."  
```  
`msxbadig.py test.bad -nc -cp -tg g`  
```BlitzBasic  
10 ' {at_last}  
20 print "What?"  
30 if me$="Huh?" then 10 else 50  
40 print:print "Not here."  
50 ' {i_agree}  
60 print "That is (almost) all folks."  
```  
  
**Misc**  
  
- *Long variable summary*  
A summary of all the long name variables used on the code, along with their associated classic short names, can be generated on `REM` lines at the end of the converted code and the amount shown per line can be set. If used without number argument the amount shown per line is `5`.  
`ini: long_var_summary`  `arg: -vs #`  `Default: 5`  
  
- *Running from build system*  
On build systems, like the one in Sublime, errrors and warning messages demand the file name to be on the offending log line. To declutter the log on a run from a console window this information is omitted unless told so.  
`arg: -fb`  `Default: False`  
  
- *Verbose*  
Set increasing leves of feedback given by the program.  
`ini: verbose_level`  `arg: -vb {0,1,2,3}`  `Default: 2`  
`0` show nothing, `1` shows the conversion steps and errors, `2` (default) conversion steps, errors, and warnings  messages and `3` everything so far plus a detailed step by step.  
  
- *Use the `.ini` file*  
Tells if the `.ini` file settings should be used or not, allowing it to be disabled without being moved or deleted.  
`ini: use_ini_file` `Default: True`  
  
- *Write the `.ini` file*  
Rewites the `.ini` file in case its is missing.  
`arg: -ini`  
  
- *Help*  
Help is available using:  
`msxbadig.py -h`  
  
## Technicalities and warnings  
### Yes, they are one and the same  
  
**MSX Basic Dignfied** was made  to run on a Mac OS stock Python installation, version 2.7.10.  
The process of creating **MBD** was basically that I opened Sublime, Google and Terminal with zero Python knowledge and five days latter here we are (plus twoish more days to write this and understand Git (hey, I'm old))  
ps. Well, now there have been a lot more of days and messing since then (still not using fine subtleties like classes and methods).  
