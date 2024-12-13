(
	local NTL=#()
	function add_button title shortcut across:0=
(
		append NTL #(title, shortcut, across)
	)

	add_button "Symmetry" "W" across:undefined
	add_button "TurboSmooth" "T" across:undefined
	add_button "Edit_Poly" "E" across:undefined
	add_button "EditNormals" "N" across:undefined
	add_button "Shell" "H" across:undefined
	add_button "FFD_3x3x3" "F" across:undefined
	add_button "FFDBox" "" across:undefined
	add_button "Bend" "" across:undefined
	add_button "Extrude" "" across:undefined
	add_button "Taper" "" across:undefined
	add_button "Skin" "S" across:undefined
	add_button "Skin_Wrap" "" across:undefined
	add_button "Morpher" "M" across:undefined
	add_button "Uvwmap" "" across:undefined
	add_button "Unwrap_UVW" "U" across:undefined
	add_button "Optimize" "O" across:undefined
	add_button "PathDeform" "D" across:undefined
	add_button "Mirror" "" across:undefined
	add_button "Displace" "" across:undefined
	add_button "Lathe" "" across:undefined
	add_button "Vol__Select" "" across:undefined

	return NTL
)