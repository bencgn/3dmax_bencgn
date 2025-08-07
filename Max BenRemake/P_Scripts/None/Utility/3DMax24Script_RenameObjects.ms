rollout rOSTools "Rename Objects"
(
    
    button renameButton "Rename"
    button togglePivotButton "Toggle Pivot Mode"
    button rotateXButton "Rotate X = 90"
    label createdByLabel "Tool created by: bencgn"
    on renameButton pressed do
    (
        if selection.count == 2 do
        (
            local obj1 = selection[1]
            local obj2 = selection[2]
            
            if isValidNode(obj1) and isValidNode(obj2) do
            (
                macros.run "Tools" "PivotMode_Toggle" -- Toggle pivot mode
                obj2.pivot = obj1.pivot -- Set pivot of obj2 to match obj1
                obj2.name = obj1.name -- Rename obj2
            )
        )
    )
    
    on togglePivotButton pressed do
    (
        macros.run "Tools" "PivotMode_Toggle" -- Toggle pivot mode
    )
    
    on rotateXButton pressed do
    (
        local selectedObj = selection[1]
        
        if isValidNode(selectedObj) do
        (
            rotate selectedObj (eulerAngles 90 0 0)
            messageBox ("Rotated '" + selectedObj.name + "' 90 degrees around X-axis.")
        )
        
    )
)

createDialog rOSTools 150 160
