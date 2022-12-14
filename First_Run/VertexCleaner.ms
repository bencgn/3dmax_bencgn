-- script by Shiva
-- www.shiva3d.net


macroScript Vertex_cleaner category:"Shiva Tools" tooltip:"Vertex Cleaner 1.0 by Shiva"
(



global rltVertexCleaner
local  vx_2edges = #()
local vx_weight = #()
local  vx_selected = #()


fn vx_sort trash_val =
(

if  vx_2edges.count > 0 do (
			vx_selected = #()			
			for i = 1 to vx_2edges.count do	(				 
				if vx_weight[i] <= ( trash_val / 50 ) then append vx_selected vx_2edges[i]		
				)	--end of FOR i
			polyop.setvertselection $ vx_selected
			redrawViews()	
			
			)	--end of IF
)


try destroyDialog rltVertexCleaner catch()

rollout rltVertexCleaner "VertexCleaner" width:180 height:20
(
	spinner tresh "Threshold:" pos:[20,1] width:90 height:20 range:[0,100,10] type:#float enabled:true
	button btnCreate "Clean it!" pos:[110,1] width:50 height:16 tooltip:"start cleaning" enabled:true
	hyperLink homepage "?" address:"http://www.shiva3d.net/" pos:[165,1] 
	

	on tresh changed val do
	(
		vx_sort ( tresh.value )
	)
	
	
	on btnCreate pressed do
	(
		undo on(
		
					vx_sort ( tresh.value )
					polyop.setvertselection $  vx_selected
					$.EditablePoly.Remove ()
					redrawViews()	
		) -- end undo


	try destroyDialog rltVertexCleaner catch()
	str = "Vertices removed: " +  vx_selected.count as string
	messagebox str title:"Result"
	
	)	-- end on btnCreate pressed

)	-- end rollout rltVertexCleaner



if classof $ == Editable_poly then 
	(
	if subobjectlevel == 1 then 
		(     -- start the action
			
		sel = polyop.getVertSelection $  -- get the selected vertices
		selcount = sel as array

		for i = 1 to selcount.count do		-- collecting all vertex with 2 edges
			(
			vi = selcount[i]
			edg = polyOp.getEdgesUsingVert $ vi  -- get the edges that use the vertice
			quantos = edg as array
			if quantos.count  == 2 then 
				(
				append vx_2edges vi
				
				
				polyop.setvertselection $ vi
				vi_pos = polyop.getVert $ vi				

				vmass1 = polyop.getVertsUsingEdge $ quantos[1] as array
				if vmass1[1] == vi then vi_1 = vmass1[2] else vi_1 = vmass1[1]
				vi_1_vec = normalize( polyop.getVert $ vi_1 - vi_pos )
					
				vmass2 = polyop.getVertsUsingEdge $ quantos[2] as array
				if vmass2[1] == vi then vi_2 = vmass2[2] else vi_2 = vmass2[1]
				vi_2_vec = normalize( polyop.getVert $ vi_2 - vi_pos )
					
				vi_fin = length ( vi_1_vec + vi_2_vec )
				
				append vx_weight vi_fin
				
				) -- end of IF
			) -- end of For i

	--	polyop.setvertselection $ vx_2edges
	--	redrawViews()	
			
		createDialog rltVertexCleaner  180 18 ( mouse.screenpos.x - 100 ) ( mouse.screenpos.y - 20 )
	
		vx_sort ( rltVertexCleaner.tresh.value )
		
		)
	else messagebox "You should select vertices first." title: "Vertex Cleaner"
	)
	else messagebox "The object selected isn't a editable poly or nothing is selected." title: "Vertex Cleaner"
)