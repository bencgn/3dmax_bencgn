--REFERENCE ROTATION WITH Z AXIS FIXED
--by: Retouchaid
--version: 1.0
--created: 01-01-2017
--modified:
--compatible with: 3ds max 2014

macroscript RotateRefZ buttonText: "Reference Rotation (Z axis fixed)" category: "Retouchaid"
(
on isEnabled return 
(
	selection.count > 0
)
on execute do 
(
	fn compareFN a b = (
		if a==b then (
			messagebox "This point have to be different then pivot point!"
			return false
		)
		else return true
	)--end fn

	relPt = #()

	p3A = pickpoint prompt:"Pick pivot point:" snap: #3D

	if (classof p3A)==point3 then 
	(
		p3B= pickpoint prompt:"Pick reference point:" snap: #3D rubberBand: p3A
		if (classof p3B)==point3 and (compareFN p3A p3B) then 
		(
			p3C = pickpoint prompt:"Pick reference point:" snap: #3D rubberBand: p3A
			if (classof p3C)==point3 and (compareFN p3A p3C) then
			(
				--flatten z value--------------------------------
				p3A.z=0
				p3B.z=0
				p3C.z=0
				--------------------------------------------------
				relPt=#((p3B - p3A), (p3C - p3A))
				--counting angel relatively to the beginning of coordinate system
				abAngle = acos (dot (normalize relPt[1]) (normalize relPt[2]))
				rotMatrix = arbAxis (cross (normalize relPt[1]) (normalize relPt[2]))
				rotMatrix.row4 = p3A
				for i in selection do
				(
					if (isValidNode i) and (classof i) != Dummy then ( --dummy is for groups; alternative exclution is - (superclassof i) != helper
					in coordsys rotMatrix about rotMatrix rotate i abAngle z_axis
					)
				)--end for
			)--end if p3C
		)--end if p3B
	)--end if p3A
)--end on execute
)--end macroscript

