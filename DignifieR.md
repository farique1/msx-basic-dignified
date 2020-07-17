  
# MSX Basic DignifieR  
**v1.2**  
  
**MSX Basic DignifieR** converts Classic MSX Basic to the Dignified format.  
It eases the heavily repetitive and error prone task of removing line numbers, creating branching labels adding spaces between keywords, etc. Helps if you want to convert a lot of files or a long one for editing or just for better visualisation / reading. There are a series of options to configure the appearance of the final Dignified code according to your preferences. .  
  
> The interplay between all the configurable options and the variety of the Basic itself is somewhat complex and was not nearly as tested as it should so keep an eye for and please report any bugs.  
  
## Usage  
### Arguments  
  
You can control the behaviour of **MSX Basic DignifieR**  through command line arguments.  
  
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
- *Convert to lower case*  
Convert all text (excluding: "", DATAs and REMs) to lowercase.  
arg: `-tl` Default: `True`  
  
- *Keep original spaces*  
All spaces are normalized to 1 by default. This will keep any original spaces beyond that.  
arg: `-ks` Default: `False`  
  
- *Convert LOCATE:PRINT*  
Convert `locate x,y:print` to `[?@]x,y `.  
arg: `-cp` Default: `True`  
  
- *Format labels*  
Define how labels are converted.  
`i` Indent non label lines after the first label.  
`s` Add a blank line before each label.  
(there can be more than one letter as argument)  
arg: `-fl [i,s]` Default: `is`  
  
- *Format REMs*  
Define how REMs are converted.  
`l` Remove REMs alone on a line.  
`i` Remove REMs at the end of a line.  
`b` Keep blank REM lines as blank lines.  
`m` Move inline REMs above its original line.  
`k` Add a label if a REM directed by a branching instruction was removed.  
(there can be more than one letter as argument)  
arg: `-fr [l,i,b,m,k]` Default: `m`  
  
- *Unravel THEN/ELSE*  
Break the line on THEN and/or ELSE with a `_` line break.  
`t` Break the line after THEN.  
`n` Break the line before THEN.  
`e` Break the line after ELSE.  
`b` Break the line before ELSE.  
(there can be more than one letter as argument)  
arg: `-ut [t,n,e,b]` Default: `te`  
  
- *Unravel colons*  
Break the line on `:`.  
`w` Break the line and do not indent.  
`i` Break the line indenting after the first `:`.  
`c` Put the `:` on the line below.  
(there can be more than one letter as argument)  
arg: `-uc [i,w,c]` Default: `ic`  
  
- *Repel before keyword*  
A case insensitive regex string with elements which should generate a space before a keyword and them.  
arg: `-rb` Default: `[a-z0-9{}")$]`  
  
- *Repel after keyword*  
A case insensitive regex string with elements which should generate a space after a keyword and them.  
arg: `-ra` Default: `[a-z0-9{}"(]`  
  
- *Join before*  
A case insensitive regex string with elements forcing the removal of spaces before them.  
arg: `-jb` Default: `^(,|:)$`  
  
- *Join after*  
A case insensitive regex string with elements forcing the removal of spaces after them.  
arg: `-ja` Default: `^(,|:)$`  
  
- *Force spaces before*  
A case insensitive regex string with elements that must have a space before them.  
arg: `-sb` Default: `^(:|\+|-|\*|/|\^|\\)$`  
  
- *Force spaces after*  
A case insensitive regex string with elements that must have a space after them.  
arg: `-sa` Default: `^(#|\+|-|\*|/|\^|\\)$`  
  
- *Force together*  
A case insensitive regex string with elements that will be forced together.  
arg: `-ft` Default: `(<=|>=|=<|=>|\)-\()`  
  
**Misc**  
- *Verbose*  
Set the level of feedback given by the program.  
`0` show nothing, `1` errors, `2` errors and warnings, `3` errors, warnings and steps and `4` errors, warnings, steps and details.  
arg: `-vb <#>`  Default: `3`  
