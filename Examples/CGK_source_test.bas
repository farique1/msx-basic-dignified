'CHANGE GRAPH KIT
'Find and modify uncompressed art on games
'
'Conversion arguments 
##
## MSX Basic Dignified test code
## Includes several unecessary things just for testing
## Highlight observations for MSX Basic.sublime-syntax

## Define highlight
define [ifa] [if a$ = ]
define [ra] [read a]

screen 0 :color 15,1,1 :width 40 :key off
 defint a-z
   c1=1 :c2=14 :c3=2 :c4=6

## Remove leading numbers
20 print "Pick a Game" :print "without extension"
## Testing ? conversion into PRINT
?:?:?:files "*.bin"
?:?:?:line input "> ";gn$

cls :screen 1 :width 32

## Label highlight (do not highlight if illegal characters found)
{inicializacao}
## and an example of a {{label issues}} highlight
	locate10,11:print "INITIALIZING"
	rem gn$="vestron6"

	open gn$+".bin" as #1 len=1
	field #1,1 as f$
	get#1,3 :a$=f$ :get#1,2 :b$=f$ :gs=(asc(a$)*256+asc(b$))-65536!
	get#1,5 :a$=f$ :get#1,4 :b$=f$ :ge=(asc(a$)*256+asc(b$))-65536!
	gl=ge-gs
	si=&h1 :ms=8 :mr=800 :hs=1
	ps=si :sx=16 :sy=23 :ss=8
	cx=0 :cy=0 :te=0

	gosub {set_color}

	for f=0    to 7    :read a :vpoke 1856+f,a  :next
	for f=0    to 7    :read a :vpoke 1864+f,a  :next
	for f=0    to 7    :read a :vpoke 1872+f,a  :next
	for f=8    to 31   :read a :vpoke f,a       :next
	## Testing defines
	## And defines highlight
	for f=1824 to 1831 :[ra]   :vpoke f,a       :next
	for f=128  to 135  :[ra]   :vpoke f,a       :next
	for f=248  to 255  :[ra]   :vpoke f,a       :next 
	for f=0    to 31   :[ra]   :vpoke 14336+f,a :next

	{search_screen}
		cls
		locate0,0:print "        CHANGE GRAPH KIT        "
		locate1,2:print "XWWWWWWWWWWY"
		locate1,3:print "VÄäîû®≤º∆–⁄V"
		locate1,4:print "VÅãïü©≥Ω«—€V"
		locate1,5:print "VÇåñ†™¥æ»“‹V"
		locate1,6:print "VÉçó°´µø…”›V"
		locate1,7:print "VÑéò¢¨∂¿ ‘ﬁV"
		if hs=1 then locate 4,7:print "FREEZE"
		locate1,8:print "VÖèô£≠∑¡À’ﬂV"
		locate1,9:print "VÜêö§Æ∏¬Ã÷‡V"
		locate1,10:print "Váëõ•Øπ√Õ◊·V"
		locate1,11:print "Vàíú¶∞∫ƒŒÿ‚V"
		locate1,12:print "Vâìùß±ª≈œŸ„V"
		locate1,13:print "ZWWWWWWWWWW["
		locate3,15:print "Srt# End#"
		locate1,17:print "S"
		locate3,17:print string$(4-len(hex$(ps)),"0")+hex$(ps)
		locate8,17:print string$(4-len(hex$(ps+7)),"0")+hex$(ps+7)
		locate1,19:print "R"
		locate3,19:print string$(4-len(hex$(si)),"0")+hex$(si)
		locate8,19:print string$(4-len(hex$(si+799)),"0")+hex$(si+799)
		locate1,21:print "G"
		locate3,21:print string$(4-len(hex$(1)),"0")+hex$(1)
		locate8,21:print string$(4-len(hex$(gl)),"0")+hex$(gl)
		locate13,2:print "XWWWWWWWRWWWWWWWWY"
		locate13,3:print "VMS  8x"+right$(str$(ms),1)+"VEditing V"
		locate13,4:print "VMR  "+right$(str$(mr),3)+"V"+gn$+string$(8-len(gn$)," ")+"V"
		locate13,5:print "ZWWWWWWWQWWWWWWWW["
		locate13,7:print "VÍVMove VPVSave"
		locate13,9:print "VÈVStep VMVSize"
		locate13,11:print "VËVEdit VEVExplode"
		locate13,13:print "VCVTogle Refrehs"
		locate13,15:print "VQVPrev VWVNext"
		locate13,17:print "VZV4x   VXV4x"
		locate13,19:print "VAVSrtVSVMidVDVEnd"
		locate14,21:print "ABBBBBBBBBBBBBBC"
		
		ay=sy+(ss-2) :ax=0
		if sy+(ss-2) > 101 then ax=8 :ay=23+(sy+(ss-2))-103
		if sx+ax > 95 then ay=200
		vpoke 6912,sy  :vpoke 6913,sx
		vpoke 6916,ay  :vpoke 6917,ax+sx
		vpoke 6920,167 :vpoke 6921,126*si/gl+113
		vpoke 6928,167 :vpoke 6929,(126*si/gl)+113+(100800!/gl)

		{read_keyboard_main}
			a$ = inkey$
			## lookup keys
			## Hex notation highlight
			if a$ = chr$(&h1c) and sx+8 < 95 then sx=sx+8 :ps=ps+80	   :gosub {move_scan_sprite}
			if a$ = chr$(&h1d) and sx-8 > 15 then sx=sx-8 :ps=ps-80	   :gosub {move_scan_sprite}
			if a$ = chr$(&h1e) and sy-ms > 22 then sy=sy-ms :ps=ps-ms  :gosub {move_scan_sprite}
			if a$ = chr$(&h1f) and sy+ms < 103 then sy=sy+ms :ps=ps+ms :gosub {move_scan_sprite}

			if a$ = "E"  then goto {explode_screen}

			if a$ = "Q" then dp=ps-si :si=si-mr 	 :gosub {update_memory_position}
			if a$ = "W" then dp=ps-si :si=si+mr 	 :gosub {update_memory_position}
			if a$ = "Z" then dp=ps-si :si=si-mr*4 	 :gosub {update_memory_position}
			if a$ = "X" then dp=ps-si :si=si+mr*4 	 :gosub {update_memory_position}
			if a$ = "A" then dp=ps-si :si=&h1 		 :gosub {update_memory_position}
			if a$ = "D" then dp=ps-si :si=gl-800 	 :gosub {update_memory_position}
			if a$ = "S" then dp=ps-si :si=(gl/2)-400 :gosub {update_memory_position}

			if a$ = "L" then gosub {update_memory_position}
			if a$ = " " then gosub {change_movement_step}
			if a$ = "M" then gosub {change_sprite_size}

			## Testing concatenate line with leadng : (colon)
			if a$ = "P" then _
				:screen 0 :width 40
				:close
				:print gn$+" closed"
				:print :print :print
				:print "ENTER to open another file ";
				:line input a$
				:run
			endif 

			## Testing concatenate line with trailing (:) (colon)
			if a$ = "C" then _
				hs = abs(hs-1):
				if hs = 1 then _
					locate4,7:print "FREEZE" _
				else _
					locate1,7:print "VÑéò¢¨∂¿ ‘ﬁV":
					gosub {update_memory_position}
				endif 
			endif 

			if a$ = chr$(13) and hs = 0 then goto {edit_screen}

			if a$ = "1" then c1=c1-1 :gosub {set_color}
			if a$ = "2" then c1=c1+1 :gosub {set_color}
			if a$ = "3" then c2=c2-1 :gosub {set_color}
			if a$ = "4" then c2=c2+1 :gosub {set_color}
			if a$ = "5" then c3=c3-1 :gosub {set_color}
			if a$ = "6" then c3=c3+1 :gosub {set_color}
			if a$ = "7" then c1=c4-1 :gosub {set_color}   
			if a$ = "8" then c1=c4+1 :gosub {set_color}

		goto {read_keyboard_main}

