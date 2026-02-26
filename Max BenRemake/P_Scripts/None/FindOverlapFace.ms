-- Written By Colin Senner
-- www.colinsenner.com

-- Functions 
global trim_dupsArray
global findPolyCoinstancedFaces
global findMeshCoinstancedFaces
global findCoinstancedObjects
global compareCenterAndNormalsPoly
global compareCenterAndNormalsMesh

-- Rollouts
global rlt_findCoinstances

-- Variables
global todo

if rlt_findCoinstances != undefined then destroyDialog rlt_findCoinstances


rollout rlt_findCoinstances "Find Coinstances 1.01" (
    dropDownList lst_todo items:#("Select Only Duplicates","Select All") selection:1 width:140
    button btn_Find "Find" width:70
    button btn_Help "?" offset:[60,-24] height:16 width:20
    on lst_todo selected sel do ( todo = sel )

    on btn_Help pressed do (
        local txt = ""
        txt += "Help Dialog v1.01 - Find CoInstances, by Colin Senner\n\n"
        txt += "Find CoInstances works in two ways:\n\n"
        txt += "   1. With Multiple Objects selected it will find objects that are cloned on top of each other\n"
        txt += "    resulting in animation flickering because of coplanarity\n\n"
        txt += "   2. With a single object selected it will find and select faces that are coplanar\n\n"
        txt += "To select all faces which are coplanar use the list-box to \"Select All\", or\n"
        txt += "To select only those faces which are copies of the original, use \"Select Only Duplicates\"\n"
        messagebox txt title:"Help" beep:false
    )

    on btn_Find pressed do (
        local objs = getCurrentSelection()

        if objs.count == 1 then (
            if classof objs[1] == Editable_Poly then (
                if lst_todo.selection == 1 then
                    dupFaces = (findPolyCoinstancedFaces objs[1] returnOnlyDupes:true)
                else if lst_todo.selection == 2 then
                    dupFaces = (findPolyCoinstancedFaces objs[1] returnOnlyDupes:false)
            ) else if classof objs[1] == Editable_Mesh then (
                if lst_todo.selection == 1 then
                    dupFaces = (findMeshCoinstancedFaces objs[1] returnOnlyDupes:true)
                else if lst_todo.selection == 2 then
                    dupFaces = (findMeshCoinstancedFaces objs[1] returnOnlyDupes:false)
            ) else (
                messageBox "Please select an editable poly or mesh."
                return false
            )

            objs[1].selectedFaces = dupFaces
            subObjectLevel = 4
        ) else (
            -- Multiple Objects Selected
            clearSelection()
            dupObjs = (findCoInstancedObjects objs)
            select dupObjs
        )
    )
)
createDialog rlt_findCoinstances 160 60


fn findPolyCoinstancedFaces obj returnOnlyDupes:false = (
    local objArrSFC = #()
    local objArrNrm = #()
    local dupFaces = #{}
    format "findpoly returnOnlyDupes:%\n" returnOnlyDupes

    if classof obj == Editable_Poly then (      
        for i = 1 to obj.faces.count do (
            objArrSFC[i] = (polyOp.getSafeFaceCenter obj i)
            objArrNrm[i] = (polyOp.getFaceNormal obj i)
        )
        dupFaces = (compareCenterAndNormalsPoly objArrSFC objArrNrm returnOnlyDupes:returnOnlyDupes)
    ) else 
        return undefined

    dupFaces
)

-- Looks through two arrays for Matching SafeFaceCenters if matching another in the array,
-- if found, checks arrNrm array to see if the normals or inverse normals match
fn compareCenterAndNormalsPoly arrSFC arrNrm returnOnlyDupes:false = (
    local dupBitArr = #{}
    local invNrm, index

    for i = 1 to arrSFC.count do (
        index = findItem arrSFC arrSFC[i]
        if index != 0 and index != i then (
            local invNrm = (arrNrm[index]*[-1,-1,-1])
            if (arrNrm[i] == arrNrm[index]) or (arrNrm[i] == invNrm) then (
                dupBitArr[i] = true
                if not(returnOnlyDupes) then 
                    dupBitArr[index] = true
                print dupBitArr
            )
        )
    )
    dupBitArr
)

-- Looks through two arrays for Matching SafeFaceCenters if matching another in the array,
-- if found, checks arrNrm array to see if the normals or inverse normals match
fn compareCenterAndNormalsMesh arrSFC arrNrm returnOnlyDupes:false = (
    local dupBitArr = #{}
    local invNrm, index

    for i = 1 to arrSFC.count do (
        index = findItem arrSFC arrSFC[i]
        if index != 0 and index != i then (
            local invNrm = for p in arrNrm[index] collect (p*[-1,-1,-1])

            if ((arrNrm[i] as string) == (arrNrm[index] as string)) or ((arrNrm[i] as string) == (invNrm as string)) then (
                dupBitArr[i] = true
                if not(returnOnlyDupes) then 
                    dupBitArr[index] = true
                print dupBitArr
            )
        )
    )
    dupBitArr
)

-- findMeshCoinstancedFaces returns a bitarray of coplanar faces
fn findMeshCoinstancedFaces obj returnOnlyDupes:false = (
    local objArrSFC = #()
    local objArrNrm = #()
    local dupFaces = #{}

    if classof obj == Editable_Mesh then (
        for i = 1 to obj.faces.count do (
            objArrSFC[i] = (meshOp.getFaceCenter obj i)
            objArrNrm[i] = (meshOp.getFaceRNormals obj i)
        )
        dupFaces = (compareCenterAndNormalsMesh objArrSFC objArrNrm returnOnlyDupes:returnOnlyDupes)
    ) else 
        return undefined

    dupFaces
)

-- findCoinstancedObjects returns an array of duplicate objects
fn findCoinstancedObjects arr = (
    local dupObjs = #()

    for o in arr do (
        for j in arr where o != j do (
            -- Defex code hack for selecting only the duplicate
            if ((o.transform as string) == (j.transform as string)) and (o.min == j.min) and (o.max == j.max) and (o.wirecolor == j.wirecolor) then (
                append dupObjs j
                j.wirecolor = color 250 243 210
            )
            -- end Defex code
            --if ((o.transform as string) == (j.transform as string)) and (o.min == j.min) and (o.max == j.max) then
                --append dupObjs j
        )
    )
    trim_dupsArray dupObjs
)

fn trim_dupsArray a = (
    for i in a.count to 1 by -1 do 
        (
            idx = findItem a a[i]
            if (idx != 0) AND (idx != i) do (
                deleteItem a i
            )
        )
    a
)

/*fn trim_dupsArrayString arr = (
    for i=arr.count to 1 by -1 do (
        for j=arr.count to 1 by -1 do (
            if i != j and (arr[i] as string) == (arr[j] as string) then (
                deleteItem arr j
            )       
        )   
    )
    arr
)*/
