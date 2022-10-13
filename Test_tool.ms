try(destroyDialog allControls )catch()
rollout subRollout1 "Subrollout" ( )
rollout allControls "User Interface Controls" (
angle theAngle "Angle" width:80 across:2 degrees:45 align:#left
slider theSlider "Slider:" orient:#vertical
spinner theSpinner "Spinner:"
group "Group" (
button theButton "Button" across:2 width:80 align:#left
checkbutton theCheckbutton "Checkbutton" width:80 align:#right
mapbutton theMapButton "Map Button" width:80 across:2 align:#left
materialbutton theMatButton "Material Button" width:80 align:#right
pickbutton thePickbutton "Pickbutton:" width:80)
checkbox theCheckbox "Checkbox" across:2 offset:[0,2]
colorpicker theColorpicker "Colorpicker:"
listbox theListbox "Listbox:" items:#("Item 1","Item 2")\
height:3 width:80 across:2
multilistbox theMLBox "Multilistbox:" items:#("Item 1","Item 2")\
height:3 width:80
dropdownlist theDDL "DropDownList:" items:#("Item 1","Item 2")\
width:80 across:2
combobox theCombobox "Combobox:" items:#("Item 1","Item 2")\
height:3 width:80
edittext theEdittext "Edittext:"
hyperlink theHyperlink "Hyperlink" url:"http://www.autodesk.com"\
color:red across:2 offset:[10,20]
label theLabel "Label" offset:[0,20]
groupBox theGroupbox "Groupbox:" height:40 offset:[0,-40] width:174
progressbar theProgressbar "Progressbar:" value:50
radiobuttons theRadiobuttons labels:#("Option 1","Option 2")
bitmap theBitmap "Bitmap" width:80 height:50 offset:[0,0]\
bitmap:(bitmap 80 50 color:red) align:#left across:2
imgTag theImgTag "Bitmap" width:80 height:50 offset:[0,0]\
bitmap:(bitmap 80 50 color:green) align:#right
SubRollout theSubrollout "Subrollout" height:50
curvecontrol theCurvecontrol "Curvecontrol:" height:150
)
createDialog allControls 200 800
AddSubRollout allControls.theSubrollout subRollout1