(
	local NTL=#()
	function add_button title shortcut across:0=
(
		append NTL #(title, shortcut, across)
	)

	add_button "Plane" "1" across:1
	add_button "Box" "2" across:2
	add_button "Cylinder" "3" across:1
	add_button "Sphere" "4" across:2
	add_button "Torus" "5" across:1
	add_button "Text" "T" across:2
	add_button "Omni" "L" across:1
	add_button "Camera" "C" across:2
	add_button "Point" "W" across:1
	add_button "Tape" "" across:2
	add_button "Line" "Q" across:1
	add_button "Biped" "0" across:2
	add_button "Bones" "9" across:1
	add_button "Circle" "C" across:2

	return NTL
)