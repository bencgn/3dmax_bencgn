(
	local NTL=#()
	function add_button title shortcut across:0=
(
		append NTL #(title, shortcut, across)
	)

	add_button "Angle" "" across:0
	add_button "Direction" "" across:0
	add_button "Set_X" "A" across:0
	add_button "Set_Y" "S" across:0
	add_button "Set_Z" "D" across:0

	return NTL
)