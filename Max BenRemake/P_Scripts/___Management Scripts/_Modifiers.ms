

(


fn getWindowClass =
	(
		local source  = "using System;
"
		source += "using System.Runtime.InteropServices;
"
		source += "public class Window
"
		source += "{
"
		source += "	[DllImport(\"user32.dll\")]
"
		source += "	public static extern IntPtr GetForegroundWindow();
"
		source += "}
"

		local csharpProvider = dotNetObject "Microsoft.CSharp.CSharpCodeProvider"
		local compilerParams = dotNetObject "System.CodeDom.Compiler.CompilerParameters"
		compilerParams.GenerateInMemory = true
		compilerParams.ReferencedAssemblies.Add "System.dll"
		local compilerResults = csharpProvider.CompileAssemblyFromSource compilerParams #(source)
		compilerResults.CompiledAssembly.CreateInstance "Window"
	)
if NOT isKindOf ::window dotNetObject do window = getWindowClass()


try destroyDialog ::focusTest catch()


--                                             --
------Section of  Variable------
(

Global Addbutton2, M_dialog, InputBox2,mForm, _btnname
local Start_Script , Help_Btn , util_Btn , Fix_Btn , Modifiers_Btn

Fix_mode=false
NBL=#()
folder=""	
vertical=0
setting_info=(fileIn ((getdir #userscripts)+"\\P_Scripts\\___Management Scripts\\_Setting_Info.ms"))
TheFont = setting_info[7]
TheBGColor=setting_info[1]
TheBGColor2=setting_info[2]
TheBGColor3=setting_info[3]
TheBorderColor=setting_info[4]
TheFontColor=setting_info[5]
TheDisfocusFontColor=setting_info[6]
btn_w=setting_info[9]
btn_h=setting_info[10]
btn_count=0
btn_list=#()

	
)
------Section of  Variable------
--                                             --







--                                             --
-------Section of  Event-------
function ClickEvent arg ee=
(
		d=dotNetClass "Control"
		if ee.button==d.MouseButtons.Left do (Start_Script (arg.text); return true)
		if ee.button==d.MouseButtons.right do 
		(
			fileIn ((getdir #userscripts)+"\\P_Scripts\\___Management Scripts\\Mini_Modifiers_Setting.ms")
			_btnname arg.text
			return false
		)
)

function keyevent=
( 
	input_value=InputBox2.text
	InputBox2.text=""
	Start_Script input_value
)

function keyDownevent ee=
(
	
key=ee.KeyCode
if (ee.Modifiers == key.Control) do 
	(
	if key == key.Z then (max undo)
	else if key == key.Y then (actionMan.executeAction 0 "40016")
	)
if key == ee.KeyCode.Enter or key == ee.KeyCode.Space or key == ee.KeyCode.Escape then 
	(
	)
)


-------Section of  Event-------
--                                             --







--                                             --
---Section of  Dialog Controll----
fn close_M_dialog=
(
	InputBox2=undefined
	mForm=undefined
	NBL=undefined
	if M_dialog!=undefined do M_dialog.close()
	M_dialog=undefined
	--Addbutton2=undefined
	--Gc ()
)

fn Start_Script Shortcut =
(
	local scriptname
	if Shortcut=="" do (return 0)
	if Shortcut.count<4 then
		(
			Shortcut=Shortcut[1]
		Shortcut=toUpper Shortcut
		for i in btn_list do
			(
			if i[1]==Shortcut do 
				(
				scriptname= (i[2].text)
				non_close=i[3]
				exit;
				)
			)
		)
		
	else
		(
		scriptname=Shortcut
		for i in btn_list do
			(
			if (i[2].text)==Shortcut do 
				(
				non_close=i[3]
				exit;
				)
			)
		)
	if scriptname==undefined or scriptname=="" do (close_M_dialog(); return false)
	if scriptname[scriptname.count]==")" do
	(scriptname=substring scriptname 1 (scriptname.count-4))
	scriptname= execute (scriptname)
	
	undo on 
		(
				max modify mode
				modify_index=modPanel.getModifierIndex
				if $selection.count !=0 do
				(
					modPanel.addModToSelection (scriptname())
					if (doesFileExist ((getdir #userscripts)+"\\P_Scripts\\___Management Scripts\\_Modifiers_Command\\"+(scriptname as string)+".ms"))
					do (fileIn ((getdir #userscripts)+"\\P_Scripts\\___Management Scripts\\_Modifiers_Command\\"+(scriptname as string)+".ms"))
				)
					close_M_dialog()
		)
)

function Addbutton2 title shortcut =
(
	bb=btn_w
	nn=0
	if btn_count>=10 do (btn_count=0; vertical+=1)
	Title__=title
	if Shortcut!="" do (Title__=Title+" ("+Shortcut+")")
	BTN = dotNetObject "System.windows.forms.button"
	BTN.text = Title__
	BTN.flatStyle=BTN.flatStyle.flat
	BTN.BackColor = TheBGColor
	BTN.flatappearance.bordercolor = TheBorderColor
	BTN.size = dotNetObject "System.Drawing.Size" (bb) btn_h
	BTN.location = dotNetObject "System.Drawing.Point" (nn+(vertical*btn_w)) ((btn_h*(btn_count)))
	BTN.font=TheFont
	btn_count+=1
	append btn_list #(shortcut,BTN)
	mForm.controls.add BTN
	dotnet.addEventHandler BTN "Mousedown" ClickEvent
	return true
)
---Section of  Dialog Controll----
--                                             --




--                                             --
-------Section of  Main -------
fn Create_M_dialog=
(	
mForm = dotNetObject "MaxCustomControls.MaxForm" pos:[0,0]	
function get_Btn_List= (fileIn ((getdir #userscripts)+"\\P_Scripts\\___Management Scripts\\_Modifiers_List.ms"))
new_Btn_List = get_Btn_List()
for i in new_Btn_List do
(
	addbutton2 i[1] i[2]
)

	
InputBox2=dotNetObject "System.windows.forms.TextBox"
InputBox2.location = dotNetObject "System.Drawing.Point" -20 -20
mForm.controls.add InputBox2

cursor2 = dotnetclass "System.Windows.Forms.Cursor"
p2 = cursor2.Position
mForm.StartPosition = mForm.StartPosition.Manual
mForm.Location=dotnetobject "System.Drawing.Point" (p2.x-(btn_w+(btn_w*(vertical-1)))) (p2.y-((btn_h*(10+1))/2)+15)
mForm.size=dotNetObject "System.Drawing.Size" ((btn_w+(btn_w*vertical))+16) (btn_h*(10+1)+2)
mForm.FormBorderStyle = (dotnetclass "System.Windows.Forms.FormBorderStyle").FixedToolWindow
mForm.text="Modifiers"
mForm.MaximizeBox = false;
mForm.MinimizeBox = false;
	
function LostfocusEvent2 =
(
	if mForm==undefined do return 0
	if (Fix_mode==false) and (mForm.handle!= (window.getForegroundWindow())) then
		(
			close_M_dialog()
		)
	for i in btn_list do
	(
		i[2].ForeColor=TheDisFocusFontColor
	)
)

function GotfocusEvent=
( 
	InputBox2.Focus()
)
	
function GotfocusEvent2=
( 
	for i in btn_list do
	(
		i[2].ForeColor=TheFontColor
	)
)
	
--mForm.AllowTransparency=true
dotnet.addEventHandler InputBox2 "KeyDown" keyDownevent
dotnet.addEventHandler InputBox2 "KeyUp" keyevent
dotnet.addEventHandler InputBox2 "LostFocus" LostfocusEvent2
dotnet.addEventHandler InputBox2 "GotFocus" GotfocusEvent2
dotnet.addEventHandler mForm "GotFocus" GotfocusEvent
	
mForm.show()
InputBox2.Focus()

	
return mForm
 --Other Setting
)
-------Section of  Main -------
--                                             --







--                                             --
-------Create M_dialog -------
(
	if M_dialog!=undefiend do (close_M_dialog())
	M_dialog=Create_M_dialog()
	
)
-------Create M_dialog -------
--                                             --



)