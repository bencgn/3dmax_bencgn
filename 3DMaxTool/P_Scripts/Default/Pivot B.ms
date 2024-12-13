cc=deepcopy $selection

for i in cc do 
(
	i.pivot = [i.center.x,i.center.y,i.min.z]
)