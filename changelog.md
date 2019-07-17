## **v1.1.0**    
>According to the Semantic Versioning it was supposed to be **v2** (slightly incompatible with the previous version) but no, it is not **v2**.  
  
- Various bug fixes, adjustments and optimizations.  
- Reworked the whole code. It is not more pythonic or faster or smaller but it is definitely more versatile albeit a little stricter but also safer and more robust.  
- Change the grouping and order of conversions.  
- Elevated some warnings to errors and made them stop the conversion.  
- Labels will cause an error if not only alphanumeric and _ . They also cannot be only numbers.  
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