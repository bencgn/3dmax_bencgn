--------------------------------------------------------------------------------
-- CylinderSideReducer.ms
-- 3ds Max 2026 MaxScript
--
-- Muc dich: Trong 1 Editable_Poly co nhieu Element dang tru (cylinder, oc vit,
-- dinh tan, v.v...), tool nay se:
--   1. Lay danh sach cac Element (tu vung chon Element hien tai, hoac toan bo object)
--   2. Voi moi Element, "fit" mot truc hinh tru (cylinder axis) bang cach phan
--      tich cac vector phap tuyen mat (face normal) qua phep phan tich tri rieng
--      Jacobi cho ma tran 3x3 (khong phu thuoc ty le cao/rong cua tru, nen van
--      dung cho ca tru "map" lan tru "cao")
--   3. Tinh tam, ban kinh, chieu cao tu tap dinh cua Element
--   4. Dung mot Cylinder moi voi so canh (sides) do nguoi dung nhap (mac dinh 3),
--      dat dung vi tri/huong, roi Attach vao object goc
--   5. Sau khi da dung xong toan bo cylinder thay the, xoa mot lan cac mat cu
--
-- Cach dung:
--   - Chay file nay (Run Script) de mo dialog
--   - Bam "Chon Object" -> click chon object Editable_Poly chua cac element
--   - Vao Modify panel, xuong sub-object level "Element", chon 1 hoac nhieu
--     element can toi uu (giong hinh minh hoa ban gui)
--   - Chinh so "sides" mong muon (mac dinh 3)
--   - Bam nut OPTIMIZE
--------------------------------------------------------------------------------

