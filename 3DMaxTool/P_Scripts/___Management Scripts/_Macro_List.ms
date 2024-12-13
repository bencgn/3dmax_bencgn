
(

  fn getMacroScripts =
  (
  	/*
  	<DOC> Description here.
  	Arguments:
  		no arguments
  	Return:
  		<array>		Returns a big array of arrays with macro meta data
  	*/
  	
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
  
  
local Macro_List_Form, macro_List,Input_Text,macro_arr, Macro_Listbox, Find_Macro, Macro_Listbox




function Default_Menu_Setting=
(

Macro_List_Form = dotNetObject "MaxCustomControls.MaxForm" pos:[0,0]	
Macro_List_Form.StartPosition = Macro_List_Form.StartPosition.Manual
arr=windows.getWindowPos (windows.getMAXHWND ()) 
Macro_List_Form.Location=dotnetobject "System.Drawing.Point" (arr.x+400) 0
Macro_List_Form.size=dotNetObject "System.Drawing.Size" 320 650
Macro_List_Form.FormBorderStyle = (dotnetclass "System.Windows.Forms.FormBorderStyle").FixedToolWindow
Macro_List_Form.text="P_Scripts_Settings"
Macro_List_Form.MaximizeBox = false;
Macro_List_Form.MinimizeBox = false;
	
Input_Text= dotNetObject "System.Windows.Forms.TextBox" 
Input_Text.size=dotNetObject "System.Drawing.Size" 285 30
Input_Text.Location=dotnetobject "System.Drawing.Point" 10 10
Input_Text.BorderStyle= (dotnetclass "System.Windows.Forms.BorderStyle").None
Input_Text.Font=dotnetobject "System.Drawing.Font" "Arial" 15
	
Macro_Listbox= dotNetObject "System.Windows.Forms.Listbox" 
Macro_Listbox.size=dotNetObject "System.Drawing.Size" 285 520
Macro_Listbox.Location=dotnetobject "System.Drawing.Point" 10 40
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
	q=Input_Text.text
	d=macro_arr
	Find_Macro=#()
	if q=="" then 
	(
		Find_Macro=macro_arr
	)
	else
	(
	for i=1 to d.count do
		(
			ee=(Matchpattern d[i][2] pattern:(q+"*"))
			if (ee==true) do append Find_Macro (d[i])
		)
	)
	Macro_Listbox.items.clear()
	for i in Find_Macro do
	(
		Macro_Listbox.items.add i[2]
	)
)

fn Make_Script_Event=
(
	
	macro_index=(Find_Macro[(Macro_Listbox.selectedIndex+1)][1] as string)
	
	if (Macro_Listbox.SelectedItem==undefined) do (return false)
	
	New_Name="test"
	folder_name="None"
	
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
)



Macro_List_Form.controls.add Input_Text
Macro_List_Form.controls.add Macro_Listbox
Macro_List_Form.controls.add Make_Script

dotnet.AddEventHandler Input_Text "TextChanged" find_string
dotnet.AddEventHandler Make_Script "Click" Make_Script_Event

)

Default_Menu_Setting()
Macro_List_Form.showmodeless()
)

