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

	-- MAU RIENG CHO NHOM DW PIPELINE (vang gold)
	local colorDWDefault = (dotNetClass "System.Drawing.Color").FromArgb 180 140 20
	local colorDWHover	 = (dotNetClass "System.Drawing.Color").FromArgb 230 190 40
	local colorDWText	 = (dotNetClass "System.Drawing.Color").Black

	-- MAU RIENG CHO NUT DELETE (do)
	local colorDelDefault = (dotNetClass "System.Drawing.Color").FromArgb 170 40 40
	local colorDelHover	  = (dotNetClass "System.Drawing.Color").FromArgb 220 60 60

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

	-- Hover rieng cho DW pipeline (vang gold)
	fn fnDWHoverEnter ctrl = ( ctrl.BackColor = colorDWHover )
	fn fnDWHoverLeave ctrl = ( ctrl.BackColor = colorDWDefault )

	-- Hover rieng cho nut Delete (do)
	fn fnDelHoverEnter ctrl = ( ctrl.BackColor = colorDelHover )
	fn fnDelHoverLeave ctrl = ( ctrl.BackColor = colorDelDefault )

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
		-- tunrPoly: nut va o nhap polygonsize tren cung mot dong, khong popup.
		dotNetControl btTunrPoly "System.Windows.Forms.Button" width:75 height:20 across:2 align:#left
		spinner spnPolygonSize "polygonsize" range:[3,1000,5] type:#integer scale:1 fieldWidth:45 width:125 align:#right offset:[0,1]
		dotNetControl weld 			"System.Windows.Forms.Button" width:205 height:20 across:1
		dotNetControl btCheckDouble "System.Windows.Forms.Button" width:205 height:20 across:1
		dotNetControl btSelNoneMesh "System.Windows.Forms.Button" width:205 height:20 across:1
		dotNetControl btRenamePart "System.Windows.Forms.Button" width:205 height:20 across:1
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
	-- NHOM 6: DW PIPELINE (THEM MOI - khong dung cham code cu)
	------------------------------------------------------------------
	label lblDW "== DW PIPELINE ==" align:#center color:(color 230 200 60)
	group "DW pipeline" (
		dotNetControl btHBName "System.Windows.Forms.Button" width:205 height:20 across:1
		dotNetControl btGLTFName "System.Windows.Forms.Button" width:205 height:20 across:1
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
			#(btTunrPoly, 		"tunrPoly"), \
			#(weld, 			"Weld"), \
			#(btCheckDouble, 	"Check Double Face"), \
			#(btSelNoneMesh, 	"Select None Mesh (0 tris)"), \
			#(btRenamePart, 	"Rename Part 1-xx"), \
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

		-- Override mau DO cho nut Delete (van giu Text/Font tu vong lap tren)
		Deletex.BackColor = colorDelDefault
		Deletex.ForeColor = colorBtnText

		-- STYLE RIENG CHO NUT DW PIPELINE (vang gold, chu den)
		btHBName.Text = "1 click name hb"
		btHBName.Font = dotNetObject "System.Drawing.Font" "Segoe UI" 7.5
		btHBName.FlatStyle = (dotNetClass "System.Windows.Forms.FlatStyle").Flat
		btHBName.FlatAppearance.BorderSize = 1
		btHBName.UseVisualStyleBackColor = false
		btHBName.BackColor = colorDWDefault
		btHBName.ForeColor = colorDWText

		btGLTFName.Text = "1 Click tao ten gltf"
		btGLTFName.Font = dotNetObject "System.Drawing.Font" "Segoe UI" 7.5
		btGLTFName.FlatStyle = (dotNetClass "System.Windows.Forms.FlatStyle").Flat
		btGLTFName.FlatAppearance.BorderSize = 1
		btGLTFName.UseVisualStyleBackColor = false
		btGLTFName.BackColor = colorDWDefault
		btGLTFName.ForeColor = colorDWText
	)

	------------------------------------------------------------------
	-- HOVER: doi mau xanh khi ruot chuot vao nut, tra lai mau cu khi ra
	------------------------------------------------------------------
	on btConvertPoly MouseEnter arg do ( fnHoverEnter btConvertPoly )
	on btConvertPoly MouseLeave arg do ( fnHoverLeave btConvertPoly )

	on btClean MouseEnter arg do ( fnHoverEnter btClean )
	on btClean MouseLeave arg do ( fnHoverLeave btClean )

	on btTunrPoly MouseEnter arg do ( fnHoverEnter btTunrPoly )
	on btTunrPoly MouseLeave arg do ( fnHoverLeave btTunrPoly )

	on weld MouseEnter arg do ( fnHoverEnter weld )
	on weld MouseLeave arg do ( fnHoverLeave weld )

	on btCheckDouble MouseEnter arg do ( fnHoverEnter btCheckDouble )
	on btCheckDouble MouseLeave arg do ( fnHoverLeave btCheckDouble )

	on btSelNoneMesh MouseEnter arg do ( fnHoverEnter btSelNoneMesh )
	on btSelNoneMesh MouseLeave arg do ( fnHoverLeave btSelNoneMesh )

	on btRenamePart MouseEnter arg do ( fnHoverEnter btRenamePart )
	on btRenamePart MouseLeave arg do ( fnHoverLeave btRenamePart )

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

	on Deletex MouseEnter arg do ( fnDelHoverEnter Deletex )
	on Deletex MouseLeave arg do ( fnDelHoverLeave Deletex )

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

	on btHBName MouseEnter arg do ( fnDWHoverEnter btHBName )
	on btHBName MouseLeave arg do ( fnDWHoverLeave btHBName )

	on btGLTFName MouseEnter arg do ( fnDWHoverEnter btGLTFName )
	on btGLTFName MouseLeave arg do ( fnDWHoverLeave btGLTFName )

	------------------------------------------------------------------
	-- HANDLERS: MESH / POLY TOOLS
	------------------------------------------------------------------
	on btConvertPoly Click do
	(
		macros.run "Modifier Stack" "Convert_to_Poly"
		flashStatus "OK"
	)

	------------------------------------------------------------------
	-- tunrPoly: them Turn_to_Poly theo polygonsize (mac dinh 5).
	-- Moi lan bam them mot modifier MOI; khong collapse / sua modifier cu.
	-- Dung truc tiep modifier moi, khong dung $.modifiers khi chon nhieu.
	-- Chi bao trang thai trong tool / Listener, KHONG mo hop thoai.
	------------------------------------------------------------------
	on btTunrPoly Click do
	(
		if selection.count == 0 then
		(
			flashStatus "Chua chon object nao!"
		)
		else
		(
			try
			(
				max modify mode
				if (modPanel.validModifier Turn_to_Poly) then
				(
					local polySize = spnPolygonSize.value as integer
					undo "tunrPoly" on
					(
						local turnMod = Turn_to_Poly ()
						turnMod.limitPolySize = on
						turnMod.maxPolySize = polySize
						modPanel.addModToSelection turnMod ui:on
					)
					flashStatus ("tunrPoly OK | size " + (polySize as string))
				)
				else
				(
					flashStatus "Chon Mesh/Poly hop le"
				)
			)
			catch
			(
				local err = getCurrentException()
				flashStatus "Loi tunrPoly - xem Listener"
				format "tunrPoly: %\n" err
			)
		)
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
	-- btCheckDouble: quet 1 object, tim cac face bi chong len nhau
	-- (cung tam face - la nguyen nhan gay chop / z-fighting) va chon
	-- chung o sub-object Polygon de nguoi dung xu ly.
	-- Ho tro Editable Poly va Editable Mesh. Sai loai -> bam Convert Poly.
	-- Dung sai so 0.01 don vi (round toa do * 100).
	------------------------------------------------------------------
	on btCheckDouble Click do
	(
		if selection.count != 1 then
		(
			messageBox "Hay chon dung 1 object de kiem tra!"
		)
		else
		(
			local obj = selection[1]

			-- Ham tao key tu tam face (lam tron 0.01 don vi)
			-- Luu y: MAXScript KHONG co ham round -> tu lam tron bang floor(x+0.5)
			fn dfKey c =
			(
				((((floor (c.x * 100 + 0.5)) as integer) as string)) + "_" + \
				((((floor (c.y * 100 + 0.5)) as integer) as string)) + "_" + \
				((((floor (c.z * 100 + 0.5)) as integer) as string))
			)

			if (classof obj == Editable_Poly) then
			(
				local nf = polyop.getNumFaces obj
				local ht = dotNetObject "System.Collections.Hashtable"
				local keys = #()
				for i = 1 to nf do
				(
					local k = dfKey (polyop.getFaceCenter obj i)
					append keys k
					if (ht.ContainsKey k) then ht.set_Item k ((ht.get_Item k) + 1)
					else ht.Add k 1
				)
				local selFaces = #{}
				for i = 1 to nf do ( if ((ht.get_Item keys[i]) > 1) do selFaces[i] = true )

				max modify mode
				modPanel.setCurrentObject obj.baseObject
				subobjectLevel = 4  -- Polygon
				polyop.setFaceSelection obj selFaces
				redrawViews()

				if selFaces.numberSet > 0 then
					flashStatus ("Double: " + selFaces.numberSet as string + " face")
				else
					flashStatus "Khong co double face"
			)
			else if (classof obj == Editable_Mesh) then
			(
				local nf = getNumFaces obj
				local ht = dotNetObject "System.Collections.Hashtable"
				local keys = #()
				for i = 1 to nf do
				(
					local k = dfKey (getFaceCenter obj i)
					append keys k
					if (ht.ContainsKey k) then ht.set_Item k ((ht.get_Item k) + 1)
					else ht.Add k 1
				)
				local selFaces = #{}
				for i = 1 to nf do ( if ((ht.get_Item keys[i]) > 1) do selFaces[i] = true )

				max modify mode
				modPanel.setCurrentObject obj.baseObject
				subobjectLevel = 3  -- Face (Editable Mesh)
				obj.selectedFaces = selFaces
				redrawViews()

				if selFaces.numberSet > 0 then
					flashStatus ("Double: " + selFaces.numberSet as string + " face")
				else
					flashStatus "Khong co double face"
			)
			else
			(
				messageBox "Object phai la Editable Poly hoac Editable Mesh.\nHay bam Convert Poly truoc."
			)
		)
	)

	------------------------------------------------------------------
	-- btSelNoneMesh: quet TOAN BO scene, tim cac object GEOMETRY co
	-- 0 face (mesh rong / khong co gi) va CHON chung lai de nguoi dung
	-- tu quyet dinh xoa. Chi chon geometry - KHONG dung cham Dummy,
	-- Camera, Light, Spline (vi chung khong phai GeometryClass).
	--
	-- Cach dem face an toan cho tung loai:
	--   Editable_Poly -> polyop.getNumFaces
	--   Editable_Mesh -> getNumFaces
	--   Con lai (primitive, co modifier...) -> obj.mesh.numfaces
	--     (.mesh tra ve TriMesh da ap modifier, KHONG pha huy object goc)
	-- Boc try...catch: object nao loi khi doc mesh thi BO QUA (khong chon)
	-- de tranh chon nham.
	------------------------------------------------------------------
	on btSelNoneMesh Click do
	(
		local emptyObjs = #()
		for obj in objects do
		(
			if (superclassof obj == GeometryClass) then
			(
				local nf = -1
				try
				(
					case (classof obj) of
					(
						Editable_Poly: nf = polyop.getNumFaces obj
						Editable_Mesh: nf = getNumFaces obj
						default: nf = obj.mesh.numfaces
					)
				)
				catch ( nf = -1 )

				if nf == 0 then append emptyObjs obj
			)
		)

		if emptyObjs.count > 0 then
		(
			clearSelection()
			select emptyObjs
			flashStatus ("0 tris: chon " + emptyObjs.count as string + " obj")
		)
		else
		(
			clearSelection()
			flashStatus "Khong co object rong"
		)
	)

	------------------------------------------------------------------
	-- btRenamePart: doi ten cac object DANG CHON thanh part_01, part_02,
	-- part_03 ... theo thu tu tang dan. Chon 1 -> part_01. Chon nhieu ->
	-- danh so len tu 01. Padding toi thieu 2 chu so ("02d"): 01..09, 10,
	-- 11 ... 99, 100, 101 ... (tu 100 tro len tu dong dung 3 chu so).
	-- Boc undo de Ctrl+Z hoan tac 1 lan.
	------------------------------------------------------------------
	on btRenamePart Click do
	(
		if selection.count > 0 then
		(
			undo "rename part" on
			(
				local i = 1
				for obj in selection do
				(
					obj.name = "part_" + (formattedPrint i format:"02d")
					i += 1
				)
			)
			flashStatus ("Rename " + selection.count as string + " part")
		)
		else
		(
			messageBox "Chua chon object nao!"
		)
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

	------------------------------------------------------------------
	-- HANDLERS: DW PIPELINE (THEM MOI)
	-- btHBName: hoi so tang, tao bo dummy hb tai goc toa do [0,0,0]:
	--   Ground, Ground_Lower, Ground_Upper, Level_01 ... Level_NN
	------------------------------------------------------------------
	on btHBName Click do
	(
		-- Hop thoai nho hoi so tang (modal, co spinner)
		local rlDW = rollout rlDWAskLevels "DW pipeline" width:180
		(
			spinner spnLevels "So tang:" range:[1,200,8] type:#integer fieldWidth:60 align:#center
			button btnDWOK "OK" width:80 height:24 align:#center
			local result = 0
			on btnDWOK pressed do
			(
				rlDWAskLevels.result = spnLevels.value
				destroyDialog rlDWAskLevels
			)
		)
		createDialog rlDW modal:true

		local numLevels = rlDW.result
		if numLevels > 0 then
		(
			undo "1 click name hb" on
			(
				-- Danh sach ten can tao
				local hbNames = #("Ground", "Ground_Lower", "Ground_Upper")
				for i = 1 to numLevels do
					append hbNames ("Level_" + (formattedPrint i format:"02d"))

				local madeCount = 0
				for n in hbNames do
				(
					-- Tranh trung: neu da co object cung ten thi bo qua
					if (getNodeByName n) == undefined then
					(
						local d = Dummy name:n pos:[0,0,0]
						madeCount += 1
					)
				)
				flashStatus ("OK - " + madeCount as string + " dummy")
			)
		)
	)

	------------------------------------------------------------------
	-- btGLTFName: hoi ten du an, tao bo dummy hau to gltf tai goc [0,0,0]:
	--   <ten>_3dassets, _building, _ghosted, _hb, _map, _map, _tree2D
	------------------------------------------------------------------
	on btGLTFName Click do
	(
		-- Hop thoai nho hoi ten du an (modal)
		local rlGL = rollout rlGLAskName "DW pipeline" width:220
		(
			edittext txtProj "Ten du an:" fieldWidth:130 align:#center
			button btnGLOK "OK" width:80 height:24 align:#center
			local result = ""
			on btnGLOK pressed do
			(
				rlGLAskName.result = (trimLeft (trimRight txtProj.text) )
				destroyDialog rlGLAskName
			)
		)
		createDialog rlGL modal:true

		local projName = rlGL.result
		if projName != undefined and projName != "" then
		(
			undo "1 Click tao ten gltf" on
			(
				-- Hau to theo dung thu tu trong anh (co 2 _map)
				local suffixes = #("_3dassets", "_building", "_ghosted", "_hb", "_map", "_map", "_tree2D")

				local madeCount = 0
				for s in suffixes do
				(
					local d = Dummy name:(projName + s) pos:[0,0,0]
					madeCount += 1
				)
				flashStatus ("OK - " + madeCount as string + " dummy")
			)
		)
		else
		(
			if projName == "" then messageBox "Chua nhap ten du an!"
		)
	)
)

createDialog rOSTools
