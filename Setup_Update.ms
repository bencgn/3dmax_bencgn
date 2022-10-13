rollout rOSTools "Update and Set Up" rolledUp:false width:170
	(
	group "Update" (
		button btConvertPoly "ConvertPoly"  	width:130  	 	across:1
		)
	group "Setup" (
		button btConvertPoly "ConvertPoly"  	width:130  	 	across:1
		)

	
	
	--ConvertPoly
	on btConvertPoly pressed do
	(
		macros.run "Modifier Stack" "Convert_to_Poly"
	)


)
createDialog rOSTools