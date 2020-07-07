# MSX Basic DignifieR  
**v1.0**  
  
**MSX Basic DignifieR** converts Classic MSX Basic to the Dignified format.  
It eases the heavily repetitive and error prone task of removing the line numbers and creating the branching labels.  
  
During the conversion you can opt to indent all non label lines after the first label and insert a blank line before the labels for readability. You can also convert the `locate x,y:print` construct to the Dignified `[?@]x,y `.  
  
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
  
- *Print at toggle*  
Convert `locate x,y:print` to `[?@]x,y `.
arg: `-pt` Default: `False`  
