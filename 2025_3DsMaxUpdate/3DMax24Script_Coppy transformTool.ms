try(destroyDialog CopyTransformTool) catch()

rollout CopyTransformTool "Copy Transform Tool" width:200 height:150
(
    local storedTransform = undefined

    label lbl_info "Select an object to use the tool." pos:[10,10] width:180
    button btn_copy "Copy Pos/Rot/Scale" pos:[10,40] width:180
    button btn_restore "Restore Pos/Rot/Scale" pos:[10,80] width:180 enabled:false
    button btn_close "Close" pos:[10,120] width:180

    on btn_copy pressed do
    (
        if selection.count == 1 then
        (
            storedTransform = selection[1].transform
            btn_restore.enabled = true
            lbl_info.text = "Transform copied!"
        )
        else
        (
            messageBox "Please select exactly one object." title:"Error"
        )
    )

    on btn_restore pressed do
    (
        if isValidNode selection[1] and storedTransform != undefined then
        (
            selection[1].transform = storedTransform
            lbl_info.text = "Transform restored!"
        )
        else
        (
            messageBox "No transform data to restore or invalid selection." title:"Error"
        )
    )

    on btn_close pressed do
    (
        destroyDialog CopyTransformTool
    )
)

createDialog CopyTransformTool