(
	global CylinderSideReducerRollout

	try(destroyDialog CylinderSideReducerRollout) catch()

	rollout CylinderSideReducerRollout "Cylinder Side Reducer" width:280
	(
		local theObj = undefined

		group "Doi tuong"
		(
			pickbutton pbObj "Chon Object" width:250 align:#center
			label lblObjName "Chua chon object" align:#center
		)

		group "Thiet lap"
		(
			spinner spnSides "So canh (sides):" range:[3,64,3] type:#integer fieldWidth:50 align:#right
			checkbox chkAllElements "Xu ly TOAN BO Element (bo qua vung chon)" checked:false
			spinner spnMatID "Material ID danh dau:" range:[1,999,99] type:#integer fieldWidth:50 align:#right
			label lblMatIDHint "(dung de sau nay 'Chon lai' 1 phat)" align:#center
		)

		button btnRun "OPTIMIZE -> N SIDES" width:250 height:34 align:#center
		label lblStatus "" align:#center

		group "Chon lai"
		(
			button btnSelectOptimized "CHON CAC ELEMENT DA OPTIMIZE" width:250 height:28 align:#center
			label lblSelectStatus "" align:#center
		)

		----------------------------------------------------------------------
		-- Ham phu tro
		----------------------------------------------------------------------

		fn getObjectMatrixNoTrans obj = (
			local m = obj.transform
			m.row4 = [0,0,0]
			m
		)

		fn copyMat3rows m = #(#(m[1][1],m[1][2],m[1][3]), #(m[2][1],m[2][2],m[2][3]), #(m[3][1],m[3][2],m[3][3]))

		-- Phan tich tri rieng cho ma tran doi xung 3x3 (Jacobi eigenvalue algorithm)
		-- Tra ve #(eigenValues_array3, eigenVectors_array3_of_point3)
		fn jacobiEigen3 mat = (
			local a = copyMat3rows mat
			local v = #(#(1.0,0.0,0.0),#(0.0,1.0,0.0),#(0.0,0.0,1.0))
			for sweep = 1 to 60 do (
				local p = 1; local q = 2; local mx = abs a[1][2]
				if (abs a[1][3]) > mx do (p=1; q=3; mx = abs a[1][3])
				if (abs a[2][3]) > mx do (p=2; q=3; mx = abs a[2][3])
				if mx < 1e-10 do exit

				local app = a[p][p]; local aqq = a[q][q]; local apq = a[p][q]
				local phi = 0.5 * (atan2 (2*apq) (aqq - app))
				local c = cos phi; local s = sin phi
				local t1, t2

				for i = 1 to 3 do (
					t1 = a[i][p]; t2 = a[i][q]
					a[i][p] = c*t1 - s*t2
					a[i][q] = s*t1 + c*t2
				)
				for i = 1 to 3 do (
					t1 = a[p][i]; t2 = a[q][i]
					a[p][i] = c*t1 - s*t2
					a[q][i] = s*t1 + c*t2
				)
				for i = 1 to 3 do (
					t1 = v[i][p]; t2 = v[i][q]
					v[i][p] = c*t1 - s*t2
					v[i][q] = s*t1 + c*t2
				)
			)
			local eigVals = #(a[1][1], a[2][2], a[3][3])
			local eigVecs = #(
				point3 v[1][1] v[2][1] v[3][1],
				point3 v[1][2] v[2][2] v[3][2],
				point3 v[1][3] v[2][3] v[3][3]
			)
			#(eigVals, eigVecs)
		)

		-- Dung ma tran quay tu 1 vector truc Z cho truoc (thuat toan tu chon truc phu tro)
		fn buildMatrixFromZ zAxis = (
			zAxis = normalize zAxis
			local arbitrary = if (abs zAxis.x < 0.001 and abs zAxis.y < 0.001) then [1,0,0] else [0,0,1]
			local xAxis = normalize (cross arbitrary zAxis)
			local yAxis = normalize (cross zAxis xAxis)
			matrix3 xAxis yAxis zAxis [0,0,0]
		)

		-- Fit truc/tam/ban kinh/chieu cao cho 1 element (elemFaces la bitarray cac mat)
		fn fitAxisForElement obj elemFaces = (
			local faceArr = elemFaces as array
			if faceArr.count < 4 do return undefined

			local vertBits = polyop.getVertsUsingFace obj elemFaces
			local vertIdx = vertBits as array
			if vertIdx.count < 4 do return undefined

			-- Lay toa do dinh va phap tuyen mat TRUC TIEP o world space
			-- (tranh sai lech khi object co pivot / object-offset khac voi node transform)
			local pts = for vi in vertIdx collect (in coordsys world (polyop.getVert obj vi))
			local centroid = [0.0,0.0,0.0]
			for p in pts do centroid += p
			centroid /= pts.count

			-- Ma tran "tan xa" cua cac vector phap tuyen mat
			local M = #(#(0.0,0.0,0.0),#(0.0,0.0,0.0),#(0.0,0.0,0.0))
			for f in faceArr do (
				local n = normalize (in coordsys world (polyop.getFaceNormal obj f))
				M[1][1] += n.x*n.x; M[1][2] += n.x*n.y; M[1][3] += n.x*n.z
				M[2][1] += n.y*n.x; M[2][2] += n.y*n.y; M[2][3] += n.y*n.z
				M[3][1] += n.z*n.x; M[3][2] += n.z*n.y; M[3][3] += n.z*n.z
			)

			local res = jacobiEigen3 M
			local eigVals = res[1]
			local eigVecs = res[2]

			-- Truc hinh tru = vector rieng ung voi tri rieng NHO NHAT
			-- (vi da so mat ben co phap tuyen vuong goc voi truc, chi 2 mat nap moi
			--  co phap tuyen song song truc, nen do "tan xa" doc truc la nho nhat)
			local minIdx = 1
			if eigVals[2] < eigVals[minIdx] do minIdx = 2
			if eigVals[3] < eigVals[minIdx] do minIdx = 3
			local axis = normalize eigVecs[minIdx]

			local tMin = 1e9; local tMax = -1e9; local rMax = 0.0
			for p in pts do (
				local d = p - centroid
				local t = dot d axis
				if t < tMin do tMin = t
				if t > tMax do tMax = t
				local radial = d - axis*t
				local r = length radial
				if r > rMax do rMax = r
			)

			local height = tMax - tMin
			local center = centroid + axis*((tMin+tMax)/2.0)
			#(center, axis, rMax, height)
		)

		-- Dung cylinder N-canh thay the va attach vao object
		-- info[1]=tam (world), info[2]=truc (world), info[3]=ban kinh, info[4]=chieu cao
		fn buildReplacementCylinder obj info sides matID = (
			local centerWorld = info[1]; local dirWorld = normalize info[2]
			local radius = info[3]; local height = info[4]
			if height < 0.0001 or radius < 0.0001 do return false

			local cyl = Cylinder radius:radius height:height heightsegs:1 capsegs:1 sides:sides smooth:true slice:false
			local m = buildMatrixFromZ dirWorld
			m.row4 = centerWorld - dirWorld*(height/2.0)
			cyl.transform = m

			local facesBefore = polyop.getNumFaces obj
			polyop.attach obj cyl
			local facesAfter = polyop.getNumFaces obj

			-- Phan biet mat CAP (phap tuyen gan song song truc) va mat SIDE (vuong goc truc)
			-- de gan smoothing group rieng: side duoc smooth, cap thi khong smooth chung voi side
			local capFaces = #{}
			local sideFaces = #{}
			for nf = facesBefore+1 to facesAfter do (
				local n = normalize (in coordsys world (polyop.getFaceNormal obj nf))
				if (abs (dot n dirWorld)) > 0.7 then (
					capFaces[nf] = true
				) else (
					sideFaces[nf] = true
				)
			)
			if sideFaces.numberSet > 0 do polyop.setFaceSmoothGroup obj sideFaces 1
			if capFaces.numberSet > 0 do polyop.setFaceSmoothGroup obj capFaces 0

			-- Danh dau toan bo mat vua tao bang 1 Material ID rieng, de sau nay
			-- co the chon lai nhanh bang nut "CHON CAC ELEMENT DA OPTIMIZE"
			local allNewFaces = capFaces + sideFaces
			if allNewFaces.numberSet > 0 do polyop.setFaceMatID obj allNewFaces matID

			true
		)

		fn getAllElements obj = (
			local nFaces = polyop.getNumFaces obj
			local visited = #{}
			local elems = #()
			for f = 1 to nFaces do (
				if not visited[f] do (
					local ef = polyop.getElementsUsingFace obj #{f}
					append elems ef
					visited += ef
				)
			)
			elems
		)

		fn splitIntoElements obj faceBits = (
			local remaining = copy faceBits
			local elems = #()
			for f in (remaining as array) do (
				if remaining[f] do (
					local ef = (polyop.getElementsUsingFace obj #{f}) * faceBits
					append elems ef
					remaining -= ef
				)
			)
			elems
		)

		----------------------------------------------------------------------
		-- Su kien UI
		----------------------------------------------------------------------

		on pbObj picked p do (
			if p != undefined and (superclassof p == GeometryClass) then (
				theObj = p
				lblObjName.text = p.name
			)
		)

		on btnRun pressed do (
			if theObj == undefined or not isValidNode theObj do (
				messageBox "Hay bam 'Chon Object' va click chon object truoc." title:"Thieu Object"
				return()
			)

			local obj = theObj
			if classof obj != Editable_Poly do convertToPoly obj

			local sides = spnSides.value
			local elemsToProcess = #()

			if chkAllElements.checked then (
				elemsToProcess = getAllElements obj
			) else (
				local sel = polyop.getFaceSelection obj
				if sel.numberSet == 0 then (
					local goAll = queryBox "Khong co Element nao dang duoc chon (o sub-object Element).\nBan co muon xu ly TOAN BO object khong?" title:"Xac nhan"
					if goAll then elemsToProcess = getAllElements obj else return()
				) else (
					elemsToProcess = splitIntoElements obj sel
				)
			)

			if elemsToProcess.count == 0 do (
				messageBox "Khong tim thay Element nao de xu ly." title:"Khong co du lieu"
				return()
			)

			local facesBefore = polyop.getNumFaces obj
			local processed = 0

			undo "Optimize Cylinder Sides" on (
				disableSceneRedraw()
				local allOldFaces = #{}
				try (
					for ef in elemsToProcess do (
						local info = fitAxisForElement obj ef
						if info != undefined then (
							if buildReplacementCylinder obj info sides spnMatID.value then (
								allOldFaces += ef
								processed += 1
							)
						)
					)
					if allOldFaces.numberSet > 0 do polyop.deleteFaces obj allOldFaces
				) catch (
					format "CylinderSideReducer loi: %\n" (getCurrentException())
				)
				enableSceneRedraw()
			)
			completeRedraw()

			local facesAfter = polyop.getNumFaces obj
			lblStatus.text = ("Da xu ly " + processed as string + " element | Mat: " + facesBefore as string + " -> " + facesAfter as string)
		)

		on btnSelectOptimized pressed do (
			if theObj == undefined or not isValidNode theObj do (
				messageBox "Hay bam 'Chon Object' va click chon object truoc." title:"Thieu Object"
				return()
			)

			local obj = theObj
			if classof obj != Editable_Poly do convertToPoly obj

			local matID = spnMatID.value
			local bits = polyop.getFacesByMatID obj matID

			if bits.numberSet == 0 then (
				lblSelectStatus.text = ("Khong tim thay mat nao co Material ID " + matID as string)
			) else (
				max modify mode
				modPanel.setCurrentObject obj.baseObject
				subobjectLevel = 5 -- Element level cho Editable_Poly
				polyop.setFaceSelection obj bits
				completeRedraw()
				lblSelectStatus.text = ("Da chon " + bits.numberSet as string + " mat (Material ID " + matID as string + ")")
			)
		)
	)

	createDialog CylinderSideReducerRollout
)