{set_color}
	c1 = abs(c1 mod 16+16) mod 16: ' use DEF FN
	c2 = abs(c2 mod 16+16) mod 16: ' same1
	c3 = abs(c3 mod 16+16) mod 16: ' same2
	c4 = abs(c4 mod 16+16) mod 16: ' same3

	color c2,c1,c1
	vpoke 8194,c4*16+c1 :vpoke 8195,c4*16+c1
	vpoke 8192,c4*16+c3
	vpoke 6914,0  :vpoke 6918,1  :vpoke 6922,2  :vpoke 6926,3  :vpoke 6930,2 ## remove from here?
	vpoke 6915,c2 :vpoke 6919,c2 :vpoke 6923,c2 :vpoke 6927,c2
	for f=8208 to 8220 :vpoke f,c3*16+c1 : next
return

{move_scan_sprite}
	ay=sy+(ss-2) :ax=0
	if sy+(ss-2) > 101 then ax=8 :ay=23+(sy+(ss-2))-103
	if sx+ax > 95 then ay=200

	vpoke 6912,sy :vpoke 6913,sx
	vpoke 6916,ay :vpoke 6917,sx+ax
	## Testig built in define [?@]
	[?@]3,17string$(4-len(hex$(ps)),"0")+hex$(ps):' use PRINT USING
	[?@]8,17string$(4-len(hex$(ps+(ss-1))),"0")+hex$(ps+(ss-1)):' same
