(
	local NTL=#()
	function add_button title shortcut across:0=
	(
		append NTL #(title, shortcut, across)
	)



	add_button "Select Loop" "Q"
	add_button "Bone Picker"  "E"
	add_button "Shrink" "A" across:1 
	add_button "Grow" "S"  across:2 
	add_button "Loop" "1" across:1
	add_button "Ring" "2" across:2 
	add_button "Copy" "C" across:1
	add_button "Paste" "V" across:2
	add_button "Skin Weigth Absolute" "D"
	add_button  "Skin Weigth Relative" "F"
	add_button "Remove Zero Weight" "R"
	add_button "Skin Mirror" "W"
	add_button "Paint Weight" "Z"
	add_button "Weight Dialog" "P"


	return NTL
)