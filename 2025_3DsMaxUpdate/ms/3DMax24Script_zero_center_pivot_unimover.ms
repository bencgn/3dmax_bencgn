--https://i.yapx.ru/rNR.gif
-- By Nikolay Litvinov (gniklit@gmail.com)
-- Created On:	2013-08-01
-- Modified:	2016-02-24
-- tested using Max 2016

messageBox "If Shift pressed then objects will move to [0,0,0]"
messageBox "Category: \"Switchers\""
macroScript ZeroCenter_PivotSwitcher Category:"Switchers" Tooltip:"Zero-Center Pivot Unimover" icon:#("Polar",1)

(
global vSel, eSel, fSel
global gco=modPanel.getCurrentObject()
global s0=selection[1]
--CoordCenter0=GetCoordCenter()

fn ttiScale_Collapse_fn=
	(with redraw off(
	WM_SETFOCUS = 0x007
	WM_RBUTTONDOWN=0x0204 --https://msdn.microsoft.com/en-us/library/windows/desktop/ms646242(v=vs.85).aspx
	toolMode.uniformScale()
	max tti
	setCoordCenter #selection
	desktopHWND = windows.getDesktopHWND()
	desktopChildren = windows.getChildrenHWND desktopHWND
	tti=for child in desktopChildren where (child[5] == "Scale Transform Type-In") do (exit with child)
	-- get the tti's dialog handle (tti[1])
	-- get its children
	ttiSpiner_hwnd = windows.getChildrenHWND tti[1]
	windows.sendMessage ttiSpiner_hwnd[32][1] WM_SETFOCUS 0 0
	windows.sendMessage ttiSpiner_hwnd[32][1] WM_RBUTTONDOWN 1 0
	UIAccessor.CloseDialog tti[1]
	max move
	))

fn AligPivSpl_fn=(
case subobjectlevel of
(
1:	(
	countKnots=for i=1 to numSplines $ collect (getKnotSelection $ i).count
	try (UIAccessor.PressButton (for i in windows.getChildrenHWND #max where i[5]=="Fuse"	do exit with i[1]))
	catch (UIAccessor.PressButton (for i in (windows.getChildrenHWND (windows.getDesktopHWND())) where i[5]=="Fuse"	do exit with i[1]))
	spl=for i=1 to countKnots.count where countKnots[i]!=0 do exit with i
	knotCur=(getKnotSelection $ spl)[1]
	posKn=getKnotPoint $ spl knotCur
	max undo
	$.pivot=posKn
	subobjectlevel=0)
2:	(
	ttiScale_Collapse_fn()
		(
		ARarSeg=for spl=1 to numSplines $ collect  getSegSelection $ spl
		arKnot=(
		for i=1 to ARarSeg.count where ARarSeg[i].count!=0 do
		for j=1 to ARarSeg[i].count  do appendIfUnique ARarSeg[i] (ARarSeg[i][j]+1)
		for i=1 to ARarSeg.count do
			(
				endKnot=numKnots $ i
				if ARarSeg[i].count>endKnot do deleteItem ARarSeg[i] ARarSeg[i].count
			)
		ARarSeg
		)
		for spl=1 to ARarSeg.count do
		setKnotSelection $ spl arKnot[spl]
		)
		countKnots=for i=1 to numSplines $ collect (getKnotSelection $ i).count
		spl=for i=1 to countKnots.count where countKnots[i]!=0 do exit with i
		knotCur=(getKnotSelection $ spl)[1]
		posKn=getKnotPoint $ spl knotCur
		max undo
		$.pivot=posKn
		subobjectlevel=0
	)
3:	(
	ttiScale_Collapse_fn()
	(
	spl_index_int=(getSplineSelection $)[1]
	KnotCount=numKnots $ spl_index_int
	knot_idx_ar= for i=1 to KnotCount collect i
	subObjectLevel=1
	for spl=1 to numSplines $ do
	setKnotSelection $ spl #()
	setKnotSelection $ spl_index_int knot_idx_ar
	)
		countKnots=for i=1 to numSplines $ collect (getKnotSelection $ i).count
		spl=for i=1 to countKnots.count where countKnots[i]!=0 do exit with i
		knotCur=(getKnotSelection $ spl)[1]
		posKn=getKnotPoint $ spl knotCur
		max undo; max undo
		$.pivot=posKn
		subobjectlevel=0
	)
	)
)

fn SO1_pivot_polymesh_fn=(vSel=((getVertSelection s0.mesh)as array); if vSel.count==1
then ($.pivot=getPointPos $ vSel[1]; SubObjectLevel=0)
else (
	ttiScale_Collapse_fn()
	PointPos=getPointPos $ vSel[1]
	s0.pivot = PointPos
	max undo
	subobjectlevel=0)
)

fn SO2_pivot_Poly_fn=
(
eSel=((gco.GetSelection #edge)as array)
ttiScale_Collapse_fn()
VuE=polyop.getVertsUsingEdge $ eSel[1] as array
PointPos=getPointPos $ VuE[1]
max undo
$.pivot=PointPos
SubObjectLevel=0
)

fn SO2_pivot_mesh_fn=
(
eSel=((getEdgeSelection $)as array)
ttiScale_Collapse_fn()
VuE=meshop.getVertsUsingEdge $ eSel[1] as array
PointPos=getPointPos $ VuE[1]
max undo
$.pivot=PointPos
SubObjectLevel=0
)

fn SO4_pivot_poly_fn=
(
fSel=((gco.getSelection #face)as Array)
if fSel.count==1
then (s0.pivot=polyop.getFaceCenter $ fSel[1]; SubObjectLevel=0)
else
	(
	ttiScale_Collapse_fn()
	VuF=polyop.getVertsUsingFace $ fSel[1] as array
	PointPos=getPointPos $ VuF[1]
	max undo
	$.pivot=PointPos
	SubObjectLevel=0
	)
)
fn SO4_pivot_mesh_fn=
(
fSel=((getFaceSelection $)as Array)
	ttiScale_Collapse_fn()
	VuF=meshop.getVertsUsingFace $ fSel[1] as array
	PointPos=getPointPos $ VuF[1]
	max undo
	$.pivot=PointPos
	SubObjectLevel=0
)


fn Poly_AlignPiv_fn=
case subobjectlevel of
(
1:	SO1_pivot_polymesh_fn()
2:	SO2_pivot_Poly_fn()
3:	SO2_pivot_Poly_fn()
4:	SO4_pivot_poly_fn()
5:	SO4_pivot_poly_fn()
)
fn Mesh_AlignPiv_fn=
case subobjectlevel of
(
1:	SO1_pivot_polymesh_fn()
2:	SO2_pivot_mesh_fn()
3:	SO4_pivot_mesh_fn()
4:	SO4_pivot_mesh_fn()
5:	SO4_pivot_mesh_fn()
)

if (subobjectlevel!=0 and subobjectlevel!=undefined)
then case classof s0 of
(
	line:			AligPivSpl_fn()
	SplineShape:	AligPivSpl_fn()
	Editable_Poly:	Poly_AlignPiv_fn()
	PolyMeshObject:	Poly_AlignPiv_fn()
	Editable_Mesh:	Mesh_AlignPiv_fn()
	Edit_Mesh:		Mesh_AlignPiv_fn()
)
else (
	if keyboard.shiftPressed
	then for i in selection do i.pos=[0,0,0]
	else
		(
		maxOps.pivotMode=#pivotOnly
		global pivState
		case pivState of
			(
			undefined:(for i in selection do CenterPivot i; pivState=true)
			true:(for i in selection where i.pivot!=[0,0,0] do i.pivot=[0,0,0]; pivState=undefined)
			)
		max hierarchy mode
		max modify mode
		)
	)
--setCoordCenter CoordCenter0
)