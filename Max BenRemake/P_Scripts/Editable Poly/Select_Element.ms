obj=selection[1]
mod_=modpanel.getCurrentObject () as string
if (mod_=="Editable Poly") then
(
	if subobjectLevel==1 then
	(
	selVertsBA = polyop.getVertSelection obj
	aa=polyop.getfacesusingvert obj selVertsBA
	bb=polyop.getElementsUsingFace obj aa 
	cc=polyop.getvertsusingface obj bb
	$.selectedVerts=cc
	)

	else if (subObjectLevel==2) or (subObjectLevel==3) then
	(
	selVertsBA = polyop.getEdgeSelection obj
	aa=polyop.getFacesUsingEdge obj selVertsBA
	bb=polyop.getElementsUsingFace obj aa 
	cc=polyop.getedgesusingface obj bb
	$.selectededges=cc
	)

	else if (subObjectLevel==4) then
	(
	selVertsBA = polyop.getFaceSelection obj
	bb=polyop.getElementsUsingFace obj selVertsBA
	$.selectedFaces=bb
	)

)

else if (mod_=="Skin:Skin") then
(
	skinOps.growSelection $.modifiers[#Skin]
	skinOps.growSelection $.modifiers[#Skin]
	skinOps.growSelection $.modifiers[#Skin]
	skinOps.loopSelection $.modifiers[#Skin]
	skinOps.ringSelection $.modifiers[#Skin]
	skinOps.loopSelection $.modifiers[#Skin]
	skinOps.ringSelection $.modifiers[#Skin]
	skinOps.growSelection $.modifiers[#Skin]
	
)