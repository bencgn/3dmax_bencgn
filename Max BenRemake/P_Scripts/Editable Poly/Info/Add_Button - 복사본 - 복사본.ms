(
	local NTL=#()
	function add_button title shortcut across:0=
(
		append NTL #(title, shortcut, across)
	)

	add_button "Select Loop" "Q" across:0
	add_button "Select Same Normal" "W" across:1
	add_button "Fill" "F" across:2
	add_button "Similar" "E" across:0
	add_button "Select_outedge" "" across:0
	add_button "Shrink" "A" across:1
	add_button "Grow" "S" across:2
	add_button "Loop" "1" across:1
	add_button "Ring" "2" across:2
	add_button "Autosmooth" "H" across:0
	add_button "Preserve UVs" "U" across:0

	return NTL
)