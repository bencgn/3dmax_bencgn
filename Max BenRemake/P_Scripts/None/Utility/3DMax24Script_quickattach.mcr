macroScript Quick_Attach
	category:"# Scripts"
	toolTip:"Quick Attach v1.71"
	Icon:#("BodyObjects",4)
(
	--This script created by Morozov Anton
	-- Create emty Editable Poly and attach selected objects
try destroyDialog Quick_Attach catch()
global seq = 300 -- how many objectts add to one part

function attachAll =
(
	if selection.count != 0 then (
	seq = Quick_Attach.spn1.value
	arr = (selection as array)
	clearSelection()
	count = 0
	meshes=#()
	b = Editable_Mesh()
	if Quick_Attach.rdo1.state == 1 do convertTo b Editable_Poly
	b.name = arr[1].name
	append meshes b
	precents = 0 as float
	for i = 1 to arr.count do
	(
		count += 1
		if count >= seq do (
			count = 1
			b = Editable_Mesh()
			if Quick_Attach.rdo1.state == 1 do convertTo b Editable_Poly
			b.name = arr[i].name
			append meshes b
			precents = 1000/(arr.count*10 / i)
			Quick_Attach.pb1.value = precents
			gc()
			if (((maxVersion())[1] / 1000) >= 13) do windows.processPostedMessages() --��� ���� ���� �� �������
			if  (keyboard.EscPressed) and (queryBox "you want to abort the Quick_Attach?") then return b
		)
		if (SuperClassOf (arr[i]) == GeometryClass) and (IsValidNode (arr[i])) then (
			case Quick_Attach.rdo1.state of (
				1: polyop.attach b arr[i]
				2: meshop.attach b arr[i] attachMat:#IDToMat condenseMat:true deleteSourceNode:true
			)
		) else (
		if (Quick_Attach.chk1.checked) and (SuperClassOf (arr[i]) == Shape) and (arr[i].render_renderable) and (IsValidNode (arr[i])) do (
			arr[i].render_displayRenderMesh = true
			case Quick_Attach.rdo1.state of (
				1: polyop.attach b arr[i]
				2: meshop.attach b arr[i] attachMat:#IDToMat condenseMat:true deleteSourceNode:true
			)
		)
		)
	)
	if meshes.count > 1 do (
		b = meshes[1]
		for i = 2 to meshes.count do
			(
				case Quick_Attach.rdo1.state of (
					1: polyop.attach b meshes[i]
					2: meshop.attach b meshes[i] attachMat:#IDToMat condenseMat:true deleteSourceNode:true
				)
				precents = 1000/(meshes.count*10 / i)
				Quick_Attach.pb1.value = precents
				gc()
				if (((maxVersion())[1] / 1000) >= 13) do windows.processPostedMessages()
				if  (keyboard.EscPressed) and (queryBox "you want to abort the Quick_Attach?") then return b
			)
	)
	select b
	mymax = b.max
	mymin = b.min
	b.pivot = [(mymax.x+mymin.x)/2, (mymax.y+mymin.y)/2, (mymax.z+mymin.z)/2]
	messagebox ("Attach is done")
	Quick_Attach.pb1.value = 0
	free arr; free meshes;
	b
	) else messagebox ("select objects first")
)

rollout Quick_Attach "Quick Attach v1.71" width:177 height:405
(
	button bt_attach "Attach" pos:[38,163] width:96 height:29 toolTip:"all selected items will be combined to Editable poly"
	button bt_specify "Specify" pos:[42,278] width:96 height:19 toolTip:"Edit normals object to Specify"
	progressBar pb1 "" pos:[7,389] width:163 height:8
	label lbl1 "Selected objects:" pos:[8,8] width:144 height:16
	label lbl2 "0" pos:[8,24] width:144 height:16
	label lbl9 "To abort operation - hold Escape. You can not undo if selected more than objects in one part" pos:[7,198] width:162 height:54
	label lbl10 "Object to be converted to Editable poly" pos:[16,337] width:128 height:32
	checkbox chk1 "include renderable shapes" pos:[9,93] width:146 height:18 checked:false
	GroupBox grp1 "Normals" pos:[9,255] width:158 height:119
	button bt_reset "Reset" pos:[42,313] width:96 height:19 toolTip:"Reset normals"
	radiobuttons rdo1 "Create" pos:[24,41] width:90 height:46 labels:#("Editable Poly", "Editable Mesh") columns:1
	spinner spn1 "" pos:[6,116] width:62 height:16 enabled:true range:[1,10000,0] type:#integer
	label lbl11 "Objects in one part" pos:[72,116] width:101 height:17
	label lbl19 "reduce, if not enough memory" pos:[9,133] width:155 height:17
	on Quick_Attach open  do
	(	
		spn1.value = seq
	)
	on bt_attach pressed do
	(
		undo "Quick_Attach" on (
			b = attachAll()
		)
		lbl2.caption = selection.count as string
	)
	on bt_specify pressed do
	(
		if selection.count == 1 then (
		b = selection[1]
		if (SuperClassOf (b) == GeometryClass) then (
		undo "Quick_Attach" on (
		if (ClassOf (b) != Editable_Poly) do convertTo b Editable_Poly
		modPanel.addModToSelection (Edit_Normals ()) ui:on
		normcount = b.edit_normals.EditNormalsMod.GetNumNormals ()
		b.edit_normals.EditNormalsMod.SetSelection #{1..normcount}
		b.edit_normals.EditNormalsMod.Specify ()
		subobjectLevel = 0
		maxOps.CollapseNodeTo $ 1 true
		)
		) else messagebox ("Selection is not geometry")
		) else messagebox ("pleas select 1 object")
	)
	on bt_reset pressed do
	(
			if selection.count == 1 then (
		b = selection[1]
		if (SuperClassOf (b) == GeometryClass) then (
		undo "Quick_Attach" on (
		if (ClassOf (b) != Editable_Poly) do convertTo b Editable_Poly
		modPanel.addModToSelection (Edit_Normals ()) ui:on
		normcount = b.edit_normals.EditNormalsMod.GetNumNormals ()
		b.edit_normals.EditNormalsMod.SetSelection #{1..normcount}
		b.edit_normals.EditNormalsMod.Reset ()
		subobjectLevel = 0
		maxOps.CollapseNodeTo $ 1 true
		)
		) else messagebox ("Selection is not geometry")
		) else messagebox ("pleas select 1 object")
	)
)

if selection.count != 0 then (
	createDialog Quick_Attach;
	Quick_Attach.lbl2.caption = selection.count as string
	) else messagebox ("first select objects")
)

