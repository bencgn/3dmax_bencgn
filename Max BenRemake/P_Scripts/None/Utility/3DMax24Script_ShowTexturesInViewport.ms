/*

Script Name:	ShowTexturesInViewport.ms
Compatible:	3dsMax 2012 and higher
Version:		v1.0
Release date:  January 29, 2019
Last update:	January 29, 2019
Code by:		Hernan Rodenstein
Website:		http://www.splinedynamics.com/free-3dsmax-scripts/

Description:
A simple checkbutton to show or hide the textures for all materials in scene at once.
Should handle almost any kind of material and render engine.

*/

macroScript SD_ShowTexturesInViewport
category:"Spline Dynamics - free scripts"
tooltip:"Show textures in viewport"
buttontext:"ShowTex"

(
	local state = false --this variable lives in the Macro and controls its checked state
	
	fn ShowTextures newState =
	(
		for matClass in material.classes do (
			for m in (getclassinstances matClass processChildren:true) do (
				if (refs.dependentNodes m).count>0 then (
					if classof m != Multimaterial then showTexturemap m newState
				)
			)
		)
	)
	
	on isChecked return state --check or uncheck the Macro button
 	on execute do --if the Macro button was pressed,
 	(
		state = not state --switch the checked state
		setWaitCursor() 
		ShowTextures state
		setArrowCursor() 
 	)
)