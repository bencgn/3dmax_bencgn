(
function getFacesByAngle oPoly iFace fDegThresh contig: #byVert =
(
    if ((classOf oPoly) != Editable_Poly) and ((classOf oPoly) != Edit_Poly)   then
        throw "Wrong input in function getFacesByAngle() - Editable Poly"
        
    if ((classOf iFace) != Integer) then
        throw "Wrong input in function getFacesByAngle() - Face Index"

    if ( (iFace <= 0) or (iFace > (polyOp.getNumFaces oPoly)) ) then
        throw "Wrong input in function getFacesByAngle() - Face Index out of boundaries"
        
    if ( (classOf fDegThresh != Float) and (classOf fDegThresh != Integer) ) then
        throw "Wrong input in function getFacesByAngle() - Angle Threshold"

    if ( (fDegThresh < 0) or (fDegThresh > 180) ) then
        throw "Wrong input in function getFacesByAngle() - Angle Threshold out of boundaries"

    -- remove all the previous test if not necessary

    local p3FaceNormal = polyOp.getFaceNormal oPoly iFace
    local fTestDot = cos fDegThresh
    
    local iNumFaces = polyOp.getNumFaces oPoly 
    
    if (contig == #none) then
    (
        local baSelFaces = #{1..iNumFaces}

        for i = 1 to iNumFaces do
        (
            p3ItemNormal = polyOp.getFaceNormal oPoly i
                
            if ((dot p3FaceNormal p3ItemNormal) < fTestDot) then
                baSelFaces[i] = false
        )
    )
    else if (contig == #byVert) then
    (print 33
        local baLimitVerts = #{}
        local baLimitFaces = #{iFace}
        
        local baSelFaces = #{iFace}
        local baUnselFaces = #{}

        while (baLimitFaces.numberSet > 0) do
        (
            baLimitVerts = (polyOp.getVertsUsingFace oPoly baSelFaces) - (polyOp.getVertsUsedOnlyByFaces oPoly baSelFaces)
            baLimitFaces = (polyOp.getFacesUsingVert oPoly baLimitVerts) - baSelFaces - baUnselFaces

            for item in baLimitFaces do
            (
                p3ItemNormal = polyOp.getFaceNormal oPoly item
                    
                if ((dot p3FaceNormal p3ItemNormal) >= fTestDot) then
                (
                    baSelFaces[item] = true
                )
                else
                (
                    baUnselFaces[item] = true
                )
            )
        )
    )
    else if (contig == #byEdge) then
    (
        local iNumFaces = polyOp.getNumFaces oPoly
    
        local baLimitVerts = #{}
        local baLimitFaces = #{iFace}
        
        local baSelFaces = #{iFace}
        local baUnselFaces = #{}

        local baEdgeSet01 = #{}
        local baFaceSet01 = #{}
        local baEdgeSet02 = #{}

        while (baLimitFaces.numberSet > 0) do
        (
            baEdgeSet01 = polyOp.getEdgesUsingFace oPoly baSelFaces
            baFaceSet01 = #{1..iNumFaces} - baSelFaces
            baEdgeSet02 = polyOp.getEdgesUsingFace oPoly baFaceSet01

            baLimitEdges = baEdgeSet01 * baEdgeSet02
            baLimitFaces = (polyOp.getFacesUsingEdge oPoly baLimitEdges) - baSelFaces - baUnselFaces

            for item in baLimitFaces do
            (
                p3ItemNormal = polyOp.getFaceNormal oPoly item
                    
                if ((dot p3FaceNormal p3ItemNormal) >= fTestDot) then
                (
                    baSelFaces[item] = true
                )
                else
                (
                    baUnselFaces[item] = true
                )
            )
        )
    )

    ( -- just for visual feedback, remove if unneeded
        polyOp.setFaceSelection oPoly baSelFaces
    )

    return baSelFaces
)

list=#{}
dd=($.EditablePoly.GetSelection #Face)
for i in dd do ((getFacesByAngle $ i 45); list+=($.EditablePoly.GetSelection #Face))
print list
$.EditablePoly.SetSelection #Face #{}
$.EditablePoly.SetSelection #Face (list)
)