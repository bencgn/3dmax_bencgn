

rollout rOSTools "BEN Tool Demo" rolledUp:false width:450
	(
	label createdByLabel "Tool created by: bencgn" 
		group "Fuck" (
	button btConvertPoly "ConvertPoly"  	width: 80  	 	across:5
	button btCollapto "Collapse To"  	width:80  	 	across:5 	
	button btInst "Select Inst"  	width:80  	 	across:5 
	button btClean "CleanDeadFace"  	width:80  	 	across:5 
	button ExportSelect "ExportSelect"  	width: 100  	 	across:5
	button OpenChanel2 "OpenChanel2"  	width: 100  	 	across:5
		)
	
	button btSetup "SetUpOfBen "  	width:80  	 	across:1
	button btOpenUnwrap "Open Unwrap"  	width:80  	 	across:1
	button btUVMap11 "UV Map 1m"  	width:130  	 	across:1
	button Reset00 "Reset00"  	width:130  	 	across:1	
		
	
	
	group "Export" (
	button btToolExport "Open Tool Export"  	width:130  	 	across:2
	button SetUnity "SetUnity Export"  	width:130  	 	across:2)

		group "Rename" (
			
	label lblInstructions "Select objects and click a button to rename them:"
	button Set_high "Set _high"  	width:130  	 	across:3
	button Set_low  "Set _low"  	width:130  	 	across:3
	button Set_  "Suffix _"  	width:130  	 	across:3
			
			)
	
	group "Model" (
	button btBox "Box"  	width:50  	 	across:5
	button btCylinder "Cylinder"  	width:50  	 	across:5
	button btSphere "Sphere"  	width:50  	 	across:5
	button btPlane "Plane"  	width:50  	 	across:5
	button btDummy "Dummy"  	width:50  	 	across:5	
		)
	
	group "Mirror" (
	button XYZ "XYZ"  	width:50  	 	across:1	  	 	
	button btMirrorx "Mirror_X"  	width:50  	 	across:3
	button btMirrory "Mirror_Y"  	width:50  	 	across:3
	button btMirrorz "Mirror_Z"  	width:50  	 	across:3)
		
	group "MTL" (
	button btNone "None Mat"  	width:50  	 	across:2
	button btNormal "Normal"  	width:50		across:2
	button btStandard "Step 1: Standard MTL"  	width:130  	 	across:1
	button btWireFrame "WireFrame"  	width:50  	 	across:2		
	button btColor "Color"  	width:50  	 	across:2

	)
	
	group "ViewPort" (
	button btL "Left"  	width:40  	 	across:4
	button btR "Right"  	width:40		across:4
	button btT "Top"  	width:40	across:4
	button btB "Botton"  	width:40  	 	across:4	

	button HideUnselected "HideUnselected"  	width: 80  	 	across:1
	button UnhideAll "Unhide All"  	width: 80  	 	across:1
	button Deletex "Deletex"  	width: 80  	 	across:1
	
	)
	
	group "Open Outside" (
	button btQa "Quick Attach"  	width:100  	 	across:1
	button miauuAlignObjsToVector "AlignObjsToVector"  	width:100  	 	across:1
	button Pivot_Bottom "Pivot_Bottom"  	width:100  	 	across:1
	button detachbyID "detachbyID"  	width:80  	 	across:2		
	button objectrename "rename_Pro"  	width:80  	 	across:2
	button helperManager "helperManager"  	width:80  	 	across:1
	button IFWNormals "IFWNormals"  	width:80  	 	across:1
	button polydamageV1_01 "polydamage"  	width:100  	 	across:1
	button QuadRemesher "QuadRemesher"  	width:100  	 	across:1
	button detach "Detach_Elements"  	width:100  	 	across:1

	)
	
	
	group "Hien Thi" (
		button displayname "Ten Object"  	width:100  	 	across:2
		button displaygroup "Ten Group"  	width:100  	 	across:2

	)
	
	group "Pivot Unity" (
		button setPivot "Pivot"  	width:100  	 	across:3
		button Pivot90 "Set x=90"  	width:100  	 	across:3
		button Move000 "Move to Origin"  	width:100  	 	across:3


	)
	group "Assembly Tool" (
	button assemblytoolrunfirst "RUNFIRST"  	width:100  	 	across:1
	button assemblytoolOpen "Open"  	width:100  	 	across:1
	)
	group "kilaD" (
	button kilaD "kilaD"  	width:100  	 	across:1
	
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


--QuadRemesherQuadRemesherQuadRemesherQuadRemesherQuadRemesherQuadRemesherQuadRemesher
	on SetUnity pressed do
	(
macros.run "Tools" "PivotMode_Toggle"
rotate $ (angleaxis 90 [90,0,0])		)			
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
	on kilaD pressed do
	(
	macros.run "kilaD" "openGhostTown"
	)
	
	on displayname pressed do
	(
	fileIn "D:\\3dmax_bencgn\\3dmax_bencgn\\Run\\displayname.ms"
	)
	
	on displaygroup pressed do
	(
	fileIn "D:\\3dmax_bencgn\\3dmax_bencgn\\Run\\displaygroup.ms"
	)
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
	on assemblytoolrunfirst pressed do
	(
	fileIn "D:\\3dmax_bencgn\\3dmax_bencgn\\Run\\assemblytool_1.191_0.mzp"
	)
	
	on assemblytoolOpen pressed do
	(
macros.run "Utopia" "AssemblyTool"
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
	on btQa pressed do
	(
		macros.run "# Scripts" "Quick_Attach"
	)


--ConvertPoly
	on btClean pressed do
	(
			
		polyop.collapseDeadStructs $

	)
	
	--ConvertPoly
	on btInst pressed do
	(
			
		macros.run "Selection" "SelectInstances"

	)
	--ConvertPoly
	on btL pressed do
	(
		max vpt left	
		max zoomext sel
	)
	on btR  pressed do
	(
		max vpt right	
		max zoomext sel
	)
	on btT pressed do
	(
max vpt top	
		max zoomext sel
	)
	on btB pressed do
	(
		max vpt bottom	
		max zoomext sel
	)
	
	--ConvertPoly
	on btConvertPoly pressed do
	(
		macros.run "Modifier Stack" "Convert_to_Poly"
	)
	--ConvertPoly
	on btCollapto pressed do
	(
maxOps.CollapseNodeTo $ 1 off
	)
	--SetUpOfBen
	on btSetup pressed do
	(
		max tool maximize
		macros.run "Scene Explorer" "SELayerExplorer"
		max render scene
	)
	--OpenUnwrap
	on btOpenUnwrap pressed do
	(
modPanel.addModToSelection (Unwrap_UVW ()) ui:on
	$.modifiers[#unwrap_uvw].unwrap2.setFreeFormMode on
	)
	--btUVMap11
	on btUVMap11 pressed do
	(
		modPanel.addModToSelection (Uvwmap ()) ui:on
$.modifiers[#UVW_Map].maptype = 4
$.modifiers[#UVW_Map].length = 100
$.modifiers[#UVW_Map].width = 100
$.modifiers[#UVW_Map].height = 100
macros.run "Modifier Stack" "Convert_to_Poly"
	)
	--vidu
	on btToolExport pressed do
	(
macros.run "N00BY" "Macro_Export"	
	)	
	--btBox
	on btBox pressed do
	(
Box length:1000 width:1000 height:1000 pos:[0,0,0] isSelected:on
	)
	--btBox
	on btCylinder pressed do
	(
Cylinder radius:200 height:200 pos:[0,0,0] isSelected:on
	)
	--btSphere
	on btSphere pressed do
	(
Sphere radius:500 pos:[0,0,0] isSelected:on
	)
	--btNone
	on btNone pressed do
	(
$. mat = null
	)
	--btPlane
	on btPlane pressed do
	(
Plane length:250 width:250 pos:[0,0,0] isSelected:on
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
	--btStandard
	on btStandard pressed do
	(
		max select
meditMaterials[1] = Standardmaterial ()
meditMaterials[2] = Standardmaterial ()
meditMaterials[3] = Standardmaterial ()
meditMaterials[4] = Standardmaterial ()
meditMaterials[5] = Standardmaterial ()
meditMaterials[6] = Standardmaterial ()
meditMaterials[7] = Standardmaterial ()
meditMaterials[8] = Standardmaterial ()
meditMaterials[9] = Standardmaterial ()
	)
	
	--btWireFrame
	on btWireFrame pressed do
	(
		meditMaterials[9].opacity = 0
		max select
		$.material = meditMaterials[9]
		
	)
	--btColor
	on btColor pressed do
	(
meditMaterials[8].Diffuse = color 64 64 64
meditMaterials[8].ambient = color 64 64 64
meditMaterials[8].Diffuse = color 64 64 64
meditMaterials[8].ambient = color 64 64 64
meditMaterials[8].specularLevel = 79
meditMaterials[8].glossiness = 25
		max select
		$.material = meditMaterials[8]
	)
	

)
createDialog rOSTools