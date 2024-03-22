rollout SetPivotRotationRollout "Set Pivot Rotation"
(
    label lblInstructions "Click the text to set pivot rotation to 90 degrees on X-axis:"
    button btnSetPivot "Set Pivot Rotation" width: 80
    
    on btnSetPivot pressed do
    (
        -- Get the selected object
        local obj = selection[1]
        
        -- Check if an object is selected
        if obj != undefined then
        (
            -- Set the pivot rotation
            obj.pivot.rotation = eulerangles 90 0 0
            messageBox "Pivot rotation set to 90 degrees on the X-axis."
        )
        else
        (
            messageBox "No object selected!"
        )
    )

    on lblInstructions mouseUp do
    (
        -- Get the selected object
        local obj = selection[1]
        
        -- Check if an object is selected
        if obj != undefined then
        (
            -- Set the pivot rotation
            obj.pivot.rotation = eulerangles 90 0 0
            messageBox "Pivot rotation set to 90 degrees on the X-axis."
        )
        else
        (
            messageBox "No object selected!"
        )
    )
)

createDialog SetPivotRotationRollout width:200 height:50
