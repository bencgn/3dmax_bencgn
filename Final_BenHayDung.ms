rollout rOSTools "BEN Tool Demo" rolledUp:false width:170
	(
	button btConvertPoly "ConvertPoly"  	width:130  	 	across:1
	button btCollapto "Collapse To"  	width:130  	 	across:1 	
	
	group "Need" (
	button btSetup "SetUpOfBen "  	width:130  	 	across:1
	button btOpenUnwrap "Open Unwrap"  	width:130  	 	across:1
	button btUVMap11 "UV Map 1m"  	width:130  	 	across:1)
	group "Export" (
	button btToolExport "Open Tool Export"  	width:130  	 	across:1)
	
	group "Model" (
	button btBox "Box"  	width:50  	 	across:3
	button btCylinder "Cylinder"  	width:50  	 	across:3
	button btSphere "Sphere"  	width:50  	 	across:3
	button btPlane "Plane"  	width:50  	 	across:1)
	
	group "Mirror" (
		  	 	
	button btMirrorx "Mirror_X"  	width:50  	 	across:3
	button btMirrory "Mirror_Y"  	width:50  	 	across:3
	button btMirrorz "Mirror_Z"  	width:50  	 	across:3)
		
	group "MTL" (
	button btNone "None Mat"  	width:50  	 	across:2
	button btNormal "Normal"  	width:50		across:2
	button btStandard "Step 1: Standard MTL"  	width:130  	 	across:1
	button btWireFrame "select 1: mtl WireFrame"  	width:130  	 	across:1		
	button btColor "select 2: mtl Color"  	width:130  	 	across:1)
	
	
	
	
	
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