/*
 * MoveXPositionTool.ms
 * 3ds Max script for moving objects along X axis
 */

rollout MoveXPositionTool "Move X Position Tool" width:300 height:220
(
    -- UI Controls
    group "Object Selection"
    (
        button btnSelectObjects "Select Objects" width:150 height:30 tooltip:"Click to select objects"
        label lblSelectedCount "No objects selected" align:#center
    )
    
    group "Move Settings"
    (
        spinner spnBaseOffset "Base Offset:" range:[-1000, 1000, 10] type:#float width:150 tooltip:"Starting offset value"
        spinner spnIncrementValue "Increment:" range:[-100, 100, 5] type:#float width:150 tooltip:"Amount to increase offset for each subsequent object"
        button btnMoveObjects "Move Objects" width:150 height:30 tooltip:"Move selected objects by incremental X offset" enabled:false
    )
    
    -- Variables
    local selectedObjects = #()
    
    -- Functions
    fn updateSelectionCount =
    (
        if selectedObjects.count == 0 then
            lblSelectedCount.text = "No objects selected"
        else if selectedObjects.count == 1 then
            lblSelectedCount.text = "1 object selected"
        else
            lblSelectedCount.text = selectedObjects.count as string + " objects selected"
        
        -- Enable/disable move button based on selection
        btnMoveObjects.enabled = (selectedObjects.count > 0)
    )
    
    fn moveObjectsAlongX baseOffset incrementValue =
    (
        if selectedObjects.count > 0 then
        (
            undo "Move Objects Along X" on
            (
                -- Apply incremental offset based on selection order
                for i = 1 to selectedObjects.count do
                (
                    local obj = selectedObjects[i]
                    -- Get current position
                    local currentPos = obj.pos
                    -- Calculate offset for this object based on its position in selection
                    local objectOffset = baseOffset + (incrementValue * (i-1))
                    -- Create new position with modified X value
                    local newPos = [currentPos.x + objectOffset, currentPos.y, currentPos.z]
                    -- Apply new position
                    obj.pos = newPos
                )
            )
            -- Refresh viewports
            redrawViews()
        )
    )
    
    -- Event handlers
    on btnSelectObjects pressed do
    (
        -- Store current selection
        selectedObjects = getCurrentSelection()
        updateSelectionCount()
    )
    
    on btnMoveObjects pressed do
    (
        -- Get base offset and increment values from spinners
        local baseOffset = spnBaseOffset.value
        local incrementValue = spnIncrementValue.value
        -- Apply incremental movement
        moveObjectsAlongX baseOffset incrementValue
    )
    
    -- Initialize
    on MoveXPositionTool open do
    (
        -- Check if there's already a selection when opening
        selectedObjects = getCurrentSelection()
        updateSelectionCount()
    )
)

-- Create and show the dialog
if (MoveXPositionToolFloater != undefined) and (MoveXPositionToolFloater.open) do
(
    closeRolloutFloater MoveXPositionToolFloater
)

MoveXPositionToolFloater = newRolloutFloater "Move X Position Tool" 320 260
addRollout MoveXPositionTool MoveXPositionToolFloater
