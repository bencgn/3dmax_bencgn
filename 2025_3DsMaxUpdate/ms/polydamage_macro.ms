macroscript PolyDamage
category:"PolyDesign3D"
toolTip:"PolyDamageV1"
(
	(
		scriptsDir = (GetDir #scripts) + @"\"
		polydamagescript = scriptsDir + "polydamage_nm.mse"
		
		if (doesFileExist polydamagescript) then
		(
			fileIn polydamagescript
		)else
		(
			messageBox ("Can't find the script file. \nPlease copy the polydamage_nm.mse from installer folder and paste it to: \n " + (GetDir #scripts) + " \nfolder.") title:"PolyDamage" beep:false
		)
	)
)