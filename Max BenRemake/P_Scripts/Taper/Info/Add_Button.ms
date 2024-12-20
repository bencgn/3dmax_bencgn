(
	local NTL=#()
	function add_button title shortcut across:0=
(
		append NTL #(title, shortcut, across)
	)

	add_button "Amount" "" across:0
	add_button "Curve" "" across:0

	return NTL
)