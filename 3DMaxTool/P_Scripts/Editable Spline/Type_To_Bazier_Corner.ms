undo on
(
	for i=1 to (numSplines $) do
	(
		arr=getKnotSelection $ i
		for ii in arr do
		(
			setKnotType $ i ii #beziercorner)
		)
	updateshape $	
)