
(

tool select_loop_for_skin
( 

local arrObj, arrPos, curObjIx, resultt, save1, save_skin, tm , arrDist , r , ss , save2
	
fn draw_line=
		(	
			ss=#{curObjIx}
			if (modpanel.getCurrentObject () as string=="Editable Poly") then
			( 
				polyop.setEdgeSelection $ ss; 
				save2=polyop.getEdgeSelection $
				
				polyop.setEdgeSelection $ save2;
				completeRedraw() 
			) 
			else if (modpanel.getCurrentObject () as string=="Skin:Skin") then
			( 
				skinOps.SelectVertices $.modifiers[#Skin] #{}
				save2=#()
				polyop.setEdgeSelection $ ss
				arr=($.EditablePoly.GetSelection #Edge) as array
				for i=1 to (arr.count)
				do 
					(
					save2+= (polyop.getEdgeVerts $ arr[i])
					)
				for i=1 to $.verts.count do
				(
					if (1==(skinOps.IsVertexSelected $.modifiers[#Skin] i))
					do save2+=#{i}
				) 
				skinOps.SelectVertices $.modifiers[#Skin] save2
				completeRedraw() 
			) 
			
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
			arrDist = for p in arrPos collect (p[2] * inverse tm)
			arrDist = for p in arrDist collect length (p * [1,1,0])
			curObjIx = finditem arrDist (amin arrDist)
			if (resultt.index)!=(curObjIx) do 
			(
				resultt=$.edges[curObjIx]
				draw_line()
			)
			
		)
		
on freeMove do
		(
			pickObj ()
			
		)
on start do
	(	
		resultt=$.edges[1]
		save1=$.EditablePoly.GetSelection #Edge 
		if (modpanel.getCurrentObject () as string=="Skin:Skin") then
			(
				save_skin=#{}
				for i=1 to $.verts.count do
				(
					if (1==(skinOps.IsVertexSelected $.modifiers[#Skin] i))
					do save_skin+=#{i}
				) 
			)		
		
		r = mapscreentoworldray mouse.pos
		tm = matrixfromnormal r.dir
		arrPos=for i=1 to $.edges.count collect (
			im=polyop.getEdgeVerts $ i
			#(i,(($.verts[im[1]].pos+$.verts[im[2]].pos)/2))
			)
		pickObj ()
	)	
on mousePoint arg do if arg == 2 do
	(
		ss=#{curObjIx}
		if (modpanel.getCurrentObject () as string=="Editable Poly") then
		(
			if ctrlKey or shiftkey then 
				(
				polyop.setEdgeSelection $ ss; $.ButtonOp #SelectEdgeLoop
				save2=polyop.getEdgeSelection $
				save2+=save1
				polyop.setEdgeSelection $ save2;
				) 
			else if altKey then 
				(
				polyop.setEdgeSelection $ ss; $.ButtonOp #SelectEdgeLoop
				save2=polyop.getEdgeSelection $
				save1-=save2
				polyop.setEdgeSelection $ save1;
				) 
			else (polyop.setEdgeSelection $ ss; macros.run "PolyTools" "Loop")
			
		)
		else if (modpanel.getCurrentObject () as string=="Skin:Skin") then
		(subobjectLevel = 1
			if ctrlKey or shiftkey then 
				(
				save2=#()
				polyop.setEdgeSelection $ ss
				$.ButtonOp #SelectEdgeLoop
				arr=($.EditablePoly.GetSelection #Edge) as array
				for i=1 to (arr.count)
					do (
						save2+= (polyop.getEdgeVerts $ arr[i])
						)
					save_skin=save_skin+(save2 as bitarray)
				skinOps.SelectVertices $.modifiers[#Skin] save_skin
				polyop.setEdgeSelection $ save1
				) 
			else if altKey then 
				(
				save2=#()
				polyop.setEdgeSelection $ ss
				$.ButtonOp #SelectEdgeLoop
				arr=($.EditablePoly.GetSelection #Edge) as array
				for i=1 to (arr.count)
					do (
						save2+= (polyop.getEdgeVerts $ arr[i])
						)
					save_skin=save_skin-(save2 as bitarray)
				skinOps.SelectVertices $.modifiers[#Skin] save_skin
				polyop.setEdgeSelection $ save1
				) 
			else (
				save2=#()
				polyop.setEdgeSelection $ ss
				$.ButtonOp #SelectEdgeLoop
				arr=($.EditablePoly.GetSelection #Edge) as array
				for i=1 to (arr.count)
					do (
						save2+= (polyop.getEdgeVerts $ arr[i])
						)
				skinOps.SelectVertices $.modifiers[#Skin] save2
				polyop.setEdgeSelection $ save1
				) 
		)
		#stop
	)
on mouseAbort arg do ()
		
)

if ($selection.count==1) do  
		(  test=modpanel.getCurrentObject () as string
		if ( test=="Editable Poly") then 
		(
		max modify mode; 
		subobjectLevel = 2
		startTool select_loop_for_skin
		)
		else if (test=="Skin:Skin" ) then
		(
		max modify mode; 
		subobjectLevel = 1
		startTool select_loop_for_skin
		)
	)
			

			
)