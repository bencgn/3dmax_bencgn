macroScript RotateToGrid
	category:"Custom"
	internalCategory:"Custom" 
	tooltip:"Rotate To Grid"
	ButtonText:"Rotate To Grid" 
	autoUndoEnabled:false
(--rotate to grid
	
	fn SortVectors Vectors idx vSample =
	(				
		local i = 1
		
		for i = 1 to 3 do
		(		
			local dot1 = dot Vectors[idx] vSample
			local dot2 = dot Vectors[i] vSample
			
						
			if abs dot1 < abs dot2 then
			(
				local tmp = Vectors[idx]
				Vectors[idx] = Vectors[i]
				Vectors[i] = tmp 
			)
		)
		
	)
	
	fn getBitsAsArray bits = 
	(
		arr = #{}
		for i = 1 to 32 do (
			arr[i] = bit.get bits i;
		)
		return arr;
	)
	
	
	--if selected is not class of editable poly or don't have edit poly modifier and edge level chosen then disable 
	On IsEnabled return (Filters.Is_EPoly() and (subobjectlevel == 2))
	--On IsVisible return (Filters.Is_EPoly() and (subobjectlevel == 2))
	
	on execute do
	(
		
		
		local obj = $			
		local dir
		local dirNorm
		local pos = [0,0,0]
		
		local selEdges 		
		local epMod = modPanel.GetCurrentObject()
		
		case (classof epMod) of
 		(
 			(Editable_Poly):
 			(
 				selEdges = ( polyOp.getEdgeSelection obj ) as array					
 			)
 			(Edit_Poly):
 			( 				
 				selEdges = ( epMod.GetSelection #Edge ) as array 				
 			)
 			default: return false
 		)
		
				
		if selEdges.count > 1 then
		(
			print "Warning: more than 1 edge selected!! Only first edgeID's was taken"		
		)
		
		local selEdge = selEdges[1]
			
		
		local connectedVerts = (polyop.getVertsUsingEdge obj selEdge) as array
		local vert1pos = obj.verts[connectedVerts[1]].pos
		local vert2pos = obj.verts[connectedVerts[2]].pos		
		local connectedFaces = polyop.getFacesUsingEdge obj selEdge as Array
		
		pos = [(vert1pos.x +vert2pos.x)/2, (vert1pos.y +vert2pos.y)/2, (vert1pos.z +vert2pos.z)/2]		
		
		dir = normalize (vert1pos - vert2pos)		
		
		Face1SM = getBitsAsArray (polyop.getFaceSmoothGroup obj connectedFaces[1])
		Face2SM = getBitsAsArray (polyop.getFaceSmoothGroup obj connectedFaces[2])

		
		dirNorm = try
			(
				if (Face1SM*Face2SM).isEmpty != 0
				then
				(polyop.getFaceNormal obj connectedFaces[1])
				else
				(polyop.getFaceNormal obj connectedFaces[1] + polyop.getFaceNormal obj connectedFaces[2])/2				
			) 			
			catch (polyop.getFaceNormal obj connectedFaces[1])
		
		dircross = cross dirNorm dir 
		
		local vectors = #(dir, dirNorm, dircross)
						
		SortVectors Vectors 1 [1,0,0]		
		SortVectors Vectors 2 [0,1,0]		
		SortVectors Vectors 3 [0,0,1]		
		
		if dot [1,0,0] Vectors[1] < 0 then Vectors[1] *= -1 
		if dot [0,1,0] Vectors[2] < 0 then Vectors[2] *= -1
		if dot [0,0,1] Vectors[3] < 0 then Vectors[3] *= -1
		
		local tm = orthogonalize (matrix3 Vectors[1] Vectors[2] Vectors[3] pos)
		
		tmquat = tm as Quat
		
		undo on		
		(		
		
			--p = point ()
			--p.transform = tm
			
			in coordsys tm about pos rotate obj tmquat
		
		)
		CompleteRedraw()4
	)
	
)