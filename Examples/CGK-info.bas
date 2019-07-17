10 ' Refactored with MSX Basic Dignified
20 ' CHANGE GRAPH KIT
30 ' v1.2.5
40 ' Bug fixes
50 ' Edit uncompressed graphics on MSX binary files on disk
60 ' Copyright (1984 - 2019) - Fred Rique (farique)
70 ' https://github.com/farique1/Change-Graph-Kit
80 '
90 SCREEN 0 :COLOR 15,1,1 :WIDTH 40 :KEY OFF
100 DEFINT A-Z
110 DEF FN ZZ(X) = ABS(X MOD 16 + 16) MOD 16
120 ZY = 1 :ZX = 15 :ZW = 2 :ZV = 6
130 ZU = 0 :ZT = 0 :ZS = 0 :ZR = 0
140 ZW$ = "" ' leave blank to enable file request
150 IF ZW$ <> "" THEN GOTO 230 :' {inicializacao}
160 LOCATE 12,8 :PRINT "Insert game disk"
170 LOCATE 11,10 :PRINT "and press any key."
180 A$ = INKEY$ :IF A$ = "" GOTO 180 :' {SELF}
190 CLS
200 PRINT "Pick a Game" :PRINT "without extension"
210 PRINT :PRINT :PRINT :FILES "*.bin"
220 PRINT :PRINT :PRINT :LINE INPUT "> "; ZW$
230 ' {inicializacao}
240 '
250 CLS :SCREEN 1 :WIDTH 32
260 VPOKE 6914,0 :VPOKE 6918,1 :VPOKE 6922,2 :VPOKE 6926,3 :VPOKE 6930,2 'Assign sprites
270 LOCATE 10,11 :PRINT "INITIALIZING"
280 OPEN ZW$ + ".bin" AS #1 LEN = 1
290 FIELD #1,1 AS ZZ$
300 GET #1,3 :ZY$ = ZZ$ :GET #1,2 :ZX$ = ZZ$ :ZQ = (ASC(ZY$) * 256 + ASC(ZX$)) - 65536!
310 GET #1,5 :ZY$ = ZZ$ :GET #1,4 :ZX$ = ZZ$ :ZP = (ASC(ZY$) * 256 + ASC(ZX$)) - 65536!
320 ZE = ZP - ZQ
330 ZD = &H1 :ZC = 8 :ZB = 800 :ZU = 1
340 ZA = ZD :YZ = 16 :YY = 23 :YX = 8
350 GOSUB 1390 :' {set_color}
360 FOR F = 0 TO 7 :READ A :VPOKE 1856 + F,A :NEXT
370 FOR F = 0 TO 7 :READ A :VPOKE 1864 + F,A :NEXT
380 FOR F = 0 TO 7 :READ A :VPOKE 1872 + F,A :NEXT
390 FOR F = 0 TO 23 :READ A :VPOKE 8 + F,A :NEXT
400 FOR F = 0 TO 7 :READ A :VPOKE 1824 + F,A :NEXT
410 FOR F = 0 TO 7 :READ A :VPOKE 128 + F,A :NEXT
420 FOR F = 0 TO 7 :READ A :VPOKE 248 + F,A :NEXT
430 FOR F = 0 TO 31 :READ A :VPOKE 14336 + F,A :NEXT
440 ' {search_screen}
450 '
460 CLS
470 LOCATE 0,0 :PRINT "        CHANGE GRAPH KIT        "
480 LOCATE 1,2 :PRINT "XWWWWWWWWWWY"
490 LOCATE 1,3 :PRINT "VÄäîû®≤º∆–⁄V"
500 LOCATE 1,4 :PRINT "VÅãïü©≥Ω«—€V"
510 LOCATE 1,5 :PRINT "VÇåñ†™¥æ»“‹V"
520 LOCATE 1,6 :PRINT "VÉçó°´µø…”›V"
530 LOCATE 1,7 :PRINT "VÑéò¢¨∂¿ ‘ﬁV"
540 LOCATE 1,8 :PRINT "VÖèô£≠∑¡À’ﬂV"
550 LOCATE 1,9 :PRINT "VÜêö§Æ∏¬Ã÷‡V"
560 LOCATE 1,10 :PRINT "Váëõ•Øπ√Õ◊·V"
570 LOCATE 1,11 :PRINT "Vàíú¶∞∫ƒŒÿ‚V"
580 LOCATE 1,12 :PRINT "Vâìùß±ª≈œŸ„V"
590 LOCATE 1,13 :PRINT "ZWWWWWWWWWW["
600 LOCATE 3,15 :PRINT "Srt# End#"
610 LOCATE 1,17 :PRINT "C"
620 LOCATE 3,17 :PRINT STRING$(4-LEN(HEX$(ZA)),"0")+HEX$(ZA)
630 LOCATE 8,17 :PRINT STRING$(4-LEN(HEX$(ZA + ( YX - 1))),"0")+HEX$(ZA + ( YX - 1))
640 LOCATE 1,19 :PRINT "R"
650 LOCATE 3,19 :PRINT STRING$(4-LEN(HEX$(ZD)),"0")+HEX$(ZD)
660 LOCATE 8,19 :PRINT STRING$(4-LEN(HEX$(ZD + 799)),"0")+HEX$(ZD + 799)
670 LOCATE 1,21 :PRINT "G"
680 LOCATE 3,21 :PRINT STRING$(4-LEN(HEX$(1)),"0")+HEX$(1)
690 LOCATE 8,21 :PRINT STRING$(4-LEN(HEX$(ZE)),"0")+HEX$(ZE)
700 LOCATE 13,2 :PRINT "XWWWWWWWRWWWWWWWWY"
710 ' Cm = Cursor Movement   Rm = Region Movement
720 LOCATE 13,3 :PRINT "VCm #  "+RIGHT$(STR$(ZC),1)+"VEditing V"
730 LOCATE 13,4 :PRINT "VRm #"+RIGHT$(HEX$(ZB),3)+"V"+ZW$+STRING$(8-LEN(ZW$)," ")+"V"
740 LOCATE 13,5 :PRINT "ZWWWWWWWQWWWWWWWW["
750 ' {keys_page_start}
760 '
770 ON ZR GOTO 850 :' {keys_page_2}
780 LOCATE 13,7 :PRINT "VÍVMove VPVSave   "
790 LOCATE 13,9 :PRINT "VÈVStep VDVSize   "
800 LOCATE 13,11 :PRINT "VËVEdit VRVRefresh"
810 LOCATE 13,13 :PRINT "VFVFreeze/Unfreeze"
820 LOCATE 13,15 :PRINT "VEVExplode/Ovrview"
830 LOCATE 13,17 :PRINT "                  "
840 GOTO 930 :' {keys_page_end}
850 ' {keys_page_2}
860 '
870 LOCATE 13,7 :PRINT "VNVNew            "
880 LOCATE 13,9 :PRINT "VQVPrev VWVNext   "
890 LOCATE 13,11 :PRINT "VAVP 4x VSVN 4x   "
900 LOCATE 13,13 :PRINT "VZVSrtVXVMidVCVEnd"
910 LOCATE 13,15 :PRINT "V1-8VChange Colors"
920 LOCATE 13,17 :PRINT "                  "
930 ' {keys_page_end}
940 '
950 LOCATE 13,19 :PRINT "      VVVMore Keys" ' VHVHelp
960 LOCATE 13,21 :PRINT "ABBBBBBBBBBBBBBBBC"
970 GOSUB 1910 :REM if haltScan=1 then locate 2,2:print "WWFREEZEWW" :' {end_scan}
980 IF ZT = 1 THEN LOCATE 2,13 :PRINT "WOverviewW"
990 YW = YY + (YX - 2) :YV = 0
1000 IF YY + (YX - 2) > 101 THEN YV = 8 :YW = 23 + (YY + (YX - 2)) - 103
1010 IF YZ + YV > 95 THEN YW = 200
1020 VPOKE 6912,YY - 1 :VPOKE 6913,YZ
1030 VPOKE 6916,YW + 1 :VPOKE 6917,YV + YZ
1040 VPOKE 6920,167 :VPOKE 6921,142 * ZD / ZE + 105
1050 VPOKE 6928,167 :VPOKE 6929,(142 * ZD / ZE) + 105 + (100800! / ZE)
1060 IF ZS = 1 THEN ZS = 0 :GOSUB 1720 :' {update_memory_position}
1070 ' {read_keyboard_main}
1080 '
1090 A$ = INKEY$
1100 IF A$ = "1" THEN ZY = ZY - 1 :GOSUB 1390 :' {set_color}
1110 IF A$ = "2" THEN ZY = ZY + 1 :GOSUB 1390 :' {set_color}
1120 IF A$ = "3" THEN ZX = ZX - 1 :GOSUB 1390 :' {set_color}
1130 IF A$ = "4" THEN ZX = ZX + 1 :GOSUB 1390 :' {set_color}
1140 IF A$ = "5" THEN ZW = ZW - 1 :GOSUB 1390 :' {set_color}
1150 IF A$ = "6" THEN ZW = ZW + 1 :GOSUB 1390 :' {set_color}
1160 IF A$ = "7" THEN ZV = ZV - 1 :GOSUB 1390 :' {set_color}
1170 IF A$ = "8" THEN ZV = ZV + 1 :GOSUB 1390 :' {set_color}
1180 IF A$ = CHR$(&H1C) AND YZ + 8 < 95 THEN YZ = YZ + 8 :ZA = ZA + 80 :GOSUB 1510 :' {move_scan_sprite}
1190 IF A$ = CHR$(&H1D) AND YZ - 8 > 15 THEN YZ = YZ - 8 :ZA = ZA - 80 :GOSUB 1510 :' {move_scan_sprite}
1200 IF A$ = CHR$(&H1E) AND YY - ZC > 22 THEN YY = YY - ZC :ZA = ZA - ZC :GOSUB 1510 :' {move_scan_sprite}
1210 IF A$ = CHR$(&H1F) AND YY + ZC < 103 THEN YY = YY + ZC :ZA = ZA + ZC :GOSUB 1510 :' {move_scan_sprite}
1220 IF A$ = "P" THEN SCREEN 0 :WIDTH 40 :CLOSE :PRINT ZW$ + " closed" :PRINT :PRINT :PRINT :PRINT "ENTER to open another file "; :LINE INPUT A$ :RUN
1230 IF A$ = " " THEN GOSUB 1960 :' {change_movement_step}
1240 IF A$ = "D" THEN GOSUB 1620 :' {change_sprite_size}
1250 IF A$ = CHR$(13) THEN GOTO 2020 :' {edit_screen}
1260 IF A$ = "E" THEN GOTO 3080 :' {explode_screen}
1270 IF A$ = "R" THEN ZO = 0 :GOSUB 1850 :' {scan}
1280 IF A$ = "F" THEN ZO = 0 :ZU = ABS(ZU - 1) :IF ZU = 1 THEN GOSUB 1910 :ELSE :GOSUB 1850 :' {end_scan} {scan}
1290 IF A$ = "Q" THEN ZO = ZA - ZD :ZD = ZD - ZB :GOSUB 1720 :' {update_memory_position}
1300 IF A$ = "W" THEN ZO = ZA - ZD :ZD = ZD + ZB :GOSUB 1720 :' {update_memory_position}
1310 IF A$ = "A" THEN ZO = ZA - ZD :ZD = ZD - ZB * 4 :GOSUB 1720 :' {update_memory_position}
1320 IF A$ = "S" THEN ZO = ZA - ZD :ZD = ZD + ZB * 4 :GOSUB 1720 :' {update_memory_position}
1330 IF A$ = "Z" THEN ZO = ZA - ZD :ZD = &H1 :GOSUB 1720 :' {update_memory_position}
1340 IF A$ = "X" THEN ZO = ZA - ZD :ZD = (ZE / 2) - 400 :GOSUB 1720 :' {update_memory_position}
1350 IF A$ = "C" THEN ZO = ZA - ZD :ZD = ZE - 800 :GOSUB 1720 :' {update_memory_position}
1360 IF A$ = "N" THEN RUN
1370 IF A$ = "V" THEN ZR = ABS(ZR - 1) :GOTO 750 :' {keys_page_start}
1380 GOTO 1070 :' {read_keyboard_main}
1390 ' {set_color}
1400 '
1410 ZY = FN ZZ(ZY)
1420 ZX = FN ZZ(ZX)
1430 ZW = FN ZZ(ZW)
1440 ZV = FN ZZ(ZV)
1450 COLOR ZX,ZY,ZY
1460 VPOKE 8194,ZV * 16 + ZY :VPOKE 8195,ZV * 16 + ZY 'Borders character color, blocks of 8 chars
1470 VPOKE 8192,ZV * 16 + ZW 'Region character colors, blocks of 8 chars
1480 VPOKE 6915,ZX :VPOKE 6919,ZX :VPOKE 6923,ZX :VPOKE 6927,ZX :VPOKE 6931,ZX 'Sprite color
1490 FOR F = 8208 TO 8220 :VPOKE F,ZW * 16 + ZY :NEXT 'Scan area character colors, blocks of 8 chars
1500 RETURN
1510 ' {move_scan_sprite}
1520 '
1530 YW = YY + ( YX - 2) :YV = 0
1540 IF YY + ( YX - 2) > 101 THEN YV = 8 :YW = 23 + (YY + ( YX - 2)) - 103
1550 IF YZ + YV > 95 THEN YW = 200
1560 VPOKE 6912,YY - 1 :VPOKE 6913,YZ
1570 VPOKE 6916,YW + 1 :VPOKE 6917,YZ + YV
1580 LOCATE 3,17 :PRINT STRING$(4 - LEN(HEX$(ZA)),"0")+HEX$(ZA)
1590 LOCATE 8,17 :PRINT STRING$(4 - LEN(HEX$(ZA + ( YX - 1))),"0")+HEX$(ZA + ( YX - 1))
1600 RETURN
1610 RETURN
1620 ' {change_sprite_size}
1630 '
1640 IF YX = 8 THEN YX = 32 ELSE YX = 8
1650 YW = YY + (YX - 2) :YV = 0
1660 IF YY + (YX - 2) > 101 THEN YV = 8 :YW = 23 + (YY + (YX - 2)) - 103
1670 IF YZ + YV > 95 THEN YW = 200
1680 VPOKE 6916,YW + 1 :VPOKE 6917,YZ + YV
1690 LOCATE 3,17 :PRINT STRING$(4-LEN(HEX$(ZA)),"0")+HEX$(ZA)
1700 LOCATE 8,17 :PRINT STRING$(4-LEN(HEX$(ZA + ( YX - 1))),"0")+HEX$(ZA + ( YX - 1))
1710 RETURN
1720 ' {update_memory_position}
1730 '
1740 IF ZD < &H1 THEN ZD = &H1
1750 IF ZD + 800 > ZE THEN ZD = ZE - 800
1760 ZA = ZD + ZO
1770 VPOKE 6920,167 :VPOKE 6921,142 * ZD / ZE + 105
1780 VPOKE 6928,167 :VPOKE 6929,(142 * ZD / ZE) + 105 + (100800! / ZE)
1790 LOCATE 3,17 :PRINT STRING$(4 - LEN(HEX$(ZA)),"0")+HEX$(ZA)
1800 LOCATE 8,17 :PRINT STRING$(4 - LEN(HEX$(ZA + 7)),"0")+HEX$(ZA + 7)
1810 LOCATE 3,19 :PRINT STRING$(4 - LEN(HEX$(ZD)),"0")+HEX$(ZD)
1820 LOCATE 8,19 :PRINT STRING$(4 - LEN(HEX$(ZD + 799)),"0")+HEX$(ZD + 799)
1830 IF ZU = 0 THEN 1850 :' {scan}
1840 RETURN
1850 ' {scan}
1860 '
1870 ZT = 0
1880 LOCATE 2,2 :PRINT "WWWSCANWWW"
1890 LOCATE 2,13 :PRINT "WVÈVStopWW"
1900 FOR F = ZD TO ZD + 799 :VPOKE 1024 - ZD + F,0 :GET #1,F :A$ = ZZ$ :VPOKE 1024 - ZD + F,ASC(A$) :IF INKEY$=" " THEN 1910 ELSE NEXT :' {end_scan}
1910 ' {end_scan}
1920 '
1930 IF ZU = 1 THEN LOCATE 2,2 :PRINT "WWFREEZEWW" ELSE LOCATE 2,2 :PRINT "WWWWWWWWWW"
1940 LOCATE 2,13 :PRINT "WWWWWWWWWW"
1950 RETURN
1960 ' {change_movement_step}
1970 '
1980 IF ZC = 8 THEN ZC = 1 ELSE ZC = 8
1990 IF ZB = 800 THEN ZB = 400 ELSE ZB = 800
2000 LOCATE 20,3 :PRINT RIGHT$(HEX$(ZC),1) :LOCATE 18,4 :PRINT RIGHT$(HEX$(ZB),3)
2010 RETURN
2020 ' {edit_screen}
2030 '
2040 CLS
2050 VPOKE 6920,200 :VPOKE 6928,200
2060 LOCATE 0,0 :PRINT "        CHANGE GRAPH KIT        "
2070 LOCATE 1,2 :PRINT "XWWWWWWWWWWY"
2080 LOCATE 1,3 :PRINT "VÄäîû®≤º∆–⁄V"
2090 LOCATE 1,4 :PRINT "VÅãïü©≥Ω«—€V"
2100 LOCATE 1,5 :PRINT "VÇåñ†™¥æ»“‹V"
2110 LOCATE 1,6 :PRINT "VÉçó°´µø…”›V"
2120 LOCATE 1,7 :PRINT "VÑéò¢¨∂¿ ‘ﬁV"
2130 LOCATE 1,8 :PRINT "VÖèô£≠∑¡À’ﬂV"
2140 LOCATE 1,9 :PRINT "VÜêö§Æ∏¬Ã÷‡V"
2150 LOCATE 1,10 :PRINT "Váëõ•Øπ√Õ◊·V"
2160 LOCATE 1,11 :PRINT "Vàíú¶∞∫ƒŒÿ‚V"
2170 LOCATE 1,12 :PRINT "Vâìùß±ª≈œŸ„V"
2180 LOCATE 1,13 :PRINT "ZWWWWWWWWWW["
2190 LOCATE 3,15 :PRINT "Srt# End#"
2200 LOCATE 1,17 :PRINT "C"
2210 LOCATE 3,17 :PRINT STRING$(4-LEN(HEX$(ZA)),"0")+HEX$(ZA)
2220 LOCATE 8,17 :PRINT STRING$(4-LEN(HEX$(ZA + ( YX - 1))),"0")+HEX$(ZA + ( YX - 1))
2230 LOCATE 1,19 :PRINT "R"
2240 LOCATE 3,19 :PRINT STRING$(4-LEN(HEX$(ZD)),"0")+HEX$(ZD)
2250 LOCATE 8,19 :PRINT STRING$(4-LEN(HEX$(ZD + 799)),"0")+HEX$(ZD + 799)
2260 LOCATE 1,21 :PRINT "G"
2270 LOCATE 3,21 :PRINT STRING$(4-LEN(HEX$(1)),"0")+HEX$(1)
2280 LOCATE 8,21 :PRINT STRING$(4-LEN(HEX$(ZE)),"0")+HEX$(ZE)
2290 LOCATE 14,2 :PRINT "________________"
2300 LOCATE 14,3 :PRINT "________________"
2310 LOCATE 14,4 :PRINT "________________"
2320 LOCATE 14,5 :PRINT "________________"
2330 LOCATE 14,6 :PRINT "________________"
2340 LOCATE 14,7 :PRINT "________________"
2350 LOCATE 14,8 :PRINT "________________"
2360 LOCATE 14,9 :PRINT "________________"
2370 LOCATE 14,10 :PRINT "________________"
2380 LOCATE 14,11 :PRINT "________________"
2390 LOCATE 14,12 :PRINT "________________"
2400 LOCATE 14,13 :PRINT "________________"
2410 LOCATE 14,14 :PRINT "________________"
2420 LOCATE 14,15 :PRINT "________________"
2430 LOCATE 14,16 :PRINT "________________"
2440 LOCATE 14,17 :PRINT "________________"
2450 LOCATE 13,19 :PRINT "VEVErzVRVRldVTVInv"
2460 LOCATE 13,21 :PRINT "VÈVTglVPVSavVËVBck"
2470 VPOKE 6924,15 :VPOKE 6925,112
2480 YU = 0 :YT = 0 :YS = 0
2490 ' {fill_edit_area}
2500 '
2510 YR = -1 :YQ = 0 :YP = 0
2520 IF YX = 8 THEN ZN = 7 ELSE ZN = 15
2530 ZM = ZA + (YX - 1) 'find formula to cap at gameLength to avoid next if
2540 IF ZM > ZE - 1 THEN ZM = ZE - 1
2550 FOR I = ZA TO ZM
2560 YR = YR + 1
2570 IF YS = 0 THEN GET #1,I :A$ = ZZ$ :ZV$ = STRING$(8-LEN(BIN$(ASC(A$))),"0") + BIN$(ASC(A$)) :VPOKE 1024 - ZD + I,ASC(A$)
2580 IF YR > 15 THEN YQ = 8 :YP = -16
2590 FOR F = 1 TO 8
2600 IF YS = 2 THEN ZL = 16
2610 IF YS = 0 THEN IF MID$(ZV$,F,1) = "0" THEN ZL = 16 ELSE ZL = 228
2620 IF YS = 1 THEN IF VPEEK ((YQ + 13 + F) + (YP + 2 + YR) * 32 + 6144) = 16 THEN ZL = 228 ELSE ZL = 16
2630 VPOKE (YQ + 13 + F) + (YP + 2 + YR) * 32 + 6144,ZL
2640 NEXT
2650 NEXT
2660 ' {read_keyboard_edit}
2670 '
2680 A$ = INKEY$
2690 IF A$ = CHR$(&H1C) AND YU < ZN THEN YU = YU + 1 :GOSUB 2800 :' {move_cursor}
2700 IF A$ = CHR$(&H1D) AND YU > 0 THEN YU = YU - 1 :GOSUB 2800 :' {move_cursor}
2710 IF A$ = CHR$(&H1E) AND YT > 0 THEN YT = YT - 1 :GOSUB 2800 :' {move_cursor}
2720 IF A$ = CHR$(&H1F) AND YT < ZN THEN YT = YT + 1 :GOSUB 2800 :' {move_cursor}
2730 IF A$ = "E" THEN YS = 2 :GOTO 2490 :' {fill_edit_area}
2740 IF A$ = "R" THEN YS = 0 :GOTO 2490 :' {fill_edit_area}
2750 IF A$ = "T" THEN YS = 1 :GOTO 2490 :' {fill_edit_area}
2760 IF A$ = " " THEN GOSUB 2840 :' {change_bit}
2770 IF A$ = "P" THEN GOSUB 2900 :' {save_drawing}
2780 IF A$ = CHR$(13) THEN VPOKE 6924,200 :GOTO 440 :' {search_screen}
2790 GOTO 2660 :' {read_keyboard_edit}
2800 ' {move_cursor}
2810 '
2820 VPOKE 6924,15 + (YT * 8) :VPOKE 6925,112 + (YU * 8)
2830 RETURN
2840 ' {change_bit}
2850 '
2860 ZL = VPEEK ((YU + 14) + (YT + 2) * 32 + 6144)
2870 ZL = (228 + 16) - ZL
2880 VPOKE (YU + 14) + (YT + 2) * 32 + 6144,ZL
2890 RETURN
2900 ' {save_drawing}
2910 '
2920 YR = -1 :YQ = 0 :YP = 0
2930 ZM = ZA + (YX - 1) 'find formula to cap at gameLength to avoid next if
2940 IF ZM > ZE - 1 THEN ZM = ZE - 1
2950 FOR I = ZA TO ZM
2960 YR = YR + 1
2970 IF YR > 15 THEN YQ = 8 :YP = -16
2980 YO = 128 :YN = 0
2990 FOR F = 1 TO 8
3000 IF VPEEK ((YQ + 13 + F) + (YP + 2 + YR) * 32 + 6144) = 16 THEN G$ = "0" ELSE G$ = "1"
3010 YN = VAL(G$) * YO + YN :YO = YO / 2
3020 NEXT
3030 A$ = CHR$(YN)
3040 LSET ZZ$ = A$ :PUT #1,I
3050 VPOKE 1024 - ZD + I,YN
3060 NEXT
3070 RETURN
3080 ' {explode_screen}
3090 '
3100 CLS
3110 LOCATE 0,0 :PRINT "        CHANGE GRAPH KIT        "
3120 LOCATE 1,2 :PRINT "XWWWWWWWWWWWWWWWWWWWY"
3130 LOCATE 1,3 :PRINT "VÄ ä î û ® ≤ º ∆ – ⁄V"
3140 LOCATE 1,4 :PRINT "V                   V"
3150 LOCATE 1,5 :PRINT "VÅ ã ï ü © ≥ Ω « — €V"
3160 LOCATE 1,6 :PRINT "V                   V"
3170 LOCATE 1,7 :PRINT "VÇ å ñ † ™ ¥ æ » “ ‹V"
3180 LOCATE 1,8 :PRINT "V                   V"
3190 LOCATE 1,9 :PRINT "VÉ ç ó ° ´ µ ø … ” ›V"
3200 LOCATE 1,10 :PRINT "V                   V"
3210 LOCATE 1,11 :PRINT "VÑ é ò ¢ ¨ ∂ ¿   ‘ ﬁV"
3220 LOCATE 1,12 :PRINT "V                   V"
3230 LOCATE 1,13 :PRINT "VÖ è ô £ ≠ ∑ ¡ À ’ ﬂV"
3240 LOCATE 1,14 :PRINT "V                   V"
3250 LOCATE 1,15 :PRINT "VÜ ê ö § Æ ∏ ¬ Ã ÷ ‡V"
3260 LOCATE 1,16 :PRINT "V                   V"
3270 LOCATE 1,17 :PRINT "Vá ë õ • Ø π √ Õ ◊ ·V"
3280 LOCATE 1,18 :PRINT "V                   V"
3290 LOCATE 1,19 :PRINT "Và í ú ¶ ∞ ∫ ƒ Œ ÿ ‚V"
3300 LOCATE 1,20 :PRINT "V                   V"
3310 LOCATE 1,21 :PRINT "Vâ ì ù ß ± ª ≈ œ Ÿ „V"
3320 LOCATE 1,22 :PRINT "ZWWWWWWWWWWWWWWWWWWW["
3330 LOCATE 23,03 :PRINT "VOV Ovrw"
3340 LOCATE 23,21 :PRINT "VEV Back"
3350 VPOKE 6912,200 :VPOKE 6916,200
3360 VPOKE 6920,200 :VPOKE 6928,200
3370 IF ZT = 1 THEN GOSUB 3750 :' {end_overview}
3380 ' {move_overview_sprite}
3390 '
3400 IF ZT = 0 THEN 3460 :' {explode_keys}
3410 VPOKE 6912,(ZJ + 1) * 16 + 6 :VPOKE 6913,(ZK + 1) * 16
3420 VPOKE 6916,(ZJ + 1) * 16 + 14 :VPOKE 6917,(ZK + 1) * 16
3430 ZF = (ZJ * ZH) + (ZK * (ZH * 10))
3440 LOCATE 27,13 :PRINT STRING$(4 - LEN(HEX$(ZF)),"0") + HEX$(ZF)
3450 LOCATE 27,15 :PRINT STRING$(4 - LEN(HEX$(ZF + 799)),"0") + HEX$(ZF + 799)
3460 ' {explode_keys}
3470 '
3480 A$=INKEY$
3490 IF A$ = "O" THEN GOSUB 3570 :' {overview}
3500 IF A$ = CHR$(&H1C) AND ZK < 9 THEN ZK = ZK + 1 :GOSUB 3380 :' {move_overview_sprite}
3510 IF A$ = CHR$(&H1D) AND ZK > 0 THEN ZK = ZK - 1 :GOSUB 3380 :' {move_overview_sprite}
3520 IF A$ = CHR$(&H1F) AND ZJ < 9 THEN ZJ = ZJ + 1 :GOSUB 3380 :' {move_overview_sprite}
3530 IF A$ = CHR$(&H1E) AND ZJ > 0 THEN ZJ = ZJ - 1 :GOSUB 3380 :' {move_overview_sprite}
3540 IF A$ = CHR$(13) AND ZT = 1 THEN ZD = (ZJ * ZH) + (ZK * (ZH * 10)) :ZS = 1 :ZA = ZD :YZ = 16 :YY = 23 :IF ZD + 799 > ZE THEN ZD = ZE - 799 :YZ = 16 :YY = 23 :ZA = ZD :GOTO 440 ELSE GOTO 440 :' {search_screen} {search_screen}
3550 IF A$ = "E" THEN GOTO 440 :' {search_screen}
3560 GOTO 3460 :' {explode_keys}
3570 ' {overview}
3580 '
3590 ZI = 0
3600 ZT = 1
3610 ZH = (ZE / 100)
3620 ZG = (9 * ZH) + (9 * (ZH * 10)) + 8
3630 LOCATE 2,2 :PRINT "WWWWWWWSCANWWWWWWWW"
3640 LOCATE 2,22 :PRINT "WWWWWVÈVStopWWWWWWW"
3650 FOR F = 1 TO ZG STEP ZH
3660 FOR I = F TO F + 7
3670 VPOKE 1024 + ZI,0
3680 GET #1,I
3690 A$ = ZZ$
3700 VPOKE 1024 + ZI,ASC(A$)
3710 IF INKEY$ = " " THEN 3750 :' {end_overview}
3720 ZI = ZI + 1
3730 NEXT
3740 NEXT
3750 ' {end_overview}
3760 '
3770 VPOKE 6912,(ZJ + 1) * 16 + 6 :VPOKE 6913,(ZK + 1) * 16
3780 VPOKE 6916,(ZJ + 1) * 16 + 14 :VPOKE 6917,(ZK + 1) * 16
3790 LOCATE 23,05 :PRINT "VÍV Move"
3800 LOCATE 23,07 :PRINT "VËV Go"
3810 LOCATE 23,11 :PRINT "Region"
3820 ZF = (ZJ * ZH) + (ZK * (ZH * 10))
3830 LOCATE 23,13 :PRINT "St# " + STRING$(4-LEN(HEX$(ZF)),"0")+HEX$(ZF)
3840 LOCATE 23,15 :PRINT "Ed# " + STRING$(4-LEN(HEX$(ZF + 799)),"0")+HEX$(ZF + 799)
3850 LOCATE 02,2 :PRINT "WWWWWWWWWWWWWWWWWWW"
3860 LOCATE 2,22 :PRINT "WWWWWWWWWWWWWWWWWWW"
3870 RETURN
3880 END
3890 ' {character_shapes}
3900 '
3910 DATA 4,4,36,100,252,96,32,0
3920 DATA 0,0,219,154,82,211,0,0
3930 DATA 231,195,165,24,24,165,195,231
3940 DATA 255,128,128,128,128,128,128,255
3950 DATA 255,0,0,0,0,0,0,255
3960 DATA 255,1,1,1,1,1,1,255
3970 DATA 0,126,126,126,126,126,126,0
3980 DATA 255,129,129,129,129,129,129,255
3990 DATA 255,255,255,255,255,255,255,255
4000 ' {sprite_shapes}
4010 '
4020 DATA 255,129,0,0,0,0,0,0
4030 DATA 129,255,0,0,0,0,0,0
4040 DATA 0,128,128,128,128,128,128,0
4050 DATA 255,129,129,129,129,129,129,255
4060 ' {functions_not_used}
4070 '
4080 ' {create_character_block}
4090 '
4100 C=127
4110 FOR X=2 TO 11
4120 FOR Y=3 TO 12
4130 C=C+1 :LOCATE X,Y :PRINT :PRINT CHR$(C)
4140 NEXT
4150 NEXT
4160 END
4170 ' {character_map}
4180 '
4190 FOR I=0 TO 255
4200 X=I MOD 32 :Y=I\32
4210 C=I
4220 IF C<32 OR C=127 THEN C=32
4230 LOCATE X,Y :PRINT CHR$(C)
4240 LOCATE X,Y+10 :PRINT CHR$(1)+CHR$(C)
4250 NEXT
4260 END
4270 ' ZZ$-bytes$, ZZ-colorBase, ZY$-lowByte$, ZY-color1, ZX$-highByte$
4280 ' ZX-color2, ZW$-gameName$, ZW-color3, ZV$-bitFull$, ZV-color4
4290 ' ZU-haltScan, ZT-isOverview, ZS-goOverview, ZR-keysPage, ZQ-gameStart
4300 ' ZP-gameEnd, ZO-cursorDisplace, ZN-areaSize, ZM-finalPos, ZL-pixel
4310 ' ZK-ovrwX, ZJ-ovrwY, ZI-bytePos, ZH-sliceSize, ZG-lastSlice
4320 ' ZF-ovrwRegion, ZE-gameLength, ZD-regionStart, ZC-spriteStep, ZB-regionStep
4330 ' ZA-cursorPos, YZ-cursorX, YY-cursorY, YX-cursorSize, YW-adjustY
4340 ' YV-adjustX, YU-editX, YT-editY, YS-editType, YR-position
4350 ' YQ-gridX, YP-gridY, YO-bitPos, YN-byteDecimal
