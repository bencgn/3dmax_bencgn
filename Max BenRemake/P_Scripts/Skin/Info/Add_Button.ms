(
	local NTL=#()
	function add_button title shortcut across:0=
(
		append NTL #(title, shortcut, across)
	)

	add_button "Select Loop" "Q" across:0
	add_button "Bone Picker" "E" across:0
	add_button "Shrink" "A" across:1
	add_button "Grow" "S" across:2
	add_button "Loop" "1" across:1
	add_button "Ring" "2" across:2
	add_button "Copy" "C" across:1
	add_button "Paste" "V" across:2
	add_button "Skin Weigth Absolute" "D" across:0
	add_button "Skin Weigth Relative" "F" across:0
	add_button "Remove Zero Weight" "R" across:0
	add_button "Skin Mirror" "W" across:0
	add_button "Paint Weight" "Z" across:0
	add_button "Weight Dialog" "P" across:0
	add_button "Convert_Poly" "" across:0
	add_button "AssemblyTool" "" across:0

	return NTL
)