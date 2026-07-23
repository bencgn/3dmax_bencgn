/*
	BENCGN TOOLS
	------------
	- Nut dang dotNetControl (System.Windows.Forms.Button) de co the doi
	  mau khi hover chuot (xanh duong).
	- Sau khi bam bat ky nut nao thanh cong, dong chu "OK" hien len o
	  cuoi tool, tu dong bien mat sau 3 giay (dung timer rieng).
	- Toan bo LOGIC BEN TRONG (duong dan fileIn, ten macro, action ID...)
	  giu nguyen 100% so voi ban truoc, chi doi kieu nut + them hieu ung.
*/

dotNet.loadAssembly "System.Windows.Forms"
dotNet.loadAssembly "System.Drawing"

rollout rOSTools "Bencgn Tool Thao Tac Nhanh" rolledUp:false width:230
(
	------------------------------------------------------------------
	-- MAU SAC DUNG CHUNG CHO NUT (dotNet Color)
	------------------------------------------------------------------
	local colorBtnDefault = (dotNetClass "System.Drawing.Color").FromArgb 60 60 60
	local colorBtnHover 	= (dotNetClass "System.Drawing.Color").FromArgb 40 120 215
	local colorBtnText 	= (dotNetClass "System.Drawing.Color").White

	------------------------------------------------------------------
	-- HAM DUNG CHUNG: gan UVW Map (Box, kich thuoc sz) cho tung object
	-- trong selection - lam rieng tung object de tranh loi khi chon
	-- nhieu object cung luc ("Unknown property: modifiers in $selection")
	------------------------------------------------------------------
	fn applyUVWMap sz =
	(
		if selection.count > 0 then
		(
			-- modPanel.addModToSelection ton trong dung sub-object dang chon
			-- (VD: chi chon vai Face) - addModifier KHONG lam duoc dieu nay,
			-- no luon tu tat sub-object level va ap len ca object (theo tai
			-- lieu MAXScript chinh thuc cua Autodesk)
			modPanel.addModToSelection (Uvwmap ()) ui:on
			for obj in selection do
			(
				obj.modifiers[#UVW_Map].maptype = 4
				obj.modifiers[#UVW_Map].width = sz
				obj.modifiers[#UVW_Map].height = sz
				obj.modifiers[#UVW_Map].length = sz
			)
			true
		)
		else
		(
			messageBox "Chua chon object nao!"
			false
		)
	)

	------------------------------------------------------------------
	-- HOVER (xanh duong khi ruot chuot vao nut)
	------------------------------------------------------------------
	fn fnHoverEnter ctrl = ( ctrl.BackColor = colorBtnHover )
	fn fnHoverLeave ctrl = ( ctrl.BackColor = colorBtnDefault )

	------------------------------------------------------------------
	-- TIEU DE
	------------------------------------------------------------------
	label createdByLabel "Tool created by: bencgn" align:#center

	------------------------------------------------------------------
	-- NHOM 1: MESH / POLY TOOLS
	------------------------------------------------------------------
	label lblMesh "== MESH / POLY ==" align:#center color:(color 255 140 0)
	group "Mesh / Poly" (
		dotNetControl btConvertPoly 	"System.Windows.Forms.Button" width:100 height:20 across:2
		dotNetControl btClean 			"System.Windows.Forms.Button" width:100 height:20 across:2
		dotNetControl weld 			"System.Windows.Forms.Button" width:205 height:20 across:1
	)

	------------------------------------------------------------------
	-- NHOM 2: UV MAPPING
	------------------------------------------------------------------
	label lblUV "== UV MAPPING ==" align:#center color:(color 0 170 170)
	group "UV Mapping" (
		dotNetControl btUVMap11 	"System.Windows.Forms.Button" width:100 height:20 across:2
		dotNetControl btUVMap5m 	"System.Windows.Forms.Button" width:100 height:20 across:2
		dotNetControl btUVMap10m 	"System.Windows.Forms.Button" width:100 height:20 across:2
		dotNetControl btUVMap100m 	"System.Windows.Forms.Button" width:100 height:20 across:2
	)

	------------------------------------------------------------------
	-- NHOM 3: VIEWPORT & HIEN THI
	------------------------------------------------------------------
	label lblViewport "== VIEWPORT ==" align:#center color:(color 70 130 220)
	group "Viewport" (
		dotNetControl HideUnselected 	"System.Windows.Forms.Button" width:100 height:20 across:2
		dotNetControl UnhideAll 		"System.Windows.Forms.Button" width:100 height:20 across:2

		dotNetControl Deletex 			"System.Windows.Forms.Button" width:100 height:20 across:2
		dotNetControl btWireView 		"System.Windows.Forms.Button" width:100 height:20 across:2

		dotNetControl btDisplayDefault "System.Windows.Forms.Button" width:205 height:20 across:1
	)

	------------------------------------------------------------------
	-- NHOM 4: PIVOT & TRANSFORM
	------------------------------------------------------------------
	label lblPivot "== PIVOT / XFORM ==" align:#center color:(color 170 90 220)
	group "Pivot / Transform" (
		dotNetControl setPivot 	"System.Windows.Forms.Button" width:100 height:20 across:2
		dotNetControl Move000 	"System.Windows.Forms.Button" width:100 height:20 across:2
	)

	------------------------------------------------------------------
	-- NHOM 5: EXPORT
	------------------------------------------------------------------
	label lblExport "== EXPORT ==" align:#center color:(color 60 180 90)
	group "Export" (
		dotNetControl ExportSelect "System.Windows.Forms.Button" width:205 height:20 across:1
	)

	------------------------------------------------------------------
	-- DONG TRANG THAI (hien "OK" sau khi bam nut, tu tat sau 3s)
	------------------------------------------------------------------
	label lblStatus "" align:#center height:16 color:(color 60 200 90)
	timer tmrStatus interval:3000 active:false

	-- fn nay phai dat SAU khi lblStatus va tmrStatus da duoc khai bao o tren,
	-- neu khong se bi loi "Unknown property in undefined" vi MAXScript chua
	-- biet den 2 control nay tai thoi diem ham duoc dinh nghia
	fn flashStatus msg =
	(
		lblStatus.text = msg
		tmrStatus.active = false
		tmrStatus.active = true
	)

	on tmrStatus tick do
	(
		lblStatus.text = ""
		tmrStatus.active = false
	)

	------------------------------------------------------------------
	-- KHOI TAO GIAO DIEN: gan chu + mau mac dinh + hover cho tat ca nut
	------------------------------------------------------------------
	on rOSTools open do
	(
		local allBtns = #(
			#(btConvertPoly, 	"Convert Poly"), \
			#(btClean, 			"Clean Dead Face"), \
			#(weld, 			"Weld"), \
			#(btUVMap11, 		"UV Map 1m"), \
			#(btUVMap5m, 		"UV Map 5m"), \
			#(btUVMap10m, 		"UV Map 10m"), \
			#(btUVMap100m, 		"UV Map 100m"), \
			#(HideUnselected, 	"Hide Unselected"), \
			#(UnhideAll, 		"Unhide All"), \
			#(Deletex, 			"Delete"), \
			#(btWireView, 		"Wire View On/Off"), \
			#(btDisplayDefault, "DisplayDefault"), \
			#(setPivot, 		"Pivot Mode"), \
			#(Move000, 			"Move to Origin"), \
			#(ExportSelect, 	"Export Select") \
		)

		for pair in allBtns do
		(
			local b = pair[1]
			b.Text = pair[2]
			b.Font = dotNetObject "System.Drawing.Font" "Segoe UI" 7.5
			b.FlatStyle = (dotNetClass "System.Windows.Forms.FlatStyle").Flat
			b.FlatAppearance.BorderSize = 1
			b.UseVisualStyleBackColor = false
			b.BackColor = colorBtnDefault
			b.ForeColor = colorBtnText
		)
	)

	------------------------------------------------------------------
	-- HOVER: doi mau xanh khi ruot chuot vao nut, tra lai mau cu khi ra
	------------------------------------------------------------------
	on btConvertPoly MouseEnter arg do ( fnHoverEnter btConvertPoly )
	on btConvertPoly MouseLeave arg do ( fnHoverLeave btConvertPoly )

	on btClean MouseEnter arg do ( fnHoverEnter btClean )
	on btClean MouseLeave arg do ( fnHoverLeave btClean )

	on weld MouseEnter arg do ( fnHoverEnter weld )
	on weld MouseLeave arg do ( fnHoverLeave weld )

	on btUVMap11 MouseEnter arg do ( fnHoverEnter btUVMap11 )
	on btUVMap11 MouseLeave arg do ( fnHoverLeave btUVMap11 )

	on btUVMap5m MouseEnter arg do ( fnHoverEnter btUVMap5m )
	on btUVMap5m MouseLeave arg do ( fnHoverLeave btUVMap5m )

	on btUVMap10m MouseEnter arg do ( fnHoverEnter btUVMap10m )
	on btUVMap10m MouseLeave arg do ( fnHoverLeave btUVMap10m )

	on btUVMap100m MouseEnter arg do ( fnHoverEnter btUVMap100m )
	on btUVMap100m MouseLeave arg do ( fnHoverLeave btUVMap100m )

	on HideUnselected MouseEnter arg do ( fnHoverEnter HideUnselected )
	on HideUnselected MouseLeave arg do ( fnHoverLeave HideUnselected )

	on UnhideAll MouseEnter arg do ( fnHoverEnter UnhideAll )
	on UnhideAll MouseLeave arg do ( fnHoverLeave UnhideAll )

	on Deletex MouseEnter arg do ( fnHoverEnter Deletex )
	on Deletex MouseLeave arg do ( fnHoverLeave Deletex )

	on btWireView MouseEnter arg do ( fnHoverEnter btWireView )
	on btWireView MouseLeave arg do ( fnHoverLeave btWireView )

	on btDisplayDefault MouseEnter arg do ( fnHoverEnter btDisplayDefault )
	on btDisplayDefault MouseLeave arg do ( fnHoverLeave btDisplayDefault )

	on setPivot MouseEnter arg do ( fnHoverEnter setPivot )
	on setPivot MouseLeave arg do ( fnHoverLeave setPivot )

	on Move000 MouseEnter arg do ( fnHoverEnter Move000 )
	on Move000 MouseLeave arg do ( fnHoverLeave Move000 )

	on ExportSelect MouseEnter arg do ( fnHoverEnter ExportSelect )
	on ExportSelect MouseLeave arg do ( fnHoverLeave ExportSelect )

	------------------------------------------------------------------
	-- HANDLERS: MESH / POLY TOOLS
	------------------------------------------------------------------
	on btConvertPoly Click do
	(
		macros.run "Modifier Stack" "Convert_to_Poly"
		flashStatus "OK"
	)

	-- btClean: chua duoc gan lenh trong file goc, de trong cho ban gan sau
	on btClean Click do
	(
	)

	on weld Click do
	(
		$.weldThreshold = 0.001
		$.EditablePoly.weldFlaggedVertices ()
		flashStatus "OK"
	)

	------------------------------------------------------------------
	-- HANDLERS: UV MAPPING
	------------------------------------------------------------------
	on btUVMap11 Click do
	(
		if applyUVWMap 1 do flashStatus "OK"
	)

	on btUVMap5m Click do
	(
		if applyUVWMap 5 do flashStatus "OK"
	)

	on btUVMap10m Click do
	(
		if applyUVWMap 10 do flashStatus "OK"
	)

	on btUVMap100m Click do
	(
		if applyUVWMap 100 do flashStatus "OK"
	)

	------------------------------------------------------------------
	-- HANDLERS: VIEWPORT & HIEN THI
	------------------------------------------------------------------
	on HideUnselected Click do
	(
		actionMan.executeAction 0 "281"  -- Tools: Hide Unselected
		flashStatus "OK"
	)

	on UnhideAll Click do
	(
		actionMan.executeAction 0 "277"  -- Tools: Unhide All
		flashStatus "OK"
	)

	on Deletex Click do
	(
		actionMan.executeAction 0 "40020"  -- Edit: Delete Objects
		flashStatus "OK"
	)

	-- btWireView: bat/tat Visibility (0-1) cho (cac) object dang chon
	-- Tuong duong voi: chuot phai object > Object Properties > Rendering Control > Visibility
	on btWireView Click do
	(
		if selection.count > 0 then
		(
			for obj in selection do
			(
				if obj.visibility == 0 then obj.visibility = 1 else obj.visibility = 0
			)
			flashStatus "OK"
		)
		else
		(
			messageBox "Chua chon object nao!"
		)
	)

	-- btDisplayDefault: dat lai Object Properties > Display Properties cho
	-- (cac) object dang chon: BAT "Backface Cull" + "Edges Only", TAT tat ca
	-- cac muc con lai (See-Through, Display as Box, Vertex Ticks, Motion Path,
	-- Ignore Extents, Show Frozen in Gray, Vertex Channel Display)
	on btDisplayDefault Click do
	(
		if selection.count > 0 then
		(
			for obj in selection do
			(
				obj.xray = false
				obj.boxMode = false
				obj.backFaceCull = true
				obj.allEdges = false
				obj.vertexTicks = false
				obj.showTrajectory = false
				obj.ignoreExtents = false
				obj.showFrozenInGray = false
				obj.showVertexColors = false
				obj.neverDegrade = false
			)
			flashStatus "OK"
		)
		else
		(
			messageBox "Chua chon object nao!"
		)
	)

	------------------------------------------------------------------
	-- HANDLERS: PIVOT & TRANSFORM
	------------------------------------------------------------------
	on setPivot Click do
	(
		macros.run "Tools" "PivotMode_Toggle"
		flashStatus "OK"
	)

	on Move000 Click do
	(
		-- Get the selected objects
		local selectedObjects = getCurrentSelection()

		-- Check if any objects are selected
		if selectedObjects.count > 0 then
		(
			-- Move each selected object to the world origin
			for obj in selectedObjects do
			(
				obj.position = [0,0,0]
			)
			-- Deselect the objects after moving
			clearSelection()
			flashStatus "OK"
		)
		else
		(
			messageBox "Chua chon object nao!"
		)
	)

	------------------------------------------------------------------
	-- HANDLERS: EXPORT
	------------------------------------------------------------------
	on ExportSelect Click do
	(
		move $ [0,0,0]
		select $
		actionMan.executeAction 0 "40373"  -- File: Export Selected
		flashStatus "OK"
	)
)

createDialog rOSTools
