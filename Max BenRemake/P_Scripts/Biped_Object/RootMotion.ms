
	undo on
		(
			with animate on
			(
				if selection.count > 0 then
				(
					Transform_array = #()
					
					TempTM = exposeTM()
					
					TempTM.exposeNode = $
					TempTM.localReferenceNode = $Dummy_Root

					at time SliderTime(append Transform_array TempTM.WorldPosition;)
					at time 0(append Transform_array TempTM.LocalPositionX; append Transform_array TempTM.LocalPositionY;)
					
					at time SliderTime($Dummy_Root.position.controller.value.x = Transform_array[1][1]-Transform_array[2])
					at time SliderTime($Dummy_Root.position.controller.value.y = Transform_array[1][2]-Transform_array[3])
					
					biped.addNewKey $.controller.horizontal.controller SliderTime
					
					NewPos = $.controller.horizontal.controller.value[4]

					NewPos.x = Transform_array[2]
					NewPos.y = Transform_array[3]
					NewPos.z = Transform_array[1][3]
					   
					biped.setTransform $ #pos NewPos false
					
					addnewkey $Dummy_Root.position.controller SliderTime
					
					k = getkeyindex $Dummy_Root.position.controller.x_position.controller SliderTime
					
					$Dummy_Root.position.controller.x_position.controller.keys[k].InTangentType = #linear
					$Dummy_Root.position.controller.y_position.controller.keys[k].OutTangentType = #linear
					
					
					
					i = getkeyindex $.controller.horizontal.controller slidertime
					(Biped.getkey $.controller.horizontal.controller i).continuity = 0
					
					delete TempTM
				)
				else false
			)
		)
		
	/*
	undo on
		(
			with animate on
			(
				if selection.count > 0 then
				(
					Transform_array = #()
					
					TempTM = exposeTM()
					
					TempTM.exposeNode = $
					TempTM.localReferenceNode = $Dummy_Root

					at time SliderTime(append Transform_array TempTM.WorldPosition)
					at time 0(append Transform_array TempTM.LocalPositionY)
					
					at time SliderTime($Dummy_Root.position.controller.value.y = Transform_array[1][2]-Transform_array[2])
					
					biped.addNewKey $.controller.horizontal.controller SliderTime
					
					NewPos = $.controller.horizontal.controller.value[4]

					NewPos.x = Transform_array[1][1]
					NewPos.y = Transform_array[2]
					NewPos.z = Transform_array[1][3]
					   
					biped.setTransform $ #pos NewPos false
					
					addnewkey $Dummy_Root.position.controller SliderTime
					
					k = getkeyindex $Dummy_Root.position.controller.y_position.controller SliderTime
					
					$Dummy_Root.position.controller.y_position.controller.keys[k].InTangentType = #linear
					$Dummy_Root.position.controller.y_position.controller.keys[k].OutTangentType = #linear
					
					i = getkeyindex $.controller.horizontal.controller slidertime
					(Biped.getkey $.controller.horizontal.controller i).continuity = 0
					
					delete TempTM
				)
				else false
			)
		)*/