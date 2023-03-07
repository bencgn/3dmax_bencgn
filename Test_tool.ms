rollout myRollout "My Rollout" width:150 height:50
(
    button clickButton "Click" 
    on clickButton pressed do 
    (
        box width:1.0 length:1.0 height:1.0
    )
)

fn dockRolloutToMainUI rl =
(
    local toolbar = getToolBar "Main UI"
    local floater = newRolloutFloater rl.name rl.width rl.height
    addRollout rl floater
    dockControl floater (toolbar.pos + [4, toolbar.count * 24])
)

dockRolloutToMainUI myRollout