return
return

{change_sprite_size}
	if ss = 8 then ss=32 else ss=8
	
	ay=sy+(ss-2) :ax=0
	if sy+(ss-2) > 101 then ax=8 :ay=23+(sy+(ss-2))-103
	if sx+ax > 95 then ay=200

	vpoke 6916,ay :vpoke 6917,sx+ax

	[?@]3,17 string$(4-len(hex$(ps)),"0")+hex$(ps):' use PRINT USING
	[?@]8,17 string$(4-len(hex$(ps+(ss-1))),"0")+hex$(ps+(ss-1)):' same
return

{update_memory_position}
	if si < &h1 then si=&h1
	if si+800 > gl then si=gl-800
	ps=si+dp

	vpoke 6920,167 :vpoke 6921,126*si/gl+113
	vpoke 6928,167 :vpoke 6929,(126*si/gl)+113+(100800!/gl)

	[?@]3,17 string$(4-len(hex$(ps)),"0")+hex$(ps):' use PRINT USING
	[?@]8,17 string$(4-len(hex$(ps+7)),"0")+hex$(ps+7):' same
	[?@]3,19 string$(4-len(hex$(si)),"0")+hex$(si):' same
	[?@]8,19 string$(4-len(hex$(si+799)),"0")+hex$(si+799):' same

	'for f = si to si+799:
	vpoke 1024-si+f,peek(f) :next

	if hs=0 then _
		locate5,2:print "SCAN":
		for f=si to si+799:
			get #1,f:
			a$=f$:
			vpoke 1024-si+f,asc(a$):
		next:
		locate5,2:print "WWWW"
	endif
return

{change_movement_step}
	if ms=8 then ms=1 else ms=8
	if mr=800 then mr=400 else mr=800

	locate20,3:print right$(str$(ms),1)
	:locate18,4:print right$(str$(mr),3)
return

