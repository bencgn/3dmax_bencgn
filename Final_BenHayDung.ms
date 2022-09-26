rollout rOSTools "BEN Tool Demo" rolledUp:false width:170
	(
	button btConvertPoly "ConvertPoly"  	width:130  	 	across:1
	button btCollapto "Collapse To"  	width:130  	 	across:1
	button btSetup "SetUpOfBen"  	width:130  	 	across:1
	button btOpenUnwrap "Open Unwrap"  	width:130  	 	across:1
	button btUVMap11 "UV Map 1m"  	width:130  	 	across:1
	button btToolExport "Open Tool Export"  	width:130  	 	across:1
	button btNo "a--------------------------------a"  	width:170 across:1
	button btBox "Box"  	width:50  	 	across:3
	button btCylinder "Cylinder"  	width:50  	 	across:3
	button btSphere "Sphere"  	width:50  	 	across:3
	button btNoo "a--------------------------------a"  	width:170 across:1
	button btNone "None Mat"  	width:50  	 	across:1
	
	
	
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
	
	
	
)
createDialog rOSTools