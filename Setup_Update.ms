rollout rOSTools "Update and Set Up" rolledUp:false width:170
	(
	group "Run First" (
		button RunPivotBottom "RunPivotBottom"  	width:130  	 	across:1
		button lbtools "Runlbtools_helper_manager"  	width:140  	 	across:1
		
		
		
		)
	

	
	
	--
	on RunPivotBottom pressed do
	(
	fileIn "D:\\3dmax_bencgn\\3dmax_bencgn\\CaiDat\\AutoPivot_v1.2\\AutoPivot_Bottom_v1.2.mzp"
	)
	--
	on lbtools pressed do
	(
	fileIn "D:\\3dmax_bencgn\\3dmax_bencgn\\Run\\lbtools_helper_manager.mzp"
	)
	

)
createDialog rOSTools