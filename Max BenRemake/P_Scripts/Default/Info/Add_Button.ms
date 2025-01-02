(
	local NTL=#()
	function add_button title shortcut across:0=
(
		append NTL #(title, shortcut, across)
	)

	add_button "Move To Zero" "R" across:0
	add_button "SetState" "" across:1
	add_button "LoadState" "" across:2
	add_button "Freeze_Transform" "" across:1
	add_button "UnFreeze_Transfrom" "" across:2
	add_button "Turn CCW" "Z" across:1
	add_button "Turn CW" "X" across:2
	add_button "Frozen_Gray" "" across:1
	add_button "SelectInstances" "" across:2
	add_button "BackFaceCull" "" across:1
	add_button "ResetXForm" "" across:2
	add_button "DeleteAnim" "" across:0
	add_button "Delete" "" across:0
	add_button "EditPoly" "" across:0
	add_button "Convert_Poly" "" across:0

	return NTL
)