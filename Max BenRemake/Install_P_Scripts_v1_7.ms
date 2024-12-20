fn getDirs A NULL = 
	(
	for i in (getDirectories (A + "\\*")) do (
	append NULL i
	getDirs i NULL
	)
)

fn Install_full=
(
	Flist=#()
	target_folder=getdir #UserScripts
	fromfolder=getFilenamePath (getThisScriptFilename() )
	fromfolder=substring fromfolder 1 (fromfolder.count-1)
	getDirs fromfolder Flist
	
	SList=#()
	for i in Flist do
	(
		local arr
		arr=(getfiles (i+"*"))
		for ii in arr do
		(
			append SList ii
		)
	)
	
	Flist2=#()
	for i in Flist do
	(
		append Flist2 (substring i (fromfolder.count+1) (i.count))
	)-- \P_scripts\ ~~~

	Slist2=#()
	for i in Slist do
	(
		append Slist2 (substring i (fromfolder.count+1) (i.count))
	) 
	-- \P_scripts\ ~~~
		
	
	
	for i in Flist2 do
	(
		makedir (target_folder+i)
	)
		
	for i in Slist2 do
	(
		if (findstring i "_Setting_Info")!=undefined then
		( 
		)
		else if (findstring i "_Color_Preset")!=undefined then
		( 
		)
		else if (doesFileExist (target_folder+i))==true do
		(
			deletefile (target_folder+i)	
		)
		copyfile (fromfolder+i) (target_folder+i)	
	)
	s= (getThisScriptFilename())
	s=substring s (fromfolder.count+1) (s.count)
		
	if (doesFileExist (target_folder+s))==true do
	(
		deletefile (target_folder+s)	
	)
	copyfile (getThisScriptFilename()) (target_folder+s)
	
	
	fileIn ((getdir #UserScripts)+"\\P_Scripts\\P_Scripts.ms")
	messagebox "Install Succes\nRegister shortcut.\nCustomize User Interface - Keyboard\nCategory: P_Scripts\nRecommend \"C\" or Space bar"

)
fn Install_only=
(
	Flist=#()
	target_folder=getdir #UserScripts
	fromfolder=getFilenamePath (getThisScriptFilename() )
	fromfolder=substring fromfolder 1 (fromfolder.count-1)
	getDirs fromfolder Flist
	
	Flist2=#()
	for i in Flist do
	(
		append Flist2 (substring i (fromfolder.count+1) (i.count))
	)-- \P_scripts\ ~~~
	
	
	for i in Flist2 do
	(
		makedir (target_folder+i)
	)
		
	if (doesFileExist (target_folder+"\\P_Scripts\\P_Scripts.ms") == true) do
	(
		deletefile (target_folder+"\\P_Scripts\\P_Scripts.ms")
	)
	copyfile (fromfolder+"\\P_Scripts\\P_Scripts.ms") (target_folder+"\\P_Scripts\\P_Scripts.ms")
		
	
	if (doesFileExist (target_folder+"\\P_Scripts\\P_Scripts(FIX).ms") == true) do
	(
		deletefile (target_folder+"\\P_Scripts\\P_Scripts(FIX).ms")
	)
	copyfile (fromfolder+"\\P_Scripts\\P_Scripts(FIX).ms") (target_folder+"\\P_Scripts\\P_Scripts(FIX).ms")
		
	
	if (doesFileExist (target_folder+"\\P_Scripts\\___Management Scripts\\_Help.ms") == true) do
	(
		deletefile (target_folder+"\\P_Scripts\\___Management Scripts\\_Help.ms")
	)
	copyfile (fromfolder+"\\P_Scripts\\___Management Scripts\\_Help.ms") (target_folder+"\\P_Scripts\\___Management Scripts\\_Help.ms")
	
	
	if (doesFileExist (target_folder+"\\P_Scripts\\___Management Scripts\\Mini_Modifiers_Setting.ms") == true) do
	(
		deletefile (target_folder+"\\P_Scripts\\___Management Scripts\\Mini_Modifiers_Setting.ms")
	)
	copyfile (fromfolder+"\\P_Scripts\\___Management Scripts\\Mini_Modifiers_Setting.ms") (target_folder+"\\P_Scripts\\___Management Scripts\\Mini_Modifiers_Setting.ms")
	
	
	if (doesFileExist (target_folder+"\\P_Scripts\\___Management Scripts\\Mini_Button_Setting.ms") == true) do
	(
		deletefile (target_folder+"\\P_Scripts\\___Management Scripts\\Mini_Button_Setting.ms")
	)
	copyfile (fromfolder+"\\P_Scripts\\___Management Scripts\\Mini_Button_Setting.ms") (target_folder+"\\P_Scripts\\___Management Scripts\\Mini_Button_Setting.ms")
	
	
	if (doesFileExist (target_folder+"\\P_Scripts\\___Management Scripts\\_Utility.ms") == true) do
	(
		deletefile (target_folder+"\\P_Scripts\\___Management Scripts\\_Utility.ms")
	)
	copyfile (fromfolder+"\\P_Scripts\\___Management Scripts\\_Utility.ms") (target_folder+"\\P_Scripts\\___Management Scripts\\_Utility.ms")
	
	
	if (doesFileExist (target_folder+"\\P_Scripts\\___Management Scripts\\Information.rtf") == true) do
	(
		deletefile (target_folder+"\\P_Scripts\\___Management Scripts\\Information.rtf")
	)
	copyfile (fromfolder+"\\P_Scripts\\___Management Scripts\\Information.rtf") (target_folder+"\\P_Scripts\\___Management Scripts\\Information.rtf")
	
	
	if (doesFileExist (target_folder+"\\P_Scripts\\___Management Scripts\\help.rtf") == true) do
	(
		deletefile (target_folder+"\\P_Scripts\\___Management Scripts\\help.rtf")
	)
	copyfile (fromfolder+"\\P_Scripts\\___Management Scripts\\help.rtf") (target_folder+"\\P_Scripts\\___Management Scripts\\help.rtf")
	
	
	if (doesFileExist (target_folder+"\\P_Scripts\\___Management Scripts\\version.a") == true) do
	(
		deletefile (target_folder+"\\P_Scripts\\___Management Scripts\\version.a")
	)
	copyfile (fromfolder+"\\P_Scripts\\___Management Scripts\\version.a") (target_folder+"\\P_Scripts\\___Management Scripts\\version.a")
	
	
	fileIn ((getdir #UserScripts)+"\\P_Scripts\\P_Scripts.ms")
	messagebox "Install Succes\nRegister shortcut.\nCustomize User Interface - Keyboard\nCategory: P_Scripts\nRecommend \"C\" or Space bar"


)

(
btn_h=320
btn_w=340
target_folder=(getdir #UserScripts)
from_folder=getFilenamePath (getThisScriptFilename())
from_folder=substring from_folder 1 (from_folder.count-1)
	
hForm = dotNetObject "MaxCustomControls.MaxForm" pos:[0,0]	
cursor = dotnetclass "System.Windows.Forms.Cursor"
p = cursor.Position
hform.StartPosition = hform.StartPosition.Manual
hForm.Location=dotnetobject "System.Drawing.Point" (p.x-(btn_w/2)) (p.y-20)
hForm.size=dotNetObject "System.Drawing.Size" (btn_w+17) btn_h
--hForm.FormBorderStyle = (dotnetclass "System.Windows.Forms.FormBorderStyle").none
hForm.text="BenCGN Remake"
hForm.MaximizeBox = false;
hForm.MinimizeBox = false;
	
imageClass = dotNetclass "System.Drawing.image"
Image1 = imageClass.fromfile (from_folder+"\\Installer.png")
Image_Btn = dotNetObject "System.windows.forms.button"
Image_Btn.flatStyle=Image_Btn.flatStyle.flat
Image_Btn.BackColor = TheBGColor3
Image_Btn.backgroundimage=Image1
Image_Btn.size = dotNetObject "System.Drawing.Size" (btn_w) (120+45)
Image_Btn.location = dotNetObject "System.Drawing.Point" 0 0
Image_Btn.font=dotnetobject "System.Drawing.Font" "" 9
hForm.controls.add Image_Btn
	
Script_Box1_Info = dotnetobject "System.Windows.Forms.label"
Script_Box1_Info.text="P_Scripts is not installed on this computer\nPress 'Install With All SubScripts'"
Script_Box1_Info.size=dotNetObject "System.Drawing.Size" (btn_w) 30
Script_Box1_Info.Location=dotnetobject "System.Drawing.Point" 5 (128+50)
hForm.controls.add Script_Box1_Info
	
Fix_Btn = dotNetObject "System.windows.forms.button"
Fix_Btn.text = "Install With All SubScripts"
Fix_Btn.flatStyle=Fix_Btn.flatStyle.flat
Fix_Btn.BackColor = TheBGColor3
Fix_Btn.flatappearance.bordercolor = TheBorderColor
Fix_Btn.size = dotNetObject "System.Drawing.Size" (btn_w/2) 70
Fix_Btn.location = dotNetObject "System.Drawing.Point" 0 (160+50)
Fix_Btn.font=dotnetobject "System.Drawing.Font" "" 9
hForm.controls.add Fix_Btn
	
Fix_Btn2 = dotNetObject "System.windows.forms.button"
Fix_Btn2.text = "Update "
Fix_Btn2.flatStyle=Fix_Btn2.flatStyle.flat
Fix_Btn2.BackColor = TheBGColor3
Fix_Btn2.flatappearance.bordercolor = TheBorderColor
Fix_Btn2.size = dotNetObject "System.Drawing.Size" (btn_w/2) 70
Fix_Btn2.location = dotNetObject "System.Drawing.Point" (btn_w/2)  (160+50)
Fix_Btn2.font=dotnetobject "System.Drawing.Font" "" 9
Fix_Btn2.enabled=false
hForm.controls.add Fix_Btn2
	
	
hForm.showmodeless()



originalPscripts=doesFileExist (target_folder+"\\P_Scripts\\P_Scripts.ms")
if originalPscripts==true do 
(
	Script_Box1_Info.text="The Previous version of P_Scripts is installed\nWhat would you like to do?"
	Fix_Btn.text = "Install All \n[Existing]"
	Fix_Btn2.enabled=true
	if (doesFileExist (target_folder+"\\P_Scripts\\___Management Scripts\\version.a")) do
	(
		a=openfile (target_folder+"\\P_Scripts\\___Management Scripts\\version.a") mode:"r"
		a_ver=(readline a) as float
		close a
		
		b=openfile (from_folder+"\\P_Scripts\\___Management Scripts\\version.a") mode:"r"
		b_ver=(readline b) as float
		close b
		
		if (a_ver>=b_ver) do 
		(
			Script_Box1_Info.text="What would you like to do?"
			Fix_Btn2.enabled=false
		)
	)
)

function close_=
(
	Image1.Dispose();
)

function Install_1=
(
	Install_full()
	hForm.close()
)

function Install_2=
(
	install_Only()
	hForm.close()
)

dotNet.addEventHandler hForm "Closing" close_
dotNet.addEventHandler Fix_Btn "Click" Install_1
dotNet.addEventHandler Fix_Btn2 "Click" Install_2

)