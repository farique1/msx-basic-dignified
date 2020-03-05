# MSX Basic Dignified  
  
## **v1.5.0**  
***4-3-2020***  
- Ported to Python 3.8!  
- No more forcing an 8 character file name for output (we are all adults here and understand the limitations of the MSX disk system.)  
- Added **Loop Labels**.  
- Added **Line Toggles**.  
- Added **Rem Blocks** with `''` and `###`.  
- Added `-tr` and `translate=` to **translate unicode special characters** to a MSX ASCII similar.  
- Added `-rh` and `rem_header=` to remove the two info REM header lines on  
- Added the possibility of DEFINEs as a variables to other DEFINEs.  
	- Re coded and streamlined the entire DEFINE replacement routine.  
the converted code.  
- Added linefeed to last line of code to force parsing it.  
- Changed the standing characters for the DATA, REM, QUOTES and LABELS placeholders to way above the usual ASCII range of the old computers to prevent misinterpretation.  
- Changed colon spaces to preserve spacing if keep spacing is used  
- Changed defaults to provide a more compact code.  
	- General spacing default now is 0 spaces.  
	- Label line default is now `2` (no REM labels.).  
	- Strip the GOTOs after THEN/ELSE is now the default.  
- Changed `-fb` to `-frb` to standardize the nomenclature (3 letters are for internal arguments).  
- Integrated colon spacing arguments `-bc`, `-ac`, `nnbr_spaces_bef_colon=` and `nnbr_spaces_aft_colon=` into `-cs` and `colon_spaces=` that takes `b`, `a` and `ba` for *before*, *after* and *before and after*.  
- Integrated label line spacing arguments `-br`, `-ar`, `rem_bef_label` and `rem_aft_label` into `-lg` and `label_gap=` that takes `b`, `a`, `ba` for *before*, *after* and *before and after*.  
- Integrated spacing arguments `-ks` and `keep_original_spaces=` into `-gs` and `general_spaces=` that now takes `0`, `1` and `k` for *no space*, *one space* and *keep original spacing* (there is no more option for more the 1 general space.)  
- Integrated indent arguments `-ci`, `-si`, `keep_indent_space_chars=` and `indent_tab_spaces=` into `-ki` and `keep_indent=` and made it take the number of TAB spaces.  
- Integrated REM format arguments `-lr`, `-rr`, `label_rem_format=` and `regul_rem_format=` into `-nr` and `new_rem_format=` (there is no more distinction between label and regular REMs.)  
- Improved verbose output  
	- Optimised a little.  
	- Standardised the arguments help text.  
	- Added reporting of [?@] arguments on detailed verbose.  
	- Comments after a label without `'` generates a warning.  
	- Undefined DEFINEs demoted to *warning* from *error* (while bug picking `[...]` constructs inside DATA, REM and QUOTES is not fixed.  
	- `-vb 0` now quit silently on errors.  
- Fixed a bug with parentheses on function call variables and improved the underlying code.  
- Fixed a potential small bug with spaces before colon.  
- Fixed small bug converting existing REMs.  
- Fixed potential small bug removing line numbers.  
  
## **v1.4.0**  
***30-1-2020***  
- Added integration with **MXS Basic Tonekizer** and **openMSX Basic (de)Tokenizer** to export tokenized code.  
	- Verbose setting propagate down to tokenizers.  
- Added ability to monitor the Basic program execution on **openMSX** after the conversion.  
	- Will catch error messages, display them on Sublime and tag the offending line.  
- Better integration with **MSX Sublime Tools**' build system.  
- Better `-fb` *(from build)* argument handling.  
- Verbose level redefined to: `0` silent, `1` errors, `2` +warnings, `3` +steps, `4` +details  
- Fixed bug offsetting lines on INCLUDEd code by 1.  
- Fixed a bug with uppercase `true` and `false`.  
- Several log improvements.  
  
## **v1.3.0**  
***15-1-2020***  
- Implemented Proto-functions. Works as normal functions with some limitations. See README for details.  
- Implemented double arithmetic and compound operators `++`, `--`, `+=`, `-=`, `*=`, `/=`, `^=`.  
- Line labels can now have a `'` (not `REM`) after it. Will be preserved on conversion with `-ll 0` and `-ll 1`.  
- Fixed bug preventing the correct replacement of DEFINEs with different variables on the same line.  
- Fixed bug breaking labels with "rem" on the name.  
- Fixed bug where part of instructions and variables were being replaced by shorter variables names contained in them if they shared the same line.  
  
## **v1.2.0**  
***18-9-2019***  
- Variables on DEFINES. A `[]` inside a DEFINE will be substituted for an argument touching the closing bracket.  
	- If the variable bracket is not empty, the text inside will be used as default in case no argument is found  
	- ex: using `[var] [poke 100,[10]]`, a subsequent `[var]30` will be replaced by `poke 100,30`  
- New way of assigning long name variables:  
	- A long name now is attached to a short name independently of the variable type, it only need to be declared  
	- once and can be used for all types, int, single, double, string and typeless of the same name.  
	- The DECLARE command now takes only the base name of the variable, without the type symbol,  
	- it also can assign explicit short names in the format AAAA:BB where the AAAA is the long name and BB the short.  
	- This will reduce the available names but will be more compatible with the MSX Basic conventions  
	- and will still give ~700 variables (26*26) not counting the ~300 (letter+number and single letters) not assignable.  
- Added support for all types of variables. Int, single, double, string and none.  
- Added GitHub link to REM header  
- Added True and False statements, converts to -1 and 0. Can use NOT operator to flip or check.  
- Added an INCLUDE command to insert an external .bad file into the current code.  
- Fixed a bug misinterpreting commas inside the DEFINES  
- Fixed a bug potentially causing REM and DATA being mixed with normal instructions and QUOTES mixed with itself.  
- Fixed handling of leading line numbers  
- Error if duplicated DEFINES are found.  
- Error if duplicated line labels are found.  
- Warning if variable DECLARED more than once.  
- Better handling of DEFINEs and DECLAREs.  
- Handles error when destination folder is not found.  
- Blank lines now removed after a Dignified command (define, declare,...) even when opted to keep blank lines.  
- Keep space to prevent ST OR A confusion with S TO AR.  
- Minor log output tweak  
  
## **v1.1.0**  
***17-7-2019***  
- Various bug fixes, adjustments and optimizations.  
- Reworked the whole code. It is not more pythonic or faster or smaller but it is definitely more versatile albeit a little stricter but also safer and more robust.  
- Change the grouping and order of conversions.  
- Elevated some warnings to errors and made them stop the conversion.  
- Labels will cause an error if not only alphanumeric and _ . They also cannot be only numbers.  
- As invalid labels will stop the conversion, the whole {{}} thing was removed.  
- Multiple defines can be created on a line, separated by commas.  
- `[?@]x,y` MUST now be followed by an empty space.  
- `endif`s not alone on a line and not part of a `label`, `rem`, `data` or `quote` will generate a warning (but will not be removed).  
- By default will now strip spaces around `+-=<>*/^\.,;` but can use `-uo` argument to prevent it.  
- Can now use variables with names bigger than 2 characters (double and strings for now).  
- fixed a potential bug when dealing with `x or` becoming `xor` when removing spaces.  
- New display log system with better errors and warnings handling.  
  
## **v1.0.3**  
- Learned to use the local path.  
- Added TODO comments.  
  
## **v1.0.2**  
- Variable names more Pythonic.  
  
## **v1.0.1**  
- Conformed to PEP-8 (sorta).  
  
## **v1.0**  
- Original release.  
