-- =====================================================================
--   STRAIGHTEN TOOL - Auto Align Rotated Mesh (Fix Xoay Vertex)
-- =====================================================================
--   Dùng cho object đã Reset Xform (Rotation node = 0,0,0) nhưng
--   geometry (vertex) vẫn còn bị nghiêng 1 góc bất kỳ trong không gian
--   (như trường hợp Object006 trong ảnh chụp 3ds Max).
--
--   Tool này KHÔNG xoay Transform của object (rotation vẫn giữ 0,0,0),
--   mà xoay trực tiếp toạ độ VERTEX trong local space để mesh thẳng
--   theo trục X/Y (giống kết quả ở ảnh 3).
--
--   CÁCH DÙNG:
--   1. Chọn object (Editable Poly hoặc có Edit Poly modifier ở top stack)
--   2. Vào Vertex sub-object mode
--   3. Chọn ĐÚNG 2 vertex nằm trên 1 cạnh mà bạn biết chắc phải thẳng
--      ngang hoặc thẳng dọc (ví dụ 1 đoạn tường dài)
--   4. Bấm "1. Lấy 2 Vertex Đang Chọn"
--   5. Chọn Pivot (tâm xoay) mong muốn
--   6. Bấm "2. XOAY THẲNG (Apply)"
-- =====================================================================

try(destroyDialog StraightenRollout) catch()

rollout StraightenRollout "Straighten Tool - Fix Xoay Object" width:300
(
    label lbl1 "Bước 1: Vào Editable Poly > Vertex" align:#left
    label lbl2 "Bước 2: Chọn 2 vertex nằm trên 1 cạnh" align:#left
    label lbl3 "        (cạnh đó phải thẳng ngang/dọc)" align:#left

    button btnGet "1. Lấy 2 Vertex Đang Chọn" width:280 height:30

    label lblAngle "Góc hiện tại: --"
    label lblTarget "Góc mục tiêu (gần nhất 90°): --"
    label lblDelta "Cần xoay: --"

    group "Tâm xoay (Pivot)"
    (
        radioButtons rdoPivot labels:#("Tâm Object (Pivot thật - đứng yên)", "Vertex đầu tiên đã chọn", "Tâm Bounding Box (có thể lệch)") default:1
    )

    button btnApply "2. XOAY THẲNG (Apply)" width:280 height:35 enabled:false

    group "Thông số đã xoay (lưu trên Object)"
    (
        label lblSaved "Tổng đã xoay: --" align:#left
        button btnRefreshSaved "Làm mới thông số" width:280 height:20
    )

    local vertSelArr = #()
    local p1local, p2local
    local deltaAngle = 0.0
    local obj

    -- Đọc góc đã lưu từ trước trên Object (nếu có), lưu trong User-Defined Properties
    -- nên KHÔNG mất khi save/close file, dù Rotation transform vẫn hiện 0,0,0
    fn getSavedAngle o = (
        local s = getUserProp o "StraightenAngle"
        if s == undefined then 0.0 else (
            try (s as float) catch (0.0)
        )
    )

    fn setSavedAngle o val = (
        setUserProp o "StraightenAngle" (val as string)
    )

    fn refreshSavedLabel = (
        if obj != undefined then
        (
            local total = getSavedAngle obj
            lblSaved.text = "Tổng đã xoay: " + (total as string) + "°  (lưu trong UserProp: StraightenAngle)"
        )
        else
            lblSaved.text = "Tổng đã xoay: -- (chưa chọn object)"
    )

    on btnRefreshSaved pressed do
    (
        if selection.count > 0 do obj = selection[1]
        refreshSavedLabel()
    )

    fn getLocalPivot mode = (
        case mode of
        (
            1: [0,0,0]                       -- pivot THẬT của object (local origin) -> không dịch chuyển
            2: (p1local)                      -- vertex đầu tiên (local)
            3: (obj.center - obj.pos)         -- tâm bbox, quy về local space (có thể gây lệch)
            default: [0,0,0]
        )
    )

    on btnGet pressed do
    (
        obj = selection[1]
        if obj == undefined then
        (
            messageBox "Hãy chọn object trước."
            return()
        )

        local vertSel = polyop.getVertSelection obj
        vertSelArr = vertSel as array

        if vertSelArr.count != 2 then
        (
            messageBox "Cần chọn ĐÚNG 2 vertex ở Vertex sub-object mode.\nHiện đang chọn: " + (vertSelArr.count as string) + " vertex."
            return()
        )

        p1local = polyop.getVert obj vertSelArr[1]
        p2local = polyop.getVert obj vertSelArr[2]

        local dir = p2local - p1local
        local currentAngle = atan2 dir.y dir.x
        local ratio = currentAngle / 90.0
        local nearest90 = 0.0
        if ratio >= 0 then
            nearest90 = (floor (ratio + 0.5)) * 90.0
        else
            nearest90 = (ceil (ratio - 0.5)) * 90.0
        deltaAngle = nearest90 - currentAngle

        lblAngle.text = "Góc hiện tại: " + (currentAngle as string) + "°"
        lblTarget.text = "Góc mục tiêu: " + (nearest90 as string) + "°"
        lblDelta.text = "Cần xoay: " + (deltaAngle as string) + "°"

        refreshSavedLabel()

        btnApply.enabled = true
    )

    on btnApply pressed do
    (
        if obj == undefined then return()

        local pivotLocal = getLocalPivot rdoPivot.state
        local rotMat = (transMatrix (pivotLocal * -1)) * (rotateZMatrix deltaAngle) * (transMatrix pivotLocal)

        local numV = polyop.getNumVerts obj
        undo "Straighten Vertices" on
        (
            for i = 1 to numV do
            (
                local vp = polyop.getVert obj i
                local newP = vp * rotMat
                polyop.setVert obj i newP
            )
        )

        update obj
        completeRedraw()

        -- Cộng dồn góc vừa xoay vào tổng đã lưu trên Object (không phụ thuộc Rotation transform)
        local prevTotal = getSavedAngle obj
        local newTotal = prevTotal + deltaAngle
        setSavedAngle obj newTotal
        refreshSavedLabel()

        messageBox ("Đã xoay xong!\nGóc vừa xoay: " + (deltaAngle as string) + "°\nTổng cộng đã xoay (lưu trên Object): " + (newTotal as string) + "°\n\nLưu ý: Rotation transform vẫn giữ 0,0,0 vì tool này xoay trực tiếp Vertex,\nthông số góc thật được lưu trong User-Defined Property \"StraightenAngle\" của Object.\nXem Object Properties > User Defined để kiểm tra lại bất cứ lúc nào.")

        btnApply.enabled = false
    )
)

createDialog StraightenRollout
