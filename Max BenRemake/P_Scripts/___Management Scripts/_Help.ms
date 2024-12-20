(
	
function bsort a b=
(
    if (a[1] == "O" and b[1]!="O") do (return -1)
    if (b[1] == "O" and a[1]!="O") do (return 1)
    local sortedArr = sort #(a, b)
    if sortedArr[1] == a then
        return -1
    else
        return 1
	return 0
)
	
function Check_Current_Selected_Type=
			(
				function get_Modify_List=
				(
					a=filein ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_List.ms")
					return a
				)

				Modify_List=get_Modify_List()

				fn Check_Folder_Exist dir=( return doesFileExist ((getdir #UserScripts)+"\\P_Scripts\\"+dir+"\\Info"))
				
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

fn YN_Messagebox _text=
(
	-- setup dotnet classes / objects
	local mb = dotNetClass "System.Windows.Forms.MessageBox"
	local buttons = dotNetClass "System.Windows.Forms.MessageBoxButtons"
	local icons = dotNetClass "System.Windows.Forms.MessageBoxIcon"
	local defaultButton = dotNetClass "System.Windows.Forms.MessageBoxDefaultButton"
	local dialogResult = dotNetClass "System.Windows.Forms.DialogResult"
	local result = mb.show _text "Quit" buttons.YesNo icons.Information defaultButton.Button3
	
	-- evaluate result of messageBox (which button has been pressed by the user)
	if ( result == dialogResult.Yes ) then
	(
		return #Yes
	)
	else if ( result == dialogResult.No ) then
	(
		return #No
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


Local Check_Scripts_Setting_Change=false
Local Scripts_BTN, Info_BTN, Design_BTN, Scripts_BTN, Folder_BTN, Utility_BTN, Modifiers_BTN, Help_BTN, Save_BTN
local Macro_List_Form, macro_List,Input_Text,macro_arr, Macro_Listbox, Find_Macro, Macro_Listbox, getMacroScripts, arraysort


	 
 if helpForm!=undefined do 
 (
	helpForm.close()
	helpForm=undefined
 )

Local helpForm, Script_Box1, Script_Box2, Script_Box3, Before_Category,Category_Setting_Render
Local Get_Scripts_List, Get_Button_List, Get_Category_List, Category_List, Button_Setting_Render
Local Check_Buttons_List_Change=false
Current_Category_Index=0
Form_List=#()
BTN_count=0

function addbutton Title Form=
(
	BTN = dotNetObject "System.windows.forms.button"
	BTN.text = Title
	BTN.flatStyle=BTN.flatStyle.Popup
	BTN.BackColor = (DotNetClass  "System.Drawing.Color").FromArgb 40 40 80
	BTN.size = dotNetObject "System.Drawing.Size" 170 48
	BTN.location = dotNetObject "System.Drawing.Point" 5 ((48*BTN_count)+11)		
	Form.controls.add BTN
	BTN_count+=1
	return BTN
)

function delete_Before_Form=
(
	function color_Reset=
	(
		Scripts_BTN.BackColor = (DotNetClass  "System.Drawing.Color").FromArgb 40 40 80
		Info_BTN.BackColor = (DotNetClass  "System.Drawing.Color").FromArgb 40 40 80
		Design_BTN.BackColor = (DotNetClass  "System.Drawing.Color").FromArgb 40 40 80
		Scripts_BTN.BackColor = (DotNetClass  "System.Drawing.Color").FromArgb 40 40 80
		Help_BTN.BackColor = (DotNetClass  "System.Drawing.Color").FromArgb 40 40 80
		Utility_BTN.BackColor = (DotNetClass  "System.Drawing.Color").FromArgb 40 40 80
		Modifiers_BTN.BackColor = (DotNetClass  "System.Drawing.Color").FromArgb 40 40 80
		Save_BTN.BackColor = (DotNetClass  "System.Drawing.Color").FromArgb 40 40 80
	)

	if (Check_Buttons_List_Change==true) do
	(
		case (YNC_Messagebox "The button has been modified.\nDo you want to save it?") of
		(
			#yes:
			(
				Button_Setting_Render()
				Check_Buttons_List_Change=false
				for i in Form_List do
				(helpForm.controls.remove i)
				color_Reset()
				return true
			)
			#no:
			(
				Check_Buttons_List_Change=false
				for i in Form_List do
				(helpForm.controls.remove i)
				color_Reset()
				return true
			)
			#cancel:
			(
				Check_Buttons_List_Change=true
				return false
			)
		)
	)
	
	for i in Form_List do
	(helpForm.controls.remove i)
	color_Reset()
	return true
)


	local Position_y=10
	local Position_1=188
	local Position_2=188+201
	local Position_3=188+201+201


function Information_View=
(
Info_BTN.BackColor = (DotNetClass  "System.Drawing.Color").FromArgb 220 100 40
Info_Box= dotNetObject "System.Windows.Forms.RichTextBox" pos:[0,0]
Info_Box.Location=dotnetobject "System.Drawing.Point" 180 10
Info_Box.size=dotNetObject "System.Drawing.Size" 595 434
Info_Box.BackColor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
Info_Box.BorderStyle= (dotnetclass "System.Windows.Forms.BorderStyle").None
Info_Box.LoadFile ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\Information.rtf")
Info_Box.Readonly=true
	
helpForm.controls.add Info_Box
append Form_List Info_Box
)

local preset_List, preset_List_Array, Render_Preset, get_preset_List_Array
local Back_Color_Button, Help_Color_Button, Fix_Color_Button, Border_Color_Button
local Text_Color_Button, DisFocus_Color_Button,Color_Preset,Apply_to_Sample
local Font_Size_Spinner, Button_Width, Button_Height,Original_Font,Original_Font2
local Sample_Button_List=#()

function Design_Setting_View=
(
	Position_y=10
	Position_1=188
	Position_2=188+201
	Position_3=188+201+144
	Sample_Button_List=#()
	function get_Now_Color=
	(
			a=filein ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Setting_Info.ms")
			return a
	)
	nowcolor=get_Now_Color()
	Original_Button_Width=nowcolor[9]
	Original_Button_Height=nowcolor[10]
	Original_Font=nowcolor[7]
	Original_Font2=dotnetobject "System.Drawing.Font" "" (Original_Font.size-1)
	
	function get_preset_List_Array=
	(
		preset_List.items.clear()
		function Load_Color_Preset=
		(
			a=filein ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Color_Preset.ms")
			return a
		)
		Color_Preset=Load_Color_Preset()
		Color_Preset_List=#()
		for i in Color_Preset do
		(
			append Color_Preset_List i._name 
		)
		for i in Color_Preset_List do
		(
			preset_List.items.add i
		)
	)
 	function Apply_to_Sample=
	(
		for i in Sample_Button_List do
		(
			i.Backcolor=Back_Color_Button.backcolor
			i.flatappearance.bordercolor=Border_Color_Button.backcolor
			i.ForeColor=Text_Color_Button.backcolor
			i.font=dotnetobject "System.Drawing.Font" "" (Font_Size_Spinner.value)
		)
		Sample_Button_List[1].font=dotnetobject "System.Drawing.Font" "" (Font_Size_Spinner.value-1)
		Sample_Button_List[2].font=Sample_Button_List[1].font
		Sample_Button_List[3].font=Sample_Button_List[1].font
		Sample_Button_List[4].font=Sample_Button_List[1].font
		Sample_Button_List[3].Backcolor=Help_Color_Button.backcolor
		Sample_Button_List[4].Backcolor=Fix_Color_Button.backcolor
		Sample_Button_List[9].forecolor=Disfocus_Color_Button.backcolor
		Sample_Button_List[10].forecolor=Disfocus_Color_Button.backcolor
		Sample_Button_List[11].forecolor=Disfocus_Color_Button.backcolor
		
		Sample_Button_List[1].size=dotNetObject "System.Drawing.Size" (Button_Width.value/4) Button_Height.value
		Sample_Button_List[1].Location=dotNetObject "System.Drawing.Point" (Position_1+10) (Position_y+20)
		Sample_Button_List[2].size=dotNetObject "System.Drawing.Size" (Button_Width.value/4) Button_Height.value
		Sample_Button_List[2].Location=dotNetObject "System.Drawing.Point" (Position_1+10+(Button_Width.value/4*1)) (Position_y+20)
		Sample_Button_List[3].size=dotNetObject "System.Drawing.Size" (Button_Width.value/4) Button_Height.value
		Sample_Button_List[3].Location=dotNetObject "System.Drawing.Point" (Position_1+10+(Button_Width.value/4*2)) (Position_y+20)
		Sample_Button_List[4].size=dotNetObject "System.Drawing.Size" (Button_Width.value/4) Button_Height.value
		Sample_Button_List[4].Location=dotNetObject "System.Drawing.Point" (Position_1+10+(Button_Width.value/4*3)) (Position_y+20)
		
		Sample_Button_List[5].size=dotNetObject "System.Drawing.Size" (Button_Width.value) Button_Height.value
		Sample_Button_List[5].Location=dotNetObject "System.Drawing.Point" (Position_1+10) (Position_y+20+Button_Height.value*1)			
		Sample_Button_List[6].size=dotNetObject "System.Drawing.Size" (Button_Width.value/2) Button_Height.value
		Sample_Button_List[6].Location=dotNetObject "System.Drawing.Point" (Position_1+10) (Position_y+20+Button_Height.value*2)
		Sample_Button_List[7].size=dotNetObject "System.Drawing.Size" (Button_Width.value/2) Button_Height.value
		Sample_Button_List[7].Location=dotNetObject "System.Drawing.Point" (Position_1+10+Button_Width.value/2) (Position_y+20+Button_Height.value*2)
		Sample_Button_List[8].size=dotNetObject "System.Drawing.Size" (Button_Width.value) Button_Height.value
		Sample_Button_List[8].Location=dotNetObject "System.Drawing.Point" (Position_1+10) (Position_y+20+Button_Height.value*3)
		Sample_Button_List[9].size=dotNetObject "System.Drawing.Size" (Button_Width.value) Button_Height.value
		Sample_Button_List[9].Location=dotNetObject "System.Drawing.Point" (Position_1+10) (Position_y+20+Button_Height.value*4)			
		Sample_Button_List[10].size=dotNetObject "System.Drawing.Size" (Button_Width.value/2) Button_Height.value
		Sample_Button_List[10].Location=dotNetObject "System.Drawing.Point" (Position_1+10) (Position_y+20+Button_Height.value*5)
		Sample_Button_List[11].size=dotNetObject "System.Drawing.Size" (Button_Width.value/2) Button_Height.value
		Sample_Button_List[11].Location=dotNetObject "System.Drawing.Point" (Position_1+10+Button_Width.value/2) (Position_y+20+Button_Height.value*5)


	)
	
	(
	Design_BTN.BackColor = (DotNetClass  "System.Drawing.Color").FromArgb 220 100 40	
				
		
	Sample_Label = dotnetobject "System.Windows.Forms.label"
	Sample_Label.text="Sample"
	Sample_Label.flatStyle=Sample_Label.flatStyle.Popup
	--Sample_Label.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Sample_Label.size=dotNetObject "System.Drawing.Size" 80 15
	Sample_Label.Location=dotnetobject "System.Drawing.Point" (Position_1)  (Position_y+5)
	Sample_Label.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Sample_Label
	append Form_List Sample_Label
		
	Sample_util_Button1 = dotnetobject "System.Windows.Forms.button"
	Sample_util_Button1.text="U"
	Sample_util_Button1.flatStyle=Sample_util_Button1.flatStyle.flat
	--Sample_Button1.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Sample_util_Button1.size=dotNetObject "System.Drawing.Size" (Original_Button_Width/4) Original_Button_Height
	Sample_util_Button1.Location=dotnetobject "System.Drawing.Point" (Position_1+70) (Position_y+60)
	Sample_util_Button1.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	Sample_util_Button1.Font=Original_Font_1
	helpForm.controls.add Sample_util_Button1
	append Form_List Sample_util_Button1
	append Sample_Button_List Sample_util_Button1
	
	Sample_Mod_Button1 = dotnetobject "System.Windows.Forms.button"
	Sample_Mod_Button1.text="M"
	Sample_Mod_Button1.flatStyle=Sample_Mod_Button1.flatStyle.flat
	--Sample_Button1.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Sample_Mod_Button1.size=dotNetObject "System.Drawing.Size" (Original_Button_Width/4) Original_Button_Height
	Sample_Mod_Button1.Location=dotnetobject "System.Drawing.Point" (Position_1+70+(Original_Button_Width/4*1)) (Position_y+60)
	Sample_Mod_Button1.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	Sample_Mod_Button1.Font=Original_Font_1
	helpForm.controls.add Sample_Mod_Button1
	append Form_List Sample_Mod_Button1
	append Sample_Button_List Sample_Mod_Button1
	
	Sample_Help_Button1 = dotnetobject "System.Windows.Forms.button"
	Sample_Help_Button1.text="H"
	Sample_Help_Button1.flatStyle=Sample_Help_Button1.flatStyle.flat
	--Sample_Button1.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Sample_Help_Button1.size=dotNetObject "System.Drawing.Size" (Original_Button_Width/4) Original_Button_Height
	Sample_Help_Button1.Location=dotnetobject "System.Drawing.Point" (Position_1+70+(Original_Button_Width/4*2)) (Position_y+60)
	Sample_Help_Button1.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	Sample_Help_Button1.Font=Original_Font_1
	helpForm.controls.add Sample_Help_Button1
	append Form_List Sample_Help_Button1
	append Sample_Button_List Sample_Help_Button1
	
	Sample_Fix_Button1 = dotnetobject "System.Windows.Forms.button"
	Sample_Fix_Button1.text="F"
	Sample_Fix_Button1.flatStyle=Sample_Fix_Button1.flatStyle.flat
	--Sample_Button1.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Sample_Fix_Button1.size=dotNetObject "System.Drawing.Size" (Original_Button_Width/4) Original_Button_Height
	Sample_Fix_Button1.Location=dotnetobject "System.Drawing.Point" (Position_1+70+(Original_Button_Width/4*3)) (Position_y+60)
	Sample_Fix_Button1.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	Sample_Fix_Button1.Font=Original_Font_1
	helpForm.controls.add Sample_Fix_Button1
	append Form_List Sample_Fix_Button1
	append Sample_Button_List Sample_Fix_Button1
	
	Sample_Button1 = dotnetobject "System.Windows.Forms.button"
	Sample_Button1.text="Sample Button"
	Sample_Button1.flatStyle=Sample_Button1.flatStyle.flat
	--Sample_Button1.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Sample_Button1.size=dotNetObject "System.Drawing.Size" Original_Button_Width Original_Button_Height
	Sample_Button1.Location=dotnetobject "System.Drawing.Point" (Position_1+70) (Position_y+60+30)
	Sample_Button1.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Sample_Button1
	append Form_List Sample_Button1
	append Sample_Button_List Sample_Button1

	Sample_Button6 = dotnetobject "System.Windows.Forms.button"
	Sample_Button6.text="Sample"
	Sample_Button6.flatStyle=Sample_Button6.flatStyle.flat
	--Sample_Button6.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Sample_Button6.size=dotNetObject "System.Drawing.Size" (Original_Button_Width/2) Original_Button_Height
	Sample_Button6.Location=dotnetobject "System.Drawing.Point" (Position_1+70) (Position_y+60+30+30)
	Sample_Button6.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Sample_Button6
	append Form_List Sample_Button6
	append Sample_Button_List Sample_Button6

	Sample_Button3 = dotnetobject "System.Windows.Forms.button"
	Sample_Button3.text="Sample"
	Sample_Button3.flatStyle=Sample_Button3.flatStyle.flat
	--Sample_Button3.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Sample_Button3.size=dotNetObject "System.Drawing.Size" (Original_Button_Width/2) Original_Button_Height
	Sample_Button3.Location=dotnetobject "System.Drawing.Point" (Position_1+70+(Original_Button_Width/2)) (Position_y+60+30+30)
	Sample_Button3.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Sample_Button3
	append Form_List Sample_Button3
	append Sample_Button_List Sample_Button3
	
	Sample_Button4 = dotnetobject "System.Windows.Forms.button"
	Sample_Button4.text="Sample Button"
	Sample_Button4.flatStyle=Sample_Button4.flatStyle.flat
	--Sample_Button4.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Sample_Button4.size=dotNetObject "System.Drawing.Size" Original_Button_Width Original_Button_Height
	Sample_Button4.Location=dotnetobject "System.Drawing.Point" (Position_1+70) (Position_y+60+30+30+30)
	Sample_Button4.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Sample_Button4
	append Form_List Sample_Button4
	append Sample_Button_List Sample_Button4
		
	Sample_Button5 = dotnetobject "System.Windows.Forms.button"
	Sample_Button5.text="DisFocus"
	Sample_Button5.flatStyle=Sample_Button5.flatStyle.flat
	--Sample_Button5.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Sample_Button5.size=dotNetObject "System.Drawing.Size" Original_Button_Width Original_Button_Height
	Sample_Button5.Location=dotnetobject "System.Drawing.Point" (Position_1+70) (Position_y+60+30+30+30+30)
	Sample_Button5.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Sample_Button5
	append Form_List Sample_Button5
	append Sample_Button_List Sample_Button5

	Sample_Button2 = dotnetobject "System.Windows.Forms.button"
	Sample_Button2.text="DisFocus"
	Sample_Button2.flatStyle=Sample_Button2.flatStyle.flat
	--Sample_Button2.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Sample_Button2.size=dotNetObject "System.Drawing.Size" (Original_Button_Width/2) Original_Button_Height
	Sample_Button2.Location=dotnetobject "System.Drawing.Point" (Position_1+70) (Position_y+60+30+30+30+30+30)
	Sample_Button2.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Sample_Button2
	append Form_List Sample_Button2
	append Sample_Button_List Sample_Button2

	Sample_Button7 = dotnetobject "System.Windows.Forms.button"
	Sample_Button7.text="DisFocus"
	Sample_Button7.flatStyle=Sample_Button7.flatStyle.flat
	--Sample_Button7.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Sample_Button7.size=dotNetObject "System.Drawing.Size" (Original_Button_Width/2) Original_Button_Height
	Sample_Button7.Location=dotnetobject "System.Drawing.Point" (Position_1+70+(Original_Button_Width/2)) (Position_y+60+30+30+30+30+30)
	Sample_Button7.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Sample_Button7
	append Form_List Sample_Button7
	append Sample_Button_List Sample_Button7
			
		
	Button_Width_Label = dotnetobject "System.Windows.Forms.label"
	Button_Width_Label.text="Button Width"
	Button_Width_Label.flatStyle=Button_Width_Label.flatStyle.Popup
	--Button_Width_Label.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Button_Width_Label.size=dotNetObject "System.Drawing.Size" 80 20
	Button_Width_Label.Location=dotnetobject "System.Drawing.Point" (Position_1) (Position_y+360)
	Button_Width_Label.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Button_Width_Label
	append Form_List Button_Width_Label
		
	Button_Width = dotnetobject "system.windows.forms.numericUpDown"
	Button_Width.text="Button Width"
	--Button_Width.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Button_Width.size=dotNetObject "System.Drawing.Size" 70 20
	Button_Width.Location=dotnetobject "System.Drawing.Point" (Position_1) (Position_y+380)
	Button_Width.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	Button_Width.forecolor=(DotNetClass  "System.Drawing.Color").FromArgb 255 255 255
	Button_Width.Maximum=400
	Button_Width.Increment=4
	Button_Width.value=Original_Button_Width
	helpForm.controls.add Button_Width
	append Form_List Button_Width
			
	Button_height_Label = dotnetobject "System.Windows.Forms.label"
	Button_height_Label.text="Button Height"
	Button_height_Label.flatStyle=Button_height_Label.flatStyle.Popup
	--Button_height_Label.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Button_height_Label.size=dotNetObject "System.Drawing.Size" 84 20
	Button_height_Label.Location=dotnetobject "System.Drawing.Point" (Position_1+90) (Position_y+360)
	Button_height_Label.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Button_height_Label
	append Form_List Button_height_Label
		
	Button_height = dotnetobject "system.windows.forms.numericUpDown"
	Button_height.text="Button Width"
	--Button_height.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Button_height.size=dotNetObject "System.Drawing.Size" 70 20
	Button_height.Location=dotnetobject "System.Drawing.Point" (Position_1+90) (Position_y+380)
	Button_height.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	Button_height.forecolor=(DotNetClass  "System.Drawing.Color").FromArgb 255 255 255
	Button_height.Maximum=400
	Button_height.Increment=1
	Button_Height.value=Original_Button_Height
	helpForm.controls.add Button_height
	append Form_List Button_height
	
	Font_Size_Label = dotnetobject "System.Windows.Forms.label"
	Font_Size_Label.text="Font Size"
	Font_Size_Label.flatStyle=Font_Size_Label.flatStyle.Popup
	--Font_Size_Label.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Font_Size_Label.size=dotNetObject "System.Drawing.Size" 80 20
	Font_Size_Label.Location=dotnetobject "System.Drawing.Point" (Position_1+180) (Position_y+360)
	Font_Size_Label.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Font_Size_Label
	append Form_List Font_Size_Label
		
	Font_Size_Spinner = dotnetobject "system.windows.forms.numericUpDown"
	Font_Size_Spinner.text="Button Width"
	--Font_Size_Spinner.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Font_Size_Spinner.size=dotNetObject "System.Drawing.Size" 70 20
	Font_Size_Spinner.Location=dotnetobject "System.Drawing.Point" (Position_1+180) (Position_y+380)
	Font_Size_Spinner.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	Font_Size_Spinner.forecolor=(DotNetClass  "System.Drawing.Color").FromArgb 255 255 255
	Font_Size_Spinner.Maximum=400
	Font_Size_Spinner.Increment=1
	Font_Size_Spinner.value=(Original_Font.size as integer)
	helpForm.controls.add Font_Size_Spinner
	append Form_List Font_Size_Spinner
	
		
	Back_Color_Label = dotnetobject "System.Windows.Forms.label"
	Back_Color_Label.text="Button Color"
	Back_Color_Label.flatStyle=Back_Color_Label.flatStyle.Popup
	--Back_Color_Label.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Back_Color_Label.size=dotNetObject "System.Drawing.Size" 90 20
	Back_Color_Label.Location=dotnetobject "System.Drawing.Point" (Position_3) (Position_y+10)
	Back_Color_Label.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Back_Color_Label
	append Form_List Back_Color_Label

	Back_Color_Button = dotnetobject "System.Windows.Forms.button"
	Back_Color_Button.text=""
	Back_Color_Button.flatStyle=Back_Color_Button.flatStyle.Popup
	--Back_Color_Button.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Back_Color_Button.size=dotNetObject "System.Drawing.Size" 90 30
	Back_Color_Button.Location=dotnetobject "System.Drawing.Point" (Position_3) (Position_y+10+20)
	Back_Color_Button.Backcolor=nowcolor[1]
	helpForm.controls.add Back_Color_Button
	append Form_List Back_Color_Button
	
	Help_Color_Label = dotnetobject "System.Windows.Forms.label"
	Help_Color_Label.text="Help Button Color"
	Help_Color_Label.flatStyle=Help_Color_Label.flatStyle.Popup
	--Help_Color_Label.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Help_Color_Label.size=dotNetObject "System.Drawing.Size" 110 20
	Help_Color_Label.Location=dotnetobject "System.Drawing.Point" (Position_3+110) (Position_y+10)
	Help_Color_Label.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Help_Color_Label
	append Form_List Help_Color_Label

	Help_Color_Button = dotnetobject "System.Windows.Forms.button"
	Help_Color_Button.text=""
	Help_Color_Button.flatStyle=Help_Color_Button.flatStyle.Popup
	--Help_Color_Button.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Help_Color_Button.size=dotNetObject "System.Drawing.Size" 90 30
	Help_Color_Button.Location=dotnetobject "System.Drawing.Point" (Position_3+110) (Position_y+10+20)
	Help_Color_Button.Backcolor=nowcolor[2]
	helpForm.controls.add Help_Color_Button
	append Form_List Help_Color_Button
	
	Fix_Color_Label = dotnetobject "System.Windows.Forms.label"
	Fix_Color_Label.text="Fix Button Color"
	Fix_Color_Label.flatStyle=Fix_Color_Label.flatStyle.Popup
	--Fix_Color_Label.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Fix_Color_Label.size=dotNetObject "System.Drawing.Size" 110 20
	Fix_Color_Label.Location=dotnetobject "System.Drawing.Point" (Position_3) (Position_y+10+60)
	Fix_Color_Label.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Fix_Color_Label
	append Form_List Fix_Color_Label

	Fix_Color_Button = dotnetobject "System.Windows.Forms.button"
	Fix_Color_Button.text=""
	Fix_Color_Button.flatStyle=Fix_Color_Button.flatStyle.Popup
	--Fix_Color_Button.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Fix_Color_Button.size=dotNetObject "System.Drawing.Size" 90 30
	Fix_Color_Button.Location=dotnetobject "System.Drawing.Point" (Position_3) (Position_y+10+20+60)
	Fix_Color_Button.Backcolor=nowcolor[3]
	helpForm.controls.add Fix_Color_Button
	append Form_List Fix_Color_Button
	
	Border_Color_Label = dotnetobject "System.Windows.Forms.label"
	Border_Color_Label.text="Border Color"
	Border_Color_Label.flatStyle=Border_Color_Label.flatStyle.Popup
	--Border_Color_Label.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Border_Color_Label.size=dotNetObject "System.Drawing.Size" 110 20
	Border_Color_Label.Location=dotnetobject "System.Drawing.Point" (Position_3+110) (Position_y+10+60)
	Border_Color_Label.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Border_Color_Label
	append Form_List Border_Color_Label

	Border_Color_Button = dotnetobject "System.Windows.Forms.button"
	Border_Color_Button.text=""
	Border_Color_Button.flatStyle=Border_Color_Button.flatStyle.Popup
	--Border_Color_Button.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Border_Color_Button.size=dotNetObject "System.Drawing.Size" 90 30
	Border_Color_Button.Location=dotnetobject "System.Drawing.Point" (Position_3+110) (Position_y+10+60+20)
	Border_Color_Button.Backcolor=nowcolor[4]
	helpForm.controls.add Border_Color_Button
	append Form_List Border_Color_Button
	
	Text_Color_Label = dotnetobject "System.Windows.Forms.label"
	Text_Color_Label.text="Text Color"
	Text_Color_Label.flatStyle=Text_Color_Label.flatStyle.Popup
	--Text_Color_Label.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Text_Color_Label.size=dotNetObject "System.Drawing.Size" 110 20
	Text_Color_Label.Location=dotnetobject "System.Drawing.Point" (Position_3) (Position_y+10+120)
	Text_Color_Label.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Text_Color_Label
	append Form_List Text_Color_Label

	Text_Color_Button = dotnetobject "System.Windows.Forms.button"
	Text_Color_Button.text=""
	Text_Color_Button.flatStyle=Text_Color_Button.flatStyle.Popup
	--Text_Color_Button.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Text_Color_Button.size=dotNetObject "System.Drawing.Size" 90 30
	Text_Color_Button.Location=dotnetobject "System.Drawing.Point" (Position_3) (Position_y+10+120+20)
	Text_Color_Button.Backcolor=nowcolor[5]
	helpForm.controls.add Text_Color_Button
	append Form_List Text_Color_Button
	
	Disfocus_Label = dotnetobject "System.Windows.Forms.label"
	Disfocus_Label.text="DisFocus Text Color"
	Disfocus_Label.flatStyle=Disfocus_Label.flatStyle.Popup
	--Disfocus_Label.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Disfocus_Label.size=dotNetObject "System.Drawing.Size" 130 20
	Disfocus_Label.Location=dotnetobject "System.Drawing.Point" (Position_3+110) (Position_y+10+120)
	Disfocus_Label.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Disfocus_Label
	append Form_List Disfocus_Label

	Disfocus_Color_Button = dotnetobject "System.Windows.Forms.button"
	Disfocus_Color_Button.text=""
	Disfocus_Color_Button.flatStyle=Disfocus_Color_Button.flatStyle.Popup
	--Disfocus_Color_Button.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Disfocus_Color_Button.size=dotNetObject "System.Drawing.Size" 90 30
	Disfocus_Color_Button.Location=dotnetobject "System.Drawing.Point" (Position_3+110) (Position_y+10+120+20)
	Disfocus_Color_Button.Backcolor=nowcolor[6]
	helpForm.controls.add Disfocus_Color_Button
	append Form_List Disfocus_Color_Button
	
	Color_Save = dotnetobject "System.Windows.Forms.button"
	Color_Save.text="Apply"
	Color_Save.flatStyle=Color_Save.flatStyle.Popup
	--Color_Save.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Color_Save.size=dotNetObject "System.Drawing.Size" 200 30
	Color_Save.Location=dotnetobject "System.Drawing.Point" Position_3 (Position_y+10+120+20+40)
	Color_Save.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Color_Save
	append Form_List Color_Save
	
	
	Preset_Label = dotnetobject "System.Windows.Forms.label"
	Preset_Label.text="Preset"
	Preset_Label.flatStyle=Preset_Label.flatStyle.Popup
	--Preset_Label.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Preset_Label.size=dotNetObject "System.Drawing.Size" 200 20
	Preset_Label.Location=dotnetobject "System.Drawing.Point" Position_3 (Position_y+200+40)
	Preset_Label.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Preset_Label
	append Form_List Preset_Label
	
	preset_List = dotNetObject "System.Windows.Forms.ListBox" pos:[0,0]
	preset_List.text="Buttons List"
	preset_List.size=dotNetObject "System.Drawing.Size" 200 80
	--preset_List.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	preset_List.Location=dotnetobject "System.Drawing.Point" Position_3 (Position_y+220+40)
	preset_List.BackColor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	preset_List.Forecolor=(DotNetClass  "System.Drawing.Color").FromArgb 255 255 255
	preset_List.BorderStyle= (dotnetclass "System.Windows.Forms.BorderStyle").Fixed3D
	get_preset_List_Array()
	helpForm.controls.add preset_List
	append Form_List preset_List
	
	preset_Apply = dotnetobject "System.Windows.Forms.button"
	preset_Apply.text="Load Preset"
	preset_Apply.flatStyle=preset_Apply.flatStyle.Popup
	--preset_Apply.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	preset_Apply.size=dotNetObject "System.Drawing.Size" 100 30
	preset_Apply.Location=dotnetobject "System.Drawing.Point" Position_3 (Position_y+220+80+40)
	preset_Apply.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add preset_Apply
	append Form_List preset_Apply
	
	preset_Save = dotnetobject "System.Windows.Forms.button"
	preset_Save.text="New Preset"
	preset_Save.flatStyle=preset_Save.flatStyle.Popup
	--preset_Save.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	preset_Save.size=dotNetObject "System.Drawing.Size" 100 30
	preset_Save.Location=dotnetobject "System.Drawing.Point" (Position_3+100) (Position_y+220+80+40)
	preset_Save.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add preset_Save
	append Form_List preset_Save

	preset_Rename = dotnetobject "System.Windows.Forms.button"
	preset_Rename.text="Rename"
	preset_Rename.flatStyle=preset_Rename.flatStyle.Popup
	--preset_Rename.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	preset_Rename.size=dotNetObject "System.Drawing.Size" 100 30
	preset_Rename.Location=dotnetobject "System.Drawing.Point" Position_3 (Position_y+220+80+30+40)
	preset_Rename.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add preset_Rename
	append Form_List preset_Rename

	preset_Delete = dotnetobject "System.Windows.Forms.button"
	preset_Delete.text="Delete"
	preset_Delete.flatStyle=preset_Delete.flatStyle.Popup
	--preset_Delete.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	preset_Delete.size=dotNetObject "System.Drawing.Size" 100 30
	preset_Delete.Location=dotnetobject "System.Drawing.Point" (Position_3+100) (Position_y+220+80+30+40)
	preset_Delete.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add preset_Delete
	append Form_List preset_Delete
	
	
		
	Info_Box= dotNetObject "System.Windows.Forms.RichTextBox" pos:[0,0]
	Info_Box.Location=dotnetobject "System.Drawing.Point" 180 10
	Info_Box.size=dotNetObject "System.Drawing.Size" 595 434
	Info_Box.BackColor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	Info_Box.BorderStyle= (dotnetclass "System.Windows.Forms.BorderStyle").None
	Info_Box.Readonly=true
	helpForm.controls.add Info_Box
	append Form_List Info_Box
	
	
	)--All of Button
	
	
	

	fn Back_Color_Button_Event=
	(
		color_dialog=dotnetobject "System.Windows.Forms.ColorDialog"
		color_dialog.AllowFullOpen=true
		color_dialog.ShowDialog()
		_color=#(color_dialog.Color.r,color_dialog.Color.g,color_dialog.Color.b)
		Back_Color_Button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb _color[1] _color[2] _color[3]
		Apply_to_Sample()
	)
	fn Help_Color_Button_Event=
	(
		color_dialog=dotnetobject "System.Windows.Forms.ColorDialog"
		color_dialog.ShowDialog()
		_color=#(color_dialog.Color.r,color_dialog.Color.g,color_dialog.Color.b)
		Help_Color_Button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb _color[1] _color[2] _color[3]
		Apply_to_Sample()
	)
	fn Fix_Color_Button_Event=
	(
		color_dialog=dotnetobject "System.Windows.Forms.ColorDialog"
		color_dialog.ShowDialog()
		_color=#(color_dialog.Color.r,color_dialog.Color.g,color_dialog.Color.b)	
		Fix_Color_Button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb _color[1] _color[2] _color[3]	
		Apply_to_Sample()
	)
	fn Border_Color_Button_Event=
	(
		color_dialog=dotnetobject "System.Windows.Forms.ColorDialog"
		color_dialog.ShowDialog()
		_color=#(color_dialog.Color.r,color_dialog.Color.g,color_dialog.Color.b)	
		Border_Color_Button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb _color[1] _color[2] _color[3]	
		Apply_to_Sample()
	)
	fn Text_Color_Button_Event=
	(
		color_dialog=dotnetobject "System.Windows.Forms.ColorDialog"
		color_dialog.ShowDialog()
		_color=#(color_dialog.Color.r,color_dialog.Color.g,color_dialog.Color.b)	
		Text_Color_Button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb _color[1] _color[2] _color[3]	
		Apply_to_Sample()
	)
	fn Disfocus_Color_Button_Event=
	(
		color_dialog=dotnetobject "System.Windows.Forms.ColorDialog"
		color_dialog.ShowDialog()
		_color=#(color_dialog.Color.r,color_dialog.Color.g,color_dialog.Color.b)	
		Disfocus_Color_Button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb _color[1] _color[2] _color[3]	
		Apply_to_Sample()
	)
	fn Color_Save_Event=
	(
		aa=openfile ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Setting_Info.ms") mode:"w"
		format "(\nbgcolor=(DotNetClass \"System.Drawing.Color\").FromArgb " to:aa
		format "% % %" (Back_Color_Button.Backcolor.r) (Back_Color_Button.Backcolor.g) (Back_Color_Button.Backcolor.b) to:aa
		format "\nbgcolor2=(DotNetClass \"System.Drawing.Color\").FromArgb " to:aa
		format "% % %" (Help_Color_Button.Backcolor.r) (Help_Color_Button.Backcolor.g) (Help_Color_Button.Backcolor.b) to:aa		
		format "\nbgcolor3=(DotNetClass \"System.Drawing.Color\").FromArgb " to:aa
		format "% % %" (Fix_Color_Button.Backcolor.r) (Fix_Color_Button.Backcolor.g) (Fix_Color_Button.Backcolor.b) to:aa			
		format "\nbordercolor=(DotNetClass \"System.Drawing.Color\").FromArgb " to:aa
		format "% % %" (Border_Color_Button.Backcolor.r) (Border_Color_Button.Backcolor.g) (Border_Color_Button.Backcolor.b) to:aa			
		format "\nFontColor=(DotNetClass \"System.Drawing.Color\").FromArgb " to:aa
		format "% % %" (Text_Color_Button.Backcolor.r) (Text_Color_Button.Backcolor.g) (Text_Color_Button.Backcolor.b) to:aa		
		format "\nDisfocusFontColor=(DotNetClass \"System.Drawing.Color\").FromArgb " to:aa
		format "% % %" (Disfocus_Color_Button.Backcolor.r) (Disfocus_Color_Button.Backcolor.g) (Disfocus_Color_Button.Backcolor.b) to:aa		
		format "\nOriginal_Font=dotnetobject \"System.Drawing.Font\" \"\" %" Font_Size_Spinner.value to:aa
		format "\n_Height=%" Button_Height.value to:aa
		format "\n_Width=%" Button_Width.value to:aa
		format "\n#(bgcolor,bgcolor2,bgcolor3,BorderColor,FontColor,DisfocusFontColor,Original_Font,Original_Font_1,_Width,_Height) \n)" to:aa
		
		close aa
	)	
	fn Preset_Apply_Event=
	(
		if (Preset_List.selectedIndex==-1) do (return false)
		a=Color_Preset[Preset_List.selectedIndex+1]
		Back_Color_Button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb a.bg[1] a.bg[2] a.bg[3]
		Help_Color_Button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb a.bg[4] a.bg[5] a.bg[6]
		Fix_Color_Button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb a.bg[7] a.bg[8] a.bg[9]
		Border_Color_Button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb a.bg[10] a.bg[11] a.bg[12]
		Text_Color_Button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb a.ft[1] a.ft[2] a.ft[3]
		Disfocus_Color_Button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb a.ft[4] a.ft[5] a.ft[6]
		Button_Width.value=a.info[1]
		Button_Height.value=a.info[2]
		Font_Size_Spinner.value=a.info[3]
		
		Apply_to_Sample()
	)
	fn Render_Preset=
	(
		global aa
		aa=openfile ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Color_Preset.ms") mode:"w"
		format "struct colorpreset (_name,bg,ft,info)" to:aa
		format "\narr=#()" to:aa
		format "\nfunction addcolorpreset n b f i=" to:aa
		format "\n(\n\tappend arr (colorpreset _name:n bg:b ft:f info:i)\n)\n" to:aa
		for i in Color_Preset do
		(
			format "\naddcolorpreset \"%\" % % %" i._name i.bg i.ft i.info to:aa
		)
		format "\n\nreturn arr" to:aa
		close aa
		get_preset_List_Array()
	)
	fn Preset_Save_Event=
	(
		_newname_=(Dialog_modal "Want Name" "")
		if (_newname_=="") do (return false)
		struct colorpreset (_name,bg,ft,info)
		current_bg=#(Back_Color_Button.backcolor.r,Back_Color_Button.backcolor.g,Back_Color_Button.backcolor.b,
						Help_Color_Button.backcolor.r,Help_Color_Button.backcolor.g,Help_Color_Button.backcolor.b,
						Fix_Color_Button.Backcolor.r,Fix_Color_Button.Backcolor.g,Fix_Color_Button.Backcolor.b,
						Border_Color_Button.backcolor.r,Border_Color_Button.backcolor.g,Border_Color_Button.backcolor.b
						)
						
		current_ft=#(Text_Color_Button.backcolor.r,Text_Color_Button.backcolor.g,Text_Color_Button.backcolor.b,
						Disfocus_Color_Button.backcolor.r,Disfocus_Color_Button.backcolor.g,Disfocus_Color_Button.backcolor.b
						)
		current_info=#(Button_Width.value,Button_Height.value,Font_Size_Spinner.value)
		append Color_Preset (colorpreset _name:_newname_ bg:current_bg ft:current_ft info:current_info)
		Render_Preset()
	)	
	fn Preset_Rename_Event=
	(
		if (Preset_List.selectedIndex==-1) do (Messagebox "Select Preset"; return false)
		a=Color_Preset[Preset_List.selectedIndex+1]
		_newname_=(Dialog_modal "Want Name" "")
		if (_newname_=="") do (return false)
		a._name=_newname_
		Render_Preset()
	)	
	fn Preset_Delete_Event=
	(
		if ((YNC_Messagebox "Really Want Delete This?")!=#yes) do (return false)
		if (Preset_List.selectedIndex==-1) do (Messagebox "Select Preset"; return false)
		deleteitem Color_Preset (Preset_List.selectedIndex+1)
		Render_Preset()
	)	
	fn Chane_Value_Event=
	(
		Apply_to_Sample()
	)
	
	dotnet.AddEventHandler Back_Color_Button "Click" Back_Color_Button_Event
	dotnet.AddEventHandler Help_Color_Button "Click" Help_Color_Button_Event
	dotnet.AddEventHandler Fix_Color_Button "Click" Fix_Color_Button_Event
	dotnet.AddEventHandler Border_Color_Button "Click" Border_Color_Button_Event
	dotnet.AddEventHandler Text_Color_Button "Click" Text_Color_Button_Event
	dotnet.AddEventHandler Disfocus_Color_Button "Click" Disfocus_Color_Button_Event
	dotnet.AddEventHandler Color_Save "Click" Color_Save_Event
	dotnet.AddEventHandler Preset_Apply "Click" Preset_Apply_Event
	dotnet.AddEventHandler Preset_Save "Click" Preset_Save_Event
	dotnet.AddEventHandler Preset_Rename "Click" Preset_Rename_Event
	dotnet.AddEventHandler Preset_Delete "Click" Preset_Delete_Event
	dotnet.AddEventHandler Font_Size_Spinner "ValueChanged" Chane_Value_Event
	dotnet.AddEventHandler Button_Width "ValueChanged" Chane_Value_Event
	dotnet.AddEventHandler Button_Height "ValueChanged" Chane_Value_Event
	
	Apply_to_Sample()
)



---Scripts_Setting
function Category_Setting=(
	
	ss = stringstream ""
 showClass "*:mod*" to:ss
 seek ss 0
 modArr = #()
 while not (eof ss) do (
 	modNm = (readdelimitedstring ss " :")
		 openParenIndex = findString modNm "("
		if openParenIndex != undefined do modNm = substring modNm 1 (openParenIndex - 1)
	 find_error=(findString modNm "(")
	if (find_error!=undefined) do 
	(
		modNm= substring modNm 1 (find_error-1)
	)
 	append modArr modNm
 	skipToNextLine ss
 )
 
	Category_List=modArr
	append Category_List "None"
	append Category_List "Editable Poly"
	append Category_List "Editable Spline"
	append Category_List "BoneGeometry"
	append Category_List "Biped_Object"
	append Category_List "Default"
    append Category_List "1)Favorite"
    append Category_List "2)Favorite"
    append Category_List "3)Favorite"
	--deleteitem Category_List (findItem Category_List "Edit_Poly")
	--deleteitem Category_List (findItem Category_List "Edit_Spline")
 
	sort Category_List
)--Category_List
Button_List=#()
Scripts_List=#()
	local _Selected_Category="All commands"
	local find_string, Category_List_Form, Category_Listbox , Category_Label_Label, Save_button
function Scripts_Setting_View=
(
	Position_y=10
	Position_1=188
	Position_2=188+201
	Position_3=188+201+201
	Scripts_BTN.BackColor = (DotNetClass  "System.Drawing.Color").FromArgb 220 100 40
	Check_Scripts_Setting_Change=true
	Category_Setting()
	Button_List=#()
	Scripts_List=#()
	function Get_Category_List=
	(
		function get_Modify_List=
		(
			a=filein ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_List.ms")
			return a
		)
		Current_Category_list=get_Modify_List()
		Category_List=Category_Setting()
		for i=1 to Category_List.count do
		(
			find=false
			for ii in Current_Category_list do
			(
			if Category_List[i]==ii then (Category_List[i]=("O) "+Category_List[i]); find=true; break)
			)
			if find==false do (Category_List[i]=("   "+Category_List[i]))
		)
		Before_Category=Category_List[1]
		qsort Category_List bsort
	)
	
	function Get_Button_List=
	(
		Script_Box2.items.clear()
		function get_Modify_List=
		(
			__category=substring (Script_Box1.SelectedItem) 4 (Script_Box1.SelectedItem.count)
			if (doesFileExist ((getdir #UserScripts)+"\\P_Scripts\\"+__category+"\\Info\\Add_Button.ms")) then
			(
				a=filein ((getdir #UserScripts)+"\\P_Scripts\\"+__category+"\\Info\\Add_Button.ms")
				return a
			)
			else (return false)
		)
		Modify_List=get_Modify_List()
		if Modify_List==false do (Button_List=#(); return false)
		Button_List=#()
		for i in Modify_List do
		(
			if (i[2]!="") do
			(
				i[1]=(i[1]+" -'"+i[2]+"'")
			)
			if (i[3]!=0 and i[3]!=3) do
			(
				i[1]=("   "+i[1])
			)
			append Button_List i[1]
		)
		for i in Button_List do (Script_Box2.items.add i)
	)
	
	function Get_Scripts_List=
	(
		Script_Box3.items.clear()
		_category=substring (Script_Box1.SelectedItem) 4 (Script_Box1.SelectedItem.count)
		Scripts_List=(getfiles ((getdir #UserScripts)+"\\P_Scripts\\"+_category+"\\*"))
		for i=1 to Scripts_List.count do
		(
			Scripts_List[i]=filenameFromPath Scripts_List[i]
		)
		for i in Scripts_List do (Script_Box3.items.add i)
	)
	
	function Category_Setting_Render=
		(
			arr=#()
			for i in Category_List do
			(
				if i[1]=="O" then (append arr (substring i 4 (i.count)))
			)
			list__=openfile ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_List.ms") mode:"w"
			
			format "( \n\treturn #(" to:list__
			for i in arr do
			(
				format "\"" to:list__
				format i to:list__
				format "\","to:list__
			)
			format "\"None\""to:list__
			format ")\n" to:list__
			format ")" to:list__
			
			close list__
		)----Part of Categor
	
	function Button_Setting_Render=
	(
		function Part_Of_Button=
		(
			Half_Check=0
			arr=#()
			
			
			for i in Button_List do
			(
				title__=""
				Hotkey=""
				across=0
				
				if i[1]==" " and i[2]==" " and i[3]==" " then
				(
					if Half_Check==0 then 
					(
						Half_Check=1
						across=1
						i=(substring i 4 i.count)
						
					)
					else if Half_Check==1 then
					(
						Half_Check=0
						across=2
						i=(substring i 4 i.count)
					)					
				)
				else 
				(
					if Half_Check==1 then
					(
						Half_Check=0
						across=3
					)
				) --check across
				
				if (findstring i " -'")!=undefined then
				(
					title__=substring i 1 (i.count-5)
					Hotkey=i[i.count-1]
				)
				else
				(
					title__=i
				) -- check hotkey
				append arr (#(title__,Hotkey,across))
			)
			
			_Category=(substring Before_Category 4 Before_Category.count)
			if (doesFileExist ((getdir #UserScripts)+"\\P_Scripts\\"+_Category+"\\Info\\Add_Button.ms")==false) do
			(
				makedir ((getdir #UserScripts)+"\\P_Scripts\\"+_Category+"\\Info")
				aa=createfile ((getdir #UserScripts)+"\\P_Scripts\\"+_Category+"\\Info\\Add_Button.ms") 
				close aa
			)
			button_List_File=openfile ((getdir #UserScripts)+"\\P_Scripts\\"+_Category+"\\Info\\Add_Button.ms") mode:"w"
			format "(\n\tlocal NTL=#()\n\tfunction add_button title shortcut across:0=" to:button_List_File	
			format "\n(\n\t\tappend NTL #(title, shortcut, across)\n\t)\n\n" to:button_List_File	
			for i=1 to arr.count do
			(
				if (i==arr.count) and (arr[i][3]==1) do (arr[i][3]=0)
				format "\tadd_button \"%\" \"%\" across:%\n" arr[i][1] arr[i][2] arr[i][3] to:button_List_File
			)
			format "\n\treturn NTL\n)" to:button_List_File	
			close button_List_File
			
			
		)----Part of Buttons
		
		Part_Of_Button()
		--if (Before_Category[1]=="O") do (Part_Of_Button())
		Category_Setting_Render()
		
	)
		
		
		
	Script_Box1_title = dotnetobject "System.Windows.Forms.label"
	Script_Box1_title.text="Category"
	--Script_Box1_title.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box1_title.size=dotNetObject "System.Drawing.Size" 180 20
	Script_Box1_title.Location=dotnetobject "System.Drawing.Point" Position_1 (Position_y)
	helpForm.controls.add Script_Box1_title
	append Form_List Script_Box1_title
		
	Script_Box1_on_off = dotnetobject "System.Windows.Forms.button"
	Script_Box1_on_off.text="On/Off"
	Script_Box1_on_off.flatStyle=Script_Box1_on_off.flatStyle.Popup
	--Script_Box1_on_off.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box1_on_off.size=dotNetObject "System.Drawing.Size" 180 30
	Script_Box1_on_off.Location=dotnetobject "System.Drawing.Point" Position_1 (Position_y+315)
	Script_Box1_on_off.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box1_on_off
	append Form_List Script_Box1_on_off
		
	Script_Box1= dotNetObject "System.Windows.Forms.ListBox" pos:[0,0]
	Script_Box1.Location=dotnetobject "System.Drawing.Point" Position_1 (Position_y+20)
	Script_Box1.size=dotNetObject "System.Drawing.Size" 180 300
	Script_Box1.BackColor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	Script_Box1.BorderStyle= (dotnetclass "System.Windows.Forms.BorderStyle").Fixed3D
	--Script_Box1.Font=dotnetobject "System.Drawing.Font" "Calibri" 13
	Script_Box1.Forecolor=(DotNetClass  "System.Drawing.Color").FromArgb 255 255 255
	
	Script_Box1_Info = dotnetobject "System.Windows.Forms.label"
	Script_Box1_Info.text="You Can Use Up/Down Key"
	--Script_Box1_Info.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box1_Info.size=dotNetObject "System.Drawing.Size" 180 40
	Script_Box1_Info.Location=dotnetobject "System.Drawing.Point" Position_1 (Position_y+315+50)
	helpForm.controls.add Script_Box1_Info
	append Form_List Script_Box1_Info

	Get_Category_List()
	for i in Category_List do (Script_Box1.items.add (i))
	Script_Box1.SetSelected 0 true
		
	helpForm.controls.add Script_Box1
	append Form_List Script_Box1
		
		
	Script_Box2_title = dotnetobject "System.Windows.Forms.label"
	Script_Box2_title.text="Buttons List"
	Script_Box2_title.size=dotNetObject "System.Drawing.Size" 180 20
	--Script_Box2_title.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box2_title.Location=dotnetobject "System.Drawing.Point" Position_2 (Position_y)
	helpForm.controls.add Script_Box2_title
	append Form_List Script_Box2_title
		
	Script_Box2_Delete = dotnetobject "System.Windows.Forms.button"
	Script_Box2_Delete.text="Delete Button"
	Script_Box2_Delete.flatStyle=Script_Box2_Delete.flatStyle.Popup
	--Script_Box2_Title.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box2_Delete.size=dotNetObject "System.Drawing.Size" 180 30
	Script_Box2_Delete.Location=dotnetobject "System.Drawing.Point" (Position_2) (Position_y+315+60)
	Script_Box2_Delete.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box2_Delete
	append Form_List Script_Box2_Delete
		
	Script_Box2_Up = dotnetobject "System.Windows.Forms.button"
	Script_Box2_Up.text="Up"
	Script_Box2_Up.flatStyle=Script_Box2_Up.flatStyle.Popup
	--Script_Box2_Up.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box2_Up.size=dotNetObject "System.Drawing.Size" 90 30
	Script_Box2_Up.Location=dotnetobject "System.Drawing.Point" (Position_2) (Position_y+315+0)
	Script_Box2_Up.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box2_Up
	append Form_List Script_Box2_Up
		
	Script_Box2_Down = dotnetobject "System.Windows.Forms.button"
	Script_Box2_Down.text="Down"
	Script_Box2_Down.flatStyle=Script_Box2_Down.flatStyle.Popup
	--Script_Box2_Down.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box2_Down.size=dotNetObject "System.Drawing.Size" 90 30
	Script_Box2_Down.Location=dotnetobject "System.Drawing.Point" (Position_2+90) (Position_y+315+0)
	Script_Box2_Down.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box2_Down
	append Form_List Script_Box2_Down
		
	Script_Box2_Half = dotnetobject "System.Windows.Forms.button"
	Script_Box2_Half.text="Set Half Size"
	Script_Box2_Half.flatStyle=Script_Box2_Half.flatStyle.Popup
	--Script_Box2_Title.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box2_Half.size=dotNetObject "System.Drawing.Size" 90 30
	Script_Box2_Half.Location=dotnetobject "System.Drawing.Point" (Position_2) (Position_y+315+30)
	Script_Box2_Half.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box2_Half
	append Form_List Script_Box2_Half
		
	Script_Box2_HotKey = dotnetobject "System.Windows.Forms.button"
	Script_Box2_HotKey.text="Set HotKey"
	Script_Box2_HotKey.flatStyle=Script_Box2_HotKey.flatStyle.Popup
	--Script_Box2_HotKey.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box2_HotKey.size=dotNetObject "System.Drawing.Size" 90 30
	Script_Box2_HotKey.Location=dotnetobject "System.Drawing.Point" (Position_2+90) (Position_y+315+30)
	Script_Box2_HotKey.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box2_HotKey
	append Form_List Script_Box2_HotKey

	Script_Box2= dotNetObject "System.Windows.Forms.ListBox" pos:[0,0]
	Script_Box2.Location=dotnetobject "System.Drawing.Point" Position_2 (Position_y+20)
	Script_Box2.size=dotNetObject "System.Drawing.Size" 180 300
	Script_Box2.BackColor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	Script_Box2.BorderStyle= (dotnetclass "System.Windows.Forms.BorderStyle").Fixed3D
	--Script_Box2.Font=dotnetobject "System.Drawing.Font" "Calibri" 13
	Script_Box2.Forecolor=(DotNetClass  "System.Drawing.Color").FromArgb 255 255 255
		
	Save_button = dotnetobject "System.Windows.Forms.button"
	Save_button.text="Save"
	Save_button.flatStyle=Save_button.flatStyle.Popup
	--Save_button.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Save_button.size=dotNetObject "System.Drawing.Size" 180 30
	Save_button.Location=dotnetobject "System.Drawing.Point" Position_2 (Position_y+315+90)
	Save_button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Save_button
	append Form_List Save_button

	Get_Button_List()
		
	helpForm.controls.add Script_Box2
	append Form_List Script_Box2
		
		
	Script_Box3_title = dotnetobject "System.Windows.Forms.label"
	Script_Box3_title.text="Scripts List"
	Script_Box3_title.size=dotNetObject "System.Drawing.Size" 180 20
	--Script_Box3_title.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box3_title.Location=dotnetobject "System.Drawing.Point" Position_3 (Position_y)
	helpForm.controls.add Script_Box3_title
	append Form_List Script_Box3_title
		
	Script_Box3_Button = dotnetobject "System.Windows.Forms.button"
	Script_Box3_Button.text="Make Button"
	Script_Box3_Button.flatStyle=Script_Box3_Button.flatStyle.Popup
	--Script_Box3_Button.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box3_Button.size=dotNetObject "System.Drawing.Size" 180 30
	Script_Box3_Button.Location=dotnetobject "System.Drawing.Point" Position_3 (Position_y+315)
	Script_Box3_Button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box3_Button
	append Form_List Script_Box3_Button
		
	Script_Box3_New = dotnetobject "System.Windows.Forms.button"
	Script_Box3_New.text="New Script"
	Script_Box3_New.flatStyle=Script_Box3_New.flatStyle.Popup
	--Script_Box3_New.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box3_New.size=dotNetObject "System.Drawing.Size" 90 30
	Script_Box3_New.Location=dotnetobject "System.Drawing.Point" Position_3 (Position_y+315+30)
	Script_Box3_New.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box3_New
	append Form_List Script_Box3_New
		
	Script_Box3_From_Macro = dotnetobject "System.Windows.Forms.button"
	Script_Box3_From_Macro.text="From Macro"
	Script_Box3_From_Macro.flatStyle=Script_Box3_From_Macro.flatStyle.Popup
	--Script_Box3_From_Macro.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box3_From_Macro.size=dotNetObject "System.Drawing.Size" 90 30
	Script_Box3_From_Macro.Location=dotnetobject "System.Drawing.Point" (Position_3+90) (Position_y+315+30)
	Script_Box3_From_Macro.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box3_From_Macro
	append Form_List Script_Box3_From_Macro
		
	Script_Box3_Add = dotnetobject "System.Windows.Forms.button"
	Script_Box3_Add.text="Import"
	Script_Box3_Add.flatStyle=Script_Box3_Add.flatStyle.Popup
	--Script_Box3_Add.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box3_Add.size=dotNetObject "System.Drawing.Size" 90 30
	Script_Box3_Add.Location=dotnetobject "System.Drawing.Point" Position_3 (Position_y+315+60)
	Script_Box3_Add.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box3_Add
	append Form_List Script_Box3_Add
		
	Script_Box3_Edit = dotnetobject "System.Windows.Forms.button"
	Script_Box3_Edit.text="Edit"
	Script_Box3_Edit.flatStyle=Script_Box3_Edit.flatStyle.Popup
	--Script_Box3_Edit.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box3_Edit.size=dotNetObject "System.Drawing.Size" 90 30
	Script_Box3_Edit.Location=dotnetobject "System.Drawing.Point" (Position_3+90) (Position_y+315+60)
	Script_Box3_Edit.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box3_Edit
	append Form_List Script_Box3_Edit

	Script_Box3_Delete = dotnetobject "System.Windows.Forms.button"
	Script_Box3_Delete.text="Delete"
	Script_Box3_Delete.flatStyle=Script_Box3_Delete.flatStyle.Popup
	--Script_Box3_Delete.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box3_Delete.size=dotNetObject "System.Drawing.Size" 90 30
	Script_Box3_Delete.Location=dotnetobject "System.Drawing.Point" (Position_3+90) (Position_y+315+90)
	Script_Box3_Delete.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box3_Delete
	append Form_List Script_Box3_Delete
		
	Script_Box3_Rename = dotnetobject "System.Windows.Forms.button"
	Script_Box3_Rename.text="Rename"
	Script_Box3_Rename.flatStyle=Script_Box3_Rename.flatStyle.Popup
	--Script_Box3_Rename.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box3_Rename.size=dotNetObject "System.Drawing.Size" 90 30
	Script_Box3_Rename.Location=dotnetobject "System.Drawing.Point" (Position_3) (Position_y+315+90)
	Script_Box3_Rename.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box3_Rename
	append Form_List Script_Box3_Rename
		
	Script_Box3= dotNetObject "System.Windows.Forms.ListBox" pos:[0,0]
	Script_Box3.Location=dotnetobject "System.Drawing.Point" Position_3 (Position_y+20)
	Script_Box3.size=dotNetObject "System.Drawing.Size" 180 300
	Script_Box3.BackColor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	Script_Box3.BorderStyle= (dotnetclass "System.Windows.Forms.BorderStyle").Fixed3D
	--Script_Box3.Font=dotnetobject "System.Drawing.Font" "Calibri" 13
	Script_Box3.Forecolor=(DotNetClass  "System.Drawing.Color").FromArgb 255 255 255

	Get_Scripts_List()
		
	helpForm.controls.add Script_Box3
	append Form_List Script_Box3

	fn Script_Box1_event=
	(
		if (Check_Buttons_List_Change==true) then
		(
			case (YNC_Messagebox "The button has been modified.\nDo you want to save it?") of
			(
				#yes:
				(
					Save_button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
					Button_Setting_Render()
					Get_Scripts_List()
					Get_Button_List()
					Before_Category=Script_Box1.SelectedItem
					Current_Category_Index=Script_Box1.SelectedIndex
					Check_Buttons_List_Change=false
				)
				#no:
				(
					Save_button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
					Check_Buttons_List_Change=false
					Get_Scripts_List()
					Get_Button_List()
					Before_Category=Script_Box1.SelectedItem
					Current_Category_Index=Script_Box1.SelectedIndex
				)
				#cancel:
				(
					Check_Buttons_List_Change=""
					Script_Box1.SetSelected Current_Category_Index true
				)
			)
		)
		else if (Check_Buttons_List_Change=="") then (Check_Buttons_List_Change=true)
		else 
		(
			Get_Scripts_List()
			Get_Button_List()
			Before_Category=Script_Box1.SelectedItem
			Current_Category_Index=Script_Box1.SelectedIndex
		)
	)
	fn on_off_event=
	(
		item=Script_Box1.SelectedItem
		if item==undefined do (return false)
		if (item[1]=="O") then 
		(
			item[1]=" "; item[2]=" "; item[3]=" ";  Category_List[Script_Box1.SelectedIndex+1]=Item; 
		)
		else 
		(
			item[1]="O"; item[2]=")"; item[3]=" "; Category_List[Script_Box1.SelectedIndex+1]=Item;
		)
		num=Script_Box1.SelectedIndex
		Script_Box1.Items.Clear()
		for i in Category_List do
		(
			Script_Box1.items.add (i)
		)
		Script_Box1.SetSelected num true
		Category_Setting_Render()	
		Script_Box1.focus()
	)
	fn up_event=
	(
		Check_Buttons_List_Change=true
		Save_button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 110 110 200
		if (Script_Box2.SelectedIndex==0) or (Script_Box2.SelectedItem==undefined) do (return false)
		num=(Script_Box2.SelectedIndex-1)
		imsi=Button_List[Script_Box2.SelectedIndex+1]
		Button_List[Script_Box2.SelectedIndex+1]=Button_List[Script_Box2.SelectedIndex]
		Button_List[Script_Box2.SelectedIndex]=imsi
		Script_Box2.Items.Clear()
		for i in Button_List do (Script_Box2.items.add i)
		Script_Box2.SetSelected num true
		Script_Box2.focus()
	)
	fn down_button_event=
	(
		Check_Buttons_List_Change=true
		Save_button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 110 110 200
		if (Script_Box2.SelectedIndex+1==(Script_Box2.items.count)) or (Script_Box2.SelectedItem==undefined) do (return false)
		num=(Script_Box2.SelectedIndex+1)
		imsi=Button_List[Script_Box2.SelectedIndex+1]
		Button_List[Script_Box2.SelectedIndex+1]=Button_List[Script_Box2.SelectedIndex+2]
		Button_List[Script_Box2.SelectedIndex+2]=imsi
		Script_Box2.Items.Clear()
		for i in Button_List do (Script_Box2.items.add i)
		Script_Box2.SetSelected num true
		Script_Box2.focus()
	)
	fn Set_Half_event=
	(
		Check_Buttons_List_Change=true
		Save_button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 110 110 200
		if (Script_Box2.SelectedItem==undefined) do (return false)
		if (matchpattern (Script_Box2.SelectedItem) pattern:"   *") do 
		(
			num=(Script_Box2.SelectedIndex)
			Button_List[Script_Box2.SelectedIndex+1]=substring (Button_List[Script_Box2.SelectedIndex+1]) 4 (Button_List[Script_Box2.SelectedIndex+1]).count
			Script_Box2.Items.Clear()
			for i in Button_List do (Script_Box2.items.add i)
			Script_Box2.SetSelected num true	
			Script_Box2.focus()
			return ture
		)
			num=(Script_Box2.SelectedIndex)
			Button_List[Script_Box2.SelectedIndex+1]="   "+(Button_List[Script_Box2.SelectedIndex+1])
			Script_Box2.Items.Clear()
			for i in Button_List do (Script_Box2.items.add i)
			Script_Box2.SetSelected num true	
			Script_Box2.focus()
	)
	fn Set_HotKey_event=
	(
		Check_Buttons_List_Change=true
		Save_button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 110 110 200
		if (Script_Box2.SelectedItem==undefined) do (return false)
		New_Hotkey=toUpper (Dialog_modal "If You Want Delete Hotkey, Input 'None'" "")
		if (New_HotKey.count!=1) and (New_HotKey!="NONE") do (return false)
		New_HotKey="'"+New_HotKey+"'"
		num=(Script_Box2.SelectedIndex)
		if (matchpattern (Button_List[Script_Box2.SelectedIndex+1]) pattern:"*-'*'") do
		(
			Button_List[Script_Box2.SelectedIndex+1]=substring (Button_List[Script_Box2.SelectedIndex+1]) 1 (Button_List[Script_Box2.SelectedIndex+1].count-5)
		)
		if (New_HotKey!="'NONE'") do (Button_List[Script_Box2.SelectedIndex+1]=(Button_List[Script_Box2.SelectedIndex+1])+" -"+New_HotKey)
		Script_Box2.Items.Clear()
		for i in Button_List do (Script_Box2.items.add i)
		Script_Box2.SetSelected num true	
		Script_Box2.focus()
	)
	fn Delete_Button_event=
	(
		Check_Buttons_List_Change=true
		Save_button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 110 110 200
		if (Script_Box1.SelectedItem==undefined) or (Script_Box2.SelectedItem==undefined) do (return false)
		num=Script_Box2.SelectedIndex
		deleteitem Button_List (Script_Box2.SelectedIndex+1)
		Script_Box2.Items.Clear()
		for i in Button_List do (Script_Box2.items.add i)
		if (Button_List.count==0) then 
		(
					
		)
		else if ((Button_List.count-1)<num) then
		(
			Script_Box2.SetSelected (num-1) true
		)
		else 
		(
			Script_Box2.SetSelected num true
		)
	)
	fn Save_Button_event=
	(
		Check_Buttons_List_Change=false
		Save_button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
		Button_Setting_Render()
		Get_Button_List()
	)
	fn Make_Button_event=
	(
		Check_Buttons_List_Change=true
		Save_button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 110 110 200
		if (Script_Box1.SelectedItem==undefined) or (Script_Box3.SelectedItem==undefined) do (return false)
	
		Current_Script=substring Script_Box3.SelectedItem 1 ((findstring Script_Box3.SelectedItem ".")-1)
		dddd=(Script_Box3.SelectedItem as string)
		ccc=9
		for i=1 to (dddd.count) do
		(
			if dddd[i]=="." then (ccc=i;)
		)
		Current_Script=substring Script_Box3.SelectedItem 1 (ccc-1)
		append Button_List Current_Script
		Script_Box2.Items.Clear()
		for i in Button_List do (Script_Box2.items.add i)
		Script_Box3.focus()
		
	)
	fn New_Script_event=
	(
		if (Script_Box1.SelectedItem==undefined) do (return false)
		New_Name=(Dialog_modal ("New Script's Name") "")
		if (New_Name=="") do (return false)
		
		folder_name=substring (Script_Box1.SelectedItem) 4 (Script_Box1.SelectedItem.count)
		if not (doesFileExist ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name)) then
		(
			makedir ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name)
		)
		a=createfile ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name+"\\"+New_Name+".ms")
		close a
		Get_Scripts_List()
		Script_Box3.focus()
	)
	
	
	fn Script_Box3_From_Macro_event=
	(
		
			
	(

	  fn getMacroScripts =
	  (
		
		-- Setup the in and output
		local macroStream = stringStream ""
		local macroArray = #()
		
		macros.list to:macroStream
		seek macroStream 0
	  
		while not eof macroStream do
		(
			-- Read a line
			local macroLine = readline macroStream
			-- Get the macro number as array
			local macroItem = #(substring macroLine 1 5)
			-- Get the rest of the line
			local macroRest = substring macroLine 6 -1
			-- Make an array of it, filter it by qoutes
			local macroSplit = filterString macroRest "\""
			-- Loop  over the splitted array and clear the whitespace entries
			local macroClean = for macro in macroSplit where macro != " " collect macro
			-- Join the number and the rest of the items
			join macroItem macroClean 
			-- Append to the final macroArray
			append macroArray macroItem
		)
		  -- return macro array
		macroArray
	  )
	  
	  fn arraysort v1 v2=
	  (
		  s=#(v1[2],v2[2])
		  sort s
		  
		  if s[1]==v1[2] then (-1)
		  else (1)
	  )
	  
	  

	function Default_Menu_Setting=
	(

		
	Macro_List_Form = dotNetObject "MaxCustomControls.MaxForm" pos:[0,0]	
	Macro_List_Form.StartPosition = Macro_List_Form.StartPosition.Manual
	arr=windows.getWindowPos (windows.getMAXHWND ()) 
	Macro_List_Form.Location=dotnetobject "System.Drawing.Point" (helpform.location.x+helpform.size.width) (helpform.location.y)
	Macro_List_Form.size=dotNetObject "System.Drawing.Size" 320 650
	Macro_List_Form.FormBorderStyle = (dotnetclass "System.Windows.Forms.FormBorderStyle").FixedToolWindow
	Macro_List_Form.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 40 40 80
	Macro_List_Form.text="Macro Script List"
	Macro_List_Form.MaximizeBox = false;
	Macro_List_Form.MinimizeBox = false;
		
	Category_Label= dotNetObject "System.Windows.Forms.Button" 
	Category_Label.size=dotNetObject "System.Drawing.Size" 85 22
	Category_Label.Location=dotnetobject "System.Drawing.Point" 210 10
	Category_Label.Font=dotnetobject "System.Drawing.Font" "Arial" 8
	Category_Label.flatStyle=Category_Label.flatStyle.flat
	Category_Label.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	Category_Label.text="Category"
		
	Category_Label_Label= dotNetObject "System.Windows.Forms.Label" 
	Category_Label_Label.size=dotNetObject "System.Drawing.Size" 285 15
	Category_Label_Label.Location=dotnetobject "System.Drawing.Point" 10 40
	Category_Label_Label.Font=dotnetobject "System.Drawing.Font" "Arial" 8
	Category_Label_Label.flatStyle=Category_Label_Label.flatStyle.flat
	Category_Label_Label.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 40 40 80
	Category_Label_Label.text="Category : All Commands"
		
	Input_Text= dotNetObject "System.Windows.Forms.TextBox" 
	Input_Text.size=dotNetObject "System.Drawing.Size" 195 30
	Input_Text.Location=dotnetobject "System.Drawing.Point" 10 10
	Input_Text.BorderStyle= (dotnetclass "System.Windows.Forms.BorderStyle").None
	Input_Text.Font=dotnetobject "System.Drawing.Font" "Arial" 15
		
	Macro_Listbox= dotNetObject "System.Windows.Forms.Listbox" 
	Macro_Listbox.size=dotNetObject "System.Drawing.Size" 285 490
	Macro_Listbox.Location=dotnetobject "System.Drawing.Point" 10 60
	Macro_Listbox.BorderStyle= (dotnetclass "System.Windows.Forms.BorderStyle").None
	Macro_Listbox.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	Macro_Listbox.Forecolor=(DotNetClass  "System.Drawing.Color").FromArgb 255 255 255
	Macro_Listbox.Font=dotnetobject "System.Drawing.Font" "Arial" 9

	Make_Script = dotnetobject "System.Windows.Forms.button"
	Make_Script.text="Make Script"
	Make_Script.flatStyle=Make_Script.flatStyle.flat
	--Sample_Button1.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Make_Script.size=dotNetObject "System.Drawing.Size" 285 40
	Make_Script.Location=dotnetobject "System.Drawing.Point" 10 560
	Make_Script.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	Make_Script.Font=Original_Font_1
		
		
	c=getMacroScripts()
	macro_arr=#()

	qsort c arraysort

	for i in c do
	(
		append macro_arr i
	)

	for i in macro_arr do
	(
		Macro_Listbox.items.add i[2]
	)
	Find_Macro=macro_arr


	function find_string=
	(
		Category_Label_Label.text="Category : "+_Selected_Category
		item=_Selected_Category
		d=macro_arr
		Filter_Macro=#()
		if _Selected_Category=="All commands" then (Filter_Macro=d)
		else
		(
			for i=1 to d.count do
			(
				if (d[i][3]==item) do (append Filter_Macro d[i])
			)
		)
		q=Input_Text.text
		d=Filter_Macro
		Find_Macro=#()
		for i=1 to d.count do
		(
			ee=(Matchpattern d[i][2] pattern:(q+"*"))
			if (ee==true) do append Find_Macro (d[i])
		)
		Macro_Listbox.items.clear()
		for i in Find_Macro do
		(
			Macro_Listbox.items.add i[2]
		)
	)
	
	fn Category_Label_Event=
	(
		cc=#()
		for i in macro_arr do
		(
			append cc i[3]
		)
		cc= makeUniqueArray cc
		sort cc 
		
		Category_List_Form = dotNetObject "MaxCustomControls.MaxForm" pos:[0,0]	
		Category_List_Form.FormBorderStyle = (dotnetclass "System.Windows.Forms.FormBorderStyle").none
		Category_List_Form.StartPosition = Category_List_Form.StartPosition.Manual
		Category_List_Form.Location=dotnetobject "System.Drawing.Point" (Macro_List_Form.location.x+112) (Macro_List_Form.location.y+31)
		Category_List_Form.size=dotNetObject "System.Drawing.Size" 200 300
		Category_List_Form.text="Macro Script List"
		Category_List_Form.MaximizeBox = false;
		Category_List_Form.MinimizeBox = false;
		
		Category_Listbox= dotNetObject "System.Windows.Forms.Listbox" 
		Category_Listbox.size=dotNetObject "System.Drawing.Size" 180 270
		Category_Listbox.Location=dotnetobject "System.Drawing.Point" 10 10
		Category_Listbox.BorderStyle= (dotnetclass "System.Windows.Forms.BorderStyle").None
		Category_Listbox.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
		Category_Listbox.Forecolor=(DotNetClass  "System.Drawing.Color").FromArgb 255 255 255
		Category_Listbox.Font=dotnetobject "System.Drawing.Font" "Arial" 9
		
		Category_Listbox.items.add "All commands"
		for i in cc do
		(
			Category_Listbox.items.add i
		)
		
		Category_List_Form.controls.add Category_Listbox
		
		fn Category_Listbox_Event=
		(
			_Selected_Category=Category_Listbox.selectedItem
			find_string()
			Category_List_Form.close()
		)
		
		dotnet.AddEventHandler Category_Listbox "SelectedIndexChanged" Category_Listbox_Event
		
		Category_List_Form.showmodeless()
	)
	

	fn Make_Script_Event=
	(
		print ""
		macro_index="\""+(Find_Macro[(Macro_Listbox.selectedIndex+1)][3])+"\" \""+(Find_Macro[(Macro_Listbox.selectedIndex+1)][2])+"\""
		if (Macro_Listbox.SelectedItem==undefined) do (return false)
		
		folder_name=substring (Script_Box1.SelectedItem) 4 (Script_Box1.SelectedItem.count)
		
		--folder_name=substring (Script_Box1.SelectedItem) 4 (Script_Box1.SelectedItem.count)
		if not (doesFileExist ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name)) then
		(
			makedir ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name)
		)
		a=createfile ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name+"\\"+(Macro_Listbox.selectedItem+".ms"))
		close a
		a= openfile ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name+"\\"+(Macro_Listbox.selectedItem+".ms")) mode:"w"
		format "macros.run %" macro_index to:a
		close a
		Get_Scripts_List()
		Script_Box3.focus()
	)



	Macro_List_Form.controls.add Input_Text
	Macro_List_Form.controls.add Category_Label
	Macro_List_Form.controls.add Category_Label_Label
	Macro_List_Form.controls.add Macro_Listbox
	Macro_List_Form.controls.add Make_Script

	dotnet.AddEventHandler Input_Text "TextChanged" find_string
	dotnet.AddEventHandler Make_Script "Click" Make_Script_Event
 	dotnet.AddEventHandler Category_Label "Click" Category_Label_Event 

	)

	Default_Menu_Setting()
	Macro_List_Form.showmodeless()
)


	)	
	fn Add_Script_event=
	(
		if (Script_Box1.SelectedItem==undefined) do (return false)
		New_Script=getOpenFileName caption:"Open A Test File:" types:"Maxscript(*.ms,*.mse,*.mcr)|*.ms;*.mse;*.mcr"
		if (New_Script==undefined) do (return false)
		if (matchpattern New_Script pattern:"*.ms") or (matchpattern New_Script pattern:"*.mse") or (matchpattern New_Script pattern:"*.mcr") do
		(
			New_Script_Name=filenameFromPath New_Script
			folder_name=substring (Script_Box1.SelectedItem) 4 (Script_Box1.SelectedItem.count)
			if not (doesFileExist ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name)) then
			(
				makedir ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name)
			)
			a= copyfile New_Script ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name+"\\"+New_Script_Name)
			Get_Scripts_List()
			Script_Box3.focus()
		)
	)
	fn Edit_Script_event=
	(
		if (Script_Box1.SelectedItem==undefined) or (Script_Box3.SelectedItem==undefined) do (return false)
		folder_name=substring (Script_Box1.SelectedItem) 4 (Script_Box1.SelectedItem.count)
		edit ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name+"\\"+Script_Box3.SelectedItem)
	)
	fn Delete_Script=
	(
		if (Script_Box1.SelectedItem==undefined) or (Script_Box3.SelectedItem==undefined) do (return false)
		case (YN_Messagebox "Really Want Delete Script? It can not be repaired") of
		(
			#yes:
			(
				oldname=Script_Box3.SelectedItem
				if (matchpattern oldname pattern:"*.mse") or (matchpattern oldname pattern:"*.mcr") then 
				(
					oldname=substring oldname 1 (oldname.count-4)
				)
				if (matchpattern oldname pattern:"*.ms") or (matchpattern oldname pattern:"*.mcr") then 
				(
					oldname=substring oldname 1 (oldname.count-3)
				)
				for i=1 to Button_List.count do
				(
					b=Button_List[i]
					c=""
					d=""
					if (b[1]==" ") and (b[2]==" ") do 
					(
						b=substring b 4 (b.count)
						d="   "
					)
					if b[b.count]=="'" and b[b.count-2]=="'" and b[b.count-3]=="-" do 
					(
						c=substring b (b.count-4) b.count
						b=substring b 1 (b.count-5)
					)
					if b==oldname do 
					(
						deleteitem Button_List i
						Script_Box2.Items.Clear()
						exit
					)
				)
				folder_name=substring (Script_Box1.SelectedItem) 4 (Script_Box1.SelectedItem.count)
				deletefile ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name+"\\"+Script_Box3.SelectedItem)
				Get_Scripts_List()
				Script_Box3.focus()
				for i in Button_List do (Script_Box2.items.add i)
				Check_Buttons_List_Change=false
				Save_button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
				Button_Setting_Render()
				Get_Button_List()
			)
			default:
			(
			)
		)
	)
	fn Rename_Script_event=
	(		
		if (Script_Box1.SelectedItem==undefined) or (Script_Box3.SelectedItem==undefined) do (return false)
		oldname=Script_Box3.SelectedItem
		if (matchpattern oldname pattern:"*.mse") or (matchpattern oldname pattern:"*.mcr") then 
		(
			oldname=substring oldname 1 (oldname.count-4)
		)
		if (matchpattern oldname pattern:"*.ms") or (matchpattern oldname pattern:"*.mcr") then 
		(
			oldname=substring oldname 1 (oldname.count-3)
		)
		New_Name=(Dialog_modal ("Rename_Script : "+Script_Box3.SelectedItem) Script_Box3.SelectedItem)
		if (New_Name=="") or (New_Name==undefined) do (return false)
		
		if (matchpattern New_Name pattern:"*.ms") or (matchpattern New_Name pattern:"*.mse") or (matchpattern New_Name pattern:"*.mcr") then ()
		else (New_Name=New_Name+".ms")
		
		folder_name=substring (Script_Box1.SelectedItem) 4 (Script_Box1.SelectedItem.count)
		if (doesFileExist ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name+"\\"+New_Name)) do
		(
			messagebox "A file with the same name exists. Use a different name"
			return false
		)
		Renamefile ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name+"\\"+Script_Box3.SelectedItem) ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name+"\\"+New_Name)
		Get_Scripts_List()
		Script_Box3.focus()
		
		for i=1 to Button_List.count do
		(
			b=Button_List[i]
			c=""
			d=""
			if (b[1]==" ") and (b[2]==" ") do 
			(
				b=substring b 4 (b.count)
				d="   "
			)
			if b[b.count]=="'" and b[b.count-2]=="'" and b[b.count-3]=="-" do 
			(
				c=substring b (b.count-4) b.count
				b=substring b 1 (b.count-5)
			)
			if b==oldname do 
			(
				if (matchpattern New_Name pattern:"*.mse") or (matchpattern New_Name pattern:"*.mcr") then 
				(
					New_Name=substring New_Name 1 (New_Name.count-4)
				)
				if (matchpattern New_Name pattern:"*.ms") or (matchpattern New_Name pattern:"*.mcr") then 
				(
					New_Name=substring New_Name 1 (New_Name.count-3)
				)
				Button_List[i]=d+New_Name+c
				Script_Box2.Items.Clear()
				for i in Button_List do (Script_Box2.items.add i)
				exit
			)
		)
			Check_Buttons_List_Change=false
			Save_button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
			Button_Setting_Render()
			Get_Button_List()
		
		/*
		Check_Buttons_List_Change=false
		Save_button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 110 110 200
		
		Script_Box2
		/*
		if (Script_Box2.SelectedIndex==0) or (Script_Box2.SelectedItem==undefined) do (return false)
		num=(Script_Box2.SelectedIndex-1)
		imsi=Button_List[Script_Box2.SelectedIndex+1]
		Button_List[Script_Box2.SelectedIndex+1]=Button_List[Script_Box2.SelectedIndex]
		Button_List[Script_Box2.SelectedIndex]=imsi
		Script_Box2.Items.Clear()
		for i in Button_List do (Script_Box2.items.add i)
		Script_Box2.SetSelected num true
		Script_Box2.focus()*/
	
	)

	dotnet.AddEventHandler Script_Box1 "SelectedIndexChanged" Script_Box1_event
	dotnet.AddEventHandler Script_Box1_on_off "Click" on_off_event
	dotnet.AddEventHandler Script_Box2_Delete "Click" Delete_Button_event
	dotnet.AddEventHandler Script_Box2_up "Click" up_event
	dotnet.AddEventHandler Script_Box2_down "Click" down_button_event
	dotnet.AddEventHandler Script_Box2_Half "Click" Set_Half_event
	dotnet.AddEventHandler Script_Box2_Hotkey "Click" Set_HotKey_event
	dotnet.AddEventHandler Script_Box3_Button "Click" Make_Button_event
	dotnet.AddEventHandler Script_Box3_New "Click" New_Script_event
	dotnet.AddEventHandler Script_Box3_From_Macro "Click" Script_Box3_From_Macro_event
	dotnet.AddEventHandler Script_Box3_Add "Click" Add_Script_event
	dotnet.AddEventHandler Script_Box3_Edit "Click" Edit_Script_event
	dotnet.AddEventHandler Script_Box3_Delete "Click" Delete_Script
	dotnet.AddEventHandler Script_Box3_Rename "Click" Rename_Script_event
	dotnet.AddEventHandler Save_button "Click" Save_Button_event

)
----Scripts_Setting

function Utility_View=
(
	Utility_BTN.BackColor = (DotNetClass  "System.Drawing.Color").FromArgb 220 100 40
	Check_Scripts_Setting_Change=true
	Category_Setting()
	Button_List=#()
	Scripts_List=#()
	Position_y=10
	Position_1=188
	Position_2=188+201
	Position_3=188+201
	function Get_Category_List=
	(
		function get_Modify_List=
		(
			a=filein ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Utility_List.ms")
			return a
		)
		Current_Category_list=get_Modify_List()
		Category_List=Category_Setting()
		for i=1 to Category_List.count do
		(
			find=false
			for ii in Current_Category_list do
			(
			if Category_List[i]==ii then (Category_List[i]=("O) "+Category_List[i]); find=true; break)
			)
			if find==false do (Category_List[i]=("   "+Category_List[i]))
		)
		Before_Category=Category_List[1]
		qsort Category_List bsort
	)
	/*
	function Get_Button_List=
	(
		--Script_Box2.items.clear()
		function get_Modify_List=
		(
			__category=substring (Script_Box1.SelectedItem) 4 (Script_Box1.SelectedItem.count)
			if (doesFileExist ((getdir #UserScripts)+"\\P_Scripts\\"+__category+"\\Info\\Add_Button.ms")) then
			(
				a=filein ((getdir #UserScripts)+"\\P_Scripts\\"+__category+"\\Info\\Add_Button.ms")
				return a
			)
			else (return false)
		)
		Modify_List=get_Modify_List()
		if Modify_List==false do (Button_List=#(); return false)
		Button_List=#()
		for i in Modify_List do
		(
			if (i[2]!="") do
			(
				i[1]=(i[1]+" -'"+i[2]+"'")
			)
			if (i[3]!=0) do
			(
				i[1]=("   "+i[1])
			)
			append Button_List i[1]
		)
		for i in Button_List do (Script_Box2.items.add i)
	)
	*/
	function Get_Scripts_List=
	(
		Script_Box3.items.clear()
		_category=substring (Script_Box1.SelectedItem) 4 (Script_Box1.SelectedItem.count)
		Scripts_List=(getfiles ((getdir #UserScripts)+"\\P_Scripts\\"+_category+"\\Utility\\*"))
		for i=1 to Scripts_List.count do
		(
			Scripts_List[i]=filenameFromPath Scripts_List[i]
		)
		for i in Scripts_List do (Script_Box3.items.add i)
	)
	
	function Category_Setting_Render=
		(
			arr=#()
			for i in Category_List do
			(
				if i[1]=="O" then (append arr (substring i 4 (i.count)))
			)
			list__=openfile ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Utility_List.ms") mode:"w"
			
			format "( \n\treturn #(" to:list__
			for i in arr do
			(
				format "\"" to:list__
				format i to:list__
				format "\","to:list__
			)
			format "\"None\""to:list__
			format ")\n" to:list__
			format ")" to:list__
			
			close list__
		)----Part of Categor
	
	function Button_Setting_Render=
	(
				
		function Part_Of_Button=
		(
			Half_Check=0
			arr=#()
			
			for i in Button_List do
			(
				title__=""
				Hotkey=""
				across=0
				
				if i[1]==" " and i[2]==" " and i[3]==" " then
				(
					if Half_Check==0 then 
					(
						Half_Check=1
						across=1
						i=(substring i 4 i.count)
						
					)
					else if Half_Check==1 then
					(
						Half_Check=0
						across=2
						i=(substring i 4 i.count)
					)					
				)
				else 
				(
					if Half_Check==1 then
					(
						Half_Check=0
						across=3
					)
				) --check across
				
				if (findstring i " -'")!=undefined then
				(
					title__=substring i 1 (i.count-5)
					Hotkey=i[i.count-1]
				)
				else
				(
					title__=i
				) -- check hotkey
				append arr (#(title__,Hotkey,across))
			)
			
			_Category=(substring Before_Category 4 Before_Category.count)
			button_List_File=openfile ((getdir #UserScripts)+"\\P_Scripts\\"+_Category+"\\Info\\Add_Button.ms") mode:"w"
			
			format "(\n\tlocal NTL=#()\n\tfunction add_button title shortcut across:0=" to:button_List_File	
			format "\n(\n\t\tappend NTL #(title, shortcut, across)\n\t)\n\n" to:button_List_File	
			for i=1 to arr.count do
			(
				if (i==arr.count) and (arr[i][3]==1) do (arr[i][3]=0)
				format "\tadd_button \"%\" \"%\" across:%\n" arr[i][1] arr[i][2] arr[i][3] to:button_List_File
			)
			format "\n\treturn NTL\n)" to:button_List_File	
			close button_List_File
			
			
		)----Part of Buttons
		
		
		if (Before_Category[1]=="O") do (Part_Of_Button())
		Category_Setting_Render()
		
	)
		
		
		
	Script_Box1_title = dotnetobject "System.Windows.Forms.label"
	Script_Box1_title.text="Category"
	--Script_Box1_title.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box1_title.size=dotNetObject "System.Drawing.Size" 180 20
	Script_Box1_title.Location=dotnetobject "System.Drawing.Point" Position_1 (Position_y)
	helpForm.controls.add Script_Box1_title
	append Form_List Script_Box1_title
		
	Script_Box1_on_off = dotnetobject "System.Windows.Forms.button"
	Script_Box1_on_off.text="On/Off"
	Script_Box1_on_off.flatStyle=Script_Box1_on_off.flatStyle.Popup
	--Script_Box1_on_off.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box1_on_off.size=dotNetObject "System.Drawing.Size" 180 30
	Script_Box1_on_off.Location=dotnetobject "System.Drawing.Point" Position_1 (Position_y+315)
	Script_Box1_on_off.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box1_on_off
	append Form_List Script_Box1_on_off
		
	Script_Box1= dotNetObject "System.Windows.Forms.ListBox" pos:[0,0]
	Script_Box1.Location=dotnetobject "System.Drawing.Point" Position_1 (Position_y+20)
	Script_Box1.size=dotNetObject "System.Drawing.Size" 180 300
	Script_Box1.BackColor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	Script_Box1.BorderStyle= (dotnetclass "System.Windows.Forms.BorderStyle").Fixed3D
	--Script_Box1.Font=dotnetobject "System.Drawing.Font" "Calibri" 13
	Script_Box1.Forecolor=(DotNetClass  "System.Drawing.Color").FromArgb 255 255 255
	
	Script_Box1_Info = dotnetobject "System.Windows.Forms.label"
	Script_Box1_Info.text="You Can Use Up/Down Key"
	--Script_Box1_Info.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box1_Info.size=dotNetObject "System.Drawing.Size" 180 40
	Script_Box1_Info.Location=dotnetobject "System.Drawing.Point" Position_1 (Position_y+315+50)
	helpForm.controls.add Script_Box1_Info
	append Form_List Script_Box1_Info

	Get_Category_List()
	for i in Category_List do (Script_Box1.items.add (i))
	Script_Box1.SetSelected 0 true
		
	helpForm.controls.add Script_Box1
	append Form_List Script_Box1
		
	Script_Box3_title = dotnetobject "System.Windows.Forms.label"
	Script_Box3_title.text="Scripts List"
	Script_Box3_title.size=dotNetObject "System.Drawing.Size" 180 20
	--Script_Box3_title.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box3_title.Location=dotnetobject "System.Drawing.Point" Position_3 (Position_y)
	helpForm.controls.add Script_Box3_title
	append Form_List Script_Box3_title
		
	Script_Box3_New = dotnetobject "System.Windows.Forms.button"
	Script_Box3_New.text="New Script"
	Script_Box3_New.flatStyle=Script_Box3_New.flatStyle.Popup
	--Script_Box3_New.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box3_New.size=dotNetObject "System.Drawing.Size" 180 30
	Script_Box3_New.Location=dotnetobject "System.Drawing.Point" Position_3 (Position_y+315)
	Script_Box3_New.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box3_New
	append Form_List Script_Box3_New
		
	Script_Box3_Add = dotnetobject "System.Windows.Forms.button"
	Script_Box3_Add.text="Import"
	Script_Box3_Add.flatStyle=Script_Box3_Add.flatStyle.Popup
	--Script_Box3_Add.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box3_Add.size=dotNetObject "System.Drawing.Size" 90 30
	Script_Box3_Add.Location=dotnetobject "System.Drawing.Point" Position_3 (Position_y+315+30)
	Script_Box3_Add.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box3_Add
	append Form_List Script_Box3_Add
		
	Script_Box3_Edit = dotnetobject "System.Windows.Forms.button"
	Script_Box3_Edit.text="Edit"
	Script_Box3_Edit.flatStyle=Script_Box3_Edit.flatStyle.Popup
	--Script_Box3_Edit.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box3_Edit.size=dotNetObject "System.Drawing.Size" 90 30
	Script_Box3_Edit.Location=dotnetobject "System.Drawing.Point" (Position_3+90) (Position_y+315+30)
	Script_Box3_Edit.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box3_Edit
	append Form_List Script_Box3_Edit

	Script_Box3_Delete = dotnetobject "System.Windows.Forms.button"
	Script_Box3_Delete.text="Delete"
	Script_Box3_Delete.flatStyle=Script_Box3_Delete.flatStyle.Popup
	--Script_Box3_Delete.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box3_Delete.size=dotNetObject "System.Drawing.Size" 90 30
	Script_Box3_Delete.Location=dotnetobject "System.Drawing.Point" (Position_3+90) (Position_y+315+60)
	Script_Box3_Delete.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box3_Delete
	append Form_List Script_Box3_Delete
		
	Script_Box3_Rename = dotnetobject "System.Windows.Forms.button"
	Script_Box3_Rename.text="Rename"
	Script_Box3_Rename.flatStyle=Script_Box3_Rename.flatStyle.Popup
	--Script_Box3_Rename.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box3_Rename.size=dotNetObject "System.Drawing.Size" 90 30
	Script_Box3_Rename.Location=dotnetobject "System.Drawing.Point" (Position_3) (Position_y+315+60)
	Script_Box3_Rename.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box3_Rename
	append Form_List Script_Box3_Rename
		
	Script_Box3= dotNetObject "System.Windows.Forms.ListBox" pos:[0,0]
	Script_Box3.Location=dotnetobject "System.Drawing.Point" Position_3 (Position_y+20)
	Script_Box3.size=dotNetObject "System.Drawing.Size" 180 300
	Script_Box3.BackColor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	Script_Box3.BorderStyle= (dotnetclass "System.Windows.Forms.BorderStyle").Fixed3D
	--Script_Box3.Font=dotnetobject "System.Drawing.Font" "Calibri" 13
	Script_Box3.Forecolor=(DotNetClass  "System.Drawing.Color").FromArgb 255 255 255

	Get_Scripts_List()
		
	helpForm.controls.add Script_Box3
	append Form_List Script_Box3

	fn Script_Box1_event=
	(
		if (Check_Buttons_List_Change==true) then
		(
			case (YNC_Messagebox "The button has been modified.\nDo you want to save it?") of
			(
				#yes:
				(
					Button_Setting_Render()
					Get_Scripts_List()
					--Get_Button_List()
					Before_Category=Script_Box1.SelectedItem
					Current_Category_Index=Script_Box1.SelectedIndex
					Check_Buttons_List_Change=false
				)
				#no:
				(
					Check_Buttons_List_Change=false
					Get_Scripts_List()
					--Get_Button_List()
					Before_Category=Script_Box1.SelectedItem
					Current_Category_Index=Script_Box1.SelectedIndex
				)
				#cancel:
				(
					Check_Buttons_List_Change=""
					Script_Box1.SetSelected Current_Category_Index true
				)
			)
		)
		else if (Check_Buttons_List_Change=="") then (Check_Buttons_List_Change=true)
		else 
		(
			Get_Scripts_List()
			--Get_Button_List()
			Before_Category=Script_Box1.SelectedItem
			Current_Category_Index=Script_Box1.SelectedIndex
		)
	)
	fn on_off_event=
	(
		item=Script_Box1.SelectedItem
		if item==undefined do (return false)
		if (item[1]=="O") then 
		(
			item[1]=" "; item[2]=" "; item[3]=" ";  Category_List[Script_Box1.SelectedIndex+1]=Item; 
		)
		else 
		(
			item[1]="O"; item[2]=")"; item[3]=" "; Category_List[Script_Box1.SelectedIndex+1]=Item;
		)
		num=Script_Box1.SelectedIndex
		Script_Box1.Items.Clear()
		for i in Category_List do
		(
			Script_Box1.items.add (i)
		)
		Script_Box1.SetSelected num true
		Category_Setting_Render()	
		Script_Box1.focus()
	)
	fn New_Script_event=
	(
		if (Script_Box1.SelectedItem==undefined) do (return false)
		New_Name=(Dialog_modal ("New Script's Name") "")
		if (New_Name=="") do (return false)
		
		folder_name=substring (Script_Box1.SelectedItem) 4 (Script_Box1.SelectedItem.count)
		if not (doesFileExist ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name)) then
		(
			makedir ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name)
		)
		if not (doesFileExist ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name+"\\Utility")) then
		(
			makedir ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name+"\\Utility")
		)
		a=createfile ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name+"\\Utility\\"+New_Name+".ms")
		close a
		Get_Scripts_List()
	)
	fn Add_Script_event=
	(
		if (Script_Box1.SelectedItem==undefined) do (return false)
		New_Script=getOpenFileName caption:"Open A Test File:" types:"Maxscript(*.ms,*.mse,*.mcr)|*.ms;*.mse;*.mcr"
		if (New_Script==undefined) do (return false)
		
		New_Script_Name=filenameFromPath New_Script
		folder_name=substring (Script_Box1.SelectedItem) 4 (Script_Box1.SelectedItem.count)
		if not (doesFileExist ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name)) then
		(
			makedir ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name)
		)
		if not (doesFileExist ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name+"\\Utility")) then
		(
			makedir ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name+"\\Utility")
		)
		--a=createfile ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name+"\\Utility\\"+New_Script_Name+".msE")
		copyfile New_Script ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name+"\\Utility\\"+New_Script_Name)
		Script_Box3.focus()
	)
	fn Edit_Script_event=
	(
		if (Script_Box1.SelectedItem==undefined) or (Script_Box3.SelectedItem==undefined) do (return false)
		folder_name=substring (Script_Box1.SelectedItem) 4 (Script_Box1.SelectedItem.count)
		edit ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name+"\\Utility\\"+Script_Box3.SelectedItem)
	)
	fn Delete_Script=
	(
		if (Script_Box1.SelectedItem==undefined) or (Script_Box3.SelectedItem==undefined) do (return false)
		case (YNC_Messagebox "Really Want Delete Script? It can not be repaired") of
		(
			#yes:
			(
				folder_name=substring (Script_Box1.SelectedItem) 4 (Script_Box1.SelectedItem.count)
				deletefile ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name+"\\Utility\\"+Script_Box3.SelectedItem)
				Get_Scripts_List()
				Script_Box3.focus()
			)
			default:
			(
			)
		)
	)
	fn Rename_Script_event=
	(
		if (Script_Box1.SelectedItem==undefined) or (Script_Box3.SelectedItem==undefined) do (return false)
		New_Name=(Dialog_modal ("Rename_Script : "+Script_Box3.SelectedItem) "")
		if (New_Name=="") or (New_Name==undefined) do (return false)
		
		if (matchpattern New_Name pattern:"*.ms") or (matchpattern New_Name pattern:"*.mse") or (matchpattern New_Name pattern:"*.mcr") then ()
		else (New_Name=New_Name+".ms")
		
		folder_name=substring (Script_Box1.SelectedItem) 4 (Script_Box1.SelectedItem.count)
		Renamefile ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name+"\\Utility\\"+Script_Box3.SelectedItem) ((getdir #UserScripts)+"\\P_Scripts\\"+folder_name+"\\Utility\\"+New_Name)
		Get_Scripts_List()
		Script_Box3.focus()
	)

	dotnet.AddEventHandler Script_Box1 "SelectedIndexChanged" Script_Box1_event
	dotnet.AddEventHandler Script_Box1_on_off "Click" on_off_event
	dotnet.AddEventHandler Script_Box3_New "Click" New_Script_event
	dotnet.AddEventHandler Script_Box3_Add "Click" Add_Script_event
	dotnet.AddEventHandler Script_Box3_Edit "Click" Edit_Script_event
	dotnet.AddEventHandler Script_Box3_Delete "Click" Delete_Script
	dotnet.AddEventHandler Script_Box3_Rename "Click" Rename_Script_event

)

local Script_Text
function Modifiers_View=
(
	Modifiers_BTN.BackColor = (DotNetClass  "System.Drawing.Color").FromArgb 220 100 40
	Check_Scripts_Setting_Change=true
	Category_Setting()
	Button_List=#()
	Scripts_List=#()
	Position_y=10
	Position_1=188
	Position_3=188
	Position_2=188+201
	Position_4=188+201+201
	function Get_Category_List=
	(
	)
	
	function Get_Button_List=
	(
		Script_Box2.items.clear()
		function get_Modify_List=
		(
			a=filein ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Modifiers_List.ms")
			return a
		)
		
		Modify_List=get_Modify_List()
		if Modify_List==false do (Button_List=#(); return false)
		Button_List=#()
		for i in Modify_List do
		(
			if (i[2]!="") do
			(
				i[1]=(i[1]+" -'"+i[2]+"'")
			)
			append Button_List i[1]
		)
		for i in Button_List do (Script_Box2.items.add i)
	)
	
	function Get_Scripts_List=
	(
	ss = stringstream ""
	 showClass "*:mod*" to:ss
	 seek ss 0
	 modArr = #()
	 while not (eof ss) do (
		modNm = (readdelimitedstring ss " :")
		 openParenIndex = findString modNm "("
		if openParenIndex != undefined do modNm = substring modNm 1 (openParenIndex - 1)
		append modArr modNm
		skipToNextLine ss
	 )
		
	All_Modifiers_arr=modArr
	sort All_Modifiers_arr
	Script_Box3.items.clear()

		for i in All_Modifiers_arr do (Script_Box3.items.add i)
	)
	
	function Button_Setting_Render=
	(
		function Part_Of_Button=
		(
			Half_Check=0
			arr=#()
			
			for i in Button_List do
			(
				title__=""
				Hotkey=""
				
				if (findstring i " -'")!=undefined then
				(
					title__=substring i 1 (i.count-5)
					Hotkey=i[i.count-1]
				)
				else
				(
					title__=i
				) -- check hotkey
				append arr (#(title__,Hotkey))
			)
			
			button_List_File=openfile ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Modifiers_List.ms") mode:"w"
			
			format "(\n\tlocal NTL=#()\n\tfunction add_button title shortcut across:0=" to:button_List_File	
			format "\n(\n\t\tappend NTL #(title, shortcut, across)\n\t)\n\n" to:button_List_File	
			for i=1 to arr.count do
			(
				if (i==arr.count) and (arr[i][3]==1) do (arr[i][3]=0)
				format "\tadd_button \"%\" \"%\" across:%\n" arr[i][1] arr[i][2] arr[i][3] to:button_List_File
			)
			format "\n\treturn NTL\n)" to:button_List_File	
			close button_List_File
		)----Part of Buttons
		Part_Of_Button()
	)
		
	Script_Box2_title = dotnetobject "System.Windows.Forms.label"
	Script_Box2_title.text="Buttons List"
	Script_Box2_title.size=dotNetObject "System.Drawing.Size" 180 20
	--Script_Box2_title.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box2_title.Location=dotnetobject "System.Drawing.Point" Position_2 (Position_y)
	helpForm.controls.add Script_Box2_title
	append Form_List Script_Box2_title
		
	Script_Box2_Up = dotnetobject "System.Windows.Forms.button"
	Script_Box2_Up.text="Up"
	Script_Box2_Up.flatStyle=Script_Box2_Up.flatStyle.Popup
	--Script_Box2_Up.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box2_Up.size=dotNetObject "System.Drawing.Size" 90 30
	Script_Box2_Up.Location=dotnetobject "System.Drawing.Point" (Position_2) (Position_y+315+0)
	Script_Box2_Up.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box2_Up
	append Form_List Script_Box2_Up
		
	Script_Box2_Down = dotnetobject "System.Windows.Forms.button"
	Script_Box2_Down.text="Down"
	Script_Box2_Down.flatStyle=Script_Box2_Down.flatStyle.Popup
	--Script_Box2_Down.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box2_Down.size=dotNetObject "System.Drawing.Size" 90 30
	Script_Box2_Down.Location=dotnetobject "System.Drawing.Point" (Position_2+90) (Position_y+315+0)
	Script_Box2_Down.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box2_Down
	append Form_List Script_Box2_Down
		
	Script_Box2_HotKey = dotnetobject "System.Windows.Forms.button"
	Script_Box2_HotKey.text="Set HotKey"
	Script_Box2_HotKey.flatStyle=Script_Box2_HotKey.flatStyle.Popup
	--Script_Box2_HotKey.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box2_HotKey.size=dotNetObject "System.Drawing.Size" 180 30
	Script_Box2_HotKey.Location=dotnetobject "System.Drawing.Point" (Position_2) (Position_y+315+30)
	Script_Box2_HotKey.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box2_HotKey
	append Form_List Script_Box2_HotKey
		
	Script_Box2_Delete = dotnetobject "System.Windows.Forms.button"
	Script_Box2_Delete.text="Delete Button"
	Script_Box2_Delete.flatStyle=Script_Box2_Delete.flatStyle.Popup
	--Script_Box2_Title.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box2_Delete.size=dotNetObject "System.Drawing.Size" 180 30
	Script_Box2_Delete.Location=dotnetobject "System.Drawing.Point" (Position_2) (Position_y+315+60)
	Script_Box2_Delete.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box2_Delete
	append Form_List Script_Box2_Delete

	Script_Box2= dotNetObject "System.Windows.Forms.ListBox" pos:[0,0]
	Script_Box2.Location=dotnetobject "System.Drawing.Point" Position_2 (Position_y+20)
	Script_Box2.size=dotNetObject "System.Drawing.Size" 180 300
	Script_Box2.BackColor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	Script_Box2.BorderStyle= (dotnetclass "System.Windows.Forms.BorderStyle").Fixed3D
	--Script_Box2.Font=dotnetobject "System.Drawing.Font" "Calibri" 13
	Script_Box2.Forecolor=(DotNetClass  "System.Drawing.Color").FromArgb 255 255 255

	Save_button = dotnetobject "System.Windows.Forms.button"
	Save_button.text="Save"
	Save_button.flatStyle=Save_button.flatStyle.Popup
	--Save_button.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Save_button.size=dotNetObject "System.Drawing.Size" 180 30
	Save_button.Location=dotnetobject "System.Drawing.Point" Position_2 (Position_y+315+90)
	Save_button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Save_button
	append Form_List Save_button

	Get_Button_List()
		
	helpForm.controls.add Script_Box2
	append Form_List Script_Box2
		
		
	Script_Box3_title = dotnetobject "System.Windows.Forms.label"
	Script_Box3_title.text="Modifiers List"
	Script_Box3_title.size=dotNetObject "System.Drawing.Size" 180 20
	--Script_Box3_title.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box3_title.Location=dotnetobject "System.Drawing.Point" Position_3 (Position_y)
	helpForm.controls.add Script_Box3_title
	append Form_List Script_Box3_title
		
	Script_Box3_Button = dotnetobject "System.Windows.Forms.button"
	Script_Box3_Button.text="Make Button"
	Script_Box3_Button.flatStyle=Script_Box3_Button.flatStyle.Popup
	--Script_Box3_Button.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Box3_Button.size=dotNetObject "System.Drawing.Size" 180 30
	Script_Box3_Button.Location=dotnetobject "System.Drawing.Point" Position_3 (Position_y+315)
	Script_Box3_Button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Script_Box3_Button
	append Form_List Script_Box3_Button
		
	Script_Box3= dotNetObject "System.Windows.Forms.ListBox" pos:[0,0]
	Script_Box3.Location=dotnetobject "System.Drawing.Point" Position_3 (Position_y+20)
	Script_Box3.size=dotNetObject "System.Drawing.Size" 180 300
	Script_Box3.BackColor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	Script_Box3.BorderStyle= (dotnetclass "System.Windows.Forms.BorderStyle").Fixed3D
	--Script_Box3.Font=dotnetobject "System.Drawing.Font" "Calibri" 13
	Script_Box3.Forecolor=(DotNetClass  "System.Drawing.Color").FromArgb 255 255 255
	Get_Scripts_List()	
	helpForm.controls.add Script_Box3
	append Form_List Script_Box3
	
	
	Script_Text_title = dotnetobject "System.Windows.Forms.label"
	Script_Text_title.text="Script"
	Script_Text_title.size=dotNetObject "System.Drawing.Size" 180 20
	--Script_Box3_title.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Script_Text_title.Location=dotnetobject "System.Drawing.Point" Position_4 (Position_y)
	helpForm.controls.add Script_Text_title
	append Form_List Script_Text_title
	
	Save_Scripts_button = dotnetobject "System.Windows.Forms.button"
	Save_Scripts_button.text="Save Script"
	Save_Scripts_button.flatStyle=Save_button.flatStyle.Popup
	--Save_button.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Save_Scripts_button.size=dotNetObject "System.Drawing.Size" 180 30
	Save_Scripts_button.Location=dotnetobject "System.Drawing.Point" Position_4 (Position_y+315)
	Save_Scripts_button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Save_Scripts_button
	append Form_List Save_Scripts_button
	
	Show_Properties_button = dotnetobject "System.Windows.Forms.button"
	Show_Properties_button.text="Show Properties"
	Show_Properties_button.flatStyle=Save_button.flatStyle.Popup
	--Save_button.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Show_Properties_button.size=dotNetObject "System.Drawing.Size" 180 30
	Show_Properties_button.Location=dotnetobject "System.Drawing.Point" Position_4 (Position_y+315+30)
	Show_Properties_button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Show_Properties_button
	append Form_List Show_Properties_button
	
	Edit_Script_button = dotnetobject "System.Windows.Forms.button"
	Edit_Script_button.text="Edit"
	Edit_Script_button.flatStyle=Save_button.flatStyle.Popup
	--Save_button.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
	Edit_Script_button.size=dotNetObject "System.Drawing.Size" 180 30
	Edit_Script_button.Location=dotnetobject "System.Drawing.Point" Position_4 (Position_y+315+60)
	Edit_Script_button.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	helpForm.controls.add Edit_Script_button
	append Form_List Edit_Script_button
			
	Script_Text= dotNetObject "System.Windows.Forms.TextBox" pos:[0,0]
	Script_Text.Location=dotnetobject "System.Drawing.Point" Position_4 (Position_y+20)
	Script_Text.size=dotNetObject "System.Drawing.Size" 180 291
	Script_Text.BackColor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
	Script_Text.BorderStyle= (dotnetclass "System.Windows.Forms.BorderStyle").Fixed3D
	Script_Text.Multiline=true
	Script_Text.enabled=false
	--Script_Box3.Font=dotnetobject "System.Drawing.Font" "Calibri" 13
	Script_Text.Forecolor=(DotNetClass  "System.Drawing.Color").FromArgb 255 255 255
	helpForm.controls.add Script_Text
	append Form_List Script_Text

	fn Script_Box2_event=
	(
		if Script_Box2.SelectedItem==undefined do return false
		Script_Text.text=""
		Script_Text.enabled=true
		mod_name=Script_Box2.SelectedItem
		check_shortcut=findstring mod_name " -'"
		if check_shortcut!=undefined do (mod_name=substring mod_name 1 (check_shortcut-1))
		if (doesFileExist ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Modifiers_Command\\"+mod_name+".ms")) do
		(
			a=openfile ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Modifiers_Command\\"+mod_name+".ms")
			text__=""
			readline a
			readline a
			while not (eof a) do 
			(
				b=(readline a)
				text__=text__+b+"\r\n"
			)
			close a
			Script_Text.text=text__
		)
	)

	fn up_event=
	(
		Check_Buttons_List_Change=true
		if (Script_Box2.SelectedIndex==0) or (Script_Box2.SelectedItem==undefined) do (return false)
		num=(Script_Box2.SelectedIndex-1)
		imsi=Button_List[Script_Box2.SelectedIndex+1]
		Button_List[Script_Box2.SelectedIndex+1]=Button_List[Script_Box2.SelectedIndex]
		Button_List[Script_Box2.SelectedIndex]=imsi
		Script_Box2.Items.Clear()
		for i in Button_List do (Script_Box2.items.add i)
		Script_Box2.SetSelected num true
		Script_Box2.focus()
	)
	fn down_button_event=
	(
		Check_Buttons_List_Change=true
		if (Script_Box2.SelectedIndex+1==(Script_Box2.items.count)) or (Script_Box2.SelectedItem==undefined) do (return false)
		num=(Script_Box2.SelectedIndex+1)
		imsi=Button_List[Script_Box2.SelectedIndex+1]
		Button_List[Script_Box2.SelectedIndex+1]=Button_List[Script_Box2.SelectedIndex+2]
		Button_List[Script_Box2.SelectedIndex+2]=imsi
		Script_Box2.Items.Clear()
		for i in Button_List do (Script_Box2.items.add i)
		Script_Box2.SetSelected num true
		Script_Box2.focus()
	)
	fn Set_Half_event=
	(
		Check_Buttons_List_Change=true
		if (Script_Box2.SelectedItem==undefined) do (return false)
		if (matchpattern (Script_Box2.SelectedItem) pattern:"   *") do 
		(
			num=(Script_Box2.SelectedIndex)
			Button_List[Script_Box2.SelectedIndex+1]=substring (Button_List[Script_Box2.SelectedIndex+1]) 4 (Button_List[Script_Box2.SelectedIndex+1]).count
			Script_Box2.Items.Clear()
			for i in Button_List do (Script_Box2.items.add i)
			Script_Box2.SetSelected num true	
			Script_Box2.focus()
			return ture
		)
			num=(Script_Box2.SelectedIndex)
			Button_List[Script_Box2.SelectedIndex+1]="   "+(Button_List[Script_Box2.SelectedIndex+1])
			Script_Box2.Items.Clear()
			for i in Button_List do (Script_Box2.items.add i)
			Script_Box2.SetSelected num true	
			Script_Box2.focus()
	)
	fn Set_HotKey_event=
	(
		Check_Buttons_List_Change=true
		if (Script_Box2.SelectedItem==undefined) do (return false)
		New_Hotkey=toUpper (Dialog_modal "If You Want Delete Hotkey, Input 'None'" "")
		if (New_HotKey.count!=1) and (New_HotKey!="NONE") do (return false)
		New_HotKey="'"+New_HotKey+"'"
		num=(Script_Box2.SelectedIndex)
		if (matchpattern (Button_List[Script_Box2.SelectedIndex+1]) pattern:"*-'*'") do
		(
			Button_List[Script_Box2.SelectedIndex+1]=substring (Button_List[Script_Box2.SelectedIndex+1]) 1 (Button_List[Script_Box2.SelectedIndex+1].count-5)
		)
		if (New_HotKey!="'NONE'") do (Button_List[Script_Box2.SelectedIndex+1]=(Button_List[Script_Box2.SelectedIndex+1])+" -"+New_HotKey)
		Script_Box2.Items.Clear()
		for i in Button_List do (Script_Box2.items.add i)
		Script_Box2.SetSelected num true	
		Script_Box2.focus()
	)
	fn Delete_Button_event=
	(
		Check_Buttons_List_Change=true
		if (Script_Box2.SelectedItem==undefined) do (return false)
		num=Script_Box2.SelectedIndex
		deleteitem Button_List (Script_Box2.SelectedIndex+1)
		Script_Box2.Items.Clear()
		for i in Button_List do (Script_Box2.items.add i)
		if (Button_List.count==0) then 
		(
					
		)
		else if ((Button_List.count-1)<num) then
		(
			Script_Box2.SetSelected (num-1) true
		)
		else 
		(
			Script_Box2.SetSelected num true
		)
	)
	fn Save_Button_event=
	(
		Check_Buttons_List_Change=false
		Button_Setting_Render()
		Get_Button_List()
		Script_Text.enabled=false
		Script_Text.text=""
	)
	fn Make_Button_event=
	(
		Check_Buttons_List_Change=true
		if (Script_Box3.SelectedItem==undefined) do (return false)
		Current_Script=Script_Box3.SelectedItem
		append Button_List Current_Script
		Script_Box2.Items.Clear()
		for i in Button_List do (Script_Box2.items.add i)
		Script_Box3.focus()
	)
	fn Save_Scripts_Button_event=
	(
		if (Script_Box2.SelectedItem==undefined) do (return false)
		mod_name=Script_Box2.SelectedItem
		check_shortcut=findstring mod_name " -'"
		if check_shortcut!=undefined do (mod_name=substring mod_name 1 (check_shortcut-1))
		if (doesFileExist ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Modifiers_Command\\"+mod_name+".ms")) do
		(
			deletefile ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Modifiers_Command\\"+mod_name+".ms")
		)
		a=createfile ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Modifiers_Command\\"+mod_name+".ms")
		format "M = modpanel.getCurrentObject()\r\n" to:a
		format "--Do not change the text in line 1\r\n" to:a
		text_line=filterString Script_Text.text "\r\n"
		for i in text_line do
		(
			format "%\n" i to:a
		)
		close a
	)
	
	fn Show_Properties_Button_event=
	(
		if (Script_Box2.SelectedItem==undefined) do (return false)
		(
		  fn getMacroScripts =
		  (
			if (Script_Box2.SelectedItem==undefined) do (return false)
			mod_name=Script_Box2.SelectedItem
			check_shortcut=findstring mod_name " -'"
			if check_shortcut!=undefined do (mod_name=substring mod_name 1 (check_shortcut-1))
			mod_name=execute (""+mod_name+"()")
			t=""
			t=t as stringstream
			tt=#()
			showproperties mod_name to:t
			seek t 0
			while not (eof t) do 
				(
					b=(readline t)
					b=substring b 3 b.count
					--b=substring b 1 ((findstring b " : ")-1)
					cc=filterString b "("
					if cc.count!=1 do (ccc=filterstring cc[2] ")"; b=cc[1]+ccc[2])
					append tt b
				)
			return tt
		  )
		  
		  

		function Default_Menu_Setting=
		(

			
		Macro_List_Form = dotNetObject "MaxCustomControls.MaxForm" pos:[0,0]	
		Macro_List_Form.StartPosition = Macro_List_Form.StartPosition.Manual
		arr=windows.getWindowPos (windows.getMAXHWND ()) 
		Macro_List_Form.Location=dotnetobject "System.Drawing.Point" (helpform.location.x+helpform.size.width) (helpform.location.y)
		Macro_List_Form.size=dotNetObject "System.Drawing.Size" 270 410
		Macro_List_Form.FormBorderStyle = (dotnetclass "System.Windows.Forms.FormBorderStyle").FixedToolWindow
		Macro_List_Form.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 40 40 80
		Macro_List_Form.text="Macro Script List"
		Macro_List_Form.MaximizeBox = false;
		Macro_List_Form.MinimizeBox = false;
			
		Macro_Listbox= dotNetObject "System.Windows.Forms.Listbox" 
		Macro_Listbox.size=dotNetObject "System.Drawing.Size" 235 300
		Macro_Listbox.Location=dotnetobject "System.Drawing.Point" 10 10
		Macro_Listbox.BorderStyle= (dotnetclass "System.Windows.Forms.BorderStyle").None
		Macro_Listbox.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
		Macro_Listbox.Forecolor=(DotNetClass  "System.Drawing.Color").FromArgb 255 255 255
		Macro_Listbox.Font=dotnetobject "System.Drawing.Font" "Arial" 9

		Make_Script = dotnetobject "System.Windows.Forms.button"
		Make_Script.text="append text"
		Make_Script.flatStyle=Make_Script.flatStyle.flat
		--Sample_Button1.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
		Make_Script.size=dotNetObject "System.Drawing.Size" 235 40
		Make_Script.Location=dotnetobject "System.Drawing.Point" 10 320
		Make_Script.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
		Make_Script.Font=Original_Font_1
			
			
		c=getMacroScripts()
		for i in c do
		(
			Macro_Listbox.items.add i
		)
		

		fn Make_Script_Event=
		(
			if (Macro_Listbox.selecteditem==undefined) do (return false)
			__text__=Macro_Listbox.selecteditem
			__text__=replace __text__ ((findstring __text__ " :")) 2 "="
			Script_Text.text=Script_Text.text+"\r\nM"+__text__
		)


		Macro_List_Form.controls.add Macro_Listbox
		Macro_List_Form.controls.add Make_Script

		dotnet.AddEventHandler Make_Script "Click" Make_Script_Event

		)

		Default_Menu_Setting()
		Macro_List_Form.showmodeless()
		)


	)	
	
	fn Edit_Script_button_event=
	(
		if (Script_Box2.SelectedItem==undefined) do (return false)
		mod_name=Script_Box2.SelectedItem
		check_shortcut=findstring mod_name " -'"
		if check_shortcut!=undefined do (mod_name=substring mod_name 1 (check_shortcut-1))
		if (doesFileExist ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Modifiers_Command\\"+mod_name+".ms")) do
		(
			edit ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Modifiers_Command\\"+mod_name+".ms")
			return true
		)
		a=createfile ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Modifiers_Command\\"+mod_name+".ms")
		format "M = modpanel.getCurrentObject()\r\n" to:a
		format "--Do not change the text in line 1\r\n" to:a
		close a
		edit ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\_Modifiers_Command\\"+mod_name+".ms")
	)
	
	
	
	dotnet.AddEventHandler Script_Box2 "Click" Script_Box2_event
	dotnet.AddEventHandler Script_Box2_Delete "Click" Delete_Button_event
	dotnet.AddEventHandler Script_Box2_up "Click" up_event
	dotnet.AddEventHandler Script_Box2_down "Click" down_button_event
	dotnet.AddEventHandler Script_Box2_Hotkey "Click" Set_HotKey_event
	dotnet.AddEventHandler Save_button "Click" Save_Button_event
	dotnet.AddEventHandler Script_Box3_Button "Click" Make_Button_event
	dotnet.AddEventHandler Save_Scripts_button "Click" Save_Scripts_Button_event
	dotnet.AddEventHandler Show_Properties_button "Click" Show_Properties_Button_event
	dotnet.AddEventHandler Edit_Script_button "Click" Edit_Script_button_event

	
)


local Help_Box, language=false
function Help_View=
(

Help_BTN.BackColor = (DotNetClass  "System.Drawing.Color").FromArgb 220 100 40
	
Change_Language = dotnetobject "System.Windows.Forms.button"
Change_Language.text="Change Language"
Change_Language.flatStyle=Change_Language.flatStyle.Popup
--Script_Box3_Button.Font=dotnetobject "System.Drawing.Font" "Calibri" 15
Change_Language.size=dotNetObject "System.Drawing.Size" 90 40
Change_Language.Location=dotnetobject "System.Drawing.Point" 660 (Position_y+5)
Change_Language.Backcolor=(DotNetClass  "System.Drawing.Color").FromArgb 120 120 120
helpForm.controls.add Change_Language
append Form_List Change_Language
	
	
Help_Box= dotNetObject "System.Windows.Forms.RichTextBox" pos:[0,0]
Help_Box.Location=dotnetobject "System.Drawing.Point" 180 10
Help_Box.size=dotNetObject "System.Drawing.Size" 595 434
Help_Box.BackColor=(DotNetClass  "System.Drawing.Color").FromArgb 50 50 90
Help_Box.BorderStyle= (dotnetclass "System.Windows.Forms.BorderStyle").None
Help_Box.LoadFile ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\Help.rtf")
Help_Box.Readonly=true
helpForm.controls.add Help_Box
append Form_List Help_Box

fn Change_Language_event=
(
	if language==false then
	(
		Help_Box.LoadFile ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\Help(Korean).rtf")
		language=true
	)
	else
	(
		Help_Box.LoadFile ((getdir #UserScripts)+"\\P_Scripts\\___Management Scripts\\Help.rtf")
		language=false
	)
)

dotnet.AddEventHandler Change_Language "Click" Change_Language_event

)
local Save_View_count=0
local Menu_Category_Check, Button_Check, Script_Check, Utility_Category_Check, Utility_Check
local Design_Check, Modifiers_Check
function Save_View=
(
Save_View_count=0
Save_BTN.BackColor = (DotNetClass  "System.Drawing.Color").FromArgb 220 100 40
	function _addbutton _name mode=
	(
		if mode=="check" then
		(
			a= dotNetObject "System.Windows.Forms.CheckBox" pos:[0,0]
			a.checked=true
		)
		else
		(
			a= dotNetObject "System.Windows.Forms.Button" pos:[0,0]
		)
		a.Location=dotnetobject "System.Drawing.Point" 250 (20+(Save_View_count*40))
		a.size=dotNetObject "System.Drawing.Size" 200 20
		a.text=_name
		append Form_List a
		helpForm.controls.add a
		Save_View_count+=1
			return a
	)
Menu_Category_Check=_addbutton "Menu Category (Replace)" "check"
Button_Check=_addbutton "Menu Button (Replace)" "check"
Script_Check=_addbutton "Menu Scripts (Append)" "check"
Utility_Category_Check=_addbutton "Utility Category (Replace)" "check"
Utility_Check=_addbutton "Utility Scripts (Append)" "check"
Design_Check=_addbutton "Design (Replace)" "check"
Modifiers_Check=_addbutton "Modifiers (Replace)" "check"
Save_Button__=_addbutton "Save" 33
Save_Button__.size=dotNetObject "System.Drawing.Size" 150 40

function Save_Button__Event=
(
	
		messagebox "This feature currently does not work"
		return false
		o1=Menu_Category_Check.checked
		o2=Button_Check.checked
		o3=Script_Check.checked
		o4=Utility_Category_Check.checked
		o5=Utility_Check.checked
		o6=Design_Check.checked
		o7=Modifiers_Check.checked
		


		namesArray = for s in selection collect s.name
		FromFolder = (getdir #UserScripts)+"\\P_Scripts"
		ss=dotNetObject "System.Windows.Forms.SaveFileDialog"
		ss.ShowDialog()
		test_path=ss.Filename
		ar=filterString test_path "\\"
		ar2=filterString ar[ar.count] "."
		dd=""
		for i=1 to (ar.count-1) do
		(
			dd=dd+ar[i]+"\\"
		)
		test_path=dd+ar2[1]

		ToFolder= (getdir #UserScripts)+"\\Save_\\P_Scripts"

		if (o1==false) and (o2==false) and (o3==false) and (o4==false) and (o5==false) and (o6==false) and (o7==false) do (return false)
		makedir ToFolder
		makedir (ToFolder+"\\___Management Scripts")
		if o1==true do 
		(
			copyfile (FromFolder+"\\___Management Scripts\\_List.ms") (ToFolder+"\\___Management Scripts\\_List.ms") 
		)
		if o4==true do 
		(
			copyfile (FromFolder+"\\___Management Scripts\\_Utility_List.ms") (ToFolder+"\\___Management Scripts\\_Utility_List.ms") 
		)
		if o6==true do 
		(
			copyfile (FromFolder+"\\___Management Scripts\\_Color_Preset.ms") (ToFolder+"\\___Management Scripts\\_Color_Preset.ms") 
		)
		if o7==true do 
		(
			copyfile (FromFolder+"\\___Management Scripts\\_Modifiers_List.ms") (ToFolder+"\\___Management Scripts\\_Modifiers_List.ms") 
		)

		if o2 or o3 or o5 do
		(
				list=getDirectories (FromFolder+"\\*")
				deleteitem list (finditem list (FromFolder+"\\___Management Scripts\\"))
				list2=#()
				for i in list do
				(
					ar=filterString i "\\"
					append list2 ar[ar.count]
				)
			for i in list2 do
			(
				makedir (ToFolder+"\\"+i)	
				makedir (ToFolder+"\\"+i+"\\Info")
				makedir (ToFolder+"\\"+i+"\\Utility")	
			)

			if o2==true do
			(
				for i in list2 do
				(
					if (doesFileExist (FromFolder+"\\"+i+"\\info\\Add_Button.ms")) do
					(
						copyfile (FromFolder+"\\"+i+"\\info\\Add_Button.ms") (ToFolder+"\\"+i+"\\info\\Add_Button.ms") 
					)
				)
			)
			if o3==true do
			(
				for i in list2 do
				(
					list3= (getfiles (FromFolder+"\\"+i+"\\*.ms"))
					list4=#()
					for ii in list3 do
					(
						ar=filterString ii "\\"
						append list4 ar[ar.count]
					)
					
					for ii in list4 do
					(
						copyfile (FromFolder+"\\"+i+"\\"+ii) (ToFolder+"\\"+i+"\\"+ii) 
					)
				)
			)
			if o5==true do
			(
				for i in list2 do
				(
					if (doesFileExist (FromFolder+"\\"+i+"\\Utility")) do
					(
						list3= (getfiles (FromFolder+"\\"+i+"\\Utility\\*.ms"))
						list4=#()
						for ii in list3 do
						(
							ar=filterString ii "\\"
							append list4 ar[ar.count]
						)
						
						for ii in list4 do
						(
							copyfile (FromFolder+"\\"+i+"\\Utility\\"+ii) (ToFolder+"\\"+i+"\\Utility\\"+ii) 
						)		
					)
				)
			)

		)

        util = ("Compress-Archive") --the zipping-program
        zipFile = (test_path+".zip")
        sourceFile = ToFolder --a single file to zip   
        cmd = "" as stringStream --set up a zipping-command
        format "% % %" util sourceFile zipFile to:cmd --the commandstring
		cmd=cmd as string
		_delete= "; remove-item "+(getdir #UserScripts)+"\\Save_"+" -Recurse ;"
		shelllaunch "PowerShell" (cmd+_delete) --EXECUTE THE ZIPPING

)
	
dotnet.addeventhandler Save_Button__ "Click" Save_Button__Event
)






function Default_Menu_Setting=
(

helpForm = dotNetObject "MaxCustomControls.MaxForm" pos:[0,0]	
helpForm.StartPosition = helpForm.StartPosition.Manual
arr=windows.getWindowPos (windows.getMAXHWND ()) 
helpForm.Location=dotnetobject "System.Drawing.Point" ((arr.w/2)+arr.x-480) ((arr.h/2)+arr.y-245)
helpForm.size=dotNetObject "System.Drawing.Size" 800 491
print ((arr.h/2)+arr.y)
helpForm.FormBorderStyle = (dotnetclass "System.Windows.Forms.FormBorderStyle").FixedToolWindow
helpForm.text="P_Scripts_Settings"
helpForm.MaximizeBox = false;
helpForm.MinimizeBox = false;
	
--bmpRectangle = dotNetObject "System.Drawing.Rectangle" 0 0 320 320
	
Scripts_BTN=addbutton "Menu Setting" helpForm
Utility_BTN=addbutton "Utility Setting" helpForm
Modifiers_BTN=addbutton "Modifiers Setting" helpForm	
Design_BTN=addbutton "Design Setting" helpForm
Info_BTN=addbutton "Infomation" helpForm
Help_BTN=addbutton "Help" helpForm
Save_BTN=addbutton "Save Setting" helpForm
Folder_BTN=addbutton "Open Folder" helpForm
	
Close_BTN=addbutton "Close" helpForm
	
fn Scripts_BTN_Event=(if (delete_Before_Form()==true) do (Scripts_Setting_View()))
fn Utility_BTN_Event=(if (delete_Before_Form()==true) do (Utility_View()))
fn Modifiers_BTN_Event=(if (delete_Before_Form()==true) do (Modifiers_View()))
fn Design_BTN_Event=(if (delete_Before_Form()==true) do (Design_Setting_View()))
fn Info_BTN_Event=(if (delete_Before_Form()==true) do (Information_View()))
fn Folder_BTN_Event=(		shellLaunch "explorer.exe" ((getdir #UserScripts)+"\\P_Scripts"))
fn Help_BTN_Event=(if (delete_Before_Form()==true) do (Help_View()))
fn Save_BTN_Event=(if (delete_Before_Form()==true) do (Save_View()))
fn Close_BTN_Event= (helpForm.close())
fn changeBackcolor = 
(helpForm.BackColor=(DotNetClass  "System.Drawing.Color").FromArgb 0 20 50)
fn close_Event = 
(
	if (Check_Buttons_List_Change==true) do
	(
		case (YN_Messagebox "The button has been modified.\nDo you want to save it?") of
		(
			#yes:
			(
				Button_Setting_Render()
				return true
			)
			#no:
			(
				return true
			)
		)
	)
)
	
dotnet.AddEventHandler helpForm "BackColorChanged" changeBackcolor
dotnet.addEventHandler Info_BTN "Click" Info_BTN_Event
dotnet.addEventHandler Design_BTN "Click" Design_BTN_Event
dotnet.addEventHandler Scripts_BTN "Click" Scripts_BTN_Event
dotnet.addEventHandler Folder_BTN "Click" Folder_BTN_Event
dotnet.addEventHandler Utility_BTN "Click" Utility_BTN_Event
dotnet.addEventHandler Modifiers_BTN "Click" Modifiers_BTN_Event
dotnet.addEventHandler Help_BTN "Click" Help_BTN_Event
dotnet.addEventHandler Save_BTN "Click" Save_BTN_Event
dotnet.addEventHandler Close_BTN "Click" Close_BTN_Event
dotnet.AddEventHandler helpForm "Closing" close_Event
	
helpForm.BackColor = (DotNetClass  "System.Drawing.Color").FromArgb 0 20 50
	
)




Default_Menu_Setting()
Scripts_Setting_View()

helpForm.showmodeless()

current_Category= (Check_Current_Selected_Type())
for i=1 to Category_List.count do
(
	if ((substring Category_List[i] 4 (Category_List[i].count))==current_Category) do 
	(
		Script_Box1.SetSelected (i-1)	true
		Get_Scripts_List()
		Get_Button_List()
		Before_Category=Script_Box1.SelectedItem
		Current_Category_Index=Script_Box1.SelectedIndex
		exit
	)
)

)