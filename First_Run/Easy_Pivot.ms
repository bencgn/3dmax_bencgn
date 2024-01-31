/*
This script is used to move the pivot of the object as specified in the dropdown list.
Author : Yusuph Wickama
Email : Yusuph.wickama@gmail.com
Facebook Page : www.facebook.com/wickerfilms
Copyright © 2014 Wickerfilms. All Rights Reserved
*/

rollout Pivot_tool "Wickerfilms | Easy Pivot ®" width:240 height:280
(
	GroupBox functions "Controls" pos:[8,112] width:224 height:136
	dropdownList droplist1 "" pos:[96,156] width:128 height:21 items:#("Top", "Center", "Bottom", "Center Left", "Center Right", "Bottom Left", "Bottom Right", "Top left", "Top right") selection:1 toolTip:"Choose a position to place the pivot"
	label lbl1 "Pivot Position : " pos:[16,160] width:75 height:16
	button Reset_Pivot "Reset" pos:[128,200] width:96 height:32 toolTip:"Change pivot position."
	button apply "Apply" pos:[16,200] width:96 height:32 toolTip:"Change pivot position."
	label lbl2 "Copyright © 2014 Wickerfilms." pos:[44,256] width:152 height:16
	dotNetControl image "Label" pos:[0,0] width:240 height:100
	
	local ConvertClass = dotnetclass "system.convert"
	local ImageClass = dotnetclass "system.drawing.image"
	local ColorClass =dotnetclass "system.drawing.color"
	local Align = dotnetclass "System.Drawing.ContentAlignment"
	local ImageString = "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"	

	--Conversion String
	fn String2Image string =
(
	bytearr = convertclass.FromBase64String string
	memstream = dotnetobject "System.IO.MemoryStream" bytearr
	DecodedImg = ImageClass.fromstream memstream
	memstream.close()
	return DecodedImg
)	
	--OnClick Activities

	
	on Pivot_tool open do
	(
		Image.backcolor = ColorClass.FromArgb 0 0 0
		image.forecolor = ColorClass.white
		image.font = dotNetObject "System.Drawing.Font" "Courier new" 12.5
		Image.text = "Easy Pivot v1.01"
		Image.textalign = Align.MiddleRight
		Image.ImageAlign = Align.MiddleLeft
		Image.image= String2Image ImageString
		
	)
	on Reset_Pivot pressed do
	(
		if $ == undefined do 
		(
			messageBox "No object is selected!" title:"Wickerfilms | Pivot Tool ®" beep:true
		)
		
		if $ != undefined do 
		(
			for obj in $ do
		(
			--Variables for positions
			ResetPivot obj
		)
			
		)
	)
	on apply pressed do
	(
		if $ == undefined do 
		(
			messageBox "No object is selected!" title:"Wickerfilms | Pivot Tool ®" beep:true
		)
		
		if $ != undefined do 
		(
			for obj in $ do
		(
			--Variables for positions
			CenterPivot obj
			CurPos = obj.position
			MaxPos = obj.max
			MinPos = obj.min
			
			-- Function based on selection
			if droplist1.selection == 1 do
			(
				--Placing the pivot at the top of the object
				obj.pivot = [CurPos.x,CurPos.y,MaxPos.z]
			)
		
			if droplist1.selection == 2 do
			(
				--Placing the picot at the center if the object
				CenterPivot obj
			)
			
			if droplist1.selection == 3 do
			(
				--Placing the pivot at the bottom of the object
				obj.pivot = [CurPos.x,CurPos.y,MinPos.z]
			)
			
			if droplist1.selection == 4 do
			(
				--Placing the pivot at the Center left of the object
				obj.pivot = [MinPos.x,CurPos.y,CurPos.z]
			)
			
			if droplist1.selection == 5 do
			(
				--Placing the pivot at the Center right of the object
				obj.pivot = [MaxPos.x,CurPos.y,CurPos.z]
			)
			
			if droplist1.selection == 6 do
			(
				--Placing the pivot at the Bottom left of the object
				obj.pivot = [MinPos.x,CurPos.y,MinPos.z]
			)
			
			if droplist1.selection == 7 do
			(
				--Placing the pivot at the Bottom right of the object
				obj.pivot = [MaxPos.x,CurPos.y,MinPos.z]
			)
			
			if droplist1.selection == 8 do
			(
				--Placing the pivot at the Top left of the object
				obj.pivot = [MinPos.x,CurPos.y,MaxPos.z]
			)
			
			if droplist1.selection == 9 do
			(
				--Placing the pivot at the Topright of the object
				obj.pivot = [MaxPos.x,CurPos.y,MaxPos.z]
			)
		)
			
		)
	)
)
createdialog Pivot_tool