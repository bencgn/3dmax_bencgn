rollout rOSTools "Update and Set Up" rolledUp:false width:170
	(
	group "Run First" (
		button RunPivotBottom "RunPivotBottom"  	width:130  	 	across:1
		)
	group "Setup" (
		button btConvertPoly "ConvertPoly"  	width:130  	 	across:1
		)

	
	
	--Quick Attach
	on RunPivotBottom pressed do
	(
	fileIn "D:\\3dmax_bencgn\\3dmax_bencgn\\CaiDat\\AutoPivot_v1.2\\AutoPivot_Bottom_v1.2.mzp"
	)


)
createDialog rOSTools