
   
rollout My_Replace_Tool "Replace_Tool" width:240 height:296
(
   groupBox 'grp2' "Inherit" pos:[8,8] width:224 height:96 align:#left
   checkbox '_Position' "Position" pos:[16,32] width:60 height:16 align:#left checked:true
   checkbox '_Rotation' "Rotation" pos:[88,32] width:60 height:16 align:#left checked:true
   checkbox '_Scale' "Scale" pos:[160,32] width:60 height:16 align:#left
   checkbox '_Layer' "Layer" pos:[16,56] width:60 height:16 align:#left
   checkbox '_Parent' "Parent" pos:[88,56] width:60 height:16 align:#left checked:true
   checkbox '_Children' "Children" pos:[160,56] width:60 height:16 align:#left checked:true
   checkbox '_Delete' "Delete_Original" pos:[16,80] width:100 height:16 align:#left checked:true
   groupBox 'grp3' "NewObjType" pos:[8,112] width:224 height:50 align:#left
   radioButtons '_NewObjType' "" pos:[16,136] width:104 height:48 labels:#("Copy", "Instance", "Reference") align:#left
   --checkbox '_WithChildren' "With Children" pos:[128,158] width:80 height:16 align:#left
   pickButton 'Select_OBJ' "Pick REF Object" pos:[8,178] width:224 height:48 align:#left
   Button '_Start' "Start" pos:[8,234] width:224 height:48 align:#left
   
   on Select_OBJ picked obj do (Select_OBJ.caption=obj.name;)
   
   on _Start pressed do
   (
      if Select_OBJ.object=="Deleted scene node" do (print 33)
      if $selection.count==0 then (messagebox "Select replace Object")
      if (Select_OBJ.object==undefined) then (messagebox "Pick Ref Object")
      else if $selection.count!=0 do
      (
         undo on
         (
         for i in $selection do 
         (
            if i==Select_OBJ.object do (deselectnode i)
         )
         for i in $selection do
         (
            if _NewObjType.state==1 then 
               (
                  o=(copy Select_OBJ.object )   
                  o.name=o.name+"__Copy"
                  --if _WithChildren.state==true then (chil=Select_OBJ.object.children;  for iii in chil do (re_chil=copy iii; re_chil.parent=o))
               ) 
            else if _NewObjType.state==2 then 
               (
                  o=(instance Select_OBJ.object )   
                  o.name=o.name+"__Instance"
                  --if _WithChildren.state==true then (chil=Select_OBJ.object.children;  for iii in chil do (re_chil=instance iii; re_chil.parent=o))
               ) 
            else if _NewObjType.state==3 then 
               (
                  o=(reference Select_OBJ.object )   
                  o.name=o.name+"__Reference"
                  --if _WithChildren.state==true then (chil=Select_OBJ.object.children;  for iii in chil do (re_chil=reference iii; re_chil.parent=o))
               )
            
            
            if _Position.state==true do o.pos=i.pos
            if _Rotation.state==true do (p = o.pos ; o.rotation = inverse i.transform.rotation ; o.pos = p)
            if _Scale.state==true do o.scale=i.scale
               
            Select_OBJ.object.layer.addnode o
            if _Layer.state==true do i.layer.addnode o
            if _Parent.state==true do o.Parent=i.Parent
            if _Children.state==true do ( for i2 in i.children do (i2.parent=o))
            
         )
            if _Delete.state==true do (delete $selection)
         )
      )
   )
   
   
   
   
)
   rof=newrolloutfloater "Replace_Tool" 250 310
   addrollout  My_Replace_Tool rof
   
