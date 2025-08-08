(
	local NTL=#()
	function add_button title shortcut across:0=
(
		append NTL #(title, shortcut, across)
	)

	add_button "HideSelected" "H" across:1
	add_button "HideUnSelected" "G" across:2
	add_button "UnhideAll" "F" across:1
	add_button "Select Loop" "Q" across:3
	add_button "Shrink" "A" across:1
	add_button "Grow" "S" across:2
	add_button "Select Same Normal" "W" across:1
	add_button "Similar" "E" across:2
	add_button "Select_outedge" "" across:1
	add_button "DotRing" "3" across:2
	add_button "Center Loop" "4" across:1
	add_button "Select_Element" "" across:3
	add_button "Turn CCW" "Z" across:1
	add_button "Turn CW" "X" across:2
	add_button "WireFrameMat" "" across:0
	add_button "ColorMat" "" across:0
	add_button "IgnoreBackfacing" "" across:0
	add_button "PolyShiftMove" "B" across:0
	add_button "ResetXform" "" across:0
	add_button "Delete" "" across:0
	add_button "Move To Zero" "" across:0
	add_button "Convert_Poly" "" across:0
	add_button "NormalEdit" "" across:0

	return NTL
)