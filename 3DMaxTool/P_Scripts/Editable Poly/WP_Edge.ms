a=(polyop.getEdgeSelection $) as array
if a.count!=0 do
(
	a=(polyop.getVertsUsingEdge $ a[1]) as array

	c=tape target:(Targetobject pos:$.verts[a[1]].position)
	c.position=$.verts[a[2]].position
	WorkingPivot.setTM c.transform
	WorkingPivot.UseMode= true
	delete c
	completeRedraw() 
	redrawViews() 	
)