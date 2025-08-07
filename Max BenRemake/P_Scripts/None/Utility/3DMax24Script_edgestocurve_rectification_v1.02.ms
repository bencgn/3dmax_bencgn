--Author: Nikolay Litvinov
--Released 10.02.2020

macroScript EdgesToCurveRectificationDistribution Category:"Niklit Scripts" Tooltip:"EdgesCR Distribution"
icon:#("UVWUnwrapTools2",19)
(
	global ECR_Distribution
	if ECR_Distribution == undefined do ECR_Distribution=false
	on isEnabled return selection.count>0
	on ischecked return ECR_Distribution
	on Execute do ECR_Distribution = if ECR_Distribution != true then true else false
)

macroScript EdgesCRGeometryEversion Category:"Niklit Scripts" Tooltip:"EdgesCR Geometry Eversion"
icon:#("Standard_Modifiers",4)
(
	global ECRGE
	if ECRGE == undefined do ECRGE=false
	on isEnabled return selection.count>0
	on ischecked return ECRGE
	on Execute do ECRGE = if ECRGE != true then true else false
)

macroScript EdgesToCurveRectification category:"Niklit Scripts"	toolTip:"Edges ToCurve/Rectification"	--icon:#("PowerBoolean",9)	silentErrors: true 
(

global Vrt, VertEnds, ECRGE, ECR_Distribution
if ECRGE == undefined do ECRGE=false
if ECR_Distribution == undefined do ECR_Distribution=false
global ss
GroupEDG=#()

if subobjectlevel==1 do selection[1].ConvertSelectionToBorder #Vertex #Edge
global edg=GetEdgeSelection selection[1]
tmp=edg
while (not tmp.isEmpty) do
(
selection[1].setRingShift -1 false false
append GroupEDG (tmp=(edg-GetEdgeSelection selection[1]))
edg=(edg-(edg-GetEdgeSelection selection[1]))
)
GroupEDG=for i in GroupEDG where not i.isEmpty collect i
append GroupEDG  (GetEdgeSelection selection[1])


fn DrawLineBetweenTwoPoints_fn pointA pointB =
(
	ss = SplineShape pos:pointA
	addNewSpline ss
	addKnot ss 1 #corner #curve PointA
	addKnot ss 1 #corner #curve PointB
	updateshape ss
)

fn meshverttoshape_fn Curve = (

----- Collect verts, edges
global minlg=#()
if VertEnds.count==0 do
(
convertToSplineShape Curve
lg=for i=1 to Vrt.numberset	collect length (polyop.getVert selection[1] (Vrt as array)[i]-getKnotPoint Curve 1 1)
minlg=#((Vrt as array)[(for i=1 to lg.count where lg[i]==amin lg collect i)[1]])
VertEnds=minlg
)
global vx=#()
ed=#()
oldE=#{}
vx[1]=VertEnds[1]
ed[1]=(((polyop.getEdgesUsingVert selection[1] vx[1])*edg) as Array)[1]
oldE[ed[1]]=true
for i=2 to Vrt.numberset do
	(
	vx[i]=(((polyop.getVertsUsingEdge selection[1] ed[(i-1)])-#{vx[i-1]})as array)[1]
	oldE[ed[i-1]]=true
	ed[i]=(((polyop.getEdgesUsingVert selection[1] vx[i])*edg-oldE) as Array)[1]
	)
-----
global parameter_curv=#()
fn parameter_curv_fn=
(
parameter_curv=#()
sp=splineShape()
addnewSpline sp
vxPos=for i in vx collect polyop.getVert selection[1] i

if selection.count==1 -- not to curve (Rectification)
then for i=1 to vxPos.count do addKnot sp 1 #corner #line vxPos[i]
else
(
if ECR_Distribution 
then
for i=1 to vxPos.count do addKnot sp 1 #corner #line vxPos[i]
else
for i=vxPos.count to 1 by -1  do addKnot sp 1 #corner #line vxPos[i]
)
partArr=for i=1 to vxPos.count-1 collect (getSegLengths sp 1)[i]
parameter_curv[1]=0.0
for i=1 to partArr.count do parameter_curv[i+1]=parameter_curv[i]+partArr[i]
delete sp
)

	if minlg.count!=0
	then 
		if not keyboard.escPressed then parameter_curv_fn()
		else
		for i=0 to Vrt.numberset do append parameter_curv (1.0/(Vrt.numberset)*i) 
	else
		if not keyboard.escPressed then parameter_curv_fn()
		else
		for i=0 to Vrt.numberset-1 do append parameter_curv (1.0/(Vrt.numberset-1)*i)

if selection.count>1 
then
	if (not ECRGE) do vx=for i=vx.count to 1 by-1 collect vx[i]
else
if ECRGE do vx=for i=vx.count to 1 by-1 collect vx[i]

	for i=1 to vx.count do
		(
		selection[1].SetSelection #Vertex #{vx[i]};	selection[1].selectedVerts[1]= pathInterp Curve 1 parameter_curv[i]
		selection[1].SetSelection #Vertex Vrt
		)

)

for k in GroupEDG do
	(
		SetEdgeSelection selection[1] (edg=k)
		Vrt=polyop.getVertsUsingEdge selection[1] edg
		VertEnds=for i in Vrt as array where ((polyop.getEdgesUsingVert selection[1] i)*edg).numberset==1 collect i

		
		if selection.count==2 and (superClassOf selection[2])==shape then ss=selection[2] else
		DrawLineBetweenTwoPoints_fn (polyop.getVert selection[1] VertEnds[1]) (polyop.getVert selection[1] VertEnds[2])
		(meshverttoshape_fn ss; delete ss)
		--try (meshverttoshape_fn ss; delete ss) catch messageBox "Please select a loop from verts or edges>1 and not closed full ring"
	)
)