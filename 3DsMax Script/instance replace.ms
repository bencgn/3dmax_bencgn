
-- Author :  HanyElTiby mailto:Ha_tiby@Hotmail.com
-- Version:  3ds max 4
--
-- 
--***********************************************************************************************
-- MODIFY THIS AT YOUR OWN RISK

rollout Instance_Replace "Make instances" width:200 height:100
(
	pickbutton btn1 "Pick_master" pos:[85,9] width:100 height:23
	label lbl1 "Master Object :" pos:[10,12] width:75 height:20
	button btn3 "Make Instances" pos:[10,40] width:176 height:23
	on btn1 picked obj do
	(
			global Master_Obj = obj
			btn1.text = obj.name
		)
	on btn3 pressed do
		for i in selection do instancereplace i Master_Obj
)
rollout Help "Help" width:200 Height:60
(
	label lbl5 "1 : Pick master Object first                    2 : Select Objects to be instances then press Make Instances button" pos:[10,10] width:180 height:45

)
-- create the rollout window and add the  rollout
if InstanceReplaceFloater != undefined do
				(
				closerolloutfloater InstanceReplaceFloater
				)		
InstanceReplaceFloater = newRolloutFloater "InstanceReplace" 210 120 
addRollout Instance_Replace InstanceReplaceFloater
addRollout Help InstanceReplaceFloater	rolledup:true		

