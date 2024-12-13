(
	local NTL=#()
	function add_button title shortcut across:0=
(
		append NTL #(title, shortcut, across)
	)

	add_button "Figure" "T" across:1
	add_button "Pose" "P" across:2
	add_button "Select Head" "1" across:0
	add_button "Select All Spine" "W" across:0
	add_button "Right Hand" "" across:1
	add_button "Left Hand" "" across:2
	add_button "Select Right Finger" "Q" across:1
	add_button "Select Left Finger" "E" across:2
	add_button "Right Foot" "" across:1
	add_button "Left Foot" "" across:2
	add_button "Select COM" "" across:0
	add_button "Turn CCW" "Z" across:1
	add_button "Turn CW" "X" across:2
	add_button "SetKey" "" across:1
	add_button "SetPlantedKey" "" across:2
	add_button "Delete_AniKey" "" across:0

	return NTL
)