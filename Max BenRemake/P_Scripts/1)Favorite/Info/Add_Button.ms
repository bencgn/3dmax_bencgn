(
	local NTL=#()
	function add_button title shortcut across:0=
(
		append NTL #(title, shortcut, across)
	)

	add_button "View" "1" across:0
	add_button "Screen" "2" across:0
	add_button "Local" "3" across:0
	add_button "Parent" "4" across:0
	add_button "P_Center" "Q" across:0
	add_button "S_Center" "W" across:0
	add_button "Convert_Poly" "" across:0

	return NTL
)