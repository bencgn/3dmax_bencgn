/*

	CopyTo Installer
	MastaMan
*/

rollout rNotify "Installed Success!" 
(		
	dotNetControl edtStat "System.Windows.Forms.Textbox" width:350 height:460 align:#center 
			
	button btnCopy "Copy" align: #left width: 50 across: 3
	button btnScriptHelp "Help" width: 50 align: #right tooltip: "Help is not available for this script" offset: [-110, 0]	
	button btnOK "Ok" align: #right  width: 50
	
	global szScriptHelpFile = "https://3dground.github.io/CopyTo/help/index.html" 
	
	fn initTextBox textBox =
	(
		b = (colorMan.getColor #background) * 255
		t = (colorMan.getColor #text) * 255
		
		textBox.Font = dotNetObject "System.Drawing.Font" "MS Sans Serif" 8 ((dotNetClass "System.Drawing.FontStyle").Regular)
		textBox.BorderStyle = (dotNetClass "System.Windows.Forms.BorderStyle").FixedSingle
		textBox.BackColor = (dotNetClass "System.Drawing.Color").fromARGB (b[1] as integer) (b[2] as integer) (b[3] as integer)
		textBox.ForeColor = (dotNetClass "System.Drawing.Color").fromARGB (t[1] as integer) (t[2] as integer) (t[3] as integer)
		textBox.MultiLine = true
		textBox.WordWrap = true
		textBox.ScrollBars = (dotNetClass "System.Windows.Forms.ScrollBars").Vertical
		textBox.ReadOnly = true
	)	
	
	on btnScriptHelp pressed do
	(
		shellLaunch szScriptHelpFile ""
	)

	on btnOK pressed do try(DestroyDialog rNotify)catch()
	on btnCopy pressed do setClipBoardText edtStat.text	
		
	on rNotify open do
	(	
		initTextBox edtStat
		
		s = "\r\n\r\n___________________________________________________\r\n\r\n"
		n = "\r\n"
		
		m = n
		m += "CopyTo installed succes!" + n + n
		m += "Installer automatically created Quad Menu items!" + n
		m += "The installation is fully completed, and you may have to use a script." + n 
		m += "If for some reason does not appear Quad Menu items, try to run 3Ds Max by Administrator."
		m += s	
		m += "Info:" + n
		m += "\r\nFor more info please read help:" + n
		m += szScriptHelpFile + n + n
		m += "By donate the script, you will support the creator to continue the development and support this script itself."		
		m += s	
		m += "You have the right to use this shareware script, as well as to distribute it. You can enjoy all the features of this script is free." + n + n
		m += "Get more scripts on http://3dground.net"
		
		edtStat.text = m				
	)
		
)

fn installScript =
(	
	version = "3.0.0"
	
	script = (getDir #userMacros) + "\\copyTo.mcr"
	
	msZip.unloadPackage "CopyTo.mzp" "" ""
	
	if(doesFileExist script == false) do return false
	
	fileIn script
 		
	quadMenu = menuMan.getViewportRightClickMenu #nonePressed
	theMenu = quadMenu.getMenu 1

	fn findMenuItem theMenu menuName =
	(
		for i in 1 to theMenu.numItems() where (theMenu.getItem i).getTitle() == menuName do return i
		return 0
	)

	fn unregisterMenuItem theMenu menuName =
	(	
		try
		(
			for i in 1 to theMenu.numItems() do
			(
				if((theMenu.getItem i).getTitle() == menuName) do
				(
					theMenu.removeItemByPosition i 	

					if((theMenu.getItem (i - 1)).getIsSeparator()) do theMenu.removeItemByPosition (i - 1)
				)
			)
		)catch()
	)

	item = try(findMenuItem theMenu "&Clone")catch(8)

	unregisterMenuItem theMenu "CopyTo"
	unregisterMenuItem theMenu "PasteFrom"

	copyTo = menuMan.createActionItem "CopyTo" "[3DGROUND]"
	pasteFrom = menuMan.createActionItem "PasteFrom" "[3DGROUND]"

	theMenu.addItem (menuMan.createSeparatorItem()) (item += 1)
	theMenu.addItem copyTo (item += 1)
	theMenu.addItem pasteFrom (item += 1)
		
	menuMan.updateMenuBar()
		
	createDialog rNotify 350 500
)


installScript()