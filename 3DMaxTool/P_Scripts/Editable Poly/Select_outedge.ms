
if ($==undefined or $selection.count>1 or (classOf (modPanel.getCurrentObject())!=Editable_Poly)) do (return 0;)
	
subObjectLevel=3;
actionMan.executeAction 0 "40021"
select1=$.EditablePoly.GetSelection #Edge
	
	
	
	
	
alle = polyop.getNumEdges $.baseobject --get number of edges in object
okedges = #() --empty array to put edges in from the loop below


for i = 1 to alle do --loop through all edges (
(
efaces = polyop.getFacesUsingEdge $.baseobject i --get each edges faces
fnorms = for d in efaces collect (polyop.getFaceNormal $.baseobject d) --collect the facenormals into an array


if fnorms.count == 2 do --if the edge is not open do(
(
diffangle = acos (dot fnorms[1] fnorms[2]) --compare the two facenormals
if diffangle >= 60 do append okedges i --if the angle is 60 or greater put the edge in the okedges array
)

)


polyop.setEdgeSelection $.baseobject okedges --select the edges
select2=$.EditablePoly.GetSelection #Edge
$.EditablePoly.SetSelection #Edge #{}
print select1
print select2
$.EditablePoly.SetSelection #Edge (select2)
redrawviews() --update viewport
--macros.run "MY_select" "select_edge"
subObjectLevel=2;