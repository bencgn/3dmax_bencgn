
	rollout unnamedRollout "Attach Skin Objects" width:152 height:72
	(
		
		local mode=1
		local skinobj, bone_list
		Button 'btn1' "Select Skin Objects\n And press this button" pos:[16,9] width:120 height:48 align:#left
		on btn1 pressed do
		(
				if $selection.count<=1 do (Messagebox "Select Only Skin Objects"; return 0)
				for i in $selection do 
				(
				if i.modifiers[#Skin]==undefined do (Messagebox "Select Only Skin Objects"; return 0)	
				)
				sele=selection as array
				new_sele=#()
				for i in sele do
				(
					ii=copy i
					select ii
					append new_sele ii
				)
				
				converttopoly new_sele[1]
				
				for i=2 to new_sele.count do
				(
					polyop.attach new_sele[1] new_sele[i]
				)
				
				ddd=new_sele[1]
				select ddd
				addmodifier ddd (Skin_Wrap())
				ddd.modifiers[#Skin_Wrap].meshlist=sele
				ddd.modifiers[#Skin_Wrap].falloff = 10
				ddd.modifiers[#Skin_Wrap].threshold = 0.01
				ddd.modifiers[#Skin_Wrap].weightAllVerts = on
				ddd.modifiers[#Skin_Wrap].engine = 0
				select ddd
				)
	)
	
	createdialog unnamedRollout
