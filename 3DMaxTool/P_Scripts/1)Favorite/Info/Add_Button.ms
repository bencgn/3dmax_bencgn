(
	local NTL=#()
	function add_button title shortcut across:0=
(
		append NTL #(title, shortcut, across)
	)

	--add_button "Pivot Fix" "" across:0
	--add_button "Pivot Center" "" across:1
	--add_button "Pivot B" "" across:2
	--add_button "Frozen_Gray" "" across:0
	add_button "View" "1" across:0
	add_button "Screen" "2" across:0
	add_button "Local" "3" across:0
	add_button "Parent" "4" across:0
	add_button "P_Center" "Q" across:0
	add_button "S_Center" "W" across:0
	--add_button "Box" "" across:1
	--add_button "Plane" "" across:2

	return NTL
)
