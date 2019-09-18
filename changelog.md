
## **v1.2.0**    
>According to the Semantic Versioning it was supposed to be **v2** (somewhat incompatible with the previous version) but no, it is not **v2**.  

- Variables on DEFINES. A [] inside a DEFINE will be substituted for an argument touching the closing bracket.
- - If the variable bracket is not empty, the text inside will be used as default in case no argument is found
- - ex: using `[var] [poke 100,[10]]`, a subsequent `[var]30` will be replaced by `poke 100,30`
- New way of assigning long name variables:
- - A long name now is attached to a short name independently of the variable type, it only need to be declared
- - once and can be used for all types, int, single, double, string and typeless of the same name.
- - The DECLARE command now takes only the base name of the variable, without the type symbol,
- - it also can assign explicit short names in the format AAAA:BB where the AAAA is the long name and BB the short.
- - This will reduce the available names but will be more compatible with the MSX basic conventions
- - and will still give ~700 variables (26*26) not counting the ~300 (letter+number and single letters) not assignable.
- Added support for all types of variables. Int, single, double, string and none.
- Added GitHub link to REM header
- Added True and False statements, converts to -1 and 0. Can use NOT operator to flip or check.
- Added an INCLUDE command to insert and external .bad file into the current code.
- Fixed a bug misinterpreting commas inside the DEFINES
- Fixed a bug potentially causing REM and DATA being mixed with normal instructions and QUOTES mixed with itself.
- Fixed handling of leading line numbers
- Error if duplicated DEFINES are found.
- Error if duplicated line labels are found.
- Warning if variable DECLARED more than once.
- Better handling of DEFINEs and DECLAREs
- Handles error when destination folder is not found.
- Blank lines removed after a  Dignified command (define, declare,...) even when opted to keep blank lines.
- Keep space to prevent ST OR A confusion with S TO AR.
- Minor log output tweak

## **v1.1.0**      
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
