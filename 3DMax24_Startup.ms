
macroscript BENCGN_Need category:"BENCGN_Tool" tooltip:"BENCGN Need"
(
	fileIn "D:\\3dmax_bencgn\\3dmax_bencgn\\Final_BenHayDung.ms"
)
macroscript BENCGN_TestTool category:"BENCGN_Tool" tooltip:"BENCGN TestTool"
(
	fileIn "D:\\3dmax_bencgn\\3dmax_bencgn\\Test_tool.ms"
)
macroscript BENCGN_Update category:"BENCGN_Update" tooltip:"BENCGN Update"
(
	fileIn "D:\\3dmax_bencgn\\3dmax_bencgn\\Setup_Update.ms"
)

tmpMenu = menuMan.findMenu "BENCGN_Tool"
try (menuMan.unregisterMenu tmpMenu) catch()

mainMenuBar = menuMan.getMainMenuBar ()
subMenu = menuMan.createMenu "BENCGN_Tool"

subItem2 = menuMan.createActionItem "BENCGN_Need" "BENCGN_Tool"
subMenu.addItem subItem2 -1
subItem2 = menuMan.createActionItem "BENCGN_TestTool" "BENCGN_Tool"
subMenu.addItem subItem2 -1
subItem2 = menuMan.createActionItem "BENCGN_Update" "BENCGN_Update"
subMenu.addItem subItem2 -1
subMenuItem = menuMan.createSubMenuItem "" subMenu
subMenuIndex = mainMenuBar.numItems() + 1
mainMenuBar.addItem subMenuItem subMenuIndex
menuMan.updateMenuBar()