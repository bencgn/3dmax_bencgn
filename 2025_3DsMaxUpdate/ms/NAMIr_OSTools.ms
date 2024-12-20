--https://docs.google.com/document/d/13fe5kJy2HowcKgDHtW8kWAdR0gvVTVNL/edit
--Creator: King Nguyen, NamiCG
--Sep/12/2019
--Last update: Sep/12/2019
try (destroyDialog rOSTools) catch()
rollout rOSTools "Fitin Common Tools" rolledUp:false width:300
(
	button btScrub "Scrub scene"  	width:130  	 	across:2
	button btLayoutExport2Fbx "Layout --> fbx"  	width:130  	 	across:2
	button btLayoutObjectName "Layout: object name?" width:120  	
	button btLayoutMatName "Layout: material name?"  			width:130  	 	across:2
	button btLayoutFixMatName "mat name --> object name"  	width:130  	 	across:2
	button btLayoutSizePosition "Layout: size & position?"  	 	width:130  		across:2
	button btLayoutFixPos "pivot --> [0,0,0]"  						width:130  	 	across:2	
	
	
	local lstErrorObjs = #()
	fn Nami_CheckUnit = 
	(
		local st = ""
		if units.DisplayType != #metric then
			st += "\n - DisplayType: metric?"
		if units.MetricType != #meters then
			st += "\n - MetricType: meters?"
		if units.SystemType != #meters then
			st += "\n - SystemType: meters?"
		if units.SystemScale != 1.0 then
			st += "\n - SystemScale: 1?"
		if st != "" then
			st ="Unity setup: wrong!"+st+"\n"
		else
			st = "Unity setup OK!\n"
	)
	
	fn Nami_ObjectName =
	(
		local st = ""
		for obj in selection do
		(
			if (findString obj.name "__" != undefined) then
			(
				st += " - Error double bar __: "+obj.name+"\n"
				append lstErrorObjs obj				
			)
			if (findString obj.name " " != undefined) then
			(
				st += " - Error spacing: "+obj.name+"\n"
				append lstErrorObjs obj				
			)
		)
		if (st == "") then
			st = "Object name: Done!\n"
		else
			st = "Object name: Fail\n"+st		
		return st
	)
	
	fn Nami_MatName =
	(
		local st = ""
		for obj in selection do
			if obj.mat != undefined then
			(
				if (obj.name != obj.mat.name) then
				(
					st += " - "+obj.name+" --> mat: "+obj.mat.name+"\n"
					appendifUnique lstErrorObjs obj				
				)
			)
			else
			(
				st += " - no material?? "+obj.name+"\n"
				appendifUnique lstErrorObjs obj				
			)
		if (st == "") then
			st = "Material name: Done!\n"
		else
			st = "Material name: Fail\n"+st		
		return st
	)

	
	fn Nami_LayoutMissingObject =
	(
		local st = ""
		local layoutNames = #("_wall_out","_toilet_glass","_toilet_wall","_toilet_floor","_roof","_moulding","_Liv_wall_01","_Liv_wall_02","_Liv_wall_03","_Liv_wall_04","_Liv_floor","_light","_glass","_frame","_ceiling","_bedroom_floor","_balcony_wall","_balcony_floor","_door")
		local layoutRoomNames = #("_bedroom_wall_a_01","_bedroom_wall_a_02","_bedroom_wall_a_03","_bedroom_wall_a_04","_bedroom_wall_b_01","_bedroom_wall_b_02","_bedroom_wall_b_03","_bedroom_wall_b_04","_bedroom_wall_c_01","_bedroom_wall_c_02","_bedroom_wall_c_03","_bedroom_wall_c_04")
		local roomName = ""
		t = selection[1].name
		i = findString t "pn_"
		if i != undefined then
		(
			roomName = tolower (substring t 1 (i+2))
			for i = 1 to layoutNames.count do
				layoutNames[i] = roomName+tolower (layoutNames[i])
			for i = 1 to layoutRoomNames.count do
				layoutRoomNames[i] = roomName+tolower (layoutRoomNames[i])
			for obj in selection do
				if findItem layoutNames obj.name + findItem layoutRoomNames obj.name > 0 then
				(
					st  += " - "+obj.name+"\n"
					append lstErrorObjs obj	
				)
		)
		else
		(
			st = " - "+t+"\n"
			append lstErrorObjs selection[1]
		)
		
		if (st == "") then
			st = "Wrong object name: Done!\n"
		else
			st = "Wrong object name: Fail\n"+st		
		return st		
	)
	
	
	fn Nami_LayoutSizePosition =
	(
		local st = ""
		local mmax = selection.max
		local mmin = selection.min
		if (mmax.x - mmin.x > 3000 or mmax.y - mmin.y > 3000) then
			st +=" - please double-check room width/height\n"
		if (mmax.z > 4000) then
			st +=" - please double-check room height: "+ mmax.z as string +"\n"
		if (mmin.z < -30) then
			st +=" - please double-check room floor depth: "+ mmin.z as string+"\n"
		if (abs ((mmax.x+mmin.x)/2) > 100 or abs ((mmax.y +mmin.y)/2) > 100) then
			st +=" - move room to center\n"
		
		for obj in selection do
		(
			if length  obj.pos > 1.0 then
			(
				st += " - position --> [0,0,0]? "+obj.name+":"+obj.pos as string+"\n"
				appendifUnique lstErrorObjs obj				
			)
			if (findString (tolower obj.name) "_floor" != undefined) then
			(
				if obj.max.z - obj.min.z > 1.0 then
				(
					st += " - floor height ~ 0? "+obj.name+":"+obj.max as string+" -- "+obj.min as string+"\n"
					appendifUnique lstErrorObjs obj				
				)
			)
		)
		if (st == "") then
			st = "Layout Size&Position: Done!\n"
		else
			st = "Layout Size&Position: Fail\n"+st		
		return st
	)	
	
	fn Nami_checkMatName =
	(
		local st = ""
		for obj in selection do
		(
			try
			(
				if obj.name != obj.mat.name then
				(
					if ((substring obj.name 1 7) != (substring obj.mat.name 1 7) ) then
					(
						st += " - Error: "+obj.name +" --> material name "+ obj.mat.name+"\n"
						append lstErrorObjs obj
					)
				)
			)
			catch ()
			--try
			(
				if classof obj.mat == Multimaterial then
				(
					for i=0 to obj.mat.count do
					(
						if obj.mat[i] != undefined then
						(
							if (findstring obj.mat[i].name " " != undefined) then
							(
								st += " - Error: "+obj.name +" --> spacing "+ obj.mat[i].name+"\n"
								append lstErrorObjs obj
							)	
						)
					)
				)
				else
				(
					if obj.mat != undefined then
					(
						if (findstring obj.mat.name " " != undefined) then
						(
							st += " - Error: "+obj.name +" --> spacing "+ obj.mat.name+"\n"
							append lstErrorObjs obj
						)				
					)
				)	
			)
			--catch()
		)
		if (st == "") then
			st = "Material name: Done!\n"
		else
			st = "Material name: Fail\n"+st
		return st
	)
	
	function Nami_checkMultiSub = 
	(
		local st = ""
		for obj in selection do
		(
			local n = 0
			try
			(
				n = obj.mat.count
			) catch ()
			if (n>0) then 
			(
				st += " - Error: "+obj.name +" --> multisub material\n"
				append lstErrorObjs obj
			)
		)
		if (st == "") then
			st = "Multisub material: Done!\n"
		else
			st = "Multisub material: Fail\n"+st
		return st
	)
	
	function Nami_checkPoly4 =
	(
		local st = ""
		local retVal = undefined
		local sel = selection as array
		local sel1 = #()
		for obj in sel do
			if (classOf obj == Editable_Poly) then
				append sel1 obj
		retVal = gePolyFunc.findNGonFaces sel1 4 true ">4"
		
		for obj in selection do
			append lstErrorObjs obj
		select sel
		if (retVal[1] == 0) then 
			st = "Poly>4: Done!\n"
		else
			st = "Poly>4: Fail!\n"+st
		return st
	)
	function Nami_CheckXform =
	(
		local st = ""
		for obj in selection  do	
			if (obj.rotation.x >= 0.001 or obj.rotation.x <= -0.001) then 
			(
				st += obj.name+"\n"
				append lstErrorObjs obj
			)		
		if (st == "") then 
			st = "Rail xfom: Done!\n"
		else
			st = "Rail xfom: Fail!\n"+st
		return st
	)
	
	function isDuplicate lst sname =
	(
		local isDup = false;
		for s in lst do
			if (s  == sname) then 
				isDup = true
		return isDup
	)
	
	function isDuplicateMat lst mat =
	(
		local isDup = false
		local val = undefined
		for s in lst do
			if (tolower s[1].name  == tolower mat.name) then 
			try 
			(
				local f1 = toLower (filenameFromPath s[1].diffuseMap.filename)
				local f2 = toLower (filenameFromPath mat.diffuseMap.filename)
				if (f1 != f2) then 
				(
					isDup = true
					val = s
					--print (s[1].name +": "+f1 +" - " +f2)
				)

			)
			catch
			(
								print s[2]
			)
		return #(isDup,val)
	)
	
	
	function Nami_checkDuplicateObjectName = 
	(
		lstname = #()
		lstdup = #()
		lstdupobj =#()
		local st = ""
		for obj in selection do
		(
				if (isDuplicate lstname (tolower obj.name)) then
				(
					if (isDuplicate lstdup (tolower obj.name)) == false then
						append lstdup (tolower obj.name)
				)
				else
					append lstname (tolower obj.name)
		)
		for s in lstdup do
		(
			for obj in selection do
				if s == (tolower obj.name) then 
				(
					append lstErrorObjs obj
				)
			st += " - Error: "+s+" --> duplicate name\n"
		)
		if (st == "") then
			st = "Duplicate object name: Done!\n"
		else
			st = "Duplicate object name: Fail\n"+st		
		return st
	)	

	fn Nami_checkDummyandName =
	(
		local lstobj = #()
		local lstobj1 = #()
		local st= ""
		for obj in selection do
			if (obj.parent == undefined) then
				append lstobj obj
		if (lstobj.count!=1) then
			st +=" - Error: "+lstobj as string+" scene must have only 1 basic dummy!\n"
		else
		(
			if (length lstobj[1].pos > 0.001) then 
				st +=" - Error: "+lstobj[1].name +" -- > "+lstobj[1].pos as string+" basic dummy must at [0,0,0]!\n"			
			if (classOf lstobj[1] != Dummy) then
				st +=" - Error: scene must have 1 basic dummy!\n"
			else
			(
				for obj in selection do
					if (obj.parent == lstobj[1]) then
						append lstobj1 obj
				if (lstobj1.count != 1) then
					st +=" - Error: scene must have only 1 ref dummy!\n"
				else
				(
					if (classOf lstobj1[1] != Dummy) then
						st +=" - Error: scene must have 1 ref dummy!\n"
					if ((toLower lstobj1[1].name) != ((toLower (substring lstobj[1].name 1 6))+"_ref")) then
						st +=" - Error: wrong ref dummy name\n"
					print (toLower lstobj1[1].name)
					print ((toLower (substring lstobj[1].name 1 6))+"_ref")
					local maindummy = toLower (substring lstobj[1].name 1 6)
					for obj in selection do
						if (maindummy != toLower (substring obj.name 1 6)) then
						(
							st +=" - Error: "+obj.name+" --> wrong object name\n"
							append lstErrorObjs obj
						)
				)
			)
		)
		if (st == "") then
			st = "Dummy and object name: Done!\n"
		else
			st = "Dummy and object name: Fail\n"+st		
		return st
	)
	function collectMat sel = 
	(
		local mats = #()
		local objs = #()
		for obj in sel do
		(
			try
			(
				for m in obj.mat do
					if (findItem mats m == 0) then
					(
						append mats m
						append objs obj
					)
			)
			catch
			(
				if (findItem mats obj.mat == 0) then
				(
					append mats obj.mat
					append objs obj
				)
			)
		)			
		return #(mats,objs)
	)
	local lstMatError = #()
	local lstTexError = #()
	function Nami_checkTexMat = 
	(
		local val = collectMat selection
		local lstTexture =#()
		lstMatError = #()
		lstTexError = #()
		for m in val[1] do
		try
			if (m != undefined) then
			(
				local filename = toLower (filenameFromPath m.diffuseMap.filename)
				if (findItem lstTexture filename == 0) then
				(
					append  lstTexture filename
				)
				else
				(
					if (findItem lstTexError filename == 0) then
					(
						append lstMatError m
						append lstTexError filename
					)
				)
			)
		catch()
		local i = 1
		for m in lstMatError do
		(
			if (i < meditMaterials.count) then
			(
				meditMaterials[i] = m
				i += 1
			)
		)
		if (lstTexError.count > 0) then
			return ("Same texture = same material: Fail\n- Error:"+ lstTexError as string+"\n")		
		else
			return ("Same texture = same material: Done!"+"\n")		
	)
	
	function Nami_checkMissingMap = 
	(
		local val = collectMat selection
		local lstTexture =#()
		lstMatError = #()
		lstTexError = #()

		local val = (collectMat selection)
		local sel = #()
		for i=1 to val[1].count do
		try
		(
			local f = maxfilepath+(filenameFromPath val[1][i].diffuseMap.filename)
			if not (doesFileExist f) then
			(
				append lstMatError val[1][i] 
				append lstTexError f				
				append lstErrorObjs val[2][i]
			)
			
		) catch (
				append lstMatError meditmaterials[1]
				append lstErrorObjs val[2][i]
		)


		local i = 1
		for m in lstMatError do
		(
			if (i < meditMaterials.count) then
			(
				meditMaterials[i] = m
				i += 1
			)
		)
		if (lstTexError.count > 0) then
			return ("Missing map: Fail\n- Error:"+ lstTexError as string+"\n")		
		else
			return ("Missing map: Done!"+"\n")		
	)
	
	function Nami_checkTextureSize = 
	(
		local lstTexture = getFiles (maxfilepath+"*.dds")
		local lstTextureError = ""
		for f in lstTexture do
		try
		(
			bm = openBitmap f
			local cW = (bm.width == 8 or bm.width == 16 or bm.width == 32 or bm.width == 64 or bm.width == 128 or bm.width == 256 or bm.width == 512 or bm.width == 1024 or bm.width == 2048)
			local cH = (bm.height == 8  or 	bm.height == 16 or bm.height == 32 or bm.height == 64 or bm.height == 128 or bm.height == 256 or bm.height == 512 or bm.height == 1024 or bm.height == 2048)
			if (cW and cH ) then
			(
			)
			else
				append lstTextureError (f+ " - wrong dimension: "+bm.width as string+"x"+bm.height as string+"\n")
			close bm
			gc()
		) 
		catch 
		(
			append lstTextureError (f+" error\n")
		)

		if (lstTextureError !="") then
			return ("Wrong texture size: Fail\n"+ lstTextureError as string)		
		else
			return ("Wrong texture size: Done!"+"\n")		
	)	
	
	
	--CHECK TEX SIZE
	fn checkBitmap bm = 
	(
		potW = false
		potH = false
			for i = 0 to 12 do
			(
				if bm.width == Pow 2 i then
				(
					potW = true
					break
				)
			)
			for i = 0 to 12 do
			(
				if bm.height == Pow 2 i then
				(
					potH = true
					break
				)
			)
		if potW == false or potH == false  then
		(
			return 0
		)
		return 1
	)
	
	function Nami_checkTexSize =
	(
		local st = ""
		for mat in sceneMaterials do
		(
			if classof mat == Multimaterial then
			(
				for j=1 to mat.count do
				(
					if classof mat[j] == Standardmaterial then
					(
						if mat[j].diffusemap != undefined then
						(
							local bmpfile = openBitmap mat[j].diffusemap.filename --revise this
							try
							(
								if checkBitmap bmpfile == 0 then
									st += " - Wrong size : "+bmpfile.filename +" --> texture size : "+ bmpfile.width as string + "*" + bmpfile.height as string +"\n" 
							)
							catch
							(
								st += " - Missing file : " + mat[j].diffusemap.filename as string + " --> error\n"
							)
						)
					)
				)
			)
			else if classof mat == Standardmaterial then
			(
				if mat.diffusemap != undefined then
				(
					local bmpfile = openBitmap mat.diffusemap.filename --revise this
					try
					(
						if checkBitmap bmpfile == 0 then
							st += " -Wrong size : "+ bmpfile +" --> texture size : "+ bmpfile.width + "*" + bmpfile.height+"\n" 
					)
					catch
					(
						st += " - Missing file : " + mat.diffusemap.filename + " --> error\n"
					)
				)
			)
		)
		if (st == "") then
			st = "Texture size: Done!\n"
		else
			st = "Texture size: Fail\n"+ st
		return st
	)
	-- check naming convention for object in room
	on btLayoutObjectName pressed do
	(
		max unhide all
		max select all
		lstErrorObjs = #()
		local st = Nami_ObjectName()
		st += Nami_LayoutMissingObject()
		messagebox st
		print st
		max select none
		select (lstErrorObjs as array)
	)
	
	--check material name?
	on btLayoutMatName pressed do
	(
		max unhide all
		max select all
		lstErrorObjs = #()
		local st = Nami_MatName()
		messagebox st
		print st
		max select none
		select (lstErrorObjs as array)
	)
	
	on btLayoutFixMatName pressed do
	(
		for obj in selection do
		(
			if obj.mat == undefined  or classof obj.mat != Standardmaterial then
			(
				local m = Standardmaterial ()
				m.name = obj.name
				m.diffuse = color (random 0 255) (random 0 255) (random 0 255)
				obj.mat = m
			)
			obj.mat.name = obj.name
		)
	)	
	
	on btLayoutFixPos pressed do
	(
		for obj in selection do
			obj.pivot = [0,0,0]
	)
	
	on btLayoutSizePosition pressed do
	(
		max unhide all
		max select all
		lstErrorObjs = #()
		local st = Nami_LayoutSizePosition()
		messagebox st
		print st
		max select none
		select (lstErrorObjs as array)
	)
		
	on btLayoutExport2Fbx pressed do
	(
		local lstRoom = #("_a_","_b_","_c_","_d_","_e_")
		local p = getSavePath caption:"Apartment layout path"
		if p != undefined then
		(
			local listObjs = selection as array 
			for obj in listObjs do
			(
				max select none 
				select obj
				
				foldername = obj.name
				t = substring foldername (foldername.count-4) 3
				if findItem lstRoom t > 0 then
				(
					foldername	= substring foldername 1 (foldername.count-3)
					--print foldername
				)
				else
					if tolower (substring foldername (foldername.count-7) 6) == "_wall_" then
						foldername	= substring foldername 1 (foldername.count-3)
				
				filepath = p + "\\"+foldername
				--print filepath
				makeDir filepath
				filepath += "\\"+obj.name+".fbx"
				exportFile filepath #noPrompt selectedOnly:true using:FBXEXP
			)
		)
	)
	on btScrub pressed do
	(

		max unhide all
		max select all
		lstErrorObjs = #()
		local st = ""
		local st0 = Nami_ObjectName()
		st0 += Nami_LayoutMissingObject()		
		local st1 = Nami_MatName()
		local st2 = Nami_LayoutSizePosition()
		st = st0+st1+st2
		messagebox st
		print st
		max select none
		select (lstErrorObjs as array)	
	)
		
	
)
createDialog rOSTools