macroScript h_instancer
category:"Developer Tools"
icon:#("Systems",3)
(

rollout h_instancer "Instancer 1.0" width:162 height:300
(
  group " Main object "
  (
    pickbutton pick_main "[ pick ]" toolTip:"" width:130
    label main_name "[picked:] ---"
  )
  on pick_main picked obj do
  (
    main_name.text = "[picked:] " + obj.name
    global main_obj = obj
    print ("picked: " + obj as string)
  )
  group " Instances "
  (
    checkbox rep "replace selection" checked:true
    checkbox sca "apply scale" checked:true
    checkbox rot "apply rotation" checked:true
    button go "[ make instances ]" width:130
  )
  on go pressed do
  (
    if main_obj == undefined then
    (
      messagebox "no main object selected"
    )
    else
    (
    undo on
    (
      for i = 1 to selection.count  do
      (
        n = instance(main_obj)
        if rot.checked == true do ( n.rotation = selection[i].rotation )
        n.position = selection[i].position
        if sca.checked == true do ( n.scale = selection[i].scale )
        n.name = selection[i].name
      )
      if ( rep.checked == true ) do
      (
        delete( $ )
      )
    )
    )
  )
)
CreateDialog h_instancer height:185
)
