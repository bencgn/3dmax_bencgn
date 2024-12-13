rollout unnamedRollout "Search_By_Same_Face_Num" width:192 height:192
(
	pickbutton 'btn1' "Pick Ref" pos:[8,8] width:176 height:56 align:#left
	button 'btn2' "Search" pos:[8,72] width:176 height:56 align:#left
	
	label 'lbl1' "1. Pick Ref Object" pos:[8,136] width:112 height:16 align:#left
	
	label 'lbl2' "2. Choose the objects to inspect." pos:[8,152] width:168 height:16 align:#left
	label 'lbl3' "3. Press the [Search] button." pos:[8,168] width:112 height:16 align:#left
	on btn1 picked arg do
	(
		btn1.text=arg.name
	)
	on btn2 pressed do
	(
		arr_=#()
		if (btn1.object==undefined) do (return false)
		a= (getNumFaces btn1.object)
		for i in $selection do 
		(
			if ((classOf i)==Editable_Poly) and ((getNumFaces i)==a) do
			(
				append arr_ i
			)
		)
		actionMan.executeAction 0 "40043"  -- Selection: Select None
		select arr_
	)
)


CreateDialog unnamedRollout