{edit_screen}
	cls
	vpoke 6920,200 :vpoke 6928,200

	LOCATE0,0:PRINT "        CHANGE GRAPH KIT  [ra]      "
	LOCATE1,2:PRINT"XWWWWWWWWWWY"
	LOCATE1,3:PRINT"VÄäîû®≤º∆–⁄V"
	LOCATE1,4:PRINT"VÅãïü©≥Ω«—€V"
	LOCATE1,5:PRINT"VÇåñ†™¥æ»“‹V"
	LOCATE1,6:PRINT"VÉçó°´µø…”›V"
	LOCATE1,7:PRINT"VÑéò¢¨∂¿ ‘ﬁV"
	LOCATE1,8:PRINT"VÖèô£≠∑¡À’ﬂV"
	LOCATE1,9:PRINT"VÜêö§Æ∏¬Ã÷‡V"
	LOCATE1,10:PRINT"Váëõ•Øπ√Õ◊·V"
	LOCATE1,11:PRINT"Vàíú¶∞∫ƒŒÿ‚V"
	LOCATE1,12:PRINT"Vâìùß±ª≈œŸ„V"
	LOCATE1,13:PRINT"ZWWWWWWWWWW["
	locate3,15:print "Srt# End#"
	locate1,17:print "S"
	locate3,17:print string$(4-len(hex$(ps)),"0")+hex$(ps)
	locate8,17:print string$(4-len(hex$(ps+7)),"0")+hex$(ps+7)
	locate1,19:print "R"
	locate3,19:print string$(4-len(hex$(si)),"0")+hex$(si)
	locate8,19:print string$(4-len(hex$(si+799)),"0")+hex$(si+799)
	locate1,21:print "G"
	locate3,21:print string$(4-len(hex$(1)),"0")+hex$(1)
	locate8,21:print string$(4-len(hex$(gl)),"0")+hex$(gl)
	locate14,2:print "________________"
	locate14,3:print "________________"
	locate14,4:print "________________"
	locate14,5:print "________________"
	locate14,6:print "________________"
	locate14,7:print "________________"
	locate14,8:print "________________"
	locate14,9:print "________________"
	locate14,10:print "________________"
	locate14,11:print "________________"
	locate14,12:print "________________"
	locate14,13:print "________________"
	locate14,14:print "________________"
	locate14,15:print "________________"
	locate14,16:print "________________"
	locate14,17:print "________________"
	LOCATE13,19:PRINT"VÈVTglVCVErzVIVInv"
	LOCATE13,21:PRINT"VOVRldVPVSavVËVBck"

	cx = 0 :cy = 0 :te = 0
	vpoke 6924,15 :vpoke 6925,112

	{fill_edit_area}
		c=-1 :ox=0 :oy=0
		if ss=8 then cl=7 else cl=15
		for i=ps to ps+(ss-1)
			c=c+1
			if te=0 then _
				get #1,i:
				a$=f$:
				p$=bin$(asc(a$)):
				a=len(p$):
				z=8-a:
				c$=string$(z,"0"):
				b$=c$+p$
			endif
			if c>15 then ox=8 :oy=-16
			for f=1 to 8
				if te=0 then _
						if mid$(b$,f,1)="0" then g=16 else g=228
				if te=1 then _
						if vpeek((ox+13+f)+(oy+2+c)*32+6144)=16 then g=228 else g=16
				if te=2 then g=16
				vpoke(ox+13+f)+(oy+2+c)*32+6144,g
			next
		next
		## this will not persirt
		{read_keyboard_edit}
			a$ = inkey$
			rem this will
			## More define test
			[ifa]chr$(&h1c) and cx < cl then cx = cx+1 :gosub {move_cursor}
			[ifa]chr$(&h1d) and cx > 0 then cx = cx-1  :gosub {move_cursor}
			[ifa]chr$(&h1e) and cy > 0 then cy = cy-1  :gosub {move_cursor}
			[ifa]chr$(&h1f) and cy < cl then cy = cy+1 :gosub {move_cursor}

			[ifa]chr$(13) then vpoke 6924,200 :goto {search_screen}

			[ifa]" " then 		gosub {change_bit}
			[ifa]"O" then te = 0 :goto {fill_edit_area}
			[ifa]"I" then te = 1 :goto {fill_edit_area}
			[ifa]"C" then te = 2 :goto {fill_edit_area}
			[ifa]"P" then 		gosub {save_drawing}

		goto {read_keyboard_edit}

{move_cursor}
	vpoke 6924,15+(cy*8)
	:vpoke 6925,112+(cx*8)
return

{change_bit}
	g = vpeek((cx+14)+(cy+2)*32+6144)
	if g = 16 then g = 228 else g = 16
	vpoke(cx+14)+(cy+2)*32+6144,g
return

