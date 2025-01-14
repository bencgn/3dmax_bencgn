

rollout MutfakScript "Mutfak Script" width:265 height:504


(




	button 'btn1' "Düz Kapak Yap" pos:[24,120] width:92 height:26 align:#left




	button 'btn2' "Dolap Yap" pos:[24,40] width:92 height:26 align:#left




	button 'btn5' "Kulp Yap" pos:[33,290] width:92 height:26 align:#left




	pickbutton 'btn4' "Kulp Seç" pos:[136,240] width:92 height:26 align:#left




	button 'btn9' "Yerlestir" pos:[32,240] width:92 height:26 align:#left




	edittext 'edt1' "Derinlik/cm" pos:[128,42] width:104 height:20 align:#left




	edittext 'edt2' "Kalinlik/cm" pos:[127,122] width:104 height:20 align:#left




	button 'btn6' "Camli Kapak Yap" pos:[24,151] width:92 height:26 align:#left




	button 'btn7' "Tezgah Yap" pos:[84,445] width:92 height:26 align:#left




	GroupBox 'grp1' "Kapaklar" pos:[8,96] width:250 height:96 align:#left




	GroupBox 'grp2' "Dolaplar" pos:[8,16] width:248 height:64 align:#left




	GroupBox 'grp3' "Kulplar" pos:[8,208] width:248 height:213 align:#left




	dropdownList 'ddl2' "" pos:[137,292] width:95 height:21 items:#("Kulp1", "Kulp2", "Kulp3") align:#left


	dropdownList 'ddl3' "Kulp Boyu / cm" pos:[138,322] width:92 height:40 items:#("12", "16", "19", "22") selection:4 align:#left


	dropDownList 'ddl4' "Yerlesim Yönü" pos:[137,370] width:90 height:40 items:#("Dikey","Yatay") align:#left

	
		
		
	Global Objesayisi = 0
Global sayim=0
global isim=#()
	global isim2=#()
	global kulpadi
	global kulpadi2
		global derinlik
	global kalinlik
		global camisim
		global tezgahisim
		global kulpuzunluk
		
		
		
		
		
		

	on btn1 pressed do -- Kapak Yapma

		(


	kalinlik=edt2.text as integer


	obj = selection[1]



	actionMan.executeAction 1 "40213"  -- Edit: Clone

	maxOps.cloneNodes $ cloneType:#copy newNodes:&nnl


	select nnl

	move $ [0,105.832,0]



	for i in selection do -- Seçili Objelere Modifier Atama


		(

			harita = Shell() 



			harita2 = Edit_poly()


			objesayisi=objesayisi+1


			obj=selection[objesayisi]


	addmodifier selection[objesayisi] (copy harita)	

			obj.modifiers[#Shell].innerAmount = 0


	obj.modifiers[#Shell].outerAmount = kalinlik



			addmodifier selection[objesayisi] (copy harita2)	

		)



		sayim=selection.count


		for j = 1 to sayim do  --Diziye Obje isimlerini atama



					(


						isim[j]=selection[j]


					)



					for j = 1 to sayim do --Objelere Deisiklikleri Uygulama


					(


						select isim[j]


						scale $ [0.99,1,0.99]
						
						max modify mode

							subobjectLevel = 2


					$.modifiers[#Edit_Poly].SetSelection #Edge #{} 


	$.modifiers[#Edit_Poly].Select #Edge #{1, 2, 3, 4, 5, 6, 7, 8} 


	$.modifiers[#Edit_Poly].SetOperation #ChamferEdge


	$.modifiers[#Edit_Poly].chamferEdgeAmount = 0.15

	$.modifiers[#Edit_Poly].edgeChamferSegments = 3


	$.modifiers[#Edit_Poly].edgeChamferSmoothType = 0


	


	


	$.modifiers[#Edit_Poly].edgeChamferSmoothThreshold = 50


	


	


	$.modifiers[#Edit_Poly].Commit ()


	


	


						


	


	


		$.modifiers[#Edit_Poly].SetSelection #Edge #{}


	


	


	


	


	


	$.modifiers[#Edit_Poly].Select #Edge #{12, 14, 18, 31..32, 39..40}


	


	


	$.modifiers[#Edit_Poly].Select #Edge #{9, 15, 19, 33..34, 41..42}


	


	


	$.modifiers[#Edit_Poly].Select #Edge #{11, 13, 17, 29..30, 37..38}


	


	


	$.modifiers[#Edit_Poly].Select #Edge #{10, 16, 20, 35..36, 43..44}


	


	


		


	


	


	$.modifiers[#Edit_Poly].SetOperation #ChamferEdge


	


	


	$.modifiers[#Edit_Poly].chamferEdgeAmount = 0.15


	


	


	$.modifiers[#Edit_Poly].edgeChamferSegments = 3


	


	


	$.modifiers[#Edit_Poly].edgeChamferSmoothType = 0


	


	


	$.modifiers[#Edit_Poly].edgeChamferSmoothThreshold = 52


	


	


	$.modifiers[#Edit_Poly].Commit ()


	


	


		


	


	


	subobjectLevel = 4


	


	


	


	


	


	$.modifiers[#Edit_Poly].Select #Face #{1,2,3,4,5,6}


	


	


	$.modifiers[#Edit_Poly].SetOperation #SetSmooth


	


	


	$.modifiers[#Edit_Poly].smoothingGroupsToSet = 0


	


	


	$.modifiers[#Edit_Poly].smoothingGroupsToClear = -1


	


	


	subobjectLevel = 0


	


	


					)


	


	


					select nnl


	


	


					objesayisi=0


	


	


					sayim=0


	


	


					


	


	


					


	


	


		)


	on btn2 pressed do -- Dolap Yapma

		(


	


	


	


	


	


	obj = selection[1]


	


	


	derinlik=edt1.text as integer


	


	


	


	


	


	actionMan.executeAction 1 "40213"  -- Edit: Clone


	


	


	maxOps.cloneNodes $ cloneType:#copy newNodes:&nnl


	


	


	select nnl


	


	


	move $ [0,105.832,0]


	


	


	


	


	


		sayim=selection.count


	


	


		


	


	


		for j = 1 to sayim do  --Diziye Obje isimlerini atama


	


	


					(


	


	


						isim[j]=selection[j]


	


	


					)


	


	


					


	


	


					for s = 1 to sayim do --Objelere Deisiklikleri Uygulama


	


	


					(


	


	


						


	


	


						select isim[s]


	


	


						


	


	


							modPanel.addModToSelection (Shell ()) ui:on


	


	


	$.modifiers[#Shell].outerAmount = 0


	


	


	$.modifiers[#Shell].innerAmount = derinlik


	


	


	modPanel.addModToSelection (Edit_Poly ()) ui:on


	


	


	subobjectLevel = 4


	


	


	$.modifiers[#Edit_Poly].SetSelection #Face #{}


	


	


	$.modifiers[#Edit_Poly].Select #Face #{1}


	


	


	$.modifiers[#Edit_Poly].SetOperation #Inset


	


	


	$.modifiers[#Edit_Poly].insetAmount = 2


	


	


	$.modifiers[#Edit_Poly].Commit ()


	


	


	$.modifiers[#Edit_Poly].SetOperation #ExtrudeFace


	


	


	$.modifiers[#Edit_Poly].extrudeFaceHeight = -derinlik+2


	


	


	$.modifiers[#Edit_Poly].Commit ()


	


	


		subobjectLevel = 0


	


	


					)


	


	


					select nnl


	


	


		)


	on btn5 pressed do --Kulp Yapma

		(


		


	


		actionMan.executeAction 1 "40213"  -- Edit: Clone


	


	


		maxOps.cloneNodes $ cloneType:#copy newNodes:&nnl


	


	


		select nnl


	


	


		move $ [0,102.6,0]


	


	


		if ddl3.selection==1 then kulpuzunluk=12


		if ddl3.selection==2 then kulpuzunluk=16


		if ddl3.selection==3 then kulpuzunluk=19


		if ddl3.selection==4 then kulpuzunluk=22


	


			sayim=selection.count


	


			


		max create mode


	Rectangle length:1.2 width:kulpuzunluk cornerRadius:0 pos:[0,0,0] isSelected:on


	kulpadi=selection[1]


		modPanel.addModToSelection (Shell ()) ui:on


	


		$.modifiers[#Shell].innerAmount = 0


	


		$.modifiers[#Shell].outerAmount = 1


	


		modPanel.addModToSelection (Edit_Poly ()) ui:on


			


	if ddl2.selection==1 then


	(


	


	subobjectLevel = 2


	


	


	$.modifiers[#Edit_Poly].SetSelection #Edge #{}


	


	


	$.modifiers[#Edit_Poly].Select #Edge #{1, 3, 6..7}


	


	


	$.modifiers[#Edit_Poly].SetOperation #ConnectEdges


	


	


	$.modifiers[#Edit_Poly].connectEdgeSegments = 2


	


	


	$.modifiers[#Edit_Poly].connectEdgePinch = 60


	


	


	$.modifiers[#Edit_Poly].Commit ()


	


	


	$.modifiers[#Edit_Poly].SetOperation #ChamferEdge


	


	


	$.modifiers[#Edit_Poly].chamferEdgeAmount = 0.7


	


	


	$.modifiers[#Edit_Poly].Commit ()


	


	


	subobjectLevel = 4


	


	


	$.modifiers[#Edit_Poly].SetSelection #Face #{}


	


	


	$.modifiers[#Edit_Poly].Select #Face #{17}


	


	


	$.modifiers[#Edit_Poly].Select #Face #{18}


	


	


	$.modifiers[#Edit_Poly].SetOperation #ExtrudeFace


	


	


	$.modifiers[#Edit_Poly].extrudeFaceHeight = 1.5


	


	


	$.modifiers[#Edit_Poly].Commit ()


	


	


	subobjectLevel = 2


	


	$.modifiers[#Edit_Poly].SetSelection #Edge #{}


	$.modifiers[#Edit_Poly].Select #Edge #{1,2,3,4}


	$.modifiers[#Edit_Poly].Select #Edge #{13,14,15,16}


	$.modifiers[#Edit_Poly].Select #Edge #{29,30,31,32}


	$.modifiers[#Edit_Poly].SetOperation #ChamferEdge


	$.modifiers[#Edit_Poly].chamferEdgeAmount = 0.12


	$.modifiers[#Edit_Poly].edgeChamferSegments = 3


	$.modifiers[#Edit_Poly].Commit ()


	subobjectLevel = 0


	if ddl4.selection==1 then
	(
	rotate $ (angleaxis 90 [0,0,1])
	rotate $ (angleaxis 90 [1,0,0])
	)
	if ddl4.selection==2 then
	(
	--rotate $ (angleaxis 45 [0,0,1])
	rotate $ (angleaxis 90 [1,0,0])
	)


	)


	if ddl2.selection==2 then


	(


	subobjectLevel = 2


	$.modifiers[#Edit_Poly].SetSelection #Edge #{}


	$.modifiers[#Edit_Poly].Select #Edge #{1, 3, 6..7}


	$.modifiers[#Edit_Poly].SetOperation #ConnectEdges


	$.modifiers[#Edit_Poly].connectEdgeSegments = 11


	$.modifiers[#Edit_Poly].Commit ()


	subobjectLevel = 0


	modPanel.addModToSelection (Bend ()) ui:on


	$.modifiers[#Bend].BendAxis = 0


	$.modifiers[#Bend].BendAngle = 50


	modPanel.addModToSelection (Edit_Poly ()) ui:on


	subobjectLevel = 4


	$.modifiers[#Edit_Poly].SetSelection #Face #{}


	$.modifiers[#Edit_Poly].Select #Face #{25}


	$.modifiers[#Edit_Poly].Select #Face #{19}


	$.modifiers[#Edit_Poly].SetOperation #ExtrudeFace


	$.modifiers[#Edit_Poly].extrudeFaceHeight = 1.5


	$.modifiers[#Edit_Poly].Commit ()


	$.modifiers[#Edit_Poly].ButtonOp #MakePlanarInZ


	subobjectLevel = 2


	$.modifiers[#Edit_Poly].SetSelection #Edge #{}


	$.modifiers[#Edit_Poly].SetSelection #Edge #{}


	$.modifiers[#Edit_Poly].Select #Edge #{13}


	$.modifiers[#Edit_Poly].SetSelection #Edge #{}


	$.modifiers[#Edit_Poly].Select #Edge #{1, 13..23}


	$.modifiers[#Edit_Poly].Select #Edge #{3, 24..34}


	$.modifiers[#Edit_Poly].Select #Edge #{4}


	$.modifiers[#Edit_Poly].Select #Edge #{2}


	$.modifiers[#Edit_Poly].SetOperation #ChamferEdge


	$.modifiers[#Edit_Poly].chamferEdgeAmount = 0.1


	$.modifiers[#Edit_Poly].edgeChamferSegments = 3


	$.modifiers[#Edit_Poly].Commit ()


	subobjectLevel = 0


	if ddl4.selection==1 then
	(
	rotate $ (angleaxis 90 [0,0,1])
	rotate $ (angleaxis 90 [1,0,0])
	)
	if ddl4.selection==2 then
	(
	--rotate $ (angleaxis 45 [0,0,1])
	rotate $ (angleaxis 90 [1,0,0])
	)


	


	)


	if ddl2.selection==3 then


	(


	subobjectLevel = 2


	$.modifiers[#Edit_Poly].SetSelection #Edge #{}


	$.modifiers[#Edit_Poly].Select #Edge #{1, 3, 6..7}


	$.modifiers[#Edit_Poly].SetOperation #ConnectEdges


	$.modifiers[#Edit_Poly].connectEdgeSegments = 14


	$.modifiers[#Edit_Poly].Commit ()


	subobjectLevel = 4


	actionMan.executeAction 0 "369"


	$.modifiers[#Edit_Poly].SetSelection #Face #{}


	$.modifiers[#Edit_Poly].Select #Face #{6}


	subobjectLevel = 0


	modPanel.setCurrentObject $.modifiers[#Edit_Poly]


	deleteModifier $ 1


	modPanel.addModToSelection (Edit_Poly ()) ui:on


	subobjectLevel = 4


	$.modifiers[#Edit_Poly].SetSelection #Face #{}


	$.modifiers[#Edit_Poly].Select #Face #{1..6}


	$.modifiers[#Edit_Poly].SetOperation #Inset


	$.modifiers[#Edit_Poly].insetType = 1


	$.modifiers[#Edit_Poly].insetAmount = 0.02


	$.modifiers[#Edit_Poly].Commit ()


	subobjectLevel = 2


	$.modifiers[#Edit_Poly].SetSelection #Edge #{}


	$.modifiers[#Edit_Poly].Select #Edge #{1, 3, 6..7, 17, 19, 26, 28, 33, 35, 49, 51}


	$.modifiers[#Edit_Poly].SetOperation #ConnectEdges


	$.modifiers[#Edit_Poly].connectEdgeSegments = 5


	$.modifiers[#Edit_Poly].Commit ()


	$.modifiers[#Edit_Poly].SetOperation #Transform


	$.modifiers[#Edit_Poly].MoveSelection  [0,0,1.27453]


	$.modifiers[#Edit_Poly].Commit ()


	$.modifiers[#Edit_Poly].SetSelection #Edge #{}


	$.modifiers[#Edit_Poly].Select #Edge #{1, 7, 17, 28, 35, 49, 70, 75, 90, 95, 105, 120}


	$.modifiers[#Edit_Poly].Select #Edge #{3, 6, 19, 26, 33, 51, 65, 80, 85, 100, 110, 115}


	$.modifiers[#Edit_Poly].SetOperation #ConnectEdges


	$.modifiers[#Edit_Poly].connectEdgeSegments = 1


	$.modifiers[#Edit_Poly].Commit ()


	$.modifiers[#Edit_Poly].SetOperation #Transform


	$.modifiers[#Edit_Poly].MoveSelection  [0,0,-0.637992] 


	$.modifiers[#Edit_Poly].Commit ()


	


	$.modifiers[#Edit_Poly].SetSelection #Edge #{}


	$.modifiers[#Edit_Poly].Select #Edge #{206}


	$.modifiers[#Edit_Poly].Select #Edge #{206..207, 209, 212, 214..215, 217, 220..221, 224, 226..227}


	$.modifiers[#Edit_Poly].Select #Edge #{124}


	$.modifiers[#Edit_Poly].Select #Edge #{124, 126, 131, 139, 144, 146, 151, 159, 161, 169, 174, 176}


	$.modifiers[#Edit_Poly].Select #Edge #{121}


	$.modifiers[#Edit_Poly].Select #Edge #{121, 129, 134, 136, 141, 149, 154, 156, 164, 166, 171, 179}


	$.modifiers[#Edit_Poly].Select #Edge #{205}


	$.modifiers[#Edit_Poly].Select #Edge #{205, 208, 210..211, 213, 216, 218..219, 222..223, 225, 228}


	$.modifiers[#Edit_Poly].SetOperation #ChamferEdge


	$.modifiers[#Edit_Poly].chamferEdgeAmount = 0.05


	$.modifiers[#Edit_Poly].edgeChamferSegments = 3


	$.modifiers[#Edit_Poly].Commit ()


	subobjectLevel = 0

if ddl4.selection==1 then
	(
	rotate $ (angleaxis 90 [0,0,1])
	rotate $ (angleaxis 90 [1,0,0])
	)
	if ddl4.selection==2 then
	(
	--rotate $ (angleaxis 45 [0,0,1])
	rotate $ (angleaxis 90 [1,0,0])
	)

	)


	


	select nnl


			for j = 1 to sayim do  --Diziye Obje isimlerini atama


	


	


						(


	


	


							isim[j]=selection[j]


	


	


						)


	


	


						


	select kulpadi


	


						for j = 1 to sayim do  --Diziye Obje isimlerini atama


	


	


								(


	


									actionMan.executeAction 1 "40213"  -- Edit: Clone


	


	


									maxOps.cloneNodes $ cloneType:#copy newNodes:&nll


	


	


									select nll


	


	


									setCoordCenter #Selection


	


	


									CenterPivot $


	


	


									isim2[j]=selection[1]


	


								)


	


				for s = 1 to sayim do --Objelere Deisiklikleri Uygulama


	


	


						(


							isim2[s].pos=isim[s].pos


	


							)


	


							objesayisi=0


							sayim=0	


							select nnl


							delete $

select kulpadi
	delete $


	


		)


	on btn4 picked obj do --Obje Secimi

		(


	


	


		--select obj


	


	


		if obj.parent==undefined then kulpadi=obj else kulpadi=obj.parent


	


	


		


	


	


	btn4.caption=kulpadi.name


	


	


		)


	on btn9 pressed do -- Seçili Objeyi Yerlestirme

		(


	


	


		actionMan.executeAction 1 "40213"  -- Edit: Clone


	


	


				maxOps.cloneNodes $ cloneType:#copy newNodes:&nnl


	


	


				select nnl


	


	


				move $ [0,104,0]


	


	


					sayim=selection.count


					


	


					for j = 1 to sayim do  --Diziye Obje isimlerini atama


	


	


								(


	


	


									isim[j]=selection[j]


	


	


								)


	


								


								select kulpadi


	


	


					for j = 1 to sayim do  --Diziye Obje isimlerini atama


	


	


								(


	


									actionMan.executeAction 1 "40213"  -- Edit: Clone


	


	


									maxOps.cloneNodes $ cloneType:#copy newNodes:&nll


	


	


									select nll


	


	


									setCoordCenter #Selection


	


	


									CenterPivot $


	


	


									isim2[j]=selection[1]


	


								)


	


				for s = 1 to sayim do --Objelere Deisiklikleri Uygulama


	


	


						(


							isim2[s].pos=isim[s].pos


	


							)


	


							objesayisi=0


							sayim=0	


							select nnl


							delete $


	


	


		)


	on btn6 pressed do --Camli Kapak Yapma

		(


	


	


		kalinlik=edt2.text as integer


	


	


		obj = selection[1]


	


	


		


	


	


		


	


	


		actionMan.executeAction 1 "40213"  -- Edit: Clone


	


	


		maxOps.cloneNodes $ cloneType:#copy newNodes:&nnl


	


	


		select nnl


	


	


		move $ [0,105.832,0]


	


	


		


	


	


		


	


	


		


	


	


		for i in selection do -- Seçili Objelere Modifier Atama


	


	


			(


	


	


				harita = Shell() 


	


	


				harita2 = Edit_poly()


	


	


				objesayisi=objesayisi+1


	


	


				obj=selection[objesayisi]


	


	


		


	


	


		addmodifier selection[objesayisi] (copy harita)	


	


	


				obj.modifiers[#Shell].innerAmount = 0


	


	


		obj.modifiers[#Shell].outerAmount = kalinlik - 0.5


	


	


		


	


	


				


	


	


				


	


	


			


	


	


				


	


	


			)


	


	


			


	


	


			sayim=selection.count


	


	


			


	


	


			for j = 1 to sayim do  --Diziye Obje isimlerini atama


	


	


						(


	


	


							isim[j]=selection[j]


	


	


						)


	


	


						


	


	


						for j = 1 to sayim do --Objelere Deisiklikleri Uygulama


	


	


						(


	


	


							


	


	


							select isim[j]


	


	


							scale $ [0.99,1,0.99]


	


	


		


	


	


							


	


	


	camisim=$.name


	


	


	modPanel.addModToSelection (Edit_Poly ()) ui:on


	


	


	subobjectLevel = 4


	


	


	$.modifiers[#Edit_Poly].SetSelection #Face #{}


	


	


	$.modifiers[#Edit_Poly].Select #Face #{1}


	


	


	$.modifiers[#Edit_Poly].Select #Face #{2}


	


	


	$.modifiers[#Edit_Poly].SetOperation #Inset


	


	


	$.modifiers[#Edit_Poly].insetAmount = 5


	


	


	$.modifiers[#Edit_Poly].CommitAndRepeat ()


	


	


	$.modifiers[#Edit_Poly].insetAmount = 5


	


	


	$.modifiers[#Edit_Poly].Commit ()


	


	


	$.modifiers[#Edit_Poly].SetSelection #Face #{}


	


	


	$.modifiers[#Edit_Poly].Select #Face #{9}


	


	


	$.modifiers[#Edit_Poly].SetSelection #Face #{}


	


	


	$.modifiers[#Edit_Poly].Select #Face #{1}


	


	


	$.modifiers[#Edit_Poly].Select #Face #{2}


	


	


	$.modifiers[#Edit_Poly].ButtonOp #BridgePolygon


	


	


	$.modifiers[#Edit_Poly].SetSelection #Face #{}


	


	


	$.modifiers[#Edit_Poly].Select #Face #{5,6,7,8}


	


	


	$.modifiers[#Edit_Poly].SetOperation #ExtrudeFace


	


	


	$.modifiers[#Edit_Poly].extrudeFaceHeight = 0.5


	


	


	$.modifiers[#Edit_Poly].Commit ()


	


	


	$.modifiers[#Edit_Poly].SetSelection #Face #{}


	


	


	subobjectLevel = 2


	


	


	$.modifiers[#Edit_Poly].SetSelection #Edge #{}


	


	


	$.modifiers[#Edit_Poly].Select #Edge #{14}


	


	


	$.modifiers[#Edit_Poly].Select #Edge #{13..16}


	


	


	$.modifiers[#Edit_Poly].CreateShape "Camim" 


	


	


	


	


	


	$.modifiers[#Edit_Poly].SetSelection #Edge #{}


	


	


	


	


	


	$.modifiers[#Edit_Poly].Select #Edge #{49..52}


	


	


	$.modifiers[#Edit_Poly].Select #Edge #{5..8}


	


	


	$.modifiers[#Edit_Poly].Select #Edge #{53..56}


	


	


	$.modifiers[#Edit_Poly].Select #Edge #{13..16}


	


	


	$.modifiers[#Edit_Poly].Select #Edge #{29..32}


	


	


	$.modifiers[#Edit_Poly].Select #Edge #{37..40}


	


	


	$.modifiers[#Edit_Poly].SetOperation #ChamferEdge


	


	


	$.modifiers[#Edit_Poly].chamferEdgeAmount = 0.2


	


	


	$.modifiers[#Edit_Poly].edgeChamferSegments = 3


	


	


	$.modifiers[#Edit_Poly].Commit ()


	


	


	$.modifiers[#Edit_Poly].SetSelection #Edge #{}


	


	


	$.modifiers[#Edit_Poly].Select #Edge #{12, 20, 28, 36, 44, 48, 60, 63, 66, 72, 76, 80, 84, 87, 115..116, 127..128, 135..136, 143..144, 151..152, 157..158}


	


	


	$.modifiers[#Edit_Poly].Select #Edge #{11, 19, 25, 35, 41, 47, 59, 64..65, 71, 75, 77, 83, 88, 113..114, 125..126, 133..134, 137..138, 149..150, 159..160}


	


	


	$.modifiers[#Edit_Poly].Select #Edge #{10, 18, 26, 34, 42, 46, 58, 61, 68, 70, 74, 78, 82, 85, 119..120, 123..124, 131..132, 139..140, 147..148, 153..154}


	


	


	$.modifiers[#Edit_Poly].Select #Edge #{9, 17, 27, 33, 43, 45, 57, 62, 67, 69, 73, 79, 81, 86, 117..118, 121..122, 129..130, 141..142, 145..146, 155..156}


	


	


	$.modifiers[#Edit_Poly].SetOperation #ChamferEdge


	


	


	$.modifiers[#Edit_Poly].Commit ()


	


	


	subobjectLevel = 4 --yumusatmayi kaldirma


	


	


	$.modifiers[#Edit_Poly].SetSelection #Face #{}


	


	


	$.modifiers[#Edit_Poly].Select #Face #{5..8, 109..112, 217..224}


	


	


	$.modifiers[#Edit_Poly].SetOperation #SetSmooth


	


	


	$.modifiers[#Edit_Poly].smoothingGroupsToSet = 0


	


	


	$.modifiers[#Edit_Poly].smoothingGroupsToClear = -1


	


	


	


	


	


	subobjectLevel = 0 --cami olusturma


	


	


	select $camim


	


	


	$.name=(camisim+"cam") as string


	


	--Noktalari sert yapma


	max modify mode


	subobjectLevel = 1


	actionMan.executeAction 0 "40021"  -- Selection: Select All


	max select all


	fn filterSpline spl = (classof spl == Line or classof spl == SplineShape)


	fn changeKnotTypes btn: = 1


	(


		if selection.count == 1 and filterSpline selection[1] and (selection[1].modifiers).count == 0 do


		(


			local spl = selection[1]


			for s = 1 to (numSplines spl) do


			(


				if (knots = getKnotSelection spl s).count != 0 do


				(


					local type = #corner


					)


					for k = 1 to knots.count do setKnotType spl s knots[k] type


				)


			)


			updateshape spl


		)


	--Sert Yapma bitim


	modPanel.addModToSelection (Extrude ()) ui:on


	


	


	$.modifiers[#Extrude].amount = 0.4


	


	


	clearSelection()


	


	


						)


	


	


						select nnl


	


	


						objesayisi=0


	


	


						sayim=0


	


	


						


	


	


						


	


	


			


	


	


		


	


	


		


	


	


		


	


	


		)


	on btn7 pressed do --Tezgah Yap

		(


	


	


		


		--tezgahisim=$.name


	


	


		modPanel.addModToSelection (Shell ()) ui:on


	


	


			$.modifiers[#Shell].innerAmount = 0


	


	


	$.modifiers[#Shell].outerAmount = 2


	


	


	


	


	


		modPanel.addModToSelection (Edit_Poly ()) ui:on


	


	


	subobjectLevel = 4


	


	


	$.modifiers[#Edit_Poly].SetSelection #Face #{}


	


	


	$.modifiers[#Edit_Poly].Select #Face #{6}


	


	


	$.modifiers[#Edit_Poly].Select #Face #{3}


	


	


	$.modifiers[#Edit_Poly].Select #Face #{4}


	


	


	$.modifiers[#Edit_Poly].SetOperation #ExtrudeFace


	


	


	$.modifiers[#Edit_Poly].extrudeFaceHeight = 1.05448


	


	


	$.modifiers[#Edit_Poly].extrudeFaceType = 1


	


	


	$.modifiers[#Edit_Poly].extrudeFaceHeight = 2


	


	


	$.modifiers[#Edit_Poly].Commit ()-- buraya tamam


	


	


	$.modifiers[#Edit_Poly].SetSelection #Face #{}


	$.modifiers[#Edit_Poly].Select #Face #{9}


	$.modifiers[#Edit_Poly].Select #Face #{5}


	$.modifiers[#Edit_Poly].Select #Face #{13}


	


	$.modifiers[#Edit_Poly].SetOperation #ExtrudeFace


	


	$.modifiers[#Edit_Poly].extrudeFaceType = 1


	


	$.modifiers[#Edit_Poly].Commit ()--buraya kadar bak


	


	$.modifiers[#Edit_Poly].SetSelection #Face #{}


	


	$.modifiers[#Edit_Poly].Select #Face #{15}


	$.modifiers[#Edit_Poly].Select #Face #{22}


	$.modifiers[#Edit_Poly].Select #Face #{8}


	$.modifiers[#Edit_Poly].Select #Face #{7}


	$.modifiers[#Edit_Poly].Select #Face #{14}


	$.modifiers[#Edit_Poly].Select #Face #{16}


	$.modifiers[#Edit_Poly].SetOperation #ExtrudeFace


	$.modifiers[#Edit_Poly].extrudeFaceHeight = 0.6


	$.modifiers[#Edit_Poly].Commit ()


	$.modifiers[#Edit_Poly].SetSelection #Face #{}


	$.modifiers[#Edit_Poly].Select #Face #{15}


	$.modifiers[#Edit_Poly].Select #Face #{16}


	$.modifiers[#Edit_Poly].Select #Face #{22}


	$.modifiers[#Edit_Poly].SetOperation #ExtrudeFace


	$.modifiers[#Edit_Poly].extrudeFaceHeight = 3


	$.modifiers[#Edit_Poly].Commit ()--buraya kadar tamam


	$.modifiers[#Edit_Poly].SetSelection #Face #{}


	


	subobjectLevel = 2


		


	$.modifiers[#Edit_Poly].SetSelection #Edge #{}


	


	


	$.modifiers[#Edit_Poly].Select #Edge #{69,70,71}


	


	


	$.modifiers[#Edit_Poly].SetOperation #ChamferEdge


	


	


	$.modifiers[#Edit_Poly].chamferEdgeAmount = 0.5


	


	


	$.modifiers[#Edit_Poly].edgeChamferSegments = 4


	


	


	$.modifiers[#Edit_Poly].Commit ()


	


	$.modifiers[#Edit_Poly].SetSelection #Edge #{}


	


	subobjectLevel = 4


	$.modifiers[#Edit_Poly].SetSelection #Face #{}


	$.modifiers[#Edit_Poly].Select #Face #{1..4, 6..8, 10..12, 14, 23..24, 26..28, 34}


	$.modifiers[#Edit_Poly].ButtonOp #DetachFace


	subobjectLevel = 3


	$.modifiers[#Edit_Poly].SetSelection #Edge #{}


	$.modifiers[#Edit_Poly].Select #Edge #{1..2, 5..10, 33..35, 40}


	$.modifiers[#Edit_Poly].ButtonOp #Cap


	subobjectLevel = 0


	


	--select $Tezgahon


	


	


	--$.name=(tezgahisim+"Tezgah") as string


	


	subobjectLevel = 2


	$.modifiers[#Edit_Poly].SetSelection #Edge #{}


	$.modifiers[#Edit_Poly].Select #Edge #{46}


	$.modifiers[#Edit_Poly].Select #Edge #{56}


	$.modifiers[#Edit_Poly].Select #Edge #{49}


	$.modifiers[#Edit_Poly].Select #Edge #{45}


	$.modifiers[#Edit_Poly].Select #Edge #{48}


	$.modifiers[#Edit_Poly].Select #Edge #{50}


	$.modifiers[#Edit_Poly].SetOperation #ChamferEdge


	$.modifiers[#Edit_Poly].chamferEdgeAmount = 0.3


	--actionMan.executeAction 0 "369"


	$.modifiers[#Edit_Poly].edgeChamferSmoothType = 1


	$.modifiers[#Edit_Poly].Commit ()


	$.modifiers[#Edit_Poly].SetSelection #Edge #{}


	subobjectLevel = 3


	$.modifiers[#Edit_Poly].SetSelection #Edge #{}


	$.modifiers[#Edit_Poly].Select #Edge #{113..124, 129..132, 151..162}


	$.modifiers[#Edit_Poly].ButtonOp #Cap


	$.modifiers[#Edit_Poly].SetSelection #Edge #{}


	subobjectLevel = 0


	


	objesayisi=0


	sayim=0	


	


	


	


	


	


		)


)

Createdialog MutfakScript