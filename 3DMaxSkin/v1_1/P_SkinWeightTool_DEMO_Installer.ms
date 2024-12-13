macroScript P_SkinWeightTool
	category:"P_Scripts"
	toolTip:"P_SkinWeightTool"
(
fromfolder=getFilenamePath (getThisScriptFilename() )
fromfile=fromfolder+"P_SkinWeightTool_DEMO_v1_1.mse"
targetfolder=getdir #Userscripts
targetfile=targetfolder+"\\P_SkinWeightTool_DEMO_v1_1.mse"

	
if (doesFileExist targetfile)==false do 
(
copyfile fromfile targetfile
)

fileIn targetfile
)

Messagebox "Install Success!\r\nCategort:P_Scripts"

fromfolder=getFilenamePath (getThisScriptFilename() )
fromfile=fromfolder+"P_SkinWeightTool_DEMO_v1_1.mse"
targetfolder=getdir #Userscripts
targetfile=targetfolder+"\\P_SkinWeightTool_DEMO_v1_1.mse"

if (doesFileExist targetfile)==true do 
(
deleteFile targetfile
)
copyfile fromfile targetfile

fileIn targetfile