rollout rOSTools "BEN Tool Demo" rolledUp:false width:150
	(
	button btConvertPoly "ConvertPoly"  	width:130  	 	across:1
	button btSetup "SetUpOfBen"  	width:130  	 	across:1
	button btOpenUnwrap "Open Unwrap"  	width:130  	 	across:1
	button btUVMap11 "UV Map 1m"  	width:130  	 	across:1
	
	GroupBox 'GeometryGroupBox' "Test" pos:[8,118] width:232 height:22 align:#left

	button btToolExport"Open Tool Export"  	width:130  	 	across:1
	
		
		--ConvertPoly
	on btConvertPoly pressed do
	(

		macros.run "Modifier Stack" "Convert_to_Poly"
	
	)
	on btSetup pressed do
	(
		max tool maximize
		macros.run "Scene Explorer" "SELayerExplorer"
		max render scene
		
	)
	
	on btOpenUnwrap pressed do
	(

modPanel.addModToSelection (Unwrap_UVW ()) ui:on
	$.modifiers[#unwrap_uvw].unwrap2.setFreeFormMode on

	)
	on btUVMap11 pressed do
	(

		modPanel.addModToSelection (Uvwmap ()) ui:on
$.modifiers[#UVW_Map].maptype = 4
$.modifiers[#UVW_Map].length = 100
$.modifiers[#UVW_Map].width = 100
$.modifiers[#UVW_Map].height = 100
macros.run "Modifier Stack" "Convert_to_Poly"

	
	)
	
	
	--N00BY_Export_v2.1
	on btToolExport pressed do
	(


macros.run "N00BY" "Macro_Export"	
	)	
	
)
createDialog rOSTools