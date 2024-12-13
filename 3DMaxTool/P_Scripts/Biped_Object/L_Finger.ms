(
	b=#()
	a=((biped.getNode $selection[1] #larm link:4).children)
	if a.count==0 then ()
	else if a.count==1 then (select a)
	else 
	(
		for i=2 to a.count do 
		(append b a[i])
		select b
	)
)