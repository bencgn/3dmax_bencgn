rollout myRollout "My Rollout" (
    button btn1 "ex1" width:100 align:#left
    button btn2 "ex2" width:100 align:#left
    button btn3 "ex3" width:100 align:#left
)

on btn1 pressed do (
    delete selection
)

on btn2 pressed do (
    select $Sphere001
    $.name = "My New Sphere"
)

on btn3 pressed do (
    box name:"My Box"
)

createDialog myRollout
