unregisterRedrawViewsCallback GW_displayObjectNames
 
	fn GW_displayObjectNames =
	(
		gw.setTransform (matrix3 1)
		for o in objects where not o.isHiddenInVpt and classof o != Targetobject do
		(
			if isGroupHead o or isOpenGroupHead o then
			(
				gw.text o.pos o.name color:yellow
			)
			else
			(
				if not isGroupMember o and not isOpenGroupMember o do
					gw.text o.pos o.name color:yellow				
			)
			gw.enlargeUpdateRect #whole
		)
	)
 
	registerRedrawViewsCallback GW_displayObjectNames