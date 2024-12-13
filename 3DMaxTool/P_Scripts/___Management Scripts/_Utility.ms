
(

fn YNC_Messagebox _text=
(
	-- setup dotnet classes / objects
	local mb = dotNetClass "System.Windows.Forms.MessageBox"
	local buttons = dotNetClass "System.Windows.Forms.MessageBoxButtons"
	local icons = dotNetClass "System.Windows.Forms.MessageBoxIcon"
	local defaultButton = dotNetClass "System.Windows.Forms.MessageBoxDefaultButton"
	local dialogResult = dotNetClass "System.Windows.Forms.DialogResult"
	local result = mb.show _text "Quit" buttons.YesNoCancel icons.Information defaultButton.Button3
	
	-- evaluate result of messageBox (which button has been pressed by the user)
	if ( result == dialogResult.Yes ) then
	(
		return #Yes
	)
	else if ( result == dialogResult.No ) then
	(
		return #No
	)
	else if ( result == dialogResult.Cancel ) then
	(
		return #Cancel
	)
	
)


fn Dialog_modal text1 text2=
(
-- instantiate the object
theObj = dotNetObject "MaxCustomControls.RenameInstanceDialog" text2
theobj.text =text1
DialogResult = theObj.Showmodal()

--test if the ok button was pressed
   /*
dotnet.compareenums TheObj.DialogResult ((dotnetclass "System.Windows.Forms.DialogResult").OK)*/
--get the new text string
text_=theobj.InstanceName 
text_arr=filterString text_ "\""
text_=""
for i in text_arr do
(
	text_=text_+i
)
return text_
)
	
	
	
function Check_Current_Selected_Type=
			(
				function get_Modify_List=
				(
					a=filein ((getdir #userscripts)+"\\P_Scripts\\___Management Scripts\\_List.ms")
					return a
				)

				Modify_List=get_Modify_List()

				fn Check_Folder_Exist dir=( return doesFileExist ((getdir #userscripts)+"\\P_Scripts\\"+dir+"\\Info"))
				
				Select_List=selection as array
					
				if Select_List.count==0 then 
				(
					return "None"
				)
				
				current_modify=(modpanel.getCurrentObject()) as string
				namefilter=findstring current_modify ":"
				if namefilter!=undefined do (current_modify=substring current_modify 1 (namefilter-1))

				if current_modify!="undefined" then
				(
					if (Check_Folder_Exist (current_modify)) and (finditem Modify_List (current_modify))!=0 do
					(
								return current_modify as string
					)
					case current_modify of 
					(
						"Edit_Poly" :
						(
							return "Editable Poly"
						)
						"Line" :
						(
							return "Editable Spline"
						)
						"Edit_Spline" :
						(
							return "Editable Spline"
						)
						/*default : 
						(
							return "Default"
						)*/
					)
				)
				--else
				(
					if Select_List.count > 1 do
					(
						for i=2 to Select_List.count do
						(
							if (Superclassof Select_List[i]) != (Superclassof Select_List[i-1]) do
							(
								return "Default"
							)
						)
					)
					
					case (Superclassof Select_List[1]) of
					(
					GeometryClass:
						(
							if Select_List.count > 1 do
							(
								for i=2 to Select_List.count do
								(
									if (classof Select_List[i]) != (classof Select_List[i-1]) do
									(
										return "Default"
									)
								)
							)
							case (classof (Select_List[1])) of 
							(
							Biped_Object:
								(
									if (Check_Folder_Exist "Biped_Object") and ((finditem Modify_List "Biped_Object")!=0) do (return "Biped_Object")
									return "Default"		
								)
							BoneGeometry:
								(
									if (Check_Folder_Exist "BoneGeometry") and ((finditem Modify_List "BoneGeometry")!=0) do (return "BoneGeometry")
									return "Default"
								)
							Default:
								(
									return "Default"
								)
							)
						)
					Shape:
						(
							if (Check_Folder_Exist "Shape") and ((finditem Modify_List "Shape")!=0) do (return "Shape")
							return "Default"
						)
					Helper:
						(
							if (Check_Folder_Exist "Helper") and ((finditem Modify_List "Helper")!=0) do (return "Helper")
							return "Default"
						)
					Camera:
						(
							if (Check_Folder_Exist "Camera") and ((finditem Modify_List "Camera")!=0) do (return "Camera")
							return "Default"
						)
					Light:
						(
							if ((Check_Folder_Exist "Light")==true) and ((finditem Modify_List "Light")!=0) do (return "Light")
							return "Default"
						)
					)
				)
			)
			
function refresh_list arg=
(
		local arr3, arr4=#()
		arr3=getFiles ((getdir #userscripts)+"\\P_Scripts\\"+arg+"\\Utility\\*")
		for i in arr3 do
		(
			append arr4 (filenameFromPath i)
		)
		return arr4
)



rollout Utility_rollout "Utility" width:185 height:232
(
	dropdownList 'ddl1' "" pos:[8,8] width:169 height:22 align:#left
	listbox 'cbx1' "" pos:[8,32] width:169 height:11 align:#left
	button 'btn1' "Run" pos:[4,184] width:84 height:44 align:#left
	button 'btn2' "New" pos:[89,184] width:45 height:22 align:#left
	button 'btn3' "Import" pos:[135,184] width:45 height:22 align:#left
	button 'btn5' "Edit" pos:[89,206] width:45 height:22 align:#left
	button 'btn4' "R" pos:[135,206] width:22 height:22 align:#left
	button 'btn6' "D" pos:[157,206] width:22 height:22 align:#left
	
	on ddl1 selected arg do
	(
		cbx1.items=(refresh_list ddl1.items[arg])
	)
	
	on ddl1 rightClick do
	(
		if (ddl1.selection+1)>(ddl1.items.count) then (ddl1.selection=1)
		else (ddl1.selection=ddl1.selection+1)
		cbx1.items=(refresh_list ddl1.items[ddl1.selection])
	)
	
	on cbx1 doubleClicked arg do
	(
		fileIn ((getdir #userscripts)+"\\P_Scripts\\"+ddl1.selected+"\\Utility\\"+cbx1.selected)
	)
	
	on cbx1 RightClick arg do
	(
		doscommand ("explorer " +((getdir #userscripts)+"\\P_Scripts\\"+ddl1.selected+"\\Utility"))
	)
	
	on btn1 pressed do 
	(
		fileIn ((getdir #userscripts)+"\\P_Scripts\\"+ddl1.selected+"\\Utility\\"+cbx1.selected)
	)
	
	on btn2 pressed do
	(
		New_Name=(Dialog_modal ("New Script's Name") "")
		if (New_Name=="") do (return false)
		folder_name=(ddl1.selected)
		a=createfile ((getdir #userscripts)+"\\P_Scripts\\"+folder_name+"\\Utility\\"+New_Name+".ms")
		close a
		cbx1.items=(refresh_list ddl1.selected)
		
	)
	
	on btn3 pressed do
	(
		New_Script=getOpenFileName caption:"Open A Test File:" types:"Maxscript(*.ms,*.mse,*.mcr)|*.ms;*.mse;*.mcr"
		if (New_Script==undefined) do (return false)
		
		New_Script_Name=filenameFromPath New_Script
		folder_name=(ddl1.selected)
		copyfile New_Script ((getdir #userscripts)+"\\P_Scripts\\"+folder_name+"\\Utility\\"+New_Script_Name)
		cbx1.items=(refresh_list ddl1.selected)
	)
	
	on btn4 pressed do
	(
		New_Name=(Dialog_modal ("Rename_Script : "+cbx1.selected ) cbx1.selected )
		if (New_Name=="") or (New_Name==undefined) do (return false)
		if (matchpattern New_Name pattern:"*.ms") or (matchpattern New_Name pattern:"*.mse") or (matchpattern New_Name pattern:"*.mcr") then ()
		else (New_Name=New_Name+".ms")
		folder_name=(ddl1.selected)
		Renamefile ((getdir #userscripts)+"\\P_Scripts\\"+folder_name+"\\Utility\\"+cbx1.selected) ((getdir #userscripts)+"\\P_Scripts\\"+folder_name+"\\Utility\\"+New_Name)
		cbx1.items=(refresh_list ddl1.selected)
	)
	
	on btn5 pressed do
	(
		folder_name=(ddl1.selected)
		edit ((getdir #userscripts)+"\\P_Scripts\\"+folder_name+"\\Utility\\"+cbx1.selected)
	)
	
	on btn6 pressed do
	(
		folder_name=(ddl1.selected)
		case (YNC_Messagebox "Really Want Delete Script? It can not be repaired") of
		(
			#yes:
			(
				folder_name=(ddl1.selected)
				deletefile ((getdir #userscripts)+"\\P_Scripts\\"+folder_name+"\\Utility\\"+cbx1.selected)
		cbx1.items=(refresh_list ddl1.selected)
			)
			default:
			(
			)
		)
	)
)


createdialog Utility_rollout pos:mouse.screenpos  

function get_Utility_List=
(
	a=filein ((getdir #userscripts)+"\\P_Scripts\\___Management Scripts\\_Utility_List.ms")
			return a
)

arr2=get_Utility_List()

/*
arr= (getDirectories ((getdir #userscripts)+"\\P_Scripts\\*"))
--print arr
arr2=#()
for i in arr do
(
	local a
	b=i.count
	a=substring i ((findstring i "P_Scripts\\")+10) (30)
	a=substring a 1 (a.count-1)
	append arr2 a
)
print arr2
*/

Utility_rollout.ddl1.items=arr2
Utility_rollout.cbx1.items=(refresh_list (Utility_rollout.ddl1.items[1]))
	
current_type=Check_Current_Selected_Type()
for i=1 to Utility_rollout.ddl1.items.count do
(
	if (Utility_rollout.ddl1.items[i]==current_type) do 
	(
		Utility_rollout.cbx1.items=(refresh_list Utility_rollout.ddl1.items[i])
		Utility_rollout.ddl1.selection=i
		exit
	)
)


)
