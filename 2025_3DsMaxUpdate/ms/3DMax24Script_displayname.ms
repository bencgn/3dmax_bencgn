unregisterRedrawViewsCallback GW_displayObjectNames
 
	function FindTopMostGroupHead obj = 
	(
		while obj != undefined and (not isGroupHead obj or isGroupMember obj) do
			(obj = obj.parent)
		obj
	)
 
	fn GW_displayObjectNames =
	(
		gw.setTransform (matrix3 1)
		for o in objects where not o.isHiddenInVpt and classof o != Targetobject do
		(
			if isGroupHead o or isOpenGroupHead o or isGroupMember o or isOpenGroupMember o then
			(
				grpHead = FindTopMostGroupHead o
				gw.text grpHead.pos grpHead.name color:yellow
			)
			else
			(				
				gw.text o.pos o.name color:yellow				
			)
			gw.enlargeUpdateRect #whole
		)
	)
 
	registerRedrawViewsCallback GW_displayObjectNames