
-- Overlap Face Finder v1.1
-- Finds faces that sit on top of each other (same vertex positions)
-- Supports both Editable Poly and Editable Mesh objects
-- Based on concepts from Colin Senner's Find CoInstances script

fn quantizePoint p tol =
(
	-- Snap a point to a tolerance grid so nearly-equal verts compare equal
	point3 (floor ((p.x / tol) + 0.5) * tol) (floor ((p.y / tol) + 0.5) * tol) (floor ((p.z / tol) + 0.5) * tol)
)

fn comparePoint3 a b =
(
	if a.x != b.x then (a.x < b.x)
	else if a.y != b.y then (a.y < b.y)
	else (a.z < b.z)
)

fn faceKey positions tol includeFlip:true =
(
	local pts = for p in positions collect quantizePoint p tol

	-- Build a stable key that ignores face winding when includeFlip is true
	if includeFlip do
	(
		qsort pts comparePoint3
	)

	local str = ""
	for p in pts do str += (p as string)
	str
)

fn collectOverlapFacesPoly obj tol includeFlip:true returnOnlyDupes:false =
(
	if (classof obj != Editable_Poly) do return #{}

	local faceCount = polyop.getNumFaces obj
	local keyMap = dotNetObject "System.Collections.Generic.Dictionary`2[System.String,System.Collections.Generic.List`1[System.Int32]]"

	for f = 1 to faceCount do
	(
		local verts = polyop.getFaceVerts obj f
		local positions = for v in verts collect (polyop.getVert obj v)
		local key = faceKey positions tol includeFlip:includeFlip

		if (not keyMap.ContainsKey key) do
			keyMap.Add key (dotNetObject "System.Collections.Generic.List`1[System.Int32]")
		keyMap.Item[key].Add f
	)

	local overlaps = #{}
	for key in keyMap.Keys do
	(
		local faceList = keyMap.Item[key]
		if faceList.Count > 1 do
		(
			if returnOnlyDupes then
			(
				-- Skip the first face (original), only select duplicates
				for i = 1 to faceList.Count - 1 do overlaps[faceList.Item[i]] = true
			)
			else
			(
				-- Select all faces including the original
				for i = 0 to faceList.Count - 1 do overlaps[faceList.Item[i]] = true
			)
		)
	)

	overlaps
)

fn collectOverlapFacesMesh obj tol includeFlip:true returnOnlyDupes:false =
(
	if (classof obj != Editable_Mesh) do return #{}

	local faceCount = obj.numFaces
	local keyMap = dotNetObject "System.Collections.Generic.Dictionary`2[System.String,System.Collections.Generic.List`1[System.Int32]]"

	for f = 1 to faceCount do
	(
		local face = getFace obj f
		local positions = #()
		append positions (getVert obj face.x)
		append positions (getVert obj face.y)
		append positions (getVert obj face.z)
		
		local key = faceKey positions tol includeFlip:includeFlip

		if (not keyMap.ContainsKey key) do
			keyMap.Add key (dotNetObject "System.Collections.Generic.List`1[System.Int32]")
		keyMap.Item[key].Add f
	)

	local overlaps = #{}
	for key in keyMap.Keys do
	(
		local faceList = keyMap.Item[key]
		if faceList.Count > 1 do
		(
			if returnOnlyDupes then
			(
				-- Skip the first face (original), only select duplicates
				for i = 1 to faceList.Count - 1 do overlaps[faceList.Item[i]] = true
			)
			else
			(
				-- Select all faces including the original
				for i = 0 to faceList.Count - 1 do overlaps[faceList.Item[i]] = true
			)
		)
	)

	overlaps
)

rollout overlapRoll "Overlap Face Finder v1.1" width:260
(
	dropDownList ddlMode "Selection Mode:" items:#("Select All Overlaps", "Select Only Duplicates") selection:1 width:240
	spinner spnTol "Position tolerance:" range:[0.0001,10.0,0.001] scale:0.001 type:#float fieldwidth:60 align:#right
	checkbox chkFlip "Treat flipped faces as overlap" checked:true
	button btnRun "Find Overlapping Faces" width:200 height:30
	button btnHelp "?" width:30 height:24 align:#right offset:[0,-34]
	label lblStatus "" width:240

	on btnHelp pressed do
	(
		local txt = ""
		txt += "Overlap Face Finder v1.1 - Help\n\n"
		txt += "This tool finds faces that are overlapping (same vertex positions).\n\n"
		txt += "SELECTION MODES:\n"
		txt += "  • Select All Overlaps - Selects all faces involved in overlaps\n"
		txt += "    (includes both originals and duplicates)\n\n"
		txt += "  • Select Only Duplicates - Selects only duplicate faces\n"
		txt += "    (excludes the first instance of each overlap group)\n\n"
		txt += "SETTINGS:\n"
		txt += "  • Position tolerance - How close vertices must be to be\n"
		txt += "    considered identical (lower = more strict)\n\n"
		txt += "  • Treat flipped faces as overlap - When checked, faces with\n"
		txt += "    reversed vertex order are still considered overlapping\n\n"
		txt += "SUPPORTED OBJECTS:\n"
		txt += "  • Editable Poly\n"
		txt += "  • Editable Mesh\n"
		messageBox txt title:"Help" beep:false
	)

	on btnRun pressed do
	(
		if selection.count == 0 then
		(
			lblStatus.text = "Please select objects first."
			return()
		)

		local totalFound = 0
		local returnOnlyDupes = (ddlMode.selection == 2)
		
		for obj in selection do
		(
			local overlaps = #{}
			local objType = classof obj
			
			if objType == Editable_Poly then
			(
				overlaps = collectOverlapFacesPoly obj spnTol.value includeFlip:chkFlip.checked returnOnlyDupes:returnOnlyDupes
			)
			else if objType == Editable_Mesh then
			(
				overlaps = collectOverlapFacesMesh obj spnTol.value includeFlip:chkFlip.checked returnOnlyDupes:returnOnlyDupes
			)
			else
			(
				format "% is not Editable Poly or Mesh. Skipping.\n" obj.name
				continue
			)

			if overlaps.numberSet > 0 then
			(
				if objType == Editable_Poly then
					polyop.setFaceSelection obj overlaps
				else
					setFaceSelection obj overlaps
				
				setCommandPanelTaskMode #modify
				max modify mode
				subobjectLevel = 4
				select obj

				format "%: found % overlapping faces.\n" obj.name overlaps.numberSet
				totalFound += overlaps.numberSet
			)
			else
			(
				format "%: no overlapping faces found.\n" obj.name
			)
		)

		lblStatus.text = if totalFound > 0 then
			("Selected " + totalFound as string + " faces.")
		else "No overlaps found."
	)
)

try (destroyDialog overlapRoll) catch()
createDialog overlapRoll
