(
	b=#()
	for i=1 to 10 do
	(
		a=biped.getNode $selection[1] #spine link: i
		if a==undefined do exit
		append b a
	)
	select b
)