{save_drawing}
	c=-1 :ox=0 :oy=0
	for i=ps to ps+(ss-1)
		c=c+1
		## Rem syntax carrie thorugh if ending with : (colon)
		## but not if the colon is next line

		'get #1,i :a$ = f$ :p$ = bin$(asc(a$)):
		a = len(p$) :z = 8-a :c$ = string$(z,"0") :b$ = c$+p$

		if c>15 then ox=8 :oy=-16
		b$="" :m=128 :n=0
		for f=1 to 8
			if vpeek ((ox+13+f)+(oy+2+c)*32+6144)=16 _
			  then g$ = "0" else g$ = "1"
			b$=b$+g$
			n=val(g$)*m+n :m=m/2
		next
		a$=chr$(n)
		lset f$=a$ :put #1,i
		vpoke 1024-si+i,n
	next
return

{explode_screen}
	cls
	vpoke 6912,200 :vpoke 6916,200 :vpoke 6920,200 :vpoke 6928,200
	locate0,0:print "        CHANGE GRAPH KIT        "
	locate1,2:print "XWWWWWWWWWWWWWWWWWWWY"
	locate1,3:print "VÄ ä î û ® ≤ º ∆ – ⁄V"
	locate1,4:print "V                   V"
	locate1,5:print "VÅ ã ï ü © ≥ Ω « — €V"
	locate1,6:print "V                   V"
	locate1,7:print "VÇ å ñ † ™ ¥ æ » “ ‹V"
	locate1,8:print "V                   V"
	locate1,9:print "VÉ ç ó ° ´ µ ø … ” ›V"
	locate1,10:print "V                   V"
	locate1,11:print "VÑ é ò ¢ ¨ ∂ ¿   ‘ ﬁV"
	locate1,12:print "V                   V"
	locate1,13:print "VÖ è ô £ ≠ ∑ ¡ À ’ ﬂV"
	locate1,14:print "V                   V"
	locate1,15:print "VÜ ê ö § Æ ∏ ¬ Ã ÷ ‡V"
	locate1,16:print "V                   V"
	locate1,17:print "Vá ë õ • Ø π √ Õ ◊ ·V"
	locate1,18:print "V                   V"
	locate1,19:print "Và í ú ¶ ∞ ∫ ƒ Œ ÿ ‚V"
	locate1,20:print "V                   V"
	locate1,21:print "Vâ ì ù ß ± ª ≈ œ Ÿ „V"
	locate1,22:print "ZWWWWWWWWWWWWWWWWWWW["
	locate23,11:print "VEV Back"
	if inkey$ = "E" then goto {search_screen} else goto {@}
end

{character_shapes}
	## data lines highlight
	data 4,4,36,100,252,96,32,0
	data 0,0,219,154,82,211,0,0
	data 231,195,165,24,24,165,195,231
	data 255,128,128,128,128,128,128,255
	data 255,0,0,0,0,0,0,255
	data 255,1,1,1,1,1,1,255
	data 0,126,126,126,126,126,126,0 
	data 255,129,129,129,129,129,129,255 :print:rem data with : after
	data 255,255,255,255,255,255,255,255 :rem this stay ## this doesn't

{sprite_shapes}
	## data lines highlight with line concatenation
	data 255,129,000,000,000,000,000,000,_ 
		 129,255,000,000,000,000,000,000,_ ## this works but the highlight stops _
		 000,128,128,128,128,128,128,000,_ ## if not using an _ at the end
		 255,129,129,129,129,129,129,255

' Support routines only (not used by the main program)
{test_syntax_and_hashes_removal}
	data 00,00,"00",00 :rem more highlight test
	data 00,00,00,00 :rem this stay ## this don't
	data 00,00,00,## ## keep ## on data
	print "## test" ## keep ## on quotes
	print "however" ## also keep "this" (if "" after ##)

{cria_bloco_de_caracteres}
	c=127
	for x=2 to 11
		for y=3 to 12
			c=c+1:
			locatex,y:print chr$(c)
		next
	next
end

{mapa_de_caracteres}
	for i=0 to 255
		x=i mod 32: y=i\32
		c=i
		if c<32 or c=127 then c=32
		locatex,y:print chr$(c)
		locatex,y+10:print chr$(1)+chr$(c)
	next
end