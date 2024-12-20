(
	local s,c,d,e2,f,f2
	fn getObjs = -- get biped objects
	(
		
		s=#()
		for i=1 to (skinOps.GetNumberBones ($selection[1].modifiers[#Skin])) do 
		(
		c=skinOps.GetBoneName ($selection[1].modifiers[#Skin]) i 1
		c=getNodeByName c
		append s c
		)
		return s
	)
	
	tool objPick
	(
		local arrObj, arrPos, curObjIx
		
		fn gwDrawBBox o =
		(	
			arrBPos = nodeGetBoundingBox o o.transform
			x1 = arrBPos[1].x; x2 = arrBPos[2].x
			y1 = arrBPos[1].y; y2 = arrBPos[2].y
			z1 = arrBPos[1].z; z2 = arrBPos[2].z
			gw.setTransform o.transform
			gw.setColor #line o.wirecolor
			gw.Polyline #([x1,y1,z1], [x1,y2,z1], [x1,y2,z2], [x1,y1,z2]) true
			gw.Polyline #([x2,y1,z1], [x2,y2,z1], [x2,y2,z2], [x2,y1,z2]) true
			gw.Polyline #([x1,y1,z1], [x2,y1,z1]) false
			gw.Polyline #([x1,y2,z1], [x2,y2,z1]) false
			gw.Polyline #([x1,y2,z2], [x2,y2,z2]) false
			gw.Polyline #([x1,y1,z2], [x2,y1,z2]) false
			gw.setTransform o.transform
		)
		
		fn gwDrawBipName o = -- bip only
		(
			head = biped.getnode o 11 link:1
			gw.setTransform head.objecttransform
			gw.text [1.5,0,0] o.controller.rootnode.name color:yellow
		)
		
		fn cbDrawBBox =
		(
			gwDrawBBox arrObj[curObjIx]
			--gwDrawBipName arrObj[curObjIx] -- bip only
			
			gw.enlargeUpdateRect #whole
		)
		
		fn getMouseBaseTm =
		(
			r = mapscreentoworldray mouse.pos
			tm = matrixfromnormal r.dir
			tm.pos = r.pos
			tm
		)
		
		fn pickObj =
		(
			tm = getMouseBaseTm ()
			
			arrDist = for p in arrPos collect (p * inverse tm)
			arrDist = for p in arrDist collect length (p * [1,1,0])
			curObjIx = finditem arrDist (amin arrDist)
			
			redrawviews()
		)
		
		on freeMove do
		(
			pickObj ()
		)
		
		on mousePoint arg do if arg == 2 do
		(
			sk=$.modifiers[#Skin]
			for i=1 to (skinOps.GetNumberBones sk) do
			(
				if (skinOps.GetBoneName sk i 1) == arrObj[curObjIx].name do (skinOps.SelectBone sk i; exit)
			)
			--skinOps.SelectBone $.modifiers[#Skin] curObjIx
			#stop
		)
		
		on start do
		(
			arrObj = getObjs ()
			arrPos = for o in arrObj collect
			(
				 o.center -- for normal objs
				--if (biped.getidlink o).x == 12 then [-.1,0,0] * o.objecttransform else o.center -- for biped
			)
			pickObj ()
			registerRedrawViewsCallback cbDrawBBox
			redrawviews ()
		)
		
		on stop do
		(
			unregisterRedrawViewsCallback cbDrawBBox
			redrawviews ()
		)
	)
	
	if (getObjs ()).count > 0 do
	(
		stopTool objPick
		startTool objPick
		
	)
)

