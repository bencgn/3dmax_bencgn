sele=#();
fn p3Equal p3a p3b = (
	if 	(p3a.x+0.001 > p3b.x) and (p3a.x-0.001 < p3b.x) and 
		(p3a.y+0.001 > p3b.y) and (p3a.y-0.001 < p3b.y) and 
		(p3a.z+0.001> p3b.z) and (p3a.z-0.001 < p3b.z)   
		then          true      else         false   )

fn delete_du a b= (
	if 
		p3Equal (polyOp.getFaceCenter $ a) (polyOp.getFaceCenter $ b) 
	then (append sele b return 1) 
	else (return 2))


rollout select_duplicate_face "select_duplicate_face" width:162 height:105
(
	button btn2 "Select!" pos:[8,58] width:143 height:40
	label lbl1 "1. select editable poly object" pos:[5,26] width:148 height:16
	label lbl2 "2. press button" pos:[5,41] width:150 height:14
	label lbl3 "Select Duplicate Face" pos:[5,8] width:146 height:18
	on btn2 pressed do
	(
	sele=#();
	for i=1 to (polyop.getNumFaces $) do 
		(
					for ii=i+1 to (polyop.getNumFaces $) do 
						(if delete_du i ii == 1 do  exit)
		)
		
	max modify mode;
	subObjectLevel = 4
	polyop.SetFaceSelection $ sele
	)
)



createdialog select_duplicate_face