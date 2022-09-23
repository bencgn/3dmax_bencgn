--Creator: King Nguyen, NamiCG, StudioWA Vietnam, GlassEgg Digital Media
--Created: Oct/01/2006
--Last update:Jun/05/2013
--GuardRail Tools
---------------------------------------------------------------
try ( destroyDialog NAMIr_GuardrailsEx ) catch()

rollout NAMIr_GuardrailsEx "GuardrailsEx" rolledUp:false width:240
(



--interpCurve3D <SplShape> <Spl_index> <param_float> [pathParam:<boolean>]
--Returns a <point3> coordinate on the indexed curve. If pathParam:false, param is the fraction of the Spl length, 
--otherwise it is a segment-based (path) fraction. Default is pathParam:false
--tangentCurve3D <SplShape> <Spl_index> <param_float> [pathParam:<boolean>]
--Returns a <point3> tangent on the indexed curve. If pathParam:false, param is the fraction of the Spl length, 
--otherwise it is a segment-based (path) fraction. Default is pathParam:false

		listbox blstObj "Objects" height:4
		button bAddObj "Add" across:2
		button bRemoveObj "Remove" across:2
		listbox blstSpl "Splines" height:2
		button bAddSpl "Add" across:2
		button bRemoveSpl "Remove" across:2

		checkbox cbScale "random scale"  across:1 checked:true
		spinner spScale1 "Min scale" range:[0.0,10.0,1.0] type:#float  across:2
		spinner spScale2 "Max scale" range:[0.0,10.0,1.2] type:#float across:2

		button btSlide "Slide" width:120 

		local lstObj = #()
		local lstSpl = #()
		local objDir = #()
		global gnlstObj = #()


		on cbScale changed e do
		(
			spScale1.enabled = e
			spScale2.enabled = e
		)
			
		on bAddObj pressed do
		(
			for obj in selection do
				if classOf obj == Editable_Poly then	
				(
					lst = blstObj.items
					append lstObj obj
					append lst obj.name
					blstObj.items = lst
				)
		)

		on bRemoveObj pressed do
		(
			if blstObj.selection>0 then
			(
				lst = blstObj.items
				deleteItem lstObj blstObj.selection
				deleteItem lst blstObj.selection
				blstObj.items = lst
			)

		)

		on bAddSpl pressed do
		(
			lst = blstSpl.items
			for obj in selection do
				if (classOf obj == Line) or (classOf obj == SplineShape) then	
					if (findItem lstSpl obj) == 0 then
					(
						append lstSpl obj
						append lst obj.name
					)
			blstSpl.items = lst
		)

		on bRemoveSpl pressed do
		(
			if blstSpl.selection>0 then
			(
				lst = blstSpl.items
				deleteItem lstSpl blstSpl.selection
				deleteItem lst blstSpl.selection
				blstSpl.items = lst
			)

		)

		
	on btSlide pressed do
		if (lstObj.count>0) and (lstSpl.count>0) then
		(
			local gnlstObj = #()
			for iii = 1 to lstSpl.count do
				for ii = 1 to (numSplines lstSpl[iii]) do
				(
					local startparam = 0
					local endparam = 1
					local startlength = 0
					local endlength = 0
					segLength = getSegLengths lstSpl[iii] ii cum:true
					local splinelength = segLength[segLength.count]
					totallength = splinelength
					endlength = totallength
					local knot = getKnotSelection lstSpl[iii] ii
					local nKnot = numKnots lstSpl[iii] ii
					if (knot.count >= 1) then
					(
						if (knot[1] != 1) then
						(
							startparam = segLength[knot[1]-1]
							startlength = segLength[nKnot-1 +knot[1]-1]
						)
						if (knot.count > 1) then
						(
							endparam = segLength[knot[knot.count]-1]
							endlength = segLength[nKnot-1+knot[knot.count]-1]
						)
					)
					local dparam = endparam-startparam
					totallength = endlength - startlength
					print ("Total: " +totallength as string)
					print ("Start: "+startparam as string+" - "+startlength as string)
					print ("End: "+endparam as string+" - "+endlength as string)

					gnlstObj = #()
					local obj
					local objLength
					undo on
					(
						param = (startlength)/splinelength
						local i = 0
						while param<=1 do
						(
							i+=1 
							obj = lstObj[random 1 lstObj.count]
							--objLength = lstObj[1].max.x-lstObj[1].min.x
							objLength = lstObj[1].max.x-lstObj[1].pos.x
							
								
							--maxOps.cloneNodes obj cloneType:#instance newNodes:&nnl
							local nnl
							maxOps.cloneNodes obj cloneType:#instance newNodes:&nnl #nodialog
							append gnlstObj nnl[1]
							s = random spScale1.value spScale2.value
							if cbScale.checked then
								nnl[1].scale = [1,1,1]*s
							--append gnlstObj (copy obj)
							--gnlstObj[n].scale.x *=pscale 
							if param <= 1 then
							(
								exactPos = interpCurve3D lstSpl[iii] ii param
								gnlstObj[i].pos = exactPos
							)
							if cbScale.checked then
								param += objLength*s/splinelength
							else
								param += objLength/splinelength
								
						)
						for i = 1 to gnlstObj.count do
						(
				
							local objDir = (gnlstObj[i].rotation as matrix3)[1]
							if i<gnlstObj.count then
								newDir = normalize (gnlstObj[i+1].pos-gnlstObj[i].pos)
							else
								newDir = normalize (interpCurve3D lstSpl[iii] ii 1-gnlstObj[i].pos)
							
							rot_axis = normalize (cross objDir newDir)
							rot_angle = - acos((dot objDir newDir)/(length objDir)/(length newDir))
							newquat = quat rot_angle rot_axis
							eulerangle = (quatToEuler newquat order:1)
							--if not bRoll.checked then eulerangle.x = 0
							rotate gnlstObj[i] eulerangle
						)
					)
				)
				select gnlstObj
		)-- catch()
/*
	on btSlide pressed do
		if (lstObj.count>0) and (lstSpl.count>0) then
		(
			--old code at center
			--lstObj[1].pivot.x = (lstObj[1].max.x+lstObj[1].min.x)/2
			local lstVert =#()
			local obj = lstObj[1]
			local n = polyOp.getNumVerts obj
			local objLength = lstObj[1].max.x-lstObj[1].min.x
			local objDir = [1,0,0]
			for i = 1 to n do
			(
				append lstVert (polyOp.getVert obj i)
				lstVert[i].x -= obj.min.x
				lstVert[i].y -= obj.pos.y
				lstVert[i].z -= obj.pos.z
			)
			local listHead = findTilingVert obj bThreshold.value
			print "List vertices:"
			--print lstVert
			print "Object information:"
			--print listHead
			local isMatch = cbMatch.checked 
			for iii = 1 to lstSpl.count do
				for ii = 1 to (numSplines lstSpl[iii]) do
				(
					local startparam = 0
					local endparam = 1
					local startlength = 0
					local endlength = 0
					segLength = getSegLengths lstSpl[iii] ii cum:true
					local splinelength = segLength[segLength.count]
					totallength = splinelength
					endlength = totallength
					local knot = getKnotSelection lstSpl[iii] ii
					local nKnot = numKnots lstSpl[iii] ii
					if (knot.count >= 1) then
					(
						if (knot[1] != 1) then
						(
							startparam = segLength[knot[1]-1]
							startlength = segLength[nKnot-1 +knot[1]-1]
						)
						if (knot.count > 1) then
						(
							endparam = segLength[knot[knot.count]-1]
							endlength = segLength[nKnot-1+knot[knot.count]-1]
						)
					)
					local dparam = endparam-startparam
					totallength = endlength - startlength
					print ("Total: " +totallength as string)
					print ("obj length: "+ objLength as string)
					print ("Start: "+startparam as string+" - "+startlength as string)
					print ("End: "+endparam as string+" - "+endlength as string)
					

					nobj = (Floor (totallength/objLength)) as integer 
					print (lstSpl[iii].name +": "	+nobj as string)
					if (isMatch)  then
					(
						if (spN.value > 0) then
							nobj = spN.value
					)
					else
					(
						spN.value = nobj
					)
					local pscale = totallength/(nobj*objLength)
					print ("Scale: "+pscale as string)
					gnlstObj = #()
					undo on
					(
						for i = 1 to nobj do
						(
							param = (startlength+(i*objLength-objLength))/splinelength
							if (isMatch) then
								param = (startlength+(i*objLength-objLength)*pscale)/splinelength							
								
							append gnlstObj #()
							n = gnlstObj.count
							--maxOps.cloneNodes obj cloneType:#instance newNodes:&nnl
							append gnlstObj[n] (copy obj)
							gnlstObj[n].scale.x *=pscale 
							if param <= 1 then
							(
								exactPos = interpCurve3D lstSpl[iii] ii param
								gnlstObj[i][1].pos = exactPos
							)
						)
						for i = 1 to nobj do
						(
				
							local objDir = (gnlstObj[i][1].rotation as matrix3)[1]
							if i<nobj then
								newDir = normalize (gnlstObj[i+1][1].pos-gnlstObj[i][1].pos)
							else
								newDir = normalize (interpCurve3D lstSpl[iii] ii 1-gnlstObj[i][1].pos)
							
							rot_axis = normalize (cross objDir newDir)
							rot_angle = - acos((dot objDir newDir)/(length objDir)/(length newDir))
							newquat = quat rot_angle rot_axis
							eulerangle = (quatToEuler newquat order:1)
							if not bRoll.checked then eulerangle.x = 0
							rotate gnlstObj[i][1] eulerangle
						)
					)

					if bSnap.checked then 
						undo on
						(
							for i = 1 to nobj-1 do
							(
								for j = 1 to listHead.count do
								(
									tpos = ((polyOp.getVert gnlstObj[i][1] listHead[j][2]) + (polyOp.getVert gnlstObj[i+1][1] listHead[j][1]))/2.0
									polyOp.setVert gnlstObj[i][1] #(listHead[j][2]) tpos 
									polyOp.setVert gnlstObj[i+1][1] #(listHead[j][1]) tpos 
								)
		    				)
						)
						
					if bAttach.checked then 
						undo on
						if nobj>1 then
						(
							for i = 2 to nobj do
								gnlstObj[1][1].EditablePoly.attach gnlstObj[i][1] gnlstObj[1][1]
		
							sel = gnlstObj[1][1]
							sel.weldThreshold = bThreshold.value
							polyOp.weldVertsByThreshold sel (#{1..(polyOp.getNumVerts sel)} as array)
						)
				)
		)-- catch()
*/

		
	
	on NAMIr_GuardrailsEx open do
	(
	)		
)		

createDialog NAMIr_GuardrailsEx
