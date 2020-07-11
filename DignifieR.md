# MSX Basic DignifieR  
**v1.1**  
  
**MSX Basic DignifieR** converts Classic MSX Basic to the Dignified format.  
It eases the heavily repetitive and error prone task of removing line numbers, creating branching labels, adding spaces between keywords, etc.  
Helps if you want to convert a lot of files or a long one for editing or just for better visualisation / reading.  
  
There is a series of options to configure the appearance of the final Dignified code according to your preferences.  
  
## Usage  
### Arguments  
  
You can control the behaviour of **MSX Basic DignifieR** through command line arguments.  
  
Run with: `msxbader.py <source> [destination] args...`  
  
**Files**  
- *Source file*  
The Classic code file to be read.  
ini: `source_file = [source]` arg: `<source>`  
  
- *Destination file*  
The Dignified MSX Basic file to be saved.  
ini: `destin_file = [destination]` args: `[destination]`  
  
	If no name is given, the *destination* file will be the *source* with a `.bad` extension.  
	(it will overwrite any file with the same name).  
  
**Format**  
- *Indent toggle*  
Indent all non label lines after the first label.  
arg: `-it` Default: `True`  
  
- *Blank line toggle*  
Insert a blank line before line labels.  
arg: `-lt` Default: `True`  
  
- *LOCATE:PRINT toggle*  
Convert `locate x,y:print` to `[?@]x,y `.  
arg: `-pt` Default: `False`  
  
- *Remove REMs*  
Remove line or inline REMs from the code  
Branching instructions to removed REM lines will be orphaned but a warning will be generated.  
`l` remove line REMs, `i` remove inline REMs.  
arg: `-rr [l,i]` Default: `None`  
  
- *Unravel lines*  
Insert a line break after a `:`.  
`i` with indent, `w` without indent.  
arg: `-ul [i, w]` Default: `None`  
  
- *Unravel THEN*  
Insert a `_` line break after a `THEN` or `ELSE`.  
`t` after THEN, `e` after ELSE, `b` before ELSE.  
arg: `-ut [t,e,b]` Default: `None`  
  
- *Repel before keyword*  
A regex string with elements which should generate a space before a keyword.  
arg: `-rb` Default: `[A-Za-z0-9{}")]`  
  
- *Repel after keyword*  
A regex string with elements which should generate a space after a keyword.  
arg: `-ra` Default: `[A-Za-z0-9{}"(]`  
  
- *Force spaces before*  
A regex string with elements that must have a space before them.  
arg: `-sb` Default: `^(:|\+|-|\*|/|\^|\\)$`  
  
- *Force spaces after*  
A regex with elements that must have a space after them.  
arg: `-sa` Default: `^(\+|-|\*|/|\^|\\)$`  
  
- *Force together*  
A regex with elements that will be forced together.  
arg: `-ft` Default: `^(\+|-|\*|/|\^|\\)$`  
  
**Misc**  
- *Verbose*  
Set the level of feedback given by the program.  
`0` show nothing, `1` errors, `2` errors and warnings, `3` errors, warnings and steps and `4` errors, warnings, steps and details.  
arg: `-vb <#>`  Default: `3`  
