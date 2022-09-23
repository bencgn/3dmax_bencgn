rollout rlObjectRandomizer " Object Randomizer"
(
	local mX,mY,mZ, rX, rY, rZ, sX, sY, sZ
	
	fn fnObjMove = (
		mX = (random rlObjectRandomizer.spnXMMin.value rlObjectRandomizer.spnXMMax.value)
		mY = (random rlObjectRandomizer.spnYMMin.value rlObjectRandomizer.spnYMMax.value)
		mZ = (random rlObjectRandomizer.spnZMMin.value rlObjectRandomizer.spnZMMax.value)
	)
	
	fn fnObjRotate =	(
		rX = (random rlObjectRandomizer.spnXRMin.value rlObjectRandomizer.spnXRMax.value) as float
		rY = (random rlObjectRandomizer.spnYRMin.value rlObjectRandomizer.spnYRMax.value) as float
		rZ = (random rlObjectRandomizer.spnZRMin.value rlObjectRandomizer.spnZRMax.value) as float
	)
	
	fn fnObjScale = (
		sX = random ((rlObjectRandomizer.spnXSMin.value)*0.01) ((rlObjectRandomizer.spnXSMax.value)*0.01)
		sY = random ((rlObjectRandomizer.spnYSMin.value)*0.01) ((rlObjectRandomizer.spnYSMax.value)*0.01)
		sZ = random ((rlObjectRandomizer.spnZSMin.value)*0.01) ((rlObjectRandomizer.spnZSMax.value)*0.01)
	)
	
	groupbox gbxMove "" width:245 height:64 pos:[10,10]  -- Position
	label lbX " X " pos:[92,10]
	label lbY " Y " pos:[150,10]
	label lbZ " Z " pos:[208,10]	
	checkbox ckbxMove "Move" pos:[20,10]
	label lbXMMin "Min: " pos:[20,30]
	label lbXMMax "Max: " pos:[20,50]
	spinner spnXMMin "" fieldwidth:45 range:[-9999,9999,-6] enabled:false type:#float pos:[70,30]
	spinner spnXMMax "" fieldwidth:45 range:[-9999,9999,6] enabled:false type:#float pos:[70,50]
	spinner spnYMMin "" fieldwidth:45 range:[-9999,9999,-6] enabled:false type:#float pos:[130,30]
	spinner spnYMMax "" fieldwidth:45 range:[-9999,9999,-6] enabled:false type:#float pos:[130,50]
	spinner spnZMMin "" fieldwidth:45 range:[-9999,9999,-6] enabled:false type:#float pos:[190,30]
	spinner spnZMMax "" fieldwidth:45 range:[-9999,9999,6] enabled:false type:#float pos:[190,50]
	groupbox gbxRotate "" width:245 height:64 pos:[10,80] -- Rotation
	label lbX2 " X " pos:[92,80]
	label lbY2 " Y " pos:[150,80]
	label lbZ2 " Z " pos:[208,80]
	checkbox ckbxRotate "Rotate" pos:[20,80]
	label lbXRMin "Min: " pos:[20,100]
	label lbXRMax "Max: " pos:[20,120]
	Spinner spnXRMin "" fieldwidth:45 range:[-9999,9999,-45] enabled:false type:#float pos:[70,100]
	spinner spnXRMax "" fieldwidth:45 range:[-9999,9999,45] enabled:false type:#float pos:[70,120]
	spinner spnYRMin "" fieldwidth:45 range:[-9999,9999,-45] enabled:false type:#float pos:[130,100]
	spinner spnYRMax "" fieldwidth:45 range:[-9999,9999,45] enabled:false type:#float pos:[130,120]
	spinner spnZRMin "" fieldwidth:45 range:[-9999,9999,-45] enabled:false type:#float pos:[190,100]
	spinner spnZRMax "" fieldwidth:45 range:[-9999,9999,45] enabled:false type:#float pos:[190,120]
	groupbox gbxScale "" width:245 height:82 pos:[10,150] -- Scale
	label lbX3 " X " pos:[92,150]
	label lbY3 " Y " pos:[150,150]
	label lbZ3 " Z " pos:[208,150]
	checkbox ckbxScale "Scale" pos:[20,150]
	label lbXSMin "Min %: " pos:[20,170]
	label lbXSMax "Max %: " pos:[20,190]
	Spinner spnXSMin "" fieldwidth:45 range:[-9999,9999,-10] enabled:false type:#float pos:[70,170]
	spinner spnXSMax "" fieldwidth:45 range:[-9999,9999,10] enabled:false type:#float pos:[70,190]
	spinner spnYSMin "" fieldwidth:45 range:[-9999,9999,-10] enabled:false type:#float pos:[130,170]
	spinner spnYSMax "" fieldwidth:45 range:[-9999,9999,10] enabled:false type:#float pos:[130,190]
	spinner spnZSMin "" fieldwidth:45 range:[-9999,9999,-10] enabled:false type:#float pos:[190,170]
	spinner spnZSMax "" fieldwidth:45 range:[-9999,9999,10] enabled:false type:#float pos:[190,190]
	label lbUniformScale "Uniform Scale: " pos:[160,212] across:2 
	checkbox ckbtnUniformScale "" width:20 enabled:false checked:true pos:[234,212]
	radiobuttons rbtnTransformType labels:#("Absolute", "Relative") pos:[10,245] default:1  -- Transform
	button btnApply "Apply" width:115 height:25 pos:[140,240]
		
	on ckbxMove changed theState do (if theState == true then(spnXMMin.enabled = spnYMMin.enabled = spnZMMin.enabled = spnXMMax.enabled = spnYMMax.enabled = spnZMMax.enabled = true)else(spnXMMin.enabled = spnYMMin.enabled = spnZMMin.enabled = spnXMMax.enabled = spnYMMax.enabled = spnZMMax.enabled = false))
	on ckbxRotate changed theState do (if theState == true then(spnXRMin.enabled = spnYRMin.enabled = spnZRMin.enabled = spnXRMax.enabled = spnYRMax.enabled = spnZRMax.enabled = true)else(spnXRMin.enabled = spnYRMin.enabled = spnZRMin.enabled = spnXRMax.enabled = spnYRMax.enabled = spnZRMax.enabled = false))
	on ckbxScale changed theState do (if theState == true then(spnXSMin.enabled = spnXSMax.enabled = ckbtnUniformScale.enabled = true if ckbtnUniformScale.checked == true then(spnYSMin.enabled = spnYSMax.enabled = spnZSMin.enabled = spnZSMax.enabled = false)else(spnYSMin.enabled = spnYSMax.enabled = spnZSMin.enabled = spnZSMax.enabled = true))else(spnXSMin.enabled = spnXSMax.enabled = spnYSMin.enabled = spnYSMax.enabled = spnZSMin.enabled =	spnZSMax.enabled = ckbtnUniformScale.enabled = false))	
	on ckbtnUniformScale changed state do (spnYSMin.enabled =	spnYSMax.enabled = spnZSMin.enabled = spnZSMax.enabled = not ckbtnUniformScale.checked)		
	on btnApply rightclick do(spnXMMin.value = spnYMMin.value = spnZMMin.value = spnXMMax.value = spnYMMax.value = spnZMMax.value = spnXRMin.value = spnYRMin.value = spnZRMin.value = spnXRMax.value = spnYRMax.value = spnZRMax.value = spnXSMin.value = spnYSMin.value = spnZSMin.value = spnXSMax.value = spnYSMax.value = spnZSMax.value = 0)
		
	on btnApply pressed do
	(
		undo on
		(
			case rbtnTransformType.state of 
			(
				1:	(	for obj in selection do -- Absolute
						(
							fnObjMove() 
							if (ckbxMove.checked == true) do (obj.position = [mX,mY,mZ])
							fnObjRotate()
							if (ckbxRotate.checked == true) do (in coordsys (transmatrix obj.transform.pos) obj.rotation = (eulerangles rX rY rZ))
							fnObjScale()
							if (ckbxScale.checked == true) do (obj.scale = [sX, sY, sZ] if ckbtnUniformScale.checked == true do (obj.scale = [sX, sX, sX]))
						)
					)
					
				2:	(	for obj in selection do -- Relative
						(
							fnObjMove()
							if (ckbxMove.checked == true) do (move obj [mX,mY,mZ])
							fnObjRotate()
							if (ckbxRotate.checked == true) do (in coordsys local rotate obj (EulerAngles rX rY rZ))
							fnObjScale()
							if (ckbxScale.checked == true) do (obj.scale = [(obj.scale.x * sX), (obj.scale.y * sY), (obj.scale.z * sZ)] if ckbtnUniformScale.checked == true do (obj.scale = [(obj.scale.x * sX), (obj.scale.x * sX), (obj.scale.x * sX)]))
						)
					)
			)
		)
	)
)
createDialog rlObjectRandomizer 265 272 style:#(#style_SysMenu, #style_ToolWindow)