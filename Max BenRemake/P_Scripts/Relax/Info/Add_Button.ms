(
	local NTL=#()
	function add_button title shortcut across:0=
(
		append NTL #(title, shortcut, across)
	)

	add_button "Relax Value" "" across:0
	add_button "Iterations" "" across:0
	add_button "Convert_Poly" "" across:0

	return NTL
)