(
	local NTL=#()
	function add_button title shortcut across:0=
(
		append NTL #(title, shortcut, across)
	)

	add_button "Inner Amount" "" across:0
	add_button "Outer Amount" "" across:0
	add_button "Segments" "" across:0

	return NTL
)