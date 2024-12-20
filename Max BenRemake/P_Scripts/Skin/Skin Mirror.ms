
undo on
	(
	$.modifiers[#Skin].mirrorEnabled = on
	skinOps.mirrorPaste $.modifiers[#Skin]
	$.modifiers[#Skin].mirrorEnabled = off
	)