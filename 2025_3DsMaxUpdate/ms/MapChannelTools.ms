rollout MapChannelTools "MapChannel" rolledUp:false
(

		spinner spnFromChannel "Channel:  from" range:[1,99,1] type:#integer scale:1 fieldwidth:24 align:#left offset:[-4,0]
		spinner spnToChannel "-->to" range:[1,99,2] type:#integer scale:1 fieldwidth:24 align:#right offset:[4,-22]
		
		button btnCopyMapChan_OneObj "Copy Source / Paste Source" width:155 height:20 offset:[0, 2]
		
		editText eSuffix "* Src objs co suffix: --> " text:"_old"  width:150 height:16 offset:[0, 4]
		button btnCopyMapChan_TwoObj "Copy Source / Paste Dest" width:155 height:20 offset:[-3, 0]
	
	fn fnCopyMapChannel_OneObj obj fromChannel toChannel =
	(
		try
		(
			if (fromChannel != toChannel) then
			(
				local currentNumMaps=(polyOp.getNumMaps obj)-1			
				if currentNumMaps<1 do polyOp.setNumMaps obj toChannel+1 keep:true
					
				local currentMapSupport1=polyOp.getMapSupport obj fromChannel			
				if currentMapSupport1==false do polyOp.defaultMapFaces obj fromChannel
					
				local currentMapSupport2=polyOp.getMapSupport obj toChannel			
				if currentMapSupport2==false do polyOp.defaultMapFaces obj toChannel
					
				channelInfo.CopyChannel obj 3 fromChannel
				channelInfo.PasteChannel obj 3 toChannel
			)
		)
		catch ()
	)
	
	fn fnCopyMapChannel_TwoObj fromObj toObj fromChannel toChannel =
	(
		try
		(
			if (polyOp.getMapSupport fromObj fromChannel) then
			(
				local currentNumMaps=(polyOp.getNumMaps toObj) - 1			
				if currentNumMaps<1 then
					polyOp.setNumMaps toObj (toChannel+1) keep:true
					
				if ((polyOp.getMapSupport toObj toChannel) ==  false) then
					polyOp.defaultMapFaces toObj toChannel
					
				channelInfo.CopyChannel fromObj 3 fromChannel
				channelInfo.PasteChannel toObj 3 toChannel
			)
		)
		catch ()
	)
	
	on btnCopyMapChan_OneObj pressed do
	(
		try
		(
			for obj in selection do
			(
				convertTo obj Editable_Poly
				fnCopyMapChannel_OneObj obj spnFromChannel.value spnToChannel.value
				convertTo obj Editable_Poly
			)
		)
		catch ()
	)
	
	on btnCopyMapChan_TwoObj pressed do
	(
		try
		(
			local copiedChanObjs = #()
			
			for obj in selection do
			(
				local toName = substring obj.name 1 (obj.name.count - eSuffix.text.count)
				
				local fromObj = getNodeByName (toName + eSuffix.text)
				local toObj = getNodeByName toName
				
				if (fromObj != undefined) and (toObj != undefined) then
				(
					convertTo fromObj Editable_Poly
					convertTo toObj Editable_Poly
					
					fnCopyMapChannel_TwoObj fromObj toObj spnFromChannel.value spnToChannel.value
					
					convertTo toObj Editable_Poly					
					append copiedChanObjs toObj
				)
			)
			
			select copiedChanObjs
		)
		catch ()
	)

)






createDialog MapChannelTools width:180
