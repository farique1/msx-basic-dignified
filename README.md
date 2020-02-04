<img src="https://github.com/farique1/msx-basic-dignified/blob/master/Images/GitHub_Badig_Logo-02.png" alt="MSX Basic Dignified" width="290" height="130">  
  
# MSX Basic Dignified  
**v1.4**   (this is probably the last version in Python 2.7 [we can hope])  
  
**MSX Basic Dignified** is a 'dialect' of MSX Basic using modern coding style and standards that can be composed on any text editor and converted to the traditional MSX Basic to be executed.  
  
Dignified Basic can be written **without line numbers**, can be **indented** using TABs or spaces and have **broken lines**, can use variables with **long names**, have macros **defined** and external files **included**, a kind of **function** can be used, as well as **true** and **false** statements, **compound arithmetic** operators and more.  
  
>I felt the need for something like this when I was redoing [**Change Graph Kit**](https://github.com/farique1/Change-Graph-Kit), an MSX program I did back in the day, just to see how much I could improve it. I coded on Sublime and used Excel, REM tags on branching instructions and a lot of patience to add and change line numbers and such, not pretty.  
>Long after the **CGK** episode I discovered [Tabmegx](http://ni.x0.com/msx/tabmegx/) and also found [Inliner](https://giovannireisnunes.wordpress.com/meu-software/inliner/) ([GitHub](https://github.com/plainspooky/inliner)) during research for **MBD**, ([NestorPreTer](https://github.com/Konamiman/NestorPreTer) is yet another similar tool I found later). They were great sources of 'inspiration' but I wanted something even closer to the workflow I had been working on with other languages.  
  
There is a [syntax highlight, theme, build system, snippets and comment setting](https://github.com/farique1/MSX-Sublime-Tools) available for **Sublime Text 3** working with the **MSX Basic** and **MSX Basic Dignified** rules to help improve the overall experience.  
  
![# Versions.jpg](https://github.com/farique1/msx-basic-dignified/blob/master/Images/Versions.jpg)  
  
>Please, be aware that **MBD** and its tools are by no mean finished products and are sort of expected to misbehave.  
  
## The Program  
### Standard behaviour  
  
**MSX Basic Dignigied** reads a text file containing the Dignified code and write back a traditional MSX Basic in ASCII and/or tokenized format.  
The Dignified code uses a `.bad` extension, the ASCII is given `.asc` and the tokenized `.bas`.  
  
> One of the flavours of [**MSX Basic Tokenizer**](https://github.com/farique1/MSX-Basic-Tokenizer) must be installed for tokenized output.  
  
If **MSX Basic Tokenizer** is used, a list file (like the ones on assemblers) can be exported showing some statistics and the correspondence of the tokenized code with the ASCII one. A line from the `.mlt` file would be:  
<pre>
80da: ee80 7800 44 49 ef 50 49 f2 1f 41 31 41 59 26 53 60 00 00        120 DI=PI-3.1415926536  
</pre>  
(more information on the **MSX Basic Tokenizer** page.)  
  
If running from the build system on [**MSX Sublime Tools**](https://github.com/farique1/MSX-Sublime-Tools), the code execution can be monitored on **openMSX**; Basic errors will be catch by **Sublime** and the offending lines will be tagged.  
  
Different from the traditional MSX Basic, instructions, functions and variables must be separated by spaces from alphanumeric characters. The MSX Syntax Highlight will reflect this and there are several settings to conform the spacing when the conversion is made.  
  
**Note:** Special characters do not translate nicely between MSX Basic ASCII and UTF. The best match so far is the  `Western (Windows 1252)` encoding; it will not translate the characters but will preserve the ones typed on the MSX. Saving an ASCII MSX Basic program from an emulator with the special characters needed, opening it on a editor and copying the characters to the Dignified code is so far the best way to use them. (a translation algorithm is in the TODO list when the leap to Python 3 is made.)  
  
### Features and usage  
  
Run with: `msxbadig.py <source> [destination] args...`  
  
>From now on, when showing code, usually the first excerpt is Dignified, followed by the program call and the traditional Basic output.  
  
- Directing the code flow is done with **labels**.  
Labels are created using curly brackets `{like_this}` and can be used alone on a line to receive the code flow or on a branching (jump) instruction to direct the flow to the corresponding line label. They can only have letters, numbers and underscore and they cannot be only numbers. `{@}` points to its own line (abraço, Giovanni!).  
Labels marking a section are called line labels and labels on jump instructions  (`GOTO`, `GOSUB`, etc) are called branching labels.  
A comment can be used after a line label using a `'` (`REM` is not supported) and it will stay after the conversion as an addition to the label or alone in the line, depending on the label conversion argument used.  
Labels not following the naming convention, duplicated line labels or branching to inexistent line labels will generate an error and stop the conversion. Labels with illegal characters are higlighted when using the MSX Syntax Highlight.  
  
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
Duplicated **defines** will give an error and stop the conversion.  
A `[]` inside a **define** content will be substituted for an argument touching the closing bracket. If the variable bracket is not empty the text inside will be used as default in case no argument is found.  
For instance, using `DEFINE [var] [poke 100,[10]]`, a subsequent `[var]30` will be replaced by `poke 100,30`; `[var]` alone will be replaced by `poke 100,10`.  
Variables passed to **defines**  must be followed by an space, indicating the end of the variable content. A **define** that takes a variable but was not given one must also be followed by an space after the closing bracket, indicating no variable is given.  
  > **Defines** cannot be used as variables for other **defines** (for now).  
  
	`[?@]x,y ` is a built in **define** that becomes `LOCATEx,y:PRINT`, it must be followed by an empty space.  
	```BlitzBasic  
	define [ifa] [if a$ = ], [pause] [a$=inkey$ :if a$<>[" "] goto {@}]  
	[ifa]"2" then print "dois"  
	[ifa]"4" then print "quatro"  
	[?@]10,10 "dez"  
	[pause]chr$(13)  
	```  
	`msxbadig.py test.bad`  
	```BlitzBasic  
	10 IF A$="2" THEN PRINT "dois"  
	20 IF A$="4" THEN PRINT "quatro"  
	30 LOCATE 10,10:PRINT "dez"  
	40 A$=INKEY$:IF A$<>CHR$(13) GOTO 40  
	```  
  
- **Long name variables** can be used on the Dignified code. They can only have letters, numbers and underscore and cannot be only numbers or have less than 3 characters. As is the case with the instructions, they must be separated by empty spaces from other alphanumeric characters or commands (the non alpha characters `~`, `$`, `%`, `!`, `#` on the variables can touch other commands).  
When converted they are replaced by an associated standard two letter variables. They are assigned on a descending order from `ZZ` to `AA` and single letters and letter+number are never used. Each long name is assigned to a short name independent of type, so if `variable1`  becomes `XX` so will `variable1$` become `XX$`  
To use these variables they must be declared, there are two ways to do that:  
  -- On a `declare` line, separated by commas: `declare variable1, variable2, variable3`.  
  -- In place, preceded by an `~`: `~long_var = 3`.  
An explicit assignment between a long and a short name can be forced by using  a `:` when declaring a variable (only on a `declare` command): `declare variable:va` will assign `VA` to `variable`. Forcing declaration of the same variable to different short names will cause an error.  
As variables are assigned independent of type, explicit type character (`$%!#`) cannot be used on a `declare` line.  
When a long name variable is declared with an `~` or on a `declare` line, a new two letter variable is assigned to it, redeclaring the variable will maintain the previous assignment. A warning will be given for repeated `~` declarations. Variables declared on `declare` lines have precedence over `~` declarations.  
After it is assigned, a long name variable can be used without the `~` but a long named variable without the `~` that has not been previously declared will be understood as a loose text and not be converted, will not even generate any erros or warnings.  
Reserved MSX Basic commands should not be used as variables names.  
Traditional one and two letters variables can be used normally alongside long names ones, just be aware that the letters at the end of the alphabet are being used up and they may clash with the hard coded ones.  
The conversion will try to catch illegal variables when declared but is not always perfect so keep an eye on them.  
The MSX Syntax Highlight will show illegal variables on `declare` lines or when assigned with `~`.  
A summary of the long and short name associations can be generated on `REM`s at the end of the converted code.  
  
	```BlitzBasic  
	declare food, drink:dk  
	if food$ = "cake" and drink = 3 then _  
		~result$ = "belly full":  
		~sleep = 10  
	endif  
	```  
	`msxbadig.py test.bad`  
	```BlitzBasic  
	10 IF ZZ$="cake" AND DK=3 THEN ZY$="belly full":ZX=10  
	```  
	Optional, with  `msxbadig.py test.bad -vs`  
	```BlitzBasic  
	20 ' ZZ-food, ZY-result, ZX-sleep, DK-drink  
	```  
  
- **Proto-functions** can be used to emulate the use of modern function definition and calls.  
They are defined with `func .functionName(arg1, arg2, etc)` and must end with a `return` alone on a line.  
The arguments can have default values as in `func .function(arg$="teste")` and the `return` can have return variables like `return ret1, ret2, etc`. The `return` and can also have a `:` before it or at the end of the line above to join them on the conversion.  
The functions are called with `.functionName(arg1, arg2, etc)` and can be assigned to variables like `ret1, ret2 = .functionName(args)`. They can be separated by `:` as usual and can also come after a `THEN` or `ELSE`: `if a=1 then .doStuff() else .dontDoStuff()`.  
The number of arguments and return variables must be the same and explicitly given except for an argument with a default value, in this case the default will be used if a empty space is passed on that position. To use a function call with empty argument positions and preserve the variable value, the default must be the variable name, eg: `func .applyColor(color1=color1, color2=color2)` can be called with `.applyColor(10,)`, `.applyColor(,20)` or even `.applyColor(,)`.  
**Proto-functions** with return variables cannot have conditional returns (only the first `return` alone on a line will be parsed for variables and will signal the end of the function definition) but the conditional value can be established a priori in a variable with an `IF THEN ELSE` and then passed on the `return`.  
Obviously there are no local variables on the MSX Basic (which can limit the usefulness of the proto-functions) but this can be simulated by using unique named variables inside the functions. They can also be useful to apply the result to different variables at different points in the code.  
When converting to traditional Basic, function definitions are essentially **labels** so they cannot have the same name as one of them. A function call is a `gosub` to that label with the variables assigned before and after it accordingly.  
If the arguments or return variable are the same between function calls or definitions they will not be equated on the conversion to avoid unnecessary repetition like `A$=A$`. The same way, an empty argument location with a default variable equated to itself will not be converted.  
Different from a normal function, `func` definitions will not deviate the code flow from itself so they must be placed at a point unreachable by the normal code flow.  
Everything on the same line as the function definition will be converted to a comment. `##` comments will be ignored as usual.  
Upon conversion, function definitions and calls will follow the **label** configurations.  
	> Some known limitations:  
	> **Proto-function** definitions and calls cannot have the `_` line separator inside them.  
	> Function recursion (called inside itself) is not recommended.  
	> Text with the format of function calls (`.xxx()`) inside `REM`, `DATA` or `""` WILL be converted as function calls.  
	> There must be an empty line after a `return` if it is the last line of the code.  
  
	```BlitzBasic  
	ch$ = .getUpper("a")  
	print ch$  
	end  
	func .getUpper(up$)  
		ch = asc(up$) - 32  
	return chr$(ch)  
	```  
	`msxbadig.py test.bad`  
	```BlitzBasic  
	10 UP$="a":GOSUB 40:CH$=CHR$(CH)  
	20 PRINT CH$  
	30 END  
	40 ' {getUpper}  
	50 CH=ASC(UP$)-32  
	60 RETURN  
	```  
  
- A single traditional MSX Basic line can  span several lines on Dignified code using `:` or `_` breaks. They are then **joined** when converting to form a single line.  
Colons `:` can be used at the end of a line (joining the next one) or the beginning of a line (joining the previous one) and are retained when joined. Their function is the same as on the traditional MSX Basic, separating different instructions.  
Underscores `_` can only be used at the end of a line and they are deleted when the line is joined. They are useful to join broken instructions like `IF THEN ELSE`, long quotes or anything that must form a single command on the converted code.  
`endif`s can be used (not obligatory, just Python it) but are for cosmetical or organisational purpose only. They must be alone on their lines and are removed upon conversion without any validation regarding to their `IF`s. If they are not alone and are not part of a `DATA`, `REM` or `QUOTE` they will generate a warning but will not be deleted. `endif`s that are part of any of the previous commands but are alone on a line due to a line break will be deleted.  
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
  
- The Dignified code can use exclusive **comments** `##` that are stripped during the conversion.  
Regular `REM`s are kept. A tenacious bug (called My Own Regex Incompetency) prevents the `##` from being removed if there are any `"` after it.  
  
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
  
- An external piece of Dignified code can be inserted anywhere using the **include** command.  
`include "code.bad"` will insert the contents of `code.bad` exactly where the `include` was and can even have its lines joined with the main code by using `:` or `_` on any of the files.  
  
	```BlitzBasic  
	print "This is the main file."  
	'  
	include "help.bad"  
	'  
	print "This is the main file again."  
	```  
	`msxbadig.py test.bad`  
	```BlitzBasic  
	10 PRINT "This is the main file."  
	20 '  
	30 PRINT "This is a helper code."  
	40 PRINT "Saved on another file."  
	50 '  
	60 PRINT "This is the main file again."  
	```  
  
- **True** and **false** statements can be used with numeric variables, they will be converted to `-1` and `0` respectively and their variables can be treated as true booleans on `if`s and with `not` operators.  
  
	```BlitzBasic  
	~variable = true  
	~condition = false  
	if condition then variable = not variable  
	```  
	`msxbadig.py test.bad`  
	```BlitzBasic  
	10 ZZ=-1  
	20 ZY=0  
	30 IF ZY THEN ZZ=NOT ZZ  
	```  
  
- **Shorthand and compound** arithmetic operators (`++`, `--`, `+=`, `-=`, `*=`, `/=`, `^=`) can be used and will be converted to normal MSX Basic operations.  
If the **unpack operator** (`-uo`) argument is used, the conversion will try to preserve the spaces used with the operators.  
  
	```BlitzBasic  
	PX++ :PY --  
	LO+=20 :DI -= 10  
	```  
	`msxbadig.py test.bad -uo`  
	```BlitzBasic  
	10 PX=PX+1:PY = PY - 1  
	20 LO=LO+20:DI = DI - 10  
	```  
  
  
### Configurable arguments  
  
Arguments can be passed on the code itself, on `MSXBadig.ini` or through the command line with each method having a priority higher than the one before.  
  
**Files**  
- *Source file*  
The Dignified code file to be read.  
ini: `source_file = [source]` arg: `<source>`  
  
- *Destination file*  
The traditional MSX Basic code file to be saved.  
ini: `destin_file = [destination]` args: `[destination]`  
  
	If no name is given the destination file will be the first 8 characters from the source with a `.bas` or `.asc` extension accordingly.  
  
- *Tokenize Tool*  
	The tokenizer to use: **MSX Basic Tokenizer** (**MBT**) or **openMSX Basic (de)Tokenizer** (**oMBdT**).  
 ini: `tokenize_tool = [b,o]` arg:  `-tt <b,o>` Default: `b`  
 `b` will call **MBT** and `o` will call **oMBdT**.  
  
- *Output Format (tonekized format is only available if **MBT** or **oMBdT** are present)*  
The format of the converted output.  
ini: `output_format = [t,a,b]` arg: `-of <t,a,b>` Default: `b`  
Both formats are exported by default (`b`). A single format can be forced by using `a` (ASCII) or `t` (tokenized).  
	>The ASCII format is always exported, it will only be deleted if the tokenized is successfully saved.  
  
- *Export List (only available if **MBT** is present, do not work with **oMBdT**)*  
	Saves an `.mlt` list file similar to the ones exported by assemblers with the tokens alongside the ASCII code and some statistics.  
 ini: `export_list = [0-32]` arg:  `-el [0-32]` Default: `16`  
  
	The `[0-32]` argument refer to the number of bytes shown on the list after the line number.  
	The max value is `32`. If no number is given the default of `16` will be used. If `0` is given the list will not be exported.  
  
- ***MSX Basic Tokenizer** Path*  
The path to the **MBT** installation.  
ini: `batoken_filepath = []`  
  
- ***openMSX Basic (de)Tokenizer** Path*  
The path to the **oMBdT** installation.  
ini: `openbatoken_filepath = []`  
  
**Numbering**  
- *Starting line number*  
The number of the first line.  
ini: `line_start = [#]` arg: `-ls [#]` Default: `10`  
  
- *Line step value*  
The line number increment amount.  
ini: `line_step = [#]` arg: `-lp [#]` Default: `10`  
  
- *Add leading zeros*  
Line numbers can be padded with zeroes, this helps to review the converted code on an editor.  
ini: `leading_zeros = [true,false]` arg: `-lz` Default: `false`  
  
```BlitzBasic  
{do_stuff}  
	print "Say something"  
	do$ = "Do something"  
goto {do_stuff}  
```  
###  
`msxbadig.py test.bad -ls 5 -lp 5`  
```BlitzBasic  
5 ' {do_stuff}  
10 PRINT "Say something"  
15 DO$="Do something"  
20 GOTO 5  
```  
###  
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
ini: `handle_label_lines = [0,1,2]` arg: `-ll <0,1,2>` Default: `0`  
  
	By default (option `0`) line labels are left on the code on a `REM` line for reference.  
Their names can be removed, leaving only a blank `REM` on its place (option `1`)  as an anchor or separator.  
On both the above cases the corresponding branching labels are replaced with the line number of the `REM` line where the label is.  
They can also be stripped altogether (option `2`), leaving a smaller, more concise code. In this case the code flow is directed to the line mediately after where the label was.  
  
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
ini: `show_branches_labels = [true,false]` arg: `-sl` Default: `false`  
  
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
Blank lines after Dignified commands (define, declare,...) are always removed.  
Extra lines can also be added close to labels for clarity and organization.  
  
- *Keep blank lines*  
Do not erase blank lines on the converted code, convert them to `rem`s.  
ini: `keep_blank_lines = [true,false]` arg: `-bl` Default: `false`  
  
- Add line before a label  
Add a blank line **before** a label. (has no effect if the line labels were removed)  
ini: `rem_bef_label = [true,false]` arg: `-br` Default: `false`  
  
- Add line after a label  
Add a blank line **after** a label. (has no effect if the line labels were removed)  
ini: `rem_aft_label = [true,false]` arg: `-ar` Default: `false`  
  
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
Add a number of spaces **before** the instruction separating character `:` on multi instruction lines.  
ini: `nnbr_spaces_bef_colon = [#]` arg: `-bc <#>` Default: `0`  
  
- *Number of spaces after `:`*  
Add a number of spaces **after** the instruction separating character `:` on multi instruction lines.  
ini: `nnbr_spaces_aft_colon = [#]` arg: `-ac <#>` Default: `0`  
  
- *Amount of general spacing*  
The conversion automatically strips all blanks (**spaces** and **TAB**s) from the code leaving only 1 space throughout. This amount can be changed with:  
ini: `nmbr_spaces_general = [#]` arg: `-gs [#]` Default: `1`  
  
- *Unpack operators*  
All spaces surrounding mathematical operators and punctuation (`+-=<>*/^\.,;`) are stripped by default. They can be kept as general spaces by using:  
ini: `unpack_operators = [true,false]` arg: `-uo` Default: `false`  
  
- *Keep original spaces*  
Maintains the original spacing used on the source code (**TAB**s and **spaces**).  
ini: `keep_original_spaces = [true,false]` arg: `-ks` Default: `false`  
  
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
**MBD**, by default, also strips all indentation used on the Dignified code. This can be mitigated and refined in three ways.  
  
- *Keep indentation*  
Maintain the original **TAB** indentations by converting them to **spaces** (2 by default).  
ini: `keep_indent = [true,false]` arg: `-ki`  Default: `false`  
  
- *Number of spaces per **TAB** on indentation*  
Change the default amount of **spaces** per **TAB**.  
ini: `indent_tab_spaces = [#]` arg: `-si <#>`  Default: `2`  
  
- *Keep space characters on indents*  
If **spaces** are being used to indent the code, this will keep them.  
ini: `keep_indent_space_chars = [true,false]` arg: `-ci`  Default: `false`  
  
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
ini: `label_rem_format = [s,rem]`  arg: `-lr <s,rem>`  Default: `s`  
  
- *Regular `REM` format*  
Some **non label** `REM`s are also created sometimes by **MBD**; they are also applied as `'` (option `s`) but they can be told to use the regular form (option `rem`) :  
ini: `regul_rem_format = [s,rem]`  arg: `-rr <s,rem>`  Default: `s`  
  
- *Convert all `REM`s*  
All **pre existing** `REM`s (not added by **MBD**) can be changed to maintain coherence along the converted code. The conversion will conform to the two conditions above.  
ini: `convert_rem_formats = [true,false]`  arg: `-cr`  Default: `false`  
  
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
ini: `capitalize_all = [true,false]`  arg: `-nc`  Default: `true`  
  
- *Convert `?` to `PRINT`*  
`?` as `PRINT` are left alone on the conversion, they can be told to become `PRINT` with:  
ini: `convert_interr_to_print = [true,false]`  arg: `-cp`  Default: `false`  
  
- *Strip adjacent `THEN`/`ELSE` or `GOTO`s*  
MSX Basic doesn't need both `THEN` or `ELSE` and `GOTO` if they are adjacent. The converted code can be told to strip the `THEN`/`ELSE` (option `t`), `GOTO` (option `g`) or they can all, as default, be left alone (option `k`)  
ini: `strip_then_goto = [t,g,k]`  arg: `-tg <t,g,k>`  Default: `k`  
  
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
A summary of all the long name variables used on the code along with their associated classic short names can be generated on `REM` lines at the end of the converted code and the amount shown per line can be set. If used without number argument the amount shown per line is `5`.  
ini: `long_var_summary = [#]`  arg: `-vs [#]`  Default: `5`  
  
- *Verbose*  
Set the level of feedback given by the program.  
ini: `verbose_level = [#]`  arg: `-vb <#>`  Default: `3`  
`0` show nothing, `1` errors, `2` errors and warnings, `3` errors, warnings and steps and `4` errors, warnings, steps and details.  
  
- *Running from build system*  
On build systems, like the one in Sublime, errrors and warning messages demand the file name to be on the offending log line. To declutter the log on a run from a console window this information is omitted unless told so.  
arg: `-fb`  Default: `false`  
  
- *Monitor Execution (only works with `-fb`)*  
If running from the build system on **MSX Sublime Tools** this will trigger the monitoring of the code execution on **openMSX**.  
ini: `monitor_execution = [true,false]` arg: `-exe`  Default: `false`  
  
- *Use the `.ini` file*  
Tells if the `.ini` file settings should be used or not, allowing it to be disabled without being moved or deleted.  
ini: `use_ini_file = [true,false]` Default: `true`  
  
- *Write the `.ini` file*  
Rewites the `.ini` file in case its is missing.  
arg: `-ini` Default: `false`  
  
- *Help*  
Help is available using:  
`msxbadig.py -h`  
  
## Technicalities and warnings  
### Yes, they are one and the same  
  
**MSX Basic Dignfied** was made  to run on a Mac OS stock Python installation, version 2.7.10.  
The process of creating **MBD** was basically that I opened Sublime, Google and Terminal with zero Python knowledge and five days latter here we are (plus twoish more days to write this and understand Git (hey, I'm old))  
ps. Well, now there have been a lot more of days and messing since then (still not using fine subtleties like classes and methods).  
