macroScript Mover Category:"Niklit Scripts" Tooltip:"TransformByStep-Mover" icon: #("UVWUnwrapModes",1)
(
--______________________________________________________________________________________
MoveState=GetToolBtnState #move
gco=modPanel.getCurrentObject()
if classof gco==Unwrap_UVW then gco.move() else
(
global Pos_MoverRollout, MoverRollout, vectorMove
if vectorMove==[0,0,0] do vectorMove=undefined
if vectorMove==undefined do 
vectorMove=case toolmode.axisConstraints of
		(
		#x:	[0.1,0,0]
		#y:	[0,0.1,0]
		#z:	[0,0,0.1]
		
		#XY: [0.1,0.1,0]
		#YZ: [0,0.1,0.1]
		#ZX: [0.1,0,0.1]
		)

if Pos_MoverRollout==undefined do Pos_MoverRollout=mouse.screenpos
rollout MoverRollout "MoverRollout" width:90 height:103
(
	spinner 'spn1' "Dist" width:80 height:16 align:#left range:[-100,100,0.1] scale:0.1 pos:[10,4]
	checkButton 'ckb1' "Invert" width:65 height:44 align:#left tooltip: "Hotkey: Esc+W"
		Button 'btn1' "Reset" width:65 height:25 align:#left --6pos:[30,11]

on MoverRollout open do
	(
	spn1.value=(for i=1 to 3 where vectorMove[i]!=0 collect vectorMove[i])[1]
	case toolmode.axisConstraints of
		(
			#x: (vectorMove[1]=spn1.value)
			#y: (vectorMove[2]=spn1.value)
			#z: (vectorMove[3]=spn1.value)

			#XY: (vectorMove[1]=spn1.value; vectorMove[2]=spn1.value)
			#YZ: (vectorMove[2]=spn1.value; vectorMove[3]=spn1.value)
			#ZX: (vectorMove[1]=spn1.value; vectorMove[3]=spn1.value)
			--default: messageBox "Activate one axis!" title:"Align to XYZ"
		)
	)

on spn1 changed arg do
	(
	vectorMove=[0,0,0]
	case toolmode.axisConstraints of
	(
		#x: vectorMove[1]=arg
		#y: vectorMove[2]=arg
		#z: vectorMove[3]=arg

		#XY: (vectorMove[1]=arg; vectorMove[2]=arg)
		#YZ: (vectorMove[2]=arg; vectorMove[3]=arg)
		#ZX: (vectorMove[1]=arg; vectorMove[3]=arg)
		--default: messageBox "Activate one axis!" title:"Align to XYZ"
	)
	)

on ckb1 changed state do 
(
spn1.value*=(-1)
vectorMove*=(-1)
)
on btn1 pressed do 
with undo on for i in selection do
(
tm=i.transform
tm.row4=(matrix3 1)[4]
i.transform=tm
)

on MoverRollout moved pos do Pos_MoverRollout=pos

)

fn dialog_isOpen_fn nameRolloutAsString=
(
dialog_isOpen = false
ChildWindows = UIAccessor.GetChildWindows (DialogMonitorOPS.GetWindowHandle())
--for i in ChildWindows do format "%\n" (UIAccessor.GetWindowText i)
for i in ChildWindows where (UIAccessor.GetWindowText i)==nameRolloutAsString do exit with dialog_isOpen = true
dialog_isOpen
)
--______________________________________________________________________________________



global screenAXIS

if keyboard.escPressed 
then
	(
		if dialog_isOpen_fn "MoverRollout"
		then (
				MoverRollout.spn1.value*=(-1)
				MoverRollout.ckb1.state=if MoverRollout.ckb1.state==false then on else off
				vectorMove*=(-1)
			 )
		else (CreateDialog MoverRollout pos:Pos_MoverRollout; max move)
	)
else
	if (MoveState and dialog_isOpen_fn "MoverRollout")
	then
			(
				case toolmode.axisConstraints of
				(
					#x: (vectorMove=[0,0,0] ;vectorMove[1]=MoverRollout.spn1.value; screenAXIS=(inverse(getViewTM())).row1*vectorMove.x)
					#y: (vectorMove=[0,0,0] ;vectorMove[2]=MoverRollout.spn1.value; screenAXIS=(inverse(getViewTM())).row2*vectorMove.y)
					#z: (vectorMove=[0,0,0] ;vectorMove[3]=MoverRollout.spn1.value; screenAXIS=(inverse(getViewTM())).row3*vectorMove.z)

				#XY: (vectorMove[1]=MoverRollout.spn1.value; vectorMove[2]=MoverRollout.spn1.value; screenAXIS=[0,0,0])
				#YZ: (vectorMove[2]=MoverRollout.spn1.value; vectorMove[3]=MoverRollout.spn1.value; screenAXIS=[0,0,0])
				#ZX: (vectorMove[1]=MoverRollout.spn1.value; vectorMove[3]=MoverRollout.spn1.value; screenAXIS=[0,0,0])
				--default: messageBox "Activate one axis!" title:"Align to XYZ"
				)

	fn	move_fn=if getRefCoordSys()==#screen
			then 
			(
				global tm0 
				when select $ changes do tm0=undefined
				if tm0==undefined do tm0=$.transform 
				if getRefCoordSys()==#screen or not (viewport.getType()==#view_persp_user or viewport.getType()==#view_iso_user)
				then 
				(
				screenTM=tm0*(getViewTM())
				screenTM.pos+=vectorMove
				worldTM=screenTM*(inverse(getViewTM()))
				$.transform=worldTM
				tm0=$.transform
				)
			)
			else move $ vectorMove


				if classof $.modifiers[1]==SliceModifier then (modPanel.getCurrentObject()).Slice_Plane.Position += vectorMove
				else
				case subobjectlevel of
				(
				undefined: move_fn()
				0: move_fn()
				1: (if getRefCoordSys()==#screen then vectorMove=screenAXIS; if $.useSoftSel==true then polyop.moveVert $ #all vectorMove useSoftSel:true else polyop.moveVert $ $.selectedVerts vectorMove useSoftSel: off )
				2: (if getRefCoordSys()==#screen then vectorMove=screenAXIS; vrt=polyop.getVertsUsingEdge $ (GetEdgeSelection $); if $.useSoftSel==true then ($.SetSelection #Vertex vrt; polyop.moveVert $ #all vectorMove useSoftSel:true) else polyop.moveVert $ vrt vectorMove useSoftSel: off)
				3: (if getRefCoordSys()==#screen then vectorMove=screenAXIS; vrt=polyop.getVertsUsingEdge $ (GetEdgeSelection $); if $.useSoftSel==true then ($.SetSelection #Vertex vrt; polyop.moveVert $ #all vectorMove useSoftSel:true) else polyop.moveVert $ vrt vectorMove useSoftSel: off)
				4: (if getRefCoordSys()==#screen then vectorMove=screenAXIS; vrt=polyop.getVertsUsingFace $ (GetFaceSelection $); if $.useSoftSel==true then ($.SetSelection #Vertex vrt; polyop.moveVert $ #all vectorMove useSoftSel:true) else polyop.moveVert $ vrt vectorMove useSoftSel: off)
				5: (if getRefCoordSys()==#screen then vectorMove=screenAXIS; vrt=polyop.getVertsUsingFace $ (GetFaceSelection $); polyop.moveVert $ vrt vectorMove useSoftSel: off)
				)
			)
		else max Move
			
	)
)




/*
Rotation
Objects
Subobjects
Slice		Modifier
symmetry	Modifier
Uvwmap	Modifier
mirror	Modifier
Bend	Modifier

 Author: Nikolay Litvinov
 Created in the 3dsMax 2016
*/

macroScript Rotator Category:"Niklit Scripts"	Tooltip:"TransformByStep-Rotator" icon: #("UVWUnwrapModes",3)
(
RotateState=GetToolBtnState #rotate
gco=modPanel.getCurrentObject()
------------------------------------------------------------------------------------------------------------
global Pos_RotatorRollout, RotatorRollout, Ang
if Pos_RotatorRollout==undefined do Pos_RotatorRollout=mouse.screenpos
--ROLLOUT--
rollout RotatorRollout "RotatorRollout" width:90 height:125
(
	spinner 'spn1' "Angle" width:80 height:16 align:#left range:[-360,360,90.0] scale:0.001 pos:[10,4]
	checkButton 'ckb1' "Invert" width:65 height:44 align:#left tooltip: "Hotkey: Esc+E"
	Button 'btn1' "Reset" width:55 height:25 align:#left pos:[20,75]

	Button 'btnX' "" width:25 height:8 align:#left pos:[19,105] tooltip: "Rotate by 2Vert or Edge to X View"
	Button 'btnY' "" width:8 height:25 align:#left pos:[6,76] tooltip: "Rotate by 2Vert or Edge to Y View"
	Button 'btnZ' "z" width:15 height:15 align:#left pos:[3,102] tooltip: "Rightclick - rotate by quat"
	
	

on RotatorRollout open do
	(
	Ang=spn1.value
		global WorldToScreenPos()
		fn WorldToScreenPos p =
		(
		local screen_width = RenderWidth
		local screen_height = RenderHeight
		local thePos = p * viewport.getTM()
		local screen_origin = mapScreenToView [0,0] (thePos.z) [screen_width,screen_height]
		local end_screen = mapScreenToView [screen_width,screen_height] (thePos.z) [screen_width,screen_height]
		local world_size = screen_origin-end_screen
		local x_aspect = screen_width/(abs world_size.x)
		local y_aspect = screen_height/(abs world_size.y)
		local screen_coords = point2 (x_aspect*(thePos.x-screen_origin.x)) (-(y_aspect*(thePos.y-screen_origin.y)))
		return screen_coords
		)
	)
on spn1 changed arg do
	(
	Ang=arg
	)
on ckb1 changed state do 
(
spn1.value*=(-1)
Ang*=(-1)
)
on btn1 pressed do 
with undo on for i in selection do
(
tm=i.transform
tm.row1=(matrix3 1)[1]; tm.row2=(matrix3 1)[2]; tm.row3=(matrix3 1)[3]
i.transform=tm
)

on btnX pressed do
with undo on try (
gco=modPanel.getCurrentObject()
if classof gco==Unwrap_UVW do
(
DesktopChild=(windows.getChildrenHWND (windows.getDesktopHWND()))
--clearlistener(); for i in DesktopChild do format "%\n" i
UIAccessor.PressButton (for i=1 to DesktopChild.count where DesktopChild[i][4]=="RollupPanelTitle" and DesktopChild[i][5]=="Quick Transform" do exit with DesktopChild[(i+8)][1])
)
global s1=selection[1]
global PointPos=#()
if classof gco==Editable_Poly then
(
		fn ViewTransformTM=(
		p1 = WorldToScreenPos PointPos[2]
		p2 = WorldToScreenPos PointPos[1]
		vec = normalize (p1 - p2)
		horizont = [1,0,0]
		ang = acos (dot [vec.x,vec.y,0] horizont)
		if p1.y <= p2.y then ang *= (-1)
		if ang < -135 do ang=180+ang
		if ang > 135 do ang=ang-180
		--viewport.SetTM ((viewport.GetTM()) * RotateZMatrix ang)
		vectViewport = (inverse(getViewTM())).row3
		rotate s1 (angleaxis ang vectViewport)
		)

		(
		s_lvl0=subobjectLevel
		--suspendediting()
		ResetXForm s1; if converttosplineshape s1==undefined do converttopoly s1
		with redraw off ViewTransformTM()
		ResetXForm s1; if converttosplineshape s1==undefined do converttopoly s1
		--resumeediting()
		subobjectLevel = s_lvl0
		)
	)
 	else 
 		if selection.count==1 and (classof $==SplineShape or classof $==line)
		then case subobjectlevel of
				(
					default: if numKnots $==2 do PointPos=#(getKnotPoint $ 1 1, getKnotPoint $ 1 2)
					1: GetKnot_Pos_fn()
					2: (FN_Seg_2_Knot_Ctrl_1(); GetKnot_Pos_fn())
				)
		else PointPos = case subobjectlevel of
				(
					1: (vert=getVertSelection s1.mesh as array; if vert.count>0 do for i=1 to 2 collect getPointPos s1 vert[i])
					2: (vert=(PolyOp.GetVertsUsingEdge s1 (polyop.getEdgeSelection s1)) as array; if vert.count>0 do for i=1 to 2 collect getPointPos s1 vert[i])
				)
) catch()

on btnY pressed do 
with undo on try (
gco=modPanel.getCurrentObject()
if classof gco==Unwrap_UVW do
(
DesktopChild=(windows.getChildrenHWND (windows.getDesktopHWND()))
--clearlistener(); for i in DesktopChild do format "%\n" i
UIAccessor.PressButton (for i=1 to DesktopChild.count where DesktopChild[i][4]=="RollupPanelTitle" and DesktopChild[i][5]=="Quick Transform" do exit with DesktopChild[(i+8)][1])
)
global s1=selection[1]
global PointPos=#()
if classof gco==Editable_Poly then
(

	
		fn ViewTransformTM=(
		p1 = WorldToScreenPos PointPos[2]
		p2 = WorldToScreenPos PointPos[1]
		vec = normalize (p1 - p2)
		horizont = [1,0,0]
		ang = acos (dot [vec.x,vec.y,0] horizont)
		if p1.y <= p2.y then ang *= (-1)
		ang=ang-270
		--viewport.SetTM ((viewport.GetTM()) * RotateZMatrix ang)
		vectViewport = (inverse(getViewTM())).row3
		rotate s1 (angleaxis ang vectViewport)
		)
					(
			s_lvl0=subobjectLevel
			--suspendediting()
			ResetXForm s1; if converttosplineshape s1==undefined do converttopoly s1
			with redraw off ViewTransformTM()
			ResetXForm s1; if converttosplineshape s1==undefined do converttopoly s1
			--resumeediting()
			subobjectLevel = s_lvl0
			)

		)
 else 	if selection.count==1 do
		if	classof $==SplineShape or classof $==line 
		then case subobjectlevel of
				(
					default: if numKnots $==2 do PointPos=#(getKnotPoint $ 1 1, getKnotPoint $ 1 2)
					1: GetKnot_Pos_fn()
					2: (FN_Seg_2_Knot_Ctrl_1(); GetKnot_Pos_fn())
				)
		else PointPos = case subobjectlevel of
				(
					1: (vert=getVertSelection s1.mesh as array; if vert.count>0 do for i=1 to 2 collect getPointPos s1 vert[i])
					2: (vert=(PolyOp.GetVertsUsingEdge s1 (polyop.getEdgeSelection s1)) as array; if vert.count>0 do for i=1 to 2 collect getPointPos s1 vert[i])
				)
) catch()

on btnZ pressed do try 
(
with undo on
	(
	curTM=$.transform
	curTM.row1=(inverse (viewport.getTM())).row1
	curTM.row2=(inverse (viewport.getTM())).row2
	curTM.row3=(inverse (viewport.getTM())).row3
	$.transform=curTM
	)
) catch()
on btnZ rightclick do with undo on rotate $ (viewport.getTM()).rotationpart

on RotatorRollout moved pos do Pos_RotatorRollout=pos
)
--END ROLLOUT--

fn dialog_isOpen_fn nameRolloutAsString=
(
dialog_isOpen = false
ChildWindows = UIAccessor.GetChildWindows (DialogMonitorOPS.GetWindowHandle())
--for i in ChildWindows do format "%\n" (UIAccessor.GetWindowText i)
for i in ChildWindows where (UIAccessor.GetWindowText i)==nameRolloutAsString do exit with dialog_isOpen = true
dialog_isOpen
)

if keyboard.escPressed
then
	if dialog_isOpen_fn "RotatorRollout"
	then (
		 RotatorRollout.spn1.value*=(-1)
		 RotatorRollout.ckb1.state=if RotatorRollout.ckb1.state==false then on else off
		 Ang*=(-1)
		 )
	else (CreateDialog RotatorRollout pos:Pos_RotatorRollout; max rotate)
else
if (RotateState and dialog_isOpen_fn "RotatorRollout")
then
--if toolmode.commandmode!=#Rotate then
(
global XYZaxsis, X_Euler, Y_Euler, Z_Euler

XYZaxsis=#([1,0,0],[0,1,0],[0,0,1])

if getRefCoordSys()!=#screen 
then
(
X_Euler=angleaxis Ang XYZaxsis[1]
Y_Euler=angleaxis Ang XYZaxsis[2]
Z_Euler=angleaxis Ang XYZaxsis[3]
)
else
(
X_Euler=angleaxis Ang XYZaxsis[2]
Y_Euler=angleaxis Ang XYZaxsis[3]
Z_Euler=angleaxis Ang XYZaxsis[1]
)
fn Obj_Subobj_rotate_fn=
if subobjectlevel!=0 and subobjectlevel!=undefined
then (

		fn Rxyz_fn arg1 arg2 =(
		WM_SETFOCUS = 0x007
		VK_RETURN=0x000D
		WM_CHAR=0x0102
		WM_ACTIVATE = 0x6
		SendKeys = dotNetClass "System.Windows.Forms.SendKeys"
		sl0=subobjectlevel
		toolmode0=toolmode.commandmode
		modPanel.addModToSelection (FFD_2x2x2 ()) ui:on; subObjectLevel=1; max select all
		toolmode.commandmode=#Rotate; max tti
		tti=for i in windows.getChildrenHWND (windows.getDesktopHWND()) where i[5] == "Rotate Transform Type-In" do exit with i[1]
		tti_ch = windows.getChildrenHWND tti
		--for i in tti_ch do format "%\n" i
		UIAccessor.sendMessage tti_ch[arg1][1] WM_SETFOCUS 0 0
		--Windows.sendMessage tti WM_ACTIVATE tti 0
		
		sc=Ang as string
		numP=(for i=1 to sc.count where sc[i]=="." collect i)[1]
		sc=replace sc numP 1 ","
		SendKeys.SendWait sc

		windows.sendMessage tti_ch[arg2][1] WM_CHAR VK_RETURN 0
		UIAccessor.CloseDialog tti
		if classof (modPanel.getCurrentObject())==FFD_2x2x2 do for o in selection do maxOps.CollapseNodeTo o 1 off
		toolmode.commandmode=toolmode0
		subobjectlevel=sl0
		)

		Rxyz=#(10,12,13,15,16,18)
		case toolmode.axisConstraints of
			(
				#x: Rxyz_fn Rxyz[1] Rxyz[2]
				#y: Rxyz_fn Rxyz[3] Rxyz[4]
				#z: Rxyz_fn Rxyz[5] Rxyz[6]
				default: messageBox "Activate one axis!" title:"Align to XYZ"
			)
	)
else
case toolmode.axisConstraints of
	(
		#x: if selection.count>1 then about $.center rotate $ X_Euler else rotate $ X_Euler
		#y: if selection.count>1 then about $.center rotate $ Y_Euler else rotate $ Y_Euler
		#z: if selection.count>1 then about $.center rotate $ Z_Euler else rotate $ Z_Euler
		default: messageBox "Activate one axis!" title:"Align to XYZ"
	)

----------------------------------SCRIPT----------------------------------
if keyboard.altPressed
then (
	fn RandomRotation_fn ax=for i in selection do rotate i (angleaxis (random -360 360) ax)
	case toolmode.axisConstraints of
		(
			#x: (RandomRotation_fn XYZaxsis[1])
			#y: (RandomRotation_fn XYZaxsis[2])
			#z: (RandomRotation_fn XYZaxsis[3])
			default: messageBox "Activate one axis!" title:"Align to XYZ"
		)
	)
else
case classof gco of
		(
SliceModifier:	(
				fn xyzMT_fn AngARG axisARG=(xTMPoint=point(); rotate xTMPoint (angleaxis AngARG axisARG); xTM=xTMPoint.transform; delete xTMPoint; xTM)
				case toolmode.axisConstraints of
					(
						#x: gco.Slice_Plane.transform=xyzMT_fn Ang XYZaxsis[2]
						#y: gco.Slice_Plane.transform=xyzMT_fn Ang XYZaxsis[1]
						#z: gco.Slice_Plane.transform=xyzMT_fn Ang XYZaxsis[3]
						default: messageBox "Activate one axis!" title:"Align to XYZ"
					)
				)
		Uvwmap:	(subObjectLevel=1
				case toolmode.axisConstraints of
					(
						--#x: gco.Gizmo.transform=rotate gco.Gizmo.transform X_Euler
						--#y: gco.Gizmo.transform=rotate gco.Gizmo.transform Y_Euler
						--#z: gco.Gizmo.transform=rotate gco.Gizmo.transform Z_Euler

						#x: gco.axis = 2
						#y: gco.axis = 0
						#z: gco.axis = 1
						default: messageBox "Activate one axis!" title:"Align to XYZ"
					)
					UIAccessor.PressButton (for i in windows.getChildrenHWND #max where i[5]=="Fit" do exit with i[1])
				)
	symmetry: case toolmode.axisConstraints of
					(
						#x: gco.axis=0
						#y: gco.axis=1
						#z: gco.axis=2
						default: messageBox "Activate one axis!" title:"Align to XYZ"
					)
		mirror:	case toolmode.axisConstraints of
					(
						#x: gco.mirror_axis=0
						#y: gco.mirror_axis=1
						#z: gco.mirror_axis=2
						default: messageBox "Activate one axis!" title:"Align to XYZ"
					)
		Bend:	case toolmode.axisConstraints of
					(
						#x: gco.BendAxis=0
						#y: gco.BendAxis=1
						#z: gco.BendAxis=2
						default: messageBox "Activate one axis!" title:"Align to XYZ"
					)
	Unwrap_UVW:	gco.RotateSelectedCenter (degToRad Ang)
		Default:	(
			if getRefCoordSys()==#screen or not (viewport.getType()==#view_persp_user or viewport.getType()==#view_iso_user) 
			then 
				if subobjectlevel!=0 and subobjectlevel!=undefined 
				then PolyToolsModeling.RotateSelection Ang 1 -(viewport.getTM()).row3
				else rotate $ Ang (inverse(viewport.getTM())).row3
			else Obj_Subobj_rotate_fn()
			)
		)
	max views redraw
	)
else max rotate
	
	------------------------------------------------------------------------------------------------------------
)







macroScript Scaler Category:"Niklit Scripts" Tooltip:"TransformByStep-Scaler" icon: #("UVWUnwrapModes",5)
(
gco=modPanel.getCurrentObject()
if classof gco==Unwrap_UVW 
then
	case gco.getFreeFormMode() of 
	(
	false: gco.setFreeFormMode on
	true: (gco.setFreeFormMode off; gco.scale())
	)
else
	(
--______________________________________________________________________________________
ScaleState=if (GetToolBtnState #uscale) or (GetToolBtnState #nuscale) then true else false

if Pos_ScalerRollout==undefined do Pos_ScalerRollout=mouse.screenpos

rollout ScalerRollout "ScalerRollout" width:90 height:115
(
	spinner 'spn1' "Sc" width:80 height:16 align:#left range:[-10000,10000,100.1] scale:0.1 pos:[10,4]
	checkButton 'ckb1' "Invert" width:65 height:44 align:#left pos:[13,22] tooltip: "Hotkey: Esc+R"
	Button 'btn1' "ResXF" width:65 height:25 align:#left --6pos:[30,11]
	checkbox 'chk1' "tti" width:31 height:12 align:#left --pos:[15,68]

	fn FixResetObj_fn =
	for i in selection as array where (superclassof i)==GeometryClass do
	(
	select i
	selFixed=#()
	layer0=i.layer
	pivot0=i.pivot
	meshO = editable_mesh name: i.name wirecolor: (random black white)
	converttoPoly meshO
	meshO.attach i meshO
	append selFixed meshO
	layer0.addnode meshO
	select selFixed
	$.backfacecull = on; addModifier $ (Normalmodifier flip: on); addModifier $ (Normalmodifier flip: on)
	converttoPoly $; $.pivot=pivot0
	--$.material=undefined
	)

on ScalerRollout open do()
on spn1 changed arg do()
on ckb1 changed state do spn1.value*=(-1)
on btn1 pressed do FixResetObj_fn() --for i in selection do (ResetXForm i; collapseStack i)

on ScalerRollout moved pos do Pos_ScalerRollout=pos
)
--______________________________________________________________________________________

fn dialog_isOpen_fn nameRolloutAsString=
(
dialog_isOpen = false
ChildWindows = UIAccessor.GetChildWindows (DialogMonitorOPS.GetWindowHandle())
--for i in ChildWindows do format "%\n" (UIAccessor.GetWindowText i)
for i in ChildWindows where (UIAccessor.GetWindowText i)==nameRolloutAsString do exit with dialog_isOpen = true
dialog_isOpen
)

fn ScalePolyMod_fn AmountSC=
with redraw off
(
	global SendKeys = dotNetClass "System.Windows.Forms.SendKeys"
	WM_SETFOCUS = 0x007
	global VK_RETURN=0x000D
	global WM_CHAR=0x0102
	toolMode.uniformScale()
	max tti
	desktopHWND = windows.getDesktopHWND()
	desktopChildren = windows.getChildrenHWND desktopHWND
	global tti=for child in desktopChildren where (child[5] == "Scale Transform Type-In") do (exit with child)
	-- get the tti's dialog handle (tti[1])
	-- get its children
	ttiSpiner_hwnd = windows.getChildrenHWND tti[1]
	windows.sendMessage ttiSpiner_hwnd[11][2] WM_SETFOCUS 0 0
	SendKeys.SendWait AmountSC
	SendKeys.SendWait "{ENTER}"
 	--for i=1 to desktopChildren.count do for k=1 to (desktopChildren[i]).count where desktopChildren[i][k]==658216 do format "% %" i k
	windows.sendMessage desktopChildren[1021][1] WM_SETFOCUS 0 0
OK
)

if keyboard.escPressed 
then
	if dialog_isOpen_fn "ScalerRollout" 
	then
	(
	ScalerRollout.spn1.value*=(-1)
	ScalerRollout.ckb1.state=if ScalerRollout.ckb1.state==false then on else off
	)
	else (CreateDialog ScalerRollout pos:Pos_ScalerRollout; max scale)
else
	if (ScaleState and dialog_isOpen_fn "ScalerRollout")
	then
		(
			sc=ScalerRollout.spn1.value as string
			numP=(for i=1 to sc.count where sc[i]=="." collect i)[1]
			sc=replace sc numP 1 ","
			ScalePolyMod_fn sc
			if ScalerRollout.chk1.checked==false then UIAccessor.CloseDialog tti[1] else SendKeys.SendWait "{ESC}"
			--(vbsESCPath = (GetDir #scripts) + "\\ESC.vbs"; shellLaunch "explorer.exe" vbsESCPath)
		)
	else max scale
			
		
	)
)