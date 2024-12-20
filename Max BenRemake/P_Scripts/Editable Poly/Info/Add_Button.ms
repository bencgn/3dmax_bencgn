(
	local NTL=#()
	function add_button title shortcut across:0=
(
		append NTL #(title, shortcut, across)
	)

	add_button "Select Loop" "Q" across:0
	add_button "Shrink" "A" across:1
	add_button "Grow" "S" across:2
	add_button "Select Same Normal" "W" across:1
	add_button "Fill" "F" across:2
	add_button "Similar" "E" across:1
	add_button "Select_outedge" "" across:2
	add_button "Loop" "1" across:1
	add_button "Ring" "2" across:2
	add_button "DotRing" "3" across:1
	add_button "Center Loop" "4" across:2
	add_button "Select_Element" "" across:0
	add_button "Turn CCW" "Z" across:1
	add_button "Turn CW" "X" across:2
	add_button "IgnoreBackfacing" "" across:0
	add_button "PolyShiftMove" "B" across:0
	add_button "ResetXform" "" across:0

	return NTL
)