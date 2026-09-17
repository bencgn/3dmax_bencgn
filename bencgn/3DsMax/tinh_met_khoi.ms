-- BENCGN Volume Tool v3 (FAST) - 3ds Max 2026
try (destroyDialog BENCGN_VolumeTool) catch()

rollout BENCGN_VolumeTool "BENCGN - Tính Mét Kh?i" width:320
(
    button btnObj "Tính Object (Box/Poly)" width:145 height:32 pos:[10,10]
    button btnElem "Tính Element Ðang Ch?n" width:145 height:32 pos:[165,10]

    groupBox grpF "L?c Element theo th? tích" pos:[10,50] width:300 height:58
    spinner spnVol "Du?i (m³):" range:[0.0,999999.0,0.01] scale:0.001 type:#float fieldwidth:70 pos:[20,70]
    button btnFilter "Ch?n Element < ngu?ng" width:130 height:24 pos:[175,68]

    button btnClear "Xóa Log" width:300 height:22 pos:[10,114]
    listbox lbLog "" height:11 width:300 pos:[10,142]

    fn unitToMeter =
    (
        local s = units.SystemScale
        case units.SystemType of
        (
            #Inches: s * 0.0254
            #Feet: s * 0.3048
            #Miles: s * 1609.344
            #Millimeters: s * 0.001
            #Centimeters: s * 0.01
            #Meters: s * 1.0
            #Kilometers: s * 1000.0
            default: s
        )
    )

    fn addLog txt =
    (
        local items = lbLog.items
        append items txt
        lbLog.items = items
        lbLog.selection = items.count
    )

    -- The tich signed cua 1 tap face poly, tinh truc tiep (fan triangulation)
    -- verts: mang Point3 da cache san
    fn facesSignedVolume obj faceBits verts =
    (
        local vol = 0.0
        local getFV = polyop.getFaceVerts
        for f in faceBits do
        (
            local fv = getFV obj f
            local p1 = verts[fv[1]]
            for i = 2 to fv.count - 1 do
                vol += dot p1 (cross verts[fv[i]] verts[fv[i+1]])
        )
        vol / 6.0
    )

    fn meshVolume msh =
    (
        local vol = 0.0
        for f = 1 to msh.numfaces do
        (
            local fv = getFace msh f
            vol += (dot (getVert msh fv.x) (cross (getVert msh fv.y) (getVert msh fv.z))) / 6.0
        )
        abs vol
    )

    fn cacheVerts obj =
    (
        local n = polyop.getNumVerts obj
        local verts = #()
        verts.count = n
        local getV = polyop.getVert
        for v = 1 to n do verts[v] = getV obj v
        verts
    )

    fn calcObject =
    (
        if selection.count != 1 then ( addLog "! Ch?n dúng 1 object" ; return() )
        local obj = selection[1]
        local k = unitToMeter()
        local vol
        if classof obj == Box then
            vol = obj.length * obj.width * obj.height * k * k * k
        else if classof obj == Editable_Poly then
        (
            local verts = cacheVerts obj
            vol = (abs (facesSignedVolume obj #{1..(polyop.getNumFaces obj)} verts)) * k * k * k
        )
        else
        (
            local msh = snapshotAsMesh obj
            vol = (meshVolume msh) * k * k * k
            delete msh
        )
        addLog (obj.name + " = " + (formattedPrint vol format:".4f") + " m³")
    )

    fn calcElement =
    (
        if selection.count != 1 or classof (modPanel.getCurrentObject()) != Editable_Poly then
        ( addLog "! Vào Editable Poly, ch?n Element" ; return() )
        local obj = selection[1]
        local selFaces = polyop.getFaceSelection obj
        if selFaces.numberset == 0 then ( addLog "! Chua ch?n face/element nào" ; return() )
        local k = unitToMeter()
        local verts = cacheVerts obj
        local vol = (abs (facesSignedVolume obj selFaces verts)) * k * k * k
        addLog ("Element (" + selFaces.numberset as string + " faces) = " + (formattedPrint vol format:".4f") + " m³")
    )

    fn filterElements =
    (
        if selection.count != 1 or classof selection[1] != Editable_Poly then
        ( addLog "! Ch?n 1 object Editable Poly" ; return() )

        local obj = selection[1]
        local st = timeStamp()
        local k = unitToMeter()
        local k3 = k * k * k
        local limit = spnVol.value
        local numF = polyop.getNumFaces obj
        local verts = cacheVerts obj
        local getElem = polyop.getElementsUsingFace

        local done = #{}
        local resultFaces = #{}
        local elemCount = 0
        local foundCount = 0

        for f = 1 to numF where not done[f] do
        (
            local elemFaces = getElem obj #{f}
            done += elemFaces
            elemCount += 1
            local vol = (abs (facesSignedVolume obj elemFaces verts)) * k3
            if vol < limit then
            (
                resultFaces += elemFaces
                foundCount += 1
            )
        )

        max modify mode
        subObjectLevel = 5
        polyop.setFaceSelection obj resultFaces
        redrawViews()

        addLog ("Quét " + elemCount as string + " element, ch?n " + foundCount as string \
            + " < " + (formattedPrint limit format:".4f") + " m³ (" \
            + ((timeStamp() - st) / 1000.0) as string + "s)")
    )

    on btnObj pressed do calcObject()
    on btnElem pressed do calcElement()
    on btnFilter pressed do filterElements()
    on btnClear pressed do lbLog.items = #()
)

createDialog BENCGN_VolumeTool