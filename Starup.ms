
macroscript Unity3D category:"BENCGN_Tool" tooltip:"Unity3DTools"
(
	fileIn "//proj-server/project_rt/Technical/3dsmaxscript/NAMIr_Unity3DToolsEx.mse"	
)



tmpMenu = menuMan.findMenu "BENCGN_Tool"
try (menuMan.unregisterMenu tmpMenu) catch()

mainMenuBar = menuMan.getMainMenuBar ()
subMenu = menuMan.createMenu "BENCGN_Tool"

subItem2 = menuMan.createActionItem "Unity3D" "BENCGN_Tool"
subMenu.addItem subItem2 -1


subMenuItem = menuMan.createSubMenuItem "" subMenu
subMenuIndex = mainMenuBar.numItems() + 1
mainMenuBar.addItem subMenuItem subMenuIndex
menuMan.updateMenuBar()


