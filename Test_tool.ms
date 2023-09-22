rollout rOSTools "Rename Objects"
(
    button renameButton "Rename"
    
    on renameButton pressed do
    (
        if selection.count == 2 do
        (
            local obj1 = selection[1]
            local obj2 = selection[2]
            
            if isValidNode(obj1) and isValidNode(obj2) do
            (
                obj2.name = obj1.name
                
            )
            
        )
        
    )
)

createDialog rOSTools 200 80
