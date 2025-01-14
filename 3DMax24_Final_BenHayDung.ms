

rollout rOSTools "BENCGN Demo" rolledUp:false width:400
	(
	label createdByLabel "Tool created by: bencgn" 
		group "Fuck" (
	button btConvertPoly "ConvertPoly"  	width: 80  	 	across:5
	button btInst "Select Inst"  	width:80  	 	across:5 
	button btClean "CleanDeadFace"  	width:80  	 	across:5 
	button ExportSelect "ExportSelect"  	width: 100  	 	across:5
	button OpenChanel2 "OpenChanel2"  	width: 100  	 	across:5
		)
	
	button btUVMap11 "UV Map 1m"  	width:130  	 	across:1
	button Reset00 "Reset00"  	width:130  	 	across:1	
		
	
	

	
	

		group "Rename" (
			
	label lblInstructions "Select objects and click a button to rename them:"
	button Set_high "Set _high"  	width:130  	 	across:2
	button Set_low  "Set _low"  	width:130  	 	across:2
	button Set_LOD00  "Set_LOD00"  	width:130  	 	across:1
	button Set_LOD01  "Set_LOD01"  	width:130  	 	across:1

	button Set_  "Suffix _"  	width:130  	 	across:1
	
			)
	

	
	group "Mirror" (
	button XYZ "XYZ"  	width:50  	 	across:2	  	 	
	button btMirrorx "Mirror_X"  	width:50  	 	across:2
	button btMirrory "Mirror_Y"  	width:50  	 	across:2
	button btMirrorz "Mirror_Z"  	width:50  	 	across:2)
		

	
	group "ViewPort" (


	button HideUnselected "HideUnselected"  	width: 80  	 	across:1
	button UnhideAll "Unhide All"  	width: 80  	 	across:1
	button Deletex "Deletex"  	width: 80  	 	across:1
	
	)
	

	

	
	group "Group " (
		button setPivot "Pivot"  	width:100  	 	across:2
		button Move000 "Move to Origin"  	width:100  	 	across:2


	)

	--Rename
	on Set_ pressed do
    (
        local selectedObjects = getCurrentSelection()
        for obj in selectedObjects do
        (
            obj.name = (obj.name + "_")
        )
    )
	
	

		--set

	
	on Set_low pressed do
    (
        local selectedObjects = getCurrentSelection()
        for obj in selectedObjects do
        (
            if not (matchPattern obj.name pattern:"*_low") do
            (
                if not (matchPattern obj.name pattern:"*_high") do
                (
                    obj.name = (obj.name + "_low")
                )
            )
        )
    )
	
	
		
	on Set_high pressed do
    (
        local selectedObjects = getCurrentSelection()
        for obj in selectedObjects do
        (
            if not (matchPattern obj.name pattern:"*_high") do
            (
                if not (matchPattern obj.name pattern:"*_low") do
                (
                    obj.name = (obj.name + "_high")
                )
            )
        )
    )
	
	on Set_LOD00 pressed do
    (
        local selectedObjects = getCurrentSelection()
        for obj in selectedObjects do
        (
            if not (matchPattern obj.name pattern:"*_LOD00") do
            (
                if not (matchPattern obj.name pattern:"*_LOD01") do
                (
                    obj.name = (obj.name + "_LOD00")
                )
            )
        )
    )
	
	on Set_LOD01 pressed do
    (
        local selectedObjects = getCurrentSelection()
        for obj in selectedObjects do
        (
            if not (matchPattern obj.name pattern:"*_LOD01") do
            (
                if not (matchPattern obj.name pattern:"*_LOD00") do
                (
                    obj.name = (obj.name + "_LOD01")
                )
            )
        )
    )
	--setPivot
	on Move000 pressed do
	(-- Get the selected objects
        local selectedObjects = getCurrentSelection()
        
        -- Check if any objects are selected
        if selectedObjects.count > 0 do
        (
            -- Move each selected object to the world origin
            for obj in selectedObjects do
            (
                obj.position = [0,0,0]
            )
            
            -- Deselect the objects after moving
            clearSelection()	)
		)

	

	on setPivot pressed do
	(
macros.run "Tools" "PivotMode_Toggle"		)
	
	--Detach_Elements
	on detach pressed do
	(
fileIn "D:\\3dmax_bencgn\\3dmax_bencgn\\Run\\Detach_Elements.ms"		)	


				
--QuadRemesherQuadRemeswherQuadRemesherQuadRemesherQuadRemesherQuadRemesherQuadRemesher
	on QuadRemesher pressed do
	(
macros.run "Exoside" "QuadRemesher"	)		
--IFWNormalsIFWNormalsIFWNormalsIFWNormalsIFWNormalsIFWNormalsIFWNormalsIFWNormalsIFWNormals
	on IFWNormals pressed do
	(
fileIn "D:\\3dmax_bencgn\\3dmax_bencgn\\Face_Weighted_Normals\\IFWNormals.mse"	)
--polydamageV1_01polydamageV1_01polydamageV1_01polydamageV1_01polydamageV1_01polydamageV1_01polydamageV1_01polydamageV1_01
	on polydamageV1_01 pressed do
	(
fileIn "D:\\3dmax_bencgn\\3dmax_bencgn\\polydamageV1_01\\polydamage_nm.mse"	)

	

	
--DisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplay
	on OpenChanel2 pressed do
	(
	
modPanel.addModToSelection (Unwrap_UVW ()) ui:on
$.modifiers[#unwrap_uvw].unwrap.setMapChannel 2
$.modifiers[#unwrap_uvw].unwrap.scale ()
	)
	
	
--DisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplayDisplay
	on ExportSelect pressed do
	(move $ [0,0,0]
		
		select $
actionMan.executeAction 0 "40373"  -- File: Export Selected
	)
	
	
	
	
	--btTake
	on XYZ pressed do
	(
	$.EditablePoly.MakePlanarIn #X
$.EditablePoly.MakePlanarIn #Y
$.EditablePoly.MakePlanarIn #Z
	)
	
	--HideUnselected
	on HideUnselected pressed do
	(
	actionMan.executeAction 0 "281"  -- Tools: Hide Unselected
	)
	
	--UnhideAll
	on UnhideAll pressed do
	(
actionMan.executeAction 0 "277"  -- Tools: Unhide All	
	)
	--UnhideAll

	on Deletex pressed do
	(
		
actionMan.executeAction 0 "40020"  -- Edit: Delete Objects	
	)
	
	--Reset00
	on Reset00 pressed do
	(
	move $ [0,-0,0]
scale $ [1,1,1]
rotate $ (angleaxis 0 [0,0,0])
	)
	--helperManager
	on helperManager pressed do
	(
	macros.run "LB Tools" "helperManager"
	)
	
	--Quick Attach
	on btDummy pressed do
	(
	Dummy pos:[0,0,0] isSelected:on
	)
	

	
	--Quick Attach
	on objectrename pressed do
	(
	fileIn "D:\\3dmax_bencgn\\3dmax_bencgn\\Run\\objectrename.mse"
	)
	
	--Quick Attach
	on detachbyID pressed do
	(
	fileIn "D:\\3dmax_bencgn\\3dmax_bencgn\\Run\\detachbyID.ms"
	)
	
	--Quick Attach
	on Pivot_Bottom pressed do
	(
		macros.run "Visuali Studio" "AutoPivot_Bottom"
	)
	--Quick Attach
	on miauuAlignObjsToVector pressed do
	(
		macros.run "miauu" "miauuAlignObjsToVector"
	)
--Quick Attach
	
	
	--ConvertPoly
	on btConvertPoly pressed do
	(
		macros.run "Modifier Stack" "Convert_to_Poly"
	)
	


	--btUVMap11
	on btUVMap11 pressed do
	(
		modPanel.addModToSelection (Uvwmap ()) ui:on
$.modifiers[#UVW_Map].maptype = 4
$.modifiers[#UVW_Map].length = 100
$.modifiers[#UVW_Map].width = 100
$.modifiers[#UVW_Map].height = 100

	)
	--vidu
	on btToolExport pressed do
	(
macros.run "N00BY" "Macro_Export"	
	)	
	

	
	--btNormal
	on btNormal pressed do
	(
macros.run "Modifiers" "EditNormals"
actionMan.executeAction 0 "40021"
max select all
actionMan.executeAction 0 "40021"  -- Selection: Select All
max select all
$.modifiers[#Edit_Normals].EditNormalsMod.Break ()
$.modifiers[#Edit_Normals].EditNormalsMod.Average ()
$.modifiers[#Edit_Normals].EditNormalsMod.Reset ()
	)
	--btMirrorx
	on btMirrorx pressed do
	(
modPanel.addModToSelection (mirror ()) ui:on
	$.modifiers[#Mirror].mirror_axis = 0
$.modifiers[#Mirror].copy = on
maxOps.CollapseNodeTo $ 1 off
	)

	--btMirrory
	on btMirrory pressed do
	(
modPanel.addModToSelection (mirror ()) ui:on
	$.modifiers[#Mirror].mirror_axis = 1
$.modifiers[#Mirror].copy = on
maxOps.CollapseNodeTo $ 1 off
	)
	
	--btMirrorz
	on btMirrorz pressed do
	(
modPanel.addModToSelection (mirror ()) ui:on
	$.modifiers[#Mirror].mirror_axis = 2
$.modifiers[#Mirror].copy = on
maxOps.CollapseNodeTo $ 1 off
	)

	


	

)
createDialog rOSTools