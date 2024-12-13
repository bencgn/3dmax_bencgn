macroScript P_MorpherHelper
	category:"P_Scripts"
	toolTip:"P_MorpherHelper"
(
fromfolder=getFilenamePath (getThisScriptFilename() )
fromfile=fromfolder+"P_MorpherHelper_v2.5.mse"
targetfolder=getdir #Userscripts
targetfile=targetfolder+"\\P_MorpherHelper_v2.5.mse"

if (doesFileExist targetfile)==false do 
(
copyfile fromfile targetfile
)

fileIn targetfile
)
Messagebox "Install Success!\r\nCategort:P_Scripts"

fromfolder=getFilenamePath (getThisScriptFilename() )
fromfile=fromfolder+"P_MorpherHelper_v2.5.mse"
targetfolder=getdir #Userscripts
targetfile=targetfolder+"\\P_MorpherHelper_v2.5.mse"

if (doesFileExist targetfile)==false do 
(
copyfile fromfile targetfile
)

fileIn targetfile