(
	local NTL=#()
	function add_button title shortcut across:0=
(
		append NTL #(title, shortcut, across)
	)

	add_button "Dummy" "" across:0
	add_button "Import" "" across:0
	add_button "Export_Batch" "" across:0
	add_button "StandardMTL" "" across:0
	add_button "AssemblyTool" "" across:0
	add_button "SelectBone" "" across:0
	add_button "SelectAll_Filter" "" across:0
	add_button "SelectShape" "" across:0
	add_button "3DMax24_Final_BenHayDung" "" across:0

	return NTL
)