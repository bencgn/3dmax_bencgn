(

fn dotnetcolor r g b = (
		(dotNetClass "System.Drawing.Color").fromARGB r g b
	)
(


local xButton = dotNetObject "System.windows.forms.button"
xButton.text = "X"
xButton.size = dotNetObject "System.Drawing.Size" 45 40 
xButton.location = dotNetObject "System.Drawing.Point" 0 0
xButton.foreColor=(dotnetcolor 255 0 0)

local yButton = dotNetObject "System.windows.forms.button"
yButton.text = "Y"
yButton.size = dotNetObject "System.Drawing.Size" 45 40 
yButton.location = dotNetObject "System.Drawing.Point" 45 0

local zButton = dotNetObject "System.windows.forms.button"
zButton.text = "Z"
zButton.size = dotNetObject "System.Drawing.Size" 45 40 
zButton.location = dotNetObject "System.Drawing.Point" 90 0

local txtbox=dotNetObject "System.windows.forms.TextBox"
txtbox.location = dotNetObject "System.Drawing.Point" 60 90
--txtbox.Hide()
 
local hForm = dotNetObject "MaxCustomControls.MaxForm" pos:[0,0]
cursor = dotnetclass "System.Windows.Forms.Cursor"
p = cursor.Position
hform.StartPosition = hform.StartPosition.Manual
hForm.Location=dotnetobject "System.Drawing.Point" (p.x-20) (p.y-5)
hForm.size=dotNetObject "System.Drawing.Size" 30 50
hForm.FormBorderStyle = (dotnetclass "System.Windows.Forms.FormBorderStyle").none
hForm.controls.add txtbox
hForm.controls.add xButton
hForm.controls.add yButton
hForm.controls.add zButton
function MakePlanefn arg=
(
	undo on
	(
	if arg==1 then $.EditablePoly.MakePlanarIn #X
	else if arg==2 then $.EditablePoly.MakePlanarIn #Y
	else $.EditablePoly.MakePlanarIn #Z
	)
)
function selectaxis tt =
(
	xButton.foreColor=(dotnetcolor 255 255 255)
	yButton.foreColor=(dotnetcolor 255 255 255)
	zButton.foreColor=(dotnetcolor 255 255 255)
	max undo
	if tt=="x" then (xButton.foreColor=(dotnetcolor 255 0 0);  MakePlanefn 1)
	else if tt=="y" then (yButton.foreColor=(dotnetcolor 255 0 0);   MakePlanefn 2)
	else if tt=="z" then (zButton.foreColor=(dotnetcolor 255 0 0);   MakePlanefn 3)
	txtbox.focus()
	txtbox.text=""
)

function keyevent ee=
(
if ee.KeyCode == ee.KeyCode.A then (print "X"; selectaxis "x")
else if ee.KeyCode == ee.KeyCode.S then (print "Y"; selectaxis "y")
else if ee.KeyCode == ee.KeyCode.D then (print "Z"; selectaxis "z")
else if ee.KeyCode == ee.KeyCode.Space then (hForm.close())
else (max undo; hForm.close())
)

function lostfocuss=(hForm.close())

function gotfocuss =()

dotnet.addEventHandler txtbox "KeyDown" keyevent
dotnet.addEventHandler txtbox "Lostfocus" lostfocuss
dotNet.setLifetimeControl hForm #dotnet
hForm.show()
txtbox.Focus()
)
gc()
)