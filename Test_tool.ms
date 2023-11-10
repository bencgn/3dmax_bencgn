try(destroyDialog pickAndAssignMaterial) catch()

rollout pickAndAssignMaterial "Pick and Assign Material"
(
    label lblPick "Pick a material from this object:"
    pickButton btnPickMaterial "Pick Material"
    
    label lblAssign "Assign the picked material to selected objects:"
    button btnAssignMaterial "Assign Material"
    
    local pickedMaterial = undefined -- Variable to store the picked material
    
    on btnPickMaterial picked obj do
    (
        if isKindOf obj Material do
        (
            pickedMaterial = obj
            format "Picked Material: %\n" pickedMaterial.name to:MaxScriptListener
        )
    )
    
    on btnAssignMaterial pressed do
    (
        if isValidNode pickedMaterial do
        (
            local selectedObjects = getCurrentSelection()
            for obj in selectedObjects where isKindOf obj GeometryClass do
            (
                obj.material = pickedMaterial
            )
            format "Assigned Material: % to % objects\n" pickedMaterial.name selectedObjects.count to:MaxScriptListener
        )
    )
)

createDialog pickAndAssignMaterial 300 150
