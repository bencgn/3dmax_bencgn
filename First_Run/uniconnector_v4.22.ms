-- Uniconnector.ms
-- By Nikolay Litvinov (gniklit@gmail.com)
-- Created On:	2014-05-10
-- Modified:	2016-03-18
-- tested using Max 2016

macroScript FlowConnectSwitcher_macro Category:"Niklit Scripts" Tooltip:"Uconnector FlowConnect Switcher"
icon:#("SubObjectIcons",22)
(
	global FlowConnectSwitcher
	if FlowConnectSwitcher == undefined do FlowConnectSwitcher=false
	on isEnabled return selection.count>0
	on ischecked return FlowConnectSwitcher
	on Execute do FlowConnectSwitcher = if FlowConnectSwitcher != true then true else false
)
macroScript RefineConnectSwitcher_macro Category:"Niklit Scripts" Tooltip:"Uconnector RefineConnect Switcher"
icon:#("Max_Edit_Modifiers",15)
(
	global RefineConnectSwitcher
	if RefineConnectSwitcher == undefined do RefineConnectSwitcher=false
	on isEnabled return selection.count>0
	on ischecked return RefineConnectSwitcher
	on Execute do RefineConnectSwitcher = if RefineConnectSwitcher != true then true else false
)


messageBox "Category: \"Niklit Scripts\""
macroScript UniConnector Category:"Niklit Scripts" Tooltip:"UniConnector"
(
------------------------- Functions -------------------------
global NewSpline, num_CurO, Es_, gco


universal=null
struct polyFns
	(
		fn GetSelectionEdge fco node_i=fco.getselection #edge,
		fn SetSelectionEdge fco edges_bitA node_i=fco.SetSelection #Edge edges_bitA,
		fn getNumFaces_fn fco node_i=fco.getNumFaces()
	)
struct polyMODFns
	(
		fn GetSelectionEdge fco node_i=fco.getselection #edge node:selection[node_i],
		fn SetSelectionEdge fco edges_bitA node_i=(fco.SetSelection #Edge #{}; setEdgeSelection node_i fco edges_bitA keep:on),
		fn getNumFaces_fn fco node_i=fco.GetNumFaces node:selection[node_i]
	)

	fn tryInit fco =
		case classOf fco of
		(
			Editable_Poly: (universal = polyFns(); "Editable_Poly")
			Edit_Poly: (universal = polyMODFns(); "Edit_Poly")
		)
global Pos_AllAxisProportional_Rollout
fn GabaritAssigner_fn=
(
if Pos_AllAxisProportional_Rollout==undefined do Pos_AllAxisProportional_Rollout=mouse.screenpos
rollout AllAxisProportional_Rollout "GabaritAssigner" width:99 height:57
(
	checkButton ckb1 "Proportional" pos:[10,11] width:78 height:35
	on AllAxisProportional_Rollout moved pos do Pos_AllAxisProportional_Rollout=pos
)
createdialog AllAxisProportional_Rollout pos: Pos_AllAxisProportional_Rollout
isSelMode=getToolbtnState #select
oStart = pickobject()
oEnd = pickobject()
if oStart!=undefined and oEnd!=undefined and (not keyboard.escPressed)
then
(
oStartVector=oStart.max-oStart.min
oEndVector=oEnd.max-oEnd.min
Nx=oEndVector.x/oStartVector.x
Ny=oEndVector.y/oStartVector.y
Nz=oEndVector.z/oStartVector.z

if isSelMode then scale oStart [Nx,Ny,Nz]
else
 case toolmode.axisConstraints of
	(
		#x: (if AllAxisProportional_Rollout.ckb1.state==on then  scale  oStart [Nx,Nx,Nx] else scale  oStart [Nx,1,1])
		#y: (if AllAxisProportional_Rollout.ckb1.state==on then  scale  oStart [Ny,Ny,Ny] else scale  oStart [1,Ny,1])
		#z: (if AllAxisProportional_Rollout.ckb1.state==on then  scale  oStart [Nz,Nz,Nz] else scale  oStart [1,1,Nz])
		#XY: scale  oStart [Nx,Ny,1]
		#YZ: scale  oStart [1,Ny,Nz]
		#ZX: scale  oStart [Nx,1,Nz]
		Default: oStart [Nx,Ny,Nz]
	)
DestroyDialog AllAxisProportional_Rollout
)
else DestroyDialog AllAxisProportional_Rollout
)

fn MultiAttach_Spl_fn=
(
spl_ar=for i in selection where IsShapeObject i collect (convertToSplineShape i);
for i=2  to spl_ar.count do addandweld spl_ar[1] spl_ar[i] 0.002
)

fn WeldThreshold_fn = (
	maxWindow_hwnd=(windows.getChildrenHWND (windows.getDesktopHWND()))
	--for i in windows.getChildrenHWND #max do format "%\SplCount" i
	WeldThreshold_hwnd=(for i=1 to maxWindow_hwnd.count where maxWindow_hwnd[i][5]=="Weld" do exit with maxWindow_hwnd[(i+1)][1])
WM_SETFOCUS = 0x007
VK_RETURN=0x000D
WM_CHAR=0x0102
SendKeys=dotNetClass "System.Windows.Forms.SendKeys"
windows.sendMessage WeldThreshold_hwnd WM_SETFOCUS 0 0
SendKeys.SendWait "0,002"
windows.sendMessage WeldThreshold_hwnd WM_CHAR VK_RETURN 0
SendKeys.SendWait "{up}"
UIAccessor.PressButton (for i in maxWindow_hwnd where i[5]=="Weld" do exit with i[1])
)


fn DrawLineBetweenTwoPoints_fn =
(
undo on
	(
	
	slp_kn_pos=#(); for spl=1 to numSplines $ do for kn=1 to (getKnotSelection $ spl).count do append slp_kn_pos #(spl,(getKnotSelection $ spl)[kn],(getKnotPoint $ spl ((getKnotSelection $ spl)[kn]))); slp_kn_pos
		if classof $==splineShape or classof $==line do
		(
		if (numSplines $)==1 then (close $ 1; updateshape $)
		else
			(
			kn=addNewSpline $
			kn_A=addKnot $ kn #corner #line  slp_kn_pos[1][3]
			kn_B=addKnot $ kn #corner #line  slp_kn_pos[2][3]
			try updateShape $ catch ()
			setKnotSelection $ kn #(kn_A,kn_B) keep:true
			setKnotSelection $ slp_kn_pos[1][1] #(slp_kn_pos[1][2]) keep:true
			setKnotSelection $ slp_kn_pos[2][1] #(slp_kn_pos[2][2]) keep:true
			splineOps.weld $
			updateShape $
			redrawviews()
			)
		)
	)
)

fn ShapeConn_fn fco=
(
fco = $
case subobjectlevel of (
	1: 
		--if (classof selection[1]==line or classof selection[1]==SplineShape) and 
		if not (
		numselKnots = for i=1 to (numSplines selection[1]) collect getKnotSelection selection[1] i
		numKn=0;	for i in numselKnots where i.count>0 do numKn+=i.count;	numKn==2
		)
	then 
		(
		global RefineConnectSwitcher
		if RefineConnectSwitcher == undefined do RefineConnectSwitcher=false
		if subobjectlevel!=2
		then
		if RefineConnectSwitcher then (max modify mode; subobjectlevel=1; splineOps.startRefineConnect $) else (max modify mode; subobjectlevel=1; splineOps.startRefine $) -- Refine Connect
		)
	else DrawLineBetweenTwoPoints_fn()
	2: splineOps.divide fco
	3: (spl_index_int=(getSplineSelection fco)[1]
		splCount=numSegments fco spl_index_int
		arSpl=for i=1 to splCount collect i
		for i=1 to numSplines fco do
		setSegSelection fco i #()
		setSegSelection fco spl_index_int arSpl keep: on
		subObjectLevel=2
		splineOps.divide fco
		subObjectLevel=3)
	)
)



fn TriFace_fn fco=(
NumF1=fco.getNumFaces()
fco.CreateFace (fco.getSelection #Vertex as array); try fco.Commit() catch()
NumF2=fco.getNumFaces()
NumF1 != NumF2
)

fn NEXTvettoconnect_fn = (
FuV=polyop.getFacesUsingVert $ (polyop.getVertSelection $) as array
HInumberset=#(#{},0)
for i=1 to FuV.count where (polyop.getEdgesUsingFace $ FuV[i]).numberset>HInumberset[1].numberset do (HInumberset[1]=(polyop.getEdgesUsingFace $ FuV[i]);HInumberset[2]=FuV[i])
$.EditablePoly.SetSelection #Face #{HInumberset[2]}
	NumF1=$.getNumFaces()
aF    = polyop.getFaceSelection $ as Array
baEuF = polyop.getEdgesUsingFace $ aF[1]

baV     = polyop.getVertSelection $ as Array
baEuV1  = polyop.getEdgesUsingVert $ baV[1]
baEuV2  = polyop.getEdgesUsingVert $ baV[2]

baE0=baEuV1*baEuV2

aE1=(baEuF*(baEuV1+baEuV2)-baE0) as Array
baV1=(for i in aE1 collect (((polyop.getVertsUsingEdge $ i)-(baV as BitArray))as Array)[1]) as BitArray
$.EditablePoly.SetSelection #Vertex baV1
macros.run "Editable Polygon Object" "EPoly_Connect"

baF1    = (polyop.getFacesUsingEdge $ (baE0 as Array)[1])
baFcur  = polyop.getFaceSelection $
baFset=baFcur-baF1
$.EditablePoly.SetSelection #Face baFset
NumF2=$.getNumFaces()
NumF1 != NumF2
)

fn BridgeBorder_fn fco =(
NumF1=fco.getNumFaces()
fco.ButtonOp #BridgeBorder
NumF2=fco.getNumFaces()
NumF1 != NumF2
)

fn BridgePolygon_fn fco =(
NumF1=fco.getNumFaces()
fco.ButtonOp #BridgePolygon
NumF2=fco.getNumFaces()
NumF1 != NumF2
)


fn FilterOpenVert_fn fco=(
usOpenVert=(fco.getSelection #Vertex) as Array
OpenE=#()
resultType = openEdges.Check currentTime selection[1] &OpenE
allOpnVert=for e in OpenE collect fco.GetEdgeVertex e 1
FilterOpenVert = #()
	for i=1 to usOpenVert.count  do
	if	 findItem allOpnVert usOpenVert[i]!=0 do appendIfUnique FilterOpenVert usOpenVert[i]
FilterOpenVert.count>2
)

fn PostWeld_fn fco = try (fco.weldThreshold=0.002; fco.buttonOp #WeldSelected)
catch (fco.weldVertexThreshold=0.002; fco.buttonOp #WeldVertex)

fn VertConnect_ThroughE_fn fco =(
			Sys0=getRefCoordSys()
			toolMode.coordsys #local
			NumF1=fco.getNumFaces()
arVs=for i in selection collect (fco.getSelection #vertex) as Array
startVertex_id=arVs[num_CurO][1]

global startPosition_p3
startPosition_p3=fco.GetVertex arVs[num_CurO][1]
global endPosition_p3
endPosition_p3=fco.GetVertex arVs[num_CurO][2]

viewDirection_p3=(inverse(getViewTM())).row3

try (fco.cutVertices startVertex_id endPosition_p3 viewDirection_p3)
catch ( fco.StartCut #Vertex startVertex_id endPosition_p3 viewDirection_p3 node:selection[num_CurO]; fco.Commit() )
			setRefCoordSys Sys0
			PostWeld_fn fco
			NumF2=fco.getNumFaces()
			NumF1 != NumF2
)

fn EdgeConnect_ThroughE_fn fco =(
tryInit fco
arEs=for i=1 to selection.count collect (universal.GetSelectionEdge fco i) as Array
if arEs[num_CurO].count==2 do
(
startEdge_id=arEs[num_CurO][1]
EndEdge_id=arEs[num_CurO][2]
viewDirection_p3=(inverse(getViewTM())).row3

if iskindof fco Editable_poly then
(fco.cutEdges startEdge_id .5 EndEdge_id .5 viewDirection_p3
arEs=fco.getSelection #Edge
fco.setSelection #Edge arEs)
else
if iskindof fco Edit_poly do
		(
		setVertSelection selection[num_CurO] fco #{} keep:off
		for e in arEs[num_CurO] do fco.DivideEdge e .5 node:selection[num_CurO]; fco.Commit()
		arVs=for i=1 to selection.count collect (getVertSelection selection[num_CurO].mesh) as Array
		startVertex_id=arVs[num_CurO][1]
		endPosition_p3=fco.GetVertex arVs[num_CurO][2] node:selection[num_CurO]
		fco.setSelection #Edge #{} node:selection[num_CurO]
		fco.StartCut #Vertex startVertex_id endPosition_p3 viewDirection_p3 node:selection[num_CurO]; fco.Commit()
		)
	)
)

fn VertConn_fn fco =(
NumF1=fco.getNumFaces()
fco.ButtonOp #ConnectVertices
NumF2=fco.getNumFaces()
NumF1 != NumF2
)

fn so1_operation_fn fco =(
		if not VertConn_fn fco then
		if not (VertConnect_ThroughE_fn fco) then
		try NEXTvettoconnect_fn() catch
		if FilterOpenVert_fn fco then TriFace_fn fco
	max select
	)

fn DivideEdg_fn fco =try($.selectedVerts=#{(fco.DivideEdge ((polyop.getEdgeSelection $)as array)[1] 0.5)})
		catch (fco.DivideEdge (Es_ as array)[1] 0.5 node:selection[num_CurO]; fco.Commit())

fn FaceBy2EdgVectors fco=
try (
	NumF1=fco.getNumFaces()
	OE= #()
	openEdges.Check currentTime Selection[1] &OE
	edg0=fco.GetSelection #Edge
	if not (edg0*(OE as BitArray)).isEmpty
	then
		(
			VuE=try (for i in edg0 collect polyop.getVertsUsingEdge fco #{i}) catch for i in edg0 collect #{(fco.GetEdgeVertex i 1 node:selection[1]),(fco.GetEdgeVertex i 2 node:selection[1])}
			v0=((VuE[1]*VuE[2]) as array)[1]
			v12=((VuE[1]-VuE[2])+(VuE[2]-VuE[1])) as array
			v0_pos=try polyop.getvert fco v0 catch (fco.GetVertex v0 node:selection[1])
			v12pos=try for i in v12 collect polyop.getvert fco i catch for i in v12 collect (fco.GetVertex i node:selection[1])
			newVpos=(v12pos[1]+(v12pos[2]-v0_pos))
			newV=try polyop.createVert fco newVpos catch fco.CreateVertex newVpos*(selection[1]).transform node:selection[1]
			polyop.createPolygon fco #(v12[1], newV, v12[2], v0)
			fco.SetSelection #Vertex #{newV}
		)
NumF2=fco.getNumFaces()
NumF1 != NumF2
) catch false

fn EdgConnect_fn fco =(
NumF01=fco.getNumFaces()
fco.connectEdgeSegments=1
fco.ButtonOp #ConnectEdges
NumF02=fco.getNumFaces()
/*if NumF01!=NumF02 do 

baE1=fco.getSelection #Edge
fco.ButtonOp #GrowSelection
baE2=fco.getSelection #Edge
polyop.setEdgeSelection $ (baE2-baE1)
)*/
NumF01!=NumF02
)

fn conn2Edg_fn fco =(
NumF1=fco.getNumFaces()
EdgConnect_fn fco
NumF2=fco.getNumFaces()
NumF1 != NumF2
)

fn BridgeEdge_fn fco =(
NumF1=fco.getNumFaces()
fco.ButtonOp #BridgeEdge
NumF2=fco.getNumFaces()
NumF1 != NumF2
)

fn ConnectVertByEdges_fn fco=
try (
with redraw off(
NumF1=fco.getNumFaces()
baE=polyop.getEdgeSelection fco as Array

VuE1=polyop.getVertsUsingEdge fco baE[1] as Array
VuE2=polyop.getVertsUsingEdge fco baE[2] as Array

fco.connectEdgeSegments = 1
fco.ConnectEdges ()
baE1=polyop.getEdgeSelection fco

if not 
(
polyop.setVertSelection fco (#{VuE1[1]}+#{VuE2[1]})
fco.ConnectVertices vertexFlag:1
polyop.setVertSelection fco (#{VuE1[2]}+#{VuE2[2]})
fco.ConnectVertices vertexFlag:1
)
do
(
polyop.setVertSelection fco (#{VuE1[1]}+#{VuE2[2]})
fco.ConnectVertices vertexFlag:1
polyop.setVertSelection fco (#{VuE1[2]}+#{VuE2[1]})
fco.ConnectVertices vertexFlag:1
)
fco.SetSelection #Edge #{}
polyop.setEdgeSelection fco baE1
fco.EditablePoly.Remove ()

VuEend=polyop.getVertsUsingEdge fco baE as Array
VertClear2=((for i in VuEend where (polyop.getEdgesUsingVert fco i).numberset == 2 collect i) as BitArray)
polyop.setVertSelection fco VertClear2; fco.EditablePoly.Remove selLevel:#Vertex flag:1
polyop.setEdgeSelection fco baE
NumF2=fco.getNumFaces()
if	NumF1 == NumF2 do (max undo; polyop.setEdgeSelection fco baE)
NumF1 != NumF2
)
)catch (max undo ; polyop.setEdgeSelection fco baE; false)

fn so2_operation_fn fco =(
--if (if Es_.numberset==2 do if OpenEdges_sel_less2_fn() and isEdgeStream_fn fco do DistanceConnect_fn())==undefined do
if Es_.numberset==1 then DivideEdg_fn fco -- divide
else
if Es_.numberset==2
then (

	if not ConnectVertByEdges_fn fco then
	if fco.getNumEdges()<=4
	then EdgConnect_fn fco else
	if not BridgeEdge_fn fco then
		
	if not conn2Edg_fn fco then 
	if not FaceBy2EdgVectors fco then EdgeConnect_ThroughE_fn fco
	)
else
	if not BridgeEdge_fn fco then
	(
	if FlowConnectSwitcher == undefined do FlowConnectSwitcher=false
	if FlowConnectSwitcher then macros.run "PolyTools" "FlowConnect" else EdgConnect_fn fco -- Edge Connect
	)
)


fn so4_operation_fn fco =(
if (fco.getSelection #Face).numberset > 1 
then if BridgePolygon_fn fco==off do (fco.ToggleCommandMode #QuickSlice)
else (try fco.tesselateBy = 1 catch fco.tessellateByFace = 1; fco.buttonop #Tessellate; max select)
)

fn vSETi_sel_fn fco =(i_sel=1; Vet_ar=#()
				Vet_ar= try for i=1 to selection.count collect (getVertSelection selection[i].baseObject.mesh)
						catch for i=1 to selection.count collect (getVertSelection selection[i].mesh)
				while Vet_ar[i_sel].numberset==0 do i_sel+=1
				i_sel)
fn eSETi_sel_fn fco =(i_sel=1
				Edge_ar=for i=1 to selection.count collect (universal.GetSelectionEdge fco i)
				while Edge_ar[i_sel].numberset==0 do i_sel+=1
				i_sel)



	fn getRandomPos = 
	(
		mmax = 0.1
		mmin = 0.001
		[random mmax mmin, random mmax mmin, random mmax mmin]
	)

fn InsertFormSphere_fn = 
	(
		sel = selection as array
		if sel.count ==  2 then 
		(
			a = sel[1]
			b = sel[2]
			if a.parent == b then
			(
				--print "b is parent"
				avarPos = (a.pos + b.pos) / 2.0
				avarPos += getRandomPos()
				c = copy b

				c.pos =  avarPos
				try ( c.scale = (a.scale + b.scale) / 2.0 ) catch()
				a.parent = c
				c.parent = b
				c.wirecolor = (a.wirecolor + b.wirecolor) / 2.0
				
				try ( c.radius = (a.radius + b.radius) / 2.0 ) catch()
				try ( c.radius += 0.001 ) catch()
				select c
				
			)
			else if b.parent == a then
			(
				--print "a is parent"
				avarPos = (a.pos + b.pos) / 2
				avarPos += getRandomPos()
				c = copy a
				c.pos =  avarPos
				try ( c.scale = (a.scale + b.scale) / 2.0 ) catch()
				b.parent = c
				c.parent = a
				
				c.wirecolor = (a.wirecolor + b.wirecolor) / 2.0
				
				try ( c.radius = (a.radius + b.radius) / 2.0 ) catch()
				try ( c.radius += 0.001 ) catch()
				
				select c
			)
			else 
			(
				messageBox "The selected Form Spheres are not in the same branch."
			)
		)
		else
		(
			messageBox "Select two Form Spheres."
		)
	)

	fn AppendFormSphere_fn =
	(
		if selection.count != 0 then
		(
			aftersel = #()
			for i in selection do
			(
				maxmin = i.max - i.min
				widx = maxmin[1] / 1.5
				widy = maxmin[2] / 1.5
				widz = maxmin[3] / 1.5
				wirecol = i.wirecolor
				if keyboard.shiftpressed then obj2 = instance i
				else obj2 = copy i
				append aftersel obj2
				obj2.wirecolor = wirecol
				obj2.parent = i
				camview = Inverse(getViewTM())
				camdir = -camview.row3
				if getRefCoordsys() == #local then
				(
					seldir = obj2.objecttransform
					dirs = #(acos (dot camdir seldir.row1), acos (dot camdir -seldir.row1), acos (dot camdir seldir.row2), acos (dot camdir -seldir.row2), \
					acos (dot camdir seldir.row3), acos (dot camdir -seldir.row3))
					eldodir = finditem dirs (amin dirs)
					movesarr = #([0,-widy,0], [0,widy,0], [widx,0,0], [-widx,0,0], [0,0,-widz], [0,0,widz])
					in coordsys local move obj2 movesarr[eldodir]
				)
				else
				(
					dirs = #(acos (dot camdir [1,0,0]), acos (dot camdir [-1,0,0]), acos (dot camdir [0,1,0]), acos (dot camdir [0,-1,0]), \
					acos (dot camdir [0,0,1]), acos (dot camdir [0,0,-1]))
					eldodir = finditem dirs (amin dirs)
					movesarr = #([0,-widy,0], [0,widy,0], [widx,0,0], [-widx,0,0], [0,0,-widz], [0,0,widz])
					move obj2 movesarr[eldodir]
				)
			)
			aftersel.pos += getRandomPos()
			select aftersel
		)
		else
		(
			messageBox "Select one Form Sphere."
		)
	)
------------------------- Script -------------------------

case classof selection[1] of
(
Form_Sphere: (if selection.count==2 then  InsertFormSphere_fn() else if selection.count !=0 then AppendFormSphere_fn() )
default: 	(
				
					if selection.count==0 then GabaritAssigner_fn() 
					else
					if (subObjectLevel==0 or getCommandPanelTaskMode()!=#modify) then modPanel.addModToSelection (Edit_Poly ()) ui:on
					else
					if (gco = modPanel.getCurrentObject(); iskindof gco Editable_poly or iskindof gco Edit_poly)
					then
					case subobjectlevel of
									(
									 1: (
											selected_arr= --try for i=1 to selection.count where not (getVertSelection selection[i].baseobject.mesh).isEmpty collect (getVertSelection selection[i].baseobject.mesh) catch 
														for i=1 to selection.count where not (getVertSelection selection[i].mesh).isEmpty collect (getVertSelection selection[i].mesh)

											if selected_arr.count>0 and selected_arr[1].numberset>1 then (num_CurO=vSETi_sel_fn gco; so1_operation_fn gco) else
											case selected_arr.count of
											(
											0: (
												try (UIAccessor.PressButton (for i in windows.getChildrenHWND #max where i[5]=="Target Weld" do exit with i[1]))
												catch UIAccessor.PressButton (for i in (windows.getChildrenHWND (windows.getDesktopHWND())) where i[5]=="Target Weld" do exit with i[1])
												)
											1: (
														fn RemoveArr_fn=(
														vertAr_cgl = #()
														global vertsBitArr1	= #()
														global FirstVert = #()
														)
														
												(
																		RemoveArr_fn()
																		unregisterredrawviewscallback orderVertSel_fn
														
														
																		fn orderVertSel_fn =
																		(if selection.count>0 and classof gco==Editable_Poly and subobjectlevel==1
																			do	(
																					try(
																						vertsBitArr1 = gco.GetSelection #Vertex as array
																						
																						toConnectVerts=((vertsBitArr1 as bitarray)-(FirstVert as bitarray)) as array
																						
																						
																						if vertsBitArr1.count==1 do FirstVert[1]=vertsBitArr1[1]
																						
																						if keyboard.ShiftPressed then
																						with undo on (
																								if toConnectVerts.count<3 
																								then
																									for i=1 to toConnectVerts.count do
																									(
																									polyop.weldVerts $ toConnectVerts[i] FirstVert[1] (polyop.getVert $ toConnectVerts[i])
																									)
																									else
																								for i=1 to toConnectVerts.count do
																								(
																								gco.SetSelection #Vertex ((FirstVert as bitarray) + #{(toConnectVerts[i])} )
																								macros.run "Editable Polygon Object" "EPoly_Connect"
																								)
																								unregisterredrawviewscallback orderVertSel_fn
																								RemoveArr_fn()
																							)
																						) Catch()
																				)
																		)
																		registerredrawviewscallback orderVertSel_fn
												)


												--try (UIAccessor.PressButton (for i in windows.getChildrenHWND #max where i[5]=="Cut" do exit with i[1]))
												--catch UIAccessor.PressButton (for i in (windows.getChildrenHWND (windows.getDesktopHWND())) where i[5]=="Cut" do exit with i[1])
												)
											)
										)
									 2: (
									 	tryInit gco
									 	selected_arr= try for i=1 to selection.count where not (getEdgeSelection selection[i].baseobject.mesh).isEmpty collect ((getEdgeSelection selection[i].baseobject.mesh)as array)
										catch for i=1 to selection.count where not (getEdgeSelection selection[i].mesh).isEmpty collect ((getEdgeSelection selection[i].mesh)as array)
										
									 	if selected_arr.count==0 do 
									 	try (UIAccessor.PressButton (for i in windows.getChildrenHWND #max where i[5]=="Cut" do exit with i[1]))
										catch UIAccessor.PressButton (for i in (windows.getChildrenHWND (windows.getDesktopHWND())) where i[5]=="Cut" do exit with i[1])
										if selected_arr.count>0 do (num_CurO=eSETi_sel_fn gco; Es_=universal.GetSelectionEdge gco num_CurO; so2_operation_fn gco)
										)
									 3: if not (max select; BridgeBorder_fn gco) do macros.run "Editable Polygon Object" "EPoly_Cap"
									 4: (if (gco.getSelection #Face).numberset == 0 then try gco.ToggleCommandMode #CutFace catch gco.ToggleCommandMode #Cut
											else so4_operation_fn gco)
									 5: gco.ToggleCommandMode #QuickSlice
									)
					else
					if superclassof gco == shape do try (ShapeConn_fn gco; max select) catch()
					
			)
)
	
redrawviews()
)