

rollout UVEditor "Unwrap UVW Modifier"
(
	button openUVBtn "Open UV Editor"
	
	on openUVBtn pressed do
	(
		modPanel.setCurrentObject $	
		modPanel.addModToSelection (Unwrap_UVW ()) ui:on
		modifierPanel.setCurrentModifier (modPanel.getCurrentObject()) (Unwrap_UVW ())
		UVW = modPanel.getCurrentObject().modifiers[modPanel.getCurrentObject().modifiers.count]
		UVW.setMapChannel 2
		UVW.Edit()
	)
)

createDialog UVEditor
