(
	local NTL=#()
	function add_button title shortcut across:0=
(
		append NTL #(title, shortcut, across)
	)

	add_button "Push Value" "" across:0

	return NTL
)