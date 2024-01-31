-- Random Extrude Script
-- Edit by Mustafa Mamdouh @MCUBE Studios 2015-05-02

-- Description
-- Random Extrude for Object Faces

-- Procedure
-- Convert object to edit poly
-- select all faces
-- Random Extrude (local) by given values

try(destroyDialog ExtrudeFaces)catch()
rollout ExtrudeFaces "Random Extrude" width:130 height:225

--User Interface

(
button button1 "Random Extrude" pos:[10,10] width:105 height:35
spinner minExtrude "Min " range:[0,10000,0] type:#worldunits  pos:[10,55] width:105
spinner maxExtrude "Max" range:[0,10000,3.937] type:#worldunits pos:[10,75] width:105
checkbox setid "Random Face ID?" checked:true pos:[15,100] 
Spinner ID "ID Count:" range:[1,100,100] type:#integer pos:[18,120] width:97
progressbar prog color:green pos:[13,145] width:102
Label Editor "Edit by Mustafa"
label credit1 "MCUBE Studios"
hyperLink creditLink "www.mcubestudios.com" color:[0,0,0] hoverColor:[255,255,255] visitedColor:[0,0,0] address:"http://www.mcubestudios.com" offset:[-5,0]
	
--Functions

	on button1 pressed do 
	undo on
	(
		(
		myMin = minExtrude.value
		myMax = maxExtrude.value
		convertTo $ PolyMeshObject
		facecount = $.faces.count
		for i = 1 to $.faces.count do
			(
			ranid = random 1 ID.value
			polyop.setFaceSelection $ #{i}
			if setid.checked == true 
			then (polyop.setFaceMatID $ i (ranid))
			$.ExtrudeFaces (random myMin myMax)	
			prog.value = 100.*i/facecount
			)
		)
	)
)	

CreateDialog ExtrudeFaces lockWidth:true lockHeight:true style:#(#style_toolwindow, #style_resizing, #style_sysmenu)