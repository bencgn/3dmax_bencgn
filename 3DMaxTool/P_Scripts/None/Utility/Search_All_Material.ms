
(
	
local y_value=20, filter_mode=false
local dp_mat, search_all_Tex, search_all_Mat, Map_tex_list
local Texture_Slot_List_arr,ro_bmRename, sort_type=#Missing
	

	


function Search_tex_From_Scene targetList:""=
(
   dp_mat=#()
    
    function search_all_Tex tex parent target=
    ( 
		  if (getNumSubTexmaps tex)==0 then 
		  (--print tex
			appendIfUnique parent tex
			append dp_mat parent
		  )
		  else 
		  (
				 check_=false
		  for i=1 to (getNumSubTexmaps tex) do
			 (
				t=(getSubTexmap tex i)
				if t!=undefined do
				(
					check_=true
				   appendIfUnique parent tex
				   _parent=deepcopy parent
				   search_all_Tex t _parent target
				)
			 )
			if check_==false do 
			(
				appendIfUnique parent tex
				append dp_mat parent
			)
		)
    )
     
    
    function search_all_Mat mat parent target=
    (
      if ((superclassof mat)==material) and (getNumSubMtls mat)!=0 then
      (
         for i=1 to (getNumSubTexmaps mat) do
         (
            t=(getSubTexmap mat i)
            if t!=undefined do
            (
               appendIfUnique parent mat
               _parent=deepcopy parent
               search_all_tex t _parent target
            )
         )
         for i=1 to (getNumSubMtls mat) do
         (
            if  (getSubMtl mat i)!=undefined do
            (
               appendIfUnique parent mat
               _parent=deepcopy parent
               search_all_Mat (getSubMtl mat i) _parent target
            )
         )
      )
      else 
      (
         for i=1 to (getNumSubTexmaps mat) do
         (
            t=(getSubTexmap mat i)
            if t!=undefined then
            (
               appendIfUnique parent mat
               _parent=deepcopy parent
               search_all_tex t _parent target
            )
			else 
			(
				--appendIfUnique dp_mat  #(mat,"")
			)
         )
      )   
    )
    

      for i in sceneMaterials do
      (
         search_all_Mat i #() targetlist
      )
      if (dp_mat.count==1) do
      (
         count_=0
         dp_mat=#(#("-----"+(filenameFromPath targetList) as string+"-----"))
         join dp_mat #(#("(This texture only exists in the material editor.)"))
         count_=dp_mat.count
         for i in meditMaterials  do
         (
            search_all_Mat i #() targetlist
         )   
         if (dp_mat.count==count_) do
         (
            dp_mat[count_]=#("(This texture exists in the file)")
            append dp_mat #("(But this texture is not a material texture / ex: Modifiers Map)")
         )
         
      )
      return dp_mat
)

	
	
	
	
	
	
	
rollout Material_Map_List "Material Map List" width:346 height:642
(
      
   multiListBox 'multiListBox_' "" pos:[8,8] width:328 height:31 align:#left
   label 'Info' "Double cick : Material to active Material editor Slot" pos:[8,420]
   label 'Info2' "Right cick : Deselect" pos:[8,435]
   button 'Reload' "Reload" pos:[8,440+10] width:160 height:40 align:#left
   button 'To_MaterialSlot' "To MaterialSlot" pos:[176,440+10] width:160 height:40 align:#left
   button 'Select_Object_by_Material' "Select Object from\nSelected Material" pos:[8,488+10] width:160 height:40 align:#left
   button 'Select_Material_by_Object' "Select Material from\nSelected Object" pos:[176,488+10] width:160 height:40 align:#left
   button 'Select_Samename' "Select Same Name" pos:[8,536+10] width:160 height:40 align:#left
   button 'Select_SameTexture' "Select Same Taxture" pos:[176,536+10] width:160 height:40 align:#left
   button 'Set_Mtl_Map_From_Mtlslot_Selection' "Set Mtl/Map\nFrom Active Mtlslot" pos:[8,584+10] width:160 height:40 align:#left
   button 'Select_SameTexture2' "??" pos:[176,584+10] width:160 height:40 align:#left
   
   on multiListBox_ doubleclicked arg do
   (
      MatEditor.mode=#basic
      MatEditor.Open() 
      if (classof Map_tex_list[arg][1])!=string do
      (
         setMeditMaterial activeMeditSlot Map_tex_list[arg][1] 
      )
   )
   
   on multiListBox_ rightclick arg do
   (
     multiListBox_.selection=#()
   )
   
   function Select_MM type_ deselect:false=
   (
      selection_=#()
      for i=1 to Map_tex_list.count do
      (
         if Map_tex_list[i][3]==type_ or Map_tex_list[i][4]==type_ do
         (
            append selection_ i
         )
      )
      c=multiListBox_.selection
	  if deselect==false then
      (
		join c (selection_ as bitarray)
		multiListBox_.selection=c
	  )
	  else
	  (
		  d=#()
		  for ii in c do
		  (
			_test_=false
			  for iii in selection_ do
			  (
				  if ii==iii do 
				  (_test_=true; break)
			  )
			if (_test_==false) do (appendIfUnique d (ii))
		  )
		multiListBox_.selection=d
	  )
   )
   
   function Reload_=
   (
      local result_=#()
      join result_ (Search_tex_From_Scene ())
      if result_.count!=0 do
      (
         _arr=#()
         for i=1 to result_.count do
         (
            for ii=1 to result_[i].count do
            (
               if i>1 then
               (
                  if result_[i][ii]!=result_[i-1][ii] do
                  (
                     empty_=""
                     for j=1 to ii-1 do
                     (
                        empty_=empty_+"   "
                     )
                 type_2=#empty
                     type_=#Parent_Map
                     if (isproperty result_[i][ii] "filename")==true and ((superclassof result_[i][ii-1])==material) then (type_=#Map; type_2=#Parent_Map)
                     else if (isproperty result_[i][ii] "filename")==true then (type_=#Map)
                     else if ((superclassof result_[i][ii])==material) and (getNumSubMtls result_[i][ii])!=0 then (type_=#MultiMat)
                     else if ((superclassof result_[i][ii])==material) and (getNumSubMtls result_[i][ii])==0 and ii==1  then (type_=#MultiMat; type_2=#Mat)
                     else if ((superclassof result_[i][ii])==material) and (getNumSubMtls result_[i][ii])==0 and ii!=1  then (type_=#Mat;)
                     else if ((classof result_[i][ii])==string) then (type_=#nothing; continue)
                     append _arr #(result_[i][ii],(empty_+(result_[i][ii] as string)),type_,type_2)
                  )
               )
               else 
               (
                  empty_=""
                  for j=1 to ii-1 do
                  (
                     empty_=empty_+"   "
                  )
                     type_=#nothing
                     if (isproperty result_[i][ii] "filename")==true then (type_=#Map)
                else if (ii!=1 and (superclassof result_[i][ii-1])==material) then (type_=#Parent_Map)
                     else if ((superclassof result_[i][ii])==material) and (getNumSubMtls result_[i][ii])!=0 then (type_=#MultiMat)
                     else if ((superclassof result_[i][ii])==material) and (getNumSubMtls result_[i][ii])==0 and ii==1 then (type_=#MultiMat)
                     else if ((superclassof result_[i][ii])==material) and (getNumSubMtls result_[i][ii])==0 and ii!=1 then (type_=#Mat)
                     else if ((classof result_[i][ii])==string) then (type_=#nothing; continue)
                  append _arr #(result_[i][ii],(empty_+(result_[i][ii] as string)),type_,type_2)
               )
            )
         )
         _arr_text=#()
         for i in _arr do
         (
            append _arr_text i[2]
         )
         Map_tex_list=_arr
         Material_Map_List.multiListBox_.items=_arr_text
		 Material_Map_List.multiListBox_.selection=#()
      )
   )
   
   on Reload pressed do
   (
	   Reload_()
   )
   on To_MaterialSlot pressed do
   (
      MatEditor.mode=#basic
      MatEditor.Open() 
      ms_count=1
      for i in multiListBox_.selection do
      (
         if (classof Map_tex_list[i][1])!=string do
         (
            setMeditMaterial ms_count Map_tex_list[i][1] 
            ms_count+=1
         )
      )
   )
   
   on Select_Object_by_Material pressed do
   (
		obj_list=#()
      for i in multiListBox_.selection do
      (
         if (classof Map_tex_list[i][1])!=string do
         (
            append obj_list (refs.dependentnodes Map_tex_list[i][1])
         )
      )
	  deselect selection
	  for i in obj_list do (selectmore i)
   )
   
   on Select_Material_by_Object pressed do
   (
		sel_list=#()
      for i=1 to multiListBox_.items.count do
      (
         if (classof Map_tex_list[i][1])!=string do
         (
			 for ii in selection do 
			(
				print Map_tex_list[i][1]
				print ii.material
				if Map_tex_list[i][1]==ii.material do
				(
					
					append sel_list i
				)
			)
         )
      )
	Material_Map_List.multiListBox_.selection=sel_list
   )
   
   on Select_Samename pressed do
   (
		sel_list=#()
	   target= (Map_tex_list[(((Material_Map_List.multiListBox_.selection) as array)[1])][1])
	   for i=1 to multiListBox_.items.count do
      (
         if (classof Map_tex_list[i][1])!=string do
         (
			if Map_tex_list[i][1].name==target.name do
			(
				append sel_list i
			)
         )
      )
		Material_Map_List.multiListBox_.selection=sel_list
   )
   
   on Select_SameTexture pressed do
   (
	sel_list=#()
	   target= (Map_tex_list[(((Material_Map_List.multiListBox_.selection) as array)[1])][1])
	   if (hasProperty target "filename")==true do 
	   (
		for i=1 to multiListBox_.items.count do
		  (
			 if (classof Map_tex_list[i][1])!=string do
			 (
				if (hasProperty Map_tex_list[i][1] "filename")==true do 
				(
					if Map_tex_list[i][1].filename==target.filename do
					(
						append sel_list i
					)
				)
			 )
		  )
		Material_Map_List.multiListBox_.selection=sel_list
		)
   )
   
   on Set_Mtl_Map_From_Mtlslot_Selection pressed do
   (
	if (queryBox "!WARNING!\nThe selected materials(Maps) are changed to the first material(Map) in the Material Editor. \nBe absolutely careful")==false do return false
	obj_list=#()
	target=getMeditMaterial activeMeditSlot
	
    for i in multiListBox_.selection do
    (
        if (classof Map_tex_list[i][1])!=string do
        (
			if (superclassof Map_tex_list[i][1])!=(superclassof target) do 
			(
				print (superclassof Map_tex_list[i][1])
				print (superclassof target)
				messagebox "Material(map) types do not match!"; return false
			)
		)
	)
	
    for i in multiListBox_.selection do
    (
        if (classof Map_tex_list[i][1])!=string do
        (
			replaceInstances (Map_tex_list[i][1]) target
		)
	)
		messagebox "Success"
	   Reload_()
   )
)
	
	
	
	

         try (destroydialog Material_Map_List)
         catch()
         createdialog Material_Map_List  --modal:true


)