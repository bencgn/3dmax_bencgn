

rollout rOSTools "BENCGN Demo" rolledUp:false width:400
	(
	label createdByLabel "Tool created by: bencgn" 
		group "Edge Chuan" (
	button selectfirt "Select and Extrude 1"  	width:130  	 	across:1
			button selectfirta "Select and Extrude xx"  	width:130  	 	across:1
	button Del "CTRL Del"  	width:130  	 	across:1	
		button selecthai "No"  	width:130  	 	across:1
button selectba "Select and Extrude 3"  	width:130  	 	across:1
		)
	

	
	

	--Rename
	on selectfirt pressed do
    (
        $.edgeExtrudeWidth = 0.004
$.edgeExtrudeHeight = 0
$.EditablePoly.buttonOp #Extrude


    )
	
	on selectfirta pressed do
    (
        $.edgeExtrudeWidth = 0.003
$.edgeExtrudeHeight = 0
$.EditablePoly.buttonOp #Extrude


    )
		on Del pressed do
    (
$.EditablePoly.Remove ()

    )
	
		on selecthai pressed do
    (
$.edgeExtrudeWidth = 0.0029
$.edgeExtrudeHeight = 0
    )
	
	on selectba pressed do
    (
$.edgeChamfer = 0.003
$.edgeChamferMiteringType = 0
$.edgeChamferSegments = 3
$.edgeChamferTension = 1
$.edgeChamferEndBias = 0.5
$.edgeChamferRadialBias = 0
$.edgeChamferSmoothThreshold = 30
$.EditablePoly.buttonOp #Chamfer
    )
	
	
	

)
createDialog rOSTools