(
	local NTL=#()
	function add_button title shortcut across:0=
(
		append NTL #(title, shortcut, across)
	)

	add_button "Arc" "" across:0
	add_button "Refine" "R" across:0
	add_button "Type_To_Bazier" "1" across:0
	add_button "Type_To_Bazier_Corner" "2" across:0
	add_button "Type_To_Corner" "3" across:0
	add_button "Type_To_Smooth" "4" across:0
	add_button "Convert_Poly" "" across:0

	return NTL
)