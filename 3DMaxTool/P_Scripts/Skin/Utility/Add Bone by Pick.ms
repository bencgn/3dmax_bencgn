rollout unnamedRollout "Add Bone(Pick)" width:152 height:72
(
	
	local mode=1
	local skinobj, bone_list
	Button 'btn1' "Select Skin Object\n And press this button" pos:[16,9] width:120 height:48 align:#left
	on btn1 pressed do
	(
		if mode==1 then 
			(
				if $selection.count!=1 do (messagebox "Select One Object" return 0)
				if $selection[1].modifiers[#Skin]==undefined do (messagebox "Select Skin Object" return 0)
				btn1.text="Select bone\n And press this button"
				skinobj=(selection as array)[1]
				skinobj.xray = on
				freeze skinobj
				deselect skinobj
				mode=2
			)
		else
			(
			skinobj.xray = off
			unfreeze skinobj
			bone_list=selection as array
			select skinobj
			if bone_list.count==0 do (return 0)
			for i in bone_list do
				(
				skinOps.addbone ($selection[1].modifiers[#Skin]) i -1
				)
			destroydialog unnamedRollout
			)
			
	)
)

createdialog unnamedRollout