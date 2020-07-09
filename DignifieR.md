
# MSX Basic DignifieR  
**v1.0**  
  
**MSX Basic DignifieR** converts Classic MSX Basic to the Dignified format.  
It eases the heavily repetitive and error prone task of removing the line numbers and creating the branching labels.  
  
For readability, during the conversion you can opt to insert spaces around instructions, indent all non label lines after the first label and insert a blank line before the labels. ~~You can also convert the `locate x,y:print` construct to the Dignified `[?@]x,y `~~ (temporally removed).  

>Future versions will allow to break `IF` and `FOR` lines along with other improvements.  
  
## Usage  
### Arguments  
  
You can control the behaviour of **MSX Basic DignifieR** by altering the variables on the code or through command line arguments. 
  
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

~~- *Print at toggle*  
Convert `locate x,y:print` to `[?@]x,y `.  
arg: `-pt` Default: `False`~~  
  
For now some changes should be made inside the code, modifying the value of some variables.  

- *Repel character before*  
A regex with characters which should generate a space before a keyword.  
variable: `repelcbef` Default: `[A-Za-z0-9{}")]`  

- *Repel character after*  
A regex with characters which should generate a space after a keyword.  
variable: `repelcaft` Default: `[A-Za-z0-9{}"(]`  

- *Force spaces before*  
A regex with elements that must have a space before them.   
variable: `spacesbef` Default: `^(:|\+|-|\*|/|\^|\\|and|or|not|xor|eqv|imp|mod)$`  

- *Force spaces after*  
A regex with elements that must have a space after them.   
variable: `spacesaft` Default: `^(\+|-|\*|/|\^|\\|and|or|not|xor|eqv|imp|mod)$`  
