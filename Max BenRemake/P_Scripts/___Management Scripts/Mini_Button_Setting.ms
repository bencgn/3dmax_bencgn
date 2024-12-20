(
	
	global _cate , _btnname
	local category__name, btn__name
	
fn Dialog_modal text1 text2=
(
-- instantiate the object
theObj = dotNetObject "MaxCustomControls.RenameInstanceDialog" text2
theobj.text =text1
DialogResult = theObj.Showmodal()

--test if the ok button was pressed
   /*
dotnet.compareenums TheObj.DialogResult ((dotnetclass "System.Windows.Forms.DialogResult").OK)*/
--get the new text string
text_=theobj.InstanceName 
text_arr=filterString text_ "\""
text_=""
for i in text_arr do
(
	text_=text_+i
)
return text_
)
	
category__name=""
btn__name=""
	
rollout mini_button_Setting "Fast_Button_Setting" width:168 height:96
(
	label 'BTN' "Button" pos:[8,3] width:174 height:32 enabled:true align:#left
	button 'editscript' "Edit Script" pos:[8,40] width:72 height:24 align:#left
	button 'renamescript' "Rename Script" pos:[80,40] width:72 height:24 align:#left
	button 'sethotkey' "Set Hotkey" pos:[8,64] width:72 height:24 align:#left
	button 'close_' "Close" pos:[80,64] width:72 height:24 align:#left
	
	
	
	
	
	
	
	on editscript pressed do
	(
		_name__=btn__name
		if _name__[_name__.count]==")" and _name__[(_name__.count-2)]=="(" do 
		(
			_name__=substring _name__ 1 (_name__.count-4)
		)
		edit ((getdir #userscripts)+"\\P_Scripts\\"+category__name+"\\"+_name__+".ms")
	)
	on renamescript pressed do
	(
		New_name=(Dialog_modal "Want name?" "")
		if (New_name=="") do (return false)
		
		btnfile=openfile ((getdir #userscripts)+"\\P_Scripts\\"+category__name+"\\Info\\Add_button.ms") 
		_name__=btn__name
		minus_value=2
		if _name__[_name__.count]==")" and _name__[(_name__.count-2)]=="(" do 
		(
			_name__=substring _name__ 1 (_name__.count-4)
			minus_value=3
		)
		
		_name__2=""
		if (btn__name[btn__name.count]==")") and (btn__name[btn__name.count-2]=="(") do
		(
			_name__2=" "+btn__name[btn__name.count-2]+btn__name[btn__name.count-1]+btn__name[btn__name.count]
		)
		btn__name_=New_name+_name__2
		btn__name=New_name+_name__2
		mini_button_Setting.Btn.text="Category : "+category__name+"\nButton : "+btn__name_
		
		
		seek btnfile 0
		textArr = #()
		while not (eof btnfile) do 
		(
			aa=(readline btnfile)
			find_btn_name=(findstring aa _name__)
			if find_btn_name!=undefined do 
			(
				aa=replace aa (find_btn_name) (_name__.count) New_name
			)
			append textArr aa
		)
		close btnfile
		
		btnfile=openfile ((getdir #userscripts)+"\\P_Scripts\\"+category__name+"\\Info\\Add_button.ms") mode:"w"
		for i in textArr do
		(
			format "%\r\n" i to:btnfile
		)
		close btnfile
		
		Renamefile ((getdir #userscripts)+"\\P_Scripts\\"+category__name+"\\"+_name__+".ms") ((getdir #userscripts)+"\\P_Scripts\\"+category__name+"\\"+New_name+".ms")
	)
	on sethotkey pressed do
	(
		New_HotKey=toupper (Dialog_modal "If You Want Delete Hotkey, Input 'None'" "")
		if (New_HotKey.count!=1) and (New_HotKey!="NONE") do (return false)
		if (New_HotKey=="NONE") do (New_HotKey=""; btn__name_="")
		
		btnfile=openfile ((getdir #userscripts)+"\\P_Scripts\\"+category__name+"\\Info\\Add_button.ms") 
		_name__=btn__name
		minus_value=2
		if _name__[_name__.count]==")" and _name__[(_name__.count-2)]=="(" do 
		(
			_name__=substring _name__ 1 (_name__.count-4)
			minus_value=3
		)
		
		btn__name_=_name__+" ("+New_HotKey+")"
		mini_button_Setting.Btn.text="Category : "+category__name+"\nButton : "+btn__name_
		
		seek btnfile 0
		textArr = #()
		while not (eof btnfile) do 
		(
			aa=(readline btnfile)
			find_btn_name=(findstring aa _name__)
			if find_btn_name!=undefined do 
			(
				aa=replace aa (find_btn_name+(_name__.count)+2) minus_value ("\""+New_HotKey+"\"")
			)
			append textArr aa
		)
		close btnfile
		
		btnfile=openfile ((getdir #userscripts)+"\\P_Scripts\\"+category__name+"\\Info\\Add_button.ms") mode:"w"
		for i in textArr do
		(
			format "%\r\n" i to:btnfile
		)		
		close btnfile
	)
	on close_ pressed do
		(_cate=undefined; _btnname=undefined; destroydialog mini_button_Setting)
)




function _cate a=
(
	category__name=a
	mini_button_Setting.Btn.text="Category : "+category__name+"\nButton : "+btn__name
)
function _btnname b=
(
	btn__name=b
	mini_button_Setting.Btn.text="Category : "+category__name+"\nButton : "+btn__name
)

m_pos=mouse.screenpos 
m_pos.x=m_pos.x+20
m_pos.y=m_pos.y-50
createdialog mini_button_Setting pos:m_pos
)             